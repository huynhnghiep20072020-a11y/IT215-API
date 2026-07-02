from fastapi import APIRouter, HTTPException, status
from data import orders_dict

router = APIRouter()

@router.get("/orders/{order_id}/payment")
def get_order_payment(order_id: int):
    try:
        if order_id not in orders_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Order not found"
            )
            
        order = orders_dict[order_id]
        
        return {
            "payment_status": order["payment_status"],
            "method": order["method"]
        }
        
    except HTTPException:
        raise
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra sự cố hệ thống. Vui lòng thử lại sau."
        )