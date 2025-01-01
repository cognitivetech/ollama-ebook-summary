# 1. split a pdf, its pages flattened into lines of a text file
# 2. extract its images to the output directory
# 3. split into sections
import os, sys, csv, re, pandas as pd
from PyPDF2 import PdfReader
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional

def split_text_by_headings(text: str, row_headings: List[str]) -> List[Tuple[str, str]]:
    """
    Split text into sections based on the headings provided for this specific row.
    If no headings match, return the entire text as one section.
    Combines empty sections with next section's heading.

    Args:
        text (str): The text content to split.
        row_headings (List[str]): List of headings that should be in this text.
    Returns:
        List[Tuple[str, str]]: A list of (heading, text) pairs.
    """
    lines = text.replace('\\n', '\n').split('\n')
    sections: List[Tuple[str, str]] = []
    found_any_heading = False
    current_heading = None
    current_content_lines = []
    pending_empty_headings = []  # Track headings with no content

    def finalize_current_section():
        """
        Finalizes the content for the `current_heading` by appending to `sections`.
        Handles empty sections by combining with next section's heading.
        """
        nonlocal current_heading, current_content_lines, pending_empty_headings

        if current_heading is not None:
            joined_content = '\\n'.join(current_content_lines)

            if not joined_content.strip():
                # If current section is empty, add to pending headings
                pending_empty_headings.append(current_heading)
            else:
                # If we have pending empty headings, combine them with current heading
                if pending_empty_headings:
                    combined_heading = ' > '.join(pending_empty_headings + [current_heading])
                    pending_empty_headings = []  # Clear pending headings
                else:
                    combined_heading = current_heading

                # If the last heading in sections is the same, just append text there
                if sections and sections[-1][0] == combined_heading:
                    prev_heading, prev_text = sections[-1]
                    sections[-1] = (prev_heading, prev_text + '\\n' + joined_content)
                else:
                    sections.append((combined_heading, joined_content))

        current_content_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Attempt to match the line to one of the row_headings
        matched_heading = None
        clean_line = re.sub(r'^\d+(\.\d+)*\s*', '', line).strip()
        for heading in row_headings:
            ratio = SequenceMatcher(None, clean_line.lower(), heading.lower()).ratio()
            if clean_line.lower() == heading.lower() or ratio > 0.9:
                matched_heading = heading
                found_any_heading = True
                break

        if matched_heading is not None:
            finalize_current_section()
            current_heading = matched_heading
        else:
            if current_heading is None:
                if row_headings:
                    current_heading = row_headings[0]
                    found_any_heading = True
            current_content_lines.append(line)

    # Finalize the last section
    finalize_current_section()

    # Handle any remaining pending empty headings
    if pending_empty_headings and sections:
        # Combine remaining empty headings with the last section
        last_heading, last_content = sections[-1]
        combined_heading = ' > '.join(pending_empty_headings + [last_heading])
        sections[-1] = (combined_heading, last_content)

    # If no headings were found at all, return entire text as one section
    if not found_any_heading and row_headings:
        full_text = '\\n'.join(lines)
        sections = [(row_headings[0], full_text)]

    return sections

def get_text_length(text: str) -> int:
    """Helper function to get consistent text length measurement"""
    return len(text.replace('\\n', '\n'))

def process_intermediate_csv(input_csv: str, output_csv: str, unwind_pages: bool = False):
    """
    Process the intermediate CSV, grouping consecutive rows with same headings.

    Args:
        input_csv (str): Path to input CSV file
        output_csv (str): Path to output CSV file
        unwind_pages (bool): If True, unwind sections back to original pages. If False, keep sections combined.
    """
    df = pd.read_csv(input_csv)
    final_sections = []

    i = 0
    while i < len(df):
        # Start a new group
        current_titles = df.iloc[i]['titles']
        current_levels = df.iloc[i]['levels']
        group_pages = []
        group_text = []
        original_lengths = []

        # Collect all consecutive rows with same headings
        while i < len(df) and df.iloc[i]['titles'] == current_titles:
            # [existing code for collecting group data]
            current_text = df.iloc[i]['text']

            if i + 1 < len(df):
                next_row = df.iloc[i + 1]
                next_text = next_row['text']
                next_titles = next_row['titles'].split(';')

                # Find first heading occurrence in next_text
                first_heading_pos = -1
                for heading in next_titles:
                    heading = heading.strip()
                    pattern = r'(?:\d+(?:\.\d+)*\s*)?' + re.escape(heading)
                    match = re.search(pattern, next_text, re.IGNORECASE)
                    if match:
                        first_heading_pos = match.start()
                        break

                # If text appears before first heading, it belongs to previous section
                if first_heading_pos > 0:
                    preceding_text = next_text[:first_heading_pos].strip()
                    if preceding_text:
                        current_text = current_text + '\\n' + preceding_text
                        # Update next row's text to remove the preceding portion
                        df.at[i + 1, 'text'] = next_text[first_heading_pos:].strip()

            group_pages.append(df.iloc[i]['page'])
            original_lengths.append(get_text_length(current_text))
            group_text.append(current_text)
            i += 1

        # Combine text from all pages in group
        combined_text = '\n'.join(group_text)

        # Get headings and levels for this group
        row_headings = [t.strip() for t in current_titles.split(';')]
        if isinstance(current_levels, str):
            row_levels = [int(l) for l in current_levels.split(';')]
        else:
            row_levels = [int(current_levels)] * len(row_headings)

        # Split combined text into sections
        sections = split_text_by_headings(combined_text, row_headings)

        if unwind_pages:
            # Redistribute sections back to original pages
            current_section_idx = 0
            current_section_offset = 0

            for page_idx, page_num in enumerate(group_pages):
                page_sections = []
                accumulated_length = 0
                target_length = original_lengths[page_idx]

                # [existing unwinding logic]
                is_last_page = page_idx == len(group_pages) - 1

                while (current_section_idx < len(sections) and 
                       (is_last_page or accumulated_length < target_length)):
                    heading, content = sections[current_section_idx]
                    first_heading = heading.split(' > ')[0].strip()
                    level = row_levels[row_headings.index(first_heading)]

                    remaining_content = content[current_section_offset:]
                    content_length = get_text_length(remaining_content)

                    if is_last_page or accumulated_length + content_length <= target_length:
                        page_sections.append({
                            'titles': heading,
                            'levels': str(level),
                            'page': page_num,
                            'text': remaining_content,
                            'len': get_text_length(remaining_content)  # Add length here
                        })
                        accumulated_length += content_length
                        current_section_idx += 1
                        current_section_offset = 0
                    else:
                        available_length = target_length - accumulated_length
                        split_point = find_split_point(remaining_content, available_length)

                        page_sections.append({
                            'titles': heading,
                            'levels': str(level),
                            'page': page_num,
                            'text': remaining_content[:split_point],
                            'len': get_text_length(remaining_content[:split_point])  # Add length here
                        })
                        current_section_offset += split_point
                        break

                final_sections.extend(page_sections)
        else:
            # Keep sections combined (don't unwind to pages)
            for heading, content in sections:
                first_heading = heading.split(' > ')[0].strip()
                level = row_levels[row_headings.index(first_heading)]
                final_sections.append({
                    'titles': heading,
                    'levels': str(level),
                    'page': f"{group_pages[0]}-{group_pages[-1]}" if len(group_pages) > 1 else str(group_pages[0]),
                    'text': content,
                    'len': get_text_length(content)  # Add length here                    
                })

    # Create final DataFrame and save
    final_df = pd.DataFrame(final_sections)
    final_df.to_csv(output_csv, index=False)
    print(f"Created final sections CSV: {output_csv}")
    print(f"Total sections: {len(final_sections)}")

def find_split_point(text: str, target_length: int) -> int:
    """Find appropriate point to split text, preferring natural breaks"""
    if target_length >= len(text):
        return len(text)

    # Look for natural break points near target length
    text = text.replace('\\n', '\n')

    # Try to split at paragraph
    for i in range(target_length, max(0, target_length - 100), -1):
        if i < len(text) and text[i:i+2] == '\n\n':
            return i

    # Try to split at sentence
    for i in range(target_length, max(0, target_length - 50), -1):
        if i < len(text) and text[i] in '.!?' and (i+1 >= len(text) or text[i+1].isspace()):
            return i + 1

    # Fall back to word boundary
    for i in range(target_length, max(0, target_length - 20), -1):
        if i < len(text) and text[i].isspace():
            return i

    # Last resort: split at exact length
    return target_length

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

def get_document_title(reader, pdf_path):
    """
    Attempt to get the document title in order of preference:
    1. PDF metadata title
    2. First outline item if it appears on page 1
    3. Cleaned filename as fallback
    """
    # Try to get title from PDF metadata
    try:
        if reader.metadata and reader.metadata.get('/Title'):
            return reader.metadata['/Title'].strip()

        # Check if there's an outline and its first item is on page 1
        outline = check_pdf_outline(pdf_path)
        if outline:
            sections = get_outline_sections(outline, reader)
            if sections and sections[0][1] == 0:  # page 0 is first page
                return sections[0][0].strip()
    except Exception as e:
        print(f"Warning: Error accessing PDF metadata: {e}")

    # Fall back to filename if no title found in metadata or outline
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    clean_name = re.sub(r'[-_]', ' ', base_name).strip()
    return clean_name

def extract_pdf_to_csv_and_images(pdf_path):
    """
    Extract text and images from the PDF. Split text by page and by sections defined in the PDF outline.
    If no outline is present, print each page on a single line with newlines replaced by double spaces.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' does not exist.")
        return

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    csv_path = f"{base_name}_extracted.csv"

    images_folder = os.path.join('out', base_name, 'images')
    os.makedirs(images_folder, exist_ok=True)
    image_count = 0
    images_extracted = False

    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return

    # Get document title
    document_title = get_document_title(reader, pdf_path)

    outline = check_pdf_outline(pdf_path)
    sections = []
    if outline:
        sections = get_outline_sections(outline, reader)
        if sections:
            sections = sorted(sections, key=lambda x: x[1])
    else:
        print("No outline found in the PDF. Proceeding with page-based extraction.")

    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Headers
            if sections:
                csv_writer.writerow(['titles', 'levels', 'page', 'text'])
            else:
                csv_writer.writerow(['page', 'text'])

            total_pages = len(reader.pages)
            section_index = 0
            current_title = document_title
            current_level = "0"  # Root level for document title

            for page_num in range(total_pages):
                page = reader.pages[page_num]

                # Collect all sections that start on this page
                current_sections_for_page = []
                while (sections and 
                       section_index < len(sections) and 
                       page_num >= sections[section_index][1]):
                    current_sections_for_page.append(sections[section_index])
                    section_index += 1

                # Update current title and level if new sections are found
                if current_sections_for_page:
                    current_title = "; ".join(replace_quotes(section[0]) 
                                           for section in current_sections_for_page)
                    current_level = "; ".join(str(section[2]) 
                                           for section in current_sections_for_page)

                # Extract text from the page
                text = page.extract_text() or ""
                text = re.sub(r'\n', r'\\n', text)

                # Write the content to the CSV
                if sections:
                    csv_writer.writerow([
                        current_title,
                        current_level,
                        page_num + 1,
                        replace_quotes(text)
                    ])
                else:
                    csv_writer.writerow([page_num + 1, replace_quotes(text)])

                # Image extraction code (unchanged)
                if '/XObject' in page['/Resources']:
                    xobjects = page['/Resources']['/XObject'].get_object()
                    for obj_name in xobjects:
                        obj = xobjects[obj_name]
                        if obj['/Subtype'] == '/Image':
                            # Determine image extension
                            if '/Filter' in obj:
                                filter_type = obj['/Filter']
                                if isinstance(filter_type, list):
                                    filter_type = filter_type[0]
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

                            image_filename = f"{page_num + 1:03d}_{base_name}_img{image_count + 1:02d}.{ext}"
                            image_path = os.path.join(images_folder, image_filename)

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

def process_pdf_to_sections(pdf_path: str, unwind_pages: bool = False):
    """
    Combined processing function that:
    1. Extracts text and images from PDF
    2. Processes the extracted text into properly split sections
    """
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' does not exist.")
        return

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    intermediate_csv = f"{base_name}_extracted.csv"
    final_csv = f"{base_name}_final.csv"

    # Step 1: Extract PDF content
    extract_pdf_to_csv_and_images(pdf_path)

    # Step 2: Check if 'titles' column exists in the intermediate CSV
    try:
        df = pd.read_csv(intermediate_csv)
    except Exception as e:
        print(f"Error reading intermediate CSV file '{intermediate_csv}': {e}")
        return

    if 'titles' in df.columns and 'levels' in df.columns:
        # Proceed with intermediate processing
        process_intermediate_csv(intermediate_csv, final_csv, unwind_pages=unwind_pages)

        # Clean up intermediate file
        try:
            os.remove(intermediate_csv)
            print(f"Cleaned up intermediate file: {intermediate_csv}")
        except Exception as e:
            print(f"Warning: Could not remove intermediate file: {e}")
    else:
        # No 'titles' column; skip intermediate processing and rename intermediate CSV to final CSV
        try:
            print(f"No outline found. Skipped intermediate processing.")
            print(f"Final CSV is the same as the extracted CSV: '{intermediate_csv}'")
        except Exception as e:
            print(f"Error renaming intermediate CSV to final CSV: {e}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Process PDF file into sections with images')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--full', action='store_true', 
                       help='Unwind sections back to original pages')

    args = parser.parse_args()

    if not (os.path.isfile(args.pdf_path) and args.pdf_path.lower().endswith('.pdf')):
        print("The provided path is not a valid PDF file.")
        sys.exit(1)

    process_pdf_to_sections(args.pdf_path, unwind_pages=args.full)

if __name__ == "__main__":
    main()