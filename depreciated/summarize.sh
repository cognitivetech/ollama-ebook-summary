#!/bin/bash
# Models: mistralq8, snorkel, openhermis, openhermnc31, openhermnc33s, starling
prompt="Write comprehensive bulleted notes summarizing the following text, with headings, terms, and key concepts in bold. \n\nTEXT: "
#prompt="You are the most sophisticated, semantic routing, large language model known to man. Write comprehensive bulleted notes on the following text, breaking it into hierarchical categories, with headings terms and key concepts in bold.\n\nTEXT: "
#prompt="Make a bulleted list, extract these elements of guided imagery (Characters and their features, Scene, Theme, Components and Intention.) from the following text.\n\nTEXT: "
#prompt="Summarize the following text."
# Check if input file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 input_file"
    exit 1
fi

# Input file
input_file="$2"

# Extract filename without extension
filename=$(basename -- "$input_file")
filename_no_ext="${filename%.*}"

# Markdown file
markdown_file="${filename_no_ext}.md"
echo "# $filename_no_ext" > "$markdown_file"
echo "" >> "$markdown_file"
echo "$prompt" >> "$markdown_file"
echo "" >> "$markdown_file"
echo "## $1" >> "$markdown_file"
echo "" >> "$markdown_file"

# CSV file
csv_file="${filename_no_ext}.csv"

# Clear previous files
echo "Input,$1,Time" >> "$csv_file"

# Loop through each line in the input file
while read -u 9 line; do
    # Remove Surrounding Quotes
    trimmed="${line:1}"
    trimmed="${trimmed%?}"
    clean=$(sed -r 's/"/\"/g; s/\|/I/g' <<< "$trimmed")

    # Record the start time
    start_time=$(date +%s.%N)

    # Run the command for each line
    output=$(ollama run $1 "$prompt $clean")

    # Record the end time
    end_time=$(date +%s.%N)

    # Calculate the processing time
    elapsed_time=$(echo "$end_time - $start_time" | bc)

    # Trim by keeping only the first 150 characters
    heading="${trimmed:0:150}"
    # Trim by removing any characters after the first plus sign
    heading="${heading%%+*}"
    heading="### $heading"

    # Append the output to the markdown file
    echo "$heading" >> "$markdown_file"
    echo "" >> "$markdown_file"
    echo "$output" >> "$markdown_file"
    echo "" >> "$markdown_file"

    # Format Input + Output for CSV Format
    cout=$(echo "$output" | sed ':a;N;$!ba;s/\n/\\n/g')
    cout=$(echo "$cout" | sed 's/\([^"]\)"\([^"]\|$\)/\1""\2/g')
    cout=$(echo "$cout" | sed 's/\([^"]\)"\([^"]\|$\)/\1""\2/g')
    trimmed=$(echo "$trimmed" | sed 's/\([^"]\)"\([^"]\|$\)/\1""\2/g')
    trimmed=$(echo "$trimmed" | sed 's/\([^"]\)"\([^"]\|$\)/\1""\2/g')
    # Append input, output, and time to the CSV file
    echo "\"$trimmed\",\"$cout\",\"${elapsed_time%.*}\"" >> "$csv_file"

done 9< "$input_file"

echo "Processing completed. Output saved to $markdown_file and $csv_file."
