# Hotel Booking System

Repository hiện có Backend xác thực nhân viên bằng Django và bản Frontend
HTML/JavaScript cơ bản. Hai phần phát triển độc lập và giao tiếp theo API contract.

## Phạm vi hiện tại

- Cấp CSRF token cho frontend độc lập.
- Đăng nhập bằng session cookie.
- Kiểm tra phiên và trạng thái bắt buộc đổi mật khẩu.
- Đổi mật khẩu; mật khẩu mới chỉ cần không rỗng và khớp với ô xác nhận.
- Đăng xuất và hủy phiên hiện tại.
- Quản lý tài khoản Django và `EmployeeProfile` trong Django Admin.

Chưa bao gồm nghiệp vụ phòng hoặc đặt phòng.

## Tài liệu nghiệp vụ

- [Quy trình đặt phòng](docs/reference/quy-trinh-dat-phong.pdf): bản tài liệu
  nghiệp vụ dùng cho dự án, đã bỏ trang bìa đầu tiên.
- [Kế hoạch phối hợp sau xác thực](docs/next_steps_after_auth.md): thứ tự triển
  khai và mốc bàn giao chung giữa Backend và Frontend.

## Cấu trúc

```text
backend/
├── authentication/  # API, model, migration và test xác thực
└── booking/         # Nghiệp vụ đặt phòng sẽ phát triển tiếp
frontend/
├── api.js
├── login.html
├── change-password.html
├── index.html
└── README.md         # Việc Frontend cần hoàn thiện để tích hợp Backend
docs/
├── api_contract.md
├── backend_guide.md
├── git_workflow.md
├── huong_dan_chay_du_an.md
├── next_steps_after_auth.md
└── reference/
    └── quy-trinh-dat-phong.pdf
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
[API contract](docs/api_contract.md), [README Backend](backend/README.md),
[hướng dẫn làm việc Backend](docs/backend_guide.md),
[quy tắc làm việc với Git](docs/git_workflow.md),
[README Frontend](frontend/README.md) và
[lộ trình sau xác thực](docs/next_steps_after_auth.md).

## Kiểm tra trước khi push

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
```
