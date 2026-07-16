from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, service
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital Management API")

@app.post("/clinics", response_model=schemas.ClinicDetailResponse, status_code=status.HTTP_201_CREATED)
def create_clinic(clinic: schemas.ClinicCreate, db: Session = Depends(get_db)):
    return service.create_clinic(db=db, clinic_data=clinic)

@app.get("/clinics/{clinic_id}", response_model=schemas.ClinicDetailResponse)
def get_clinic(clinic_id: int, db: Session = Depends(get_db)):
    db_clinic = service.get_clinic_detail(db, clinic_id=clinic_id)
    if db_clinic is None:
        raise HTTPException(status_code=404, detail="Phòng khám không tồn tại")
    return db_clinic

@app.patch("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def update_doctor(doctor_id: int, doctor_data: schemas.DoctorUpdate, db: Session = Depends(get_db)):
    db_doctor = service.update_doctor(db, doctor_id=doctor_id, doctor_data=doctor_data)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Bác sĩ không tồn tại")
    return db_doctor

@app.delete("/licenses/{license_id}")
def delete_license(license_id: int, db: Session = Depends(get_db)):
    success = service.delete_license(db, license_id=license_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chứng chỉ không tồn tại")
    return {"message": "Đã xóa vĩnh viễn chứng chỉ hành nghề"}