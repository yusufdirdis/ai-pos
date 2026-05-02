from db.session import engine
from db.models import Base
from sqlalchemy import text

print("Creating database extensions...")
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
