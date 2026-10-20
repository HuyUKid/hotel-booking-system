# API Contract — Xác thực và demo đặt phòng

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

## 7. API demo đặt phòng

Các API dưới đây đã được triển khai. Đây là contract của bản demo đơn giản,
thay cho các endpoint `requests/`, `reservations/` còn ở mức đề xuất trong kế hoạch
nâng cấp. Toàn bộ API nghiệp vụ yêu cầu session hợp lệ và đã đổi mật khẩu lần đầu.

| Method | URL | Response thành công |
| --- | --- | --- |
| GET | `/api/booking/room-types/` | `{status, items: [{id, name, capacity, total_rooms, nightly_price}]}` |
| GET | `/api/booking/availability/?check_in=2026-11-01&check_out=2026-11-03` | `{status, items: [{room_type_id, name, total_rooms, available_rooms, nightly_price}]}` |
| GET | `/api/booking/bookings/?q=An&status=confirmed` | `{status, items: [Booking]}`; q tìm tên/điện thoại, status là tùy chọn |
| POST | `/api/booking/bookings/` | HTTP 201, `{status, booking: Booking}` |
| GET | `/api/booking/bookings/1/` | `{status, booking: Booking}` kèm lịch sử |
| POST | `/api/booking/bookings/1/actions/` | `{status, booking: Booking}` kèm lịch sử |
| GET | `/api/booking/handover/?date=2026-11-01` | `{status, date, arrivals: [Booking], departures: [Booking], staying_rooms, waiting_count}` |

Request tạo phiếu (một loại phòng/phiếu):

```json
{
  "customer_name": "Nguyễn An",
  "phone": "0901234567",
  "email": "",
  "address": "Hà Nội",
  "group_name": "",
  "source": "Điện thoại",
  "arrival_time": "14:00",
  "check_in": "2026-11-01",
  "check_out": "2026-11-03",
  "guests": 3,
  "room_type_id": 1,
  "quantity": 2,
  "nightly_price": "500000",
  "guaranteed": false,
  "payment_method": "Tiền mặt",
  "notes": "Cần phòng yên tĩnh"
}
```

Các trường bắt buộc: tên khách, điện thoại, hai ngày, số khách, loại phòng, số lượng
và giá. Các trường chữ còn lại có thể để trống. Giờ đến mặc định 14:00;
`guaranteed` mặc định false. Backend tự lưu nhân viên từ session, không nhận
`created_by` hay trạng thái do Frontend tự đặt.

`Booking` gồm các trường dữ liệu trên cùng `id`, `code` (ví dụ DP00001),
`room_type_name`, `status`, `status_label`, `total_price`, `created_by`,
`confirmation_channel`, `reconfirmed_at`. API chi tiết/tạo/thao tác có thêm
`events: [{description, actor, at}]`. Tiền ở phiếu và availability trả dạng chuỗi
số nguyên VND; giá trong room-types được Django serialize từ Decimal. Ngày ở dạng
YYYY-MM-DD; thời điểm lịch sử ở dạng ISO 8601.

Request thao tác:

```json
{"action": "confirm", "channel": "Điện thoại", "note": "Đã gọi khách An"}
```

| action | Điều kiện / kết quả |
| --- | --- |
| `agree` | pending/waiting → agreed; khách đồng ý phương án, lưu phiếu |
| `wait` | pending/waiting/agreed → waiting |
| `reject` | pending/waiting/agreed → rejected |
| `confirm` | agreed → confirmed; bắt buộc channel là Điện thoại, Email hoặc Trực tiếp; kiểm tra lại tồn |
| `reconfirm` | confirmed; ghi thời điểm khách khẳng định lại |
| `edit` | Gửi toàn bộ trường như request tạo; giữ trạng thái, kiểm tra tồn nếu đã confirmed, xóa mốc khẳng định lại |
| `cancel` | Phiếu chưa kết thúc → cancelled; note bắt buộc chứa người yêu cầu/lý do |

Phiếu cancelled/rejected không sửa hoặc xử lý tiếp. Lặp confirm trả 409,
không tạo phiếu hay chiếm phòng lần thứ hai. Chỉ confirmed chiếm tồn phòng;
availability không giữ chỗ. Danh sách được sắp theo ngày đến rồi tên khách.

Lỗi nghiệp vụ:

| code | HTTP | Ý nghĩa |
| --- | --- | --- |
| `INVALID_DATA` | 400 | Ngày, số lượng, sức chứa, giá hoặc dữ liệu nhập không hợp lệ |
| `INVALID_JSON` | 400 | Body không phải object JSON |
| `NOT_FOUND` | 404 | Không có phiếu |
| `INVALID_STATE` | 409 | Thao tác không phù hợp trạng thái |
| `NO_AVAILABILITY` | 409 | Không đủ phòng khi xác nhận/sửa; phiếu cũ được giữ nguyên |

Ngày đi phải sau ngày đến và không quá 365 đêm. Số lượng/số khách là số nguyên
dương, giá là số nguyên VND không âm. Tổng tiền = số đêm × số phòng × giá một đêm.
Bàn giao chỉ bao gồm phiếu confirmed; đây là dự kiến, chưa phải tình trạng lưu trú thực tế.
