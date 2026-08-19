# Phần 1: Phát hiện lỗi và Test case
# 1. Các đoạn code chưa đúng trong hệ thống hiện tại:

# if full_name == "":: Chỉ kiểm tra chuỗi rỗng tuyệt đối, bỏ qua trường hợp người dùng nhập toàn dấu cách (khoảng trắng).

# Thiếu kiểm tra Email: Code hiện tại hoàn toàn không có logic kiểm tra biến email có chứa ký tự @ hay không.

# if len(phone) < 10:: Chỉ kiểm tra độ dài nhỏ hơn 10. Nếu người dùng nhập "09876abcde" (độ dài 10, chứa chữ cái) hoặc "12345678901" (độ dài 11), hệ thống vẫn cho qua.

# Thiếu kiểm tra loại file (MIME type): Hệ thống không kiểm tra avatar.content_type, dẫn đến việc có thể tải lên file PDF, EXE, Script độc hại.

# Thiếu kiểm tra dung lượng: File được đọc thẳng vào RAM và lưu xuống ổ cứng mà không quan tâm kích thước là bao nhiêu.

# file_path = UPLOAD_DIR / avatar.filename: Sử dụng trực tiếp filename từ client gửi lên. Nếu hai người dùng tải lên file cùng tên, file cũ sẽ bị ghi đè. Kẻ gian cũng có thể lợi dụng điều này để thực hiện tấn công Path Traversal.

# Xử lý HTTP Status chưa chuẩn: Khi có lỗi xảy ra, hệ thống vẫn trả về HTTP 200 OK kèm "success": False. Theo chuẩn RESTful, cần phải trả về mã HTTP tương ứng như 400 (Bad Request) hoặc 413 (Payload Too Large).

# 2. Các Test case cụ thể:

# Test case 1: Họ tên chỉ chứa khoảng trắng

# Dữ liệu đầu vào: full_name = "   "

# Kết quả hiện tại: Đăng ký thành công (HTTP 200 OK).

# Kết quả mong đợi: Báo lỗi HTTP 400 Bad Request.

# Nguyên nhân sai: Biểu thức "   " == "" trả về False, nên logic chặn lỗi bị bỏ qua.

# Test case 2: Email không đúng định dạng

# Dữ liệu đầu vào: email = "nguyenvana.gmail.com"

# Kết quả hiện tại: Đăng ký thành công (HTTP 200 OK).

# Kết quả mong đợi: Báo lỗi HTTP 400 Bad Request.

# Nguyên nhân sai: Code chưa có bất kỳ dòng nào kiểm tra chuỗi email.

# Test case 3: Số điện thoại chứa chữ cái

# Dữ liệu đầu vào: phone = "09876abcde"

# Kết quả hiện tại: Đăng ký thành công (HTTP 200 OK).

# Kết quả mong đợi: Báo lỗi HTTP 400 Bad Request.

# Nguyên nhân sai: Code chỉ kiểm tra len(phone) < 10, trong khi chuỗi trên có độ dài bằng 10 nhưng lại chứa các ký tự không phải số.

# Test case 4: Upload tài liệu không phải ảnh

# Dữ liệu đầu vào: avatar = "student-profile.pdf" (MIME type: application/pdf).

# Kết quả hiện tại: Đăng ký thành công, file PDF được lưu vào thư mục uploads/.

# Kết quả mong đợi: Báo lỗi HTTP 400 Bad Request.

# Nguyên nhân sai: API không kiểm tra thuộc tính content_type của đối tượng UploadFile.

# Test case 5: Upload ảnh vượt quá 2MB

# Dữ liệu đầu vào: avatar = "high_res_photo.jpg" (Kích thước: 5 MB).

# Kết quả hiện tại: Đăng ký thành công, toàn bộ 5 MB được ghi xuống ổ cứng.

# Kết quả mong đợi: Báo lỗi HTTP 413 Payload Too Large.

# Nguyên nhân sai: Code dùng hàm avatar.read() đọc toàn bộ file mà không kiểm tra độ lớn của biến content sau khi đọc xong.

# Test case 6: Trùng tên file (Ghi đè dữ liệu)

# Dữ liệu đầu vào: Sinh viên A upload avatar.jpg. Tiếp theo sinh viên B cũng upload file có tên avatar.jpg.

# Kết quả hiện tại: File của sinh viên B lưu thành công và ghi đè (xóa mất) file của sinh viên A.

# Kết quả mong đợi: Cả hai file đều tồn tại dưới ổ cứng với 2 tên khác nhau.

# Nguyên nhân sai: Code nối trực tiếp thư mục lưu với thuộc tính avatar.filename do trình duyệt gửi lên.



import uuid
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_COURSES = [
    "Python Basic",
    "FastAPI",
    "Data Analysis",
]

# Giới hạn kích thước file: 2MB
MAX_FILE_SIZE = 2 * 1024 * 1024

# Định dạng được phép
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]

@app.post("/students/register")
async def register_student(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    course: str = Form(...),
    avatar: UploadFile = File(...),
):
    # 1. Kiểm tra Họ và tên (Dùng strip để loại bỏ khoảng trắng thừa)
    if full_name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full name is required and cannot be just spaces."
        )

    # 2. Kiểm tra Email cơ bản
    if "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address."
        )

    # 3. Kiểm tra số điện thoại (Chỉ chứa số và đúng 10 ký tự)
    if not phone.isdigit() or len(phone) != 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be exactly 10 digits."
        )

    # 4. Kiểm tra Khóa học
    if course not in ALLOWED_COURSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is not available."
        )

    # 5. Kiểm tra định dạng ảnh (Chỉ chấp nhận JPG, PNG)
    if avatar.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPG and PNG are allowed."
        )

    # Đọc dữ liệu file vào memory
    content = await avatar.read()

    # 6. Kiểm tra dung lượng file (Không vượt quá 2MB)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 2MB limit."
        )

    # 7. Tạo tên file mới để chống ghi đè và lỗi bảo mật Path Traversal
    # Lấy phần mở rộng của file cũ (vd: .jpg)
    file_extension = Path(avatar.filename).suffix 
    if not file_extension:
        # Dự phòng nếu file không có đuôi, dựa vào content_type
        file_extension = ".jpg" if avatar.content_type == "image/jpeg" else ".png"
        
    new_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / new_filename

    # Chỗ này an toàn để lưu file vì tất cả các điều kiện đã thỏa mãn
    with open(file_path, "wb") as file:
        file.write(content)

    return {
        "success": True,
        "message": "Registration successful",
        "data": {
            "full_name": full_name.strip(),
            "email": email.strip(),
            "phone": phone,
            "course": course,
            "avatar": str(file_path),
        },
    }