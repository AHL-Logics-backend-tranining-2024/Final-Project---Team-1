import re
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr, Field, field_validator
from passlib.context import CryptContext
from dotenv import load_dotenv
load_dotenv()

#Set up password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$"

class UserBaseModel(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool = False
    is_active: bool = True

class UserResponseModel(UserBaseModel):
    id: UUID
    created_at: datetime

class UserCreateRequestModel(BaseModel):
    username: str = Field(
        ...,
        description="The customer's chosen username."
    )
    email: EmailStr = Field(
        ...,
        description="The customer's email address."
    )
    password: str = Field(
        ...,
        min_length=8,
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$",
        description="The password, which must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character."
    )


#Inheriting from UserBaseModel
class User(UserBaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default=None)

    


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[UUID] = None


