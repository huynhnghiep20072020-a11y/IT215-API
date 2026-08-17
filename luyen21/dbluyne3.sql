CREATE DATABASE cntt5_project;

USE cntt5_project;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Cột ID tự động tăng, làm khóa chính
    name VARCHAR(100) NOT NULL,         -- Cột Tên, kiểu chuỗi, không được để trống
    email VARCHAR(100) UNIQUE NOT NULL, -- Cột Email, không được trùng lặp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Tự động lưu thời gian tạo
);


INSERT INTO users (name, email) 
VALUES 
    ('Huỳnh Nhơn Nguyên Nghiệp', 'nghiep@example.com'),
    ('Lê Taans Toàn ', 'toan@example.com');

SELECT * FROM users;