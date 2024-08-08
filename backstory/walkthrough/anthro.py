import anthropic
import time
import os
import sys

# For Anthropic Api
# Using filename of txt as command-line argument, this script will output MD and CSV file. this time new rows on CSV to calculate length of input and output and save the time.
def process_documents(input_file):
    with open(input_file, 'r') as file:
        documents = file.readlines()

    client = anthropic.Anthropic(
        api_key="YOUR-ANTROPIC-API-KEY",
    )

    output_file = os.path.splitext(input_file)[0] + "_ant.md"
    csv_file = os.path.splitext(input_file)[0] + "_ant.csv"

    with open(output_file, 'w') as md_file, open(csv_file, 'w') as csv_file:
        csv_file.write("Document,dLen,Output,oLength,Time\n")
        md_file.write(f"# {input_file}\n\n## Anthropic API\n\n")

        for i, document in enumerate(documents):
            time.sleep(2)
            start_time = time.time()
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                temperature=0.3,
                system="You are a bulleted notes specialist.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "```When creating comprehensive bulleted notes, you should follow these guidelines: Use multiple headings based on the referenced topics, not categories like quotes or terms. Headings should be surrounded by bold formatting and not be listed as bullet points themselves. Leave no space between headings and their corresponding list items underneath. Important terms within the content should be emphasized by setting them in bold font. Any text that ends with a colon should also be bolded. Before submitting your response, review the instructions, and make any corrections necessary to adhered to the specified format. Do not reference these instructions within the notes.``` \nBased on the content between backticks create comprehensive bulleted notes."
                            }
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "**Bulleted Note Creation Guidelines**\n\n**Headings**:\n- Based on referenced topics, not categories like quotes or terms\n- Surrounded by **bold** formatting \n- Not listed as bullet points\n- No space between headings and list items underneath\n\n**Emphasis**:\n- **Important terms** set in bold font\n- **Text ending in a colon**: also bolded\n\n**Review**:\n- Ensure adherence to specified format\n- Do not reference these instructions in your response."
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"```{document}``` \\nCreate comprehensive bulleted notes summarizing the content between backticks, with headings and terms in bold."
                            }
                        ]
                    }
                ]
            )

            output = message.content[0].text.strip()
            end_time = time.time()

            # Extract heading from the first 150 characters
            heading = document[:150].lstrip('"').split('+')[0].strip()

            # Write to markdown file
            md_file.write(f"### {heading}\n\n{output}\n\n")

            # Write to CSV file
            csv_file.write(document.strip() + ',' + str(len(document)) + ',"' + output.replace('"', '""').replace('\n', '\\n') + '",' + str(len(output)) + ',' + str(end_time - start_time) + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    process_documents(input_file)
