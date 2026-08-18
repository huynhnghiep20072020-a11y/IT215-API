# Giả lập Database (In-memory)
users_db = {
    "admin_01": {"id": "admin_01", "username": "admin_01", "password": "password123", "role": "admin", "is_active": True},
    "student_01": {"id": "student_01", "username": "student_01", "password": "password123", "role": "user", "is_active": True},
    "student_02": {"id": "student_02", "username": "student_02", "password": "password123", "role": "user", "is_active": True},
    "locked_01": {"id": "locked_01", "username": "locked_01", "password": "password123", "role": "user", "is_active": False},
}

assignments_db = {}
submissions_db = {}

# Sequence ID
counters = {"assignment": 0, "submission": 0}