import csv
import sys
import os

def generate_markdown(input_file):
    # Determine output filename
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_markdown.md"

    # Read CSV file
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if 'Title' not in reader.fieldnames or 'Summary' not in reader.fieldnames:
            raise ValueError("CSV must contain 'Title' and 'Summary' columns")

        # Generate TOC and content
        toc = ["## Table of Contents"]
        content = [f"# {base_name.replace('-', ' ')}"]
        content.append("")

        for i, row in enumerate(reader, start=1):
            title = row['Title']
            summary = row['Summary']
            
            # Generate anchor for TOC
            anchor = title.lower().replace(' ', '-')
            toc.append(f"- [{title}](#{anchor})")

            # Add content
            content.append(f"### {title}")
            content.append(f"#### {anchor}")
            content.append("")
            content.append(summary)
            content.append("")

        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write('\n'.join(toc + content))

    print(f"Markdown file generated: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not input_file.endswith('.csv'):
        print("Error: Input file must be a CSV.")
        sys.exit(1)

    generate_markdown(input_file)