import os
import re
import sys
import csv
import torch
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import nltk
from concurrent.futures import ThreadPoolExecutor
from sklearn.decomposition import PCA
import numpy as np

nltk.download('punkt')

def preprocess(text):
    text = text.replace('\\n', '\\\\n')  # Escape newlines
    text = text.replace('"', '\\"')  # Escape double quotes
    text = text.replace('!', '.')  # Replace exclamation marks with periods
    text = text.replace('%', ' percent')  # Replace percent signs with 'percent'
    result = re.sub(r'\s+', ' ', text)
    result = result.strip()
    return result

def calculate_similarity(embeddings, idx1, idx2):
    similarity = torch.dot(embeddings[idx1], embeddings[idx2]).item()
    return similarity

def split_text(text, min_chunk_size=10, max_chunk_size=30):
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

def group_by_similarity(chunks, threshold=0.9, model_name='mixedbread-ai/mxbai-embed-large-v1', max_group_size=5000):
    grouped_chunks = []
    current_group = []
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, convert_to_tensor=True)

    for i, chunk in enumerate(chunks):
        if not current_group:
            current_group.append(chunk)
        else:
            last_chunk_idx = len(current_group) - 1
            similarity = calculate_similarity(embeddings, last_chunk_idx, i)
            if similarity > threshold and len(' '.join(current_group)) + len(chunk) <= max_group_size:
                current_group.append(chunk)
            else:
                grouped_chunks.append(' '.join(current_group))
                current_group = [chunk]

    if current_group:
        grouped_chunks.append(' '.join(current_group))

    return grouped_chunks

def write_to_csv(chunks, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['text', 'length']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for chunk in chunks:
            content = preprocess(chunk)
            length = len(content)
            writer.writerow({'text': content, 'length': length})

def main():
    input_file = sys.argv[1]
    output_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(input_file))[0] + '_chunked1.csv')

    with open(input_file, 'r') as f:
        text = f.read()

    text = re.sub(r'\n(?=[a-z])', ' ', text)

    chunks = split_text(text)
    grouped_chunks = group_by_similarity(chunks)
    write_to_csv(grouped_chunks, output_file)

if __name__ == '__main__':
    main()
