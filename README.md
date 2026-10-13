# Hotel Booking System — Authentication Backend

Repository hiện chứa backend xác thực nhân viên bằng Django. Phần frontend do
thành viên frontend phát triển độc lập dựa trên API contract.

## Phạm vi hiện tại

- Cấp CSRF token cho frontend độc lập.
- Đăng nhập bằng session cookie.
- Kiểm tra phiên và trạng thái bắt buộc đổi mật khẩu.
- Đổi mật khẩu theo bộ kiểm tra mật khẩu của Django.
- Đăng xuất và hủy phiên hiện tại.
- Quản lý tài khoản Django và `EmployeeProfile` trong Django Admin.

Chưa bao gồm nghiệp vụ phòng hoặc đặt phòng.

## Cấu trúc

```text
backend/             # Django API, model, migration và test xác thực
frontend/README.md   # Tài liệu duy nhất bàn giao cho thành viên frontend
docs/
├── api_contract.md
├── backend_guide.md
└── huong_dan_chay_du_an.md
```

## Chạy backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Xem [hướng dẫn chạy](docs/huong_dan_chay_du_an.md),
[API contract](docs/api_contract.md) và [hướng dẫn Backend](docs/backend_guide.md).

## Kiểm tra trước khi push

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test booking
```
