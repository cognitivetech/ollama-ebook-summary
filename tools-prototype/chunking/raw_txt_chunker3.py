import os
import sys
import csv
import re
from sentence_transformers import SentenceTransformer, util
import numpy as np
from nltk.tokenize import sent_tokenize

def calculate_sentence_similarities(text):
    model = SentenceTransformer('mixedbread-ai/mxbai-embed-large-v1')
    sentences = sent_tokenize(text)
    embeddings = model.encode(sentences, convert_to_tensor=True)
    cosine_similarities = util.pytorch_cos_sim(embeddings, embeddings)
    return sentences, cosine_similarities

def segment_into_chapters(sentences, cosine_similarities, similarity_threshold):
    chapters = []
    current_chapter = [sentences[0]]
    
    for i in range(1, len(sentences)):
        # Extract the slice of cosine similarities for the current sentence against all previous ones
        similarity_slice = cosine_similarities[i, :i]
        
        # Convert the tensor slice to a numpy array if it's not already
        if not isinstance(similarity_slice, np.ndarray):
            similarity_slice = similarity_slice.cpu().numpy()
        
        # Calculate the average similarity of the current sentence to all previous sentences in the current chapter
        avg_similarity = np.mean(similarity_slice)
        
        if avg_similarity < similarity_threshold:
            # If the average similarity is below the threshold, start a new chapter
            chapters.append(' '.join(current_chapter))
            current_chapter = [sentences[i]]
        else:
            # Otherwise, add the sentence to the current chapter
            current_chapter.append(sentences[i])
    
    # Add the last chapter
    if current_chapter:
        chapters.append(' '.join(current_chapter))
    
    return chapters

def process_document_into_chapters(text, similarity_threshold):
    sentences, cosine_similarities = calculate_sentence_similarities(text)
    chapters = segment_into_chapters(sentences, cosine_similarities, similarity_threshold)
    return chapters

# Function to write chunks and their lengths to a CSV file
def write_to_csv(chapters, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ["Text", "Length"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for chapter in chapters:
            chunk = chapter
            # Replace all newline characters with spaces
            chunk = re.sub(r'\n', ' ', chunk)
            # Optionally, you can also remove multiple spaces
            chunk = re.sub(r'\s+', ' ', chunk).strip()

            writer.writerow({"Text": chunk, "Length": len(chunk)})

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file> <similarity_threshold>")
        sys.exit(1)

    input_file = sys.argv[1]
    similarity_threshold = 1.2
    output_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(input_file))[0] + '_chunked3.csv')

    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    chapters = process_document_into_chapters(text, similarity_threshold)
    write_to_csv(chapters, output_file)

if __name__ == '__main__':
    main()
