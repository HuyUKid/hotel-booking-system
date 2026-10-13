# Quy tắc làm việc với Git cho Frontend và Backend

Tài liệu này giúp hai nhóm làm việc trong cùng repository mà hạn chế ghi đè code,
xung đột file và thay đổi API không được thông báo.

## 1. Nhánh sử dụng

- `main`: chỉ chứa phiên bản đã kiểm tra và có thể bàn giao.
- Mỗi công việc được thực hiện trên một nhánh riêng tạo từ `main` mới nhất.
- Không viết tính năng trực tiếp trên `main`.

Quy tắc đặt tên nhánh:

```text
frontend/<ten-cong-viec>
backend/<ten-cong-viec>
docs/<ten-cong-viec>
fix/<ten-loi>
```

Ví dụ:

```text
frontend/login-page
backend/create-booking-api
docs/update-api-contract
fix/session-expired
```

Tạo nhánh mới:

```powershell
git switch main
git pull origin main
git switch -c backend/create-booking-api
```

Thành viên Frontend thay `backend/` bằng `frontend/` trong tên nhánh.

## 2. Phạm vi file của từng nhóm

### Frontend

Frontend chịu trách nhiệm chính đối với:

```text
frontend/
frontend/README.md
```

Frontend không tự sửa model, migration, cấu hình xác thực hoặc API Backend. Nếu
cần thay đổi request/response, hai bên thống nhất và cập nhật API contract trước.

### Backend

Backend chịu trách nhiệm chính đối với:

```text
backend/
backend/README.md
docs/backend_guide.md
```

Backend không tự thay đổi cấu trúc màn hình hoặc mã nguồn trong `frontend/`. Khi
API thay đổi, Backend phải mô tả rõ ảnh hưởng đối với Frontend.

### File dùng chung

Hai bên cùng chịu trách nhiệm đối với:

```text
README.md
docs/api_contract.md
docs/next_steps_after_auth.md
docs/git_workflow.md
```

Nếu cùng cần sửa một file dùng chung, thông báo trước trong nhóm và chia người sửa
theo từng commit để tránh xử lý conflict không cần thiết.

## 3. Quy trình của Frontend

1. Cập nhật `main` và tạo nhánh `frontend/...`.
2. Đọc `frontend/README.md` và `docs/api_contract.md`.
3. Làm giao diện bằng dữ liệu mock đúng cấu trúc API đã thống nhất.
4. Tích hợp API thật, gồm cookie, CSRF, loading và xử lý lỗi.
5. Không commit mật khẩu, tài khoản thật, file `.env` hoặc dependency đã cài.
6. Kiểm tra luồng giao diện rồi commit và push nhánh.
7. Tạo pull request vào `main`, ghi rõ màn hình và API đã sử dụng.

## 4. Quy trình của Backend

1. Cập nhật `main` và tạo nhánh `backend/...`.
2. Thống nhất API với Frontend và cập nhật `docs/api_contract.md`.
3. Viết model, migration, service, view, URL và test trong đúng Django app.
4. Không sửa hoặc xóa migration đã được thành viên khác sử dụng; tạo migration mới.
5. Không commit database `db.sqlite3`, môi trường ảo, `.env` hoặc khóa bí mật.
6. Chạy kiểm tra Backend trước khi commit:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
```

7. Push nhánh và tạo pull request vào `main`; ghi rõ migration, endpoint và thay
   đổi API contract.

## 5. Commit

Mỗi commit chỉ nên giải quyết một mục đích và phải có thông điệp dễ hiểu:

```text
frontend: add login form validation
backend: add room availability endpoint
fix: keep session after password change
test: cover booking cancellation
docs: update booking API contract
```

Trước khi commit, luôn kiểm tra:

```powershell
git status
git diff
```

Chỉ dùng `git add` cho những file thuộc công việc hiện tại. Không dùng
`git add .` khi thư mục đang có thay đổi của thành viên khác hoặc file chưa rõ
nguồn gốc.

## 6. Pull request và review

Pull request cần ghi:

- Vấn đề hoặc chức năng được xử lý.
- Thay đổi chính.
- Cách kiểm tra.
- Endpoint, migration hoặc ảnh hưởng tới nhóm còn lại.
- Ảnh giao diện nếu thay đổi Frontend.

Người review kiểm tra code, API contract, migration và kết quả test trước khi
merge. Sau khi merge, các thành viên cập nhật lại nhánh cá nhân:

```powershell
git switch main
git pull origin main
git switch <ten-nhanh>
git merge main
```

Nếu có conflict, người hiểu file bị conflict trực tiếp xử lý. Không chọn toàn bộ
phiên bản của một bên khi chưa đọc và so sánh nội dung.

## 7. Thứ tự phối hợp khi API thay đổi

1. Frontend mô tả dữ liệu cần gửi hoặc hiển thị.
2. Backend đề xuất endpoint, request, response và HTTP status.
3. Hai bên thống nhất rồi cập nhật `docs/api_contract.md`.
4. Backend triển khai API và test; Frontend có thể dùng mock JSON để làm song song.
5. Backend bàn giao base URL, migration và dữ liệu thử.
6. Frontend tích hợp API thật và báo lỗi kèm thông tin trong Network.
7. Hai bên kiểm thử hoàn chỉnh trước khi merge vào `main`.

Không merge thay đổi phá vỡ API hiện tại nếu phần Frontend tương ứng chưa sẵn sàng
hoặc chưa có cách tương thích trong thời gian chuyển đổi.

