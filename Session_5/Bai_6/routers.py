from fastapi import APIRouter, HTTPException, status
from schemas import ProductCreate
from data import products

router = APIRouter()

@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    new_id = max([p["id"] for p in products], default=0) + 1
    
    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price
    }
    
    products.append(new_product)
    
    return {
        "message": "Create product successfully",
        "data": new_product
    }

@router.get("/products")
def get_products():
    return products

@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    for index, p in enumerate(products):
        if p["id"] == product_id:
            deleted_product = products.pop(index)
            return {
                "message": "Delete product successfully",
                "data": deleted_product
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Product not found"
    )