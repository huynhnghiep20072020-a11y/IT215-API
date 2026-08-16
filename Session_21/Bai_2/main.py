import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "day_la_khoa_bi_mat_rat_an_toan_cua_ban"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: int = 30) -> str:
    """Tạo JWT access token với thời gian hết hạn."""

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    
  
    to_encode.update({"exp": expire})
    
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Giải mã JWT và kiểm tra tính hợp lệ/thời gian hết hạn."""
    try:
        
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
        
    except jwt.ExpiredSignatureError:
        raise ValueError("Token đã hết hạn. Vui lòng đăng nhập lại.")
    except jwt.InvalidTokenError:
        raise ValueError("Token không hợp lệ hoặc đã bị thay đổi.")

if __name__ == "__main__":
  
    payload_data = {
        "sub": "student01@gmail.com",
        "user_id": 1,
        "role": "student"
    }

  
    print("--- TẠO TOKEN ---")
    token = create_access_token(data=payload_data, expires_minutes=30)
    print(f"Token: {token}\n")

  
    print("--- GIẢI MÃ TOKEN ---")
    try:
        decoded_payload = decode_access_token(token)
        print("Kết quả giải mã hợp lệ:")
        print(decoded_payload)
    except Exception as e:
        print(f"Lỗi: {e}")
        
# Ba phần của JWT là gì?
# Một chuỗi JWT (được phân cách bởi 2 dấu chấm .) bao gồm ba phần:

# Header: Chứa thông tin về loại token (typ: JWT) và thuật toán mã hóa (alg: HS256).

# Payload: Chứa các dữ liệu cần truyền tải (claims) như thông tin người dùng (user_id, role) và thời gian hết hạn (exp).

# Signature (Chữ ký): Được tạo ra bằng cách kết hợp Header, Payload và khóa bí mật (SECRET_KEY) thông qua thuật toán được chỉ định để đảm bảo tính toàn vẹn.

# Payload của JWT có được mã hóa để che giấu dữ liệu hay không?
# Không. Header và Payload của JWT chỉ được mã hóa theo chuẩn Base64Url để an toàn khi truyền qua URL hoặc HTTP Headers. 
# Bất kỳ ai có được chuỗi JWT đều có thể dễ dàng giải mã Base64 (bằng các công cụ như jwt.io) để đọc được toàn bộ nội dung bên trong Payload.
# Đó là lý do tuyệt đối không được đưa thông tin nhạy cảm (mật khẩu, mã thẻ tín dụng, private key) vào JWT.

# Signature có vai trò gì?
# Signature có vai trò đảm bảo tính toàn vẹn (Integrity) và tính xác thực (Authenticity) của token. Khi server nhận được JWT từ người dùng, nó sẽ dùng SECRET_KEY (chỉ server mới biết) 
# để tính toán lại chữ ký từ Header và Payload của token. Nếu chữ ký server tự tính khớp với chữ ký đính kèm trên token, 
# chứng tỏ dữ liệu không bị sửa đổi trên đường truyền và token này thực sự do hệ thống của bạn phát hành.

# Điều gì xảy ra nếu người dùng tự sửa trường role trong Payload?
# Giả sử người dùng lấy token, giải mã Base64, đổi trường "role": "student" thành "role": "admin", sau đó mã hóa Base64 lại và gửi lên server.
# Lúc này, server sẽ báo lỗi (InvalidTokenError). Lý do là vì Payload đã bị thay đổi, nhưng người dùng không biết SECRET_KEY nên không thể tạo ra được phần Signature mới tương ứng.
# Khi server kiểm tra, chữ ký đi kèm token sẽ không khớp với Payload đã bị sửa, và token lập tức bị từ chối.