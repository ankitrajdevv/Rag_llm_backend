from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")  
DB_NAME = os.getenv("MONGODB_DB")

# MongoDB utilities
class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

@asynccontextmanager
async def lifespan(app):
    print("Starting lifespan event...")
    try:
        mongodb.client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        mongodb.db = mongodb.client[DB_NAME]
        await mongodb.db.command("ping")
        print("✅ MongoDB connection successful!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        # Allow app to start even if DB is down
        yield
        mongodb.client.close()
        return
    yield
    mongodb.client.close()

async def get_db():
    return mongodb.db

# Example user authentication helper (expand as needed)
async def find_user(username):
    return await mongodb.db.users.find_one({"username": username})

async def create_user(user_data):
    return await mongodb.db.users.insert_one(user_data)