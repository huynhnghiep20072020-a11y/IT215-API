from fastapi import APIRouter, HTTPException, Request, status
from datetime import datetime
from schemas import UnifiedResponse
from data import orders_db

router = APIRouter()

@router.delete("/orders/{order_id}", response_model=UnifiedResponse)
def cancel_order(order_id: int, request: Request):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
        
    if order["status"] == "DELIVERED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot cancel a delivered order"
        )
        
    order["status"] = "CANCELLED"
    
    return {
        "statusCode": status.HTTP_200_OK,
        "message": "Hủy đơn hàng thành công",
        "data": order,
        "error": None,
        "timestamp": datetime.now().isoformat(),
        "path": request.url.path
    }