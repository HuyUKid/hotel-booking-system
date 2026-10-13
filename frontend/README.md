# Hướng dẫn Frontend tích hợp API xác thực

Thư mục này không chứa giao diện mẫu. Thành viên frontend tự chọn HTML/CSS/JS,
React, Vue hoặc công nghệ khác và tích hợp với backend theo tài liệu này.

Backend phát triển mặc định tại:

```text
http://127.0.0.1:8000
```

Frontend nên chạy tại một trong hai origin đã được backend cho phép:

```text
http://127.0.0.1:5500
http://127.0.0.1:5501
```

Không trộn `localhost` với `127.0.0.1`, vì cookie phiên có thể không được gửi.

## Các màn hình Frontend cần làm

### 1. Trang đăng nhập

Trường nhập:

- `username`: tên đăng nhập.
- `password`: mật khẩu.

Luồng xử lý:

1. Lấy CSRF token từ `GET /api/csrf/`.
2. Gửi `POST /api/login/`.
3. Nếu `must_change_password = true`, chuyển đến trang đổi mật khẩu.
4. Nếu bằng `false`, chuyển đến trang chính của ứng dụng.
5. Nếu HTTP 400/401, hiển thị `message` từ backend.

### 2. Trang đổi mật khẩu bắt buộc

Trường nhập:

- `new_password`.
- `confirm_password`.

Gửi `POST /api/change-password/`. Thành công thì chuyển đến trang chính. Nếu lỗi,
hiển thị `message`; backend sẽ kiểm tra độ mạnh và hai mật khẩu có khớp hay không.

### 3. Kiểm tra phiên khi mở trang riêng tư

Mỗi khi mở trang cần đăng nhập, gọi `GET /api/session/`:

- HTTP 401: chuyển về trang đăng nhập.
- `must_change_password = true`: chuyển sang trang đổi mật khẩu.
- Thành công: dùng `username` để hiển thị tên nhân viên.

Không dùng `localStorage` làm bằng chứng đăng nhập. Backend xác định người dùng từ
session cookie.

### 4. Đăng xuất

Nút đăng xuất gửi `POST /api/logout/`, sau đó chuyển về trang đăng nhập. Vô hiệu
hóa nút trong lúc gửi để tránh thao tác lặp.

## Hàm gọi API tham khảo

Frontend phải gửi cookie bằng `credentials: "include"` và gửi CSRF token cho POST:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';
let csrfToken = '';

async function prepareCsrf() {
  const response = await fetch(`${API_BASE_URL}/api/csrf/`, {
    credentials: 'include'
  });
  const data = await response.json();
  csrfToken = data.csrf_token;
}

async function apiRequest(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const headers = new Headers(options.headers || {});

  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    if (!csrfToken) await prepareCsrf();
    headers.set('X-CSRFToken', csrfToken);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    method,
    headers,
    credentials: 'include'
  });
  const data = await response.json();
  return { response, data };
}
```

Ví dụ đăng nhập:

```javascript
const { response, data } = await apiRequest('/api/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

if (!response.ok) {
  showError(data.message);
} else if (data.must_change_password) {
  goToChangePassword();
} else {
  goToHome();
}
```

## Quy ước lỗi

| HTTP status | Cách xử lý ở frontend |
| --- | --- |
| 200 | Thao tác thành công |
| 400 | Dữ liệu thiếu, sai định dạng hoặc mật khẩu không hợp lệ |
| 401 | Sai tài khoản/mật khẩu hoặc session hết hạn |
| 403 | Thiếu/sai CSRF token hoặc origin chưa được backend cho phép |
| 405 | Gọi sai HTTP method |
| 500 | Báo lỗi hệ thống, không hiển thị stack trace |

## Frontend cần bàn giao lại cho Backend

- Origin phát triển và origin triển khai thật để backend cấu hình CORS/CSRF.
- Tên và đường dẫn các màn hình đăng nhập, đổi mật khẩu và trang chính.
- Cách frontend muốn hiển thị lỗi validation.
- Kết quả thử đủ bốn luồng: đăng nhập đúng, đăng nhập sai, đổi mật khẩu, đăng xuất.
- Log Network của trình duyệt nếu gặp lỗi tích hợp: URL, method, status và response.

Chi tiết request/response chính thức nằm tại `docs/api_contract.md`.
