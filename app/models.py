from datetime import datetime, timezone
from uuid import uuid4,UUID
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

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class StatusCreate(BaseModel):
    name: str

class StatusUpdate(BaseModel):
    name: str


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    is_available: Optional[bool] = True

class ProductUpdate(BaseModel):
    name: Optional[str]
    price: Optional[float]
    stock: Optional[int]

class ProductSearchParams(BaseModel):
    name: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_available: Optional[bool] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    sort_by: Optional[str] = "name"
    sort_order: Optional[str] = "asc"
    
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The name of the product.")
    description: Optional[str] = Field(None, description="The description of the product.")
    price: Optional[float] = Field(None, description="The price of the product.")
    stock: Optional[int] = Field(None, description="The stock quantity of the product.")
    is_available: Optional[bool] = Field(None, description="Indicates if the product is available.")