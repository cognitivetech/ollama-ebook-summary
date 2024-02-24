#!/bin/bash
MISTRAL_API_KEY={your_key_here}
prompt="Write comprehensive bulleted notes summarizing the following text, with headings and terms in bold. \n\nTEXT: "

# Input file
input_file="$1"

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
echo "Input,Output,Time" >> "$csv_file"

# Loop through each line in the input file
while read -u 9 line; do
    # Remove Surrounding Quotes
    trimmed="${line:1}"
    trimmed="${trimmed%?}"
    clean=$(sed -r 's/"/\"/g; s/\|/I/g' <<< "$trimmed")
    clean=$(sed -r 's/!/\./g' <<< "$clean")

    # Record the start time
    start_time=$(date +%s.%N)

    # Run the command for each line
    output=$(curl --location 'https://api.mistral.ai/v1/chat/completions' --header 'Content-Type: application/json' --header 'Accept: application/json' --header "Authorization: Bearer $MISTRAL_API_KEY" --data "{\"model\": \"mistral-tiny\",\"messages\": [{\"role\": \"user\", \"content\": \"$prompt $clean\"}]}" | jq '.choices[0].message.content')
    # Record the end time
    end_time=$(date +%s.%N)

    # Calculate the processing time
    elapsed_time=$(echo "$end_time - $start_time" | bc)

    # Trim by keeping only the first 150 characters
    heading="${trimmed:0:150}"
    # Trim by removing any characters after the first plus sign
    heading="${heading%%+*}"
    heading="### $heading"

    # Format for Render
    trim="${output:1}"
    trim="${trim%?}"
    # Append the output to the markdown file
    echo "$heading" >> "$markdown_file"
    echo "" >> "$markdown_file"
    echo -e "$trim" >> "$markdown_file"
    echo "" >> "$markdown_file"

    # Format Input + Output for CSV Format
    cout=$(echo "$output" | sed ':a;N;$!ba;s/\n/\\n/g')
    cout=$(echo "$cout" | sed 's/!/./g')
    cout=$(echo "$cout" | sed 's/\\"/""/g')
    trimmed=$(echo "$trimmed" | sed 's/\([^"]\)"\([^"]\|$\)/\1""\2/g')
    trimmed=$(echo "$trimmed" | sed 's/\([^"]\)"\([^"]\|$\)/\1""\2/g')
    # Append input, output, and time to the CSV file
    echo "\"$trimmed\",$cout,\"${elapsed_time%.*}\"" >> "$csv_file"

done 9< "$input_file"

echo "Processing completed. Output saved to $markdown_file and $csv_file."
