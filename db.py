from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB")

class MongoDB:
    client = None
    db = None

mongodb = MongoDB()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MongoDB at startup and close at shutdown"""
    mongodb.client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    mongodb.db = mongodb.client[DB_NAME]
    try:
        await mongodb.db.command("ping")
        print("✅ MongoDB connected!")
    except Exception as e:
        raise RuntimeError("MongoDB not initialized") from e
    try:
        yield
    finally:
        if mongodb.client:
            mongodb.client.close()
            print("MongoDB connection closed.")

def get_db():
    if mongodb.db is None:
        raise RuntimeError("Database not initialized")
    return mongodb.db
