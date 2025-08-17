import io
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os

# -----------------------------
# Global model + FAISS cache
# -----------------------------
# Load embedding model ONCE (cold start only once per container)
print("[INIT] Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Gemini client (global)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-pro")

# In-memory FAISS indexes {file_id: (index, chunks)}
faiss_indexes = {}


# -----------------------------
# Utils
# -----------------------------
def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber."""
    import pdfplumber

    text = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50):
    """Split text into chunks with overlap."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


def build_index_for_file(file_id: str, chunks: list[str]):
    """Build and cache FAISS index for a given file."""
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    faiss_indexes[file_id] = (index, chunks)
    print(f"[CACHE] Built FAISS index for {file_id}, chunks={len(chunks)}")


def ensure_index_for_file(file_id: str, pdf_bytes: bytes = None):
    """Ensure FAISS index exists (build from bytes if missing)."""
    if file_id in faiss_indexes:
        return faiss_indexes[file_id]

    if pdf_bytes:
        text = extract_text_from_bytes(pdf_bytes)
        chunks = split_into_chunks(text)
        build_index_for_file(file_id, chunks)
        return faiss_indexes[file_id]

    raise ValueError(f"No cached index and no pdf_bytes provided for {file_id}")


def get_top_chunks(file_id: str, query: str, k: int = 5):
    """Return top-k matching chunks from FAISS."""
    if file_id not in faiss_indexes:
        raise ValueError(f"No FAISS index for {file_id}")

    index, chunks = faiss_indexes[file_id]
    query_emb = embedding_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_emb, k)
    return [chunks[i] for i in I[0] if i < len(chunks)]


def ask_llm(context: str, query: str) -> str:
    """Call Gemini with context + query."""
    prompt = f"Answer the question based on the following context:\n\n{context}\n\nQuestion: {query}"
    response = gemini_model.generate_content(prompt)
    return response.text.strip()
