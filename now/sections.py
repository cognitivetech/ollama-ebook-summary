# split_sections.py
# Created/Modified files during execution:
# ["split_sections.py"]

import csv, re, sys, pandas as pd
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional
import re
import logging

# Configure logging at the beginning of your script
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of log messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Logs will be output to the console
        # You can also log to a file by uncommenting the next line
        # logging.FileHandler('debug.log'),
    ]
)

import sys
from typing import List, Tuple

# If using "thefuzz":
from thefuzz import fuzz

# If using sentence-transformers for embeddings:
from sentence_transformers import SentenceTransformer, util

# Initialize a global embedding model once per script run
model = None
def get_embedding_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def compute_similarity(line: str, heading: str, method: str = 'fuzzy', fuzzy_threshold: int = 80, embed_threshold: float = 0.90) -> bool:
    """
    Determines if 'line' matches 'heading' based on a selected method.
    Now handles variations in number formatting (e.g., "6.Research" vs "6 Research")
    """
    # Normalize number formatting in both strings
    def normalize_numbers(s):
        # Replace patterns like "6." or "6 " with "6 "
        return re.sub(r'(\d+)[.\s]+', r'\1 ', s)

    line_norm = normalize_numbers(line)
    heading_norm = normalize_numbers(heading)

    if method == 'fuzzy':
        ratio = fuzz.ratio(line_norm.lower(), heading_norm.lower())
        return (ratio >= fuzzy_threshold)
    elif method == 'embedding':
        embed_model = get_embedding_model()
        line_vec = embed_model.encode(line_norm, convert_to_tensor=True)
        head_vec = embed_model.encode(heading_norm, convert_to_tensor=True)
        cos_sim = float(util.cos_sim(line_vec, head_vec)[0][0])
        return (cos_sim >= embed_threshold)
    else:
        raise ValueError(f"Unknown similarity method '{method}'")

def normalize_headings(text: str) -> str:
    """
    Normalize headings in the text to ensure they are properly formatted.
    """
    # Add a newline before headings that start with a number followed by a period
    text = re.sub(r'(\d+\.\s*[A-Za-z])', r'\n\1', text)
    return text

def split_text_by_headings(
    text: str,
    row_headings: List[str],
    method: str = 'fuzzy',
    fuzzy_threshold: int = 80,
    embed_threshold: float = 0.90
) -> List[Tuple[str, str]]:
    """
    Split text into sections based on the *strictly ordered* list of row_headings.
    The first heading is assumed to start at the beginning of the text.

    Args:
        text (str): The entire text content to split.
        row_headings (List[str]): Ordered list of headings that must appear in sequence.
        method (str): "fuzzy" or "embedding" to determine how headings are matched.
        fuzzy_threshold (int): The minimum fuzz.ratio threshold (0-100).
        embed_threshold (float): The minimum cosine similarity for embeddings (0.0-1.0).

    Returns:
        List[Tuple[str, str]]: List of (heading, text_section) pairs in the order matched.
    """
    logging.debug("Starting split_text_by_headings (fuzzy/embedding) with ordered headings.")

    # Normalize the text to ensure headings are properly formatted
    text = normalize_headings(text)

    lines = text.replace('\\n', '\n').split('\n')
    lines = [ln.strip() for ln in lines if ln.strip()]  # remove blank lines

    sections: List[Tuple[str, str]] = []

    # Initialize with the first heading, assuming it starts at the beginning
    current_heading_idx = 0
    sections.append((row_headings[0], ""))  # Add first heading
    current_heading_idx += 1

    # Set up for finding the next heading
    current_heading = row_headings[current_heading_idx] if current_heading_idx < len(row_headings) else None
    current_content_lines: List[str] = []

    logging.debug(f"Ordered Headings to find: {row_headings}")

    for line_num, line in enumerate(lines, start=1):
        # If we already matched all headings, remaining lines belong to the last heading
        if current_heading_idx >= len(row_headings):
            current_content_lines.append(line)
            continue

        # Check if this line matches the next required heading
        is_match = compute_similarity(
            line=line,
            heading=current_heading,
            method=method,
            fuzzy_threshold=fuzzy_threshold,
            embed_threshold=embed_threshold
        )

        if is_match:
            # Finalize the previous heading's content
            prev_heading, prev_text = sections[-1]
            combined_text = prev_text
            if current_content_lines:
                if combined_text:
                    combined_text += '\\n'
                combined_text += '\\n'.join(current_content_lines)
            sections[-1] = (prev_heading, combined_text)

            # Start a new section for the newly found heading
            sections.append((current_heading, ""))
            current_content_lines = []
            current_heading_idx += 1

            # Update current_heading to the next one if available
            if current_heading_idx < len(row_headings):
                current_heading = row_headings[current_heading_idx]
        else:
            # Not a match -> belongs to the current heading's content
            current_content_lines.append(line)

    # Finished iterating lines.
    # If we found all headings, finalize the last heading's content
    if current_heading_idx >= len(row_headings):
        # Append any leftover lines to the final heading
        if sections:
            final_heading, final_text = sections[-1]
            if final_text and current_content_lines:
                final_text += '\\n'
            final_text += '\\n'.join(current_content_lines)
            sections[-1] = (final_heading, final_text)
    else:
        # We haven't found all required headings
        missing_headings = row_headings[current_heading_idx:]
        msg = (
            f"Not all required headings were located in the text.\n"
            f"Found headings up to index {current_heading_idx-1}, "
            f"but missing: {missing_headings}.\n"
            "Please investigate or adjust thresholds."
        )
        raise Exception(msg)

    logging.debug(f"Completed split_text_by_headings. Created {len(sections)} sections.")
    return sections

def get_text_length(text: str) -> int:
    """Helper function to get consistent text length measurement"""
    return len(text.replace('\\n', '\n'))

def find_split_point(text: str, target_length: int) -> int:
    """Find appropriate point to split text, preferring natural breaks"""
    if target_length >= len(text):
        return len(text)

    # Replace escaped newlines with actual newlines for splitting logic
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
            current_text = df.iloc[i]['text']

            # ------------------------------------------------------
            # BEGIN UPDATED LOGIC for detecting the earliest full heading in next_text
            if i + 1 < len(df):
                next_row = df.iloc[i + 1]
                next_text = next_row['text']
                next_titles = next_row['titles'].split(';')

                # Attempt to detect the earliest heading position in next_text via fuzzy match
                candidate_lines = next_text.splitlines()
                first_heading_pos = None
                best_match_pos = None
                best_match_ratio = 0

                # Try each heading in the next row
                for heading in next_titles:
                    heading_str = heading.strip()
                    for cand_line in candidate_lines:
                        # Make sure we don't feed empty or purely whitespace lines
                        if not cand_line.strip():
                            continue

                        # Use compute_similarity with a slightly higher threshold 
                        # to avoid partial matches like "3."
                        if compute_similarity(cand_line, heading_str, method='fuzzy', fuzzy_threshold=85):
                            # If it's a match, check the ratio
                            ratio = fuzz.ratio(cand_line.lower(), heading_str.lower())
                            if ratio > best_match_ratio:
                                best_match_ratio = ratio
                                best_match_pos = next_text.index(cand_line)
                    # If we found a best match for this heading, break to preserve ordering
                    if best_match_pos is not None:
                        first_heading_pos = best_match_pos
                        break

                # If we found a heading match somewhere in next_text
                if first_heading_pos is not None and first_heading_pos > 0:
                    preceding_text = next_text[:first_heading_pos].strip()
                    if preceding_text:
                        # This preceding text belongs to the current row
                        current_text = current_text + '\\n' + preceding_text
                    # Update next row's text to remove the preceding portion
                    df.at[i + 1, 'text'] = next_text[first_heading_pos:].strip()
            # ------------------------------------------------------

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

def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Process CSV file to split sections')
    parser.add_argument('input_csv', help='Input CSV file')
    parser.add_argument('--full', action='store_true', 
                      help='Unwind sections back to original pages')

    args = parser.parse_args()

    output_csv = args.input_csv.replace('.csv', '_sections.csv')
    process_intermediate_csv(args.input_csv, output_csv, unwind_pages=args.full)

if __name__ == "__main__":
    main()