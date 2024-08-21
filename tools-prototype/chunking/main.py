import sys
import os
import importlib

def load_chunker(module_name):
    module = importlib.import_module(module_name)
    class_ = getattr(module, module_name.capitalize())
    return class_()

def main():
    input_file = sys.argv[1]
    chunker_name = sys.argv[2]  # e.g., "semantic_chunker"

    chunker = load_chunker(chunker_name)
    output_file = os.path.splitext(input_file)[0] + f'_chunked_{chunker.id}.csv'

    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # Preprocess and chunk text
    text = chunker.preprocess_text(text)
    chunks = chunker.chunk_text(text)

    # Assume the function to write chunks to CSV is implemented here
    # For demonstration, let's just print the output file name after processing
    print(f"Processing complete. Output saved to: {output_file}")

if __name__ == '__main__':
    main()
