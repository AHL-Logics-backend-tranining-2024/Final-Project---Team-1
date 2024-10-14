from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

# Create a Product
def create_product(db: Session, product_data: schemas.ProductCreate):
    existing_product = db.query(models.Product).filter(models.Product.name == product_data.name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail=f"Product name '{product_data.name}' already exists. Please use a unique name.")

    new_product = models.Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        is_available=product_data.is_available
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Get Product by ID
def get_product_by_id(product_id: str, db: Session):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
    return product

# Update Product by ID
def update_product(product_id: str, update_data: schemas.ProductUpdate, db: Session):
    product = get_product_by_id(product_id, db)

    if update_data.name:
        existing_product = db.query(models.Product).filter(models.Product.name == update_data.name, models.Product.id != product_id).first()
        if existing_product:
            raise HTTPException(status_code=400, detail=f"Product name '{update_data.name}' already exists. Please use a unique name.")
        product.name = update_data.name

    if update_data.description is not None:
        product.description = update_data.description
    if update_data.price is not None:
        product.price = update_data.price
    if update_data.stock is not None:
        product.stock = update_data.stock
    if update_data.is_available is not None:
        product.is_available = update_data.is_available

    db.commit()
    db.refresh(product)
    return product

# Delete Product by ID
def delete_product(product_id: str, db: Session):
    product = get_product_by_id(product_id, db)
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

# List Products
def list_products(db: Session) -> List[schemas.Product]:
    products = db.query(models.Product).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found.")
    return products
# Search Products
def search_products(search_params: schemas.ProductSearchParams, db: Session) -> List[schemas.Product]:
    query = db.query(models.Product)

    if search_params.min_price is not None:
        query = query.filter(models.Product.price >= search_params.min_price)

    if search_params.max_price is not None:
        query = query.filter(models.Product.price <= search_params.max_price)

    if search_params.is_available is not None:
        query = query.filter(models.Product.is_available == search_params.is_available)

    # Sorting
    if search_params.sort_by in ["created_at", "updated_at", "price"]:
        if search_params.sort_order == "desc":
            query = query.order_by(getattr(models.Product, search_params.sort_by).desc())
        else:
            query = query.order_by(getattr(models.Product, search_params.sort_by))

    products = query.all()
    if not products:
        raise HTTPException(status_code=404, detail="No products match the search criteria.")
    
    return products