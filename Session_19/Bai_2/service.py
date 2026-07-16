from sqlalchemy.orm import Session
from . import models, schemas

def create_clinic(db: Session, clinic_data: schemas.ClinicCreate):
    try:
        db_clinic = models.Clinic(**clinic_data.model_dump())
        db.add(db_clinic)
        db.commit()
        db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        db.rollback()
        raise e

def get_clinic_detail(db: Session, clinic_id: int):
    return db.query(models.Clinic).filter(models.Clinic.id == clinic_id).first()

def update_doctor(db: Session, doctor_id: int, doctor_data: schemas.DoctorUpdate):
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not db_doctor:
        return None
    
    try:
        # exclude_unset=True đảm bảo chỉ lấy những trường có gửi dữ liệu lên
        update_data = doctor_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_doctor, key, value)
        
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        db.rollback()
        raise e

def delete_license(db: Session, license_id: int):
    db_license = db.query(models.License).filter(models.License.id == license_id).first()
    if not db_license:
        return False
    
    try:
        db.delete(db_license)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e