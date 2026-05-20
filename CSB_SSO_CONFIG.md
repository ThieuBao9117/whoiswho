# Cấu hình Tích hợp SSO (HRM -> CSB Connection)

Tài liệu này cung cấp các thông số kỹ thuật cần thiết để hệ thống HRM (WHO) tích hợp đăng nhập một lần (SSO) sang hệ thống CSB Connection.

## 1. Thông số kỹ thuật JWT

Hệ thống CSB sử dụng JSON Web Token (JWT) để xác thực. Các thông số sau đây **bắt buộc** phải khớp giữa hai hệ thống:

*   **Thuật toán (Algorithm):** `HS256`
*   **Khóa bí mật (Secret Key):** `09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7`
*   **Thời hạn Token (Expiration):** Khuyến nghị từ **3 - 5 phút** kể từ lúc tạo.

## 2. Cấu hình URL

Khi người dùng nhấn nút chuyển sang CSB, HRM cần redirect về địa chỉ sau:

*   **URL Đích:** `http://localhost:5173/game/sso?token={JWT_TOKEN}`
*   *(Thay `localhost:5173` bằng domain chính thức khi triển khai Production)*

## 3. Cấu trúc Payload (JWT)

Dữ liệu bên trong Token cần có các trường sau:

```json
{
  "sub": "username_cua_nhan_vien", 
  "exp": 1716180000, 
  "iat": 1716179700
}
```
*   **sub (Subject):** Bắt buộc phải là `username` của nhân viên. **Lưu ý:** Hệ thống CSB hiện tại hỗ trợ tìm kiếm không phân biệt chữ hoa/chữ thường (Case-insensitive).
*   **exp (Expiration Time):** Thời gian hết hạn (Unix timestamp).
*   **iat (Issued At):** Thời gian tạo token (Unix timestamp).

## 4. Ví dụ Code tạo Token (Python/Django)

```python
import jwt
import datetime

# Thông số cấu hình
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
CSB_SSO_URL = "http://localhost:5173/game/sso"

def generate_sso_link(username):
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return f"{CSB_SSO_URL}?token={token}"
```

## 5. Lưu ý quan trọng
1.  **Dữ liệu người dùng:** Username trong token phải tồn tại trong cơ sở dữ liệu của CSB (đã qua bước Đồng bộ/Sync).
2.  **Cổng kết nối (Ports):**
    *   Backend CSB: Chạy tại cổng **7000**.
    *   Frontend CSB: Chạy tại cổng **5173**.
    *   Vite Proxy: Đã được cấu hình để chuyển tiếp các yêu cầu `/api` sang cổng **7000**.
