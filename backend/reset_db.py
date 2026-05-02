"""
Reset script - drops all tables and recreates them fresh.
Run this when models change and you want a clean slate.
"""
from db.session import engine
from db.models import Base
from sqlalchemy import text

print("Dropping all existing tables...")
with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE;"))
    conn.execute(text("CREATE SCHEMA public;"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()

print("Recreating all tables from models...")
Base.metadata.create_all(bind=engine)
print("✅ Database reset complete!")
