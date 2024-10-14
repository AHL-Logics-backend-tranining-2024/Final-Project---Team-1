from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ... import models,schemas, database
from app.services import order_service
from app.api.routes import dependencies

router = APIRouter()

@router.post("/orders/", response_model=schemas.OrderCreateResponse, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(
    order: schemas.OrderCreateRequest, 
    db: Session = Depends(database.get_db), 
    current_user: dict = Depends(dependencies.get_current_user)
):
    new_order = order_service.create_order(db, current_user["id"], order)
    return new_order

@router.get("/orders/{order_id}", response_model=schemas.OrderDetailResponse, status_code=status.HTTP_200_OK)
def get_order_endpoint(order_id: str, db: Session = Depends(database.get_db)):
    order = order_service.get_order_by_id(order_id, db)
    return order

@router.put("/orders/{order_id}/status", response_model=schemas.OrderUpdateResponse, status_code=status.HTTP_200_OK)
def update_order_status_endpoint(
    order_id: str, 
    status_request: schemas.UpdateOrderStatusRequest, 
    db: Session = Depends(database.get_db), 
    admin_user: dict = Depends(dependencies.get_admin_user)
):
    updated_order = order_service.update_order_status(order_id, status_request.status, db)
    return updated_order

@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order_endpoint(
    order_id: str, 
    db: Session = Depends(database.get_db), 
    current_user: dict = Depends(dependencies.get_current_user)
):
    order_service.cancel_order(order_id, db)
    return None