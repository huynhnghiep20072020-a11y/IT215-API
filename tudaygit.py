import os
import subprocess

# --- BAN CHI CAN DOI THONG TIN O DAY MOI NGAY HOC ---
ten_session = "Session_4"  # Doi thanh buoi hoc hom nay
so_bai_tap = 6  # So luong bai tap
# ---------------------------------------------------

print(f"1. Dang kiem tra thu muc {ten_session}...")

os.makedirs(ten_session, exist_ok=True)

for i in range(so_bai_tap):
    thu_muc_con = f'{ten_session}/Bai_{i + 1}'
    os.makedirs(thu_muc_con, exist_ok=True)
    
    file_main = f'{thu_muc_con}/main.py'
    if not os.path.exists(file_main):
        with open(file_main, 'w') as f:
            pass 

print("\n" + "="*50)
loi_nhan = input(" Nhập lời nhắn commit (bạn có thể để trống để dùng lời nhắn mặc định): ")

if loi_nhan.strip() == "":
    loi_nhan = f"Cap nhat code cho {ten_session}"
print("="*50 + "\n")

print(f"2. Dang gom code {ten_session} va day len GitHub...")

# --- ĐOẠN ĐÃ SỬA ĐỂ ĐẨY CHUẨN LÊN NHÁNH MAIN ---
# Thêm toàn bộ các thay đổi mới (bao gồm cả file script và thư mục Session)
subprocess.run(['git', 'add', '.'])
# Thực hiện commit với lời nhắn của bạn
subprocess.run(['git', 'commit', '-m', loi_nhan])
# Đẩy code lên nhánh 'main' thay vì 'master'
subprocess.run(['git', 'push', 'origin', 'main'])

print(f"\nTHANH CONG! Bai cua ban da duoc day len với loi nhan: '{loi_nhan}'")