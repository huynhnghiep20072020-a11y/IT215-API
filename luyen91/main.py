from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

import models, schemas, crud
from database import engine, get_db

# Tạo bảng trong DB nếu chưa có
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vehicle Management API")

# --- Hàm hỗ trợ định dạng Response 6 trường ---
def create_response(status_code: int, data: any, message: str, path: str, error: str = None):
    return {
        "statusCode": status_code,
        "data": data,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "path": path,
        "error": error
    }

# --- GLOBAL EXCEPTION HANDLERS ---
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return create_response(
        status_code=exc.status_code,
        data=None,
        message="Client Error",
        path=request.url.path,
        error=exc.detail
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Lấy message lỗi đầu tiên để hiển thị cho gọn
    error_msg = exc.errors()[0]['msg'] if exc.errors() else "Data validation failed"
    return create_response(
        status_code=422,
        data=None,
        message="Validation Error",
        path=request.url.path,
        error=error_msg
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Tránh crash app, trả về 500 nhưng vẫn chuẩn 6 trường
    return create_response(
        status_code=500,
        data=None,
        message="Internal Server Error",
        path=request.url.path,
        error=str(exc)
    )

# --- ENDPOINTS ---

@app.get("/vehicles", response_model=schemas.StandardResponse)
def get_vehicles(
    request: Request,
    brand: str = None, 
    status: str = None, 
    sort_by: str = None, 
    order: str = "asc", 
    db: Session = Depends(get_db)
):
    vehicles = crud.get_vehicles(db, brand=brand, status=status, sort_by=sort_by, order=order)
    return create_response(200, vehicles, "Fetched vehicles successfully", request.url.path)

@app.get("/vehicles/{vehicle_id}", response_model=schemas.StandardResponse)
def get_vehicle(vehicle_id: str, request: Request, db: Session = Depends(get_db)):
    vehicle = crud.get_vehicle_by_id(db, vehicle_id=vehicle_id.upper())
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")
    return create_response(200, vehicle, "Fetched vehicle details successfully", request.url.path)

@app.post("/vehicles", response_model=schemas.StandardResponse)
def create_vehicle(vehicle: schemas.VehicleCreate, request: Request, db: Session = Depends(get_db)):
    db_vehicle = crud.get_vehicle_by_id(db, vehicle_id=vehicle.id)
    if db_vehicle:
        raise HTTPException(status_code=409, detail="Vehicle ID already exists")
    
    new_vehicle = crud.create_vehicle(db=db, vehicle=vehicle)
    return create_response(201, new_vehicle, "Vehicle created successfully", request.url.path)

@app.put("/vehicles/{vehicle_id}", response_model=schemas.StandardResponse)
def update_vehicle(vehicle_id: str, vehicle_update: schemas.VehicleUpdate, request: Request, db: Session = Depends(get_db)):
    db_vehicle = crud.get_vehicle_by_id(db, vehicle_id=vehicle_id.upper())
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    updated_vehicle = crud.update_vehicle(db=db, db_vehicle=db_vehicle, vehicle_update=vehicle_update)
    return create_response(200, updated_vehicle, "Vehicle updated successfully", request.url.path)

@app.delete("/vehicles/{vehicle_id}", response_model=schemas.StandardResponse)
def delete_vehicle(vehicle_id: str, request: Request, db: Session = Depends(get_db)):
    db_vehicle = crud.get_vehicle_by_id(db, vehicle_id=vehicle_id.upper())
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return create_response(200, None, "Vehicle deleted successfully", request.url.path)