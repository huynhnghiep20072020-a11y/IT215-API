from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import models
import schemas

def create_student(db: Session, student: schemas.StudentCreate):
    existing_student = db.query(models.Student).filter(
        (models.Student.student_code == student.student_code) |
        (models.Student.email == student.email)
    ).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Mã sinh viên hoặc Email đã tồn tại.")
    
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_students(db: Session):
    return db.query(models.Student).all()

def create_workshop(db: Session, workshop: schemas.WorkshopCreate):
    db_workshop = models.Workshop(**workshop.model_dump())
    db.add(db_workshop)
    db.commit()
    db.refresh(db_workshop)
    return db_workshop

def get_workshops(db: Session):
    return db.query(models.Workshop).all()

def get_workshop_by_id(db: Session, workshop_id: int):
    workshop = db.query(models.Workshop).filter(models.Workshop.id == workshop_id).first()
    if not workshop:
        raise HTTPException(status_code=404, detail="Không tìm thấy workshop.")
    return workshop

def register_workshop(db: Session, reg: schemas.RegistrationCreate):
    student = db.query(models.Student).filter(models.Student.id == reg.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên.")
    if student.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Sinh viên đang bị khóa, không thể đăng ký.")

    workshop = db.query(models.Workshop).filter(models.Workshop.id == reg.workshop_id).first()
    if not workshop:
        raise HTTPException(status_code=404, detail="Không tìm thấy workshop.")
    if workshop.status != "OPEN":
        raise HTTPException(status_code=400, detail="Workshop hiện không mở đăng ký.")
    if workshop.start_time <= datetime.now():
        raise HTTPException(status_code=400, detail="Workshop đã bắt đầu hoặc kết thúc.")

    existing_reg = db.query(models.Registration).filter(
        models.Registration.student_id == reg.student_id,
        models.Registration.workshop_id == reg.workshop_id,
        models.Registration.status == "REGISTERED"
    ).first()
    if existing_reg:
        raise HTTPException(status_code=400, detail="Sinh viên đã đăng ký workshop này.")

    current_count = db.query(models.Registration).filter(
        models.Registration.workshop_id == reg.workshop_id,
        models.Registration.status == "REGISTERED"
    ).count()
    if current_count >= workshop.maximum_participants:
        raise HTTPException(status_code=400, detail="Workshop đã đạt giới hạn số lượng đăng ký.")

    new_reg = models.Registration(student_id=reg.student_id, workshop_id=reg.workshop_id)
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return new_reg

def get_student_workshops(db: Session, student_id: int):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên.")
    return student

def get_workshop_students(db: Session, workshop_id: int):
    workshop = db.query(models.Workshop).filter(models.Workshop.id == workshop_id).first()
    if not workshop:
        raise HTTPException(status_code=404, detail="Không tìm thấy workshop.")
    return workshop

def cancel_registration(db: Session, reg_id: int):
    reg = db.query(models.Registration).filter(models.Registration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đăng ký.")
    if reg.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Đăng ký này đã bị hủy từ trước.")
    
    reg.status = "CANCELLED"
    db.commit()
    db.refresh(reg)
    return reg