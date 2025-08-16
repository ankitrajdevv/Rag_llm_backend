print("FastAPI app is starting...")

import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
from auth import router as auth_router
from db import get_db
from processing import extract_text, split_into_chunks, get_top_chunks, ask_llm

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize FastAPI
app = FastAPI()
app.include_router(auth_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "RAG LLM Backend is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# Upload PDF
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), db=Depends(get_db)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    await db.uploads.insert_one({"filename": file.filename})
    return {"filename": file.filename}

# Ask question
@app.post("/ask/")
async def ask_question(
    filename: str = Form(...),
    query: str = Form(...),
    username: str = Form(...),
    db=Depends(get_db)
):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    text = extract_text(file_path)
    chunks = split_into_chunks(text)
    top_chunks = get_top_chunks(chunks, query)
    context = "\n".join(top_chunks)
    answer = ask_llm(context, query)
    await db.questions.insert_one({
        "filename": filename,
        "query": query,
        "answer": answer,
        "username": username
    })
    return {"answer": answer}

# Get history
@app.get("/history/")
async def get_history(
    username: str = Query(...),
    db=Depends(get_db)
):
    cursor = db.questions.find({"username": username}).sort("_id", -1)
    history = []
    async for doc in cursor:
        history.append({
            "filename": doc.get("filename"),
            "question": doc.get("query"),
            "answer": doc.get("answer"),
            "timestamp": str(doc.get("_id"))
        })
    return {"history": history}

# Run app with dynamic port for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render sets PORT dynamically
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
