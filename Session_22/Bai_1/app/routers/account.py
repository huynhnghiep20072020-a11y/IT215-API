from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, models, exceptions
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/account", tags=["Account"])

@router.get("/balance")
def get_balance(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Xin chào {current_user.username}", "balance": current_user.balance}

@router.post("/transfer")
def transfer(request: schemas.TransferRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.username == request.to_username:
        raise exceptions.AppException(400, "INVALID_TRANSFER", "Không thể tự chuyển tiền cho chính mình")
    

    sender = db.query(models.User).filter(models.User.id == current_user.id).with_for_update().first()
    recipient = db.query(models.User).filter(models.User.username == request.to_username).with_for_update().first()
    
    if not recipient:
        raise exceptions.AppException(404, "RECIPIENT_NOT_FOUND", "Không tìm thấy tài khoản người nhận")
    
    if sender.balance < request.amount:
        raise exceptions.AppException(400, "INSUFFICIENT_BALANCE", "Số dư không đủ")
    
    sender.balance -= request.amount
    recipient.balance += request.amount
    db.commit()
    
    return {"message": "Chuyển tiền thành công", "amount": request.amount, "to": recipient.username, "note": request.note}