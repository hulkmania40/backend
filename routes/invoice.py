from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from crud import invoice as crud_invoice
from utils.security import get_current_user
from utils.utils import get_optional_user

router = APIRouter()

# ---------- Pydantic Models ----------

class InvoiceItemCreate(BaseModel):
    item_id: int
    quantity: int
    price: float

class InvoiceCreate(BaseModel):
    customer_name: str
    items: List[InvoiceItemCreate]

class InvoiceItemUpdate(BaseModel):
    item_id: int
    quantity: int
    price: float
    
class InvoiceUpdate(BaseModel):
    customer_name: str
    items: List[InvoiceItemUpdate]
# ---------- Routes ----------

@router.post("/")
async def create_invoice(invoice: InvoiceCreate, current_user=Depends(lambda: get_current_user(optional=True))):
    """
    Create an invoice with multiple items.
    """
    try:
        new_invoice = await crud_invoice.create_invoice(invoice.customer_name, invoice.items)
        return new_invoice
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{invoice_id}")
async def update_invoice(
    invoice_id: int,
    invoice: InvoiceUpdate,
    current_user=Depends(lambda: get_current_user(optional=True))
):
    """
    Update an existing invoice with stock adjustment logic.
    This includes:
      - Increasing or decreasing item quantities.
      - Adding or removing items dynamically.
      - Automatically restoring or deducting stock based on quantity changes.
      - Preventing stock from going below zero.
    """
    try:
        updated_invoice = await crud_invoice.update_invoice(
            invoice_id, invoice.customer_name, invoice.items
        )
        return updated_invoice
    except HTTPException as e:
        # rethrow FastAPI errors (like stock issues or not found)
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_invoices(
    query: Optional[str] = Query(None),
    current_user=Depends(lambda: get_current_user(optional=True))
):
    """
    Get all invoices. Optionally filter by customer name.
    """
    return await crud_invoice.get_all_invoices(query)


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: int, current_user=Depends(get_optional_user)):
    """
    Get invoice details by ID (with items included).
    """
    invoice = await crud_invoice.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: int, current_user=Depends(get_optional_user)):
    """
    Delete invoice by ID.
    """
    deleted = await crud_invoice.delete_invoice(invoice_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Invoice not found or already deleted")
    return {"message": "Invoice deleted successfully"}
