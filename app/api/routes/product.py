from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ... import models, schemas, database
from app.services import products
from app.api.routes import dependencies
from database import get_db
from schemas import Product,ProductUpdate,ProductCreate,ProductSearchParams

router = APIRouter()
    
# Endpoint to create a new product
@router.post("/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    product: schemas.ProductCreate, 
    db: Session = Depends(database.get_db), 
    admin_user: dict = Depends(dependencies.get_current_admin)
):
    try:
        new_product = products.create_product(db, product)
        return new_product
    except ValueErrorr:
        raise HTTPException(status_code=404, detail="Bad Request .")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint to get a product by its ID
@router.get("/products/{product_id}", response_model=schemas.Product, status_code=status.HTTP_200_OK)
def get_product_endpoint(
    product_id: str, 
    db: Session = Depends(database.get_db)
):
    product = products.get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found.")
    return product

# Endpoint to update product details by ID
@router.put("/products/{product_id}", response_model=schemas.Product, status_code=status.HTTP_200_OK)
def update_product_endpoint(
    product_id: str, 
    product_update: schemas.ProductUpdateRequest, 
    db: Session = Depends(database.get_db), 
    admin_user: dict = Depends(dependencies.get_current_admin)
):
    try:
        updated_product = products.update_product(product_id, product_update, db)
        if not updated_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {product_id} not found.")
        return updated_product
    except ValueError:
        raise HTTPException(status_code=404, detail="Bad request")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint to delete a product by ID
@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(
    product_id: str, 
    db: Session = Depends(database.get_db), 
    admin_user: dict = Depends(dependencies.get_current_admin)
):
    try:
        products.delete_product(product_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to list all products
@router.get("/products", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
def list_products_endpoint(
    db: Session = Depends(database.get_db),
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_available: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "asc"
):
    products = products.list_products(
        db, name=name, min_price=min_price, max_price=max_price, is_available=is_available, 
        page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order
    )
    return products
# Endpoint to search for products based on query params
@router.get("/products/search", response_model=List[schemas.ProductResponse], status_code=status.HTTP_200_OK)
async def search_products_endpoint(
    filter_query: ProductSearchParams = Depends(),
    db: Session = Depends(database.get_db)
):
    products_list = products.search_products(
        db,
        filter_query=filter_query 
    )
    return products_list