from fastapi import APIRouter, HTTPException, status
from schemas import StatusUpdate
from data import orders_db

router = APIRouter()

@router.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
        
    return order

@router.put("/orders/{order_id}/status")
def update_order_status(order_id: int, data: StatusUpdate):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
        
    valid_statuses = ["PENDING", "SHIPPING", "DELIVERED"]
    
    if data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Trạng thái không hợp lệ"
        )
        
    order["status"] = data.status

    return {
        "message": "Cập nhật thành công", 
        "data": order
    }