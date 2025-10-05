from sqlalchemy import insert, select, delete, join, func
from models.invoice import invoices
from models.invoice_item import invoice_items
from models.item import items
from database import database


from sqlalchemy import insert, select, update
from fastapi import HTTPException
from models.invoice import invoices
from models.invoice_item import invoice_items
from models.item import items
from database import database


async def create_invoice(customer_name: str, items_list: list):
    # 1️⃣ Check inventory availability
    for item in items_list:
        # Fetch item stock
        item_query = select(items).where(items.c.id == item.item_id)
        item_in_db = await database.fetch_one(item_query)

        if not item_in_db:
            raise HTTPException(
                status_code=404,
                detail=f"Item with ID {item.item_id} does not exist."
            )

        if item_in_db.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for '{item_in_db.name}'. "
                       f"Available: {item_in_db.quantity}, Requested: {item.quantity}"
            )

    # 2️⃣ Calculate total
    total_amount = sum(item.price * item.quantity for item in items_list)

    # 3️⃣ Create invoice
    invoice_query = insert(invoices).values(
        customer_name=customer_name,
        total_amount=total_amount
    )
    invoice_id = await database.execute(invoice_query)

    # 4️⃣ Insert invoice items
    invoice_items_data = [
        {
            "invoice_id": invoice_id,
            "item_id": item.item_id,
            "quantity": item.quantity,
            "price": item.price,
        }
        for item in items_list
    ]
    await database.execute_many(insert(invoice_items), invoice_items_data)

    # 5️⃣ Update inventory quantities
    for item in items_list:
        update_query = (
            update(items)
            .where(items.c.id == item.item_id)
            .values(quantity=items.c.quantity - item.quantity)
        )
        await database.execute(update_query)

    # 6️⃣ Return response
    return {
        "invoice_id": invoice_id,
        "total": total_amount,
        "message": "Invoice created and stock updated successfully."
    }

async def update_invoice(invoice_id: int, customer_name: str, items_list: list):
    # 1️⃣ Validate basic rules
    if any(item.quantity <= 0 for item in items_list):
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    # 2️⃣ Check if invoice exists
    existing_invoice = await database.fetch_one(
        select(invoices).where(invoices.c.id == invoice_id)
    )
    if not existing_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # 3️⃣ Fetch old invoice items
    old_items = await database.fetch_all(
        select(invoice_items).where(invoice_items.c.invoice_id == invoice_id)
    )
    old_items_map = {item.item_id: item for item in old_items}
    new_items_map = {item.item_id: item for item in items_list}

    # 🧩 Track stock adjustments in memory
    stock_adjustments = {}

    # 4️⃣ Handle REMOVED items (restore stock fully)
    for old_item in old_items:
        if old_item.item_id not in new_items_map:
            stock_adjustments[old_item.item_id] = old_item.quantity  # restore full qty

    # 5️⃣ Handle UPDATED items (compare quantities)
    for item in items_list:
        if item.item_id in old_items_map:
            old_qty = old_items_map[item.item_id].quantity
            diff = item.quantity - old_qty

            if diff > 0:
                # increased quantity → need to deduct more stock
                stock_adjustments[item.item_id] = stock_adjustments.get(item.item_id, 0) - diff
            elif diff < 0:
                # decreased quantity → restore some stock
                stock_adjustments[item.item_id] = stock_adjustments.get(item.item_id, 0) + abs(diff)
        else:
            # 6️⃣ NEW items (not in old invoice) → deduct full quantity
            stock_adjustments[item.item_id] = stock_adjustments.get(item.item_id, 0) - item.quantity

    # ✅ 7️⃣ Validate stock availability before applying
    for item_id, adjustment in stock_adjustments.items():
        item_in_db = await database.fetch_one(select(items).where(items.c.id == item_id))
        if not item_in_db:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

        new_stock = item_in_db.quantity + adjustment  # adjustment can be + (restore) or - (deduct)
        if new_stock < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for '{item_in_db.name}'. "
                       f"Available: {item_in_db.quantity}, Requested change: {abs(adjustment)}"
            )

    # ✅ 8️⃣ Apply stock adjustments
    for item_id, adjustment in stock_adjustments.items():
        if adjustment == 0:
            continue
        update_stock_query = (
            update(items)
            .where(items.c.id == item_id)
            .values(quantity=items.c.quantity + adjustment)
        )
        await database.execute(update_stock_query)

    # 🧾 9️⃣ Update invoice totals
    total_amount = sum(item.price * item.quantity for item in items_list)

    update_invoice_query = (
        update(invoices)
        .where(invoices.c.id == invoice_id)
        .values(customer_name=customer_name, total_amount=total_amount)
    )
    await database.execute(update_invoice_query)

    # 🔁 10️⃣ Replace invoice_items table
    delete_query = delete(invoice_items).where(invoice_items.c.invoice_id == invoice_id)
    await database.execute(delete_query)

    new_invoice_items_data = [
        {
            "invoice_id": invoice_id,
            "item_id": item.item_id,
            "quantity": item.quantity,
            "price": item.price,
        }
        for item in items_list
    ]
    await database.execute_many(insert(invoice_items), new_invoice_items_data)

    return {
        "invoice_id": invoice_id,
        "message": "Invoice updated successfully with accurate stock handling."
    }

async def get_all_invoices(query: str | None = None):
    q = select(invoices)
    if query:
        q = q.where(invoices.c.customer_name.ilike(f"%{query}%"))
    return await database.fetch_all(q.order_by(invoices.c.id.desc()))


async def get_invoice(invoice_id: int):
    # Fetch invoice
    invoice_query = select(invoices).where(invoices.c.id == invoice_id)
    invoice = await database.fetch_one(invoice_query)
    if not invoice:
        return None

    # Fetch its items (joined with item details)
    join_query = (
        select(
            items.c.id.label("item_id"), 
            invoice_items.c.quantity,
            invoice_items.c.price,
            items.c.name.label("item_name")
        )
        .select_from(
            join(invoice_items, items, invoice_items.c.item_id == items.c.id)
        )
        .where(invoice_items.c.invoice_id == invoice_id)
    )
    invoice_items_list = await database.fetch_all(join_query)

    return {
        "id": invoice.id,
        "customer_name": invoice.customer_name,
        "invoice_date": invoice.invoice_date,
        "total_amount": invoice.total_amount,
        "items": [dict(row) for row in invoice_items_list],
    }


async def delete_invoice(invoice_id: int):
    query = delete(invoices).where(invoices.c.id == invoice_id)
    result = await database.execute(query)
    return bool(result)