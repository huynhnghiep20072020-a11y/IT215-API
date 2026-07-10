from pydantic import BaseModel

class StudentBase(BaseModel):
    full_name:str
    email:str
    major:str
    gpa:float
    
class StudentCreate(StudentBase):
    pass
class StudentUpdate(StudentBase):
    pass
class StudentResponse(StudentBase):
    id:int
    
    class config:
        from_attributes=True
        