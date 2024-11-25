# 1. split a pdf, its pages flattened into lines of a text file
# 2. extract its images to the output directory
import os, sys, csv, re
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

def get_outline_sections(outline, reader, sections=None, level=0):
    """
    Recursively parse the PDF outline to extract section titles, their starting page numbers, and levels.

    Returns a list of tuples: (section_title, starting_page_number, level)
    """
    if sections is None:
        sections = []

    for item in outline:
        if isinstance(item, list):
            # Nested outline (subsections)
            get_outline_sections(item, reader, sections, level + 1)
        else:
            title = item.title if hasattr(item, 'title') else item.get('/Title', 'Untitled')
            try:
                # Resolve the destination to find the page number
                destination = reader.get_destination_page_number(item)
                sections.append((title, destination, level))
            except Exception as e:
                print(f"Could not resolve destination for section '{title}': {e}")
                continue

    return sections

def extract_pdf_to_csv_and_images(pdf_path):
    """
    Extract text and images from the PDF. Split text by page and by sections defined in the PDF outline.
    If no outline is present, print each page on a single line with newlines replaced by double spaces.
    """
    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' does not exist.")
        return

    # Create output CSV filename based on input PDF name
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    csv_path = f"{base_name}_extracted.csv"

    # Prepare image extraction
    images_extracted = False
    images_folder = os.path.join('out', base_name, 'images')
    os.makedirs(images_folder, exist_ok=True)
    image_count = 0

    # Open the PDF file
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return

    # Extract and process outline
    outline = check_pdf_outline(pdf_path)
    sections = []
    if outline:
        sections = get_outline_sections(outline, reader)
        if sections:
            # Sort sections by starting page number
            sections = sorted(sections, key=lambda x: x[1])
    else:
        print("No outline found in the PDF. Proceeding with page-based extraction.")

    # Open the CSV file for writing
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            if sections:
                csv_writer.writerow(['title', 'level', 'page', 'text'])
            else:
                csv_writer.writerow(['page', 'text'])

            total_pages = len(reader.pages)
            current_section = "No Section"
            current_level = 0
            section_index = 0
            next_section_page = sections[section_index][1] if sections else None

            for page_num in range(total_pages):
                page = reader.pages[page_num]
                
                # Check if current page is the start of a new section (only if outline exists)
                if sections and next_section_page is not None and page_num >= next_section_page:
                    current_section, _, current_level = sections[section_index]
                    section_index += 1
                    next_section_page = sections[section_index][1] if section_index < len(sections) else None

                # Extract text from the page
                text = page.extract_text() or ""
                # Replace newlines with double spaces
                text = re.sub(r'\n', r'\\n', text)

                # Write the content to the CSV
                if sections:
                    csv_writer.writerow([
                        replace_quotes(current_section),
                        current_level,
                        page_num + 1,
                        replace_quotes(text)
                    ])
                else:
                    csv_writer.writerow([page_num + 1, replace_quotes(text)])

                # Extract images from the page (image extraction code remains unchanged)
                if '/XObject' in page['/Resources']:
                    xobjects = page['/Resources']['/XObject'].get_object()
                    for obj_name in xobjects:
                        obj = xobjects[obj_name]
                        if obj['/Subtype'] == '/Image':
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
                            image_filename = f"{page_num + 1:03d}_{base_name}_img{image_count + 1:02d}.{ext}"
                            image_path = os.path.join(images_folder, image_filename)

                            # Write image data to file
                            try:
                                with open(image_path, 'wb') as img_file:
                                    img_file.write(obj.get_data())
                                images_extracted = True
                                image_count += 1
                            except Exception as e:
                                print(f"Failed to write image {image_filename}: {e}")

        print(f"Extraction complete. Text saved to '{csv_path}'.")
        if images_extracted:
            print(f"Images have been saved to '{images_folder}'.")
        else:
            print("No images found in the PDF.")

    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        return

def replace_quotes(text):
    return re.sub(r'"', '"', text)

def main():
    if len(sys.argv) != 2:
        print("Usage: python split_pdf.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not (os.path.isfile(pdf_path) and pdf_path.lower().endswith('.pdf')):
        print("The provided path is not a valid PDF file.")
        sys.exit(1)

    extract_pdf_to_csv_and_images(pdf_path)

if __name__ == "__main__":
    main()
