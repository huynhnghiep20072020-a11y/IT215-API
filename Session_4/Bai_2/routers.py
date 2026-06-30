from fastapi import APIRouter
from data import orders

router = APIRouter()

@router.get("/orders/status/{status}")
def get_orders_by_status(status: str):
    valid_statuses = ["pending", "paid", "cancelled"]
    
    if status not in valid_statuses:
        return {
            "message": "Trạng thái đơn hàng không hợp lệ"
        }
        
    filtered_orders = [order for order in orders if order.get("status") == status]
    
    return filtered_orders