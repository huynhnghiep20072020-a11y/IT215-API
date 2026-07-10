from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate,ProductUpdate
from luyen91.app.schemas import product

def get_products(db:Session):
    return db.query(Product).all()

def get_product(db:Session,product_id:int):
    return db.query(Product).filter(Product.id ==product_id).first()
def create_product(db: Session,product:ProductCreate):
    db_product = Product(name=product.name,price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, db_product: Product,product_update:ProductUpdate):
    db_product.name = product_update.name
    db_product.price = product_update.price
    db.commit()
    db.refresh(db_product)
    return db_product
def delete_product(db:Session ,db_product:product):
    db.delete(db_product)
    db.commit()
    