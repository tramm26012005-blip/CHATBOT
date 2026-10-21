# Kiểm tra kho vector (Bài 4 – Phần II)

- Ngày chạy: 2026-10-18 15:16
- Mô hình: `bkai-foundation-models/vietnamese-bi-encoder`, tách từ trước khi sinh vector: `True`, tiền tố đoạn: `(không)`, tiền tố câu hỏi: `(không)`.
- Kho: FAISS `IndexFlatIP` (tìm vét cạn) trên vector chuẩn hóa L2, tức là điểm = cosine.
- Mọi phép kiểm chạy trên kho **nạp lại từ đĩa**, không dùng vector còn trong bộ nhớ.

## 1. Bảng kiểm

| Kho | Số đoạn vào | Số vector | Số dòng siêu dữ liệu | Khớp | Chuẩn min–max | Tự truy hồi top-1 | Số chiều | Sinh vector |
|---|---|---|---|---|---|---|---|---|
| `cau_truc_Train` | 975 | 975 | 975 | đạt | 1.000000–1.000000 | 20/20 | 768 | bộ đệm |
| `co_dinh_Train` | 956 | 956 | 956 | đạt | 1.000000–1.000000 | 20/20 | 768 | bộ đệm |
| `de_quy_Train` | 958 | 958 | 958 | đạt | 1.000000–1.000000 | 20/20 | 768 | bộ đệm |

## 2. Ba câu hỏi mẫu (top-5)

### Kho `cau_truc_Train`

**cách nấu hủ tiếu Mỹ Tho** → đưa vào mô hình: `cách nấu hủ_tiếu Mỹ_Tho`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.7425 | 49 | 03_huong_dan_nau_mon_mien_tay | Train | Cách nấu hủ tiếu Mỹ Tho tại nhà | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 6 người, chuẩn bị 45 phút và nấu khoảng 4 giờ) |
| 2 | 0.7024 | 49 | 03_huong_dan_nau_mon_mien_tay | Train | Cách nấu hủ tiếu Mỹ Tho tại nhà | Sơ chế + Cách chế biến |
| 3 | 0.5931 | 49 | 03_huong_dan_nau_mon_mien_tay | Train | Cách nấu hủ tiếu Mỹ Tho tại nhà | Hoàn thành món ăn |
| 4 | 0.5891 | 131 | 03_huong_dan_nau_mon_mien_tay | Train | Hủ tiếu chay miền Tây nấu sao | Sơ chế + Cách chế biến + Hoàn thành món ăn |
| 5 | 0.5617 | 131 | 03_huong_dan_nau_mon_mien_tay | Train | Hủ tiếu chay miền Tây nấu sao | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 5 người, chuẩn bị 20 phút và nấu khoảng 45 phút) |

**món ít béo cho người tiểu đường** → đưa vào mô hình: `món ít béo cho người tiểu_đường`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.3959 | 489 | 07_dieu_chinh_cong_thuc | Train | Muốn nấu ăn ít dầu mỡ thì làm sao | — |
| 2 | 0.3556 | 742 | 09_goi_y_mon_theo_dinh_duong | Train | Gợi ý món ăn cho người mới bắt đầu tập nấu | — |
| 3 | 0.3502 | 750 | 09_goi_y_mon_theo_dinh_duong | Train | Gợi ý ăn gì cho người ăn low carb | — |
| 4 | 0.3434 | 743 | 09_goi_y_mon_theo_dinh_duong | Train | Ăn gì cho người hay bị chuột rút | — |
| 5 | 0.3232 | 719 | 09_goi_y_mon_theo_dinh_duong | Train | Nấu gì cho bữa tiệc nhỏ tại nhà | — |

**lẩu mắm cần nguyên liệu gì** → đưa vào mô hình: `lẩu_mắm cần nguyên_liệu gì`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.6542 | 43 | 03_huong_dan_nau_mon_mien_tay | Train | Hướng dẫn mình nấu lẩu mắm miền Tây | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 4 người) |
| 2 | 0.5843 | 43 | 03_huong_dan_nau_mon_mien_tay | Train | Hướng dẫn mình nấu lẩu mắm miền Tây | Sơ chế + Cách chế biến + Hoàn thành món ăn |
| 3 | 0.5635 | 58 | 03_huong_dan_nau_mon_mien_tay | Train | Mắm chưng miền Tây làm sao bạn | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 4 đến 6 người, chuẩn bị 20 phút và hấp khoảng 1 giờ) |
| 4 | 0.5600 | 52 | 03_huong_dan_nau_mon_mien_tay | Train | Mắm kho miền Tây nấu sao cho đúng vị | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 3 đến 4 người, chuẩn bị 20 phút và nấu khoảng 40 phút) |
| 5 | 0.5529 | 87 | 03_huong_dan_nau_mon_mien_tay | Train | Lẩu mắm cá kèo nấu như thế nào | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 5 người, chuẩn bị 20 phút và nấu khoảng 45 phút) |

### Kho `co_dinh_Train`

**cách nấu hủ tiếu Mỹ Tho** → đưa vào mô hình: `cách nấu hủ_tiếu Mỹ_Tho`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.7567 | 49 | 03_huong_dan_nau_mon_mien_tay | Train | Cách nấu hủ tiếu Mỹ Tho tại nhà | — |
| 2 | 0.6981 | 49 | 03_huong_dan_nau_mon_mien_tay | Train | Cách nấu hủ tiếu Mỹ Tho tại nhà | — |
| 3 | 0.6641 | 49 | 03_huong_dan_nau_mon_mien_tay | Train | Cách nấu hủ tiếu Mỹ Tho tại nhà | — |
| 4 | 0.5645 | 131 | 03_huong_dan_nau_mon_mien_tay | Train | Hủ tiếu chay miền Tây nấu sao | — |
| 5 | 0.5587 | 131 | 03_huong_dan_nau_mon_mien_tay | Train | Hủ tiếu chay miền Tây nấu sao | — |

**món ít béo cho người tiểu đường** → đưa vào mô hình: `món ít béo cho người tiểu_đường`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.3959 | 489 | 07_dieu_chinh_cong_thuc | Train | Muốn nấu ăn ít dầu mỡ thì làm sao | — |
| 2 | 0.3556 | 742 | 09_goi_y_mon_theo_dinh_duong | Train | Gợi ý món ăn cho người mới bắt đầu tập nấu | — |
| 3 | 0.3502 | 750 | 09_goi_y_mon_theo_dinh_duong | Train | Gợi ý ăn gì cho người ăn low carb | — |
| 4 | 0.3434 | 743 | 09_goi_y_mon_theo_dinh_duong | Train | Ăn gì cho người hay bị chuột rút | — |
| 5 | 0.3232 | 719 | 09_goi_y_mon_theo_dinh_duong | Train | Nấu gì cho bữa tiệc nhỏ tại nhà | — |

**lẩu mắm cần nguyên liệu gì** → đưa vào mô hình: `lẩu_mắm cần nguyên_liệu gì`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.6010 | 43 | 03_huong_dan_nau_mon_mien_tay | Train | Hướng dẫn mình nấu lẩu mắm miền Tây | — |
| 2 | 0.5536 | 58 | 03_huong_dan_nau_mon_mien_tay | Train | Mắm chưng miền Tây làm sao bạn | — |
| 3 | 0.5520 | 576 | 04_mon_an_mien_tay | Train | Chọn rau sống ăn kèm lẩu mắm thế nào cho đủ | — |
| 4 | 0.5383 | 535 | 04_mon_an_mien_tay | Train | Lẩu mắm miền Tây ăn kèm với rau gì | — |
| 5 | 0.5284 | 87 | 03_huong_dan_nau_mon_mien_tay | Train | Lẩu mắm cá kèo nấu như thế nào | — |

### Kho `de_quy_Train`

**cách nấu hủ tiếu Mỹ Tho** → đưa vào mô hình: `cách nấu hủ_tiếu Mỹ_Tho`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.7668 | 49 | 03_huong_dan_nau_mon_mien_tay | Train | Cách nấu hủ tiếu Mỹ Tho tại nhà | — |
| 2 | 0.7434 | 49 | 03_huong_dan_nau_mon_mien_tay | Train | Cách nấu hủ tiếu Mỹ Tho tại nhà | — |
| 3 | 0.5947 | 131 | 03_huong_dan_nau_mon_mien_tay | Train | Hủ tiếu chay miền Tây nấu sao | — |
| 4 | 0.5817 | 131 | 03_huong_dan_nau_mon_mien_tay | Train | Hủ tiếu chay miền Tây nấu sao | — |
| 5 | 0.5005 | 69 | 03_huong_dan_nau_mon_mien_tay | Train | Hủ tiếu Sa Đéc nấu như thế nào | — |

**món ít béo cho người tiểu đường** → đưa vào mô hình: `món ít béo cho người tiểu_đường`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.3959 | 489 | 07_dieu_chinh_cong_thuc | Train | Muốn nấu ăn ít dầu mỡ thì làm sao | — |
| 2 | 0.3556 | 742 | 09_goi_y_mon_theo_dinh_duong | Train | Gợi ý món ăn cho người mới bắt đầu tập nấu | — |
| 3 | 0.3502 | 750 | 09_goi_y_mon_theo_dinh_duong | Train | Gợi ý ăn gì cho người ăn low carb | — |
| 4 | 0.3434 | 743 | 09_goi_y_mon_theo_dinh_duong | Train | Ăn gì cho người hay bị chuột rút | — |
| 5 | 0.3232 | 719 | 09_goi_y_mon_theo_dinh_duong | Train | Nấu gì cho bữa tiệc nhỏ tại nhà | — |

**lẩu mắm cần nguyên liệu gì** → đưa vào mô hình: `lẩu_mắm cần nguyên_liệu gì`

| # | Điểm | ID gốc | Nhóm | Tập | Câu hỏi gốc | Tên mục |
|---|---|---|---|---|---|---|
| 1 | 0.6005 | 43 | 03_huong_dan_nau_mon_mien_tay | Train | Hướng dẫn mình nấu lẩu mắm miền Tây | — |
| 2 | 0.5732 | 43 | 03_huong_dan_nau_mon_mien_tay | Train | Hướng dẫn mình nấu lẩu mắm miền Tây | — |
| 3 | 0.5670 | 58 | 03_huong_dan_nau_mon_mien_tay | Train | Mắm chưng miền Tây làm sao bạn | — |
| 4 | 0.5520 | 576 | 04_mon_an_mien_tay | Train | Chọn rau sống ăn kèm lẩu mắm thế nào cho đủ | — |
| 5 | 0.5453 | 87 | 03_huong_dan_nau_mon_mien_tay | Train | Lẩu mắm cá kèo nấu như thế nào | — |

