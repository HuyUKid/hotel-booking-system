# Hướng dẫn làm việc cho Backend

Tài liệu này hướng dẫn quy trình phát triển và bàn giao của thành viên Backend.
Phần giải thích chi tiết cấu trúc module xác thực nằm trong
[`backend/README.md`](../backend/README.md); request và response dùng để phối hợp
với Frontend nằm trong [`api_contract.md`](api_contract.md).

## 1. Phạm vi hiện tại

Backend được chia thành hai Django app:

- `authentication`: đăng nhập, đăng xuất, session, CSRF và đổi mật khẩu.
- `booking`: nghiệp vụ phòng và đặt phòng sau khi xác thực.

Không đặt model hoặc API đặt phòng vào `authentication`. Các API xác thực dùng
prefix `/api/`; các API nghiệp vụ mới dùng prefix `/api/booking/`.

## 2. Quy trình phát triển một chức năng

1. Đọc yêu cầu nghiệp vụ và xác định người dùng, dữ liệu đầu vào, kết quả đầu ra.
2. Thống nhất với Frontend URL, HTTP method, request, response và mã lỗi.
3. Cập nhật [`api_contract.md`](api_contract.md) trước khi hai bên viết code.
4. Thiết kế hoặc sửa model trong đúng Django app.
5. Tạo migration nếu schema thay đổi; không sửa migration đã được dùng chung.
6. Viết view, URL và kiểm tra quyền ở Backend.
7. Viết test cho luồng thành công, dữ liệu sai, chưa đăng nhập và thiếu quyền.
8. Chạy kiểm tra, chuẩn bị dữ liệu mẫu rồi bàn giao endpoint cho Frontend.

## 3. Quy tắc API

- Nhận và trả dữ liệu JSON, trừ endpoint không cần body.
- Trả cấu trúc lỗi thống nhất gồm `status`, `code` và `message`.
- Dùng đúng HTTP status: `400` cho dữ liệu sai, `401` cho chưa xác thực, `403`
  cho không đủ quyền và `405` cho sai method.
- Backend luôn kiểm tra lại dữ liệu; không phụ thuộc validation ở trình duyệt.
- Không trả mật khẩu, password hash, session key hoặc stack trace cho Frontend.
- Không đổi URL hoặc tên trường đã thống nhất mà chưa cập nhật API contract.
- Trả mã lỗi ổn định trong trường `code`; không yêu cầu Frontend phân tích
  nội dung tiếng Việt trong `message`.
- Mọi API `/api/booking/` phải đi qua kiểm tra session và trạng thái đổi mật khẩu.

## 4. Tài khoản dùng để tích hợp

Sau khi chạy migration, tạo tài khoản thử trong Django Admin hoặc shell:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py shell
```

```python
from django.contrib.auth.models import User

user = User.objects.create_user(username='nv01', password='mat-khau-ban-dau')
```

Signal của module `authentication` tự tạo `EmployeeProfile` với
`must_change_password=True`. Không cần tạo profile thủ công. Tài khoản tạo bằng
`createsuperuser` nhận `must_change_password=False`.

Chỉ gửi tài khoản thử qua kênh làm việc của nhóm. Không commit mật khẩu thật hoặc
dữ liệu bí mật vào repository.

## 5. Phối hợp với Frontend

Backend cần bàn giao:

- Base URL và origin Frontend đã được cấu hình CORS/CSRF.
- Endpoint, method, request, response và các HTTP status có thể xuất hiện.
- Tài khoản cùng dữ liệu mẫu để kiểm thử.
- Thay đổi API contract và migration mới nếu có.

Khi Frontend báo lỗi, yêu cầu cung cấp URL, method, request body, HTTP status và
response trong Network. Kiểm tra lần lượt backend đang chạy, origin được cho phép,
`credentials: "include"`, `X-CSRFToken` cho POST và session cookie.

## 6. Kiểm tra trước khi commit

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
```

Chỉ bàn giao khi migration chạy được, test đạt và hành vi thực tế khớp với API
contract. Với công việc tiếp theo, làm theo phân chia Backend/Frontend trong
[`next_steps_after_auth.md`](next_steps_after_auth.md).

