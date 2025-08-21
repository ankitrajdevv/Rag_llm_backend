import pdfplumber
import numpy as np
import faiss
import google.generativeai as genai
import os
from dotenv import load_dotenv
import io

# -----------------------------
# Setup Gemini
# -----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -----------------------------
# PDF text extraction
# -----------------------------
def extract_text(pdf_source) -> str:
    """
    Extract text from PDF bytes (io.BytesIO) or file path.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_source) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

# -----------------------------
# Chunking
# -----------------------------
def split_into_chunks(text, max_length=1000):
    """
    Split text into smaller chunks so they fit within Gemini's embedding limits.
    max_length is in characters, not tokens (safe limit ~1000 chars).
    """
    words = text.split()
    chunks, current_chunk = [], []

    for word in words:
        if sum(len(w) for w in current_chunk) + len(word) + 1 <= max_length:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# -----------------------------
# Embeddings (Gemini API)
# -----------------------------
def get_embeddings(texts):
    """Generate embeddings for list of texts using Gemini API"""
    model = "models/embedding-001"  # Gemini embedding model
    embeddings = []
    for t in texts:
        resp = genai.embed_content(model=model, content=t)
        embeddings.append(resp['embedding'])
    return np.array(embeddings)

# -----------------------------
# FAISS retrieval
# -----------------------------
def get_top_chunks(chunks, query, top_k=3):
    embeddings = get_embeddings(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    query_embedding = get_embeddings([query])
    _, indices = index.search(query_embedding, k=top_k)
    return [chunks[i] for i in indices[0]]

# -----------------------------
# LLM query (Gemini)
# -----------------------------
def ask_llm(context, query):
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
