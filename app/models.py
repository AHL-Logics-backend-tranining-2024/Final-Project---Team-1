from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(uuid(as_uuid=True), primary_key=True, default=uuid, unique=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"
    id = Column(uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)


    order_products = relationship("OrderProduct", back_populates="product", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    user_id = Column(uuid.UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status_id = Column(uuid.UUID(as_uuid=True), ForeignKey("order_status.id", ondelete="SET NULL"), nullable=True)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    user = relationship("User", back_populates="orders")
    status = relationship("OrderStatus", back_populates="orders")
    products = relationship("OrderProduct", back_populates="order", cascade="all, delete-orphan")


class OrderStatus(Base):
    __tablename__ = "order_status"

    id = Column(uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    orders = relationship("Order", back_populates="status")


class OrderProduct(Base):
    __tablename__ = "order_product"

    id = Column(uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    order_id = Column(uuid.UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(uuid.UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    order = relationship("Order", back_populates="products")
    product = relationship("Product", back_populates="order_products")
