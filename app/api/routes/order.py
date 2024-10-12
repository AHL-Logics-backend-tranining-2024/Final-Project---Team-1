from fastapi import APIRouter, Depends, HTTPException,status
from app.api.routes.dependencies import get_current_active_user, get_current_admin, get_current_user, products_db, orders_db
from app.models import *

router = APIRouter()


@router.post("/orders/", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_request: OrderCreateRequest,
    current_user: dict = Depends(get_current_active_user),
):
    if not order_request.products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one product must be provided."
        )

    # Initialize total price
    total_price = 0.0

    for item in order_request.products:
        product = products_db.get(item.product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found."
            )

        # Calculate item price and add to total price
        item_price = product['price'] * item.quantity
        total_price += item_price

    new_order_id = uuid4()

    # New order with a default status of "pending"
    new_order = {
        "id": new_order_id,
        "user_id": current_user["id"],
        "status": "pending",
        "total_price": total_price,
        "created_at": datetime.now(timezone.utc),
        "products": order_request.products
    }

    orders_db[new_order_id] = new_order

    return OrderCreateResponse(
        id=new_order["id"],
        user_id=new_order["user_id"],
        status=new_order["status"],
        total_price=new_order["total_price"],
        created_at=new_order["created_at"]
    )




@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
async def get_order_details(order_id: UUID):
    order = orders_db.get(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )
    
    products = [
        ProductOrder(product_id=product['product_id'], quantity=product['quantity'])
        for product in order['products']
    ]

    return OrderDetailResponse(
        id=order["id"],
        user_id=order["user_id"],
        status=order["status"],
        total_price=round(order["total_price"], 2),
        created_at=order["created_at"],
        updated_at=order.get("updated_at", order["created_at"]),  # Optional updated_at
        products=products
    )




@router.put("/orders/{order_id}/status", response_model=OrderUpdateResponse)
async def update_order_status(order_id: UUID, update_data: UpdateOrderStatusRequest, admin: dict = Depends(get_current_admin)):
    if not admin["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update order status."
        )

    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )

    order["status"] = update_data.status
    order["updated_at"] = datetime.now(timezone.utc)

    return OrderUpdateResponse(
        id=order["id"],
        user_id=order["user_id"],
        status=order["status"],
        total_price=round(order["total_price"], 2),
        created_at=order["created_at"],
        updated_at=order["updated_at"]
    )



@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: UUID, user: dict = Depends(get_current_user)):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )

    if order["user_id"] != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to cancel this order."
        )

    if order["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be canceled."
        )

    order["status"] = "canceled"
    order["updated_at"] = datetime.now(timezone.utc)

    #204 status
    return None