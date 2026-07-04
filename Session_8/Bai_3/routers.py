from fastapi import APIRouter, HTTPException, status, Response
from typing import Optional
from schemas import DeskCreate, DeskUpdate, BookingCreate, DeskStatus
from data import desks, bookings

router = APIRouter()

@router.post("/desks", status_code=status.HTTP_201_CREATED)
def create_desk(desk: DeskCreate):
    for d in desks:
        if d["desk_number"] == desk.desk_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã bàn đã tồn tại"
            )
            
    new_id = max([d["id"] for d in desks], default=0) + 1
    new_desk = {
        "id": new_id,
        "desk_number": desk.desk_number,
        "zone": desk.zone,
        "price_per_day": desk.price_per_day,
        "status": desk.status.value
    }
    
    desks.append(new_desk)
    
    return {
        "message": "Thêm bàn làm việc thành công",
        "data": new_desk
    }

@router.get("/desks")
def get_desks(
    zone_keyword: Optional[str] = None,
    max_price: Optional[float] = None,
    status: Optional[DeskStatus] = None
):
    result = desks
    
    if zone_keyword is not None:
        kw = zone_keyword.lower()
        result = [d for d in result if kw in d["zone"].lower()]
        
    if max_price is not None:
        result = [d for d in result if d["price_per_day"] <= max_price]
        
    if status is not None:
        result = [d for d in result if d["status"] == status.value]
        
    return {
        "message": "Lấy danh sách bàn làm việc thành công",
        "data": result
    }

@router.get("/desks/{desk_id}")
def get_desk_detail(desk_id: int):
    target = next((d for d in desks if d["id"] == desk_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desk not found"
        )
        
    return {
        "message": "Lấy chi tiết bàn thành công",
        "data": target
    }

@router.put("/desks/{desk_id}")
def update_desk(desk_id: int, desk_update: DeskUpdate):
    target = next((d for d in desks if d["id"] == desk_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desk not found"
        )
        
    for d in desks:
        if d["desk_number"] == desk_update.desk_number and d["id"] != desk_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã bàn đã tồn tại"
            )
            
    target["desk_number"] = desk_update.desk_number
    target["zone"] = desk_update.zone
    target["price_per_day"] = desk_update.price_per_day
    target["status"] = desk_update.status.value
    
    return {
        "message": "Cập nhật bàn làm việc thành công",
        "data": target
    }

@router.delete("/desks/{desk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_desk(desk_id: int):
    for index, d in enumerate(desks):
        if d["id"] == desk_id:
            desks.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Desk not found"
    )

@router.post("/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate):
    desk = next((d for d in desks if d["id"] == booking.desk_id), None)
    
    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desk not found"
        )
        
    if desk["status"] != "AVAILABLE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bàn làm việc không ở trạng thái AVAILABLE"
        )
        
    booking_date_str = booking.booking_date.isoformat()
    
    for b in bookings:
        if b["desk_id"] == booking.desk_id and b["booking_date"] == booking_date_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vị trí này đã có người đặt trong ngày"
            )
            
    new_id = max([b["id"] for b in bookings], default=0) + 1
    new_booking = {
        "id": new_id,
        "desk_id": booking.desk_id,
        "customer_name": booking.customer_name,
        "booking_date": booking_date_str,
        "payment_status": booking.payment_status.value
    }
    
    bookings.append(new_booking)
    
    return {
        "message": "Đăng ký đặt chỗ bàn làm việc thành công",
        "data": new_booking
    }

@router.get("/bookings")
def get_bookings():
    return {
        "message": "Lấy danh sách lịch sử đặt chỗ thành công",
        "data": bookings
    }