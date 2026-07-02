from fastapi import APIRouter, HTTPException, status
from schemas import OrderCreate
from data import products_db, orders_db

router = APIRouter()

@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    if order.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng mua phải lớn hơn 0"
        )
        
    product = next((p for p in products_db if p["id"] == order.product_id), None)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm"
        )
        
    if order.quantity > product["stock"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sản phẩm không đủ số lượng trong kho"
        )
        
    product["stock"] -= order.quantity
    
    new_order = {
        "id": len(orders_db) + 1,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total_price": order.quantity * product["price"]
    }
    
    orders_db.append(new_order)
    
    return {
        "message": "Tạo đơn hàng thành công",
        "data": new_order
    }