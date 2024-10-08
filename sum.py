import os
import sys
import csv
import time
import re
import json
import requests
import argparse
import yaml
from typing import Dict, Any, Tuple, Optional

# -----------------------------
# Configuration Management
# -----------------------------

class Config:
    """Centralized access to configuration parameters."""

    def __init__(self, config_path: str = "_config.yaml"):
        self.config = self.load_config(config_path)
        self.prompts = self.config.get('prompts', {})
        self.title_prompt = self.config.get('title_generation', {}).get('prompt', "Default title prompt.")
        self.defaults = self.config.get('defaults', {})

    @staticmethod
    def load_config(config_path: str) -> dict:
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing the configuration file: {e}")
            sys.exit(1)

    def get_prompt(self, alias: str) -> str:
        """Retrieve prompt by alias from the configuration."""
        prompt = self.prompts.get(alias, {}).get('prompt')
        if not prompt:
            print(f"Prompt alias '{alias}' not found in configuration.")
            sys.exit(1)
        return prompt

# -----------------------------
# Error Handling
# -----------------------------

def handle_error(message: str, exit: bool = True):
    """Handle errors by printing a message and optionally exiting."""
    print(message)
    if exit:
        sys.exit(1)

# -----------------------------
# API Interaction
# -----------------------------

def make_api_request(api_base: str, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Make a POST request to the specified API endpoint with error handling."""
    try:
        response = requests.post(f"{api_base}/{endpoint}", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        handle_error(f"API request error: {e}", exit=False)
    except json.JSONDecodeError:
        handle_error(f"Invalid JSON response: {response.text}", exit=False)
    return None

# -----------------------------
# Text Sanitization
# -----------------------------

def sanitize_text(text: str) -> str:
    """Sanitize the input text by replacing unwanted characters."""
    #text = re.sub(r'!', '.', text)
    #text = re.sub(r'%', ' percent', text)
    return text.strip()

# -----------------------------
# Title Generation and Uniqueness
# -----------------------------

def generate_title(api_base: str, model: str, clean_text: str, title_prompt: str, config: Config) -> Optional[str]:
    """Generate a unique title using the specified API."""
    payload = {
        "model": model,
        "prompt": f"```{clean_text}```\n\n{title_prompt}",
        "stream": False
    }
    result = make_api_request(api_base, "generate", payload)
    if result:
        return result.get("response", "").strip()
    return None

def get_unique_title(original_title: str, clean_text: str, used_titles: set, api_base: str, title_prompt: str, config: Config) -> Tuple[str, bool]:
    """Ensure the title is unique, generate a new one if necessary."""
    if original_title and original_title not in used_titles:
        used_titles.add(original_title)
        return original_title, False

    for _ in range(5):
        generated_title = generate_title(api_base, config.defaults.get('title', 'DEFAULT_TITLE_MODEL'), clean_text, title_prompt, config)
        if generated_title and generated_title not in used_titles:
            used_titles.add(generated_title)
            return generated_title, True

    # Fallback if all attempts fail
    fallback_title = clean_text[:150].strip() + "..."
    print(f"Title generation failed. Using fallback title: {fallback_title}")
    return fallback_title, True

# -----------------------------
# Text Formatting
# -----------------------------

def bold_text_before_colon(text: str) -> str:
    """Bold any text before the first colon that isn't already bolded."""
    pattern = r'^([ \t]*-[ \t]*)([a-zA-Z].*?):'
    replacement = r'\1**\2:**'
    return re.sub(pattern, replacement, text)

# -----------------------------
# Output Writing
# -----------------------------
def write_markdown_header(md_out, filename_no_ext: str, model: str, sanitized_model: str, api_base: str):
    """Write the initial headers and model information to the Markdown file."""
    md_out.write(f"# {filename_no_ext}\n\n")
    md_out.write(f"## {model}\n\n")  # Use the original model name for display
    
    payload = {"name": model}
    model_info = make_api_request(api_base, "show", payload)
    
    if model_info:
        md_out.write("### Model Information\n\n")
        details = model_info.get('details', {})
        for key, value in details.items():
            md_out.write(f"- **{key}**: {value}\n")
        
        parameters = model_info.get('parameters', "")
        if parameters:
            md_out.write("\n### Parameters\n\n")
            parameters_formatted = parameters.replace('\n', '\n- ')
            md_out.write(f"{parameters_formatted}\n\n")
    else:
        md_out.write("### Model Information\n\n")
        md_out.write("Error retrieving model information.\n\n")

def write_markdown_entry(md_out, heading: str, content: str):
    """Write a single entry to the Markdown file."""
    md_out.write(f"{heading}\n\n{content}\n\n")

def write_csv_header(writer, model: str):
    """Write the header row to the CSV file."""
    writer.writerow(["title", "gen", "text", model, "time", "len"])

def write_csv_entry(writer, unique_title: str, was_generated: bool, text: str, output: str, elapsed_time: float):
    """Write a single row to the CSV file."""
    cout = re.sub(r'\n', '\\\\n', output)
    size = len(cout)
    writer.writerow([unique_title, was_generated, text, cout, elapsed_time, size])

# -----------------------------
# Processing Logic
# -----------------------------

def process_entry(clean_text: str, title: str, config: Config, used_titles: set, api_base: str, model: str, prompt_alias: str, ptitle: str) -> Tuple[str, bool, str, float, int]:
    """Process a single text entry and return the processed data."""
    unique_title, was_generated = get_unique_title(title, clean_text, used_titles, api_base, ptitle, config)
    
    prompt = config.get_prompt(prompt_alias)
    payload = {
        "model": model,
        "prompt": f"```{clean_text}```\n\n{prompt}",
        "stream": False
    }

    start_time = time.time()
    response_json = make_api_request(api_base, "generate", payload)
    end_time = time.time()

    if response_json:
        output = response_json.get("response", "").strip()
    else:
        output = "Error: Failed to generate output."
    
    output = bold_text_before_colon(output)
    elapsed_time = end_time - start_time
    size = len(output)
    
    return unique_title, was_generated, output, elapsed_time, size

def sanitize_model_name(model: str) -> str:
    # Truncate everything before '/' if present
    model = model.split('/')[-1]
    # Remove special characters without replacement, except '_'
    return re.sub(r'[^a-zA-Z0-9_]+', '', model)


def process_csv_input(input_file: str, config: Config, api_base: str, model: str, prompt_alias: str, ptitle: str, markdown_file: str, csv_file: str):
    """Process CSV input files."""
    with open(csv_file, "w", newline="", encoding='utf-8') as csv_out:
        writer = csv.writer(csv_out)
        write_csv_header(writer, model)

        with open(input_file, "r", encoding='utf-8') as csv_in:
            reader = csv.DictReader(csv_in)
            used_titles = set()

            with open(markdown_file, "a", encoding='utf-8') as md_out:
                for row in reader:
                    original_title = next((row[key] for key in row if key.lower() == "title"), "").strip()
                    text = next((row[key] for key in row if key.lower() == "text"), "").strip()
                    clean = sanitize_text(text)

                    unique_title, was_generated, output, elapsed_time, size = process_entry(clean, original_title, config, used_titles, api_base, model, prompt_alias, ptitle)
                    
                    heading = f"#### {unique_title}" if was_generated else f"### {unique_title}"
                    write_markdown_entry(md_out, heading, output)
                    
                    write_csv_entry(writer, unique_title, was_generated, text, output, elapsed_time)

def process_text_input(input_file: str, config: Config, api_base: str, model: str, prompt_alias: str, ptitle: str, markdown_file: str, csv_file: str):
    """Process plain text input files."""
    with open(csv_file, "w", newline="", encoding='utf-8') as csv_out:
        writer = csv.writer(csv_out)
        write_csv_header(writer, model)

        with open(input_file, "r", encoding='utf-8') as txt_in:
            used_titles = set()

            with open(markdown_file, "a", encoding='utf-8') as md_out:
                for line in txt_in:
                    trimmed = line.strip().strip('()')
                    clean = sanitize_text(trimmed)
                    input_length = len(clean)
                    
                    extracted_title = clean[:150].strip().split('+')[0].strip()
                    unique_title, was_generated = get_unique_title(extracted_title, clean, used_titles, api_base, ptitle, config)
                    unique_title = unique_title.strip('"')

                    # Remove the title and the '+' from the text
                    title_pattern = re.escape(unique_title)
                    title_plus_pattern = f'(?:"{title_pattern}"|{title_pattern})\\s*\\+\\s*'
                    clean_text = re.sub(f'^{title_plus_pattern}', '', clean, count=1).strip()

                    prompt = config.get_prompt(prompt_alias)
                    payload = {
                        "model": model,
                        "prompt": f"```{clean_text}```\n\n{prompt}",
                        "stream": False
                    }

                    # Process the entry
                    unique_title, was_generated, output, elapsed_time, size = process_entry(clean_text, unique_title, config, used_titles, api_base, model, prompt_alias, ptitle)
                    
                    heading = f"#### {unique_title}" if was_generated else f"### {unique_title}"
                    write_markdown_entry(md_out, heading, output)
                    
                    write_csv_entry(writer, unique_title, was_generated, clean_text, output, elapsed_time)

# -----------------------------
# Help Display
# -----------------------------

def display_help():
    """Display help message."""
    help_message = """
    Usage: python sum.py [OPTIONS] input_file

    Options:
    -c, --csv        Process a CSV file. Expected columns: Title, Text
    -t, --txt        Process a text file. Each line should be a separate text chunk.
    -m, --model      Model name to use for generation (default from config)
    -p, --prompt     Alias of the prompt to use from config (default from config)
    --help           Show this help message and exit.

    For CSV input:
    - Ensure your CSV has 'Title' and 'Text' columns.

    For Text input:
    - Each line should be a chunk of text surrounded by double quote.

    The output CSV will include:
    - Title: Final title chosen or generated
    - Was_Generated: Boolean indicating if the title was generated
    - Text: Original input text
    - model_name: Generated output
    - Time: Processing time in seconds
    - Len: Length of the output
    """
    print(help_message)

# -----------------------------
# Main Function
# -----------------------------

def main():
    config = Config()
    parser = argparse.ArgumentParser(description="Process and summarize text or CSV files using a specified model.", add_help=False)

    # Optional Arguments
    parser.add_argument('-m', '--model', default=config.defaults.get('summary', 'DEFAULT_SUMMARY_MODEL'), help='Model name to use for generation')
    parser.add_argument('-c', '--csv', action='store_true', help='Process a CSV file')
    parser.add_argument('-t', '--txt', action='store_true', help='Process a text file')
    parser.add_argument('--help', action='store_true', help='Show help message and exit')
    parser.add_argument('-p', '--prompt', default=config.defaults.get('prompt', 'DEFAULT_PROMPT_ALIAS'), help='Alias of the prompt to use from config')

    # Make input_file optional
    parser.add_argument('input_file', nargs='?', help='Input file path')

    args = parser.parse_args()

    if args.help:
        display_help()
        sys.exit(0)

    # Check if input_file is provided when not using --help
    if not args.input_file:
        handle_error("Error: Input file is required when not using --help.")

    if not (args.csv ^ args.txt):
        handle_error("Error: You must specify either --csv or --txt.")

    processing_mode = 'csv' if args.csv else 'txt'
    model = args.model
    input_file = args.input_file
    prompt_alias = args.prompt
    api_base = "http://localhost:11434/api"
    ptitle = config.title_prompt

    filename = os.path.basename(input_file)
    filename_no_ext, _ = os.path.splitext(filename)
    sanitized_model = sanitize_model_name(model)
    markdown_file = f"{filename_no_ext}_{sanitized_model}.md"
    csv_file = f"{filename_no_ext}_{sanitized_model}.csv"

    with open(markdown_file, "w", encoding='utf-8') as md_out:
        write_markdown_header(md_out, filename_no_ext, model, sanitized_model, api_base)

    if processing_mode == 'csv':
        process_csv_input(input_file, config, api_base, model, prompt_alias, ptitle, markdown_file, csv_file)
    else:
        process_text_input(input_file, config, api_base, model, prompt_alias, ptitle, markdown_file, csv_file)

    print(f"Processing completed. Output saved to {markdown_file} and {csv_file}.")

if __name__ == "__main__":
    main()
