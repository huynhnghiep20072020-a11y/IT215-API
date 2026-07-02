from fastapi import APIRouter, HTTPException, status
from schemas import OrderPublic
from data import orders_db

router = APIRouter()

@router.get("/orders/{order_id}", response_model=OrderPublic)
def get_order_detail(order_id: int):
    for order in orders_db:
        if order["id"] == order_id:
            return order
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Order not found"
    )