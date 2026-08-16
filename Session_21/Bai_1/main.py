import bcrypt

def hash_password(password: str) -> str:
    """Băm mật khẩu gốc sử dụng Bcrypt và Salt."""

    password_bytes = password.encode('utf-8')
   
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào có khớp với mật khẩu đã băm hay không."""
 
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)

if __name__ == "__main__":
    password = "Rikkei@123"

    hashed_password = hash_password(password)
    print(f"Mật khẩu sau khi băm: {hashed_password}")

  
    print(f"Kiểm tra 'Rikkei@123': {verify_password('Rikkei@123', hashed_password)}")

   
    print(f"Kiểm tra 'Rikkei@456': {verify_password('Rikkei@456', hashed_password)}")
    
# Vì sao không nên lưu mật khẩu trực tiếp vào database?
# Lưu mật khẩu dưới dạng văn bản thuần túy (plain text) là một rủi ro bảo mật nghiêm trọng.
# Nếu cơ sở dữ liệu bị tấn công (qua SQL Injection, lộ file backup, hoặc do nội gián), hacker sẽ ngay lập tức có được toàn bộ mật khẩu của người dùng. 
# Vì hầu hết mọi người có thói quen sử dụng chung một mật khẩu cho nhiều dịch vụ (email, ngân hàng, mạng xã hội),
# việc lộ mật khẩu ở hệ thống của bạn có thể khiến người dùng bị chiếm đoạt tài khoản ở các hệ thống khác.

# Vì sao cùng một mật khẩu nhưng hai lần băm có thể tạo ra hai chuỗi hash khác nhau?
# Điều này xảy ra là do Salt (muối). Thuật toán Bcrypt (thông qua hàm bcrypt.gensalt()) sẽ tự động sinh ra một chuỗi ký tự ngẫu nhiên (gọi là salt) vào mỗi lần bạn yêu cầu băm mật khẩu.
# Khi đó, đầu vào của hàm băm không chỉ là mật khẩu, mà là mật khẩu + salt.
# Vì salt luôn thay đổi ngẫu nhiên trong mỗi lần gọi hàm, kết quả băm đầu ra sẽ hoàn toàn khác nhau dù mật khẩu gốc giống hệt nhau.
# (Lưu ý: Salt này sẽ được Bcrypt nối trực tiếp vào bên trong chuỗi hash sinh ra để dùng cho việc xác thực sau này).

# Salt có tác dụng gì trong việc chống Rainbow Table?
# Rainbow Table là một bảng cơ sở dữ liệu khổng lồ chứa sẵn hàng tỷ mật khẩu phổ biến (như 123456, password)
# đi kèm với chuỗi hash tương ứng của chúng. Nếu không dùng Salt, mật khẩu 123456 sẽ luôn tạo ra cùng một chuỗi hash XYZ.
# Hacker chỉ cần đối chiếu chuỗi XYZ bị lộ với Rainbow Table là sẽ tìm ra ngay mật khẩu gốc.