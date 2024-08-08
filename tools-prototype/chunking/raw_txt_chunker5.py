import torch, sys, os
from transformers import BertTokenizer, BertModel
import numpy as np
from scipy.spatial.distance import cosine

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def chunk_text(text, max_length=512):
    """
    Chunk text into smaller parts that fit into BERT's maximum sequence length.
    """
    tokens = tokenizer.tokenize(text)
    chunks = [' '.join(tokens[i:i+max_length]) for i in range(0, len(tokens), max_length)]
    return chunks

def get_embeddings(text_chunks):
    """
    Convert text chunks into embeddings using BERT.
    """
    embeddings = []
    for chunk in text_chunks:
        inputs = tokenizer(chunk, return_tensors='pt', padding=True, truncation=True, max_length=512)
        outputs = model(**inputs)
        # Use the mean of the last hidden state from BERT as the chunk embedding
        chunk_embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        embeddings.append(chunk_embedding)
    return np.vstack(embeddings)

def find_chapter_breaks(embeddings):
    """
    Analyze embeddings to find chapter breaks, based on cosine similarity.
    """
    breaks = []
    for i in range(1, len(embeddings)):
        sim = 1 - cosine(embeddings[i-1], embeddings[i])
        if sim < 0.4:  # Threshold for detecting a new chapter; adjust based on your text
            breaks.append(i)
    return breaks

def main(book_text):
    """
    Main function to process a book text and divide it into chapters.
    """
    # Step 1: Chunk the book text
    text_chunks = chunk_text(book_text)
    
    # Step 2: Convert chunks into embeddings
    embeddings = get_embeddings(text_chunks)
    
    # Step 3: Find chapter breaks
    chapter_breaks = find_chapter_breaks(embeddings)
    
    # Split the original text into chapters based on the breaks
    chapters = []
    start = 0
    for break_point in chapter_breaks:
        end = break_point
        chapter = ' '.join(text_chunks[start:end])
        chapters.append(chapter)
        start = end
    # Add the last chapter
    chapters.append(' '.join(text_chunks[start:]))
    
    return chapters

# Example usage
if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(input_file))[0] + '_chunked5.csv')
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()
    chapters = main(text)
    for i, chapter in enumerate(chapters, 1):
        print(f"Chapter {i}: {chapter[:100]}...")  # Print the first 100 characters of each chapter

