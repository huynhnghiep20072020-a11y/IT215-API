from sqlalchemy import Column, Integer,String,Float
from app.database import Base
class Student(Base):
    __tablename__ ="students"
    id =Column (Integer,primary_key=True,index=True)
    full_name= Column(String(255),nullable=False)
    email =Column (String(255),nullable=False)
    major =Column(String(100),nullable=False)
    gpa=Column(Float ,nullable=False)
    