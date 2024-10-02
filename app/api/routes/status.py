from fastapi import APIRouter, HTTPException, Depends, Header
from uuid import UUID, uuid4
from typing import Dict
from pydantic import BaseModel, Field
from models import StatusCreate,StatusUpdate,Status
from dependencies import get_current_admin,get_current_time,statuses,orders_db

router = APIRouter()

"""Create Status"""
@router.post("/statuses/", status_code=201)
async def create_status(status: StatusCreate, admin: bool = Depends(get_current_admin)):
# Check if the status is unique or not
    try:
        if status.name.lower() in statuses:
            raise HTTPException(status_code=400, detail="Status name must be unique.")
        
        new_status = Status(name=status.name)
        statuses[new_status.id] = new_status
        return new_status.to_dict()
    
    except HTTPException as e:
        raise e(status_code=400, detail="Bad Request")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
"""Get the status by the ID"""
@router.get("/statuses/{status_id}",status_code=200)
async def get_user(status_id: UUID,admin: bool = Depends(get_current_admin)):
    try:
        status = statuses.get(status_id)
        if status_id not in statuses:
            raise HTTPException(status_code=404, detail="Status not found.")
        return status.to_dict()
    
# Handle multiple Exceptions (403, 404)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
"""Update the tasks by the ID"""
@router.put("/statuses/{status_id}",status_code=201)
async def update_status(status_id: UUID,status_update: StatusUpdate,admin: bool = Depends(get_current_admin)):
    try:
        status = statuses.get(status_id)
        if not status:
            raise HTTPException(status_code=404, detail="Status not found")
        if any(
            existing_status['name'].lower() == status_update.name.lower() and existing_status['id'] != status_id for existing_status in statuses.values()):
            raise HTTPException(status_code=400, detail="Status name must be unique.")
        
        status.update(name=status_update.name)

        return status.to_dict()
#Handle multiple Exceptions
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
"""Delete the Status by ID"""
@router.delete("/statuses/{status_id}", status_code=200)
async def remove_status(status_id: UUID,admin: bool = Depends(get_current_admin)):
    try:
        if status_id not in statuses:
            raise HTTPException(status_code=404, detail="Status not found.")
        for order in orders_db.values():
            if order['status_id'] == str(status_id):
                raise HTTPException(status_code=400, detail="Cannot delete status. It is currently in use by an order.")
# This peace of code to be completed 

        del statuses[status_id]
        return {"detail": "Status successfully deleted."}
# Handle multiple Exceptions (403, 400, 404)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") 
