from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User
from auth_utlis import verify_token, oauth2_scheme
from database import get_db  

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify the token and extract the user ID
        user_id = verify_token(token, credentials_exception)

        # Query the database to fetch the user
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception

        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
# Dependency to get current active user
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Dependency to get current admin user
async def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user



