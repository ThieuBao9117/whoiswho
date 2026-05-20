# CÁC GIẢI PHÁP TÍCH HỢP HRM & WHO (KHÔNG DÙNG SSO)

Nếu chúng ta không muốn triển khai kiến trúc SSO (Single Sign-On) chuẩn (như OAuth2, OIDC, SAML bằng Keycloak/Authentik) vì lý do hạ tầng phức tạp, dưới đây là các phương pháp thay thế để hai hệ thống có thể kết nối với nhau:

## 1. Dùng JWT Secret Token Redirect (Khuyên dùng cho tính năng Đăng nhập tự động chéo)
**Kịch bản:** User đã đăng nhập vào HRM. Khi bấm vào nút "Đi đến WHO", hệ thống sẽ chuyển hướng và tự động đăng nhập vào WHO mà không bắt nhập lại mật khẩu.
- **Cách hoạt động:** 
  1. Cả HRM và WHO thống nhất chia sẻ chung một chuỗi bí mật (Shared Secret Key).
  2. HRM tạo một chuỗi mã JWT chứa thông tin người dùng (VD: `{"username": "admin", "emp_code": "E001"}`) và dùng Secret Key để ký điện tử (sign).
  3. HRM chuyển hướng (redirect) user sang WHO kèm theo JWT trên URL: `http://<ip-who>/auth/verify?token=ey...`
  4. WHO nhận token, dùng chính Secret Key đó để giải mã và kiểm tra. Nếu chữ ký đúng và token chưa hết hạn (chỉ set hạn khoảng 30-60 giây), WHO sẽ tự động tạo session đăng nhập cho user đó (nếu user chưa có bên WHO thì sẽ tự động khởi tạo).
- **Ưu điểm:** Dễ triển khai, nhẹ, code nhanh, không cần dựng một Identity Provider riêng.
- **Nhược điểm:** Cần bảo vệ Secret Key ở mức cao nhất. Bắt buộc phải giới hạn vòng đời của JWT cực ngắn (1 phút) để chống lại các cuộc tấn công nhặt được link cũ (Replay Attack).

## 2. Dùng chung Session (Shared Session Backend)
**Kịch bản:** Cả HRM và WHO đều chung Subdomain (ví dụ `hrm.domain.com` và `who.domain.com`) và dùng chung công nghệ (như Django).
- **Cách hoạt động:** 
  1. Hai hệ thống trỏ chung về một cơ sở dữ liệu Redis (hoặc database) làm Session Store chung.
  2. Cấu hình Cookie ở cả 2 hệ thống chia sẻ chéo Domain: `SESSION_COOKIE_DOMAIN = ".domain.com"`.
  3. Khi user đăng nhập trên HRM, một Session Cookie được lưu ở trình duyệt. Khi user truy cập sang WHO, trình duyệt gửi Cookie này, WHO lấy ID trong Cookie tra vào Redis chung và nhận diện được user.
- **Ưu điểm:** Trải nghiệm hoàn toàn mượt mà 100% giống SSO chuẩn.
- **Nhược điểm:** Tính ghép nối rất cao (Tight-coupling). Phụ thuộc vào việc phải chung subdomain và chung cách xử lý session.

## 3. Giao tiếp Backend-to-Backend bằng API Key
**Kịch bản:** Bỏ qua vấn đề tự động đăng nhập. User vẫn phải tạo tài khoản và tự đăng nhập độc lập trên 2 hệ thống. Hệ thống WHO chỉ cần liên kết để lấy dữ liệu danh bạ nhân sự từ HRM.
- **Cách hoạt động:** 
  1. HRM xây dựng một REST API nội bộ (VD: `/api/internal/employees`).
  2. HRM cấp cho WHO một chuỗi `API_KEY` bí mật.
  3. Định kỳ (hoặc khi cần), hệ thống backend của WHO sẽ gọi sang API của HRM kèm Header `Authorization: Api-Key <API_KEY>` để đồng bộ danh sách nhân viên.
- **Ưu điểm:** An toàn tuyệt đối, hai hệ thống độc lập hoàn toàn, dễ dàng mở rộng cho các hệ thống thứ 3 khác sau này.
- **Nhược điểm:** Không giải quyết được bài toán đăng nhập chung cho người dùng cuối (User vẫn cảm thấy đây là 2 hệ thống riêng biệt).

## 4. Đồng bộ bằng cơ sở dữ liệu (Database Views)
**Kịch bản:** WHO cần lấy thông tin cấu trúc tổ chức / nhân viên của HRM một cách nhanh nhất.
- **Cách hoạt động:** DB Admin cấp quyền Read-Only cho ứng dụng WHO để truy vấn trực tiếp vào Database của HRM (hoặc HRM tạo các View cung cấp riêng cho WHO đọc).
- **Ưu điểm:** Có ngay dữ liệu thực (real-time) mà không cần code các API trung gian.
- **Nhược điểm:** Rủi ro lỗi rất cao khi HRM cập nhật cấu trúc bảng (Migration) làm WHO bị gãy. Lỗi thiết kế theo kiến trúc Microservices hiện đại.

---
### TÓM LẠI & KHUYẾN NGHỊ:
- Nếu bạn muốn **trải nghiệm click sang là đăng nhập luôn** nhưng không muốn cấu hình SSO phức tạp: **HÃY CHỌN CÁCH 1 (JWT Redirect)**. Phương pháp này đủ tốt cho nội bộ.
- Nếu bạn **chỉ cần chia sẻ dữ liệu nhân viên**, mặc kệ người dùng tự quản lý tài khoản: **HÃY CHỌN CÁCH 3 (API Key)**.
- **Cách 2 và Cách 4** ít được sử dụng trong các hệ thống muốn duy trì tính độc lập.
