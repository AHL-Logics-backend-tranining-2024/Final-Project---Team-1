from fastapi import APIRouter, HTTPException, status
from models import UserCreate, User  
import re

router = APIRouter()


users_db = {}

#Password regex
password_regex = (
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=]).{8,}$'
)

@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    #Validate password
    if not re.match(password_regex, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long, contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character."
        )
    
    #Check if the email already exists
    for existing_user in users_db.values():
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered."
            )
    #Create User
    new_user = User(
        username=user.username,
        email=user.email,
        password=user.password  
    )
    users_db[str(new_user.id)] = new_user  

    #Return the created user without the password
    return new_user

