from fastapi import APIRouter
from typing import Optional
from data import products

router = APIRouter()

@router.get("/products")
def get_products(keyword: Optional[str] = None, max_price: Optional[float] = None):
    if max_price is not None and max_price < 0:
        return {
            "detail": "max_price không được âm"
        }

    result = products

    if keyword is not None:
        result = [product for product in result if keyword.lower() in product["name"].lower()]

    if max_price is not None:
        result = [product for product in result if product["price"] <= max_price]

    return result