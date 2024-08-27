# If you have a text file, where each section \ chapter is on a single line, then this will chunk each line, one at a time.
import os
import re
import torch
import argparse
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import nltk
import csv

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
def split_text(text, min_chunk_size=6500, max_chunk_size=9200):
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
    with open(output_file, 'w', newline='') as csvfile:
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

# Main function to process the input text and output chunks with their lengths
def main():
    parser = argparse.ArgumentParser(description="Process text file and output chunks with their lengths.")
    parser.add_argument('input_file', type=str, help='Path to the input text file')
    args = parser.parse_args()

    input_file = args.input_file
    output_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(input_file))[0] + '_chunkd2.csv')

    model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
    chunks = []

    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip().replace('!', '.')
            line = line.replace('%', ' percent')  # Replace '%' with ' percent'
            line = line.replace('"', '')  # Remove double quotes from the line
            title = extract_title(line)
            line_chunks = split_text(line)
            for chunk in line_chunks:
                chunks.append({"title": title, "text": chunk, "length": len(chunk)})

    write_to_csv(chunks, output_file)

if __name__ == '__main__':
    main()
