import re
import os
import sys
from typing import List, TypedDict
import click
import pypdf
import unicodedata
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@click.command()
@click.option("--dry-run", is_flag=True, help="Simulate a split")
@click.option("--regex", nargs=1, help="Select outline items that match a RegEx pattern")
@click.option("--overlap", is_flag=True, help="Overlap split points")
@click.option("--prefix", nargs=1, help="Filename prefix")
@click.argument("file")
def main(dry_run: bool, regex: str, overlap: bool, prefix: str, file: str):
    if not os.path.exists(file):
        print(f"Error: File '{file}' does not exist.")
        sys.exit(0)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        pdf = pypdf.PdfReader(input_file)
        
        # Check if the PDF is encrypted
        if pdf.is_encrypted:
            logging.error(f"Error: PDF file '{input_file}' is encrypted.")
            return
        
        # Process the PDF (e.g., extract TOC, pages, etc.)
        logging.info(f"Successfully loaded PDF: {input_file}")
        # Add further processing logic here
        
    except pypdf.errors.PdfReadError as e:
        logging.error(f"Error reading PDF: {str(e)}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logging.error("Unexpected error occurred.", exc_info=True)
        sys.exit(1)

    if len(pdf.outline) == 0:
        print("Error: File does not contain an outline.")
        sys.exit(0)

    toc = get_toc(pdf)

    page_count = len(pdf.pages)
    page_ranges = prepare_page_ranges(toc, regex, overlap, page_count)

    if len(page_ranges) == 0:
        print("No outline items match the RegEx." if regex else "No outline items found.")
    else:
        if prefix is not None:
            prefix = safe_filename(prefix)

        file_name = os.path.splitext(os.path.basename(file))[0].replace(" ", "-")
        file_name = re.sub(r'[^\w\-_]', '', file_name)
        output_dir = f"out/{file_name}/"

        os.makedirs(output_dir, exist_ok=True)

        if dry_run is True:
            dry_run_toc_split(page_ranges, prefix, output_dir)
        else:
            split_pdf(pdf, page_ranges, prefix, output_dir)

class OutlineItem(TypedDict):
    name: str
    page: int

def get_toc(pdf: pypdf.PdfReader) -> List[OutlineItem]:
    """
    Extracts the table of contents (TOC) from a PDF file and handles potential errors gracefully.

    Args:
        pdf (pypdf.PdfReader): The PDF reader object.

    Returns:
        List[OutlineItem]: A list of outline items with their names and page numbers.
    """
    toc_list = []

    try:
        # Check if the PDF has an outline
        if not hasattr(pdf, "outline") or not pdf.outline:
            logging.warning("The PDF does not contain an outline.")
            return []

        def extract_toc(toc):
            for item in toc:
                if isinstance(item, list):
                    extract_toc(item)
                else:
                    # Safely handle missing or malformed title and page information
                    title = item.get("/Title", "").strip()
                    if not title:
                        logging.warning("Skipping TOC item with no title.")
                        continue

                    try:
                        page_number = pdf.get_destination_page_number(item)
                        if page_number is None:
                            logging.warning(f"Skipping TOC item '{title}' with no valid page number.")
                            continue
                    except Exception as e:
                        logging.error(f"Error retrieving page number for TOC item '{title}': {e}")
                        continue

                    # Normalize and clean up the title
                    title = unicodedata.normalize("NFKD", title).replace("\r", " ").replace("\n", " ").replace("\t", " ")

                    toc_list.append({"name": title, "page": page_number})

        # Extract the TOC recursively
        extract_toc(pdf.outline)

        # Filter out entries with invalid or missing page numbers
        toc_list = [item for item in toc_list if item["page"] is not None]

        # Sort the TOC items by page number, handling None values safely
        toc_list = sorted(toc_list, key=lambda k: k["page"])

    except KeyError as e:
        logging.error(f"KeyError while processing TOC: {e}")
    except AttributeError as e:
        logging.error(f"AttributeError while processing TOC: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred while extracting TOC: {e}")

    return toc_list

class PageRange(TypedDict):
    name: str
    page_range: tuple

def prepare_page_ranges(toc: List[OutlineItem], regex: str, overlap: bool, page_count: int) -> List[PageRange]:
    page_ranges = get_page_ranges(toc, overlap, page_count)

    if regex is not None:
        page_ranges = filter_by_regex(page_ranges, regex)

    return page_ranges

def get_page_ranges(toc: List[OutlineItem], overlap: bool, page_count: int) -> List[PageRange]:
    page_ranges = []
    for i, item in enumerate(toc):
        name = item["name"]
        if len(name) == 0:
            name = "Untitled Section"
        if len([item for item in page_ranges if name is item["name"]]) > 0:
            name += " {}".format(len([item for item in page_ranges if name in item["name"]]) + 1)
        start_page = item["page"]
        end_page = toc[i + 1]["page"] - 1 if i + 1 < len(toc) else page_count - 1
        if overlap and i + 1 < len(toc):
            end_page = toc[i + 1]["page"]
        
        # Adjust ranges to ensure no single-page ranges and no overlaps
        if start_page == end_page:
            if i + 1 < len(toc):
                end_page = toc[i + 1]["page"]
            else:
                end_page = page_count - 1
        elif overlap and end_page >= toc[i + 1]["page"]:
            end_page = toc[i + 1]["page"] - 1

        page_ranges.append({"name": name, "page_range": (start_page, end_page)})
    
    # Merge single-page ranges with the next range
    merged_page_ranges = []
    for i in range(len(page_ranges)):
        if i < len(page_ranges) - 1 and page_ranges[i]["page_range"][1] == page_ranges[i + 1]["page_range"][0]:
            page_ranges[i + 1]["page_range"] = (page_ranges[i]["page_range"][0], page_ranges[i + 1]["page_range"][1])
        else:
            merged_page_ranges.append(page_ranges[i])
    
    return merged_page_ranges

def split_pdf(pdf: pypdf.PdfReader, page_ranges: List[PageRange], prefix: str, output_dir: str):
    for i, page_range in enumerate(page_ranges, start=1):
        pdf_writer = pypdf.PdfWriter()
        start_page, end_page = page_range["page_range"]
        logging.debug(f"Splitting pages {start_page} to {end_page} for '{page_range['name']}'")
        pdf_writer.append(
            fileobj=pdf,
            pages=(start_page, end_page + 1),
        )

        filename = f"{safe_filename(page_range['name'])}.pdf"
        if prefix is not None:
            filename = f"{prefix}{filename}"

        prefix_number = str(i).zfill(2)
        filename = f"{prefix_number}-{filename}"

        # Save the output file to the newly created directory
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "wb") as output:
            pdf_writer.write(output)

        logging.info(f"Created file '{output_path}'")

def dry_run_toc_split(page_ranges: List[PageRange], prefix: str, output_dir: str):
    print("With current options, the following PDF files would be created.\n")

    for i, item in enumerate(page_ranges, start=1):
        filename = safe_filename(item["name"])
        if prefix is not None:
            filename = f"{prefix}{filename}"

        prefix_number = str(i).zfill(2)
        filename = f"{prefix_number}-{filename}"

        # Display the output file path in the newly created directory
        output_path = os.path.join(output_dir, filename)

        if item["page_range"][0] == item["page_range"][1]:
            print(
                "– {}.pdf (contains page {})".format(
                    output_path, item["page_range"][0] + 1
                )
            )
        else:
            print(
                "– {}.pdf (contains pages {}–{})".format(
                    output_path,
                    item["page_range"][0] + 1,
                    item["page_range"][1] + 1,
                )
            )

def safe_filename(filename: str, max_length: int = 100) -> str:
    # Remove invalid characters
    sanitized = "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_", "-"))
    # Truncate to a maximum length
    return sanitized[:max_length].strip()

def filter_by_regex(input_list: List[PageRange], regex: str) -> List[PageRange]:
    return [item for item in input_list if re.search(r"{}".format(regex), item["name"])]

def get_n_levels(input_list: List[OutlineItem], level: int) -> List[OutlineItem]:
    return [item for item in input_list if item["level"] <= level]

if __name__ == "__main__":
    main()
