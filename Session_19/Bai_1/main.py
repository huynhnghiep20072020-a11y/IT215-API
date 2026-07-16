from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, service
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/warehouses", response_model=schemas.WarehouseDetailResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse(warehouse: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    return service.create_warehouse(db=db, warehouse=warehouse)

@app.get("/warehouses/{warehouse_id}", response_model=schemas.WarehouseDetailResponse)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    db_warehouse = service.get_warehouse_detail(db, warehouse_id=warehouse_id)
    if db_warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return db_warehouse

@app.patch("/packages/{package_id}", response_model=schemas.PackageResponse)
def update_package(package_id: int, package_data: schemas.PackageUpdate, db: Session = Depends(get_db)):
    db_package = service.update_package(db, package_id=package_id, package_data=package_data)
    if db_package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return db_package

@app.delete("/waybills/{waybill_id}")
def delete_waybill(waybill_id: int, db: Session = Depends(get_db)):
    success = service.delete_waybill(db, waybill_id=waybill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Waybill not found")
    return {"message": "Waybill deleted successfully"}