from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

class CarrierStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class Shift(str, Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    NIGHT = "NIGHT"

class CarrierCreate(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=3)
    max_weight_capacity: int = Field(..., gt=0)
    status: CarrierStatus

class CarrierUpdate(CarrierCreate):
    pass

class ShipmentCreate(BaseModel):
    carrier_id: int
    order_reference: str = Field(..., min_length=1)
    total_weight: int = Field(..., gt=0)
    dispatch_date: date
    shift: Shift