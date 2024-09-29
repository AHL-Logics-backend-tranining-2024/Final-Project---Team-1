from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import TokenData, verify_token
from user import users_db  
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    
    #Fetch the user
    user = None
    for existing_user in users_db.values():
        if str(existing_user.id) == username:
            user = existing_user
            break

    if user is None or not user.is_active:
        raise credentials_exception

    return TokenData(username=UUID(username))

#Dependency to get current active user
async def get_current_active_user(current_user: TokenData = Depends(get_current_user)):
    user = users_db.get(str(current_user.username))

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user

#Dependency to get current admin user
async def get_current_admin(current_user: TokenData = Depends(get_current_active_user)):
    user = users_db.get(str(current_user.username))

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user
