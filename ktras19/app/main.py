from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app import models, schemas, service
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinic Management API")

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Vi phạm ràng buộc dữ liệu (Trùng khóa duy nhất hoặc Khóa ngoại không hợp lệ)."}
    )

@app.post("/clinics", response_model=schemas.ClinicResponse, status_code=status.HTTP_201_CREATED)
def create_clinic(clinic: schemas.ClinicCreate, db: Session = Depends(get_db)):
    return service.create_clinic(db, clinic)

@app.get("/clinics", response_model=schemas.PaginatedClinicResponse)
def read_clinics(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    total, pages, data = service.get_clinics(db, page, limit, search)
    return {"total": total, "pages": pages, "data": data}

@app.get("/clinics/{clinic_id}", response_model=schemas.ClinicDetailResponse)
def read_clinic(clinic_id: int, db: Session = Depends(get_db)):
    clinic = service.get_clinic_by_id(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Không tìm thấy phòng khám")
    return clinic


@app.post("/doctors", response_model=schemas.DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    clinic = service.get_clinic_by_id(db, doctor.clinic_id)
    if not clinic:
        raise HTTPException(status_code=400, detail="Mã phòng khám (clinic_id) không tồn tại")

    return service.create_doctor(db, doctor)

@app.get("/doctors", response_model=List[schemas.DoctorResponse])
def read_doctors(clinic_id: Optional[int] = None, db: Session = Depends(get_db)):
    if clinic_id:
        return service.get_doctors_by_clinic(db, clinic_id)
    return db.query(models.Doctor).all()

@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = service.get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ")
    return doctor

@app.patch("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def update_doctor(doctor_id: int, doctor_update: schemas.DoctorUpdate, db: Session = Depends(get_db)):

    if doctor_update.clinic_id is not None:
        clinic = service.get_clinic_by_id(db, doctor_update.clinic_id)
        if not clinic:
            raise HTTPException(status_code=400, detail="Mã phòng khám (clinic_id) không tồn tại")

    updated_doctor = service.update_doctor(db, doctor_id, doctor_update)
    if not updated_doctor:
        raise HTTPException(status_code=404, detail="Không tìm thấy bác sĩ để cập nhật")
    
    return updated_doctor


@app.delete("/licenses/{license_id}")
def delete_license(license_id: int, db: Session = Depends(get_db)):
    success = service.delete_license(db, license_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy chứng chỉ để xóa")
    return {"message": "Deleted"}