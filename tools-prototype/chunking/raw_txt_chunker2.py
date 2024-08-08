import os, re, sys, csv
import torch
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import nltk

def preprocess(text):
    text = text.replace('\\n', '\\\\n')  # Escape newlines
    text = text.replace('"', '\\"')  # Escape double quotes
    text = text.replace('!', '.')  # Replace exclamation marks with periods
    text = text.replace('%', ' percent')  # Replace percent signs with 'percent'
    result = re.sub(r'\s+', ' ', text)
    result = result.strip()
    return result

# Function to calculate similarity between two sentences
def calculate_similarity(sentence1, sentence2, model):
    embeddings = model.encode([sentence1, sentence2])
    embeddings = torch.from_numpy(embeddings)
    similarity = torch.dot(embeddings[0], embeddings[1]).item()
    return similarity

def split_text(text, similarity_threshold=0.53, min_chunk_size=4500, max_chunk_size=5500):
    model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
    text = re.sub(r'\n(?=[a-z])', ' ', text)
    text = preprocess(text)
    chunks = []
    current_chunk = ''
    sentences = sent_tokenize(text)

    for i, sentence in enumerate(sentences):
        if not current_chunk:
            current_chunk = sentence
        else:
            # Check if adding the next sentence exceeds the max chunk size or not
            if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:  # +1 for the space
                proposed_chunk = current_chunk + ' ' + sentence
                # Check if this is the last sentence or if adding it doesn't make the chunk too similar
                if i == len(sentences) - 1 or calculate_similarity(current_chunk, sentence, model) < similarity_threshold:
                    current_chunk = proposed_chunk
                else:
                    # If adding the sentence makes the chunk too similar, check the current chunk size
                    if len(current_chunk) >= min_chunk_size:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk = proposed_chunk
            else:
                # If adding the sentence exceeds the max chunk size, check the current chunk size
                if len(current_chunk) >= min_chunk_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += ' ' + sentence

    # Handle the last chunk
    if current_chunk:
        if len(chunks) > 0 and len(current_chunk) + len(chunks[-1]) < min_chunk_size:
            # If the last chunk is below the minimum chunk size, append it to the previous chunk if possible
            chunks[-1] += ' ' + current_chunk.strip()
        else:
            chunks.append(current_chunk.strip())

    return chunks

# Function to write chunks and their lengths to a CSV file
def write_to_csv(chunks, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ["Text", "Length"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for chunk in chunks:
            writer.writerow({"Text": chunk, "Length": len(chunk)})

# Main function to process the input text and output chunks with their lengths
def main():
    input_file = sys.argv[1]
    output_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(input_file))[0] + '_chunked2.csv')

    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    chunks = split_text(text)
    write_to_csv(chunks, output_file)

if __name__ == '__main__':
    main()
