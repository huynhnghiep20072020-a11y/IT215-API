from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/school_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model
class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hàm Service
def delete_student_service(db: Session, student_id: int):
    # 1. Tìm học viên theo student_id
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    
    # 2. Nếu không tìm thấy, trả về lỗi 404
    if student is None:
        raise HTTPException(status_code=404, detail="Học viên không tồn tại trong hệ thống")
    
    # 3. Lưu lại thông tin cần trả về trước khi xóa object
    deleted_data = {
        "id": student.id,
        "full_name": student.full_name,
        "email": student.email
    }
    
    # 4. Gọi db.delete() và db.commit()
    db.delete(student)
    db.commit()
    
    # 5. Trả về thông tin học viên đã xóa
    return deleted_data

# API
@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    deleted_student = delete_student_service(db, student_id)
    return {
        "message": "Xóa học viên thành công",
        "data": deleted_student
    }
    
    
    """Phần 1: Phân tích & Đề xuất đa giải pháp1. 
    Phân tích yêu cầu Input / OutputInput: Tham số student_id dạng integer được truyền vào qua URL của API
    (DELETE /students/{student_id}).Output thành công: Mã trạng thái 200 OK 
    kèm theo JSON chứa thông báo thành công và thông tin học viên vừa bị xóa.JSON{
  "message": "Xóa học viên thành công",
  "data": {
    "id": 1,
    "full_name": "Nguyen Van A",
    "email": "vana@gmail.com"
  }
}
Output thất bại: Mã trạng thái 404 Not Found kèm theo JSON báo lỗi nếu không tìm thấy student_id.JSON{
  "detail": "Học viên không tồn tại trong hệ thống"
}
2. Đưa ra tối thiểu 2 giải phápGiải pháp 1: 
Lấy bản ghi rồi mới xóa (Query & Delete bằng ORM Object).Sử dụng .first() để truy vấn lấy object Student từ database. 
Kiểm tra xem object có tồn tại không. Nếu có, tiến hành sao chép thông tin cần thiết, sau đó gọi db.delete(student) 
và db.commit().Giải pháp 2: Xóa trực tiếp bằng Query (Bulk Delete).Sử dụng lệnh db.query(Student).filter(...).delete().
Lệnh này trả về số lượng bản ghi bị ảnh hưởng (rowcount). Nếu rowcount == 0 thì báo lỗi 404, nếu rowcount > 0 thì gọi db.commit().
Phần 2: So sánh & Lựa chọn1. Lập bảng so sánh các giải phápTiêu chíGiải pháp 1: Query & Delete (Lấy object rồi xóa)Giải pháp 2: Bulk Delete (Xóa trực tiếp bằng query)
Độ dễ hiểuRất trực quan và dễ hiểu với ORM (Tìm -> Thấy -> Xóa).Cần hiểu về cách SQLAlchemy thực thi query xóa và trả về rowcount.Số lượng code cần viếtNhiều hơn
(cần 2 thao tác riêng biệt: truy vấn SELECT và thực thi DELETE).Ít hơn (gộp việc tìm và xóa vào 1 câu lệnh thực thi duy nhất).Khả năng kiểm soát lỗiDễ dàng kiểm soát object và dữ liệu trả về trước khi xóa.Có thể kiểm soát được (nhờ rowcount),
nhưng không trích xuất được object đã xóa.Có kiểm tra học viên tồn tại không?Có (thông qua if student is None:).Có (thông qua if affected_rows == 0:).Mức độ phù hợp với SQLAlchemy ORMPhù hợp nhất với nguyên lý ORM (thao tác trên object).
Thường dùng cho xóa hàng loạt (Bulk operation).Khả năng tách logic vào ServiceRất tốt. Dễ dàng mock object trong quá trình viết Unit Test.Tốt, nhưng khó mở rộng nếu nghiệp vụ cần ghi log dữ liệu trước khi xóa.2. Chốt lựa chọn giải pháp phù hợp
Giải pháp được chọn: Giải pháp 1 (Lấy bản ghi rồi mới xóa).Lý do: Yêu cầu bài toán đòi hỏi phải trả về thông tin học viên đã bị xóa (gồm id, full_name, email). Giải pháp 2 chỉ trả về số lượng row bị xóa, dẫn đến việc không thể đáp ứng định dạng 
Output thành công nếu không thực hiện một câu lệnh SELECT trước đó. Vì vậy, Giải pháp 1 là bắt buộc và tối ưu nhất để giải quyết triệt để yêu cầu này."""

