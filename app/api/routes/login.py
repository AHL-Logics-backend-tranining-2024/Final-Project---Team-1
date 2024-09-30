from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import  OAuth2PasswordRequestForm
from app.api.auth_utlis import create_access_token
from models import Token, pwd_context
from user import users_db
from datetime import timedelta


router = APIRouter()



#POST /login
@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    for existing_user in users_db.values():
        if existing_user.username == form_data.username:
            user = existing_user
            break

    if not user or not pwd_context.verify(form_data.password, user.get_password_hash()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
