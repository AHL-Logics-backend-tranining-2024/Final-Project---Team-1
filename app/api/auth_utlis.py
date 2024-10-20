from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import JWTError, jwt
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import BaseSettings



load_dotenv()

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#JWT settings
class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"  # Default value
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  
    DATABASE_URL: str

    class Config:
        env_file = ".env"  


settings = Settings()

# JWT token creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# JWT token verification
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return UUID(user_id)
    except JWTError:
        raise credentials_exception



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#General method for verifying passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


