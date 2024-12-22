from pylatexenc.latex2text import LatexNodes2Text
import re
import requests
from pathlib import Path
from urllib.parse import urlparse
import os

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

# Modified process_markdown_file function:
def process_markdown_file(file_path):
    """Process a markdown file, downloading images and converting LaTeX to text."""
    try:
        # Read input file
        input_path = Path(file_path)
        with open(input_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Create output directory based on input filename
        output_dir = Path('out') / input_path.stem
        
        # Convert LaTeX to text and handle images
        content = download_and_remove_images(content, output_dir)
        cleaned_content = replace_latex_with_text(content)
        
        # Write back to same file
        with open(input_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)
            
        print(f"Successfully processed {file_path}")
        
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python script.py <markdown_file>")
        sys.exit(1)
        
    markdown_file = sys.argv[1]
    process_markdown_file(markdown_file)
