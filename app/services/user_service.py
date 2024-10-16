from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import UUID
from sqlalchemy.orm import Session
from .. import models, schemas
from api.auth_utlis import get_password_hash
from app.services import order_service



def get_user_by_id(user_id: str, db: Session) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()

def find_user_by_email_and_id(email: str, exclude_user_id: str, db: Session) -> models.User | None:
    return (
        db.query(models.User)
        .filter(models.User.email == email, models.User.id != exclude_user_id)
        .first()
    )
    
async def create_user(db: Session, user: schemas.UserCreateRequestModel) -> schemas.UserCreateResponseModel:
    # Check if the email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=False,  
        is_active=True, 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



def get_user_by_id(user_id: UUID, db: Session) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user


def update_user_in_db(
    user_id: UUID, 
    update_data: schemas.UserUpdateRequestModel, 
    db: Session) -> models.User:

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if update_data.username:
        user.username = update_data.username

    if update_data.email:
        existing_user = find_user_by_email_and_id(update_data.email, user_id, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already registered."
            )
        user.email = update_data.email

    if update_data.password:
        user.hashed_password = get_password_hash(update_data.password)

    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    return user



def delete_user_from_db(user_id: UUID, db: Session) -> None:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Check for active orders
    if order_service.has_active_orders(user_id, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Cannot delete user with active orders."
        )
    db.delete(user)
    db.commit()


def get_all_users(db: Session) -> list[schemas.GetUserResponseModel]:
    users = db.query(models.User).all()
    if not users:
        return []

    return [schemas.GetUserResponseModel.model_validate(user) for user in users]


def change_user_role(user_id: UUID, is_admin: bool, db: Session) -> None:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_admin = is_admin
    db.commit()


