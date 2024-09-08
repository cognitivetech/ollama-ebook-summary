import os
import sys
import csv
import time
import re
import requests
import json

# Add your OpenRouter API key here
OPENROUTER_API_KEY = "your_openrouter_api_key_here"

def generate_title(clean, ptitle):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
            json={
                "model": "nousresearch/hermes-3-llama-3.1-405b",
                "messages": [
                    {"role": "user", "content": f"```{clean}```\n\n{ptitle}"}
                ]
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"Unexpected API response format: {result}")
            return None
    except requests.RequestException as e:
        print(f"Error generating title: {str(e)}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding API response: {response.text}")
        return None

def get_unique_title(Title, clean, used_titles, ptitle):
    if Title not in used_titles:
        used_titles.add(Title)
        return Title, None
    else:
        generated_title = generate_title(clean, ptitle)
        if generated_title:
            return generated_title, generated_title
        else:
            fallback_title = clean[:150].strip() + "..."
            print(f"Title generation failed. Using fallback title: {fallback_title}")
            return fallback_title, fallback_title

def make_api_call(clean, prompt):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                },
                json={
                    "model": "mattshumer/reflection-70b:free",
                    "messages": [
                        {"role": "user", "content": f"```{clean}```\n\n{prompt}"}
                    ]
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            print(f"Error in API call (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Max retries reached. Skipping this API call.")
                return None

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
        
        # Write model information
        f.write("### Model Information\n\n")
        f.write(f"- Model: {model}\n")
        f.write("- API: OpenRouter\n\n")

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

            # Make the API call
            output = make_api_call(clean, prompt)

            if output is None:
                continue  # Skip this iteration if the API call failed

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
                
                unique_title, generated_title = get_unique_title(Title, clean, used_titles, ptitle)
                if generated_title:
                    heading = f"#### {unique_title}"
                else:
                    heading = f"## {h2_title}\n### {h3_title}"
            else:
                unique_title, generated_title = get_unique_title(Title, clean, used_titles, ptitle)
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

            # Wait for 2 seconds before the next API call
            time.sleep(2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sum.py <model> <input_file>")
        sys.exit(1)

    model = sys.argv[1]
    input_file = sys.argv[2]

    process_file(input_file, model)
