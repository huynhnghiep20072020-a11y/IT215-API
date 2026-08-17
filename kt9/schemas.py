from pydantic import BaseModel, Field

class FlightCreate(BaseModel):
    flight_number: str = Field(..., min_length=5, max_length=10)
    destination: str = Field(..., min_length=1)
    available_seats: int = Field(..., ge=1)