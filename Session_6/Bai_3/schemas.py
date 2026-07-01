from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

class RoomStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"

class RoomCreate(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)
    status: RoomStatus

class RoomUpdate(RoomCreate):
    pass

class BookingSlot(str, Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"

class BookingCreate(BaseModel):
    room_id: int
    class_name: str = Field(..., min_length=1)
    student_count: int = Field(..., gt=0)
    date: date
    slot: BookingSlot