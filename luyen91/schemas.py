from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime

class VehicleBase(BaseModel):
    brand: str = Field(..., min_length=2, max_length=50, description="Hãng xe")
    model: str = Field(..., min_length=1, description="Dòng xe")
    daily_rate: float = Field(..., gt=0, description="Giá thuê phải lớn hơn 0")
    production_year: int = Field(..., ge=2010, le=2026, description="Năm sản xuất 2010 - 2026")
    status: str = Field(default="available")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ["available", "rented", "maintenance"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v

class VehicleCreate(VehicleBase):
    id: str = Field(..., min_length=1, description="Mã xe duy nhất")

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str):
        return v.upper()  # Ép mã xe thành chữ in hoa

class VehicleUpdate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: str

    class Config:
        from_attributes = True

# Lớp biểu diễn chuẩn 6 trường đầu ra của doanh nghiệp
class StandardResponse(BaseModel):
    statusCode: int
    data: Any
    message: str
    timestamp: str
    path: str
    error: Optional[str]