from sqlalchemy import DateTime, Table, Column, Integer, String, ForeignKey
from database import metadata, engine

items = Table(
    "items",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("price", Integer, nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)

metadata.create_all(engine)
