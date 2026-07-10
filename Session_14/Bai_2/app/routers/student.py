from fastapi import APIRouter ,Depends,HTTPException ,status 
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.student import StudentCreate,StudentUpdate,StudentResponse
from app.services import student as student_service

router = APIRouter(prefix ="/student",tags=["Studnets"])

@router.get("",response_model=list[StudentResponse])
def get_studnets(db:Session =Depends(get_db)):
    return student_service.get_studnets(db)
@router.get("/{studnet_id}",response_model=StudentResponse)
def get_student(studnet_id:int ,db:Session=Depends(get_db)):
    db_student = studnet_service.get_student(db,student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="studnet not found")
    return db_student

@router.post("",response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate,db:Session=Depends(get_db)):
    return student_service.create_student(db,student)

@router.put("/{studnet_id}",response_model=StudentResponse)
def update_student(student_id:int,student:StudentUpdate,db:Session =Depends(get_db)):
    db_student =student_service.get_student(db,student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student_service.update_student(db,db_student,student)

@router.delete("/{student_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id:int,db:Session=Depends(getdb)):
    db_student =student_service.get_student(db,student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Student not found")
    student_service.delete_student(db,db_student)
    return None
