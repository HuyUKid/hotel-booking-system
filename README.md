# Hotel Booking System (Monorepo)

Hệ thống quản lý và đặt phòng khách sạn.

## Cấu trúc dự án
- `backend/`: Mã nguồn dịch vụ backend xây dựng bằng Django & Django REST.
- `frontend/`: Giao diện ứng dụng người dùng và nhân viên.
- `docs/`: Tài liệu đặc tả API (`api_contract.md`) và quy ước nhóm (`team_rules.md`).

## Hướng dẫn khởi chạy

### 1. Backend (Django)
```bash
cd backend
python -m venv venv
# Kích hoạt venv (Windows: .\venv\Scripts\Activate.ps1 | macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver