# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy import create_engine, text, Column, Integer, String
# from sqlalchemy.orm import sessionmaker, Session, declarative_base

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/cntt5_project"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# app = FastAPI(title="API Dự án ")
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
# @app.get("/users")
# def check_mysql_connection(db: Session = Depends(get_db)):
#     try:
#         # Gửi một câu lệnh SQL đơn giản để test
#         db.execute(text("SELECT 1"))
#         return {
#             "status": "Thành công!", 
#             "message": "Đã kết nối được với database cntt5_project trên MySQL."
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi kết nối: {str(e)}")
    
# # Khởi tạo class Base
# Base = declarative_base()

# # Tạo class User mô phỏng lại bảng 'users' trong MySQL
# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100))
#     email = Column(String(100))
# @app.get("/get-users")
# def get_all_users(db: Session = Depends(get_db)):
#     try:
#         # Lệnh này tương đương với SELECT * FROM users;
#         users = db.query(User).all()
        
#         return {
#             "status": "Thành công",
#             "total_users": len(users),
#             "data": users
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi truy vấn: {str(e)}")

