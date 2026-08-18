# Phần 1. Phát hiện lỗi
# 1. Khối code gây ra lỗiLỗ hổng thứ nhất nằm ở hàm get_current_user khi sử dụng phương thức đọc token không xác thực:
#     try:
#         # LỖI 1: Không kiểm tra chữ ký và thời hạn của token
#         payload = jwt.get_unverified_claims(token)
#     except Exception:
# Lỗ hổng thứ hai nằm ở phần kiểm tra người dùng (cũng trong hàm get_current_user), khi code bỏ qua việc kiểm tra trạng thái hoạt động của tài khoản:
#     user = USERS.get(username)

#     if user is None:
#         raise HTTPException(...)
    
#     # LỖI 2: Thiếu logic kiểm tra if not user["is_active"]:
#     return user
# 2. Vì sao việc sử dụng get_unverified_claims() không an toàn?
# Không xác thực chữ ký (Signature Bypass): Hàm get_unverified_claims()
# chỉ đơn thuần giải mã phần payload của JWT (Base64 decode) mà không dùng SECRET_KEY
# để đối chiếu chữ ký mã hóa. Hacker có thể dễ dàng sửa trường sub (từ alice thành admin)
# rồi gửi lên server mà không cần biết khóa bí mật. Hệ thống vẫn sẽ chấp nhận payload giả mạo này.
# Bỏ qua thời hạn (Expiration Ignore): Vì không chạy qua quá trình xác thực (validate), 
# các claim chuẩn bị sẵn của JWT như exp (thời gian hết hạn), nbf (thời gian bắt đầu có hiệu lực)
# hoàn toàn bị bỏ qua. Một token bị lộ dù đã hết hạn từ lâu vẫn sẽ được hệ thống chấp nhận.
# 3. Mô tả các test caseTest CaseKịch bảnKết quả mong đợiKết quả thực tế (code cũ)1. Token hợp lệCấp token cho alice (hoạt động, chưa hết hạn). 
# Gọi GET /users/me.Trả về thông tin alice với HTTP 200 OKHTTP 200 OK2. Token hết hạnGọi GET /issue-token/alice?expired=true. Dùng token này gọi GET /users/me.Báo lỗi HTTP 401 UnauthorizedHTTP 200 OK 
# (Do không check exp)3. Tài khoản bị khóaCấp token cho bob (is_active: False). Gọi GET /users/me.Báo lỗi HTTP 403 ForbiddenHTTP 200 OK (Do không check is_active)

from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError # Khai báo thêm JWTError

app = FastAPI()

SECRET_KEY = "training-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

USERS = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Nguyen",
        "role": "user",
        "is_active": True,
    },
    "bob": {
        "username": "bob",
        "full_name": "Bob Tran",
        "role": "user",
        "is_active": False,
    },
}

@app.get("/issue-token/{username}")
def issue_token(username: str, expired: bool = False):
    if username not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=-5 if expired else 30
    )

    token = jwt.encode(
        {
            "sub": username,
            "exp": expires_at,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


def get_current_user(token: str = Depends(oauth2_scheme)):
    # Định nghĩa sẵn Exception trả về 401
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # SỬA LỖI 1: Dùng jwt.decode để tự động kiểm tra chữ ký và 'exp'
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Kiểm tra token có chứa trường 'sub' không
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        # JWTError sẽ bao gồm ExpiredSignatureError (hết hạn) 
        # và JWTClaimsError (sai chữ ký, cấu trúc)
        raise credentials_exception

    # Kiểm tra người dùng có tồn tại trong hệ thống không
    user = USERS.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
        
    # SỬA LỖI 2: Chặn tài khoản không hoạt động (bị khóa)
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


@app.get("/users/me")
def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user