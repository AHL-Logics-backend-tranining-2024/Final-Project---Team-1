from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException , status
from .. import models, schemas


def calculate_total_price(db: Session, products):
    total_price = 0

    for product_data in products:
        product = db.query(models.Product).filter(models.Product.id == product_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_data.product_id} not found.")
        
        if not product.is_available:
            raise HTTPException(
                status_code=400, detail=f"Product '{product.name}' is currently unavailable."
            )

        if product.stock < product_data.quantity:
            raise HTTPException(
                status_code=400, detail=f"Insufficient stock for product '{product.name}'."
            )

        total_price += product.price * product_data.quantity

    return total_price

def add_order_products(db: Session, order_id: uuid.UUID, products):
    for product_data in products:
        order_product = models.OrderProduct(
            order_id=order_id,
            product_id=product_data.product_id,
            quantity=product_data.quantity,
        )
        db.add(order_product)

        # Update the stock of the product
        product = db.query(models.Product).filter(models.Product.id == product_data.product_id).first()
        product.stock -= product_data.quantity

    db.commit()

def create_order(db: Session, user_id: uuid.UUID, order_data: schemas.OrderCreateRequest):
    status = db.query(models.OrderStatus).filter(models.OrderStatus.name == "pending").first()
    if not status:
        raise HTTPException(status_code=500, detail="Default status 'pending' not found.")

    total_price = calculate_total_price(db, order_data.products)

    new_order = models.Order(user_id=user_id, status_id=status.id, total_price=total_price)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    add_order_products(db, new_order.id, order_data.products)

    return new_order


def get_order_by_id(order_id: str, db: Session):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def update_order_status(order_id: str, status_name: str, db: Session):
    order = get_order_by_id(order_id, db)
    status = db.query(models.OrderStatus).filter(models.OrderStatus.name == status_name).first()
    if not status:
        raise HTTPException(status_code=400, detail="Invalid status")
    order.status_id = status.id
    db.commit()
    db.refresh(order)
    return order

def cancel_order(order_id: str, db: Session):
    order = get_order_by_id(order_id, db)
    if order.status.name != "pending":
        raise HTTPException(status_code=400, detail="Only pending orders can be canceled")
    status = db.query(models.OrderStatus).filter(models.OrderStatus.name == "canceled").first()
    if not status:
        raise HTTPException(status_code=500, detail="Status 'canceled' not found")
    order.status_id = status.id
    db.commit()




def get_orders_for_user(user_id: str, db: Session) -> List[schemas.OrderDetailResponse]:
    # Query all orders to the given user_id
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()

    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No orders found for the specified user."
        )

    return orders