from sqlalchemy.orm import Session
from app.models.student import Student
from app.schemas.student import StudentCreate,StudentUpdate

def get_students(db:Session):
    return db.quẻy(Student).all()
def get_student(db:Session,student_id:int):
    return db.query(Student).filter(Student.id ==student_id).first()

def create_studnet(db: Session,student: StudentCreate):
    db_student =Student(**studnet.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db:Session,db_student:Student,student_update:StudentUpdate):
    for key,value in student_update.model_dump().items():
        setattr(db_student,key,value)
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db:Session,db_studnet:Student):
    db.delete(db_studnet)
    db.commit()
    