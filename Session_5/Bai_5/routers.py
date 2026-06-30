from fastapi import APIRouter, HTTPException, status
from data import products

router = APIRouter()

@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    target_product = next((p for p in products if p["id"] == product_id), None)
    
    if not target_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )
        
    if not target_product["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Product already inactive"
        )
        
    target_product["is_active"] = False
    
    return {
        "message": "Ngừng kinh doanh thành công",
        "data": target_product
    }