from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from db.session import Base

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(String, index=True) # Supabase user UUID
    name = Column(String, index=True)
    pos_type = Column(String) # 'square', 'clover', 'toast', 'lightspeed', 'brink'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# We rely on Supabase auth for users, so this table is optional, but kept for CRM/Profiles if needed
class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(String, primary_key=True) # Matches auth.users.id
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    name = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String, index=True)
    description = Column(String)
    base_price = Column(Float)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    embedding = Column(Vector()) # Unconstrained dimension to support Ollama (768) or OpenAI (1536)

class Modifier(Base):
    __tablename__ = "modifiers"
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    name = Column(String)
    price_adjustment = Column(Float, default=0.0)

class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    platform_name = Column(String) # 'ubereats', 'doordash', 'grubhub', 'postmates'
    platform_type = Column(String) # 'delivery', 'pos'
    credentials_secret_arn = Column(String)
    is_active = Column(Boolean, default=True)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())

class PlatformItemMapping(Base):
    __tablename__ = "platform_item_mappings"
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    platform_name = Column(String)
    external_item_id = Column(String, index=True)
    last_sync_status = Column(String)
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SyncJob(Base):
    __tablename__ = "sync_jobs"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    status = Column(String) # 'pending', 'in_progress', 'completed', 'failed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(Integer, primary_key=True, index=True)
    sync_job_id = Column(Integer, ForeignKey("sync_jobs.id"))
    platform_name = Column(String)
    action = Column(String) # 'CREATE', 'UPDATE', 'DELETE'
    status = Column(String)
    error_message = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
