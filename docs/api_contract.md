# API Contract — Xác thực nhân viên

Base URL phát triển: `http://127.0.0.1:8000`.

Frontend gửi mọi request với `credentials: "include"`. Các request POST phải có
header `X-CSRFToken` lấy từ endpoint CSRF.

## Response lỗi chung

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Nội dung lỗi có thể hiển thị cho người dùng."
}
```

Frontend dùng `code` để quyết định điều hướng và dùng `message` để hiển thị. Không
so sánh trực tiếp nội dung tiếng Việt của `message`.

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
  "username": "nv01",
  "display_name": "Nguyễn Văn A",
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
  "username": "nv01",
  "display_name": "Nguyễn Văn A",
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

## 6. Quy tắc truy cập API đặt phòng

Mọi endpoint dưới `/api/booking/` đều được Backend bảo vệ:

- HTTP 401, `AUTHENTICATION_REQUIRED`: chưa đăng nhập hoặc session hết hạn.
- HTTP 403, `PASSWORD_CHANGE_REQUIRED`: đã đăng nhập nhưng chưa đổi mật khẩu lần đầu.
- Chỉ khi đã đăng nhập và `must_change_password=false`, request mới đi tiếp đến
  API nghiệp vụ.

## Mã lỗi xác thực

| Code | HTTP | Ý nghĩa |
| --- | --- | --- |
| `INVALID_JSON` | 400 | Body không phải object JSON hợp lệ |
| `REQUIRED_FIELDS` | 400 | Thiếu username hoặc password |
| `PASSWORD_REQUIRED` | 400 | Mật khẩu mới bị trống |
| `PASSWORD_MISMATCH` | 400 | Hai mật khẩu mới không khớp |
| `INVALID_CREDENTIALS` | 401 | Username hoặc mật khẩu sai |
| `AUTHENTICATION_REQUIRED` | 401 | Chưa đăng nhập hoặc session hết hạn |
| `CSRF_FAILED` | 403 | CSRF token hoặc origin không hợp lệ |
| `PASSWORD_CHANGE_REQUIRED` | 403 | Phải đổi mật khẩu trước khi dùng nghiệp vụ |
