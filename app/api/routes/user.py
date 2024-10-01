from fastapi import APIRouter, HTTPException, status
from models import UserCreateRequestModel, User, UserCreateResponseModel 
from api.auth_utlis import get_password_hash


router = APIRouter()


users_db = {}


@router.post("/users/", response_model=UserCreateResponseModel, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateRequestModel):

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
        password=get_password_hash(user.password)
    )
    users_db[str(new_user.id)] = new_user  

    #Return the created user without the password
    return UserCreateResponseModel(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_admin=new_user.is_admin,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )

