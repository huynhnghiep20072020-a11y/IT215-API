from fastapi import APIRouter, HTTPException, status
from schemas import ProductUpdate
from data import products

router = APIRouter()

@router.put("/products/{product_id}")
def update_product(product_id: int, product_update: ProductUpdate):
    target_product = next((p for p in products if p["id"] == product_id), None)
    
    if not target_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )

    for p in products:
        if p["code"] == product_update.code and p["id"] != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Product code already exists"
            )

    target_product["code"] = product_update.code
    target_product["name"] = product_update.name
    target_product["price"] = product_update.price
    target_product["stock"] = product_update.stock

    return target_product