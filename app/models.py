from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool = False
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_password_hash(self):
        return pwd_context.hash(self.password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.get_password_hash())
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
