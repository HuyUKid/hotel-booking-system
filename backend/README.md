# Backend — hướng dẫn làm theo quy trình đặt phòng

Backend dùng Django và SQLite, xử lý xác thực, dữ liệu và quy tắc đặt phòng.
README này hướng dẫn đọc và tự phát triển bản demo hiện tại theo 8 bước trong
[PDF nghiệp vụ](../docs/reference/quy-trinh-dat-phong.pdf).

Đăng nhập là phần chuẩn bị trước nghiệp vụ. Bản demo dùng một loại phòng cho mỗi
phiếu; phạm vi giản lược được mô tả trong [sơ đồ demo](../docs/demo_walkthrough.md).
Request/response đầy đủ lấy từ [API contract](../docs/api_contract.md).

## 1. Chạy Backend

Từ thư mục gốc dự án, lần đầu chạy:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_demo
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Nếu đã có môi trường ảo thì bỏ hai lệnh tạo venv/cài thư viện khi không cần cài lại.
Lệnh `seed_demo` tạo hai loại phòng và tài khoản `demo / demo123`. Khi chạy lại,
lệnh giữ mật khẩu và dữ liệu đã có. Nhân viên demo phải đổi mật khẩu lần đầu.

Muốn vào Django Admin, tạo tài khoản quản trị ở terminal khác:

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

Mở `http://127.0.0.1:8000/admin/`. Tài khoản nhân viên thông thường không có
quyền vào Admin. Cách chạy cả hai phía nằm trong [hướng dẫn chạy](../docs/huong_dan_chay_du_an.md).

## 2. Hiểu cấu trúc trước khi làm

| File | Cần hiểu và sửa gì? |
| --- | --- |
| [config/settings.py](config/settings.py) | Database, ứng dụng, middleware, origin Frontend được phép |
| [config/urls.py](config/urls.py) | Gắn URL xác thực và URL đặt phòng |
| [authentication/models.py](authentication/models.py) | Profile và cờ bắt buộc đổi mật khẩu |
| [authentication/signals.py](authentication/signals.py) | Tự tạo profile khi có User mới |
| [authentication/apps.py](authentication/apps.py) | Đăng ký signal qua `ready()` |
| [authentication/views.py](authentication/views.py) | CSRF, login, session, đổi mật khẩu, logout |
| [authentication/middleware.py](authentication/middleware.py) | Chặn nghiệp vụ khi chưa đăng nhập/chưa đổi mật khẩu |
| [booking/models.py](booking/models.py) | `RoomType`, `Booking`, `BookingEvent` |
| [booking/services.py](booking/services.py) | Validation, tính tồn và chuyển trạng thái |
| [booking/views.py](booking/views.py) | Đọc JSON, gọi service và trả JSON |
| [booking/urls.py](booking/urls.py) | Định tuyến API nghiệp vụ |
| [booking/admin.py](booking/admin.py) | Đăng ký model để xem trong Admin |
| [booking/tests.py](booking/tests.py) | Kiểm tra luồng, tồn phòng, lỗi và quyền truy cập |
| [seed_demo.py](booking/management/commands/seed_demo.py) | Tạo dữ liệu thử mà không ghi đè dữ liệu cũ |

Luồng xử lý cần nhớ:

```text
Frontend gửi HTTP → urls.py → views.py → services.py → models.py/SQLite
Frontend nhận JSON ← views.py ← kết quả xử lý nghiệp vụ
```

View không chứa toàn bộ nghiệp vụ. Service không quyết định cách vẽ giao diện.

## 3. Phần chuẩn bị — xác thực

1. Quản trị viên tạo User nhân viên bằng Admin hoặc `User.objects.create_user()`.
2. Signal tự tạo `EmployeeProfile(must_change_password=True)`.
3. Frontend gọi `GET /api/csrf/`, sau đó `POST /api/login/`.
4. Backend tạo session và trả `username`, `display_name`, `must_change_password`.
5. Nhân viên gọi `POST /api/change-password/` để bỏ cờ bắt buộc đổi.
6. Các API `/api/booking/` mới cho phép sử dụng.

Superuser mới nhận cờ bằng false. Mật khẩu mới hiện chỉ được kiểm tra không rỗng
và khớp xác nhận theo yêu cầu dự án. Dùng `set_password()` để băm mật khẩu;
không gán mật khẩu trực tiếp vào `user.password`.

Session cookie xác nhận tài khoản; CSRF bảo vệ POST; CORS cho phép origin
Frontend đọc response. Không tắt CSRF để xử lý lỗi tích hợp.

## 4. Thực hiện 8 bước nghiệp vụ trong code

### B1. Tiếp nhận yêu cầu

- Model: `Booking` lưu khách, liên hệ, ngày giờ đến, ngày đi, phòng, giá, đảm bảo,
  thanh toán và yêu cầu đặc biệt.
- API: `POST /api/booking/bookings/`.
- View `bookings()` đọc JSON rồi gọi `create_booking()`.
- `booking_fields()` kiểm tra trường nhập, khoảng ngày, giá và sức chứa.
- Backend gắn `created_by` từ session, tạo trạng thái `pending`, ghi lịch sử.

Không nhận trạng thái hoặc ID nhân viên tự đặt từ Frontend.

### B2. Kiểm tra khả năng đáp ứng

- API: `GET /api/booking/availability/?check_in=...&check_out=...`.
- Service: `available_rooms()`.
- Tính từng đêm, trừ số lượng phòng của các phiếu `confirmed`.
- Ngày trả không chiếm phòng, nên trả ngày 03 và nhận ngày 03 không xung đột.

Kết quả kiểm tra chỉ là tồn tại thời điểm gọi, chưa giữ phòng cho khách.

### B3. Thỏa thuận hoặc chờ/từ chối

Dùng `POST /api/booking/bookings/<id>/actions/` và `process_booking()`:

- `agree`: khách đồng ý phương án, chuyển sang `agreed`.
- `wait`: đưa vào `waiting`.
- `reject`: chuyển sang `rejected`.
- Nếu khách đổi ngày/loại phòng, dùng `edit` để lưu phương án mới rồi kiểm tra lại.

Service quyết định chuyển trạng thái hợp lệ; Frontend chỉ gửi hành động.

### B4. Nhập và lưu phiếu thỏa thuận

Dữ liệu đã lưu sớm từ B1 để không mất yêu cầu. Khi nhận `agree`, Backend cập nhật
phiếu hiện có thành `agreed` và ghi lịch sử, không tạo bản sao.

Giá thỏa thuận, thanh toán và yêu cầu đặc biệt được sửa bằng hành động `edit`.
Mã phiếu có dạng `DP00001`.

### B5. Khẳng định đặt phòng với khách

- Nhân viên liên hệ khách rồi gửi `action=confirm`, kênh liên hệ và ghi chú.
- Backend chỉ nhận confirm từ trạng thái `agreed`.
- Trong transaction, Backend kiểm tra lại tồn trước khi lưu `confirmed`.
- Không đủ phòng: trả `409 / NO_AVAILABILITY`, không làm mất phiếu cũ.
- Phiếu confirmed bắt đầu chiếm phòng; gửi confirm lần nữa không chiếm thêm.

Demo chỉ ghi nhận việc nhân viên đã liên hệ, chưa tự gửi email hoặc gọi điện.

### B6. Lưu và tra cứu hồ sơ

- `GET /api/booking/bookings/`: sắp ngày đến rồi tên khách, hỗ trợ q và status.
- `GET /api/booking/bookings/<id>/`: thông tin chi tiết và lịch sử.
- `booking_data()` chuyển model thành dữ liệu JSON.
- `BookingEvent` lưu nhân viên, thời gian và nội dung xử lý.

B6 sử dụng dữ liệu đã được lưu xuyên suốt; không cần một bảng hồ sơ trùng phiếu.

### B7. Nhận khẳng định lại, sửa hoặc hủy

- `reconfirm`: ghi thời điểm khách khẳng định lại phiếu confirmed.
- `edit`: gửi đầy đủ dữ liệu phiếu, kiểm tra tồn lại nếu phiếu đã confirmed.
- Sửa thành công sẽ xóa mốc khẳng định lại và ghi rõ trường thay đổi trong lịch sử.
- `cancel`: yêu cầu ghi chú người yêu cầu/lý do, đổi thành cancelled và giải phóng phòng.
- Phiếu cancelled hoặc rejected không sửa tiếp.

Không xóa phiếu để hủy. Khi sửa thất bại, transaction giữ nguyên dữ liệu cũ.

### B8. Tổng hợp và bàn giao lễ tân

- API: `GET /api/booking/handover/?date=YYYY-MM-DD`.
- View: `handover()`.
- Trả khách dự kiến đến/đi, số phòng dự kiến sử dụng và số phiếu chờ.
- Chỉ phiếu confirmed xuất hiện trong danh sách đến/đi.

Chưa xử lý check-in/check-out thực tế, no-show, ở thêm và đi sớm.

## 5. Thứ tự tự làm lại hoặc sửa một chức năng

1. Chọn một bước nghiệp vụ nhỏ và thống nhất API với Frontend.
2. Xem model đã có đủ dữ liệu chưa; nếu đổi model, tạo migration mới.
3. Viết validation và quy tắc trong `services.py`.
4. Viết view nhận JSON/gọi service/trả JSON.
5. Thêm đường dẫn trong `urls.py`.
6. Viết test trường hợp đúng, dữ liệu sai và trạng thái không hợp lệ.
7. Cập nhật API contract và bàn giao dữ liệu mẫu cho Frontend.

Ví dụ “Khách đồng ý” đi theo:
`app.js/runAction()` → `booking_action()` → `process_booking()`
→ lưu `Booking` và `BookingEvent` → JSON → Frontend cập nhật chi tiết.

## 6. Kiểm tra trước khi bàn giao

Chạy tại thư mục `backend`:

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
```

Bàn giao endpoint, request/response, mã lỗi, migration và dữ liệu thử. Khi lỗi tích
hợp, cùng Frontend xem URL/method/status/response trong Network; không đoán theo
thông báo giao diện.

## 7. Phạm vi và tài liệu tiếp theo

Bản demo dùng chung quyền thao tác cho nhân viên đã đổi mật khẩu, một loại phòng
mỗi phiếu, chưa thu tiền, chưa quản lý từng số phòng hay chính sách giữ phòng tự động.

- [Demo walkthrough](../docs/demo_walkthrough.md): sơ đồ, kịch bản thử và giới hạn.
- [API contract](../docs/api_contract.md): nguồn request/response chính thức.
- [Backend guide](../docs/backend_guide.md): kế hoạch nâng cấp sau demo.
- [Frontend README](../frontend/README.md): giao diện tương ứng với từng bước.
- [Git workflow](../docs/git_workflow.md): phối hợp mã nguồn.
