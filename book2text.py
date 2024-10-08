import os
import re
import csv
import sys
import subprocess
import argparse  # Import argparse for command-line parsing
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import ebooklib
from ebooklib import epub
import shutil
from lib.chunking import process_csv  # Import process_csv from chunking.py

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
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return b'\n'.join(chapters).decode('utf-8')

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
        result = subprocess.run(f"python lib/epubsplit.py --split-by-section \"{input_file}\" --output-dir \"{output_dir}\"", shell=True, text=True, capture_output=True)
        if result.returncode != 0:
            print("Error detected while splitting EPUB. Error output:")
            print(result.stderr)
            print("Attempting alternative method with epubunz.py.")
            subprocess.run(f"python lib/epubunz.py \"{input_file}\" \"{output_dir}\"", shell=True)
            file_type = 'html'
    elif file_type == 'pdf':
        result = os.system(f"python3 lib/pdf_splitter.py \"{input_file}\"")
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
