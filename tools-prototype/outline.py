import os
import sys
from PyPDF2 import PdfReader

def check_pdf_outline(pdf_path):
    """
    Check if a PDF file has an outline (table of contents).
    Returns the outline if present, None otherwise.
    """
    try:
        reader = PdfReader(pdf_path)
        outline = reader.outline
        return outline if outline else None
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

def print_outline_tree(outline, level=0):
    """
    Recursively print the outline as a tree structure with indentation for levels.
    """
    if isinstance(outline, list):
        for item in outline:
            print_outline_tree(item, level)
    elif isinstance(outline, dict):
        prefix = "  " * level + ("└─ " if level > 0 else "")
        print(f"{prefix}{outline.get('/Title', 'Untitled')}")
        if '/First' in outline:
            print_outline_tree(outline['/First'], level + 1)
    if isinstance(outline, dict) and '/Next' in outline:
        print_outline_tree(outline['/Next'], level)

def process_single_pdf(pdf_path):
    """
    Process a single PDF file, checking for an outline and printing it if present.
    """
    outline = check_pdf_outline(pdf_path)
    if outline:
        print(f"{pdf_path} has the following outline structure:")
        print_outline_tree(outline)
    else:
        print(f"{pdf_path} does not have an outline.")

def process_directory(directory):
    """
    Process all PDF files in the specified directory, checking for outlines.
    """
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
    no_outline_files = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        if not check_pdf_outline(pdf_path):
            no_outline_files.append(pdf_file)

    if no_outline_files:
        print("PDF files without an outline:")
        for file in no_outline_files:
            print(file)
    else:
        print("All PDF files have an outline.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <pdf_file_or_directory>")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        process_directory(path)
    elif os.path.isfile(path) and path.lower().endswith('.pdf'):
        process_single_pdf(path)
    else:
        print("The provided path is neither a directory nor a PDF file.")
        sys.exit(1)

if __name__ == '__main__':
    main()
