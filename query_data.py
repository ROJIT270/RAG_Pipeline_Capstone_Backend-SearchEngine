import os
import asyncio
import json
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# 1. SETUP LOCAL MODEL (Ollama)
# Using host.docker.internal for Docker-to-Host communication
llm = ChatOllama(
    model="llama3.2",
    base_url=os.getenv("OLLAMA_URL", "http://host.docker.internal:11434"),
    temperature=0
)

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. CONNECT TO PINECONE
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

async def search_walled_garden_stream(user_query):
    # --- STEP 1: HyDE ---
    hyde_instruction = "Write a 2-sentence technical academic response to: "
    hyde_resp = await llm.ainvoke(f"{hyde_instruction}\n{user_query}")
    hypothetical_answer = hyde_resp.content.strip()

    # --- STEP 2: VECTOR SEARCH ---
    query_vector = embeddings.embed_query(hypothetical_answer)
    search_results = index.query(vector=query_vector, top_k=5, include_metadata=True)
    matches = search_results['matches']

    # --- STEP 3: THE GATEKEEPER (Consensus Scoring) ---
    if not matches:
        yield json.dumps({"error": "No matches found", "type": "IDK"}) + "\n"
        return

    top_score = matches[0]['score']
    supporting_chunks = [m for m in matches[1:] if m['score'] > 0.60]
    consensus_bonus = len(supporting_chunks) * 0.03
    final_score = top_score + consensus_bonus

    if final_score < 0.75:
        yield json.dumps({
            "answer": "⚠️ [IDK PROTOCOL]: I couldn't find a high-confidence match in the textbooks.",
            "threshold_met": False,
            "score": round(final_score, 4)
        }) + "\n"
        return

    # --- STEP 4: PREPARE CITATIONS ---
    sources = []
    for m in matches:
        if m['score'] > 0.60:
            sources.append({
                "source": m['metadata'].get("source", "Unknown"),
                "page": m['metadata'].get("page_label", "N/A")
            })

    # We send the metadata as the VERY FIRST line of the stream
    yield json.dumps({"type": "metadata", "sources": sources, "score": round(final_score, 4)}) + "\n"

    # --- STEP 5: STREAMING GENERATION ---
    context_str = "\n\n".join([m['metadata']['text'] for m in matches if m['score'] > 0.55])
    final_prompt = rf"""
    ROLE: DSA Academic Assistant. Answer using ONLY the context provided.
    CONTEXT: {context_str}
    QUESTION: {user_query}
    INSTRUCTION: Use LaTeX for math. Use headings and bullets.
    """

    async for chunk in llm.astream(final_prompt):
        # We send the text tokens as they generate
        yield chunk.content

# Removed the "if __name__ == '__main__'" block to keep it clean for the API
