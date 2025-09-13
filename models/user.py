from sqlalchemy import Table, Column, Integer, String, Boolean
from database import metadata, engine

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(100), unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("role", String(20), default="user"),  # "user" or "admin"
    Column("is_active", Boolean, default=True),
)

metadata.create_all(engine)
