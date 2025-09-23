from sqlalchemy import desc
from database import database
from models.item import items
from datetime import datetime

async def create_item(name: str, price: int, quantity: int):
    now = datetime.utcnow()
    query = items.insert().values(name=name, price=price, quantity=quantity, created_at = now, updated_at = now)
    item_id = await database.execute(query)
    return {"id": item_id, 
            "name": name, 
            "price": price, 
            "quantity": quantity,
            "created_at": now,
            "updated_at":now
            }

async def get_all_items(name):
    query = items.select().order_by(desc(items.c.updated_at))
    if(name):
        query = query.where(items.c.name.ilike(f"%{name}%"))
    return await database.fetch_all(query)

async def get_item(id:int):
    query = items.select().where(items.c.id == id)
    return await database.fetch_one(query)

async def edit_item(id:int,data:dict):
    now = datetime.utcnow()
    query = items.update().where(items.c.id == id).values(**data, updated_at = now)
    return await database.execute(query)

async def delete_item(id:int):
    query = items.delete().where(items.c.id == id)
    return await database.execute(query)