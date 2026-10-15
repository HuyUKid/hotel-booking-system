# Backend — module xác thực nhân viên

Backend hiện triển khai phần xác thực nhân viên. Frontend được phát triển độc lập
và giao tiếp với backend bằng HTTP/JSON theo
[`api_contract.md`](../docs/api_contract.md).

## 1. Chức năng hiện có

- Cấp CSRF token cho frontend.
- Đăng nhập bằng username/password.
- Tạo và duy trì Django session.
- Kiểm tra phiên đăng nhập hiện tại.
- Buộc nhân viên đổi mật khẩu lần đầu bằng `must_change_password`.
- Đổi mật khẩu và giữ nguyên phiên sau khi đổi.
- Đăng xuất và hủy phiên.

API đổi mật khẩu không kiểm tra độ mạnh. Mật khẩu mới chỉ cần không rỗng và khớp
với ô xác nhận.

## 2. Cấu trúc thư mục

```text
backend/
├── manage.py
├── requirements.txt
├── config/
│   ├── settings.py       # Django, database, session, CORS và CSRF
│   ├── urls.py           # Router cấp dự án
│   ├── asgi.py           # Entry point ASGI
│   └── wsgi.py           # Entry point WSGI
├── authentication/
│   ├── models.py         # EmployeeProfile
│   ├── views.py          # Xử lý API xác thực
│   ├── urls.py           # Endpoint xác thực dưới /api/...
│   ├── admin.py          # Quản lý EmployeeProfile trong Django Admin
│   ├── tests.py          # Kiểm thử API xác thực
│   └── migrations/       # Trạng thái schema của module xác thực
└── booking/
    ├── models.py         # Model đặt phòng sẽ phát triển tiếp
    ├── views.py          # API đặt phòng sẽ phát triển tiếp
    ├── urls.py           # URL có prefix /api/booking/
    └── tests.py          # Test nghiệp vụ đặt phòng
```

`authentication` và `booking` là hai app Django độc lập. Sau khi đăng nhập thành
công, frontend gọi các API trong `booking`; app xác thực không chứa nghiệp vụ phòng.

## 3. Dữ liệu xác thực

Django cung cấp model `User`, chứa username, password hash, họ tên và quyền.
Dự án bổ sung `EmployeeProfile`:

```python
class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    must_change_password = models.BooleanField(default=True)
```

Quan hệ `OneToOneField` bảo đảm một tài khoản có tối đa một profile. Khi xóa User,
profile cũng bị xóa. Nếu profile tồn tại và cờ bằng `True`, frontend phải đưa người
dùng đến màn hình đổi mật khẩu.

Signal trong `authentication/signals.py` tự tạo profile khi có User mới. Tài khoản
nhân viên nhận `must_change_password=True`; superuser nhận giá trị `False` để có
thể vào trang quản trị ngay. Migration dữ liệu cũng bổ sung profile cho các User
cũ còn thiếu.

## 4. Luồng request

```text
Frontend
  ↓ HTTP request + cookie/CSRF
config/urls.py
  ↓ include
authentication/urls.py
  ↓ chọn view theo URL và HTTP method
authentication/views.py
  ↓ Django Auth + EmployeeProfile
Database/session
  ↓
JSON response + HTTP status
```

Ví dụ đăng nhập:

1. Frontend gọi `GET /api/csrf/` để lấy CSRF token.
2. Frontend gửi `POST /api/login/` với username, password và token.
3. `authenticate()` kiểm tra mật khẩu đã băm trong database.
4. `login()` tạo session và gửi session cookie về trình duyệt.
5. Backend trả `username`, `display_name` và `must_change_password`.

Backend không trả password, password hash hoặc session key trong JSON.

## 5. Danh sách endpoint

| Method | Endpoint | Chức năng |
| --- | --- | --- |
| GET | `/api/csrf/` | Cấp CSRF token |
| GET | `/api/session/` | Trả người dùng đang đăng nhập |
| POST | `/api/login/` | Đăng nhập và tạo session |
| POST | `/api/change-password/` | Đổi mật khẩu và bỏ cờ bắt buộc đổi |
| POST | `/api/logout/` | Hủy session |

Request/response đầy đủ nằm trong
[`api_contract.md`](../docs/api_contract.md).

## 6. Trách nhiệm của Backend

- Kiểm tra mọi dữ liệu nhận từ frontend và trả lỗi đúng API contract.
- Quản lý tài khoản, mật khẩu băm, session và cờ `must_change_password`.
- Cấu hình đúng origin của frontend trong `CORS_ALLOWED_ORIGINS` và
  `CSRF_TRUSTED_ORIGINS`.
- Giữ ổn định URL, tên trường và kiểu dữ liệu đã thống nhất với frontend.
- Viết test cho cả luồng thành công, sai dữ liệu và chưa đăng nhập.

Frontend chỉ gửi dữ liệu và hiển thị kết quả. Backend vẫn phải kiểm tra lại toàn
bộ request, kể cả khi frontend đã validation.

## 7. Vai trò của các hàm chính

Trong `authentication/views.py`:

- `_json_body()`: chuyển request body JSON thành dictionary; trả HTTP 400 nếu JSON lỗi.
- `_must_change_password()`: kiểm tra cờ trên `EmployeeProfile`.
- `_unauthorized()`: tạo response HTTP 401 thống nhất.
- `api_csrf()`: tạo CSRF token và cookie.
- `api_session()`: kiểm tra session cookie và trả thông tin người dùng.
- `api_login()`: gọi `authenticate()` rồi `login()`.
- `api_change_password()`: gọi `set_password()`, cập nhật profile và session hash.
- `api_logout()`: gọi `logout()` để xóa phiên.

Phải dùng `set_password()` khi đổi mật khẩu. Không gán trực tiếp vào
`user.password`, vì Django cần băm mật khẩu đúng định dạng.

## 8. CORS, CSRF và session

- CORS xác định frontend origin nào được đọc response.
- CSRF ngăn website khác lợi dụng cookie để gửi POST giả mạo.
- Session cookie xác định người dùng đã đăng nhập.

Frontend phải gửi `credentials: "include"`. Các request POST phải gửi
`X-CSRFToken`. Origin frontend được cấu hình trong `config/settings.py`.

`BookingAuthenticationMiddleware` bảo vệ toàn bộ `/api/booking/`: request chưa
đăng nhập nhận HTTP 401; tài khoản còn `must_change_password=True` nhận HTTP 403.
Vì vậy người dùng không thể bỏ qua màn hình đổi mật khẩu bằng cách gọi API trực tiếp.

Response lỗi xác thực luôn có `status`, `code` và `message`. Frontend dùng `code`
để xử lý chương trình và dùng `message` để hiển thị cho người dùng.

## 9. Tạo tài khoản nhân viên thử nghiệm

Có thể tạo tài khoản trong Django Admin hoặc bằng `python manage.py shell`:

```python
from django.contrib.auth.models import User
user = User.objects.create_user(username='nv01', password='mat-khau-ban-dau')
```

Backend tự tạo `EmployeeProfile(must_change_password=True)`. Sau khi nhân viên
đăng nhập, frontend chuyển tới màn hình đổi mật khẩu. `createsuperuser` cũng tự
tạo profile nhưng không bắt buộc đổi mật khẩu.

## 10. Chạy và kiểm thử

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Kiểm tra trước khi commit:

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test authentication
```

## 11. Khi phối hợp với Frontend

Khi có lỗi tích hợp, kiểm tra URL, HTTP method, request body, status và response
trong Network của trình duyệt. Sau đó kiểm tra lần lượt origin CORS/CSRF,
`credentials: "include"`, header `X-CSRFToken` cho POST và session cookie.

Trước khi bàn giao, Backend cần chạy migration, tạo tài khoản có
`EmployeeProfile`, chạy toàn bộ kiểm thử và thông báo cho Frontend nếu API
contract thay đổi.

## 12. Tài liệu liên quan

- [`frontend/README.md`](../frontend/README.md): hướng dẫn frontend làm phần xác thực.
- [`api_contract.md`](../docs/api_contract.md): request/response chính thức.
- [`backend_guide.md`](../docs/backend_guide.md): quy trình phát triển và bàn giao Backend.
- [`git_workflow.md`](../docs/git_workflow.md): quy tắc nhánh, commit và phối hợp Git.
- [`huong_dan_chay_du_an.md`](../docs/huong_dan_chay_du_an.md): cách cài và chạy dự án.
- [`next_steps_after_auth.md`](../docs/next_steps_after_auth.md): công việc sau xác thực.

