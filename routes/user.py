from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from crud import user as crud_user

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
async def signup(user: UserCreate):
    return await crud_user.create_user(user.email, user.password, user.role)

@router.post("/login")
async def login(user: UserLogin):
    return await crud_user.authenticate_user(user.email, user.password)
