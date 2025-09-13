from database import database
from models.user import users
from utils.security import get_password_hash, verify_password, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta

async def create_user(email: str, password: str, role: str = "user"):
    query = users.select().where(users.c.email == email)
    existing = await database.fetch_one(query)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(password)
    query = users.insert().values(email=email, hashed_password=hashed_pw, role=role)
    user_id = await database.execute(query)
    return {"id": user_id, "email": email, "role": role}

async def authenticate_user(email: str, password: str):
    query = users.select().where(users.c.email == email)
    user = await database.fetch_one(query)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=30)
    token = create_access_token(data={"sub": email, "role": user["role"]}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}
