from fastapi import Depends, HTTPException, status
from models import TokenData 
from api.auth_utlis import verify_token, oauth2_scheme
from user import users_db  
from uuid import UUID




#Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        #Try to verify the token
        username = verify_token(token, credentials_exception)

        #Fetch the user
        user = next((u for u in users_db.values() if str(u.id) == username), None)
        if user is None or not user.is_active:
            raise credentials_exception
        
        return TokenData(username=UUID(username))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    

#Dependency to get current active user
async def get_current_active_user(current_user: TokenData = Depends(get_current_user)):
    try:
        user = users_db.get(str(current_user.username))
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the user: {str(e)}"
        )
    return user

#Dependency to get current admin user
async def get_current_admin(current_user: TokenData = Depends(get_current_active_user)):
    try:
        user = users_db.get(str(current_user.username))
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while checking admin privileges: {str(e)}"
        )
    return user


