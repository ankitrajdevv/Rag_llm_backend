import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import google.generativeai as genai

# Load the embedding model only once
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
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

def get_top_chunks(chunks, query, embed_model_override=None, top_k=3):
    model = embed_model_override or embed_model
    embeddings = model.encode(chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    query_embedding = model.encode([query])
    _, indices = index.search(np.array(query_embedding), k=top_k)
    return [chunks[i] for i in indices[0]]

def ask_llm(context, query):
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nIf the question is not answerable based on the context above, reply with 'Sorry, this question is irrelevant to the uploaded PDF.' Otherwise, provide a helpful answer.\nAnswer:"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def is_question_relevant(chunks, query, threshold=0.4):
    summary_keywords = [
        "summarize", "summary", "summarise", "summarization", "summarise everything",
        "give a summary", "provide a summary", "overview", "main points"
    ]
    lowered_query = query.lower().strip()
    if any(kw in lowered_query for kw in summary_keywords):
        return True, 1.0  # Always relevant for summary requests

    chunk_embeddings = embed_model.encode(chunks)
    query_embedding = embed_model.encode([query])[0]
    similarities = np.dot(chunk_embeddings, query_embedding) / (
        np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding) + 1e-8
    )
    max_similarity = np.max(similarities)
    return max_similarity > threshold, float(max_similarity)