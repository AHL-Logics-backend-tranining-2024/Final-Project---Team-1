from datetime import datetime, timezone
from uuid import uuid4,UUID
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy import Column, String, Text, Float, Integer, Boolean, UUID
from sqlalchemy import Boolean, Column, DateTime, String, func
from .database import Base
from pydantic import BaseModel,Field 
from typing import Optional


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Status(Base):
    __tablename__ = "statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Product(Base):
    __tablename__ = "products"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Product(name={self.name}, price={self.price}, stock={self.stock}, is_available={self.is_available})>"
