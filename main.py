# main.py
import os
import io
import traceback
from fastapi import FastAPI, File, UploadFile, Form, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from bson import ObjectId
import pdfplumber

from db import get_db, lifespan
from auth import router as auth_router
from processing import split_into_chunks, get_top_chunks, ask_llm

# -----------------------------
# Setup
# -----------------------------
load_dotenv()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(lifespan=lifespan)

# Allow CORS (all origins, dev-friendly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routes
app.include_router(auth_router)


# -----------------------------
# Health check
# -----------------------------
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "RAG LLM Backend is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}


# -----------------------------
# Upload PDF
# -----------------------------
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), db=Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file")

    try:
        bucket = AsyncIOMotorGridFSBucket(db)
        file_id = await bucket.upload_from_stream(file.filename, file.file)

        await db.uploads.insert_one({
            "filename": file.filename,
            "file_id": file_id
        })
        print(f"[UPLOAD] Stored file '{file.filename}' with id '{file_id}'")

        return {"status": "success", "filename": file.filename, "file_id": str(file_id)}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")


# -----------------------------
# Ask Question
# -----------------------------
@app.post("/ask/")
async def ask_question(
    filename: str = Form(...),
    query: str = Form(...),
    username: str = Form(...),
    db=Depends(get_db)
):
    try:
        # 1. Fetch metadata
        upload_doc = await db.uploads.find_one({"filename": filename})
        if not upload_doc:
            raise HTTPException(status_code=404, detail="File not found")
        print(f"[ASK] Found file '{filename}' for user '{username}'")

        # 2. Download from GridFS
        bucket = AsyncIOMotorGridFSBucket(db)
        file_id = upload_doc["file_id"]
        if not isinstance(file_id, ObjectId):
            file_id = ObjectId(file_id)

        stream = await bucket.open_download_stream(file_id)
        pdf_bytes = await stream.read()
        print(f"[ASK] PDF size: {len(pdf_bytes)} bytes")

        if len(pdf_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

        # 3. Extract text
        text = ""
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            if not text.strip():
                raise HTTPException(status_code=400, detail="PDF has no readable text")

            print(f"[ASK] Extracted text length: {len(text)} characters")
            print(f"[ASK] Text preview: {text[:200]}...")  # safe preview

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error extracting PDF text: {e}")

        # 4. Chunking + LLM query
        try:
            chunks = split_into_chunks(text)
            top_chunks = get_top_chunks(chunks, query)
            context = "\n".join(top_chunks)

            answer = ask_llm(context, query)
            print(f"[ASK] Generated answer (first 120 chars): {answer[:120]}...")

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"LLM query failed: {e}")

        # 5. Save Q&A in DB
        await db.questions.insert_one({
            "filename": filename,
            "query": query,
            "answer": answer,
            "username": username
        })
        print(f"[ASK] Saved Q&A for user '{username}'")

        return {"answer": answer}

    except HTTPException as he:
        print(f"[ASK] HTTPException: {he.detail}")
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# -----------------------------
# Get user history
# -----------------------------
@app.get("/history/")
async def get_history(username: str = Query(...), db=Depends(get_db)):
    try:
        cursor = db.questions.find({"username": username}).sort("_id", -1)
        history = []
        async for doc in cursor:
            history.append({
                "filename": doc.get("filename"),
                "question": doc.get("query"),
                "answer": doc.get("answer"),
                "timestamp": str(doc.get("_id"))
            })

        print(f"[HISTORY] Returning {len(history)} items for user '{username}'")
        return {"history": history}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {e}")


# -----------------------------
# Run locally
# -----------------------------
# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 8000))
#     print(f"[SERVER] Starting on port {port}")
#     uvicorn.run("main:app", host="0.0.0.0", port=port)
