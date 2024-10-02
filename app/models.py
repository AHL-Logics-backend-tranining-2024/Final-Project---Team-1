import re
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv
load_dotenv()




password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$"

class UserBaseModel(BaseModel):
    username: str = Field(..., description="The username of the user.")
    email: EmailStr = Field(..., description="The email address of the user.")


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