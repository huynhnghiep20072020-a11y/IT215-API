import requests

BASE_URL = "http://localhost:8000/api"

def run_tests():
    print("--- 1. Đăng ký tài khoản Admin và Customer ---")
    requests.post(f"{BASE_URL}/auth/register", json={"username": "admin_user", "password": "password123", "role": "admin"})
    c1 = requests.post(f"{BASE_URL}/auth/register", json={"username": "customer_1", "password": "password123"})
    print("KH1 đăng ký:", c1.json())
    requests.post(f"{BASE_URL}/auth/register", json={"username": "customer_2", "password": "password123"})

    print("\n--- 2. Kiểm tra bắt lỗi (Validation) ---")
    c1_dup = requests.post(f"{BASE_URL}/auth/register", json={"username": "customer_1", "password": "password123"})
    print("Đăng ký trùng lặp:", c1_dup.json()) # Mong đợi: USER_ALREADY_EXISTS 409

    print("\n--- 3. Đăng nhập và Lấy Token ---")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "customer_1", "password": "password123"})
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login thành công, Token cấp phát.")

    print("\n--- 4. Xem số dư (Customer) ---")
    balance = requests.get(f"{BASE_URL}/account/balance", headers=headers)
    print("Số dư:", balance.json())

    print("\n--- 5. Test Phân quyền (RBAC) ---")
    admin_api_fail = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    print("Customer gọi hàm Admin:", admin_api_fail.json()) 

    print("\n--- 6. Chuyển tiền (Transaction) ---")
    # Lỗi: Tự chuyển cho mình
    t1 = requests.post(f"{BASE_URL}/account/transfer", json={"to_username": "customer_1", "amount": 100}, headers=headers)
    print("Tự chuyển cho mình:", t1.json()) 
    
    # Thành công
    t2 = requests.post(f"{BASE_URL}/account/transfer", json={"to_username": "customer_2", "amount": 2000.0, "note": "Tra tien an"}, headers=headers)
    print("Chuyển 2000 cho customer_2:", t2.json())
    
    # Lỗi: Không đủ tiền
    t3 = requests.post(f"{BASE_URL}/account/transfer", json={"to_username": "customer_2", "amount": 90000.0}, headers=headers)
    print("Chuyển quá số dư:", t3.json()) 

    print("\n--- 7. Quản trị viên xem báo cáo ---")
    admin_token = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin_user", "password": "password123"}).json().get("access_token")
    admin_res = requests.get(f"{BASE_URL}/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    print("Báo cáo hệ thống:")
    for u in admin_res.json():
        print(f"User: {u['username']} - Role: {u['role']} - Balance: {u['balance']}")

if __name__ == "__main__":
    run_tests()
