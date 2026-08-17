from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    users = db.query(models.User).all()
    return users