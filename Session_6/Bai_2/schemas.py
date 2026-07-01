from pydantic import BaseModel, Field, EmailStr

class StudentBase(BaseModel):
    code: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    email: EmailStr
    age: int = Field(..., gt=0)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass