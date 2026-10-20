# Kế hoạch phối hợp sau xác thực

**Hiện trạng:** đã có bản demo xuyên suốt 8 bước ở mức giản lược. Xem
[sơ đồ và kịch bản demo](demo_walkthrough.md) và [API contract](api_contract.md).
Các giai đoạn bên dưới là kế hoạch nâng cấp từ demo, bao gồm phân quyền và quản lý
phòng chi tiết; không phải danh sách chức năng đều còn trống.

Kế hoạch này dựa trên
[tài liệu quy trình đặt phòng](reference/quy-trinh-dat-phong.pdf). File này chỉ
quy định thứ tự phối hợp và kết quả bàn giao chung, không lặp hướng dẫn kỹ thuật:

- Công việc chi tiết của Backend: [`backend_guide.md`](backend_guide.md).
- Công việc chi tiết của Frontend: [`frontend/README.md`](../frontend/README.md).
- Request/response chính thức: [`api_contract.md`](api_contract.md).

## Nguyên tắc phối hợp

1. Hai bên thống nhất nghiệp vụ và API trước khi code.
2. Backend và Frontend làm song song dựa trên cùng API contract.
3. Frontend dùng mock JSON trong khi Backend chưa bàn giao endpoint.
4. Backend không thay đổi contract mà không thông báo.
5. Mỗi giai đoạn chỉ hoàn thành khi một luồng tích hợp thật đã chạy được.

## Thứ tự triển khai

| Giai đoạn | Backend bàn giao | Frontend bàn giao | Hoàn thành khi |
| --- | --- | --- | --- |
| 0. Xác thực | API đăng nhập, session, đổi mật khẩu, đăng xuất | Giao diện xác thực hoàn chỉnh | Đăng nhập lần đầu, đổi mật khẩu và đăng xuất chạy được |
| 1. Phân quyền | Role trong session và kiểm tra quyền | Menu và màn hình theo role | Tài khoản chỉ thấy và gọi được chức năng được phép |
| 2. Danh mục phòng | Model, API loại phòng/phòng và dữ liệu mẫu | Giao diện đọc danh mục | Frontend hiển thị dữ liệu thật từ Backend |
| 3. Yêu cầu đặt phòng | API tạo, danh sách, chi tiết yêu cầu | Form và danh sách yêu cầu | Tạo được một yêu cầu hợp lệ từ giao diện |
| 4. Kiểm tra phòng | Service và API availability | Giao diện chọn ngày, loại và số lượng | Kết quả trống phòng khớp dữ liệu Backend |
| 5. Thỏa thuận | Trạng thái, phương án và danh sách chờ | Giao diện đề xuất, chờ hoặc từ chối | Lịch sử và trạng thái chuyển đúng quy tắc |
| 6. Xác nhận | Transaction tạo phiếu và kiểm tra lại tồn phòng | Màn hình tổng hợp và xác nhận | Sinh được mã phiếu, không tạo trùng |
| 7. Sửa/hủy | API chi tiết, sửa và hủy có lịch sử | Màn hình tra cứu, sửa và hủy | Hủy giải phóng phòng nhưng không mất lịch sử |
| 8. Bàn giao/báo cáo | API khách đến/đi và số liệu theo ngày | Dashboard hoặc bảng báo cáo | Dữ liệu nghiệp vụ khớp giữa hai phía |

## Nhịp làm việc cho mỗi giai đoạn

### Trước khi code

- Frontend liệt kê trường nhập, dữ liệu hiển thị và trạng thái giao diện.
- Backend đề xuất endpoint, method, request, response và mã lỗi.
- Hai bên cập nhật `api_contract.md`.

### Trong khi code

- Backend làm model, migration, service, API và test.
- Frontend dùng response mẫu đúng contract để xây giao diện.
- Mỗi bên làm trên nhánh riêng theo `git_workflow.md`.

### Khi tích hợp

- Backend gửi base URL, migration, tài khoản và dữ liệu thử.
- Frontend thay mock bằng API thật.
- Khi lỗi, Frontend gửi URL, method, body, HTTP status và response từ Network.
- Backend sửa hành vi hoặc hai bên cập nhật contract nếu nghiệp vụ thay đổi.

### Trước khi merge

- Backend chạy toàn bộ test.
- Frontend kiểm tra loading, empty, error và success.
- Hai bên chạy ít nhất một luồng từ giao diện tới database.
- Pull request ghi rõ thay đổi ảnh hưởng đến bên còn lại.

## Phạm vi ưu tiên trong 3–4 tuần

Mức tối thiểu nên hoàn thành:

1. Xác thực và phân quyền cơ bản.
2. Loại phòng và phòng.
3. Tạo, xem yêu cầu đặt phòng.
4. Kiểm tra phòng trống.
5. Xác nhận, xem và hủy phiếu đặt.

Thỏa thuận nâng cao, danh sách chờ và báo cáo triển khai sau nếu còn thời gian.
Không mở rộng chức năng trước khi luồng tối thiểu hoạt động ổn định.

