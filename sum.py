import os
import sys
import csv
import time
import re
import requests
import json

def generate_title(api_base, model, clean, ptitle):
    try:
        response = requests.post(f"{api_base}/generate", json={
            "model": model,
            "prompt": f"```{clean}```\n\n{ptitle}",
            "stream": False
        }, timeout=60)  # Add a timeout to prevent hanging
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        if "response" in result:
            return result["response"].strip()
        else:
            print(f"Unexpected API response format: {result}")
            return None
    except requests.RequestException as e:
        print(f"Error generating title: {str(e)}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding API response: {response.text}")
        return None

def get_unique_title(Title, clean, used_titles, api_base, ptitle):
    if Title not in used_titles:
        used_titles.add(Title)
        return Title, None
    else:
        generated_title = generate_title(api_base, "cognitivetech/obook_title:q3_k_m", clean, ptitle)
        if generated_title:
            return generated_title, generated_title
        else:
            fallback_title = clean[:150].strip() + "..."
            print(f"Title generation failed. Using fallback title: {fallback_title}")
            return fallback_title, fallback_title

def process_file(input_file, model):
    prompt = "Write comprehensive bulleted notes on the provided text."
    ptitle = "write a fewer than 20 words to concisely describe this passage."

    # Set up the Ollama API endpoint
    api_base = "http://localhost:11434/api"

    # Extract filename without extension
    filename = os.path.basename(input_file)
    filename_no_ext, _ = os.path.splitext(filename)

    # Markdown file
    markdown_file = f"{filename_no_ext}_{model}.md"
    with open(markdown_file, "w") as f:
        f.write(f"# {filename_no_ext}\n\n")
        f.write(f"{prompt}\n\n")
        f.write(f"## {model}\n\n")
        
        # Get model information
        response = requests.post(f"{api_base}/show", json={
            "name": model,
        })
        model_info = response.json()
        
        # Write relevant model information
        f.write("### Model Information\n\n")
        if 'details' in model_info:
            for key, value in model_info['details'].items():
                f.write(f"- {key}: {value}\n")
        if 'parameters' in model_info:
            f.write("\n### Parameters\n\n")
            f.write(model_info['parameters'].replace('\n', '\n- '))
        f.write("\n\n")

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
            try:
                response = requests.post(f"{api_base}/generate", json={
                    "model": model,
                    "prompt": f"```{clean}```\n\n{prompt}",
                    "stream": False
                })
                response.raise_for_status()  # This will raise an exception for HTTP errors
                
                response_json = response.json()
                if "response" in response_json:
                    output = response_json["response"].strip()
                else:
                    print(f"Unexpected API response format: {response_json}")
                    output = "Error: Unexpected API response format"
            except requests.RequestException as e:
                print(f"Error making request to API: {str(e)}")
                output = f"Error: {str(e)}"
            except json.JSONDecodeError:
                print(f"Error decoding API response: {response.text}")
                output = "Error: Invalid JSON response from API"

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
                
                unique_title, generated_title = get_unique_title(Title, clean, used_titles, api_base, ptitle)
                if generated_title:
                    heading = f"#### {unique_title}"
                else:
                    heading = f"## {h2_title}\n### {h3_title}"
            else:
                unique_title, generated_title = get_unique_title(Title, clean, used_titles, api_base, ptitle)
                heading = f"### {unique_title}" if not generated_title else f"#### {unique_title}"

            # Append the output to the markdown file
            with open(markdown_file, "a") as f:
                f.write(f"{heading}\n\n")
                f.write(f"{output}\n\n")

            # Format Input + Output for CSV Format
            cout = re.sub(r"\n", "\\\\n", output)
            size = len(cout)

            # Use generated_title if available, otherwise use the original Title
            csv_title = generated_title if generated_title else Title

            # Escape double quotes in csv_title, Text, and cout
            csv_title = re.sub(r'"', '""', csv_title)
            Text = re.sub(r'"', '""', Text)
            cout = re.sub(r'"', '""', cout)

            # Write to CSV file
            with open(csv_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([csv_title, Text, cout, elapsed_time, size])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sum.py <model> <input_file>")
        sys.exit(1)

    model = sys.argv[1]
    input_file = sys.argv[2]

    process_file(input_file, model)
