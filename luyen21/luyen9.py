# from database import Base 
# from sqlalchemy.orm import Mapped ,mapped_colum
#  class Employee(Base):
#      __tablename__="employee "
#      id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#      name: Mapped[str] = mapped_column(String(100))
#      email: Mapped[str] = mapped_column(String(100), unique=True)
#      salary: Mapped[float] = mapped_column(Float)
     
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base 
  
def create_employee_service(db, employee_data):
    employee = Employee(**employee_data)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee
    pass 