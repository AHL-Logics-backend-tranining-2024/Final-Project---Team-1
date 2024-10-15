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
def list_products(db: Session, page: int = 1, page_size: int = 10) -> List[schemas.Product]:
    offset = (page - 1) * page_size
    products = db.query(models.Product).offset(offset).limit(page_size).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found.")

    return products
# Search Products
def search_products(db: Session, filter_query: schemas.ProductSearchParams):
    name = filter_query.name
    min_price = filter_query.min_price
    max_price = filter_query.max_price
    is_available = filter_query.is_available
    page = filter_query.page
    page_size = filter_query.page_size
    sort_by = filter_query.sort_by
    sort_order = filter_query.sort_order
    pass