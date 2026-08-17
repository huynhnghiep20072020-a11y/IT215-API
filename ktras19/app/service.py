from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
import math
from app import models, schemas

def create_clinic(db: Session, clinic_data: schemas.ClinicCreate) -> models.Clinic:
    try:
        new_clinic = models.Clinic(**clinic_data.model_dump())
        db.add(new_clinic)
        db.commit()
        db.refresh(new_clinic)
        return new_clinic
    except Exception as e:
        db.rollback()
        raise e

def get_clinic_by_id(db: Session, clinic_id: int) -> Optional[models.Clinic]:
    return db.query(models.Clinic).filter(models.Clinic.id == clinic_id).first()

def get_clinics(db: Session, page: int, limit: int, search: Optional[str] = None) -> Tuple[int, int, List[models.Clinic]]:
    query = db.query(models.Clinic)
    if search:
        query = query.filter(models.Clinic.clinic_name.ilike(f"%{search}%"))
    
    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit
    
    data = query.offset(offset).limit(limit).all()
    return total, pages, data

def create_doctor(db: Session, doctor_data: schemas.DoctorCreate) -> models.Doctor:
    try:
        new_doctor = models.Doctor(**doctor_data.model_dump())
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)
        return new_doctor
    except Exception as e:
        db.rollback()
        raise e

def get_doctor_by_id(db: Session, doctor_id: int) -> Optional[models.Doctor]:
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def get_doctors_by_clinic(db: Session, clinic_id: int) -> List[models.Doctor]:
    return db.query(models.Doctor).filter(models.Doctor.clinic_id == clinic_id).all()

def update_doctor(db: Session, doctor_id: int, doctor_update: schemas.DoctorUpdate) -> Optional[models.Doctor]:
    try:
        doctor = get_doctor_by_id(db, doctor_id)
        if not doctor:
            return None
        
        update_data = doctor_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(doctor, key, value)
            
        db.commit()
        db.refresh(doctor)
        return doctor
    except Exception as e:
        db.rollback()
        raise e

def delete_license(db: Session, license_id: int) -> bool:
    try:
        license_obj = db.query(models.License).filter(models.License.id == license_id).first()
        if not license_obj:
            return False
            
        db.delete(license_obj)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e