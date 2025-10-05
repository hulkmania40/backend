# models/invoice.py

from sqlalchemy import Table, Column, Integer, String, Numeric, DateTime, ForeignKey, func
from database import metadata, engine

# Invoices table
invoices = Table(
    "invoices",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_name", String(100), nullable=False),
    Column("invoice_date", DateTime, server_default=func.now(), nullable=False),
    Column("total_amount", Numeric(10, 2)),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now())
)

# Create both tables if they don't exist
metadata.create_all(engine)
