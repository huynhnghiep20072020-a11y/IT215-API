import os
import subprocess

# --- BẠN CHỈ CẦN ĐỔI THÔNG TIN Ở ĐÂY MỖI NGÀY HỌC ---
ten_session = "Session_11"  # Đổi thành buổi học hôm nay (Ví dụ: Session_6, Session_7...)
so_bai_tap = 3  # Số lượng bài tập muốn tạo tự động
# ---------------------------------------------------

print(f"1. Dang kiem tra thu muc {ten_session}...")

# Tự động tạo thư mục Session (nếu chưa có)
os.makedirs(ten_session, exist_ok=True)

# Tự động tạo các thư mục bài tập con và file main.py trống bên trong
for i in range(so_bai_tap):
    thu_muc_con = f'{ten_session}/Bai_{i + 1}'
    os.makedirs(thu_muc_con, exist_ok=True)
    
    file_main = f'{thu_muc_con}/main.py'
    if not os.path.exists(file_main):
        with open(file_main, 'w') as f:
            pass 

# --- NHẬP LỜI NHẮN COMMIT ---
print("\n" + "="*50)
loi_nhan = input(" Nhập lời nhắn commit (bạn có thể để trống để dùng lời nhắn mặc định): ")

# Nếu bấm Enter trống, tự động dùng lời nhắn mặc định
if loi_nhan.strip() == "":
    loi_nhan = f"Cap nhat code cho {ten_session}"
print("="*50 + "\n")

print(f"2. Dang gom code {ten_session} va day len GitHub...")

# --- XỬ LÝ GIT: CHỈ ĐẨY ĐÚNG THƯ MỤC CỦA BUỔI HỌC HÔM NAY ---
# 1. Chỉ gom duy nhất thư mục Session được chỉ định ở đầu file
subprocess.run(['git', 'add', ten_session])

# 2. Gom thêm chính file script này để lưu lại lịch sử thay đổi cấu hình tên Session trên GitHub
subprocess.run(['git', 'add', 'tudaygit.py'])

# 3. Tạo commit với lời nhắn vừa nhập
subprocess.run(['git', 'commit', '-m', loi_nhan])

# 4. Đẩy chuẩn xác lên nhánh main của repository
subprocess.run(['git', 'push', 'origin', 'main'])

print(f"\nTHANH CONG! Bai cua ban da duoc day len với loi nhan: '{loi_nhan}'")