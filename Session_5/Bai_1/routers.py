from fastapi import APIRouter, HTTPException, status
from schemas import ProductCreate
from data import products

router = APIRouter()

@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    for p in products:
        if p["code"] == product.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Mã sản phẩm đã tồn tại trong hệ thống"
            )

    new_product = {
        "id": len(products) + 1,
        "code": product.code,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }
    products.append(new_product)
    
    return {
        "message": "Create product successfully",
        "data": new_product
    }