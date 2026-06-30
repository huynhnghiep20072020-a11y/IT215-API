from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class StudentCreate(BaseModel):
    full_name: str = Field(..., min_length=3)
    email: EmailStr
    age: Optional[int] = None
    course: Optional[str] = None
    phone: Optional[str] = None