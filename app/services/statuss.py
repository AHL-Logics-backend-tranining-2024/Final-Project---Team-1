from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

def create_status(db: Session, status_data: schemas.StatusCreate):
    # Check if the status already exists
    existing_status = db.query(models.Status).filter(models.Status.name == status_data.name).first()
    if existing_status:
        raise HTTPException(status_code=400, detail="Status name must be unique.")
    new_status = models.Status(name=status_data.name)
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    return new_status

def get_status_by_id(db: Session, status_id: str):
    # Retrieve the status by ID
    status = db.query(models.Status).filter(models.Status.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status

def update_status(db: Session, status_id: str, status_update: schemas.StatusUpdate):
    # Retrieve the status by ID
    status = get_status_by_id(db, status_id)
    
    # Check if another status with the same name exists
    existing_status = db.query(models.Status).filter(models.Status.name == status_update.name, models.Status.id != status_id).first()
    if existing_status:
        raise HTTPException(status_code=400, detail="Status name must be unique.")
    status.name = status_update.name
    db.commit()
    db.refresh(status)
    return status

def delete_status(db: Session, status_id: str):
    # Retrieve the status by ID
    status = get_status_by_id(db, status_id)
    
    # TODO: Check if any orders are using this status before deleting it
    order_in_use = db.query(models.Order).filter(models.Order.status_id == status_id).first()
    if order_in_use:
        raise HTTPException(status_code=400, detail="Cannot delete status. It is currently in use by an order.")
    
    db.delete(status)
    db.commit()