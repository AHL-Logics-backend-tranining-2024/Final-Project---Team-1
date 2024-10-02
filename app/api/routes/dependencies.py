from typing import Dict
from fastapi import Depends, HTTPException, status
from models import TokenData, User,Status 
from api.auth_utlis import verify_token, oauth2_scheme
from user import users_db  
from uuid import UUID
from datetime import datetime



users_db: Dict[str, User] = {}
statuses: Dict[UUID, Status] = {}
orders_db: Dict[UUID, Dict] = {}

#Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        #Verify the token and get the user ID
        user_id = verify_token(token, credentials_exception)

        #Fetch the user by ID
        user = users_db.get(str(user_id))
        if user is None:
            raise credentials_exception

        return user

    except Exception as e:
        # Catch all exceptions, including HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    

#Dependency to get current active user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    try:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the user: {str(e)}"
        )
    return current_user

#Dependency to get current admin user
async def get_current_admin(current_user: User = Depends(get_current_active_user)):
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while checking admin privileges: {str(e)}"
        )
    return current_user


# Dependency to get the user by username
async def get_user_by_username(username: str) -> User:
    user = users_db.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

def get_current_time():
    return datetime.utcnow().isoformat()

