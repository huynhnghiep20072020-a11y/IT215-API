from fastapi import APIRouter, HTTPException, status, Request
from typing import Optional
from datetime import datetime, timezone
from schemas import FlightCreate
from data import flights_db

router = APIRouter()

def get_current_time_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

@router.get("/flights", status_code=status.HTTP_200_OK)
async def get_flights(request: Request, flight_status: Optional[str] = None):
    result = flights_db
    if flight_status is not None:
        result = [f for f in result if f["status"] == flight_status]
        
    return {
        "statusCode": status.HTTP_200_OK,
        "message": "Lấy danh sách chuyến bay thành công!",
        "data": result,
        "error": None,
        "timestamp": get_current_time_str(),
        "path": request.url.path
    }

@router.post("/flights", status_code=status.HTTP_201_CREATED)
async def create_flight(flight: FlightCreate, request: Request):
    for f in flights_db:
        if f["flight_number"] == flight.flight_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Lỗi: Số hiệu chuyến bay này đã tồn tại trên hệ thống điều hành!",
                    "error": "ERR-AIR-01: Flight number conflict in current active schedule database."
                }
            )
            
    new_id = max([f["id"] for f in flights_db], default=0) + 1
    new_flight = {
        "id": new_id,
        "flight_number": flight.flight_number,
        "destination": flight.destination,
        "available_seats": flight.available_seats,
        "status": "scheduled",
        "created_at": get_current_time_str()
    }
    
    flights_db.append(new_flight)
    
    return {
        "statusCode": status.HTTP_201_CREATED,
        "message": "Khởi tạo chuyến bay mới thành công!",
        "data": new_flight,
        "error": None,
        "timestamp": get_current_time_str(),
        "path": request.url.path
    }

@router.delete("/flights/{flight_id}", status_code=status.HTTP_200_OK)
async def delete_flight(flight_id: int, request: Request):
    for index, f in enumerate(flights_db):
        if f["id"] == flight_id:
            flights_db.pop(index)
            return {
                "statusCode": status.HTTP_200_OK,
                "message": "Hủy chuyến bay thành công!",
                "data": None,
                "error": None,
                "timestamp": get_current_time_str(),
                "path": request.url.path
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "message": "Lỗi: Không tìm thấy mã chuyến bay yêu cầu để hủy!",
            "error": "ERR-AIR-02: Target flight ID is missing from system scope."
        }
    )