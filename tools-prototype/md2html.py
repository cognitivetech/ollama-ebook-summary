import os
import sys
from markdown import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

# Check if the Markdown file is provided as a command-line argument
if len(sys.argv) < 2:
    print("Please provide the Markdown file as a command-line argument.")
    sys.exit(1)

# Get the Markdown file path from the command-line argument
markdown_file = sys.argv[1]

# Check if the Markdown file exists
if not os.path.isfile(markdown_file):
    print(f"File not found: {markdown_file}")
    sys.exit(1)

# Read the Markdown file
with open(markdown_file, 'r') as file:
    markdown_text = file.read()

# Preprocess the Markdown text to handle bolded lines followed by list items
lines = markdown_text.split('\n')
processed_lines = []
for i in range(len(lines)):
    if lines[i].startswith('**') and lines[i].endswith('**'):
        processed_lines.append(lines[i])
        if i + 1 < len(lines) and lines[i + 1].startswith(('- ', '* ')):
            processed_lines.append('')  # Add a blank line before the list item
    else:
        processed_lines.append(lines[i])

processed_markdown_text = '\n'.join(processed_lines)

# Convert Markdown to HTML
html_text = markdown(processed_markdown_text, extensions=['fenced_code', 'codehilite'])

# Generate the output file name based on the input file name
output_file = os.path.splitext(markdown_file)[0] + '.html'

# Generate the HTML with GitHub-like styling
html_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
    <style>
        .markdown-body {{
            box-sizing: border-box;
            min-width: 200px;
            max-width: 980px;
            margin: 0 auto;
            padding: 45px;
        }}
        @media (max-width: 767px) {{
            .markdown-body {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <article class="markdown-body">
        {content}
    </article>
</body>
</html>
'''

# Highlight code blocks using Pygments
def highlight_code(code, lang):
    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = HtmlFormatter()
    return highlight(code, lexer, formatter)

# Replace code blocks with highlighted code
html_text = html_text.replace('<pre><code>', '<pre><code class="highlight">')
html_text = html_text.replace('</code></pre>', '</code></pre>')

# Generate the final HTML output
final_html = html_template.format(content=html_text)

# Write the HTML output to a file
with open(output_file, 'w') as file:
    file.write(final_html)

print(f"Conversion complete. HTML output saved as {output_file}")
