import re
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv
load_dotenv()




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



