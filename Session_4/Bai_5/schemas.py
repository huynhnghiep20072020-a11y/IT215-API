from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class StudentRegister(BaseModel):
    full_name: str = Field(..., min_length=3)
    email: EmailStr
    age: int = Field(..., ge=15, le=60)
    phone: str = Field(..., min_length=10, max_length=11, pattern=r'^\d+$')
    course: str
    note: Optional[str] = Field(None, max_length=200)