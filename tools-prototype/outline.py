import os
from PyPDF2 import PdfReader

def check_pdf_outline(pdf_path):
    """
    Check if a PDF file has an outline (table of contents).
    Returns True if an outline is present, False otherwise.
    """
    try:
        reader = PdfReader(pdf_path)
        outline = reader.outline  # Changed from 'outlines' to 'outline'
        if outline:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False  # Assuming no outline if an error occurs

def main(directory):
    """
    Check all PDF files in the specified directory for an outline.
    Print the names of files that do not contain an outline.
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

if __name__ == '__main__':
    directory = input("Enter the directory path containing PDF files: ")
    main(directory)
