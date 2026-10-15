# Hướng dẫn chạy dự án

Repository gồm Backend Django trong `backend/` và Frontend HTML/JavaScript trong
`frontend/`. Hai phần chạy trên hai địa chỉ khác nhau và giao tiếp bằng HTTP API.

## Tải hoặc cập nhật mã nguồn

Nếu máy chưa có dự án:

```powershell
git clone https://github.com/HuyUKid/hotel-booking-system.git
cd hotel-booking-system
```

Nếu máy đã có dự án và không có thay đổi local cần giữ:

```powershell
git switch main
git pull origin main
```

Luôn chạy `git status` trước khi pull. Nếu có file đang sửa, hãy commit trên nhánh
riêng hoặc dùng `git stash` rồi mới cập nhật.

## Thiết lập lần đầu

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py createsuperuser
```

`createsuperuser` tạo tài khoản quản trị không bắt buộc đổi mật khẩu. Khi tạo một
User nhân viên trong Django Admin hoặc bằng `User.objects.create_user()`, Backend
tự tạo `EmployeeProfile` và yêu cầu nhân viên đổi mật khẩu ở lần đăng nhập đầu.

## Chạy cả Backend và Frontend

Mở hai cửa sổ PowerShell tại thư mục gốc dự án.

Terminal 1 chạy Backend:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

- Django Admin: `http://127.0.0.1:8000/admin/`
- CSRF API: `http://127.0.0.1:8000/api/csrf/`
Terminal 2 chạy Frontend:

```powershell
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```

Mở `http://127.0.0.1:5500/login.html`. Có thể dùng VS Code Live Server thay cho
lệnh trên, miễn là Frontend chạy tại `http://127.0.0.1:5500` hoặc
`http://127.0.0.1:5501`.

Frontend phải chạy bằng HTTP; không mở `login.html` trực tiếp bằng địa chỉ
`file://` vì cookie và request API sẽ không hoạt động đúng.

Giữ cùng cách viết hostname ở hai phía, ưu tiên `127.0.0.1`; không trộn với
`localhost` để tránh lỗi cookie.

## Kiểm thử Backend tự động

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
```

## Kiểm thử tích hợp hai bên

Thực hiện lần lượt trên trình duyệt:

1. Mở `/login.html` và thử tài khoản hoặc mật khẩu sai; giao diện phải hiện lỗi.
2. Đăng nhập bằng tài khoản có `must_change_password = true`; trình duyệt phải
   chuyển sang `/change-password.html`.
3. Nhập hai mật khẩu khác nhau; Backend phải trả lỗi và không đổi mật khẩu.
4. Đổi mật khẩu hợp lệ; trình duyệt phải chuyển tới `/index.html`.
5. Tải lại `/index.html`; tên nhân viên vẫn hiển thị vì session còn hiệu lực.
6. Nhấn đăng xuất; trình duyệt trở về `/login.html`.
7. Mở lại `/index.html`; người dùng phải bị chuyển về trang đăng nhập.

Khi có lỗi, mở Developer Tools → Network và ghi lại URL, method, HTTP status cùng
response. Đối chiếu request/response với [`api_contract.md`](api_contract.md).

