from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class PackageResponse(BaseModel):
    id: int
    package_code: str
    weight: float
    warehouse_id: int

    model_config = ConfigDict(from_attributes=True)

class WarehouseCreate(BaseModel):
    warehouse_name: str
    location: str

class WarehouseDetailResponse(BaseModel):
    id: int
    warehouse_name: str
    location: str
    packages: List[PackageResponse]

    model_config = ConfigDict(from_attributes=True)

class PackageUpdate(BaseModel):
    package_code: Optional[str] = None
    weight: Optional[float] = None
    warehouse_id: Optional[int] = None

class WaybillResponse(BaseModel):
    id: int
    tracking_number: str
    shipping_status: str
    package_id: int

    model_config = ConfigDict(from_attributes=True)