from database import database
from models.item import items

async def create_item(name: str, price: int, quantity: int):
    query = items.insert().values(name=name, price=price, quantity=quantity)
    item_id = await database.execute(query)
    return {"id": item_id, "name": name, "price": price, "quantity": quantity}

async def get_all_items():
    query = items.select()
    print("Query",query)
    return await database.fetch_all(query)

async def get_item(id:int):
    query = items.select().where(items.c.id == id)
    return await database.fetch_one(query) 