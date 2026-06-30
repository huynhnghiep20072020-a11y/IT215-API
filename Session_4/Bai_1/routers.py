from fastapi import APIRouter
from data import products

router = APIRouter()

@router.get("/products/{product_id}")
def get_product_detail(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product

    return {
        "message": "Không tìm thấy sản phẩm"
    }