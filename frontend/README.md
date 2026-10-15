# Hướng dẫn Frontend hoàn thiện luồng đăng nhập

Thư mục `frontend/` đã có bản HTML/JavaScript cơ bản. Frontend cần hoàn thiện luồng
dưới đây mà không cần đổi sang framework khác. API chính thức được mô tả trong
[`api_contract.md`](../docs/api_contract.md).

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

## Luồng điều hướng bắt buộc

```text
Mở login.html
├── session hợp lệ, phải đổi mật khẩu → change-password.html
├── session hợp lệ, đã đổi mật khẩu  → index.html
└── chưa đăng nhập                   → hiển thị form đăng nhập

Đăng nhập thành công
├── must_change_password = true      → change-password.html
└── must_change_password = false     → index.html
```

Frontend phải coi `GET /api/session/` là nguồn xác nhận trạng thái đăng nhập;
không dùng `localStorage` để tự ghi rằng người dùng đã đăng nhập.

Backend hiện đã hỗ trợ đầy đủ năm endpoint xác thực trong tài liệu. Middleware
cũng đã bảo vệ prefix `/api/booking/`, nhưng các endpoint nghiệp vụ đặt phòng chưa
được xây dựng; Frontend chưa nên giả định dữ liệu đặt phòng ngoài API contract.

## Những việc Frontend cần làm

### 1. Hoàn thiện `api.js`

- Luôn gửi `credentials: "include"`.
- Tự lấy và gửi `X-CSRFToken` cho POST.
- Bọc `response.json()` trong `try/catch` vì response lỗi có thể không phải JSON.
- Trả lỗi kết nối thống nhất để mọi trang cùng hiển thị được.
- Dùng `data.code` cho điều hướng và `data.message` để hiển thị.

### 2. Hoàn thiện `login.html`

- Gọi `/api/session/` khi mở trang; người đã đăng nhập không cần thấy lại form.
- Khóa nút và hiển thị “Đang đăng nhập…” trong lúc gửi.
- Có `try/catch/finally` để lỗi mạng không làm nút bị khóa.
- Điều hướng theo `must_change_password` sau khi đăng nhập.
- Thêm `label`, `autocomplete="username"` và `autocomplete="current-password"`.

### 3. Hoàn thiện `change-password.html`

- Gọi `/api/session/` trước khi hiển thị form.
- HTTP 401 chuyển về `login.html`.
- Nếu `must_change_password=false`, chuyển tới `index.html`.
- Kiểm tra hai ô khớp nhau trước khi gửi, nhưng vẫn hiển thị lỗi Backend trả về.
- Có loading, xử lý lỗi mạng và mở lại nút khi thất bại.
- Không dùng `alert()`; hiển thị thông báo ngay trong trang.

### 4. Hoàn thiện `index.html`

- Gọi `/api/session/` trước khi hiển thị nội dung.
- Dùng `display_name` để chào nhân viên; `username` là mã đăng nhập.
- HTTP 401 chuyển về trang đăng nhập.
- `PASSWORD_CHANGE_REQUIRED` hoặc `must_change_password=true` chuyển tới trang
  đổi mật khẩu.
- Khi đăng xuất thất bại, hiển thị lỗi và mở lại nút để người dùng thử lại.

## Cách xử lý mã lỗi từ Backend

| `data.code` | Frontend cần làm |
| --- | --- |
| `INVALID_CREDENTIALS` | Giữ form đăng nhập và hiển thị `message` |
| `AUTHENTICATION_REQUIRED` | Chuyển tới `login.html`, trừ lần kiểm tra session ngay trên trang đăng nhập |
| `PASSWORD_CHANGE_REQUIRED` | Chuyển tới `change-password.html` |
| `PASSWORD_REQUIRED` | Hiển thị lỗi tại form đổi mật khẩu |
| `PASSWORD_MISMATCH` | Hiển thị lỗi tại form đổi mật khẩu |
| `CSRF_FAILED` | Lấy CSRF token mới; nếu vẫn lỗi thì báo người dùng tải lại trang |
| `INVALID_JSON` hoặc `REQUIRED_FIELDS` | Hiển thị `message` tại form hiện tại |

HTTP 401 từ lần gọi `/api/session/` khi mở `login.html` là trạng thái bình thường:
người dùng chưa có phiên nên Frontend chỉ cần hiển thị form, không hiện cảnh báo.

### 5. Giao diện tối thiểu

- Tạo một file CSS dùng chung, form căn giữa và hiển thị tốt trên điện thoại.
- Thông báo lỗi rõ ràng, không làm tải lại cả trang.
- Nút có trạng thái mặc định, đang xử lý và bị vô hiệu hóa.
- `change-password.html` và `index.html` cần đầy đủ `DOCTYPE`, `head`, charset và
  viewport như `login.html`.

## Sản phẩm Frontend cần bàn giao

- Trang đăng nhập có trạng thái đang gửi và vùng hiển thị lỗi.
- Trang đổi mật khẩu bắt buộc.
- Trang chính tạm thời để chứng minh phiên đăng nhập hoạt động.
- Nút đăng xuất.
- Một module gọi API dùng chung, luôn gửi session cookie và CSRF token đúng cách.
- Cơ chế bảo vệ trang riêng tư bằng `GET /api/session/`.

Không lưu mật khẩu, CSRF token hoặc trạng thái “đã đăng nhập” vào mã nguồn.
Session do backend xác nhận mới là nguồn dữ liệu chính xác.

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
hiển thị `message`; backend chỉ kiểm tra mật khẩu không rỗng và hai ô có khớp nhau.

### 3. Kiểm tra phiên khi mở trang riêng tư

Mỗi khi mở trang cần đăng nhập, gọi `GET /api/session/`:

- HTTP 401: chuyển về trang đăng nhập.
- `must_change_password = true`: chuyển sang trang đổi mật khẩu.
- Thành công: dùng `display_name` để hiển thị tên nhân viên.

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
  let data;
  try {
    data = await response.json();
  } catch {
    data = {
      status: 'error',
      code: 'INVALID_RESPONSE',
      message: 'Máy chủ trả về dữ liệu không hợp lệ.'
    };
  }
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
| 403 | CSRF sai hoặc tài khoản chưa hoàn thành đổi mật khẩu |
| 405 | Gọi sai HTTP method |
| 500 | Báo lỗi hệ thống, không hiển thị stack trace |

## Frontend cần bàn giao lại cho Backend

- Origin phát triển và origin triển khai thật để backend cấu hình CORS/CSRF.
- Tên và đường dẫn các màn hình đăng nhập, đổi mật khẩu và trang chính.
- Cách frontend muốn hiển thị lỗi validation.
- Kết quả thử đủ bốn luồng: đăng nhập đúng, đăng nhập sai, đổi mật khẩu, đăng xuất.
- Log Network của trình duyệt nếu gặp lỗi tích hợp: URL, method, status và response.

## Tiêu chí hoàn thành

- Đăng nhập đúng và chuyển trang theo `must_change_password`.
- Đăng nhập sai hiển thị thông báo từ backend, không tải lại cả trang.
- Tải lại trang vẫn nhận ra session hiện tại.
- Người chưa đăng nhập không vào được trang riêng tư.
- Đổi mật khẩu thành công và vẫn giữ phiên đăng nhập.
- Đăng xuất xong không truy cập lại được trang riêng tư.
- Giao diện khóa nút trong lúc gửi và không gửi trùng request.

Chi tiết request/response chính thức nằm tại
[`api_contract.md`](../docs/api_contract.md). Cách chạy hai phía nằm tại
[`huong_dan_chay_du_an.md`](../docs/huong_dan_chay_du_an.md). Quy tắc tạo nhánh,
commit và phối hợp mã nguồn nằm tại
[`git_workflow.md`](../docs/git_workflow.md).
