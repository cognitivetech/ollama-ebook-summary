#!/bin/bash
# combine all python file to single file for upload to GPT

output_file="project.txt"

# Counter to keep track of the order
file_counter=1

# Clear the output file if it already exists
> "$output_file"

# Loop through all python files in the current directory
for file in *.py; do
    # Check if the file is a regular file
    if [ -f "$file" ]; then
        # Write the file name and order to the output file
        echo "File #$file_counter: $file" >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
        
        # Append the content of the python file to the output file
        cat "$file" >> "$output_file"
        
        # Add a separator between files
        echo -e "\n\n" >> "$output_file"
        
        # Increment the file counter
        ((file_counter++))
    fi
done

echo "All Python files have been combined into $output_file"
