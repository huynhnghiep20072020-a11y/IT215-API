import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Giả sử đã import các schema và db config: LoginRequest, User, get_db

router = APIRouter()

# Cấu hình bảo mật (Thực tế nên lấy từ file .env)
SECRET_KEY = os.getenv("SECRET_KEY", "chuoi_bi_mat_cuc_ky_dai_va_phuc_tap_khong_luu_trong_code")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # 1. Tìm người dùng theo email
    user = db.query(User).filter(User.email == data.email).first()

    # 2. Xác thực gộp (Tránh lỗi User Enumeration)
    # Cần đảm bảo user.password trong DB đã được băm (hashed) từ trước
    if not user or not bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Tạo Payload an toàn (Không chứa mật khẩu, có thời gian hết hạn)
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": user.email,      # Thông tin định danh (Subject)
        "role": user.role,      # Quyền hạn để dùng cho phân quyền sau này
        "exp": expire_time      # Thời hạn của Token
    }

    # 4. Ký JWT bằng thuật toán và khóa bảo mật
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # 5. Trả về Response theo chuẩn OAuth2
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    
    # Bảng phân tích 6 vấn đề bảo mật và thiết kế
    # Vấn đề Nguy cơ Cách khắc phục
    # 1. So sánh mật khẩu trực tiếp (!=)Lộ mật khẩu gốc. Hệ thống đang lưu mật khẩu ở dạng văn bản thuần túy (plaintext).
    # Nếu DB bị hack, toàn bộ mật khẩu người dùng sẽ rơi vào tay kẻ gian.Sử dụng thuật toán băm (như Bcrypt) để băm mật khẩu trước khi lưu.
    # Khi đăng nhập, dùng hàm đối chiếu hash (vd: bcrypt.checkpw).
    # 2. Thông báo lỗi quá chi tiếtLỗi User Enumeration (Liệt kê người dùng).
    # Việc tách biệt lỗi "Email không tồn tại" và "Sai mật khẩu" giúp hacker dễ dàng dò quét xem email nào đã đăng ký tài khoản trên hệ thống.
    # Gộp chung thông báo lỗi thành: "Email hoặc mật khẩu không chính xác".
    # 3. Đưa mật khẩu vào JWT PayloadLộ thông tin nhạy cảm. JWT chỉ được mã hóa Base64Url,
    # bất kỳ ai bắt được token đều có thể dễ dàng giải mã và nhìn thấy mật khẩu gốc nằm bên trong.
    # Tuyệt đối không đưa mật khẩu vào Payload. Chỉ đưa các thông tin định danh cần thiết như user_id, email, và role.
    # 4. Hardcode Secret Key yếu ("123456")Bị giả mạo Token. Secret Key quá yếu và nằm lộ trong code giúp hacker dễ dàng bẻ khóa chữ ký,
    # từ đó tự tạo token giả mạo quyền Admin để tấn công hệ thống.Tạo một chuỗi Secret Key dài, phức tạp và lưu trữ an toàn trong biến môi trường (.env), 
    # không đưa lên Git.
    # 5. Token không có thời gian hết hạn (exp)Mất kiểm soát phiên đăng nhập.
    # Token này có hiệu lực vĩnh viễn. Nếu hacker đánh cắp được token, chúng sẽ có quyền truy cập hệ thống mãi mãi.
    # Thêm trường exp vào Payload của JWT, giới hạn thời gian sống của token (ví dụ: 30 phút hoặc 1 giờ).
    # 6. Trả về status 200 OK khi lỗiSai chuẩn thiết kế RESTful API. 
    # Trả về {"success": False} với HTTP Status 200 làm cho các ứng dụng Client (Web/App) khó xử lý lỗi xác thực tự động (như interceptors).
    # Ném ra ngoại lệ HTTPException với mã lỗi 401 Unauthorized khi xác thực thất bại.
    
# Giải thích luồng xử lý đăng nhập an toàn
# Sau khi sửa lại, quá trình đăng nhập sẽ diễn ra qua 5 bước bảo mật sau:

# Truy vấn Dữ liệu: Khi người dùng gửi request chứa email và password, hệ thống gọi xuống Database để tìm kiếm bản ghi khớp với email. Nếu không tìm thấy, biến user sẽ mang giá trị None.

# Kiểm tra Xác thực Mù (Blind Validation): Hệ thống gộp chung điều kiện kiểm tra: Nếu không có user HOẶC nếu mật khẩu băm không khớp mật khẩu nhập vào. Việc dùng chung một thông báo lỗi duy nhất ("Email hoặc mật khẩu không chính xác") cùng mã HTTP 401 đảm bảo kẻ tấn công không thể phân biệt được là do email sai hay do mật khẩu sai.

# Chuẩn bị Dữ liệu Token (Payload): Khi xác thực thành công, hệ thống tính toán thời điểm hết hạn exp (thời điểm hiện tại + 30 phút). Token chỉ đóng gói các thông tin cần thiết nhất (sub làm định danh, role để phân quyền) và tuyệt đối loại bỏ password ra khỏi quy trình.

# Ký điện tử (Signature): Hệ thống sử dụng thuật toán mã hóa đối xứng (HS256) và một Khóa bí mật (SECRET_KEY được bảo vệ độc lập với mã nguồn) để ký Token. Bước này khóa cứng Payload, bất kỳ ai sửa đổi dù chỉ một ký tự trong Token cũng sẽ làm chữ ký này mất giá trị.

# Trả về Client: Hệ thống trả về một cấu trúc JSON đúng chuẩn OAuth2 với access_token và token_type là "bearer". Client (Frontend/Mobile) sẽ lưu trữ Token này và đính kèm vào Header trong các yêu cầu gọi API tiếp theo để chứng minh danh tính.