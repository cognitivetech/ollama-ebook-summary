import zipfile
import os
import sys

def extract_html_files(epub_path):
    if not os.path.isfile(epub_path):
        print(f"Error: The file {epub_path} does not exist.")
        return
    output_dir = os.path.join(os.getcwd(), 'out', os.path.splitext(os.path.basename(epub_path))[0])

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the ZIP file
    with zipfile.ZipFile(epub_path, 'r') as zfile:
        # Iterate over each file in the ZIP
        for file_info in zfile.infolist():
            # Check if the file is an HTML file
            if file_info.filename.endswith('.html'):
                # Extract the file to a temporary location
                zfile.extract(file_info, output_dir)
                # Move the file to the base directory, discarding the original directory structure
                original_path = os.path.join(output_dir, file_info.filename)
                new_path = os.path.join(output_dir, os.path.basename(file_info.filename))
                os.rename(original_path, new_path)
                print(f"Extracted {file_info.filename} to {new_path}")
        print(f"All HTML files have been extracted to {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_html_from_epub.py <EPUB_FILE>")
    else:
        epub_file = sys.argv[1]
        extract_html_files(epub_file)
