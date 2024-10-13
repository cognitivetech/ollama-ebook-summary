import os, re, torch, nltk, csv
import argparse
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize

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
def split_text(text, min_chunk_size, max_chunk_size):
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
        fieldnames = ["title", "level", "text", "length"]
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

# ... (previous imports and functions remain the same)

def process_markdown(lines, md_level):
    title_content_pairs = []
    current_title = ""
    current_content = ""
    parent_info = []
    current_level = 0

    for line in lines:
        stripped_line = line.strip()
        heading_match = re.match(r'^(#{2,6})\s+(.*)', stripped_line)
        
        if heading_match:
            hashes, heading_text = heading_match.groups()
            level = len(hashes)
            
            # Only process headings at or above the specified md_level
            if level <= md_level:
                # Save previous section if exists
                if current_title:
                    title_content_pairs.append((current_title, current_content.strip(), current_level))
                    if current_content.strip():
                        parent_info[-1] = (parent_info[-1][0], parent_info[-1][1], True, parent_info[-1][3])
                
                # Update current title and level
                while parent_info and parent_info[-1][1] >= level:
                    parent_info.pop()
                
                if parent_info and not parent_info[-1][2] and not parent_info[-1][3]:
                    current_title = f"{parent_info[-1][0]} > {heading_text}"
                    current_level = parent_info[-1][1]
                    parent_info[-1] = (parent_info[-1][0], parent_info[-1][1], parent_info[-1][2], True)
                else:
                    current_title = heading_text
                    current_level = level
                
                parent_info.append((heading_text, level, False, False))
                current_content = ""
            else:
                current_content += f" {stripped_line}"
        else:
            current_content += f" {stripped_line}"
    
    # Add the last section
    if current_title:
        title_content_pairs.append((current_title, current_content.strip(), current_level))
    
    return title_content_pairs

def main():
    parser = argparse.ArgumentParser(description="Process text or Markdown file and output chunks with their lengths.")
    parser.add_argument('input_file', type=str, help='Path to the input text or Markdown file')
    parser.add_argument('--md', type=int, default=3, help='Markdown heading level to split on (default: 3)')
    parser.add_argument('--raw', action='store_true', help='Process the entire file as raw text and chunk it')
    parser.add_argument('-m', '--min', type=int, default=6500, help='Minimum chunk size (default: 6500)')
    parser.add_argument('-x', '--max', type=int, default=7500, help='Maximum chunk size (default: 7500)')
    args = parser.parse_args()

    input_file = args.input_file
    md_level = args.md
    min_chunk_size = args.min
    max_chunk_size = args.max
    output_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(input_file))[0] + '_chunkd2.csv')

    # Initialize the sentence transformer model
    # Initialize the sentence transformer model
    model_name_or_path = 'mixedbread-ai/mxbai-embed-large-v1'

    # Load the model
    model = SentenceTransformer(model_name_or_path)

    # Move the model to the appropriate device (GPU if available, otherwise CPU)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)

    chunks = []

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if args.raw:
        # Process entire file as single continuous block of text 
        content=' '.join([line.strip() for line in lines])
        content=preprocess(content)
 
        # Split raw content into chunks 
        line_chunks=split_text(content,min_chunk_size,max_chunk_size)
 
        for idx,chunk in enumerate(line_chunks,start=1): 
            chunks.append({
                "title":f"Raw Chunk {idx}",
                "text":chunk,
                "length":len(chunk),
                "level":"N/A"
            })
    else:
        # Determine if file is Markdown based on file extension
        if input_file.lower().endswith('.md'):
            if not args.md:
                raise ValueError("Markdown file detected. Please specify the --md flag with the desired heading level.")
            # Process Markdown
            title_content_pairs = process_markdown(lines, md_level)
        else:
            # Process as plain text,treating each line as separate entry 
            title_content_pairs=[]
            for line in lines: 
                line=line.strip().replace('!','.')
                line=line.replace('%',' percent')# Replace '%' with ' percent' 
                line=line.replace('"','')# Remove double quotes from line 
                title=extract_title(line)
                title_content_pairs.append((title,line,"N/A"))
 
        for title,content,current_level in title_content_pairs: 
            # Preprocess content 
            content=preprocess(content)
 
            # Split content into chunks 
            line_chunks=split_text(content,min_chunk_size,max_chunk_size)
 
            # Check if last chunk is below 2200 characters 
            if len(line_chunks)>1 and len(line_chunks[-1])<2200: 
                # Combine last two chunks 
                combined_chunk=line_chunks[-2]+' '+line_chunks[-1]
                line_chunks=line_chunks[:-2]+[combined_chunk]
 
            for chunk in line_chunks: 
                chunks.append({
                    "title":preprocess(title),
                    "text":chunk,
                    "length":len(chunk),
                    "level":current_level,
                })
 
    write_to_csv(chunks,output_file)
    print(f"Chunking complete. Output saved to {output_file}")

if __name__=='__main__':
   main()
