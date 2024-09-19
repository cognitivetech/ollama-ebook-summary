# 1. split a pdf, its pages flattened into lines of a text file
# 2. extract its images to the output directory
import sys
import csv
from PyPDF2 import PdfReader
import os

def extract_pdf_to_csv_and_images(pdf_path):
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' does not exist.")
        return

    # Create output CSV filename based on input PDF name
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    csv_path = f"{base_name}_extracted.txt"

    # Prepare image extraction
    images_extracted = False
    images_folder = os.path.join('out', base_name)
    os.makedirs(images_folder, exist_ok=True)
    image_count = 0

    # Open the PDF file
    try:
        pdf = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return

    # Open the CSV file for writing
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text from the page
                text = page.extract_text() or ""
                
                # Remove newlines and extra whitespace
                text = ' '.join(text.split())
                
                # Write the content to the CSV
                csv_writer.writerow([text])

                # Extract images from the page
                if '/XObject' in page['/Resources']:
                    xobjects = page['/Resources']['/XObject'].get_object()
                    page_image_count = 0  # Counter for images on this page
                    for obj_name, obj in xobjects.items():
                        obj = obj.get_object()  # Resolve IndirectObject
                        if obj.get('/Subtype') == '/Image':
                            page_image_count += 1  # Increment the counter for each image on this page
                            # Determine image extension
                            if '/Filter' in obj:
                                filter_type = obj['/Filter']
                                if isinstance(filter_type, list):
                                    filter_type = filter_type[0]  # Handle array filters
                                if filter_type == '/DCTDecode':
                                    ext = 'jpg'
                                elif filter_type == '/JPXDecode':
                                    ext = 'jp2'
                                elif filter_type == '/FlateDecode':
                                    ext = 'png'
                                elif filter_type == '/LZWDecode':
                                    ext = 'tiff'
                                else:
                                    ext = 'bin'
                            else:
                                ext = 'bin'
                            
                            # Name the image with page number before base name
                            image_filename = f"{page_num:03d}_{base_name}_img{page_image_count:02d}.{ext}"
                            image_path = os.path.join(images_folder, image_filename)
                            
                            # Write image data to file
                            try:
                                with open(image_path, 'wb') as img_file:
                                    img_file.write(obj.get_data())
                                images_extracted = True
                            except Exception as e:
                                print(f"Failed to write image {image_filename}: {e}")

    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        return

    print(f"Extraction complete. Text saved to '{csv_path}'.")

    if images_extracted:
        print(f"Images have been saved to '{images_folder}'.")
    else:
        print("no images")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_pdf_file>")
    else:
        pdf_path = sys.argv[1]
        extract_pdf_to_csv_and_images(pdf_path)
