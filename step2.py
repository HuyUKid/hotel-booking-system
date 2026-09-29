"""
Logic nghiệp vụ Bước 2: Tiếp nhận và xác định khả năng đáp ứng yêu cầu đặt buồng.
Công thức: Buồng bán được = Tổng buồng - (Đang có khách + Đã đặt chắc chắn + Hỏng) + Overbooking allowance
"""

def kiem_tra_kha_nang_dap_ung(
    tong_buong: int,
    buong_dang_o: int,
    buong_da_dat: int,
    buong_hong: int,
    buong_yeu_cau: int,
    ty_le_overbooking: float = 0.10
) -> dict:
    # 1. Tính số buồng cho phép overbooking (làm tròn xuống)
    buong_overbook = int(tong_buong * ty_le_overbooking)
    
    # 2. Tính số buồng thực tế còn trống
    buong_con_lai = tong_buong - (buong_dang_o + buong_da_dat + buong_hong)
    
    # 3. Tổng buồng tối đa được phép bán ra
    tong_buong_co_the_ban = buong_con_lai + buong_overbook

    # 4. Đưa ra quyết định nghiệp vụ
    if buong_yeu_cau <= buong_con_lai:
        trang_thai = "DAP_UNG_BINH_THUONG"
        ghi_chu = "Chấp nhận đặt buồng chính thức."
    elif buong_yeu_cau <= tong_buong_co_the_ban:
        trang_thai = "DAP_UNG_OVERBOOKING"
        ghi_chu = "Chấp nhận đặt buồng theo diện Overbooking (vượt công suất an toàn)."
    else:
        trang_thai = "TU_CHOI"
        ghi_chu = "Hết buồng, gợi ý đổi ngày hoặc đưa vào Danh sách chờ (Waiting List)."

    return {
        "tong_co_the_ban": tong_buong_co_the_ban,
        "trang_thai": trang_thai,
        "ghi_chu": ghi_chu
    }


# Kịch bản kiểm thử mẫu (Test cases để P1 và cả nhóm cùng đối chiếu)
if __name__ == "__main__":
    print("--- KỊCH BẢN 1: Còn buồng bình thường ---")
    kq1 = kiem_tra_kha_nang_dap_ung(tong_buong=100, buong_dang_o=60, buong_da_dat=20, buong_hong=5, buong_yeu_cau=10)
    print(kq1)

    print("\n--- KỊCH BẢN 2: Chạm ngưỡng Overbooking ---")
    kq2 = kiem_tra_kha_nang_dap_ung(tong_buong=100, buong_dang_o=70, buong_da_dat=20, buong_hong=5, buong_yeu_cau=12)
    print(kq2)

    print("\n--- KỊCH BẢN 3: Hết buồng, từ chối ---")
    kq3 = kiem_tra_kha_nang_dap_ung(tong_buong=100, buong_dang_o=70, buong_da_dat=25, buong_hong=5, buong_yeu_cau=15)
    print(kq3)