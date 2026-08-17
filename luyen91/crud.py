from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
import models, schemas

def get_vehicles(db: Session, brand: str = None, status: str = None, sort_by: str = None, order: str = "asc"):
    query = db.query(models.Vehicle)

    # Lọc (Filter)
    if brand:
        query = query.filter(models.Vehicle.brand.ilike(f"%{brand}%"))
    if status:
        query = query.filter(models.Vehicle.status == status)

    # Sắp xếp động (Dynamic Sorting)
    if sort_by in ["daily_rate", "production_year"]:
        sort_column = getattr(models.Vehicle, sort_by)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(asc(models.Vehicle.id)) # Mặc định

    return query.all()

def get_vehicle_by_id(db: Session, vehicle_id: str):
    return db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate):
    db_vehicle = models.Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, db_vehicle: models.Vehicle, vehicle_update: schemas.VehicleUpdate):
    update_data = vehicle_update.model_dump()
    for key, value in update_data.items():
        setattr(db_vehicle, key, value)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, db_vehicle: models.Vehicle):
    db.delete(db_vehicle)
    db.commit()