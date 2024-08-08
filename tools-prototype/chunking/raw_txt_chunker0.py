import os
import sys
import re
import csv
from sentence_transformers import SentenceTransformer, util

csv.field_size_limit(sys.maxsize)

def preprocess_text(text):
    text = text.replace('\\n', '\\\\n')  # Remove newlines
    text = text.replace('"', '\\"')  # Escape double quotes
    text = text.replace('!', '.')  # Replace exclamation marks with periods
    text = text.replace('%', ' percent')  # Replace percent signs with 'percent'
    result = re.sub(r'\s+', ' ', text)
    result = result.strip()
    return result

def semantic_chunking(text, model, min_chunk_size=6500, max_chunk_size=8500):
    sentences = [sent.strip() for sent in re.split(r'(?<=[.!?])\s+', text) if sent.strip()]
    embeddings = model.encode(sentences, convert_to_tensor=True)
    
    chunks = []
    current_chunk = []
    current_chunk_size = 0
    
    for i in range(len(sentences)):
        current_chunk.append(sentences[i])
        current_chunk_size += len(sentences[i])
        
        if i == len(sentences) - 1 or current_chunk_size >= min_chunk_size:
            chunk = ' '.join(current_chunk)
            if len(chunk) < 1700 and i < len(sentences) - 1:
                continue
            elif i < len(sentences) - 1:
                similarity = util.cos_sim(embeddings[i], embeddings[i+1]).item()
                if similarity < 0.4 or current_chunk_size >= max_chunk_size:
                    chunks.append(chunk)
                    current_chunk = []
                    current_chunk_size = 0
            else:
                chunks.append(chunk)
    
    return chunks

def process_text_file(input_file, model):
    output_file = f"{os.path.splitext(input_file)[0]}_chunked0.csv"

    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = ['Text', 'Length']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        short_text = ""

        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                if not line.strip():
                    continue

                if short_text:
                    text = short_text + line
                    char_count = len(text)
                    short_text = ""
                else:
                    text = line
                    char_count = len(text)

                if char_count < 2300:
                    short_text += text + " "
                elif char_count < 8000:
                    processed_text = preprocess_text(text)
                    # Remove newlines from the processed_text before writing to CSV
                    processed_text = processed_text.replace('\n', ' ')  # Replace newlines with spaces
                    writer.writerow({'Text': processed_text, 'Length': len(processed_text)})
                    short_text = ""
                elif char_count > 8000:
                    processed_text = preprocess_text(text)
                    chunks = semantic_chunking(processed_text, model)
                    for chunk in chunks:
                        # Remove newlines from the chunk before writing to CSV
                        chunk = chunk.replace('\n', ' ')  # Replace newlines with spaces
                        writer.writerow({'Text': chunk, 'Length': len(chunk)})
                    short_text = ""

if __name__ == '__main__':
    input_text_file = sys.argv[1]
    model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
    process_text_file(input_text_file, model)

