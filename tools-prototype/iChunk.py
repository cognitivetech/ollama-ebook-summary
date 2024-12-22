import re, os
import torch
import nltk
import csv
import sys
import argparse
import traceback
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import chardet
import pdfplumber  # For PDF handling

# Ensure NLTK resources are available
nltk.download('punkt')

from pylatexenc.latex2text import LatexNodes2Text
import requests
from pathlib import Path
from urllib.parse import urlparse

def replace_latex_with_text(content):
    """Replace LaTeX math expressions with their text representations wrapped in special delimiters."""
    converter = LatexNodes2Text()

    def clean_text(text):
        """Clean up LaTeX artifacts after conversion."""
        text = re.sub(r'%\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\$\s*Mathematical Expression:\s*\$\s*', '', text)
        text = text.replace('\\top', '^T')
        text = text.replace('×', 'x')
        text = text.replace('∈', 'in')
        text = text.replace('ℝ', 'R')
        text = text.replace('\\', '')
        text = re.sub(r'\^{?(.*?)}?', r'^\1', text)
        text = re.sub(r'_{?(.*?)}?', r'_\1', text)
        text = re.sub(r'$\)', '', text)
        text = re.sub(r'\^T$$\($⊤', r'^T', text)
        text = re.sub(r'^\\$', '', text, flags=re.MULTILINE)
        return text.strip()

    def replace_math(match):
        latex = match.group(1)
        try:
            converted = converter.latex_to_text(latex)
            cleaned = clean_text(converted)
            # Wrap mathematical expressions in special delimiters
            return f'«math»{cleaned}«/math»'
        except Exception as e:
            print(f"Error converting LaTeX: {latex} - {str(e)}")
            return f'«math»{clean_text(latex)}«/math»'

    # Replace display math ($...$) with extra newlines for block equations
    content = re.sub(r'\$\$(.*?)\$\$', lambda m: '\n' + replace_math(m) + '\n', content, flags=re.DOTALL)

    # Replace inline math ($...$)
    content = re.sub(r'\$(.*?)\$', replace_math, content)

    # Final cleanup of the entire content
    content = clean_text(content)

    return content

def download_and_remove_images(content, base_output_dir):
    """Download remote images to output directory and remove image references from content."""
    
    # Create output directory if it doesn't exist
    output_dir = Path(base_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_image(url, filename):
        """Helper function to download image"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            output_path = output_dir / filename
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
            return False

    # Handle markdown images ![alt](url) - MODIFIED REGEX
    def process_md_image(match):
        url = match.group(2)
        if url.startswith(('http://', 'https://')):
            # Check if the URL likely points to an image
            if any(url.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg')):
                filename = os.path.basename(urlparse(url).path)
                if download_image(url, filename):
                    print(f"Downloaded: {url} -> {filename}")
                return ''  # Remove the image reference if downloaded
            else:
                return match.group(0) # Return the original link if not an image
        return match.group(0) # Return the original link if not an external URL

    # More standard markdown image regex
    content = re.sub(r'!$(.*?)$$(https?://.*?)$', process_md_image, content)

    # Handle HTML img tags
    def process_html_image(match):
        src_match = re.search(r'src=["\'](https?://[^\'"]+)["\']', match.group(0))
        if src_match:
            url = src_match.group(1)
            filename = os.path.basename(urlparse(url).path)
            if download_image(url, filename):
                print(f"Downloaded: {url} -> {filename}")
        return ''  # Remove the img tag
    
    content = re.sub(r'<img\s+[^>]*>', process_html_image, content)
    
    # Remove SVG tags and content (since these are typically inline)
    content = re.sub(r'<svg.*?</svg>', '', content, flags=re.DOTALL)
    
    return content

def safe_file_operations(func):
    """Decorator to handle common file operation exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnicodeDecodeError as e:
            print(f"\033[91mEncoding Error: {e}\nTry using a different file encoding.\033[0m")
        except FileNotFoundError as e:
            print(f"\033[91mFile Error: {e}\nPlease check if the file path is correct.\033[0m")
        except PermissionError as e:
            print(f"\033[91mPermission Error: {e}\nCheck file permissions.\033[0m")
        except Exception as e:
            print(f"\033[91mUnexpected Error: {str(e)}\033[0m")
            print(f"Error occurred at:\n{traceback.format_exc()}")
        return None
    return wrapper

@safe_file_operations
def read_file(file_path):
    """Read the content of a file, supporting both text and PDF formats."""
    if file_path.lower().endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            text_content = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.extend(text.split('\n'))
        return text_content
    else:
        with open(file_path, 'rb') as f:
            raw = f.read(10000)
            detected = chardet.detect(raw)
            encoding = detected['encoding'] if detected['confidence'] > 0.7 else 'utf-8'
        with open(file_path, 'r', encoding=encoding) as f:
            return f.readlines()


def preprocess(text):
    """Remove extra spaces and trim the text."""
    return re.sub(r'\s+', ' ', text).strip()


def split_text(text, min_chunk_size, max_chunk_size):
    """
    Split text into chunks while preserving and removing math tags.

    Args:
        text (str): The input text to split.
        min_chunk_size (int): Minimum size of a chunk.
        max_chunk_size (int): Maximum size of a chunk.

    Returns:
        list: List of cleaned text chunks.
    """
    chunks = []
    current_chunk = ''

    # Split text while preserving math sections
    parts = re.split(r'(«math».*?«/math»)', text)

    for part in parts:
        if part.startswith('«math»') and part.endswith('«/math»'):
            # If adding this math section would exceed max_chunk_size
            if len(current_chunk) + len(part) > max_chunk_size:
                if len(current_chunk) >= min_chunk_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = part
                else:
                    # If current chunk is too small, combine them
                    current_chunk += ' ' + part
            else:
                current_chunk += ' ' + part
        else:
            # Normal text - split by sentences
            sentences = sent_tokenize(part)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > max_chunk_size:
                    if len(current_chunk) >= min_chunk_size:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += ' ' + sentence
                else:
                    current_chunk += ' ' + sentence

    # Add the last chunk if it exists
    if current_chunk and len(current_chunk) >= min_chunk_size:
        chunks.append(current_chunk.strip())

    # Remove math delimiters from all chunks
    cleaned_chunks = [chunk.replace('«math»', '').replace('«/math»', '') for chunk in chunks]

    return cleaned_chunks


class FileChunkProcessor:
    def __init__(self, input_file, md_level=3, use_raw=False, min_chunk_size=6500, 
                 max_chunk_size=7500, process_latex=True, process_images=True):
        self.input_file = input_file
        self.md_level = md_level
        self.use_raw = use_raw
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.process_latex = process_latex
        self.process_images = process_images
        self.output_file = os.path.join(
            os.getcwd(),
            os.path.splitext(os.path.basename(input_file))[0] + '_chunked.csv'
        )
        self.chunks = []
        self.model = self.load_model()

    def load_model(self):
        """Load the SentenceTransformer model."""
        model_name_or_path = 'mixedbread-ai/mxbai-embed-large-v1'
        model = SentenceTransformer(model_name_or_path)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model.to(device)
        return model

    def determine_processing_mode(self, lines):
        """
        Determine whether to process raw or markdown based on file type and user flags.

        Args:
            lines (list): List of lines from the input file.

        Returns:
            str: 'raw' or 'markdown'
        """
        if self.use_raw:
            return 'raw'

        if self.input_file.lower().endswith('.pdf'):
            try:
                with pdfplumber.open(self.input_file) as pdf:
                    # Assuming that presence of metadata keys indicates structured PDF
                    if not any(pdf.metadata.get(key) for key in ["Title", "Subject", "Keywords"]):
                        print("No outline detected in PDF. Using raw processing.")
                        return 'raw'
            except Exception as e:
                print(f"Error checking PDF metadata: {e}. Defaulting to raw processing.")
                return 'raw'

        # Default to markdown processing if not raw
        return 'markdown'

    def remove_math_tags(self, text):
        """Remove math tags from a text."""
        return text.replace('«math»', '').replace('«/math»', '')

    def process_raw_text(self, lines):
        """Process the entire file as raw text and chunk it."""
        content = ' '.join([line.strip() for line in lines])
        content = preprocess(content)
        content = self.remove_math_tags(content)

        line_chunks = split_text(content, self.min_chunk_size, self.max_chunk_size)

        for idx, chunk in enumerate(line_chunks, start=1):
            self.chunks.append({
                "title": f"{idx}",
                "text": chunk,
                "length": len(chunk),
                "level": "N/A"
            })

    def extract_title(self, line):
        """
        Extract the title from a line, ensuring it doesn't exceed 150 characters
        and removing any existing double quotes.
        """
        if '+' in line:
            title = line.split('+', 1)[0].strip()[:150]
        else:
            title = line[:150].strip()
        return title.strip('"')

    def process_markdown(self, lines):
        """Process markdown content and create title-content pairs."""
        title_content_pairs = []
        current_title = ""
        current_content = ""
        parent_info = []  # Tracks (heading_text, level, has_content, used_as_parent)
        current_level = 0

        # Input validation
        if not isinstance(self.md_level, int) or not (2 <= self.md_level <= 6):
            raise ValueError(f"md_level must be between 2 and 6, got {self.md_level}")

        try:
            for line_num, line in enumerate(lines, 1):
                stripped_line = line.strip()
                heading_match = re.match(r'^(#{2,6})\s+(.*)', stripped_line)

                if heading_match:
                    hashes, heading_text = heading_match.groups()
                    level = len(hashes)

                    if level <= self.md_level:
                        if current_title and current_content.strip():
                            title_content_pairs.append((current_title, current_content.strip(), current_level))
                            if parent_info:
                                parent_info[-1] = (
                                    parent_info[-1][0],
                                    parent_info[-1][1],
                                    True,  # has_content
                                    parent_info[-1][3]
                                )

                        # Update parent_info stack
                        while parent_info and parent_info[-1][1] >= level:
                            parent_info.pop()

                        # Handle nested headings
                        if parent_info and not parent_info[-1][2] and not parent_info[-1][3]:
                            current_title = f"{parent_info[-1][0]} > {heading_text}"
                            current_level = parent_info[-1][1]
                            # Mark parent as used
                            parent_info[-1] = (
                                parent_info[-1][0],
                                parent_info[-1][1],
                                parent_info[-1][2],
                                True
                            )
                        else:
                            current_title = heading_text
                            current_level = level

                        # Add new heading to parent_info
                        parent_info.append((heading_text, level, False, False))
                        current_content = ""
                    else:
                        current_content += f" {stripped_line}"
                else:
                    current_content += f" {stripped_line}"

            # Add the final section if it exists
            if current_title and current_content.strip():
                title_content_pairs.append((current_title, current_content.strip(), current_level))

            print(f"Processed {len(lines)} lines")
            print(f"Created {len(title_content_pairs)} title-content pairs")

            return title_content_pairs

        except Exception as e:
            print(f"Error processing markdown at line {line_num}: {str(e)}")
            raise

    def process_markdown_text(self, lines):
        """Handle markdown processing and chunking."""
        # Join lines into a single content string for preprocessing
        content = '\n'.join(lines)

        # Create images directory if processing images
        if self.process_images:
            images_dir = os.path.join(os.path.dirname(self.output_file), 'images')
            content = download_and_remove_images(content, images_dir)

        # Process LaTeX if enabled
        if self.process_latex:
            content = replace_latex_with_text(content)

        # Split back into lines for markdown processing
        lines = content.split('\n')

        title_content_pairs = self.process_markdown(lines)

        for title, content, level in title_content_pairs:
            content = preprocess(content)
            content = self.remove_math_tags(content)

            if len(content) > self.max_chunk_size:
                line_chunks = split_text(content, self.min_chunk_size, self.max_chunk_size)
                for chunk in line_chunks:
                    self.chunks.append({
                        "title": title,
                        "text": chunk,
                        "length": len(chunk),
                        "level": str(level)
                    })
            else:
                self.chunks.append({
                    "title": title,
                    "text": content,
                    "length": len(content),
                    "level": str(level)
                })

    def process_plain_text(self, lines):
        """Process plain text lines, ensuring math tags are removed."""
        for line in lines:
            line = line.strip().replace('!', '.').replace('%', ' percent').replace('"', '')

            if '+' in line[:150]:
                title, content = line.split('+', 1)
                title = title.strip()
            else:
                title = line[:150].strip()
                content = line

            print(f"Title: {title}")
            print(f"Content length before chunking: {len(content)}")

            content = preprocess(content)
            content = self.remove_math_tags(content)

            line_chunks = split_text(content, self.min_chunk_size, self.max_chunk_size)
            print(f"Number of chunks created: {len(line_chunks)}")

            # Combine small last chunk if necessary
            if len(line_chunks) > 1 and len(line_chunks[-1]) < 2200:
                print("Combining small last chunk")
                combined_chunk = line_chunks[-2] + ' ' + line_chunks[-1]
                line_chunks = line_chunks[:-2] + [combined_chunk]

            for chunk in line_chunks:
                self.chunks.append({
                    "title": preprocess(title),
                    "text": chunk,
                    "length": len(chunk),
                    "level": "N/A"
                })

    def write_output(self):
        """Write the processed chunks to a CSV file."""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["title", "level", "text", "length"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for idx, chunk in enumerate(self.chunks, start=1):
                print(f"Final Chunk {idx}: Title={chunk['title']}, Length={chunk['length']}")
                writer.writerow(chunk)
        print(f"Chunking complete. Output saved to {self.output_file}")

    def run(self):
        """Execute the processing workflow."""
        try:
            lines = read_file(self.input_file)
            if lines is None:
                print("Failed to read the input file.")
                sys.exit(1)

            mode = self.determine_processing_mode(lines)
            print(f"Processing mode determined: {mode}")

            if mode == 'raw':
                self.process_raw_text(lines)
            elif mode == 'markdown':
                self.process_markdown_text(lines)
            else:
                print(f"Unknown processing mode: {mode}")
                sys.exit(1)

            self.write_output()

        except KeyboardInterrupt:
            print("\n\033[93mProcess interrupted by user.\033[0m")
            sys.exit(1)
        except Exception as e:
            print(f"\033[91mFatal Error: {str(e)}\033[0m")
            print(f"Stack trace:\n{traceback.format_exc()}")
            sys.exit(1)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process text or Markdown file and output chunks with their lengths.")
    parser.add_argument('input_file', type=str, help='Path to the input text or Markdown file')
    parser.add_argument('--md', type=int, default=3, help='Markdown heading level to split on (default: 3)')
    parser.add_argument('--raw', action='store_true', help='Process the entire file as raw text and chunk it')
    parser.add_argument('-m', '--min', type=int, default=6500, help='Minimum chunk size (default: 6500)')
    parser.add_argument('-x', '--max', type=int, default=7500, help='Maximum chunk size (default: 7500)')
    parser.add_argument('--no-latex', action='store_true', help='Disable LaTeX conversion')
    parser.add_argument('--no-images', action='store_true', help='Disable image downloading and removal')
    return parser.parse_args()

def main():
    args = parse_arguments()

    processor = FileChunkProcessor(
        input_file=args.input_file,
        md_level=args.md,
        use_raw=args.raw,
        min_chunk_size=args.min,
        max_chunk_size=args.max,
        process_latex=not args.no_latex,
        process_images=not args.no_images
    )

    processor.run()

if __name__ == '__main__':
    main()