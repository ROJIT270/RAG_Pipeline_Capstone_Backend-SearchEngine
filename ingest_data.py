import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone

# 1. LOAD CONFIG
load_dotenv()
API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# 2. INITIALIZE TOOLS
pc = Pinecone(api_key=API_KEY)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
index = pc.Index(INDEX_NAME)

# 3. YOUR SPECIFIC PATHS & BOOKS
BOOK_DIR = "/home/voidbreathes/Documents/CapstoneModel/Components/Books/"
BOOK_LIST = [
    "ProgrammerHandbook_Antti.pdf",
    "ProblemSolving.pdf",
    "OpenDataStructures_Morin.pdf",
    "AlgorithmsOnStrings_Gusfield.pdf",
    "Algorithms_Jeff.pdf"
]

def ingest_book(filename):
    # Construct the full path
    pdf_path = os.path.join(BOOK_DIR, filename)
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found at: {pdf_path}")
        return

    print(f"📖 Processing {filename}...")
    try:
        loader = PyPDFLoader(pdf_path)
        # Using 1000 char chunks to keep Erickson's and Gusfield's complex 
        # explanations and code blocks intact.
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = splitter.split_documents(loader.load())

        print(f"🧩 {len(docs)} chunks created. Moving to {INDEX_NAME}...")
        
        # Batching for stability on Python 3.14
        batch_size = 50
        for i in range(0, len(docs), batch_size):
            batch = docs[i : i + batch_size]
            vectors = []
            for j, doc in enumerate(batch):
                vector_id = f"{filename}-{i+j}"
                val = embeddings.embed_query(doc.page_content)
                vectors.append({
                    "id": vector_id,
                    "values": val,
                    "metadata": {
                        "text": doc.page_content,
                        "source": filename,
                        "page": doc.metadata.get("page", 0)
                    }
                })
            index.upsert(vectors=vectors)
        print(f"✅ {filename} is securely in the Garden.")
    except Exception as e:
        print(f"⚠️ Error processing {filename}: {e}")

if __name__ == "__main__":
    print(f"--- Starting Ingestion into {INDEX_NAME} ---")
    for book in BOOK_LIST:
        ingest_book(book)
    print("\n🎉 All textbooks are now indexed and ready for retrieval.")
