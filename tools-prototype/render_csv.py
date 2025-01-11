import csv
import sys
import os
import re
import logging

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create formatters and handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Set console handler level to DEBUG
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Optional: File handler if you want log files
file_handler = logging.FileHandler('debug.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def sanitize_anchor(text):
    """
    Sanitize text to create valid markdown anchors:
    - Convert to lowercase
    - Replace special characters and spaces with hyphens
    - Remove any non-alphanumeric characters (except hyphens)
    - Remove multiple consecutive hyphens
    - Remove leading/trailing hyphens
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text

def get_heading_level(row, fieldnames_lower):
    logger.debug(f"Getting heading level for row: {dict(row)}")

    # Look specifically for the 'level' column in a case-insensitive manner
    level_key = next((k for k in row if k.lower() == 'level'), None)
    if level_key:
        level_value = row[level_key]
        logger.debug(f"Found level value: {level_value}")

        try:
            base_level = int(level_value)
            heading_level = base_level + 2
            logger.debug(f"Calculated heading level: {heading_level}")
            return min(max(heading_level, 2), 6)
        except ValueError as e:
            logger.error(f"Could not convert level value '{level_value}' to integer: {e}")

    logger.debug("Using default heading level 3")
    return 3

def process_summary(summary):
    """
    Process summary text to properly handle newlines and escape sequences
    """
    try:
        # Replace literal \n with actual newlines
        summary = summary.replace('\\n', '\n')
        return summary
    except Exception as e:
        logger.error(f"Error processing summary: {e}")
        return summary

def generate_markdown(input_file):
    try:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_markdown.md"

        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames_lower = [field.lower() for field in reader.fieldnames]

            logger.info(f"Found columns: {reader.fieldnames}")

            if 'title' not in fieldnames_lower or 'summary' not in fieldnames_lower:
                raise ValueError("CSV must contain 'title' and 'summary' columns (case-insensitive)")

            # Initialize ToC and content lists
            toc = ["## Table of Contents"]
            content = [f"# {base_name.replace('-', ' ')}", ""]  # Added list for cleaner appending

            # Temporary list to hold content sections
            content_sections = []

            for i, row in enumerate(reader, start=1):
                try:
                    logger.debug(f"Processing row {i}: {dict(row)}")
                    title = next(row[k] for k in row if k.lower() == 'title')
                    summary = next(row[k] for k in row if k.lower() == 'summary')

                    # Get and use the heading level
                    heading_level = get_heading_level(row, fieldnames_lower)
                    logger.debug(f"Using heading level {heading_level} for '{title}'")

                    processed_summary = process_summary(summary)
                    anchor = sanitize_anchor(title)

                    # Calculate indentation based on heading level
                    # Assuming heading_level >= 2
                    indent_level = heading_level - 2  # To start from no indent for level 2
                    indent = '  ' * indent_level  # Two spaces per level

                    # Append ToC entry with appropriate indentation
                    toc.append(f"{indent}- [{title}](#{anchor})")

                    # Append content section
                    content_sections.append(f"{'#' * heading_level} {title}")
                    content_sections.append("")  # Blank line
                    content_sections.extend(processed_summary.split('\n'))
                    content_sections.append("")  # Blank line

                except Exception as e:
                    logger.error(f"Error processing row {i}: {e}")
                    continue

            # After processing all rows, integrate ToC and content sections
            content.extend(toc)
            content.append("")  # Add blank line after ToC
            content.extend(content_sections)

            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.write('\n'.join(content))

            logger.info(f"Markdown file generated: {output_file}")

    except Exception as e:
        logger.error(f"Error generating markdown: {e}")
        raise
if __name__ == "__main__":
    logger.debug("Script started")
    if len(sys.argv) != 2:
        logger.error("Usage: python script.py <input_csv_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not input_file.endswith('.csv'):
        logger.error("Error: Input file must be a CSV.")
        sys.exit(1)

    generate_markdown(input_file)