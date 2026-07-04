from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

class AssetStatus(str, Enum):
    READY = "READY"
    ALLOCATED = "ALLOCATED"
    REPAIRING = "REPAIRING"
    SCRAPPED = "SCRAPPED"

class AssetCreate(BaseModel):
    serial_number: str = Field(..., min_length=1)
    model: str = Field(..., min_length=2, max_length=255)
    stock_available: int = Field(..., ge=0)
    status: AssetStatus

class AssetUpdate(AssetCreate):
    pass

class AllocationCreate(BaseModel):
    asset_id: int
    employee_email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    allocated_quantity: int = Field(..., gt=0)
    start_date: date
    duration_months: int = Field(..., ge=1, le=12)