from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from crud import item as crud_item
from utils.security import get_current_user

router = APIRouter()

class ItemCreate(BaseModel):
    name: str
    price: int

@router.post("/")
async def create_item(item: ItemCreate, current_user=Depends(get_current_user)):
    return await crud_item.create_item(item.name, item.price, current_user["id"])

@router.get("/")
async def list_items(current_user=Depends(lambda: get_current_user(optional=True))):
    # if current_user["role"] == "admin":
    print("Inside router")
    return await crud_item.get_all_items()
    # return await crud_item.get_items_by_user(current_user["id"])
