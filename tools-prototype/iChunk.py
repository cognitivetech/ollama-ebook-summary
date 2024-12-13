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

def split_text(text, min_chunk_size, max_chunk_size):
    chunks = []
    current_chunk = ''

    # Split by sentence
    for sentence in sent_tokenize(text):
        # If a single sentence is too large, split it further
        while len(sentence) > max_chunk_size:
            split_point = sentence[:max_chunk_size].rfind(' ')  # Find the last space before max_chunk_size
            if split_point == -1:  # No spaces found, force split at max_chunk_size
                split_point = max_chunk_size
            chunks.append(sentence[:split_point].strip())
            sentence = sentence[split_point:].strip()

        # Add sentence to current chunk
        if len(current_chunk) + len(sentence) > max_chunk_size:
            # Finish the current chunk if it exceeds max_chunk_size
            if len(current_chunk) >= min_chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # If current_chunk is too small, combine it with the next sentence
                current_chunk += ' ' + sentence
        else:
            current_chunk += ' ' + sentence

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())

    # Debug: Display chunk sizes for verification
    print(f"Chunks created: {[len(chunk) for chunk in chunks]}")

    return chunks

# Function to write chunks and their lengths to a CSV file
def write_to_csv(chunks, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["title", "level", "text", "length"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # Debug: Print final chunk details
        for i, chunk in enumerate(chunks):
            print(f"Final Chunk {i+1}: Title={chunk['title']}, Length={chunk['length']}")
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
    """
    Process markdown content and create title-content pairs based on heading levels.
    
    Args:
        lines (list): List of strings containing markdown content
        md_level (int): Maximum heading level to process (2-6)
    
    Returns:
        list: List of tuples (title, content, level)
    """
    title_content_pairs = []
    current_title = ""
    current_content = ""
    parent_info = []  # Tracks (heading_text, level, has_content, used_as_parent)
    current_level = 0
    
    # Input validation
    if not isinstance(md_level, int) or not (2 <= md_level <= 4):
        raise ValueError(f"md_level must be between 2 and 6, got {md_level}")
    
    try:
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            heading_match = re.match(r'^(#{2,6})\s+(.*)', stripped_line)
            
            if heading_match:
                hashes, heading_text = heading_match.groups()
                level = len(hashes)
                
                # Only process headings at or above the specified md_level
                if level <= md_level:
                    # Save previous section if exists
                    if current_title and current_content.strip():
                        title_content_pairs.append((
                            current_title,
                            current_content.strip(),
                            current_level
                        ))
                        if parent_info:
                            parent_info[-1] = (
                                parent_info[-1][0],
                                parent_info[-1][1],
                                True,  # Mark as having content
                                parent_info[-1][3]
                            )
                    
                    # Update parent_info stack based on heading level
                    while parent_info and parent_info[-1][1] >= level:
                        parent_info.pop()
                    
                    # Handle nested headings
                    if parent_info and not parent_info[-1][2] and not parent_info[-1][3]:
                        # Create hierarchical title with parent
                        current_title = f"{parent_info[-1][0]} > {heading_text}"
                        current_level = parent_info[-1][1]
                        # Mark parent as used
                        parent_info[-1] = (
                            parent_info[-1][0],
                            parent_info[-1][1],
                            parent_info[-1][2],
                            True
                        )
                    else:
                        current_title = heading_text
                        current_level = level
                    
                    # Add new heading to parent_info
                    parent_info.append((heading_text, level, False, False))
                    current_content = ""
                else:
                    current_content += f" {stripped_line}"
            else:
                current_content += f" {stripped_line}"
        
        # Add the final section if it exists
        if current_title and current_content.strip():
            title_content_pairs.append((
                current_title,
                current_content.strip(),
                current_level
            ))
        
        # Debug information
        print(f"Processed {len(lines)} lines")
        print(f"Created {len(title_content_pairs)} title-content pairs")
        
        return title_content_pairs
    
    except Exception as e:
        print(f"Error processing markdown at line {line_num}: {str(e)}")
        raise

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
        # In the main function, replace the current markdown processing with:
        if args.md:
            # Process Markdown
            title_content_pairs = process_markdown(lines, md_level)
            
            # Add this section to properly create chunks from title_content_pairs
            for title, content, level in title_content_pairs:
                # Preprocess content
                content = preprocess(content)
                
                # Split content into chunks if needed
                if len(content) > max_chunk_size:
                    line_chunks = split_text(content, min_chunk_size, max_chunk_size)
                    for idx, chunk in enumerate(line_chunks):
                        chunks.append({
                            "title": f"{title}",
                            "text": chunk,
                            "length": len(chunk),
                            "level": str(level)
                        })
                else:
                    chunks.append({
                        "title": title,
                        "text": content,
                        "length": len(content),
                        "level": str(level)
                    })
        else:
            # Process as plain text, treating each line as separate entry 
            for line in lines: 
                line = line.strip().replace('!','.').replace('%',' percent').replace('"','')
                
                # Extract title and content
                if '+' in line[:150]:
                    title, content = line.split('+', 1)
                    title = title.strip()
                else:
                    title = line[:150].strip()
                    content = line
                    
                # Debug prints
                print(f"Title: {title}")
                print(f"Content length before chunking: {len(content)}")
                
                # Preprocess content 
                content = preprocess(content)
                
                # Split content into chunks 
                line_chunks = split_text(content, min_chunk_size, max_chunk_size)
                print(f"Number of chunks created: {len(line_chunks)}")
                
                # Check if last chunk is below 2200 characters 
                if len(line_chunks) > 1 and len(line_chunks[-1]) < 2200: 
                    print("Combining small last chunk")
                    # Combine last two chunks 
                    combined_chunk = line_chunks[-2] + ' ' + line_chunks[-1]
                    line_chunks = line_chunks[:-2] + [combined_chunk]
                
                for chunk in line_chunks: 
                    chunks.append({
                        "title": preprocess(title),
                        "text": chunk,
                        "length": len(chunk),
                        "level": "N/A"
                    })
 
    write_to_csv(chunks,output_file)
    print(f"Chunking complete. Output saved to {output_file}")

if __name__=='__main__':
   main()
