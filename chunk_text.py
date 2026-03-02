import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_chunks():
    # We use a chunk size of 1000 characters with a 100-character overlap
    # to ensure no algorithm logic is cut off mid-sentence.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100,
        separators=["\n--- SOURCE", "\n\n", "\n", " ", ""]
    )

    if not os.path.exists("chunks"):
        os.makedirs("chunks")

    raw_folder = "raw_text"
    for filename in os.listdir(raw_folder):
        if filename.endswith(".txt"):
            print(f"✂️ Chunking: {filename}...")
            
            with open(os.path.join(raw_folder, filename), "r", encoding="utf-8") as f:
                text = f.read()
            
            # This performs the 'Semantic' split
            chunks = splitter.split_text(text)
            
            output_path = os.path.join("chunks", f"{filename.split('.')[0]}_chunks.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                for i, chunk in enumerate(chunks):
                    # We preserve the chunk index for future 'Deep-Link Citations'
                    f.write(f"--- CHUNK {i} ---\n{chunk}\n\n")
            
            print(f"✅ Created {len(chunks)} chunks for {filename}.")

if __name__ == "__main__":
    create_chunks()
