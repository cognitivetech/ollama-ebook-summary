import os
import sys
import re
import csv
from sentence_transformers import SentenceTransformer, util
from pathlib import Path

try:
    max_int = sys.maxsize
    while True:
        # Attempt to set the maximum field size limit, reducing if necessary
        csv.field_size_limit(max_int)
        break
except OverflowError:
    max_int = int(max_int / 10)  # Reduce the size and retry
    csv.field_size_limit(max_int)


def setup_transformer_cache():
    # Set up cache directory in user's home folder
    cache_dir = os.path.join(str(Path.home()), '.cache', 'transformers')
    os.environ['TRANSFORMERS_CACHE'] = cache_dir
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def preprocess_text(text):
    text = text.replace('\\n', ' ')  # Remove newlines
    text = text.replace('"', '\\"')  # Escape double quotes
    text = text.replace('!', '.')  # Replace exclamation marks with periods
    text = text.replace('%', ' percent')  # Replace percent signs with 'percent'
    return text

# Add this at the global scope, outside of any function
_model = None

def get_model():
    global _model
    if _model is None:
        setup_transformer_cache()  # Set up cache before loading model
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def semantic_chunking(text, min_chunk_size=6000, max_chunk_size=9200):
    sentences = [sent.strip() for sent in re.split(r'(?<=[.!?])\s+', text) if sent.strip()]
    model = get_model()  # Use the cached model
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
    output_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(input_file))[0] + '_processed.csv')

    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ['Title', 'Text', 'Character Count']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            short_text = ""
            short_title = ""
            previous_chunk = None

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
                    short_title += title + " - "
                elif char_count < 8000:
                    processed_text = preprocess_text(text)
                    writer.writerow({'Title': title, 'Text': processed_text, 'Character Count': len(processed_text)})
                    short_text = ""
                    short_title = ""
                elif char_count > 8000:
                    processed_text = preprocess_text(text)
                    chunks = semantic_chunking(processed_text)
                    
                    for i, chunk in enumerate(chunks):
                        if i == len(chunks) - 1 and len(chunk) < 2300 and previous_chunk:
                            # Append the last small chunk to the previous chunk
                            combined_chunk = previous_chunk['Text'] + " " + chunk
                            writer.writerow({
                                'Title': previous_chunk['Title'],
                                'Text': combined_chunk,
                                'Character Count': len(combined_chunk)
                            })
                            previous_chunk = None
                        elif i == len(chunks) - 1 and len(chunk) < 2300:
                            # If it's the last chunk and small, but no previous chunk, write it as is
                            writer.writerow({'Title': title, 'Text': chunk, 'Character Count': len(chunk)})
                        else:
                            # Write the current chunk and update previous_chunk
                            if previous_chunk:
                                writer.writerow(previous_chunk)
                            previous_chunk = {'Title': title, 'Text': chunk, 'Character Count': len(chunk)}
                    
                    # Write the last chunk if it wasn't combined
                    if previous_chunk:
                        writer.writerow(previous_chunk)
                        previous_chunk = None
                    
                    short_text = ""
                    short_title = ""

            # Handle any remaining short text
            if short_text:
                writer.writerow({'Title': short_title.rstrip(' | '), 'Text': short_text.strip(), 'Character Count': len(short_text)})

#input_csv = sys.argv[1]
#process_csv(input_csv)

# To this:
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
        process_csv(input_csv)

