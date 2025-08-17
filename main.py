import os
import io
import traceback
from bson import ObjectId

from fastapi import FastAPI, File, UploadFile, Form, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from db import get_db, lifespan
from auth import router as auth_router
from processing import (
    extract_text_from_bytes,
    split_into_chunks,
    ensure_index_for_file,
    get_top_chunks,
    ask_llm,
    build_index_for_file,
)

# -----------------------------
# Setup
# -----------------------------
load_dotenv()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(lifespan=lifespan)

# CORS (relaxed for dev)
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
# Upload PDF (also preprocess & cache)
# -----------------------------
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), db=Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file")

    try:
        data: bytes = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Store bytes in GridFS
        bucket = AsyncIOMotorGridFSBucket(db)
        file_id = await bucket.upload_from_stream(file.filename, io.BytesIO(data))

        # Pre-extract text + build index
        text = extract_text_from_bytes(data)
        if not text.strip():
            await db.uploads.insert_one({
                "filename": file.filename,
                "file_id": file_id,
                "text_len": 0,
                "chunk_count": 0,
            })
            return {
                "status": "success",
                "filename": file.filename,
                "file_id": str(file_id),
                "warning": "PDF has no readable text",
            }

        chunks = split_into_chunks(text)
        build_index_for_file(str(file_id), chunks)

        await db.uploads.insert_one({
            "filename": file.filename,
            "file_id": file_id,
            "text_len": len(text),
            "chunk_count": len(chunks),
        })
        print(f"[UPLOAD] Stored file '{file.filename}' with id '{file_id}', chunks={len(chunks)}")

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
        upload_doc = await db.uploads.find_one({"filename": filename})
        if not upload_doc:
            raise HTTPException(status_code=404, detail="File not found")

        file_id = upload_doc["file_id"]
        if not isinstance(file_id, ObjectId):
            file_id = ObjectId(file_id)
        file_key = str(file_id)

        # Ensure index exists
        try:
            ensure_index_for_file(file_key)
        except Exception:
            bucket = AsyncIOMotorGridFSBucket(db)
            stream = await bucket.open_download_stream(file_id)
            pdf_bytes = await stream.read()
            ensure_index_for_file(file_key, pdf_bytes=pdf_bytes)

        # Retrieve top chunks + call LLM
        top_chunks = get_top_chunks(file_key, query)
        context = "\n".join(top_chunks)
        answer = ask_llm(context, query)

        await db.questions.insert_one({
            "filename": filename,
            "file_id": file_id,
            "query": query,
            "answer": answer,
            "username": username,
        })

        return {"answer": answer}

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
                "timestamp": str(doc.get("_id")),
            })
        return {"history": history}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {e}")


# Uncomment for local dev
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
