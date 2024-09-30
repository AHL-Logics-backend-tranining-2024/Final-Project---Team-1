import re
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr, Field, field_validator
from passlib.context import CryptContext

#Set up password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$"

class UserBaseModel(BaseModel):
    username: str = Field(..., description="The username of the user.")
    email: EmailStr = Field(..., description="The email address of the user.")

class UserCreateRequestModel(UserBaseModel):
    password: str = Field(
        ...,
        min_length=8,
        pattern=password_regex,
        description="Password must be at least 8 characters long, contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character."
    )

class UserCreateResponseModel(UserBaseModel):
    id: UUID
    is_admin: bool = Field(default=False, description="Admin privileges.")
    is_active: bool = Field(default=True, description="Account active status.")
    created_at: datetime
    updated_at: datetime = None

#Inheriting from UserBaseModel
class User(UserBaseModel):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str = Field(..., description="The hashed password ")
    is_admin: bool = Field(default=False, description="Admin privileges.")
    is_active: bool = Field(default=True, description="Account active status.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="User creation timestamp.")
    updated_at: datetime = Field(default=None, description="Last updated timestamp.")

    def get_password_hash(self):
        return pwd_context.hash(self.password)
    
    #Method to verify if the provided password matches the hashed password
    def verify_password(self, password: str):
        return pwd_context.verify(password, self.get_password_hash())
    
