import os
import sys
import csv
import time
import re
import subprocess

def process_file(input_file, model):
    prompt = "Write comprehensive bulleted notes on the provided text."
    ptitle = "write a fewer than 20 words to concisely describe this passage."

    # Extract filename without extension
    filename = os.path.basename(input_file)
    filename_no_ext, _ = os.path.splitext(filename)

    # Markdown file
    markdown_file = f"{filename_no_ext}_{model}.md"
    with open(markdown_file, "w") as f:
        f.write(f"# {filename_no_ext}\n\n")
        f.write(f"{prompt}\n\n")
        f.write(f"## {model}\n\n")
        f.write(subprocess.check_output(["ollama", "show", model, "--template"]).decode())
        f.write("\n")

    # CSV file
    csv_file = f"{filename_no_ext}_summ.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Text", model, "Time", "Len"])

    # Initialize a set to store used titles
    used_titles = set()

    # Loop through each line in the input CSV file
    with open(input_file, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            Title, Text, _ = row  # Ignore the Character Count column
            clean = re.sub(r"!", ".", re.sub(r"%", " percent", Text))

            # Record the start time
            start_time = time.time()

            # Run the command for each line
            output = subprocess.check_output(["ollama", "run", model, f"```{clean}```\n\n{prompt}"]).decode()

            # Record the end time
            end_time = time.time()

            # Calculate the processing time
            elapsed_time = end_time - start_time

            # Check if the title has '|'
            if "|" in Title:
                # Split the title by '|'
                title_parts = Title.split("|")

                # The first part before '|' is the h2 title
                h2_title = title_parts[0]

                # The rest of the parts after the last '|' are joined together to form the h3 title
                h3_title = "|".join(title_parts[1:])

                # Check if the title has been used before
                title_found = False
                for used_title in used_titles:
                    if Title == used_title:
                        title_found = True
                        break

                if not title_found:
                    heading = f"## {h2_title}\n### {h3_title}"
                    used_titles.add(Title)
                else:
                    # Generate a new title using ollama
                    generated_title = subprocess.check_output(["ollama", "run", "obook_title", f"```{clean}``` {ptitle}"]).decode().strip()
                    heading = f"#### {generated_title}"
            else:
                # Check if the title has been used before
                title_found = False
                for used_title in used_titles:
                    if Title == used_title:
                        title_found = True
                        break

                if not title_found:
                    heading = f"### {Title}"
                    used_titles.add(Title)
                else:
                    # Generate a new title using ollama
                    generated_title = subprocess.check_output(["ollama", "run", "obook_title", f"```{clean}```\n\n{ptitle}"]).decode().strip()
                    heading = f"#### {generated_title}"

            # Append the output to the markdown file
            with open(markdown_file, "a") as f:
                f.write(f"{heading}\n\n")
                f.write(f"{output}\n\n")

            # Format Input + Output for CSV Format
            cout = re.sub(r"\n", "\\\\n", output)
            size = len(cout)
            
            # Escape double quotes in Title, Text, and cout
            Title = re.sub(r'(?<!")"', '""', Title)
            Text = re.sub(r'(?<!")"', '""', Text)
            cout = re.sub(r'(?<!")"', '""', cout)
            
            # Append input, output, and time to the CSV file
            with open(csv_file, "a", newline="") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerow([Title, Text, cout, int(elapsed_time), size])

    print(f"Processing completed. Output saved to {markdown_file} and {csv_file}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py model input_file")
        sys.exit(1)

    model = sys.argv[1]
    input_file = sys.argv[2]
    process_file(input_file, model)
