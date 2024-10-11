from fastapi import APIRouter, HTTPException, Depends,Query
from uuid import UUID, uuid4
from typing import Dict, Optional
from pydantic import BaseModel, Field
from dependencies import get_current_time,get_current_admin,products_db
from models import Product,ProductCreate,ProductUpdate,ProductSearchParams



router = APIRouter()
    
"""Create a Product"""
@router.post("/products/", status_code=201)
async def create_product(product: ProductCreate, admin: bool = Depends(get_current_admin)):
    
    if product.name.lower() in products_db:
        raise HTTPException(status_code=400, detail=f"Product name '{product.name}' already exists. Please use a unique name.")
    
    try:
        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            is_available=product.is_available
        )
        products_db[new_product.id] = new_product.to_dict()
        return new_product.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
"""Get the Product by ID"""
@router.get("/products/{product_id}",status_code=200 , response_model=Product)
async def get_product_details(product_id: UUID, admin: bool = Depends(get_current_admin)):
    try:
        product_uuid = UUID(product_id)
        product = products_db.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
    except ValueError:
        raise HTTPException(status_code=400,detail="Product ID must be a valid integer." )
    
    return product

"""Update products by the ID"""
@router.put("/products/{product_id}", status_code=200 ,response_model=Product)
async def update_product(product_id: UUID,update_data: ProductUpdate,admin: bool = Depends(get_current_admin)):
    
    try:
        product = products_db.get(product_id)
        raise HTTPException(status_code=404,detail=f"Product with ID {product_id} not found.")
        if update_data.name:
            if any(existing_product['name'].lower() == update_data.name.lower() for existing_product in products_db.values()):
                raise HTTPException(status_code=400,detail=f"Product name '{update_data.name}' already exists. Please use a unique name.")
        product.name = update_data.name
        if update_data.price is not None:
            product.price = update_data.price
        if update_data.stock is not None:
            product.stock = update_data.stock
    except Exception as e:
        raise (e) 
    

"""Delete product by the ID"""
@router.delete("/products/{product_id}", status_code=200)
async def delete_product(product_id: UUID):
    try:
        if product_id not in products_db:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
        del products_db[product_id]
        return {"message": "Product deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=500, detail="An error occurred while deleting the product.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

""" List Products"""
@router.get("/products", status_code=200)
async def list_products():
    if not products_db:
        return []
    
    products_list = []
    for product_id, product_data in products_db.items():
        product_dict = {
            "id": product_id,
            "name": product_data["name"],
            "price": product_data["price"],
            "description": product_data.get("description", ""), 
            "stock": product_data.get("stock", 0),  
            "isAvailable": product_data.get("isAvailable", True),  
            "created_at": product_data["created_at"]
        }
        products_list.append(product_dict)
    return products_list
    
""" Search for Product"""
@router.get("/products/search",status_code=200,response_model=dict)
async def search_products(product: ProductSearchParams):
    name = product.name
    min_price = product.min_price
    max_price = product.max_price
    isAvailable = product.isAvailable
    page = product.page
    page_size = product.page_size
    sort_by = product.sort_by
    sort_order = product.sort_order
    
    filtered_products = []
# Filling the array 
    for product_id, product_data in products_db.items():
        if name and name.lower() not in product_data["name"].lower():
            continue
        if min_price and product_data["price"] < min_price:
            continue
        if max_price and product_data["price"] > max_price:
            continue
        if isAvailable is not None and product_data["isAvailable"] != isAvailable:
            continue
        filtered_products.append({
            "id": product_id,
            "name": product_data["name"],
            "price": product_data["price"],
            "stock": product_data["stock"],
            "isAvailable": product_data["isAvailable"],
            "created_at": product_data["created_at"]
        })
        
    if not filtered_products:
        return []
    
    if sort_order == "asc":
        filtered_products.sort(key=lambda x: x[sort_by])
    elif sort_order == "desc":
        filtered_products.sort(key=lambda x: x[sort_by], reverse=True)
    total_products = len(filtered_products)
    total_pages = (total_products + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    paginated_products = filtered_products[start:end]
    
    return {
        "page": page,
        "total_pages": total_pages,
        "products_per_page": page_size,
        "total_products": total_products,
        "products": paginated_products
    }