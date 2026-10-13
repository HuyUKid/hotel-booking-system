# Hướng dẫn chạy backend xác thực

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
- Frontend được nhóm frontend triển khai riêng theo `frontend/README.md`.

## Chạy kiểm thử

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test booking
```

