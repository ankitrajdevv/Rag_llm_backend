from fastapi import FastAPI, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from dotenv import load_dotenv
import google.generativeai as genai
from auth import router as auth_router
from fastapi import Query
from db import lifespan, get_db
from processing import extract_text, split_into_chunks, get_top_chunks, ask_llm, is_question_relevant

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

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

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), db=Depends(get_db)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    await db.uploads.insert_one({"filename": file.filename})
    return {"filename": file.filename}

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

    summary_keywords = [
        "summarize", "summary", "summarise", "summarization", "summarise everything",
        "give a summary", "provide a summary", "overview", "main points"
    ]
    lowered_query = query.lower().strip()
    is_summary_query = any(kw in lowered_query for kw in summary_keywords)

    if is_summary_query:
        # For summary, use more content and a summarization prompt
        context = "\n".join(chunks[:10])  # or use the whole text if it's not too long!
        prompt = f"Summarize the following PDF content:\n{context}"
        answer = ask_llm(prompt, "Summarize this document.")
    else:
        relevant, score = is_question_relevant(chunks, query, threshold=0.4)
        if not relevant:
            answer = "Sorry, this question is irrelevant to the uploaded PDF."
        else:
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