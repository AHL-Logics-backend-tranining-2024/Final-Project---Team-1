from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel
from models import Product
from app.api.routes.dependencies import get_current_admin
from models import ProductCreate, ProductUpdate, ProductSearchParams 
from database import get_db

router = APIRouter()

"""Create a Product"""
@router.post("/products/", status_code=201)
async def create_product(product: ProductCreate, admin: bool = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        existing_product = db.query(Product).filter(Product.name == product.name).first()
        if existing_product:
            raise HTTPException(status_code=400, detail=f"Product name '{product.name}' already exists. Please use a unique name.")
        
        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            is_available=product.is_available
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
"""Get Product by ID"""
@router.get("/products/{product_id}", status_code=200, response_model=Product)
async def get_product_details(product_id: UUID, db: Session = Depends(get_db)):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
        return product
    except ValueError:
        raise HTTPException(status_code=400,detail="Product ID must be a valid integer." )
"""Update by ID"""
@router.put("/products/{product_id}", status_code=200, response_model=Product)
async def update_product(product_id: UUID, update_data: ProductUpdate, admin: bool = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
        if update_data.name:
            existing_product = db.query(Product).filter(Product.name == update_data.name, Product.id != product_id).first()
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
    except Exception as e:
        raise (e)
    
"""Delete Product by ID"""
@router.delete("/products/{product_id}", status_code=200)
async def delete_product(product_id: UUID, admin: bool = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
        
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=500, detail="An error occurred while deleting the product.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""List Products"""
@router.get("/products", status_code=200, response_model=List[Product])
async def list_products(db: Session = Depends(get_db)):
    try:
        products = db.query(Product).all()
        if not products:
            return []
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
"""Search Products"""
@router.get("/products/search", status_code=200)
async def search_products(product: ProductSearchParams, db: Session = Depends(get_db)):
    try:
        query = db.query(Product)
        if product.min_price is not None:
            query = query.filter(Product.price >= product.min_price)
        
        if product.max_price is not None:
            query = query.filter(Product.price <= product.max_price)
        
        if product.is_available is not None:
            query = query.filter(Product.is_available == product.is_available)
        
        products = query.all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")