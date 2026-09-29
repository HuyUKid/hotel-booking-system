# Bảng Quản trị Rủi ro (Risk Register)

| ID | Rủi ro | Tác động | Khả năng | Phương án giảm thiểu |
|:---|:---|:---:|:---:|:---|
| R1 | Lệch môi trường giữa các máy cá nhân | Cao | Trung bình | Dùng chung `requirements.txt` và cố định phiên bản Django |
| R2 | Sai lệch công thức tính phòng trống (Bước 2) | Cao | Cao | Chốt kịch bản số và test case cụ thể trước khi viết code |
| R3 | Xung đột khi gộp mã nguồn (Merge conflict) | Trung bình | Cao | Chia nhỏ task, cập nhật nhánh `main` hàng ngày qua PR |