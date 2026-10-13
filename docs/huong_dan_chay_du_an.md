# Hướng dẫn chạy dự án

Hiện repository đã có backend Django. Phần frontend đang được thành viên frontend
xây dựng độc lập theo [`frontend/README.md`](../frontend/README.md).

## Thiết lập lần đầu

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py createsuperuser
```

## Chạy backend

```powershell
cd backend
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

- Django Admin: `http://127.0.0.1:8000/admin/`
- CSRF API: `http://127.0.0.1:8000/api/csrf/`
- Frontend được triển khai riêng theo
  [`frontend/README.md`](../frontend/README.md).

## Chạy frontend khi đã có mã nguồn

Frontend phải chạy bằng HTTP, không mở trực tiếp file bằng địa chỉ `file://`.
Nếu dùng HTML/CSS/JavaScript thuần, có thể dùng VS Code Live Server tại
`http://127.0.0.1:5500`. Nếu dùng React/Vue, chạy lệnh của framework và gửi origin
thực tế cho Backend để thêm vào cấu hình CORS và CSRF.

Giữ cùng cách viết hostname ở hai phía, ưu tiên `127.0.0.1`; không trộn với
`localhost` để tránh lỗi cookie.

## Chạy kiểm thử

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test authentication
```

