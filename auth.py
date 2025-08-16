from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import get_db
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

@router.post("/register/", response_model=UserOut)
async def register(user: UserIn, db=Depends(get_db)):
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = pwd_context.hash(user.password)
    await db.users.insert_one({"username": user.username, "password": hashed})
    return {"username": user.username}

@router.post("/login/")
async def login(user: UserIn, db=Depends(get_db)):
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": user.username}
