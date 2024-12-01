import os, re, csv, sys, pypdf
import subprocess
import argparse  # Import argparse for command-line parsing
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import ebooklib
from ebooklib import epub
import shutil
from lib.chunking import process_csv  # Import process_csv from chunking.py
from lib.epubunz import extract_html_files
from lib.epubsplit import SplitEpub
from lib.pdf_splitter import split_pdf  # Add this import

def sanitize_filename(filename):
    # Remove or replace unsafe characters  
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Trim spaces and periods from the end
    filename = filename.rstrip('. ')
    
    # Ensure the filename isn't empty and doesn't exceed max length
    filename = filename[:255] or 'untitled'
    
    return filename


def split_epub_by_sections(input_file, output_dir):
    """
    Split an EPUB file into multiple EPUBs by sections/chapters.
    
    Args:
        input_file: Path to input EPUB file
        output_dir: Directory to save split EPUB files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize SplitEpub with input file
    with open(input_file, 'rb') as epub_file:
        splitter = SplitEpub(epub_file)
        
        # Get all split points/lines
        split_lines = splitter.get_split_lines()
        
        # Iterate through split lines to create individual EPUBs
        for i, line in enumerate(split_lines):
            # Only split if there's TOC text available
            if line['toc'] and len(line['toc']) > 0:
                # Get title from first TOC entry for this split point
                section_title = line['toc'][0]
                
                # Create sanitized filename
                section_filename = sanitize_filename(section_title)
                
                # Prepend with four-digit sequential number
                sequence_number = f"{i+1:04}"
                output_path = os.path.join(output_dir, f"{sequence_number}_{section_filename}.epub")
                
                # Create new EPUB with just this section
                with open(output_path, 'wb') as out_file:
                    # Write split EPUB
                    splitter.write_split_epub(
                        out_file,
                        linenums=[i],  # Just this section
                        titleopt=section_title,  # Use section title
                        authoropts=splitter.origauthors,  # Keep original authors
                        descopt=f"Split section from {splitter.origtitle}"
                    )
                
                print(f"Created: {output_path}")
    return True


def get_title_from_html(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            
            # Try to get the title from the <title> tag
            title_tag = soup.find('title')
            if title_tag and title_tag.string:
                return title_tag.string.strip()
            
            # If no title tag, try to get the first <h1> tag
            h1_tag = soup.find('h1')
            if h1_tag and h1_tag.string:
                return h1_tag.string.strip()
    except Exception as e:
        print(f"Error reading HTML file: {e}")
    
    # If no title found in HTML, use the filename as backup
    return os.path.splitext(os.path.basename(filepath))[0]

def epub_to_text(epub_path):
    book = epub.read_epub(epub_path)
    text_content = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            # Extract just the text, removing HTML tags
            chapter_text = soup.get_text(separator=' ', strip=True)
            text_content.append(chapter_text)
    return '\n'.join(text_content)

def html_to_text(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        return soup.get_text()

def pdf_to_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return '\n'.join(text)

def natural_sort_key(s):
    """
    This function constructs a tuple of either integers (if the pattern matches digits)
    or the original elements (if not). This tuple can be used as a key for sorting.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def process_files(directory, file_type):
    data = []
    print(directory)
    files = sorted(os.listdir(directory), key=natural_sort_key)
    for filename in files:
        filepath = os.path.join(directory, filename)
        if file_type == 'html' and filename.endswith('.html'):
            text = html_to_text(filepath)
            title = get_title_from_html(filepath)
        elif file_type == 'epub':
            try:
                text = epub_to_text(filepath)
                book = epub.read_epub(filepath)
                title = book.get_metadata('DC', 'title')[0][0]
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
        elif file_type == 'pdf' and filename.endswith('.pdf'):
            text = pdf_to_text(filepath)
            title = os.path.splitext(filename)[0]
        else:
            continue

        text = text.replace('\t', ' ').strip().replace('\n', '\\n')
        if title is None:
            title = os.path.splitext(filename)[0]
        char_count = len(text)
        data.append([filename, title, text, char_count])
    return data

def save_to_csv(data, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'Title', 'Text', 'Character Count'])
        writer.writerows(data)

def main(input_file, output_dir, output_csv):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    file_type = os.path.splitext(input_file)[1][1:]  # Remove the dot


    if file_type == 'epub':
        success = split_epub_by_sections(input_file, output_dir)  # Changed from output_directory to output_dir
        if not success:
            print("Error detected while splitting EPUB. Attempting alternative method with epubunz.py.")
            extract_html_files(input_file, output_dir)  # Make sure this matches too
            file_type = 'html'
    elif file_type == 'pdf':
        from lib.pdf_splitter import split_pdf, get_toc, prepare_page_ranges

        pdf = pypdf.PdfReader(input_file)
        toc = get_toc(pdf)
        page_count = len(pdf.pages)
        page_ranges = prepare_page_ranges(toc, regex=None, overlap=False, page_count=page_count)
        output_dir = f"out/{os.path.splitext(os.path.basename(input_file))[0]}/"
        os.makedirs(output_dir, exist_ok=True)
        result = split_pdf(pdf, page_ranges, prefix=None, output_dir=output_dir)
    else:
        print("Unsupported file type. Please provide an EPUB or PDF file.")
        sys.exit(1)

    file_data = process_files(output_dir, file_type)
    save_to_csv(file_data, output_csv)
    print(f"CSV file created: {output_csv}")

    # Now that the CSV is created, we can run the chunking script
    process_csv(output_csv)
    print("Chunking process completed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert books to text and process them.")
    parser.add_argument('input_file', type=str, help='Input file path (EPUB or PDF)')
    args = parser.parse_args()

    input_file = args.input_file
    file_name = os.path.splitext(os.path.basename(input_file))[0].replace(" ", "-")
    file_name = re.sub(r'[^\w\-_]', '', file_name)
    output_dir = os.path.join(os.getcwd(), f"out/{file_name}/")
    output_csv = os.path.join(os.getcwd(), f"out/{file_name}.csv")
    print(output_dir)
    print(output_csv)

    main(input_file, output_dir, output_csv)
