import os
import shutil
import sys
from PyPDF2 import PdfMerger

def join_pdfs(start, end, name, directory):
    # Ensure the directory exists
    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return

    # Create the 'old' directory if it doesn't exist
    old_directory = os.path.join(directory, 'old')
    os.makedirs(old_directory, exist_ok=True)

    # Initialize the PDF merger
    merger = PdfMerger()

    # Iterate through the files in the directory
    for i in range(start, end + 1):
        file_prefix = f"{i:02d}"
        for filename in os.listdir(directory):
            if filename.startswith(file_prefix) and filename.endswith('.pdf'):
                file_path = os.path.join(directory, filename)
                merger.append(file_path)
                # Move the file to the 'old' directory
                shutil.move(file_path, os.path.join(old_directory, filename))

    # Write the merged PDF to a new file
    output_file_path = os.path.join(directory, name)
    with open(output_file_path, 'wb') as output_file:
        merger.write(output_file)

    print(f"PDF files joined and saved to '{output_file_path}'.")
    print(f"Processed files moved to '{old_directory}'.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <start> <end> <directory>")
        sys.exit(1)

    try:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
        name = str(start) + '_' + str(end) + '_joined.pdf'
        directory = sys.argv[3]
        print(f"Start: {start}")
        print(f"End: {end}")
        print(f"Name: {name}")
        print(f"Directory: {directory}")
        join_pdfs(start, end, name, directory)
    except ValueError as ve:
        print(f"ValueError: {ve}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
