# main.py
import os
import io
from fastapi import FastAPI, File, UploadFile, Form, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from db import get_db, lifespan
from auth import router as auth_router
from processing import split_into_chunks, get_top_chunks, ask_llm
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
import pdfplumber

# Load environment variables
load_dotenv()

# Create uploads folder (not used with GridFS, but safe to keep)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize FastAPI with lifespan for MongoDB
app = FastAPI(lifespan=lifespan)

# Enable open CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file")
    
    # Store file in MongoDB GridFS
    bucket = AsyncIOMotorGridFSBucket(db)
    file_id = await bucket.upload_from_stream(file.filename, file.file)
    
    # Save metadata in MongoDB
    await db.uploads.insert_one({"filename": file.filename, "file_id": file_id})
    
    return {"status": "success", "filename": file.filename, "file_id": str(file_id)}

# Ask question
@app.post("/ask/")
async def ask_question(
    filename: str = Form(...),
    query: str = Form(...),
    username: str = Form(...),
    db=Depends(get_db)
):
    # Retrieve file from GridFS
    upload_doc = await db.uploads.find_one({"filename": filename})
    if not upload_doc:
        raise HTTPException(status_code=404, detail="File not found")

    bucket = AsyncIOMotorGridFSBucket(db)
    stream = await bucket.open_download_stream(upload_doc["file_id"])
    pdf_bytes = await stream.read()
    
    # Extract text from PDF
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF: {e}")

    # Split, embed, and query
    chunks = split_into_chunks(text)
    top_chunks = get_top_chunks(chunks, query)
    context = "\n".join(top_chunks)
    answer = ask_llm(context, query)

    # Save Q&A in MongoDB
    await db.questions.insert_one({
        "filename": filename,
        "query": query,
        "answer": answer,
        "username": username
    })

    return {"answer": answer}

# Get user history
@app.get("/history/")
async def get_history(username: str = Query(...), db=Depends(get_db)):
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

# Run app (optional; Render uses uvicorn command)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
