from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/learning_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_url = Column(String(500), nullable=False)

class DocumentCreate(BaseModel):
    title: str
    subject: str
    document_type: str
    file_url: str

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    return db.query(DocumentModel).all()

@app.post("/documents")
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    new_doc = DocumentModel(
        title=doc.title,
        subject=doc.subject,
        document_type=doc.document_type,
        file_url=doc.file_url
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@app.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
        
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}

"""
Giải thích ngắn gọn:
1. Định nghĩa `DocumentModel` để ánh xạ với bảng `documents` trong MySQL và `DocumentCreate` (Pydantic schema) để nhận dữ liệu an toàn từ body request.
2. API GET `/documents`: Sử dụng `db.query(DocumentModel).all()` để truy vấn và trả về toàn bộ danh sách tài liệu.
3. API POST `/documents`: Nhận dữ liệu đã qua schema, tạo object model mới, dùng `db.add()`, `db.commit()` để lưu và `db.refresh()` để trả về object hoàn chỉnh (có ID tự tăng).
4. API DELETE `/documents/{document_id}`: Tìm bản ghi bằng `.first()`. Nếu bằng None thì raise lỗi 404. Nếu tồn tại thì tiến hành `db.delete()` và `db.commit()`.
"""