from fastapi import APIRouter, HTTPException, status
from typing import Optional
from schemas import RoomCreate, RoomUpdate, BookingCreate, RoomStatus
from data import rooms, room_bookings

router = APIRouter()

@router.post("/rooms", status_code=status.HTTP_201_CREATED)
def create_room(room: RoomCreate):
    for r in rooms:
        if r["code"] == room.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã phòng đã tồn tại"
            )
            
    new_id = max([r["id"] for r in rooms], default=0) + 1
    new_room = {
        "id": new_id,
        "code": room.code,
        "name": room.name,
        "capacity": room.capacity,
        "status": room.status.value
    }
    
    rooms.append(new_room)
    
    return {
        "message": "Thêm phòng học thành công",
        "data": new_room
    }

@router.get("/rooms")
def get_rooms(
    keyword: Optional[str] = None,
    status: Optional[RoomStatus] = None,
    min_capacity: Optional[int] = None
):
    result = rooms
    
    if keyword is not None:
        kw = keyword.lower()
        result = [
            r for r in result
            if kw in r["code"].lower() or kw in r["name"].lower()
        ]
        
    if status is not None:
        result = [r for r in result if r["status"] == status.value]
        
    if min_capacity is not None:
        result = [r for r in result if r["capacity"] >= min_capacity]
        
    return {
        "message": "Lấy danh sách phòng học thành công",
        "data": result
    }

@router.get("/rooms/{room_id}")
def get_room_detail(room_id: int):
    target = next((r for r in rooms if r["id"] == room_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
        
    return {
        "message": "Lấy chi tiết phòng học thành công",
        "data": target
    }

@router.put("/rooms/{room_id}")
def update_room(room_id: int, room_update: RoomUpdate):
    target = next((r for r in rooms if r["id"] == room_id), None)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
        
    for r in rooms:
        if r["code"] == room_update.code and r["id"] != room_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã phòng đã tồn tại"
            )
            
    target["code"] = room_update.code
    target["name"] = room_update.name
    target["capacity"] = room_update.capacity
    target["status"] = room_update.status.value
    
    return {
        "message": "Cập nhật phòng học thành công",
        "data": target
    }

@router.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    for index, r in enumerate(rooms):
        if r["id"] == room_id:
            deleted_room = rooms.pop(index)
            return {
                "message": "Xóa phòng học thành công",
                "data": deleted_room
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Room not found"
    )

@router.post("/room-bookings", status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate):
    room = next((r for r in rooms if r["id"] == booking.room_id), None)
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
        
    if room["status"] != "AVAILABLE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phòng không ở trạng thái AVAILABLE"
        )
        
    if booking.student_count > room["capacity"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng học viên vượt quá sức chứa của phòng"
        )

    booking_date_str = booking.date.isoformat()
    
    for b in room_bookings:
        if b["room_id"] == booking.room_id and b["date"] == booking_date_str and b["slot"] == booking.slot.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phòng đã được đặt trong ca học này"
            )

    new_id = max([b["id"] for b in room_bookings], default=0) + 1
    
    new_booking = {
        "id": new_id,
        "room_id": booking.room_id,
        "class_name": booking.class_name,
        "student_count": booking.student_count,
        "date": booking_date_str,
        "slot": booking.slot.value
    }
    
    room_bookings.append(new_booking)
    
    return {
        "message": "Đặt lịch sử dụng phòng thành công",
        "data": new_booking
    }

@router.get("/room-bookings")
def get_bookings():
    return {
        "message": "Lấy danh sách đặt phòng thành công",
        "data": room_bookings
    }