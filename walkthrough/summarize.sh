#!/bin/bash
set -e
prompt="Write detailed notes summarizing the entirety of the following text. Use nested bullet points, with headings terms and key concepts in bold, including whitespace to ensure readability. Focus on essential knowledge from this text without adding any external information."

# Preload various prompts for testing and use by calling from second command line argument 
if [ "$#" -gt 0 ]; then
    case "$2" in
        prompt1)
            prompt="Create a detailed bullet-point notes summarizing the entirety of the following text. Use nested bullet points, with headings terms and key concepts in bold, including whitespace to ensure readability. Focus on essential facts, conveyed in this material, without adding any external information."
            ;;
        prompt2)
            prompt="Create bullet-point notes summarizing the important parts of the following text. Use nested bullet points, with headings terms and key concepts in bold, including whitespace to ensure readability. Focus on essential information, without adding anything extra."
            ;;
        prompt3)
            prompt="Create concise bullet-point notes summarizing the important parts of the following text. Use nested bullet points, with headings terms and key concepts in bold, including whitespace to ensure readability. Avoid Repetition."
            ;;
        *)
            ;;
    esac
fi

# Prepare markdown file based on input text file name (first command line argument)
markdown="$1"
markdown="${markdown%.*}.md"
echo "# ${markdown%.*}" > "$markdown"

# read text file line-by-line
while IFS= read -r line
do
  # Remove Surrounding Quotes
  trimmed="${line:1}"
  trimmed="${trimmed%?}"
  # Form JSON Query
  json='{"include_sources": false, "prompt": "'$prompt' TEXT: ```'$trimmed'```", "stream": false, "use_context": false}'
  # Send Api Call, Save response
  content=$(curl -d "$json" -H 'Content-Type: application/json' http://0.0.0.0:8001/v1/completions | jq '.choices[0].message.content')
  
  # Remove Surrounding Quotes
  tcontent="${content:1}"
  tcontent="${tcontent%?}"
  # Remove first character if space
  if [ "${tcontent:0:1}" = " " ]; then
    tcontent="${tcontent:1}"
  fi

  # Trim by keeping only the first 150 characters
  heading="${trimmed:0:150}"
  # Trim by removing any characters after the first plus sign
  heading="${heading%%+*}"
  heading="### $heading"
  # Send to Display
  echo -e "" >> "$markdown"
  echo "$heading" >> "$markdown"
  echo "" >> "$markdown"
  echo -e "$tcontent" >> "$markdown"

  # CSV file
  csv_file="$1"
  csv_file="${csv_file%.*}.csv"
  
  # Check if the CSV file exists
  if [ -e "$csv_file" ]; then
    # If the file exists, find the first empty row and append the variables
    empty_row=$(awk -F, '!$0{print NR; exit}' "$csv_file")
    if [ -n "$empty_row" ]; then
      sed -i "${empty_row}s/$/${line}	${content}/" "$csv_file"
    else
      # If no empty row is found, append a new row at the end
      echo "${line}	${content}" >> "$csv_file"
    fi
  else
    # If the file doesn't exist, create it and add the header and values
    echo "Original	Output" > "$csv_file"
    echo "${line}	${content}" >> "$csv_file"
  fi

  echo
done < $1

