from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from models import Status as StatusModel,StatusCreate,StatusUpdate,OrderModel
from database import get_db
from dependencies import get_current_admin

router = APIRouter()

# Create Status
@router.post("/statuses/", status_code=201)
async def create_status(status: StatusCreate, db: Session = Depends(get_db), admin: bool = Depends(get_current_admin)):
    try:
        existing_status = db.query(StatusModel).filter(StatusModel.name == status.name).first()
        if existing_status:
            raise HTTPException(status_code=400, detail="Status name must be unique.")
        
        new_status = StatusModel(name=status.name)
        db.add(new_status)
        db.commit()
        db.refresh(new_status)
        return new_status.to_dict()
    
    except HTTPException as e:
        raise e(status_code=400, detail="Bad Request")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get Status by ID
@router.get("/statuses/{status_id}", status_code=200)
async def get_status(status_id: UUID, db: Session = Depends(get_db), admin: bool = Depends(get_current_admin)):
    try:
        status = db.query(StatusModel).filter(StatusModel.id == status_id).first()
        if not status:
            raise HTTPException(status_code=404, detail="Status not found.")
        return status.to_dict()
    
    except HTTPException as e:
        raise e(status_code=404, detail="Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Update Status by ID
@router.put("/statuses/{status_id}", status_code=200)
async def update_status(status_id: UUID, status_update: StatusUpdate, db: Session = Depends(get_db), admin: bool = Depends(get_current_admin)):
    try:
        status = db.query(StatusModel).filter(StatusModel.id == status_id).first()
        if not status:
            raise HTTPException(status_code=404, detail="Status not found.")
    
        # Check for unique status name
        existing_status = db.query(StatusModel).filter(StatusModel.name == status_update.name, StatusModel.id != status_id).first()
        if existing_status:
            raise HTTPException(status_code=400, detail="Status name must be unique.")
        
        status.name = status_update.name
        db.commit()
        db.refresh(status)
        return status.to_dict()
    
    except HTTPException as e:
        raise e(status_code=400, detail="Bad Request")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# Delete Status by ID
@router.delete("/statuses/{status_id}", status_code=200)
async def delete_status(status_id: UUID, db: Session = Depends(get_db), admin: bool = Depends(get_current_admin)):
    try:
        status = db.query(StatusModel).filter(StatusModel.id == status_id).first()
        if not status:
            raise HTTPException(status_code=404, detail="Status not found.")
        
        # Check if status is used by any order
        # To be completed when the order is ready "(Very Important Note)""
        order_in_use = db.query(OrderModel).filter(OrderModel.status_id == status_id).first()
        if order_in_use:
            raise HTTPException(status_code=400, detail="Cannot delete status. It is currently in use by an order.")
        
        db.delete(status)
        db.commit()
        return {"detail": "Status successfully deleted."}
    
    except HTTPException as e:
        raise e(status_code=404, detail="Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")