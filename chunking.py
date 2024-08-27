import os
import sys
import re
import csv
from sentence_transformers import SentenceTransformer, util
csv.field_size_limit(sys.maxsize)

def preprocess_text(text):
    text = text.replace('\\n', ' ')  # Remove newlines
    text = text.replace('"', '\\"')  # Escape double quotes
    text = text.replace('!', '.')  # Replace exclamation marks with periods
    text = text.replace('%', ' percent')  # Replace percent signs with 'percent'
    return text

def semantic_chunking(text, min_chunk_size=6000, max_chunk_size=9200):
    sentences = [sent.strip() for sent in re.split(r'(?<=[.!?])\s+', text) if sent.strip()]
    model = SentenceTransformer('all-MiniLM-L6-v2')
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

def process_csv(input_file):
    output_file = os.path.splitext(input_file)[0] + '_processed.csv'

    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ['Title', 'Text', 'Character Count']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            short_text = ""
            short_title = ""

            for row in reader:
                if short_text:
                    title = short_title + row['Title']
                    text = short_text + row['Text']
                    char_count = len(text)
                    short_text = ""
                    short_title = ""
                else:
                    title = row['Title']
                    text = row['Text']
                    char_count = int(row['Character Count'])

                if char_count < 2300:
                    short_text += text + " "
                    short_title += title + " | "
                elif char_count < 8000:
                    processed_text = preprocess_text(text)
                    writer.writerow({'Title': title, 'Text': processed_text, 'Character Count': len(processed_text)})
                    short_text = ""
                    short_title = ""
                elif char_count > 8000:
                    processed_text = preprocess_text(text)
                    chunks = semantic_chunking(processed_text)
                    for chunk in chunks:
                        writer.writerow({'Title': title, 'Text': chunk, 'Character Count': len(chunk)})
                    short_text = ""
                    short_title = ""

input_csv = sys.argv[1]
process_csv(input_csv)