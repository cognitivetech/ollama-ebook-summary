import sys
import PyPDF2
import pprint

print(f"PyPDF2 version: {PyPDF2.__version__}")

def print_pdf_info(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"## PDF Information for: {pdf_path}\n")
            
            # Print metadata
            print("### Metadata:")
            metadata = pdf_reader.metadata
            if metadata:
                for key, value in metadata.items():
                    print(f"{key}: {value}")
            else:
                print("No metadata found.")
            print()
            
            # Print raw metadata
            print("### Raw Metadata:")
            print(pdf_reader.metadata)
            print()
            
            # Print table of contents
            print("### Table of Contents:")
            toc = pdf_reader.outline
            if toc:
                print("Raw Outline Structure:")
                pprint.pprint(toc)
                print()
                print_toc(toc)
            else:
                print("No table of contents found.")
            
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
    except PyPDF2.errors.PdfReadError:
        print(f"Error: '{pdf_path}' is not a valid PDF file or is encrypted.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

def print_toc(toc, level=0):
    for item in toc:
        print(f"{'  ' * level}Type: {type(item)}")
        if isinstance(item, PyPDF2.generic.Destination):
            print(f"{'  ' * level}- {item.title} (Destination)")
        elif isinstance(item, dict):
            print(f"{'  ' * level}- {item.get('title', 'Untitled')} (Dict)")
            if 'children' in item:
                print_toc(item['children'], level + 1)
        elif isinstance(item, list):
            print(f"{'  ' * level}- List item:")
            print_toc(item, level + 1)
        elif hasattr(item, '__iter__') and not isinstance(item, str):
            print(f"{'  ' * level}- Iterable item:")
            print_toc(item, level + 1)
        else:
            print(f"{'  ' * level}- Unknown item type: {item}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_pdf_file>")
    else:
        pdf_path = sys.argv[1]
        try:
            print_pdf_info(pdf_path)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
