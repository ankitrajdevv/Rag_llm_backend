import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import google.generativeai as genai

def extract_text(pdf_content):
    """Extract text from PDF content (bytes)"""
    text = ""
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def split_into_chunks(text, max_length=300):
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def get_top_chunks(chunks, query, embed_model=None, top_k=3):
    if embed_model is None:
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embed_model.encode(chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    query_embedding = embed_model.encode([query])
    _, indices = index.search(np.array(query_embedding), k=top_k)
    return [chunks[i] for i in indices[0]]

def ask_llm(context, query):
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text