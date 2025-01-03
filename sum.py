import os, sys, csv, time, re, json, yaml
import requests, argparse, traceback
from typing import Dict, Any, Tuple, Optional
from urllib.parse import urljoin
from pathlib import Path

class Config:
    """Centralized access to configuration parameters."""

    def __init__(self, config_path: str = None):
        # Use Path for cross-platform path handling
        script_dir = Path(__file__).parent.absolute()

        # Default config path using Path for proper path joining
        if config_path is None:
            config_path = script_dir / "_config.yaml"
        else:
            config_path = Path(config_path)

        self.config = self.load_config(config_path)
        self.prompts = self.config.get('prompts', {})
        self.title_prompt = self.config.get('title_generation', {}).get('prompt', "Default title prompt.")
        self.defaults = self.config.get('defaults', {})

    @staticmethod
    def load_config(config_path: Path) -> dict:
        """Load configuration from a YAML file."""
        try:
            with config_path.open('r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing the configuration file: {e}")
            sys.exit(1)
        except PermissionError:
            print(f"Permission denied when accessing {config_path}")
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

def handle_error(message: str, details: Dict[str, Any] = None, exit: bool = True):
    """
    Handle errors by printing a detailed message and optionally exiting.

    Args:
        message: Main error message
        details: Dictionary containing additional error details
        exit: Whether to exit the program
    """
    print("\n=== ERROR DETAILS ===")
    print(f"Error: {message}")

    if details:
        print("\n--- Additional Details ---")
        for key, value in details.items():
            print(f"{key}: {value}")

    print("=====================\n")

    if exit:
        sys.exit(1)

# -----------------------------
# API Interaction
# -----------------------------

def make_api_request(api_base: str, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Make a POST request to the specified API endpoint with detailed error handling."""
    full_url = urljoin(api_base + "/", endpoint)

    try:
        response = requests.post(full_url, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        error_details = {
            "Request URL": full_url,
            "Request Method": "POST",
            "Request Headers": dict(response.request.headers),
            "Request Payload": payload,
            "Response Status": getattr(response, 'status_code', None),
            "Response Headers": getattr(response, 'headers', {}),
            "Response Body": getattr(response, 'text', ''),
            "Exception Type": type(e).__name__,
            "Exception Message": str(e)
        }
        handle_error("API request failed", error_details, exit=False)

    except json.JSONDecodeError as e:
        error_details = {
            "Request URL": full_url,
            "Request Method": "POST",
            "Request Headers": dict(response.request.headers),
            "Request Payload": payload,
            "Response Status": response.status_code,
            "Response Headers": dict(response.headers),
            "Raw Response": response.text,
            "JSON Error": str(e),
            "JSON Error Position": f"line {e.lineno}, column {e.colno}"
        }
        handle_error("Failed to parse JSON response", error_details, exit=False)

    except Exception as e:
        error_details = {
            "Request URL": full_url,
            "Request Method": "POST",
            "Request Payload": payload,
            "Exception Type": type(e).__name__,
            "Exception Message": str(e),
            "Traceback": traceback.format_exc()
        }
        handle_error("Unexpected error during API request", error_details, exit=False)

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

def get_unique_title(original_title: str, clean_text: str, previous_original_title: str, api_base: str, title_prompt: str, config: Config) -> Tuple[str, bool]:
    """Ensure the title is unique, generate a new one if necessary."""
    if original_title and original_title != previous_original_title:
        return original_title, False

    for _ in range(5):
        generated_title = generate_title(api_base, config.defaults.get('title', 'DEFAULT_TITLE_MODEL'), clean_text, title_prompt, config)
        if generated_title and generated_title != previous_original_title:
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

def write_markdown_entry(md_out, heading: str, content: str, verbose: bool = False):
    """Write a single entry to the Markdown file and optionally print to console."""
    markdown_text = f"{heading}\n\n{content}\n\n"
    md_out.write(markdown_text)
    if verbose:
        print(markdown_text)

def write_csv_header(writer):
    """Write the CSV header with the specified format."""
    writer.writerow(["Chapter", "Heading", "Title", "Text", "Text.len", "Summary", "Summary.len", "Time"])

def write_csv_entry(writer, unique_title: str, text: str, summary: str, elapsed_time: float, is_chapter: bool, heading_level: int):
    """Write entry with the specified format."""
    # Replace newlines with escaped newlines
    escaped_summary = summary.replace('\n', '\\n')
    writer.writerow([
        is_chapter, 
        heading_level, 
        unique_title, 
        text, 
        len(text), 
        escaped_summary, 
        len(summary), 
        elapsed_time
    ])

# -----------------------------
# Processing Logic
# -----------------------------

def process_entry(clean_text: str, title: str, config: Config, previous_original_title: str, api_base: str, model: str, prompt_alias: str, ptitle: str) -> Tuple[str, bool, str, float, int, str]:
    """Process a single text entry and return the processed data."""
    unique_title, was_generated = get_unique_title(title, clean_text, previous_original_title, api_base, ptitle, config)
    
    # Choose the appropriate prompt based on text length
    if len(clean_text) < 1000:
        prompt = config.get_prompt("concise")
        model = config.defaults.get('general', model)  # Falls back to passed model if 'general' not found
    else:
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
    return unique_title, was_generated, output, elapsed_time, size, title  # Return the original title as well

def sanitize_model_name(model: str) -> str:
    # Truncate everything before '/' if present
    model = model.split('/')[-1]
    # Remove special characters without replacement, except '_'
    return re.sub(r'[^a-zA-Z0-9_]+', '', model)

def determine_header_level(row, default_level=3):
    """Determine the header level based on the 'level' column if present."""
    level = row.get('level')
    if level:
        try:
            return int(level)
        except ValueError:
            print(f"Warning: Invalid level value '{level}'. Using default level {default_level}.")
    return default_level

def process_title_with_split(title, level):
    """Process titles containing ` > `, creating appropriate headers."""
    if ' > ' in title:
        parts = title.split(' > ', 1)
        return f"{'#' * level} {parts[0]}\n\n{'#' * (level + 1)} {parts[1]}"
    return f"{'#' * level} {title}"

def process_csv_input(input_file: str, config: Config, api_base: str, model: str, 
                    prompt_alias: str, ptitle: str, markdown_file: str, 
                    csv_file: str, verbose: bool = False, continue_processing: bool = False):
    """Process CSV input files with continuation support."""

    last_processed_text = ""
    mode = "w"

    if continue_processing:
        last_processed_text = get_last_processed_text(csv_file, 'csv')  # Changed from title to text
        if last_processed_text:
            mode = "a"
            print(f"Continuing from text: {last_processed_text[:50]}...")  # Debug line, showing first 50 chars

    with open(csv_file, mode, newline="", encoding='utf-8') as csv_out:
        writer = csv.writer(csv_out)
        seen_titles = set()
        if mode == "w":
            write_csv_header(writer)

        skip_until_found = continue_processing and last_processed_text
        found_last_text = not skip_until_found  # Changed from title to text

        with open(input_file, "r", encoding='utf-8') as csv_in:
            reader = csv.DictReader(csv_in)
            has_level_column = 'level' in reader.fieldnames
            previous_original_title = ""
            current_level = 2

            with open(markdown_file, mode, encoding='utf-8') as md_out:
                if mode == "w":
                    filename_no_ext = os.path.splitext(os.path.basename(input_file))[0]
                    sanitized_model = sanitize_model_name(model)
                    write_markdown_header(md_out, filename_no_ext, model, sanitized_model, api_base)

                for row in reader:
                    text = next((row[key] for key in row if key.lower() == "text"), "").strip()
                    clean = sanitize_text(text)

                    # Skip rows until we find the last processed text
                    if skip_until_found:
                        if clean == last_processed_text:
                            skip_until_found = False
                            found_last_text = True
                            print(f"Found last processed text: {last_processed_text[:50]}...")  # Debug line
                            continue
                        continue

                    if not found_last_text:
                        continue

                    # Process row as normal
                    original_title = next((row[key] for key in row if key.lower() == "title"), "").strip()

                    # Determine if this is a chapter BEFORE title generation
                    is_chapter = original_title and original_title != previous_original_title

                    if original_title == previous_original_title:
                        unique_title, was_generated, output, elapsed_time, size, _ = process_entry(clean, "", config, previous_original_title, api_base, model, prompt_alias, ptitle)
                    else:
                        unique_title, was_generated, output, elapsed_time, size, _ = process_entry(clean, original_title, config, previous_original_title, api_base, model, prompt_alias, ptitle)

                    if has_level_column:
                        base_level = determine_header_level(row)
                    else:
                        base_level = 3  # Default to level 3 if no level column

                    if was_generated:
                        current_level = base_level + 1
                    else:
                        current_level = base_level

                    # Handle split titles
                    if ' > ' in unique_title:
                        parts = unique_title.split(' > ', 1)
                        heading = f"{'#' * current_level} {parts[0]}\n\n{'#' * (current_level + 1)} {parts[1]}"
                    else:
                        heading = f"{'#' * current_level} {unique_title}"

                    write_markdown_entry(md_out, heading, output, verbose)
                    
                    # Add title to seen titles
                    seen_titles.add(unique_title)
                    
                    write_csv_entry(
                        writer,
                        unique_title,
                        clean,
                        output,
                        elapsed_time,
                        is_chapter,
                        current_level
                    )

                    # Update previous_original_title only if the current title wasn't generated
                    if not was_generated:
                        previous_original_title = original_title

def process_text_input(input_file: str, config: Config, api_base: str, model: str, 
                      prompt_alias: str, ptitle: str, markdown_file: str, 
                      csv_file: str, verbose: bool = False, 
                      continue_processing: bool = False):
    """Process plain text input files with continuation support."""
    mode = "a" if continue_processing else "w"
    last_processed_text = ""

    if continue_processing:
        last_processed_text = get_last_processed_text(csv_file, 'txt')  # Changed from title to text
        print(f"DEBUG: Continuing from text: {last_processed_text[:50]}...")

    with open(csv_file, mode, newline="", encoding='utf-8') as csv_out:
        writer = csv.writer(csv_out)
        if mode == "w":
            write_csv_header(writer)

        with open(input_file, "r", encoding='utf-8') as txt_in:
            previous_original_title = ""
            looking_for_start = bool(continue_processing and last_processed_text)
            print(f"DEBUG: looking_for_start initial state: {looking_for_start}")

            with open(markdown_file, mode, encoding='utf-8') as md_out:
                if mode == "w":
                    filename_no_ext = os.path.splitext(os.path.basename(input_file))[0]
                    sanitized_model = sanitize_model_name(model)
                    write_markdown_header(md_out, filename_no_ext, model, sanitized_model, api_base)

                for line in txt_in:
                    trimmed = line.strip().strip('()')
                    clean = sanitize_text(trimmed)
                    extracted_title = clean[:150].strip().split('+')[0].strip()
                    if looking_for_start:
                        if clean == last_processed_text:
                            print("DEBUG: Found matching text, resuming processing")
                            looking_for_start = False
                        else:
                            print("DEBUG: Skipping this text")
                        continue

                    unique_title, was_generated, output, elapsed_time, size, original_title = process_entry(
                        clean, extracted_title, config, previous_original_title, 
                        api_base, model, prompt_alias, ptitle
                    )
                    unique_title = unique_title.strip('"')

                    # Remove the title and the '+' from the text
                    title_pattern = re.escape(unique_title)
                    title_plus_pattern = f'(?:"{title_pattern}"|{title_pattern})\\s*\\+\\s*'
                    clean_text = re.sub(f'^{title_plus_pattern}', '', clean, count=1).strip()

                    heading = f"#### {unique_title}" if was_generated else f"### {unique_title}"
                    write_markdown_entry(md_out, heading, output, verbose)
                    write_csv_entry(writer, unique_title, clean_text, output, elapsed_time, False, 3)

                    previous_original_title = original_title

# -----------------------------
# Continuation logic
# -----------------------------

def get_last_processed_text(csv_file: str, file_type: str) -> str:
    """Get the text of the last processed entry from the CSV file."""
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip header row
            text_col_idx = 3

            last_row = None
            for row in reader:
                if row:  # Skip empty rows
                    last_row = row

            return last_row[text_col_idx] if last_row else ""
    except (FileNotFoundError, IndexError):
        return ""

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
    parser.add_argument('--continue', action='store_true', help='Continue processing from last processed row')
    parser.add_argument('-p', '--prompt', default=config.defaults.get('prompt', 'DEFAULT_PROMPT_ALIAS'), help='Alias of the prompt to use from config')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display markdown output as it is generated')
    parser.add_argument('input_file', nargs='?', help='Input file path')

    args = parser.parse_args()

    if args.help:
        display_help()
        sys.exit(0)

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
    should_continue = getattr(args, 'continue', False)

    filename = os.path.basename(input_file)
    filename_no_ext, _ = os.path.splitext(filename)
    sanitized_model = sanitize_model_name(model)
    markdown_file = f"{filename_no_ext}_{sanitized_model}.md"
    csv_file = f"{filename_no_ext}_{sanitized_model}.csv"

    # Only write fresh markdown header if not continuing
    if not should_continue:
        with open(markdown_file, "w", encoding='utf-8') as md_out:
            write_markdown_header(md_out, filename_no_ext, model, sanitized_model, api_base)

    if processing_mode == 'csv':
        process_csv_input(input_file, config, api_base, model, prompt_alias, 
                        ptitle, markdown_file, csv_file, args.verbose, 
                        should_continue)
    else:
        process_text_input(input_file, config, api_base, model, prompt_alias, 
                        ptitle, markdown_file, csv_file, args.verbose,
                        should_continue)

    print(f"Processing completed. Output saved to {markdown_file} and {csv_file}.")
if __name__ == "__main__":
    main()
