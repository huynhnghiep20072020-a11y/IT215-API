from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session 
from app.database import get_db 
from app.schemas.product import ProductCreate,ProductUpdate, ProductResponse
from app.services import product as product_service 

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", reponse_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return product_service.get_products(db)
@router.get("/{product_id}",response_model=ProductResponse)
def get_prodcut(product_id: int ,db:Session =Depends(get_db)):
    db_product =product_service.get_product(db,product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="product not found")
    return db_product\
@router.post("", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, product)  
@router.put("/{product_id}", response_model=ProductResponse)    
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = product_service.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product_service.update_product(db, db_product, product)
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = product_service.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product_service.delete_product(db, db_product)
    return None