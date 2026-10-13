# Hướng dẫn Backend — module xác thực

## Backend hiện phải chịu trách nhiệm gì?

- Quản lý tài khoản bằng `django.contrib.auth`.
- Lưu cờ bắt buộc đổi mật khẩu trong `EmployeeProfile`.
- Xác thực mật khẩu và tạo/xóa session.
- Cấp, kiểm tra CSRF token cho frontend độc lập.
- Cho phép đúng frontend origin bằng CORS.
- Trả JSON và HTTP status thống nhất theo `api_contract.md`.
- Kiểm thử cả luồng thành công và thất bại.

Frontend chỉ thu thập dữ liệu và hiển thị kết quả. Backend phải kiểm tra lại mọi
request; không tin validation phía trình duyệt.

## Các file quan trọng

| File | Trách nhiệm |
| --- | --- |
| `booking/models.py` | `EmployeeProfile.must_change_password` |
| `booking/views.py` | CSRF, session, login, logout, đổi mật khẩu |
| `booking/urls.py` | URL `/api/...` |
| `booking/tests.py` | Kiểm thử API xác thực |
| `config/settings.py` | CORS, CSRF, session, password validators |
| `docs/api_contract.md` | Giao kèo chính thức với frontend |

## Công việc Backend cần làm trước khi bàn giao

1. Chốt origin mà frontend sử dụng và cập nhật `CORS_ALLOWED_ORIGINS` cùng
   `CSRF_TRUSTED_ORIGINS`.
2. Chạy migration và tạo tài khoản thử.
3. Tạo `EmployeeProfile` cho tài khoản nhân viên; đặt
   `must_change_password=True` nếu muốn buộc đổi mật khẩu lần đầu.
4. Chạy test và gửi API contract cho frontend.
5. Không đổi URL, tên trường hoặc kiểu dữ liệu mà chưa báo frontend.

Tạo tài khoản bằng Django Admin hoặc shell. Ví dụ trong shell:

```python
from django.contrib.auth.models import User
from booking.models import EmployeeProfile

user = User.objects.create_user(
    username='nv01',
    password='InitialPassword@123',
    first_name='Văn A',
    last_name='Nguyễn',
)
EmployeeProfile.objects.create(user=user, must_change_password=True)
```

## Khi Frontend báo lỗi tích hợp

Yêu cầu frontend cung cấp URL, method, request body, HTTP status và response. Sau đó
kiểm tra theo thứ tự:

1. Backend có chạy đúng `127.0.0.1:8000` không.
2. Frontend origin có nằm trong CORS/CSRF settings không.
3. Request có `credentials: "include"` không.
4. POST có `X-CSRFToken` không.
5. Session cookie có xuất hiện trong Network/Application của trình duyệt không.
6. Request body có đúng contract không.

Không tắt CSRF hoặc mở `CORS_ALLOW_ALL_ORIGINS` để sửa tạm lỗi tích hợp.

## Kiểm tra trước khi push

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test booking
```

Module đủ điều kiện bàn giao khi các lệnh trên thành công, migration chạy được từ
database mới và frontend đăng nhập/đổi mật khẩu/đăng xuất được theo contract.

## Việc nên làm tiếp theo ở Backend

- Đưa `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` và frontend origins sang biến môi trường.
- Thêm giới hạn số lần đăng nhập sai nếu triển khai thực tế.
- Quy định ai tạo tài khoản nhân viên và tự động tạo `EmployeeProfile` trong luồng đó.
- Thiết lập HTTPS, cookie secure và thời hạn session cho môi trường production.
- Chỉ bắt đầu nghiệp vụ đặt phòng sau khi nhóm chốt model và API contract riêng.

