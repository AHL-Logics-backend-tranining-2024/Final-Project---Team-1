from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import  OAuth2PasswordRequestForm
from app.api.auth_utlis import create_access_token
from models import Token, User
from user import users_db
from datetime import timedelta
from api.auth_utlis import pwd_context, get_password_hash
from dependencies import get_user_by_username


router = APIRouter()




#POST /login
@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_username(form_data.username)

# Verify the provided password against the stored hashed password
    if not user or not pwd_context.verify(form_data.password, get_password_hash(user)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
