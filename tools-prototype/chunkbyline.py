import os
import re
import torch
import argparse
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import nltk
import csv

# Ensure NLTK resources are available
nltk.download('punkt')

# Preprocess text by removing extra spaces and trimming
def preprocess(text):
    result = re.sub(r'\s+', ' ', text)
    result = result.strip()
    return result

# Function to calculate similarity between two sentences
def calculate_similarity(sentence1, sentence2, model):
    embeddings = model.encode([sentence1, sentence2])
    embeddings = torch.from_numpy(embeddings)
    similarity = torch.dot(embeddings[0], embeddings[1]).item()
    return similarity

# Function to split text into chunks using dynamic chunking
def split_text(text, min_chunk_size=6500, max_chunk_size=7500):
    chunks = []
    current_chunk = ''

    for sentence in sent_tokenize(text):
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += ' ' + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Function to write chunks and their lengths to a CSV file
def write_to_csv(chunks, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["title", "text", "length"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for chunk in chunks:
            writer.writerow(chunk)

# Function to extract the title from a line and ensure single set of double quotes
def extract_title(line):
    if '+' in line:
        title = line.split('+')[0].strip()[:150]
    else:
        title = line[:150]
    title = title.strip('"')  # Remove any existing double quotes
    return title

def process_markdown(lines, md_level):
    title_content_pairs = []
    current_title = ""
    current_content = ""
    parent_title = ""
    parent_content = ""
    current_level = 0

    for line in lines:
        stripped_line = line.strip()
        heading_match = re.match(r'^(#{1,6})\s+(.*)', stripped_line)
        
        if heading_match:
            hashes, heading_text = heading_match.groups()
            level = len(hashes)

            # If we have content to save
            if current_title and current_content:
                # Save previous section if not a child needing concatenation
                if level <= md_level or (current_level == md_level and len(parent_content) >= 1000):
                    title_content_pairs.append((current_title, current_content.strip()))
                elif current_level > md_level and len(parent_content) < 1000:
                    # Concatenate with parent
                    combined_title = f"{parent_title}. {current_title}"
                    combined_content = f"{parent_content} {current_content}"
                    title_content_pairs.append((combined_title, combined_content.strip()))
                
                # Reset parent content after saving
                parent_title = ""
                parent_content = ""

            # Update current title and content
            if level < md_level:
                parent_title = heading_text
                parent_content = ""
                current_title = heading_text
                current_content = ""
            elif level == md_level:
                current_title = f"{parent_title}. {heading_text}" if parent_title else heading_text
                current_content = ""
            else:
                current_content += f" {heading_text}"

            current_level = level
        else:
            if current_level < md_level:
                parent_content += f" {stripped_line}"
            else:
                current_content += f" {stripped_line}"

    # Add the last section correctly
    if current_title and current_content:
        if len(parent_content) < 1000 and current_level > md_level:
            combined_title = f"{parent_title}. {current_title}"
            combined_content = f"{parent_content} {current_content}"
            title_content_pairs.append((combined_title, combined_content.strip()))
        else:
            title_content_pairs.append((current_title, current_content.strip()))

    return title_content_pairs

# Main function to process the input text and output chunks with their lengths
def main():
    parser = argparse.ArgumentParser(description="Process text or Markdown file and output chunks with their lengths.")
    parser.add_argument('input_file', type=str, help='Path to the input text or Markdown file')
    parser.add_argument('--md', type=int, default=3, help='Markdown heading level to split on (default: 3)')
    args = parser.parse_args()

    input_file = args.input_file
    md_level = args.md
    output_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(input_file))[0] + '_chunkd2.csv')

    # Initialize the sentence transformer model
    model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
    chunks = []

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Determine if the file is Markdown based on file extension
    if input_file.lower().endswith('.md'):
        # Process Markdown
        title_content_pairs = process_markdown(lines, md_level)
    else:
        # Process as plain text, treating each line as a separate entry
        title_content_pairs = []
        for line in lines:
            line = line.strip().replace('!', '.')
            line = line.replace('%', ' percent')  # Replace '%' with ' percent'
            line = line.replace('"', '')  # Remove double quotes from the line
            title = extract_title(line)
            title_content_pairs.append((title, line))

    for title, content in title_content_pairs:
        # Split the content into chunks
        line_chunks = split_text(content)

        # Check if the last chunk is below 2200 characters
        if len(line_chunks) > 1 and len(line_chunks[-1]) < 2200:
            # Combine the last two chunks
            combined_chunk = line_chunks[-2] + ' ' + line_chunks[-1]
            line_chunks = line_chunks[:-2] + [combined_chunk]

        for chunk in line_chunks:
            chunks.append({"title": preprocess(title), "text": preprocess(chunk), "length": len(chunk)})

    write_to_csv(chunks, output_file)
    print(f"Chunking complete. Output saved to {output_file}")

if __name__ == '__main__':
    main()
