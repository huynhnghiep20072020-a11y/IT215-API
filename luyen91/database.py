from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Thay đổi thông tin đăng nhập MySQL của bạn tại đây
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/vehicle_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency để quản lý vòng đời (Lifecycle) của Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()