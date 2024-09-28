from fastapi import APIRouter, HTTPException, Depends, Header
from uuid import UUID, uuid4
from typing import Dict
from datetime import datetime
from pydantic import BaseModel, Field

router = APIRouter()

statuses : Dict[UUID,Dict]={}

class StatusCreate(BaseModel):
    name:str=Field(...,description="Status name example (pending, processing, completed, canceled)")

def admin_check(admin: str = Header(None)):
    if admin != "true":
        raise HTTPException(status_code=403, detail="Admin access required")
def get_current_time():
    return datetime.utcnow().isoformat()
"""Create Status"""
@router.post("/statuses/", status_code=201)
async def create_status(status: StatusCreate, admin: bool = Depends(admin_check)):
    try:
        for names in statuses.values():
            if names['name'].lower() == status.name.lower():
                raise HTTPException(status_code=400, detail="Status name must be unique.")
        status_id=uuid4()
        new_status = {
            "id": status_id,
            "name": status.name,
            "created_at": get_current_time(),
            "updated_at": get_current_time(),
            }
        statuses[status_id] = new_status
        return new_status
    except HTTPException as e:
        raise e(status_code=400, detail="Bad Request")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
