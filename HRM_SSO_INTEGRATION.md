# Tài Liệu Hướng Dẫn Tích Hợp Đăng Nhập SSO (HRM -> CSB Connection)

Tài liệu này dành cho đội ngũ phát triển (Dev) của hệ thống HRM (Django) để cấu hình nút Đăng nhập nhanh (Single Sign-On) từ HRM sang hệ thống Game "CSB Connection".

## 1. Nguyên lý hoạt động
- **Bước 1:** Nhân viên đăng nhập vào hệ thống HRM như bình thường.
- **Bước 2:** Trên giao diện HRM có nút "Vào CSB Connection". Khi click, HRM sẽ mã hóa thông tin User thành một **JWT Token** (bằng một Khóa bí mật dùng chung).
- **Bước 3:** HRM tự động Redirect trình duyệt sang trang Frontend của CSB kèm theo token trên URL.
- **Bước 4:** CSB tự động giải mã, xác thực và cho phép nhân viên vào hệ thống mà không cần gõ lại mật khẩu.

## 2. Thông tin kết nối (Cần đồng bộ)
Cả hai hệ thống (HRM và CSB) phải sử dụng chung 2 cấu hình sau:
- `SECRET_KEY`: `"csb-connection-secret-2026"` *(Có thể đổi lại trên server production, nhưng 2 bên phải giống hệt nhau)*
- `ALGORITHM`: `"HS256"`

## 3. Cấu hình bên phía HRM (Django)

### Cài đặt thư viện (nếu chưa có)
Trong hệ thống Django, cần sử dụng thư viện `PyJWT` để tạo Token:
```bash
pip install PyJWT
```

### Code tạo Token và Redirect (Django View)
Tạo một endpoint (View) trong Django để xử lý khi người dùng click vào nút "Vào CSB Connection".

```python
import jwt
import datetime
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Khóa bí mật đồng bộ với CSB (nên đưa vào settings.py hoặc .env)
CSB_SECRET_KEY = "csb-connection-secret-2026"
CSB_FRONTEND_URL = "http://localhost:5173"  # Thay bằng domain thật khi lên Production

@login_required
def redirect_to_csb_game(request):
    """
    Tạo token và chuyển hướng user sang hệ thống CSB Connection
    """
    user = request.user
    
    # 1. Khởi tạo Payload chứa thông tin cơ bản
    payload = {
        "sub": user.username,  # Quan trọng: Username phải trùng khớp với dữ liệu đã đồng bộ sang CSB
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),  # Token chỉ có hạn 5 phút để bảo mật
        "iat": datetime.datetime.utcnow(),
    }
    
    # 2. Mã hóa thành chuỗi JWT
    token = jwt.encode(payload, CSB_SECRET_KEY, algorithm="HS256")
    
    # 3. Tạo URL chuyển hướng sang CSB kèm Token
    redirect_url = f"{CSB_FRONTEND_URL}/sso?token={token}"
    
    # 4. Redirect trình duyệt
    return redirect(redirect_url)
```

### Cấu hình URL trong urls.py
```python
from django.urls import path
from .views import redirect_to_csb_game

urlpatterns = [
    # ... các url khác
    path('go-to-csb/', redirect_to_csb_game, name='go_to_csb'),
]
```

## 4. Cấu hình giao diện (Frontend HRM)
Thêm nút bấm vào menu hoặc dashboard của HRM để nhân viên nhấn vào:
```html
<!-- Nút chuyển sang game CSB -->
<a href="{% url 'go_to_csb' %}" class="btn btn-primary" target="_blank">
    🎮 Vào CSB Connection
</a>
```

## 5. Lưu ý quan trọng
1. **Bảo mật:** Token chỉ nên có thời hạn ngắn (khoảng 3-5 phút) để tránh bị copy token đem đi máy khác. Quá hạn, CSB sẽ từ chối và yêu cầu tạo lại.
2. **Đồng bộ Dữ liệu:** Username truyền trong trường `"sub"` của Token **bắt buộc** phải là Username đã tồn tại trong cơ sở dữ liệu của CSB (đã được đồng bộ trước đó qua tính năng Sync).
3. **Môi trường Web:** Nếu chạy trên server thật, nhớ thay đổi `CSB_FRONTEND_URL` thành địa chỉ web chính thức (ví dụ: `http://10.x.x.x:5173` hoặc `https://csb.company.com`).
