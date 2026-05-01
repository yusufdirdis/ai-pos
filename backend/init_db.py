from db.session import engine
from db.models import Base

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
