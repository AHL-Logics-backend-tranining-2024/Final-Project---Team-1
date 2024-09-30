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

class UserCreateRequestModel(UserBaseModel):
    password: str
    @field_validator('password')
    def validate_password(cls, value):
        if not re.match(password_regex, value):
            raise ValueError(
                "Password must be at least 8 characters long, contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character."
            )
        return value
    
    def get_password_hash(self):
        return pwd_context.hash(self.password)

#Inheriting from UserBaseModel
class User(UserBaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default=None)

    
    #Method to verify if the provided password matches the hashed password
    def verify_password(self, password: str):
        return pwd_context.verify(password, self.get_password_hash())
    


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[UUID] = None


