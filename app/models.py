import re
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr, Field, condecimal, PositiveInt
from dotenv import load_dotenv
from fastapi import Query
from decimal import Decimal
load_dotenv()
from api.routes.dependencies import get_current_time




password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$" 

class Status:
    def __init__(self, name: str):
        self.id = uuid4()  
        self.name = name
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        
    def update(self, name: str):
        self.name = name
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
class UserBaseModel(BaseModel):
    username: str = Field(..., description="The username of the user.")
    email: EmailStr = Field(..., description="The email address of the user.")

class StatusCreate(BaseModel):
    name:str=Field(...,description="Status name example (pending, processing, completed, canceled)")

class StatusUpdate(BaseModel):
    name :str=Field(...,description="Updated status name")
#Inheriting from UserBaseModel
class UserCreateRequestModel(UserBaseModel):
    password: str = Field(
        ...,
        min_length=8,
        pattern=password_regex,
        description="Password must be at least 8 characters long, contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character."
    )

#Inheriting from UserBaseModel
class UserCreateResponseModel(UserBaseModel):
    id: UUID
    is_admin: bool = Field(default=False, description="Admin privileges.")
    is_active: bool = Field(default=True, description="Account active status.")
    created_at: datetime

#Inheriting from UserBaseModel
class User(UserBaseModel):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str = Field(..., description="The hashed password ")
    is_admin: bool = Field(default=False, description="Admin privileges.")
    is_active: bool = Field(default=True, description="Account active status.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="User creation timestamp.")
    updated_at: datetime = Field(default=None, description="Last updated timestamp.")

    


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[UUID] = None

#User Update Request Model
class UserUpdateRequestModel(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str = Field(
        ...,
        min_length=8,
        pattern=password_regex,
        description="Password must be at least 8 characters long, contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character."
    )
class UserUpdateResponseModel(BaseModel):
    id: UUID
    username: str
    email: str
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),description="User creation timestamp.")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),description="Last updated timestamp.")

class ChangeRoleRequest(BaseModel):
    user_id: UUID
    is_admin: bool


class GetUserResponseModel(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

class Product:
    def __init__(self, name: str, description: Optional[str], price: float, stock: int, is_available: bool = True):
        self.id = uuid4()  
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.is_available = is_available
        self.created_at = get_current_time()  
        self.updated_at = self.created_at  
    
    def update(self, name: Optional[str], description: Optional[str], price: Optional[float], stock: Optional[int], is_available: Optional[bool]):
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if price is not None:
            self.price = price
        if stock is not None:
            self.stock = stock
        if is_available is not None:
            self.is_available = is_available
        self.updated_at = get_current_time()
    
    def to_dict(self):
        return {
            # Convert UUID to string
            "id": str(self.id), 
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "is_available": self.is_available,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
class ProductCreate(BaseModel):
    name: str = Field(..., description="Name of the product.")
    price: condecimal(gt=0, decimal_places=2) = Field(..., gt=0, description="Price of the product.Must be a positive decimal")
    description: Optional[str] = Field(None, description="Description of the product.")
    stock: int = Field(..., ge=0, description="The available stock of the product.")
    is_available: bool = Field(True, description="Is the product available for sale?") 

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the product.")
    price: Optional[condecimal(gt=0, decimal_places=2)] = Field(None, gt=0, description="Price of the product. Must be a positive decimal.")
    description: Optional[str] = Field(None, description="Description of the product.")
    stock: Optional[int] = Field(None, ge=0, description="The available stock of the product.")
    is_available: Optional[bool] = Field(None, description="Is the product available for sale?")

class ProductSearchParams(BaseModel):
    name: Optional[str] = Query(None, description="Partial or full product name")
    min_price: Optional[Decimal] = Query(None, description="Minimum price")
    max_price: Optional[Decimal] = Query(None, description="Maximum price")
    isAvailable: Optional[bool] = Query(None, description="Filter by availability")
    page: int = Query(1, ge=1, description="Page number for pagination")
    page_size: int = Query(20, ge=1, le=100, description="Number of products per page")
    sort_by: str = Query("name", description="Sort by field")
    sort_order: str = Query("asc", description="Sort order: asc or desc")


class ProductOrder(BaseModel):
    product_id: UUID = Field(..., description="The ID of the product being ordered.")
    quantity: int = Field(..., ge=1, description="The quantity of the product being ordered.")

class OrderCreateRequest(BaseModel):
    products: List[ProductOrder] = Field(..., description="List of products to order.")

class OrderCreateResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_price: float
    created_at: datetime

class OrderDetailResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_price: float
    created_at: datetime
    updated_at: datetime
    products: List[ProductOrder]


class UpdateOrderStatusRequest(BaseModel):
    status: str = Field(..., description="New status of the order", pattern="^(pending|processing|completed|canceled)$")

class OrderUpdateResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime]