# Naive attempt to get toc from raw text... sodeday maybe
import re
import sys

def extract_toc(raw_text):
    # Split the raw text into lines
    lines = raw_text.split('\n')
    
    # Initialize variables
    toc_items = []
    toc_started = False
    first_toc_item = None
    
    for line in lines:
        # Check if the TOC section has started
        if not toc_started:
            if re.search(r'CONTENTS', line, re.IGNORECASE):
                toc_started = True
            continue
        
        if toc_started:
            # Clean up the line to extract titles
            cleaned_line = re.sub(r'^\s*[\d\.\-]*\s*', '', line).strip()
            cleaned_line = re.sub(r'\s*[\d\.\-]*\s*$', '', cleaned_line).strip()
            
            # If the cleaned line is empty, skip it
            if not cleaned_line:
                continue
            
            # If this is the first TOC item, remember it
            if first_toc_item is None:
                first_toc_item = cleaned_line
            
            # Check if the current line contains the first TOC item (outside of the TOC)
            # This check is only meaningful after the first TOC item has been identified
            if first_toc_item in cleaned_line:
                break  # End the TOC extraction
            
            toc_items.append(cleaned_line)
    
    return toc_items

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <raw_text>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    with open(input_file, 'r', encoding='utf-8') as file:
        raw_text = file.read()

    toc_items = extract_toc(raw_text)
    print(toc_items)

if __name__ == "__main__":
    main()
