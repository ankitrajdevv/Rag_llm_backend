import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from google import genai

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Load document
with open("notes.txt", "r", encoding="utf-8") as f:
    document_text = f.read()

# Optional: Split document into smaller chunks (if long)
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

chunks = split_into_chunks(document_text)

# Embed the document chunks
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embed_model.encode(chunks)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Ask your question
query = input("Ask a question: ")
query_embedding = embed_model.encode([query])
_, indices = index.search(np.array(query_embedding), k=3)

# Get top-matching chunks
retrieved_chunks = [chunks[i] for i in indices[0]]
context = "\n".join(retrieved_chunks)

# Create prompt
prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"

# Generate answer from Gemini
response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt
)

print("\nAnswer:")
print(response.text)
