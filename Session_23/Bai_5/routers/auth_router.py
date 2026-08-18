from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.security import create_access_token
from dependencies.auth_deps import get_current_user
from models.mock_db import users_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is locked")
        
    access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_current_user(current_user: dict = Depends(get_current_user)):
    # Ẩn password trước khi trả về
    return {"id": current_user["id"], "username": current_user["username"], "role": current_user["role"]}