# Lộ trình sau khi hoàn thành đăng nhập và mật khẩu

Lộ trình này được xây dựng dựa trên
[tài liệu quy trình đặt phòng](reference/quy-trinh-dat-phong.pdf). File PDF trong
repository là bản đã bỏ trang bìa đầu tiên của tài liệu nguồn.

Tài liệu này chia rõ công việc Backend và Frontend sau khi module xác thực hoàn
thành. Hai bên không chờ nhau viết xong toàn bộ; mỗi bước bắt đầu bằng việc chốt
API contract, sau đó làm song song và tích hợp.

## Quy trình phối hợp áp dụng cho mọi bước

1. Cùng đọc nghiệp vụ và thống nhất kết quả người dùng cần đạt được.
2. Frontend liệt kê dữ liệu cần nhập, hiển thị và các trạng thái giao diện.
3. Backend đề xuất URL, method, request, response và mã lỗi.
4. Hai bên cập nhật `docs/api_contract.md` trước khi code.
5. Frontend dùng mock JSON đúng contract; backend xây model/API/test trong app `booking`.
6. Backend bàn giao endpoint cùng dữ liệu mẫu.
7. Frontend thay mock bằng API thật và hai bên kiểm thử luồng hoàn chỉnh.

## Bước 0 — Tích hợp xác thực hiện tại

### Backend

- Chạy đủ 5 API xác thực hiện có.
- Cấu hình đúng frontend origin trong CORS và CSRF.
- Tạo tài khoản nhân viên và `EmployeeProfile` dùng để tích hợp.
- Gửi frontend base URL, tài khoản thử và `api_contract.md`.

### Frontend

- Làm trang đăng nhập, đổi mật khẩu và nút đăng xuất.
- Gọi `/api/session/` trước khi hiển thị trang riêng tư.
- Gửi cookie bằng `credentials: "include"` và CSRF token cho POST.
- Xử lý HTTP 400, 401, 403 và trạng thái backend không kết nối được.

### Hoàn thành khi

Người dùng có thể đăng nhập, bị chuyển sang đổi mật khẩu nếu cần, vẫn giữ phiên
sau khi đổi, mở lại trang vẫn nhận đúng session và đăng xuất được.

## Bước 1 — Khung ứng dụng và phân quyền

### Backend

- Chốt các vai trò: quản trị viên, nhân viên đặt phòng, lễ tân.
- Bổ sung role/permission vào thông tin session hoặc một endpoint hồ sơ nhân viên.
- Kiểm tra quyền tại mọi endpoint nghiệp vụ, không chỉ ẩn nút ở frontend.
- Viết test 401 khi chưa đăng nhập và 403 khi thiếu quyền.

### Frontend

- Tạo layout chung: header, menu, tên nhân viên và đăng xuất.
- Hiển thị menu theo quyền backend trả về.
- Có trang 403 hoặc thông báo không đủ quyền.
- Không lưu quyền tự đặt trong `localStorage`.

### API cần chốt

- Có mở rộng `GET /api/session/` hay tạo `GET /api/me/`.
- Cấu trúc `roles` hoặc `permissions`.
- Quy tắc điều hướng khi không có quyền.

## Bước 2 — Danh mục loại phòng và phòng

### Backend

- Thiết kế model loại phòng: mã, tên, sức chứa, giá cơ bản, trạng thái.
- Thiết kế model phòng: số phòng, loại phòng, trạng thái hoạt động.
- Cung cấp API đọc danh mục cho form đặt phòng.
- Nếu quản trị qua giao diện riêng, cung cấp API thêm/sửa/ngừng hoạt động.
- Tạo migration, Django Admin, dữ liệu mẫu và test validation.

### Frontend

- Làm màn hình danh sách loại phòng/phòng nếu nằm trong phạm vi quản trị.
- Làm select loại phòng tái sử dụng trong các form sau.
- Hiển thị loading, danh sách rỗng và lỗi tải dữ liệu.
- Không hard-code loại phòng hoặc giá trong JavaScript.

### API cần chốt

- `GET /api/booking/room-types/` và cấu trúc từng loại phòng.
- API phòng nếu frontend cần hiển thị phòng cụ thể.
- Quyền nào được thay đổi danh mục.

## Bước 3 — Tiếp nhận yêu cầu đặt phòng

### Backend

- Thiết kế yêu cầu đặt phòng và các dòng loại phòng/số lượng.
- Lưu người tiếp nhận, thời điểm, khách lẻ/đoàn, liên hệ, kỳ lưu trú, nguồn đặt,
  thanh toán, loại đảm bảo và yêu cầu đặc biệt.
- Sinh mã yêu cầu duy nhất.
- Kiểm tra ngày đi sau ngày đến, số khách và số lượng phòng hợp lệ.
- Cung cấp API tạo, xem danh sách và xem chi tiết yêu cầu.

### Frontend

- Làm form theo các trường đã chốt; chia nhóm để nhân viên dễ nhập.
- Làm danh sách, tìm kiếm và trang chi tiết.
- Giữ dữ liệu người dùng đã nhập khi API báo lỗi.
- Chặn gửi lặp trong lúc request đang xử lý.

### API cần chốt

- Request body tạo yêu cầu.
- Response chứa `id`, mã yêu cầu và trạng thái ban đầu.
- Phân trang, tìm kiếm và bộ lọc của danh sách.

## Bước 4 — Kiểm tra khả năng đáp ứng

### Backend

- Xây service tính số phòng còn bán cho mọi đêm từ ngày đến đến trước ngày đi.
- Trừ phòng ngừng hoạt động và các phiếu đặt đã chiếm sức chứa.
- Không nhận overbooking trong phiên bản đầu.
- Viết test cho chồng ngày, ngày đi trùng ngày đến và nhiều loại phòng.

### Frontend

- Gửi ngày đến/ngày đi và hiển thị tồn phòng từng loại.
- Đánh dấu phương án đủ hoặc thiếu phòng.
- Cho phép nhân viên đổi ngày, loại hoặc số lượng rồi kiểm tra lại.
- Không tự tính tồn phòng từ dữ liệu cũ trên trình duyệt.

### API cần chốt

- Endpoint kiểm tra phòng và input tối thiểu.
- Giá trị `total_rooms`, `reserved_rooms`, `available_rooms`.
- HTTP 409 khi dữ liệu thay đổi trước lúc xác nhận.

## Bước 5 — Thỏa thuận và danh sách chờ

### Backend

- Lưu lịch sử các phương án đã đề xuất: loại phòng, số lượng, giá và dịch vụ.
- Hỗ trợ kết quả đang thỏa thuận, danh sách chờ hoặc từ chối.
- Ghi nhân viên, thời điểm và lý do.
- Kiểm tra lại tồn phòng trước khi chấp nhận phương án.

### Frontend

- Hiển thị phương án để nhân viên trao đổi với khách.
- Cho nhập giá thỏa thuận, dịch vụ kèm theo và ghi chú.
- Có thao tác đưa vào danh sách chờ hoặc từ chối kèm xác nhận.
- Hiển thị lịch sử theo thứ tự thời gian.

### API cần chốt

- Endpoint tạo kết quả thỏa thuận.
- Danh sách trạng thái hợp lệ và quy tắc chuyển trạng thái.
- Response khi phòng vừa hết.

## Bước 6 — Tạo và xác nhận phiếu đặt phòng

### Backend

- Chuyển yêu cầu/phương án thành phiếu đặt chính thức trong transaction.
- Kiểm tra tồn phòng lần cuối và ngăn tạo trùng khi frontend retry.
- Lưu giá tại thời điểm đặt, loại đảm bảo, thanh toán và mã phiếu.
- Phiếu xác nhận mới bắt đầu chiếm sức chứa.

### Frontend

- Hiển thị màn hình tổng hợp trước khi xác nhận.
- Cho nhân viên kiểm tra khách, phòng, giá và kỳ lưu trú.
- Xử lý HTTP 409 bằng cách đưa người dùng trở lại bước kiểm tra phòng.
- Hiển thị mã phiếu sau khi thành công; không gửi lại khi tải lại trang.

### API cần chốt

- Endpoint xác nhận từ `request_id` hoặc `negotiation_id`.
- Idempotency hoặc quy tắc ngăn phiếu trùng.
- Response tổng tiền, mã phiếu và trạng thái.

## Bước 7 — Khẳng định, sửa và hủy

### Backend

- Lưu lần liên hệ xác nhận: kênh, thời điểm, nhân viên và nội dung.
- Cho sửa kỳ lưu trú/phòng sau khi kiểm tra tồn phòng mới.
- Cho hủy, giải phóng sức chứa nhưng không xóa lịch sử.
- Lưu người yêu cầu, lý do và phí hủy nếu có.

### Frontend

- Làm chi tiết phiếu và lịch sử liên hệ.
- Làm form sửa/hủy với bước xác nhận rõ ràng.
- Hiển thị phiếu có thể in.
- Thông báo khi sửa không thể đáp ứng và giữ dữ liệu cũ.

### API cần chốt

- API chi tiết, sửa, hủy và ghi nhận liên hệ.
- Quy tắc optimistic locking hoặc xử lý hai nhân viên sửa cùng lúc.
- Các trạng thái cuối và thao tác được phép ở mỗi trạng thái.

## Bước 8 — Bàn giao lễ tân và báo cáo

### Backend

- Tổng hợp khách đến/đi theo ngày, sửa/hủy, không đến, ở thêm và đi sớm.
- Cung cấp báo cáo mật độ phòng theo khoảng thời gian.
- Phân quyền dữ liệu cho lễ tân và quản lý.

### Frontend

- Làm dashboard trong ngày và bộ lọc ngày.
- Hiển thị danh sách có thể in/xuất theo yêu cầu đồ án.
- Cho cập nhật trạng thái thực tế với xác nhận thao tác.
- Có empty state và thông báo dữ liệu được cập nhật lúc nào.

### API cần chốt

- Endpoint arrivals/departures theo ngày.
- Endpoint báo cáo và định dạng dữ liệu biểu đồ/bảng.
- Có cần xuất CSV/PDF từ backend hay frontend hay không.

## Mẫu bàn giao giữa hai bên

Backend báo frontend:

```text
Endpoint: POST /api/example/
Trạng thái: sẵn sàng tích hợp
Auth/quyền: session + booking.add_x
Request mẫu: {...}
Response 200/201: {...}
Các lỗi: 400, 401, 403, 404, 409
Dữ liệu test: ...
Contract đã cập nhật tại: docs/api_contract.md
```

Frontend báo backend:

```text
Màn hình: ...
Hành động người dùng: ...
Dữ liệu cần nhập/hiển thị: ...
Trạng thái UI cần xử lý: loading, empty, error, success
Endpoint còn thiếu hoặc trường cần bổ sung: ...
Origin phát triển: ...
```

Chỉ chuyển sang bước tiếp theo khi contract của bước hiện tại đã được cập nhật,
backend có test và frontend đã chạy được ít nhất một luồng tích hợp hoàn chỉnh.

