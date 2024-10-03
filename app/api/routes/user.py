from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.routes.dependencies import get_current_active_user, get_current_admin, get_current_user
from models import ChangeRoleRequest, UserCreateRequestModel, User, UserCreateResponseModel, UserUpdateRequestModel, UserUpdateResponseModel 
from api.auth_utlis import get_password_hash, is_valid_password


router = APIRouter()


users_db = {}

#Create User
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
    hashed_password = get_password_hash(user.password)

    new_user = User(
        id=uuid4(),
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=False,  #Default is_admin
        is_active=True,  #Default is_active
        created_at=datetime.now(timezone.utc)
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



#Get User Details
@router.get("/users/{user_id}", response_model=UserCreateResponseModel, status_code=status.HTTP_200_OK)
async def get_user_details(user_id: UUID, current_user: User = Depends(get_current_user)):
    #Fetch the user
    user = users_db.get(str(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    #Check if the current user is an admin or the user themselves
    if not current_user.is_admin and current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this user's details."
        )
    
    # Return user details, excluding sensitive fields like password
    return UserUpdateResponseModel(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )




#UPDATE user detail
@router.put("/users/{user_id}", response_model=UserUpdateResponseModel)
async def update_user(user_id: UUID, update_data: UserUpdateRequestModel, current_user: User = Depends(get_current_active_user)):

    #Authenticated user is trying to update their own information
    if str(user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own details.")
    
    user = users_db.get(str(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    #Validate and update the email if provided
    if update_data.email:
        if any(existing_user.email == update_data.email for existing_user in users_db.values() if existing_user.id != user_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
        user.email = update_data.email

    if update_data.username:
        user.username = update_data.username

    if update_data.password:
        if not is_valid_password(update_data.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password does not meet the security requirements.")
        user.hashed_password = get_password_hash(update_data.password)

    user.updated_at = datetime.now(timezone.utc)

    users_db[str(user.id)] = user

    return UserUpdateResponseModel(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )



#DELETE User
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, current_user: User = Depends(get_current_user)):
    
    if str(user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own account.")

    user = users_db.get(str(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    """
    This part will be for checking active orders
    """

    del users_db[str(user_id)]
    #Return 204 no content
    return


#GET all users 
@router.get("/users", response_model=list[UserCreateResponseModel], status_code=status.HTTP_200_OK)
async def get_all_users(current_admin: User = Depends(get_current_admin)):

    try:
        all_users = list(users_db.values())

        return [
            UserUpdateResponseModel(
                id=user.id,
                username=user.username,
                email=user.email,
                is_admin=user.is_admin,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in all_users
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving users: {str(e)}"
        )
    


#List orders for a user 
@router.get("/users/{user_id}/orders", status_code=status.HTTP_200_OK)
async def list_user_orders(user_id: UUID, current_user: User = Depends(get_current_active_user)):
    
    if str(user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own orders.")
    
    """
        Code in progress

    """


#Change role 
@router.put("/users/change_role", status_code=status.HTTP_200_OK)
async def change_role(request: ChangeRoleRequest, current_admin: User = Depends(get_current_admin)):

    try:
        user = users_db.get(str(request.user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        user.is_admin = request.is_admin
        users_db[str(request.user_id)] = user  

        return {"message": "User role updated successfully."}
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the user role: {str(e)}"
        )
    


