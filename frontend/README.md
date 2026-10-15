# Hướng dẫn Frontend tích hợp xác thực

Thư mục `frontend/` chứa giao diện HTML/JavaScript cơ bản. Frontend tiếp tục
hoàn thiện giao diện theo tài liệu này và giao tiếp với Django Backend qua HTTP/JSON.

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5500`
- API chính thức: [`docs/api_contract.md`](../docs/api_contract.md)

Không trộn `localhost` với `127.0.0.1`, vì trình duyệt có thể không gửi đúng
session cookie.

## Các file hiện có

| File | Trách nhiệm |
| --- | --- |
| `api.js` | Gọi API, gửi cookie và CSRF token |
| `login.html` | Đăng nhập và điều hướng theo trạng thái mật khẩu |
| `change-password.html` | Đổi mật khẩu bắt buộc lần đầu |
| `index.html` | Kiểm tra session, hiển thị nhân viên và đăng xuất |

Các endpoint nghiệp vụ `/api/booking/` chưa được triển khai. Frontend chưa nên
giả định dữ liệu đặt phòng ngoài API contract.

## Trạng thái sau lần kiểm tra gần nhất

Frontend đã hoàn thành:

- Giao diện đăng nhập và đổi mật khẩu có CSS chung.
- Cấu trúc HTML đầy đủ, có label và autocomplete.
- Gọi đúng các API đăng nhập, session, đổi mật khẩu và đăng xuất.
- Điều hướng theo `must_change_password`.
- Hiển thị `display_name` trên trang chính.
- Có loading và xử lý lỗi cho thao tác đăng nhập, đổi mật khẩu.

Phần xác thực chưa được nghiệm thu vì các mục trong phần **Yêu cầu còn thiếu** bên
dưới vẫn cần xử lý.

## Dữ liệu người dùng Backend trả về

`POST /api/login/` và `GET /api/session/` trả:

```json
{
  "status": "success",
  "username": "nv01",
  "display_name": "Nguyễn Văn A",
  "must_change_password": true
}
```

- Dùng `username` làm mã tài khoản.
- Dùng `display_name` để hiển thị trên giao diện.
- Dùng `must_change_password` để quyết định trang tiếp theo.

Không lưu mật khẩu hoặc tự ghi trạng thái đăng nhập vào `localStorage`. Session
do Backend xác nhận mới là nguồn dữ liệu chính xác.

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

### `login.html`

1. Gọi `GET /api/session/` khi mở trang.
2. HTTP 401 tại bước này là bình thường: hiển thị form đăng nhập.
3. Gửi `POST /api/login/` với `username` và `password`.
4. Điều hướng theo `must_change_password`.
5. Khóa nút và hiển thị trạng thái đang xử lý trong lúc gửi.

Hiện bước 1 chưa được triển khai. Phải hoàn thành để người đã đăng nhập không nhìn
thấy lại form đăng nhập.

### `change-password.html`

1. Gọi `GET /api/session/` trước khi hiển thị form.
2. HTTP 401: chuyển về `login.html`.
3. `must_change_password=false`: chuyển tới `index.html`.
4. Gửi `POST /api/change-password/` với `new_password` và
   `confirm_password`.
5. Thành công: chuyển tới `index.html`.

### `index.html`

1. Gọi `GET /api/session/` trước khi hiển thị nội dung.
2. HTTP 401: chuyển về `login.html`.
3. `must_change_password=true`: chuyển tới `change-password.html`.
4. Hiển thị `display_name`.
5. Nút đăng xuất gọi `POST /api/logout/`; chỉ chuyển trang sau khi Backend phản hồi.
6. Chưa hiển thị role cho tới khi Backend bổ sung `role` vào API contract.

## Module gọi API

Mọi request phải gửi session cookie. Request POST phải gửi CSRF token:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';
let csrfToken = '';

async function prepareCsrf() {
  const response = await fetch(`${API_BASE_URL}/api/csrf/`, {
    credentials: 'include'
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'Không lấy được CSRF token.');
  }

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

Mỗi trang phải dùng `try/catch/finally` để lỗi mạng không làm nút bị khóa hoặc
giao diện đứng yên.

## Xử lý lỗi

Backend trả lỗi theo cấu trúc:

```json
{
  "status": "error",
  "code": "INVALID_CREDENTIALS",
  "message": "Tên đăng nhập hoặc mật khẩu không đúng."
}
```

Frontend dùng `code` để điều hướng và dùng `message` để hiển thị:

| `code` | Cách xử lý |
| --- | --- |
| `INVALID_CREDENTIALS` | Giữ form đăng nhập và hiển thị lỗi |
| `AUTHENTICATION_REQUIRED` | Chuyển về `login.html` |
| `PASSWORD_CHANGE_REQUIRED` | Chuyển tới `change-password.html` |
| `PASSWORD_REQUIRED` | Hiển thị lỗi trong form đổi mật khẩu |
| `PASSWORD_MISMATCH` | Hiển thị lỗi trong form đổi mật khẩu |
| `CSRF_FAILED` | Lấy token mới; nếu vẫn lỗi thì yêu cầu tải lại trang |
| `INVALID_JSON`, `REQUIRED_FIELDS` | Hiển thị `message` trong form hiện tại |

Middleware Backend chặn toàn bộ `/api/booking/`:

- HTTP 401 nếu chưa đăng nhập.
- HTTP 403 và `PASSWORD_CHANGE_REQUIRED` nếu chưa đổi mật khẩu lần đầu.
- Request chỉ đi tiếp khi session hợp lệ và `must_change_password=false`.

## Yêu cầu còn thiếu cần Frontend xử lý

### 1. Sửa `api.js`

- Bọc mọi lần gọi `response.json()` bằng `try/catch`.
- Trả lỗi `INVALID_RESPONSE` khi máy chủ không trả JSON.
- Kiểm tra `response.ok` khi lấy CSRF token.
- Khi nhận `CSRF_FAILED`, xóa token cũ, lấy token mới và cho phép thử lại.
- Không chỉ xử lý riêng HTTP 500; mọi HTTP status đều phải trả được `data` thống nhất.

Mẫu `apiRequest()` phía trên là hành vi cần triển khai vào file thật, không chỉ để
tham khảo trong README.

### 2. Kiểm tra session khi mở `login.html`

- Gọi `GET /api/session/` trước khi hiển thị form.
- HTTP 401: hiển thị form đăng nhập, không hiện lỗi.
- Session hợp lệ và `must_change_password=true`: chuyển tới trang đổi mật khẩu.
- Session hợp lệ và `must_change_password=false`: chuyển tới trang chính.
- Có trạng thái đang kiểm tra để form không nháy lên trước khi chuyển trang.

### 3. Hoàn thiện kiểm tra ở `change-password.html`

- Ẩn form trong lúc `GET /api/session/` chưa hoàn tất.
- Bọc `checkAccess()` bằng `try/catch` và hiển thị lỗi khi Backend không kết nối.
- Kiểm tra hai mật khẩu khớp nhau trước khi gọi API.
- Xử lý riêng `CSRF_FAILED`; không chỉ rơi vào lỗi chung.

Backend vẫn kiểm tra lại mật khẩu. Validation Frontend chỉ giúp người dùng nhận
phản hồi sớm hơn.

### 4. Hoàn thiện tải trang chính

- Bọc `initializeApp()` bằng `try/catch`.
- Hiển thị thông báo khi Backend không kết nối thay vì để trang trống.
- Chỉ hiện dashboard sau khi session hợp lệ.
- Dùng `display_name`; chỉ dùng `username` làm giá trị dự phòng.

### 5. Sửa luồng đăng xuất

- Dùng `try/catch/finally`.
- Chỉ chuyển về `login.html` khi API đăng xuất thành công hoặc Backend xác nhận
  session đã hết hạn.
- Nếu request thất bại, hiển thị lỗi và mở lại nút để người dùng thử lại.

### 6. Không giả định role và API nghiệp vụ

Backend hiện chưa trả `role`. Xóa giá trị giả:

```javascript
const role = data.role || 'reservation';
```

Không dùng role giả để hiển thị menu như thể đã phân quyền. Nếu giữ màn hình phòng
trống bằng mock data, phải ghi rõ “Dữ liệu minh họa – API chưa triển khai”, không
hard-code mock như dữ liệu thật và không gọi đây là kết quả từ Backend.

### 7. Kiểm tra trước khi gửi pull request

- Thử khi Backend đang chạy và khi Backend bị dừng.
- Thử đăng nhập sai, đổi mật khẩu sai, session hết hạn và đăng xuất thất bại.
- Chạy `git diff --check` và xóa khoảng trắng cuối dòng.
- Trong pull request, liệt kê các luồng đã kiểm tra và ảnh giao diện tương ứng.

## Tiêu chí bàn giao

- Đăng nhập sai hiển thị lỗi mà không tải lại trang.
- Đăng nhập lần đầu chuyển tới trang đổi mật khẩu.
- Đổi mật khẩu thành công và giữ nguyên session.
- Tải lại trang chính vẫn hiển thị đúng `display_name`.
- Người chưa đăng nhập không mở được trang chính.
- Người chưa đổi mật khẩu không gọi được API đặt phòng.
- Đăng xuất xong không truy cập lại được trang riêng tư.
- Lỗi mất kết nối không làm giao diện bị khóa.

## Các bước Frontend tiếp theo sau xác thực

Frontend không cần chờ Backend hoàn thành toàn bộ nghiệp vụ. Sau khi hai bên chốt
contract của từng giai đoạn, Frontend dùng mock JSON đúng cấu trúc để làm song song.

### 1. Tạo khung ứng dụng và phân quyền

- Tạo header, menu, tên nhân viên và nút đăng xuất dùng chung.
- Đọc `role` từ session khi Backend bổ sung trường này.
- Hiển thị menu theo quyền và có trang thông báo không đủ quyền.
- Không tự đặt role hoặc permission trong `localStorage`.

### 2. Hiển thị loại phòng và phòng

- Làm danh sách loại phòng và phòng từ API Backend.
- Tạo component/select loại phòng để dùng lại trong form đặt phòng.
- Có trạng thái loading, danh sách rỗng và tải thất bại.
- Không hard-code tên loại phòng, giá hoặc sức chứa trong JavaScript.

### 3. Làm form yêu cầu đặt phòng

- Nhập thông tin khách, ngày đến, ngày đi, số khách và loại phòng.
- Giữ dữ liệu đã nhập khi Backend trả lỗi validation.
- Khóa nút trong lúc gửi để tránh tạo yêu cầu trùng.
- Làm trang danh sách và chi tiết yêu cầu sau khi API tương ứng sẵn sàng.

### 4. Làm màn hình kiểm tra phòng trống

- Gửi ngày và loại phòng tới API availability.
- Hiển thị số phòng còn lại do Backend trả về.
- Cho nhân viên thay đổi ngày, loại hoặc số lượng rồi kiểm tra lại.
- Không tự tính tồn phòng từ dữ liệu cũ trên trình duyệt.

### 5. Thỏa thuận và xác nhận

- Hiển thị phương án phòng, giá và dịch vụ Backend trả về.
- Có thao tác danh sách chờ hoặc từ chối khi contract đã được chốt.
- Trước khi xác nhận, hiển thị trang tổng hợp để nhân viên kiểm tra.
- Xử lý HTTP 409 bằng cách quay lại bước kiểm tra phòng.

### 6. Xem, sửa và hủy phiếu

- Làm danh sách có tìm kiếm và bộ lọc trạng thái.
- Làm trang chi tiết và lịch sử xử lý.
- Form sửa/hủy phải có bước xác nhận rõ ràng.
- Khi API báo xung đột, giữ dữ liệu đang nhập và hướng dẫn người dùng tải lại.

### 7. Bàn giao lễ tân và báo cáo

- Làm bảng khách đến, khách đi theo ngày.
- Hiển thị empty state và thời điểm dữ liệu được cập nhật.
- Chỉ làm biểu đồ hoặc xuất file khi nhóm đã chốt yêu cầu và định dạng API.

Thứ tự và mốc tích hợp chung nằm trong
[`next_steps_after_auth.md`](../docs/next_steps_after_auth.md). Frontend chỉ bắt đầu
gọi endpoint thật sau khi endpoint đó xuất hiện trong `api_contract.md`.

Cách chạy hai phía nằm tại
[`huong_dan_chay_du_an.md`](../docs/huong_dan_chay_du_an.md). Quy tắc làm việc
với Git nằm tại [`git_workflow.md`](../docs/git_workflow.md).
