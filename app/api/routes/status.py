from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from schemas import StatusCreate, StatusUpdate
from models import Status
from dependencies import get_current_admin
from services.status_service import create_status_service,get_status_by_id_service,update_status_service,delete_status_service

router = APIRouter()

"""Create Status"""
@router.post("/statuses/", status_code=201)
async def create_status(status: StatusCreate, admin: bool = Depends(get_current_admin)):
    try:
        new_status = create_status_service(status)
        return new_status
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
"""Get Status by ID"""
@router.get("/statuses/{status_id}", status_code=200)
async def get_status(status_id: UUID, admin: bool = Depends(get_current_admin)):
    try:
        status = get_status_by_id_service(status_id)
        return status
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
"""Update Status by ID"""
@router.put("/statuses/{status_id}", status_code=200)
async def update_status(status_id: UUID, status_update: StatusUpdate, admin: bool = Depends(get_current_admin)):
    try:
        updated_status = update_status_service(status_id, status_update)
        return updated_status
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

"""Delete Status by ID"""
@router.delete("/statuses/{status_id}", status_code=200)
async def delete_status(status_id: UUID, admin: bool = Depends(get_current_admin)):
    try:
        delete_status_service(status_id)
        return {"detail": "Status successfully deleted."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


