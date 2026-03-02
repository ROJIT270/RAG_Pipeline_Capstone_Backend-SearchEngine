import fitz  # PyMuPDF
import os

# 1. THE EXACT PATH YOU PROVIDED
BOOK_DIR = "/home/voidbreathes/Documents/CapstoneModel/Components/Books/"

# 2. THE EXACT NAMES YOU PROVIDED
books = [
    "OpenDataStructures_Morin.pdf",
    "Algorithms_Jeff.pdf",
    "ProblemSolving.pdf",
    "ProgrammerHandbook_Antti.pdf",
    "AlgorithmsOnStrings_Gusfield.pdf"
]

def extract_and_clean():
    # Create the output folder in your current working directory
    if not os.path.exists("raw_text"):
        os.makedirs("raw_text")

    for book_name in books:
        # Combine path and filename
        full_path = os.path.join(BOOK_DIR, book_name)
        
        if not os.path.exists(full_path):
            print(f"⚠️ Warning: {full_path} not found. Check the path!")
            continue
        
        print(f"📖 Processing: {book_name}...")
        doc = fitz.open(full_path)
        output_file = os.path.join("raw_text", f"{book_name.split('.')[0]}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                
                # Cleaning: Removing potential headers/footers
                lines = text.split('\n')
                if len(lines) > 4:
                    cleaned_text = '\n'.join(lines[2:-2])
                else:
                    cleaned_text = text
                
                # Write with citation metadata
                f.write(f"\n--- SOURCE: {book_name} | PAGE: {page_num + 1} ---\n")
                f.write(cleaned_text)
        
        print(f"✅ Saved to: {output_file}")

if __name__ == "__main__":
    extract_and_clean()
