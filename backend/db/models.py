from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from db.session import Base

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
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
    embedding = Column(Vector(1536)) # For text-embedding-3-small

class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    platform_name = Column(String) # 'square', 'clover', 'ubereats'
    encrypted_credentials = Column(String)
    status = Column(String)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())

class PlatformItemMapping(Base):
    __tablename__ = "platform_item_mappings"
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    platform_connection_id = Column(Integer, ForeignKey("platform_connections.id"))
    external_item_id = Column(String, index=True)
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    platform_connection_id = Column(Integer, ForeignKey("platform_connections.id"))
    status = Column(String)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
