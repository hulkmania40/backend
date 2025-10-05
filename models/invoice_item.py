from sqlalchemy import Table, Column, Integer, String, Numeric, DateTime, ForeignKey, func
from database import metadata, engine

# Invoice items table (many-to-many link between invoice and items)
invoice_items = Table(
    "invoice_items",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("invoice_id", Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False),
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("price", Numeric(10, 2), nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False)
)

# Create both tables if they don't exist
metadata.create_all(engine)
