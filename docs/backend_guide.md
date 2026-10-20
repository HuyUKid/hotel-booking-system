# Kế hoạch phát triển Backend sau xác thực

**Cập nhật bản demo:** app `booking` hiện đã có các file đơn `models.py`,
`services.py`, `views.py`, `urls.py`, `tests.py` và lệnh `seed_demo`. Đọc
[demo_walkthrough.md](demo_walkthrough.md) để học code đang chạy. Tài liệu bên dưới
là kế hoạch mở rộng; cấu trúc package, role và endpoint đề xuất chưa phải tất cả
đã được triển khai. Endpoint thực tế chỉ lấy từ [API contract](api_contract.md).

Tài liệu này chỉ mô tả công việc của Backend. Công việc Frontend nằm trong
[`frontend/README.md`](../frontend/README.md); thứ tự phối hợp và mốc bàn giao
chung nằm trong [`next_steps_after_auth.md`](next_steps_after_auth.md).

Backend tiếp tục phát triển trong app `booking`. Module `authentication` chỉ
chịu trách nhiệm tài khoản, session, đổi mật khẩu và bảo vệ API.

## Nguyên tắc triển khai

Mỗi chức năng Backend thực hiện theo thứ tự:

1. Đọc nghiệp vụ trong PDF và xác định dữ liệu cần lưu.
2. Thống nhất request/response với Frontend trong `api_contract.md`.
3. Tạo hoặc sửa model, sau đó tạo migration mới.
4. Đặt quy tắc nghiệp vụ trong service; view chỉ đọc request và trả response.
5. Kiểm tra session, trạng thái đổi mật khẩu và quyền.
6. Viết test cho thành công, dữ liệu sai, chưa đăng nhập và xung đột nghiệp vụ.
7. Chuẩn bị dữ liệu thử và bàn giao endpoint cho Frontend.

Không sửa migration đã được chia sẻ. Không đổi endpoint hoặc tên trường mà chưa
cập nhật API contract.

## Cấu trúc đề xuất cho app booking

```text
backend/booking/
├── models/
│   ├── room.py
│   ├── customer.py
│   ├── booking.py
│   └── negotiation.py
├── services/
│   ├── availability.py
│   ├── booking_service.py
│   └── pricing.py
├── views/
│   ├── room_views.py
│   ├── booking_views.py
│   └── report_views.py
├── tests/
│   ├── test_rooms.py
│   ├── test_availability.py
│   └── test_bookings.py
├── admin.py
└── urls.py
```

Có thể bắt đầu bằng các file đơn hiện tại rồi tách thành package khi code lớn hơn.
Không cần tạo toàn bộ cấu trúc ngay từ đầu.

## Giai đoạn 1 — Vai trò nhân viên

### Backend làm

- Thêm `role` vào `EmployeeProfile`.
- Bắt đầu với ba vai trò: `admin`, `booking_staff`, `receptionist`.
- Trả `role` trong `GET /api/session/`.
- Tạo hàm hoặc decorator kiểm tra quyền cho API nghiệp vụ.
- Viết migration và test HTTP 403 khi tài khoản không đủ quyền.

### API cần cập nhật

```json
{
  "status": "success",
  "username": "nv01",
  "display_name": "Nguyễn Văn A",
  "role": "booking_staff",
  "must_change_password": false
}
```

### Bàn giao cho Frontend

- Danh sách role chính thức.
- Quyền của từng role.
- Response session mới và tài khoản thử cho mỗi role.

## Giai đoạn 2 — Danh mục loại phòng và phòng

### Model tối thiểu

`RoomType`:

- `code`, `name`, `capacity`, `base_price`, `is_active`.

`Room`:

- `room_number`, `room_type`, `status`.

Trạng thái vận hành phòng chỉ cần `available`, `maintenance`, `inactive`.
Tình trạng trống theo ngày được tính bởi service, không lưu trực tiếp vào
`Room.status`.

### API đề xuất

```text
GET /api/booking/room-types/
GET /api/booking/rooms/
```

Nếu quản trị danh mục qua Django Admin thì giai đoạn đầu chưa cần API thêm, sửa,
xóa cho Frontend.

### Test bắt buộc

- Mã loại phòng và số phòng không trùng.
- Giá và sức chứa hợp lệ.
- Phòng liên kết đúng loại phòng.
- Tài khoản chưa đăng nhập hoặc chưa đổi mật khẩu không truy cập được.

## Giai đoạn 3 — Tiếp nhận yêu cầu đặt phòng

### Model tối thiểu

- `Customer`: họ tên, điện thoại, email và ghi chú.
- `BookingRequest`: khách hàng, ngày đến, ngày đi, số khách, trạng thái, người tạo.
- `BookingRequestItem`: loại phòng và số lượng yêu cầu.

### API đề xuất

```text
POST /api/booking/requests/
GET  /api/booking/requests/
GET  /api/booking/requests/<id>/
```

### Validation bắt buộc

- Ngày đi phải sau ngày đến.
- Số khách và số lượng phòng phải lớn hơn 0.
- Loại phòng phải đang hoạt động.
- Lưu `created_by` từ session; không nhận ID nhân viên do Frontend tự gửi.

## Giai đoạn 4 — Kiểm tra phòng trống

Tạo service `availability.py` để tính số phòng còn trống cho từng đêm. Service
phải loại trừ phòng bảo trì và các phiếu đã xác nhận có khoảng ngày giao nhau.

API đề xuất:

```text
GET /api/booking/availability/?check_in=...&check_out=...&room_type=...
```

Không để view hoặc Frontend tự tính tồn phòng. Viết test cho khoảng ngày chồng
nhau, ngày trả trùng ngày nhận tiếp theo và nhiều loại phòng.

## Giai đoạn 5 — Thỏa thuận và danh sách chờ

Backend lưu phương án đã đề xuất, giá, ghi chú, nhân viên và thời gian. Trạng thái
tối thiểu:

```text
pending → negotiating → waiting
                     ↘ rejected
```

Mỗi lần chuyển trạng thái phải được service kiểm tra. Frontend không được gửi một
trạng thái tùy ý để Backend lưu trực tiếp.

## Giai đoạn 6 — Xác nhận đặt phòng

Tạo phiếu đặt chính thức trong `transaction.atomic()`:

1. Khóa hoặc kiểm tra lại dữ liệu tồn phòng.
2. Ngăn tạo phiếu trùng khi Frontend gửi lại request.
3. Lưu giá tại thời điểm xác nhận.
4. Sinh mã phiếu duy nhất.
5. Chuyển trạng thái sang `confirmed`.

Nếu phòng vừa hết, trả HTTP 409 để Frontend quay lại bước kiểm tra khả năng đáp ứng.

## Giai đoạn 7 — Xem, sửa và hủy

API đề xuất:

```text
GET   /api/booking/reservations/
GET   /api/booking/reservations/<id>/
PATCH /api/booking/reservations/<id>/
POST  /api/booking/reservations/<id>/cancel/
```

Không xóa bản ghi đã phát sinh nghiệp vụ. Khi hủy, lưu người thực hiện, thời gian,
lý do và giải phóng sức chứa.

## Giai đoạn 8 — Bàn giao lễ tân và báo cáo

Chỉ triển khai sau khi luồng đặt phòng chính hoạt động. Backend cung cấp danh sách
khách đến, khách đi và số liệu phòng theo ngày. Chốt trước với Frontend định dạng
bảng hoặc biểu đồ; chưa cần xuất PDF/CSV nếu đồ án không yêu cầu.

## Làm song song với Frontend

Trong mỗi giai đoạn:

1. Backend và Frontend chốt contract.
2. Backend viết model, service, API và test.
3. Frontend dùng JSON mẫu để làm giao diện.
4. Backend gửi endpoint cùng dữ liệu thử.
5. Frontend thay mock bằng API thật.
6. Hai bên kiểm thử một luồng hoàn chỉnh trước khi merge.

Backend không cần chờ Frontend hoàn thiện giao diện của giai đoạn trước. Backend
chỉ cần chờ khi request/response hoặc quy tắc nghiệp vụ chưa được thống nhất.

## Kiểm tra trước khi bàn giao

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
```

Backend bàn giao cho Frontend:

- Endpoint và method.
- Request/response mẫu.
- Mã lỗi và HTTP status.
- Migration cần chạy.
- Tài khoản, role và dữ liệu thử.
- Commit hoặc pull request chứa thay đổi.

