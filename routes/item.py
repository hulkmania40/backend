from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from crud import item as crud_item
from utils.security import get_current_user
from utils.utils import get_optional_user

router = APIRouter()

class ItemCreate(BaseModel):
    name: str
    price: int
    quantity: int

@router.post("/")
async def create_item(item: ItemCreate, current_user=Depends(lambda: get_current_user(optional=True))):
    return await crud_item.create_item(item.name, item.price, item.quantity,
                                    #    current_user["id"]
                                       )

@router.get("/")
async def list_items(current_user=Depends(lambda: get_current_user(optional=True))):
    # if current_user["role"] == "admin":
    print("Inside router")
    return await crud_item.get_all_items()
    # return await crud_item.get_items_by_user(current_user["id"])

@router.get("/{id}")
async def list_item(id: int, current_user=Depends(get_optional_user)):
    item = await crud_item.get_item(id)
    return item

@router.put("/{id}")
async def edit_item(id: int, data:dict, current_user=Depends(get_optional_user)):
    item = await crud_item.edit_item(id,data)
    return item