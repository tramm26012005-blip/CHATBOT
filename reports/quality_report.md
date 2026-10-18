# Báo cáo chất lượng dataset

- File nguồn: `câu hoi .csv`
- Dòng hợp lệ: **993** — dòng trống đã bỏ: **28**
- Câu trả lời đã sửa thiếu khoảng trắng sau dấu chấm: **9** (ID: 2, 3, 4, 5, 9, 10, 11, 33, 34)
- Khoảng ID: 1–993
- ID trùng: không có
- ID nhảy số (bị thiếu): không có
- ID không phải số: không có
- Dòng có tên nhóm lạ: không có

## Tổng quan theo nhóm

| Nhóm | Số câu | Train | Test | % Test | Số lỗi | Cảnh báo |
|---|---:|---:|---:|---:|---:|---|
| 01_chao_hoi | 40 | 32 | 8 | 20.0 | 0 |  |
| 02_huong_dan_nau_an | 100 | 80 | 20 | 20.0 | 1 |  |
| 03_huong_dan_nau_mon_mien_tay | 150 | 120 | 30 | 20.0 | 6 |  |
| 04_mon_an_mien_tay | 80 | 64 | 16 | 20.0 | 0 |  |
| 05_nguyen_lieu_gia_vi | 80 | 64 | 16 | 20.0 | 0 |  |
| 06_thay_the_nguyen_lieu | 80 | 64 | 16 | 20.0 | 0 |  |
| 07_dieu_chinh_cong_thuc | 80 | 64 | 16 | 20.0 | 0 |  |
| 08_dinh_duong | 80 | 64 | 16 | 20.0 | 0 |  |
| 09_goi_y_mon_theo_dinh_duong | 80 | 64 | 16 | 20.0 | 0 |  |
| 10_bao_quan_che_bien | 78 | 64 | 14 | 17.9 | 0 |  |
| 11_an_toan_thuc_pham | 75 | 59 | 16 | 21.3 | 0 |  |
| 12_goi_y_khi_om_met | 70 | 56 | 14 | 20.0 | 0 |  |
| **Tổng** | **993** | **795** | **198** | **19.9** | **7** | |

> Số lỗi = trùng trong nhóm + trùng giữa nhóm + rò rỉ Train/Test + thiếu dữ liệu + trả lời quá ngắn/dài + ID trùng + Tập không hợp lệ. Danh sách nhóm 12 thiếu lời khuyên đi khám tính riêng.

## Chi tiết theo nhóm

### 01_chao_hoi — Chào hỏi, cảm ơn, tạm biệt

Không phát hiện lỗi.

**Top 5 nguồn URL:** không có URL

### 02_huong_dan_nau_an — Hướng dẫn nấu ăn

**Trả lời quá dài** (1)
- ID 254 (1603 ký tự): Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với


**Top 5 nguồn URL:** không có URL

### 03_huong_dan_nau_mon_mien_tay — Hướng dẫn nấu món ăn miền Tây

**Trả lời quá dài** (6)
- ID 49 (1796 ký tự): Cách nấu hủ tiếu Mỹ Tho tại nhà
- ID 54 (1687 ký tự): Hướng dẫn làm bánh tằm bì
- ID 59 (1612 ký tự): Thịt kho rệu miền Tây là gì chỉ mình cách kho
- ID 61 (1583 ký tự): Kho quẹt tôm thịt làm sao cho sánh
- ID 161 (1754 ký tự): Mình muốn nấu bún gỏi dà Sóc Trăng thì làm sao
- ID 165 (1522 ký tự): Bánh cống Sóc Trăng làm như nào vậy


**Top 5 nguồn URL:**
- 1 lần — https://www.dienmayxanh.com/vao-bep/cach-lam-mon-ca-loc-kho-to-de-nhat-ngon-nhat-00816
- 1 lần — https://www.dienmayxanh.com/vao-bep/huong-dan-chi-tiet-cach-nau-lau-mam-ngon-ngat-ngay-de-lam-01015
- 1 lần — https://vnexpress.net/doi-song-cooking-banh-xeo-mien-tay-4654925.html
- 1 lần — https://www.dienmayxanh.com/vao-bep/cach-lam-ca-loc-nuong-trui-thom-lung-hap-dan-don-02753
- 1 lần — https://www.dienmayxanh.com/vao-bep/cach-nau-canh-ga-la-giang-ngon-nhat-vi-chua-diu-thit-ga-00187

### 04_mon_an_mien_tay — Món ăn miền Tây

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 5 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/top-10-nhung-mon-an-dac-san-mien-tay-thu-hut-khach-du-lich-1363860
- 4 lần — https://www.dienmayxanh.com/vao-bep/tong-hop-25-mon-an-dan-da-mien-tay-nam-bo-noi-tieng-an-la-10866
- 3 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/mien-tay-vao-mua-nuoc-noi-ban-da-thu-het-nhung-mon-ngon-quen-troi-dat-tu-ca-linh-nay-chua-1296154
- 3 lần — https://www.dienmayxanh.com/vao-bep/cach-lam-nuoc-mam-an-banh-xeo-mien-trung-mien-tay-chua-ngot-23717
- 2 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/cach-lam-mam-ca-loc-ngon-chuan-vi-mien-tay-1386770

### 05_nguyen_lieu_gia_vi — Nguyên liệu và gia vị

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 2 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/su-khac-nhau-giua-bot-nghe-va-tinh-bot-nghe-1017282
- 2 lần — https://www.dienmayxanh.com/vao-bep/tac-dung-cua-la-lot-goi-y-10-mon-an-ngon-tu-la-lot-cho-ban-08014
- 2 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/8-mon-ngon-tu-bong-dien-dien-de-lam-chuan-vi-mien-tay-1540722
- 1 lần — https://www.dienmayxanh.com/vao-bep/nuoc-mam-la-gi-do-dam-cua-nuoc-mam-co-quyet-dinh-chat-luong-09028
- 1 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/cach-chon-mua-nuoc-mam-ngon-936843

### 06_thay_the_nguyen_lieu — Thay thế nguyên liệu

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 19 lần — https://www.dienmayxanh.com/vao-bep/gia-vi-la-gi-phan-loai-va-cac-loai-gia-vi-pho-bien-tot-cho-05726
- 7 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/them-cac-thuc-pham-nay-mon-an-se-co-vi-ngon-den-bat-ngo-1117227
- 5 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/tong-hop-cac-mon-an-tu-thit-heo-bo-ga-thom-ngon-de-lam-ngay-tai-nha-1557975
- 3 lần — https://www.dienmayxanh.com/vao-bep/cach-lam-nuoc-cot-dua-sanh-min-thom-ngon-don-gian-tai-nha-01773
- 2 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/goi-y-7-san-pham-dung-thay-the-nuoc-mam-hieu-qua-1406755

### 07_dieu_chinh_cong_thuc — Phân tích và điều chỉnh công thức

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 12 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/8-meo-nau-an-bien-co-nang-vung-ve-thanh-co-nang-dam-dang-1144391
- 10 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/cach-nem-tung-loai-gia-vi-dung-chuan-giup-mon-an-ngon-ngay-tu-khi-che-bien-1323338
- 7 lần — https://www.dienmayxanh.com/vao-bep/chua-chay-mon-an-hong-bang-nhung-meo-don-gian-den-00331
- 5 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/10-bi-quyet-chua-chay-loi-thuong-gap-khi-nau-an-1088498
- 5 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/cach-uop-thit-nuong-ngon-dam-da-972222

### 08_dinh_duong — Dinh dưỡng trong ăn uống

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 2 lần — https://suckhoedoisong.vn/lam-the-nao-de-co-bua-an-hop-ly-va-du-dinh-duong-169175399.htm
- 1 lần — https://suckhoedoisong.vn/dinh-duong-can-bang-chia-khoa-cua-kiem-soat-can-nang-169221123160733139.htm
- 1 lần — https://suckhoedoisong.vn/tai-sao-bac-si-khuyen-ban-nen-an-nhieu-rau-xanh-169130199.htm
- 1 lần — https://suckhoedoisong.vn/nuoc-uong-bao-nhieu-la-du-169159611.htm
- 1 lần — https://suckhoedoisong.vn/5-ly-do-khien-viec-an-sang-thuong-xuyen-rat-quan-trong-169231111164638663.htm

### 09_goi_y_mon_theo_dinh_duong — Gợi ý món ăn theo nhu cầu dinh dưỡng

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 3 lần — https://suckhoedoisong.vn/chon-thuc-pham-the-nao-de-vua-du-chat-vua-tiet-kiem-16926082522140106.htm
- 2 lần — https://giadinh.suckhoedoisong.vn/hom-nay-an-gi-goi-y-190-thuc-don-mon-ngon-moi-ngay-de-ca-nha-quanh-nam-am-cung-ben-mam-com-gia-dinh-172240329180403438.htm
- 2 lần — https://giadinh.suckhoedoisong.vn/5-cong-thuc-lam-bua-sang-don-gian-nau-chi-khoang-5-10-phut-ma-van-dam-bao-ngon-mieng-giau-dinh-duong-172251209164346831.htm
- 2 lần — https://giadinh.suckhoedoisong.vn/cac-mon-an-ngon-cuoi-tuan-de-lam-de-dai-khach-172240807174148817.htm
- 2 lần — https://suckhoedoisong.vn/lua-chon-mon-an-vat-lanh-manh-vua-ngon-vua-tot-cho-suc-khoe-gia-dinh-169250805160523842.htm

### 10_bao_quan_che_bien — Bảo quản và chế biến thực phẩm

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 11 lần — https://www.dienmayxanh.com/vao-bep/thoi-gian-bao-quan-cac-loai-thuc-pham-pho-bien-trong-tu-lanh-06452
- 11 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/tong-hop-cac-mon-an-tu-thit-heo-bo-ga-thom-ngon-de-lam-ngay-tai-nha-1557975
- 8 lần — https://www.dienmayxanh.com/vao-bep/5-loi-nau-an-hay-mac-phai-va-cach-khac-phuc-03235
- 6 lần — https://www.dienmayxanh.com/vao-bep/cach-bao-quan-thuc-pham-kho-dung-cach-an-toan-dung-duoc-lau-12417
- 4 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/tat-tan-tat-meo-bao-quan-thit-heo-ga-bo-ca-tuoi-ngon-ca-thang-1371137

### 11_an_toan_thuc_pham — An toàn thực phẩm

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 5 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/thuc-pham-ban-la-gi-nguyen-nhan-va-tac-hai-khi-tieu-thu-thuc-an-ban-1420156
- 3 lần — https://www.dienmayxanh.com/vao-bep/thoi-gian-bao-quan-cac-loai-thuc-pham-pho-bien-trong-tu-lanh-06452
- 1 lần — https://www.bachhoaxanh.com/kinh-nghiem-hay/nhung-viec-can-lam-khi-bi-ngo-doc-thuc-pham-tai-nha-de-xu-ly-nhanh-1592266
- 1 lần — https://medlatec.vn/tin-tuc/cach-chua-ngo-doc-thuc-pham-tai-nha-giup-giam-nhanh-cac-trieu-chung-s195-n31546
- 1 lần — https://vnexpress.net/lam-sao-biet-thuc-an-thua-da-hong-4828279.html

### 12_goi_y_khi_om_met — Gợi ý ăn uống khi cảm, ho, sốt, mệt mỏi hoặc trong thời kỳ kinh nguyệt

Không phát hiện lỗi.

**Top 5 nguồn URL:**
- 2 lần — https://suckhoedoisong.vn/thuc-pham-nen-an-va-nen-tranh-giup-nguoi-benh-cam-cum-nhanh-hoi-phuc-16921101822591353.htm
- 2 lần — https://suckhoedoisong.vn/nen-va-khong-nen-an-gi-khi-bi-sot-16993179.htm
- 2 lần — https://suckhoedoisong.vn/che-do-dinh-duong-cho-nguoi-moi-om-day-169172459.htm
- 2 lần — https://suckhoedoisong.vn/3-mon-an-giup-giam-met-moi-khi-thoi-tiet-giao-mua-169260317191849693.htm
- 2 lần — https://suckhoedoisong.vn/5-mon-an-bai-thuoc-giup-bo-huyet-dieu-hoa-kinh-nguyet-169230301233541842.htm

## Nhóm 12: câu trả lời chưa có lời khuyên đi khám / hỏi bác sĩ (39)

_Chỉ liệt kê để xem tay, script không sửa._

- ID 772 (Train): Cảm cúm kiêng ăn gì
- ID 773 (Train): Cháo gì ăn khi bị cảm tốt nhất
- ID 774 (Train): Bị cảm uống gì cho dễ chịu
- ID 775 (Train): Bị ho nên ăn gì
- ID 776 (Train): Ho kiêng ăn gì cho mau hết
- ID 779 (Train): Bị sốt nên kiêng gì
- ID 780 (Train): Sốt xong ăn gì để phục hồi sức khỏe
- ID 782 (Train): Ăn gì khi cảm thấy kiệt sức
- ID 783 (Train): Hay mệt buổi chiều nên ăn gì bữa trưa
- ID 784 (Train): Ăn gì cho đỡ mệt khi thay đổi thời tiết
- ID 785 (Train): Trong kỳ kinh nguyệt nên ăn gì
- ID 786 (Train): Kinh nguyệt nên kiêng ăn gì
- ID 787 (Train): Đau bụng kinh ăn gì cho bớt đau
- ID 788 (Train): Trước kỳ kinh nên ăn gì để bớt khó chịu
- ID 789 (Train): Sau kỳ kinh nên ăn gì bồi bổ
- ID 792 (Train): Hết cảm rồi nhưng vẫn mệt nên ăn gì
- ID 794 (Train): Nấu gì cho người nhà bị cảm ăn
- ID 797 (Train): Ăn gì khi bị cảm mà không có gừng
- ID 799 (Train): Cảm nắng ăn gì cho mau hết
- ID 800 (Train): Bị nghẹt mũi nên ăn gì cho thông
- ID 802 (Train): Bị cảm lạnh ban đêm nên uống gì trước khi ngủ
- ID 805 (Train): Làm việc nhiều mệt mỏi nên ăn gì
- ID 806 (Train): Ăn gì để bớt mệt khi học thi
- ID 807 (Train): Mệt mỏi do thay đổi thời tiết ăn uống sao cho khỏe
- ID 808 (Train): Người già hay mệt mỏi nên ăn gì
- ID 812 (Train): Trong kỳ kinh có nên uống nước dừa không
- ID 813 (Train): Hay bị mệt trước kỳ kinh nên làm gì
- ID 814 (Train): Nên nấu gì cho người nhà bị sốt
- ID 815 (Train): Bị ốm không muốn ăn cơm thì ăn gì thay
- ID 819 (Train): Mùa mưa hay bị cảm nên ăn gì phòng
- ID 821 (Train): Cách nấu cháo gà gừng cho người cảm
- ID 823 (Train): Người bị cảm có nên ăn hải sản không
- ID 827 (Test): Bị cảm có nên ăn trứng không
- ID 828 (Test): Bị sốt có uống nước dừa được không
- ID 830 (Test): Mệt mỏi do thiếu ngủ ăn gì cho tỉnh
- ID 832 (Test): Bị cảm có nên uống sữa không
- ID 834 (Test): Bị cảm có nên tắm không và ăn uống thế nào
- ID 835 (Test): Sốt virus ở trẻ nên cho ăn uống gì
- ID 840 (Test): Nấu gì cho nhanh khi người nhà bị ốm đột ngột
