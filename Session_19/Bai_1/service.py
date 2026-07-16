from sqlalchemy.orm import Session
from . import models, schemas

def create_warehouse(db: Session, warehouse: schemas.WarehouseCreate):
    try:
        db_warehouse = models.Warehouse(**warehouse.model_dump())
        db.add(db_warehouse)
        db.commit()
        db.refresh(db_warehouse)
        return db_warehouse
    except Exception as e:
        db.rollback()
        raise e

def get_warehouse_detail(db: Session, warehouse_id: int):
    return db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()

def update_package(db: Session, package_id: int, package_data: schemas.PackageUpdate):
    db_package = db.query(models.Package).filter(models.Package.id == package_id).first()
    if not db_package:
        return None
    
    try:
        update_data = package_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_package, key, value)
        
        db.commit()
        db.refresh(db_package)
        return db_package
    except Exception as e:
        db.rollback()
        raise e

def delete_waybill(db: Session, waybill_id: int):
    db_waybill = db.query(models.Waybill).filter(models.Waybill.id == waybill_id).first()
    if not db_waybill:
        return False
    
    try:
        db.delete(db_waybill)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e