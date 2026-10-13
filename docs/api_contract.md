# API Contract — Xác thực nhân viên

Base URL phát triển: `http://127.0.0.1:8000`.

Frontend gửi mọi request với `credentials: "include"`. Các request POST phải có
header `X-CSRFToken` lấy từ endpoint CSRF.

## Response lỗi chung

```json
{
  "status": "error",
  "message": "Nội dung lỗi có thể hiển thị cho người dùng."
}
```

## 1. Lấy CSRF token

```http
GET /api/csrf/
```

Response 200:

```json
{
  "status": "success",
  "csrf_token": "token-value"
}
```

## 2. Đăng nhập

```http
POST /api/login/
Content-Type: application/json
X-CSRFToken: token-value
```

Request:

```json
{
  "username": "nv01",
  "password": "initial_password"
}
```

Response 200:

```json
{
  "status": "success",
  "username": "Nguyễn Văn A",
  "must_change_password": true
}
```

Lỗi: HTTP 400 nếu thiếu dữ liệu; HTTP 401 nếu thông tin đăng nhập không đúng.

## 3. Kiểm tra phiên

```http
GET /api/session/
```

Response 200 giống phần thông tin người dùng của đăng nhập:

```json
{
  "status": "success",
  "username": "Nguyễn Văn A",
  "must_change_password": false
}
```

HTTP 401 nếu chưa đăng nhập hoặc phiên hết hạn.

## 4. Đổi mật khẩu

```http
POST /api/change-password/
Content-Type: application/json
X-CSRFToken: token-value
```

Request:

```json
{
  "new_password": "NewSecretPassword@123",
  "confirm_password": "NewSecretPassword@123"
}
```

Response 200:

```json
{
  "status": "success"
}
```

Backend không kiểm tra độ mạnh mật khẩu. Mật khẩu chỉ cần không rỗng và khớp với
`confirm_password`. Khi thành công, backend đặt `must_change_password = false` và
giữ nguyên phiên. HTTP 400 nếu dữ liệu không hợp lệ; HTTP 401 nếu chưa đăng nhập.

## 5. Đăng xuất

```http
POST /api/logout/
X-CSRFToken: token-value
```

Response 200:

```json
{
  "status": "success",
  "message": "Đã đăng xuất"
}
```

HTTP 401 nếu phiên không hợp lệ. Sau thành công, frontend chuyển về trang đăng nhập.
