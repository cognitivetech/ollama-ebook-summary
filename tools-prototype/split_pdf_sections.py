# split_sections.py
import csv
import re
from difflib import SequenceMatcher
import pandas as pd
from typing import List, Dict, Tuple, Optional

def split_text_by_headings(text: str, row_headings: List[str]) -> List[Tuple[str, str]]:
    """
    Split text into sections based on the headings provided for this specific row.
    If no headings match, return the entire text as one section.

    Args:
        text: The text content to split
        row_headings: List of headings that should be present in this text
    """
    sections = []
    current_content = []
    found_any_heading = False

    lines = text.replace('\\n', '\n').split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Check if this line matches any of our row's headings
        matched_heading = None
        for heading in row_headings:
            # Strip any existing numeric prefix from the line
            clean_line = re.sub(r'^\d+(\.\d+)*\s*', '', line).strip()

            # Check for exact match or close match
            if (clean_line.lower() == heading.lower() or
                SequenceMatcher(None, clean_line.lower(), heading.lower()).ratio() > 0.9):
                matched_heading = heading
                found_any_heading = True
                break

        if matched_heading:
            # If we have accumulated content before this heading, it belongs to the previous section
            if current_content and sections:
                prev_heading, prev_content = sections[-1]
                sections[-1] = (prev_heading, prev_content + '\\n' + '\\n'.join(current_content))
                current_content = []

            # Start new section
            sections.append((matched_heading, ''))
            current_content = []
        else:
            current_content.append(line)
        i += 1

    # Add any remaining content to the last section
    if current_content:
        if sections:
            last_heading, last_content = sections[-1]
            sections[-1] = (last_heading, last_content + '\\n' + '\\n'.join(current_content))
        elif not found_any_heading:
            # If no headings were found at all, return the entire text as one section
            # Using the first heading from row_headings as the default
            sections.append((row_headings[0], '\\n'.join(current_content)))

    return sections

def process_intermediate_csv(input_csv: str, output_csv: str):
    """Process the intermediate CSV row by row"""
    final_sections = []

    for chunk in pd.read_csv(input_csv, chunksize=1):
        row = chunk.iloc[0]

        # Get the headings for this specific row
        row_headings = [t.strip() for t in row['titles'].split(';')]

        # Handle both single integer and semicolon-separated string cases for levels
        if isinstance(row['levels'], str):
            row_levels = [int(l) for l in row['levels'].split(';')]
        else:
            # If it's a single number, create a list with that number repeated
            row_levels = [int(row['levels'])] * len(row_headings)

        # Split the text based on just these headings
        sections = split_text_by_headings(row['text'], row_headings)

        # Process sections
        for heading, content in sections:
            # Get the level for this heading
            level = row_levels[row_headings.index(heading)]

            content = content.replace('\n', '\\n').strip()
            final_sections.append({
                'titles': heading,
                'levels': str(level),
                'page': row['page'],
                'text': content
            })

    # Create final DataFrame and save
    final_df = pd.DataFrame(final_sections)
    final_df.to_csv(output_csv, index=False)

    print(f"Created final sections CSV: {output_csv}")
    print(f"Total sections: {len(final_sections)}")

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python split_sections.py <intermediate_csv>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = input_csv.replace('.csv', '_sections.csv')

    process_intermediate_csv(input_csv, output_csv)

if __name__ == "__main__":
    main()