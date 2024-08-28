import csv
import sys
import os

def process_csv(input_file):
    # Generate output filename
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}.md"

    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile, \
         open(output_file, 'w', encoding='utf-8') as mdfile:
        
        reader = csv.DictReader(csvfile)
        
        # Write the H1 title
        mdfile.write(f"# {base_name.replace('-', ' ').title()}\n\n")
        
        for row in reader:
            # Write H3 for Title
            mdfile.write(f"### {row['Title']}\n")
            # Write Summary
            mdfile.write(f"{row['Summary']}\n\n")
            # Add a single line break after each entry
            mdfile.write("---\n\n")

    print(f"Markdown file '{output_file}' has been created.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not input_file.endswith('.csv'):
        print("Error: Input file must be a CSV file.")
        sys.exit(1)
    
    process_csv(input_file)
