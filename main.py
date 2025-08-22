
# main.py
import os
import io
import traceback
from fastapi import FastAPI, File, UploadFile, Form, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from bson import ObjectId

import os
import io
import traceback
from fastapi import FastAPI, File, UploadFile, Form, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from bson import ObjectId

# Local imports
from db import get_db, lifespan
from auth import router as auth_router
from processing import split_into_chunks, get_top_chunks, ask_llm, extract_text

load_dotenv()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "RAG LLM Backend is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# Upload PDF
@app.post("/upload/")
async def upload_pdf(
    file: UploadFile = File(...),
    username: str = Form(...),
    db=Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file")
    try:
        bucket = AsyncIOMotorGridFSBucket(db)
        file_id = await bucket.upload_from_stream(file.filename, file.file)
        await db.uploads.insert_one({
            "filename": file.filename,
            "file_id": file_id,
            "username": username
        })
        print(f"[UPLOAD] Stored file '{file.filename}' for user '{username}' with id '{file_id}'")
        return {"status": "success", "filename": file.filename, "file_id": str(file_id)}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

# List PDFs for user
@app.get("/list_pdfs/")
async def list_pdfs(username: str = Query(...), db=Depends(get_db)):
    try:
        cursor = db.uploads.find({"username": username})
        pdfs = []
        async for doc in cursor:
            pdfs.append(doc.get("filename"))
        print(f"[LIST_PDFS] Returning {len(pdfs)} PDFs for user '{username}'")
        return {"pdfs": pdfs}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch PDFs: {e}")

# Ask question with multiple PDFs as context
@app.post("/ask/")
async def ask_question(
    filenames: str = Form(...),  # JSON string of filenames
    query: str = Form(...),
    username: str = Form(...),
    db=Depends(get_db)
):
    try:
        import json
        filenames_list = json.loads(filenames)
        if not isinstance(filenames_list, list) or not filenames_list:
            raise HTTPException(status_code=400, detail="No filenames provided")

        bucket = AsyncIOMotorGridFSBucket(db)

        all_contexts = []
        for filename in filenames_list:
            upload_doc = await db.uploads.find_one({"filename": filename, "username": username})
            if not upload_doc:
                continue
            file_id = upload_doc.get("file_id")
            if not file_id:
                continue
            if not isinstance(file_id, ObjectId):
                try:
                    file_id = ObjectId(file_id)
                except Exception:
                    continue
            stream = await bucket.open_download_stream(file_id)
            pdf_bytes = await stream.read()
            if not pdf_bytes:
                continue
            text = extract_text(io.BytesIO(pdf_bytes))
            if not text.strip():
                continue
            chunks = split_into_chunks(text)
            top_chunks = get_top_chunks(chunks, query)
            if top_chunks:
                all_contexts.append("\n".join(top_chunks))

        if not all_contexts:
            raise HTTPException(status_code=404, detail="No valid PDFs found for this user")

        # Combine all contexts
        context = "\n".join(all_contexts)
        answer = ask_llm(context, query)
        print(f"[ASK] Generated answer (first 120 chars): {answer[:120]}...")

        # Save Q&A in DB
        await db.questions.insert_one({
            "filenames": filenames_list,
            "query": query,
            "answer": answer,
            "username": username
        })
        print(f"[ASK] Saved Q&A for user '{username}'")

        # Return answer only
        return {"answer": answer}

    except HTTPException as he:
        print(f"[ASK] HTTPException: {he.detail}")
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Get history
@app.get("/history/")
async def get_history(username: str = Query(...), db=Depends(get_db)):
    try:
        cursor = db.questions.find({"username": username}).sort("_id", -1)
        history = []
        async for doc in cursor:
            history.append({
                "filenames": doc.get("filenames"),
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
# Get history
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
# Delete PDF for user
@app.post("/delete_pdf/")
async def delete_pdf(
    filename: str = Form(...),
    username: str = Form(...),
    db=Depends(get_db)
):
    try:
        # Find the upload document
        upload_doc = await db.uploads.find_one({"filename": filename, "username": username})
        if not upload_doc:
            raise HTTPException(status_code=404, detail="File not found for this user")
        file_id = upload_doc.get("file_id")
        # Delete from GridFS
        if file_id:
            bucket = AsyncIOMotorGridFSBucket(db)
            await bucket.delete(file_id)
        # Delete metadata
        await db.uploads.delete_one({"filename": filename, "username": username})
        print(f"[DELETE] Deleted file '{filename}' for user '{username}'")
        return {"status": "success"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF: {e}")