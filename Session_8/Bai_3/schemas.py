from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

class DeskStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    MAINTENANCE = "MAINTENANCE"

class DeskCreate(BaseModel):
    desk_number: str = Field(..., min_length=1)
    zone: str = Field(..., min_length=1)
    price_per_day: float = Field(..., gt=0)
    status: DeskStatus

class DeskUpdate(DeskCreate):
    pass

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class BookingCreate(BaseModel):
    desk_id: int
    customer_name: str = Field(..., min_length=1)
    booking_date: date
    payment_status: PaymentStatus