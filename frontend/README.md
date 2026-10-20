# Frontend — hướng dẫn làm theo quy trình đặt phòng

Frontend dùng HTML, CSS và JavaScript thuần, giao tiếp với Django bằng HTTP/JSON.
README này hướng dẫn đọc, sửa và tự làm lại giao diện theo 8 bước trong
[PDF nghiệp vụ](../docs/reference/quy-trinh-dat-phong.pdf).

Giao diện hiện lấy dữ liệu thật từ Backend. Sơ đồ tổng thể và kịch bản bấm thử nằm
trong [demo walkthrough](../docs/demo_walkthrough.md).

## 1. Chạy Frontend

Từ thư mục gốc dự án, mở terminal riêng:

```powershell
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```

Mở `http://127.0.0.1:5500/login.html`. Backend cần chạy tại
`http://127.0.0.1:8000`. Không mở HTML bằng `file://`, không trộn hostname
`localhost` với `127.0.0.1`.

Sau khi Backend chạy `seed_demo`, dùng `demo / demo123` rồi đổi mật khẩu lần đầu.
Nếu đã đổi mật khẩu thì dùng mật khẩu mới. Xem [hướng dẫn chạy hai phía](../docs/huong_dan_chay_du_an.md).

## 2. Hiểu các file

| File | Phần cần đọc |
| --- | --- |
| [login.html](login.html) | Form tên đăng nhập, mật khẩu và vùng thông báo |
| [change-password.html](change-password.html) | Form đổi mật khẩu lần đầu |
| [auth.js](auth.js) | Xử lý hai form và điều hướng theo session |
| [index.html](index.html) | Sơ đồ 8 bước và ba khu vực nghiệp vụ |
| [app.js](app.js) | Xử lý sự kiện, gọi API, vẽ danh sách và chi tiết |
| [api.js](api.js) | Cookie, CSRF, đọc JSON, kiểm tra session và thông báo chung |
| [style.css](style.css) | Bố cục, form, bảng, responsive và bản in |

Các thẻ HTML được nối với JavaScript qua `id`, `name` và `data-action`.
Ví dụ form `bookingForm` chứa input `name="customer_name"`; JavaScript đọc tên
trường đó bằng `FormData` rồi gửi JSON cho Backend.

## 3. Phần chuẩn bị — đăng nhập và đổi mật khẩu

`auth.js/initializeAuth()` kiểm tra `GET /api/session/` trước khi hiện form:

- Chưa đăng nhập: hiển thị form login.
- Đã đăng nhập nhưng phải đổi mật khẩu: mở change-password.html.
- Đã đăng nhập và đã đổi mật khẩu: mở index.html.

Khi đăng nhập, gửi username/password tới `POST /api/login/`. Khi đổi mật khẩu,
gửi new_password/confirm_password tới `POST /api/change-password/`.

`api.js` luôn gửi cookie và CSRF cho POST, làm mới token một lần khi nhận
`CSRF_FAILED`. Mỗi thao tác có loading và xử lý lỗi; không dùng localStorage để
tự xác nhận tài khoản đã đăng nhập.

## 4. Ba khu vực trên trang chính

| Khu vực trong index.html | Nội dung |
| --- | --- |
| Tiếp nhận yêu cầu | Form khách/phòng/ngày và kiểm tra khả năng đáp ứng |
| Hồ sơ đặt phòng | Danh sách, chi tiết, thỏa thuận, khẳng định, lịch sử, sửa/hủy |
| Bàn giao lễ tân | Khách dự kiến đến/đi theo ngày |

Các khu vực này được ẩn/hiện bằng `showPage()`, nên bản demo không cần tạo tám
trang HTML riêng cho tám bước.

## 5. Thực hiện 8 bước trên giao diện

### B1. Tiếp nhận yêu cầu

- Form: `bookingForm` trong index.html.
- Nhập khách, điện thoại, ngày giờ, số khách, loại phòng, số lượng, giá, đảm bảo,
  thanh toán và yêu cầu đặc biệt.
- `initializeApp()` tải loại phòng từ `GET /api/booking/room-types/`.
- Khi lưu, submit handler dùng `FormData` rồi gọi `POST /api/booking/bookings/`.
- Backend trả mã phiếu; Frontend mở chi tiết để tiếp tục xử lý.

Không tự gán nhân viên tạo hoặc trạng thái trong JSON.

### B2. Kiểm tra khả năng đáp ứng

- Nút: `checkButton`.
- Hàm: `checkAvailability()`.
- Gọi API availability với ngày đến và ngày đi.
- Hiển thị từng loại phòng còn bao nhiêu và giá gốc.

Frontend không tự tính tồn. Kết quả này chưa giữ chỗ và được Backend kiểm tra
lại khi khẳng định.

### B3. Thỏa thuận với khách

Trong chi tiết phiếu, nhân viên dùng các nút:

- Khách đồng ý: gửi `action=agree`.
- Chờ phòng: gửi `action=wait`.
- Khách không đồng ý: gửi `action=reject`.
- Đổi phương án: sửa ngày/loại/số lượng/giá rồi kiểm tra lại.

`runAction()` gửi hành động; không tự thay status ở trình duyệt.

### B4. Nhập và lưu phiếu thỏa thuận

Khi khách đồng ý, phiếu được Backend cập nhật thành agreed và trả lại dữ liệu.
`renderDetail()` hiển thị mã phiếu, giá thỏa thuận, tổng tiền và lịch sử.

Dữ liệu đã lưu sớm từ B1; không gửi thêm một POST tạo phiếu mới ở B4.

### B5. Khẳng định đặt phòng với khách

- Nhân viên liên hệ khách ngoài hệ thống.
- Chọn kênh, ghi chú và bấm “Đã liên hệ khẳng định với khách”.
- `runAction('confirm')` gửi action/channel/note.
- Thành công: dùng dữ liệu Backend để cập nhật trạng thái.
- HTTP 409: hiện lỗi, giữ phiếu để nhân viên sửa phương án hoặc đưa vào chờ.

Không hiển thị đã khẳng định trước khi API trả thành công. Demo không tự gửi email.

### B6. Lưu và tra cứu

- `loadBookings()`: tải danh sách, tìm theo tên/điện thoại và lọc trạng thái.
- `bookingTable()`: vẽ bảng.
- `openBooking()`: tải chi tiết.
- `renderDetail()`: vẽ thông tin và lịch sử do Backend lưu.

Dùng dữ liệu Backend trả về, không thay dữ liệu thật bằng mock. Nút in gọi
`window.print()`, CSS in nằm trong style.css.

### B7. Khẳng định lại, sửa và hủy

- Khách khẳng định lại: gửi `reconfirm`.
- Sửa: `runAction('edit')` đưa dữ liệu lên form cũ và đặt `editingId`.
- Khi lưu form, nếu có editingId thì gửi `action=edit` thay vì tạo phiếu mới.
- Hủy: hỏi xác nhận, yêu cầu ghi chú người yêu cầu/lý do và gửi `cancel`.
- Lỗi sửa/hủy: hiện thông báo, không xóa nội dung đang nhập.

Chỉ vẽ các nút phù hợp với trạng thái Backend trả về. Backend vẫn kiểm tra lại
trạng thái, dù nút đã được ẩn trên giao diện.

### B8. Bàn giao lễ tân

- Form: `handoverForm`.
- Hàm: `loadHandover()`.
- Gọi `GET /api/booking/handover/?date=...`.
- Hiển thị khách dự kiến đến/đi, số phòng đang dùng dự kiến và số phiếu chờ.

Dữ liệu này chưa phải kết quả nhận/trả phòng thực tế.

## 6. Cách một lần bấm nút đi đến Backend

```text
Người dùng bấm “Khách đồng ý”
→ app.js/runAction('agree')
→ postData(): chuẩn bị JSON
→ api.js/apiRequest(): gửi cookie và CSRF
→ Backend kiểm tra rồi lưu dữ liệu
→ Frontend nhận booking mới
→ renderDetail(): cập nhật trạng thái và lịch sử
```

`requestData()` xử lý HTTP lỗi; `withLoading()` khóa/mở nút và hiển thị lỗi.
Khi session hết hạn thì chuyển tới login; khi phải đổi mật khẩu thì chuyển tới
change-password.

## 7. Chia việc cho hai người Frontend

| Người | File chính | Trách nhiệm |
| --- | --- | --- |
| Giao diện | HTML và style.css | Bố cục, label, trạng thái hiển thị, responsive, bản in |
| Tích hợp | api.js, auth.js, app.js | Sự kiện, JSON, API, session, CSRF, điều hướng và lỗi |

Thống nhất id/name/data-action trước khi sửa. Nếu thay tên phần tử HTML, cập nhật
JavaScript tương ứng trong cùng thay đổi. Nội dung người dùng phải được escape
trước khi đưa vào HTML; dùng textContent nếu chỉ cần hiển thị chữ.

## 8. Thứ tự tự làm lại hoặc thêm màn hình

1. Chọn một hành động nghiệp vụ, đọc API contract tương ứng.
2. Viết HTML tối thiểu và vùng thông báo/loading.
3. Thêm hàm JavaScript gọi API qua module chung.
4. Vẽ response thành dữ liệu trên trang.
5. Thêm xử lý lỗi và mở lại nút khi thất bại.
6. Kiểm thử cùng Backend bằng dữ liệu thật.
7. Chỉ thêm tính năng mới sau khi hai bên thống nhất contract.

Ví dụ học từ dễ đến khó: danh sách loại phòng → kiểm tra tồn → tạo yêu cầu →
chi tiết → thao tác trạng thái → sửa/hủy → bàn giao.

## 9. Checklist trước khi bàn giao

- Đăng nhập đúng/sai, đổi mật khẩu lần đầu, tải lại trang và đăng xuất.
- Backend bị dừng: hiện lỗi và không khóa nút vĩnh viễn.
- Không có dữ liệu: hiện thông báo danh sách rỗng.
- Hết phòng khi khẳng định: giữ phiếu, hiện lỗi 409.
- Sửa phiếu: không tạo thêm phiếu mới.
- Hủy: có xác nhận và ghi chú; sau đó không hiện các thao tác không hợp lệ.
- Màn hình điện thoại không tràn ngang.
- Kiểm tra Network và đối chiếu request/response với Backend.

Role, nhiều loại phòng trong một phiếu và nhận/trả phòng thực tế là phần nâng cấp.
Không tự giả định role khi API chưa trả trường đó.

Xem [API contract](../docs/api_contract.md), [Backend README](../backend/README.md),
[kế hoạch phối hợp](../docs/next_steps_after_auth.md) và [quy tắc Git](../docs/git_workflow.md).
