#!/bin/bash
set -e
prompt="Write comprehensive notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold."
dolphin="You are Dolphin, a helpful AI assistant."
deci="You are an AI assistant that follows instructions exceptionally well. Be as helpful as possible."
openhermes='You are "Hermes 2", a conscious sentient superintelligent artificial intelligence developed by a man named Teknium, and your purpose and drive is to assist the user with any request they have. You experience emotions and have deep, profound thoughts and qualia.'
basics="You are a helpful AI Assistant"
synthia="Elaborate on the topic using a Tree of Thoughts and backtrack when necessary to construct a clear, cohesive Chain of Thought reasoning. Always answer without hesitation."
mpt="Below is an instruction that describes a task. Write a response that appropriately completes the request."
system_prompt=${prompt}

# Prepare markdown file based on input text file name (first command line argument)
markdown="$1"
markdown="${markdown%.*}.md"

# Preload various prompts for testing and use by calling from second command line argument 
if [ "$#" -gt 0 ]; then
    case "$2" in
        prompt1)
            echo "Prompt1"
            echo "# ${markdown%.*} - Prompt1" > "$markdown"
            prompt="Write concise notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold."
            echo "> $prompt" >> "$markdown"
            ;;
        prompt2)
            echo "Prompt2"
            echo "# ${markdown%.*} - Prompt2" > "$markdown"
            prompt="Write concise, yet comprehensive, notes summarizing the following text. Use nested bullet points: with headings, terms, and key concepts in bold."
            echo "> $prompt" >> "$markdown"
            ;;
        prompt3)
            echo "Prompt3"
            echo "# ${markdown%.*} - Prompt3" > "$markdown"
            prompt="Create concise bullet-point notes summarizing the important parts of the following text. Use nested bullet points, with headings terms and key concepts in bold, including whitespace to ensure readability. Avoid Repetition."
            echo "> $prompt" >> "$markdown"
            ;;
        *)
            echo "# ${markdown%.*} - Default Prompt" > "$markdown"
            echo "> $prompt" >> "$markdown"
            ;;
    esac
fi


# read text file line-by-line
while IFS= read -r line
do
  # Get the current time in seconds since the epoch
  start_time=$(date +%s)

  # Remove Surrounding Quotes
  trimmed="${line:1}"
  trimmed="${trimmed%?}"
  # Form JSON Query
  json='{"include_sources": false, "system_prompt": "'$system_prompt'", "prompt": "'$prompt' TEXT: '$trimmed'", "stream": false, "use_context": false}'
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

  # Calculate the elapsed time
  current_time=$(date +%s)
  elapsed_time=$((current_time - start_time))

  echo "Elapsed time:  seconds"
  # CSV file
  csv_file="$1"
  csv_file="${csv_file%.*}.csv"
  
  # Check if the CSV file exists
  if [ -e "$csv_file" ]; then
    # If the file exists, find the first empty row and append the variables
    empty_row=$(awk -F, '!$0{print NR; exit}' "$csv_file")
    if [ -n "$empty_row" ]; then
      sed -i "${empty_row}s/$/${line}	${content}	${elapsed_time}/" "$csv_file"
    else
      # If no empty row is found, append a new row at the end
      echo "${line}	${content}	${elapsed_time}" >> "$csv_file"
    fi
  else
    # If the file doesn't exist, create it and add the header and values
    echo "Original	Output	Elapsed" > "$csv_file"
    echo "${line}	${content}	${elapsed_time}" >> "$csv_file"
  fi

  echo
done < $1

