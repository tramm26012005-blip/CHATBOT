# Kiểm tra tách từ

- Kiểu đặt dấu đã chọn: **kiểu cũ: dấu đặt trên nguyên âm thứ nhất khi vần không có phụ âm cuối (hòa, thủy, khỏe, lóa)**.
- Thư viện: underthesea 9.5.0, `word_tokenize(..., format="text", fixed_words=TU_DIEN_RIENG, use_token_normalize=False)`.
- Từ điển riêng: `cau_hinh/tu_dien_rieng.txt` (69 cụm).
- Số dòng: 993. Dòng trống đã bỏ: 0.
- Tiền xử lý: 0 chỗ đổi kiểu đặt dấu, 0 ô được thêm dấu cách sau dấu câu.
- Seed ngẫu nhiên: 42.

## 1. Không mất chữ

So sánh văn bản đã tiền xử lý và bản tách từ, sau khi đổi `_` thành dấu cách và bỏ toàn bộ khoảng trắng.

- Lỗi ở Câu hỏi: **0**
- Lỗi ở Câu trả lời: **0**

## 2. Kiểm thử chuẩn hóa (slide 33)

**a) NFD và NFC**

| | NFD (dấu tổ hợp) | NFC (dựng sẵn) |
|---|---|---|
| Số ký tự của `Cách nấu cá lóc` | 20 | 15 |
| So sánh chuỗi `nfd == nfc` | `False` | |
| Có tìm thấy `"cá lóc"` (NFC) trong chuỗi? | `False` | `True` |
| Tách từ trước chuẩn hóa | `Cách nấu cá_lóc` (15 ký tự) | `Cách nấu cá_lóc` (15 ký tự) |
| Tách từ sau `normalize('NFC')` | `Cách nấu cá_lóc` | `Cách nấu cá_lóc` |

- Trước chuẩn hóa hai chuỗi **khác nhau** (20 và 15 ký tự), nên tra từ điển và đếm từ cho kết quả khác.
- Kết quả tách từ trước chuẩn hóa giống nhau: `True`. Lưu ý: underthesea 9.5 tự đổi đầu vào NFD về NFC bên trong hàm tách từ, nên riêng bước tách từ không thấy khác biệt. Các bước khác của pipeline (từ điển riêng, regex bảo vệ số, so khớp chuỗi) vẫn bị ảnh hưởng, nên NFC vẫn phải làm đầu tiên.
- Sau chuẩn hóa: `True` (giống nhau).

**b) Hai kiểu đặt dấu (bước 2), thư viện không tự sửa**

| Câu | Tách từ |
|---|---|
| `Khuấy cho đường hoà tan` (kiểu mới) | `Khuấy cho đường hoà_tan` |
| `Khuấy cho đường hòa tan` (kiểu cũ) | `Khuấy cho đường hòa tan` |
| `Khuấy cho đường hoà tan` sau khi thống nhất dấu | `Khuấy cho đường hòa tan` |

- Trước chuẩn hóa dấu, hai câu cho kết quả giống nhau? `False`: cùng một từ bị tách thành hai kiểu khác nhau.
- Sau chuẩn hóa dấu, giống nhau? `True`.

## 3. Top 50 từ ghép

| # | Từ ghép | Số lần |
|---|---|---|
| 1 | muỗng_canh | 600 |
| 2 | nước_mắm | 481 |
| 3 | chuẩn_bị | 390 |
| 4 | món_ăn | 370 |
| 5 | muỗng_cà_phê | 340 |
| 6 | hạt_nêm | 331 |
| 7 | rửa_sạch | 322 |
| 8 | nguyên_liệu | 304 |
| 9 | chế_biến | 299 |
| 10 | dầu_ăn | 294 |
| 11 | miền_tây | 291 |
| 12 | hành_tím | 288 |
| 13 | bột_ngọt | 271 |
| 14 | hành_lá | 268 |
| 15 | sơ_chế | 260 |
| 16 | hoàn_thành | 260 |
| 17 | có_thể | 228 |
| 18 | gia_vị | 219 |
| 19 | ăn_kèm | 181 |
| 20 | cá_lóc | 170 |
| 21 | vừa_ăn | 142 |
| 22 | cà_chua | 135 |
| 23 | làm_sao | 130 |
| 24 | tủ_lạnh | 127 |
| 25 | trái_cây | 125 |
| 26 | tắt_bếp | 117 |
| 27 | nấu_ăn | 114 |
| 28 | thức_ăn | 112 |
| 29 | thực_phẩm | 111 |
| 30 | canh_chua | 110 |
| 31 | rau_sống | 106 |
| 32 | nước_cốt_dừa | 102 |
| 33 | cơm_trắng | 97 |
| 34 | bảo_quản | 96 |
| 35 | nước_dừa | 94 |
| 36 | tiêu_xay | 93 |
| 37 | đậu_hũ | 92 |
| 38 | nước_muối | 85 |
| 39 | tỏi_băm | 84 |
| 40 | thịt_bò | 83 |
| 41 | nước_dùng | 80 |
| 42 | hành_tây | 79 |
| 43 | nước_sôi | 78 |
| 44 | cà_rốt | 78 |
| 45 | thịt_heo | 77 |
| 46 | chua_ngọt | 75 |
| 47 | tự_nhiên | 75 |
| 48 | cá_kèo | 75 |
| 49 | đậm_đà | 74 |
| 50 | đặc_trưng | 72 |

## 4. Nghi tách sai

**a) Cụm trong từ điển riêng vẫn bị tách rời trong kết quả cuối**

Bước ép từ điển luôn ghép đủ cụm, nên mục này phải bằng 0. Nếu khác 0 tức là bước ép bị lỗi.

- Không có (0 trường hợp).

**b) Cụm từ điển mà underthesea tách sai, đã được bước ép từ điển sửa lại**

Thư viện tách rời cụm hoặc nối cụm với từ bên cạnh (ví dụ `Nêm_nước_mắm`, `canh_chua_cá_lóc`).

| Cụm | Số lần đã sửa |
|---|---|
| hành tím | 188 |
| rửa sạch | 82 |
| ăn kèm | 68 |
| nước mắm | 54 |
| thịt heo | 53 |
| tỏi băm | 49 |
| thịt bò | 42 |
| nước cốt dừa | 41 |
| đậu hũ | 40 |
| hạt nêm | 39 |
| thịt ba chỉ | 38 |
| bông điên điển | 36 |
| miền tây | 33 |
| muỗng canh | 31 |
| nước dừa tươi | 29 |
| cá kèo | 27 |
| bông súng | 27 |
| nước dừa | 25 |
| hành lá | 24 |
| muỗng cà phê | 21 |
| rau xanh | 21 |
| rau sống | 20 |
| nước dùng | 20 |
| canh chua | 18 |
| dầu ăn | 18 |
| nước màu | 16 |
| lẩu mắm | 16 |
| cá lóc | 16 |
| nước lọc | 15 |
| ớt hiểm | 15 |
| tỏi phi | 14 |
| tắt bếp | 10 |
| mắm cá linh | 10 |
| cá linh | 10 |
| mắm ruốc | 9 |
| kho tộ | 8 |
| bữa cơm | 7 |
| đường thốt nốt | 7 |
| chiên giòn | 6 |
| rau răm | 6 |
| bông so đũa | 6 |
| món ăn | 5 |
| hành phi | 5 |
| bánh khọt | 5 |
| nước chấm | 5 |
| bữa ăn | 5 |
| kinh nguyệt | 5 |
| vitamin c | 5 |
| ngò gai | 4 |
| chất xơ | 4 |
| bạc hà | 3 |
| cơm trắng | 3 |
| luộc sơ | 3 |
| bánh tét | 3 |
| chất đạm | 3 |
| nước sôi | 2 |
| bột ngọt | 2 |
| vừa ăn | 2 |
| me chua | 2 |
| tinh bột | 2 |
| cá rô đồng | 1 |
| bánh xèo | 1 |
| nướng trui | 1 |
| nước muối | 1 |

**c) Từ ghép dài hơn 4 âm tiết**

- Không có.

## 5. So sánh trước và sau (3 dòng ngẫu nhiên mỗi nhóm, seed = 42)

### 01_chao_hoi

**ID 8**

- Câu hỏi gốc: Bạn biết nấu món miền Tây không
- Câu hỏi tách từ: `Bạn biết nấu món miền_Tây không`

Câu trả lời gốc:

```text
Biết chứ bạn. Món miền Tây là phần mình ưu tiên như canh chua cá lóc, cá kho tộ, lẩu mắm hay bánh xèo. Bạn muốn học món nào thì nói mình nhé
```

Câu trả lời tách từ (3 câu):

```text
Biết chứ bạn . Món miền_Tây là phần mình ưu_tiên như canh_chua cá_lóc , cá kho_tộ , lẩu_mắm hay bánh_xèo . Bạn muốn học món nào thì nói mình nhé
```

**ID 2**

- Câu hỏi gốc: Chào bot
- Câu hỏi tách từ: `Chào bot`

Câu trả lời gốc:

```text
Chào bạn nha. Mình là chatbot hướng dẫn nấu ăn và gợi ý món ăn theo nhu cầu dinh dưỡng. Bạn cần mình chỉ cách nấu món nào hay muốn mình gợi ý món cho bữa hôm nay
```

Câu trả lời tách từ (3 câu):

```text
Chào bạn nha . Mình là chatbot hướng_dẫn nấu_ăn và gợi_ý món_ăn theo nhu_cầu dinh_dưỡng . Bạn cần mình chỉ cách nấu món nào hay muốn mình gợi_ý món cho bữa hôm_nay
```

**ID 18**

- Câu hỏi gốc: Cảm ơn đã gợi ý món
- Câu hỏi tách từ: `Cảm_ơn đã gợi_ý món`

Câu trả lời gốc:

```text
Không có gì bạn. Mong bạn và gia đình có bữa cơm thật ngon
```

Câu trả lời tách từ (2 câu):

```text
Không có gì bạn . Mong bạn và gia_đình có bữa_cơm thật ngon
```

### 02_huong_dan_nau_an

**ID 272**

- Câu hỏi gốc: Chỉ mình cách luộc thịt heo cho trắng mà không bị khô
- Câu hỏi tách từ: `Chỉ mình cách luộc thịt_heo cho trắng mà không bị khô`

Câu trả lời gốc:

```text
Thịt heo luộc đúng cách sẽ trắng đẹp, thịt chín tới mà không bị khô hay dai, chấm nước mắm ăn rất hợp.

Nguyên liệu cần chuẩn bị
- Thịt heo 1 miếng vừa ăn
- Muối 1 ít
- Hành tím hoặc hành tây 1 ít
- Gừng 1 ít
- Giấm ăn tùy chọn
- Rượu trắng tùy chọn

Sơ chế
- Ngâm thịt heo trong nước muối 5-10 phút để chất bẩn tiết ra
- Chần thịt trong hỗn hợp nước, giấm và muối khoảng 2-3 phút rồi rửa lại bằng nước sạch

Cách chế biến
- Chuẩn bị nồi nước lạnh, cho thịt vào
- Thêm muối, hành, gừng vào nồi
- Luộc thịt khoảng 20-30 phút là thịt chín
- Vớt bọt thường xuyên để nước trong
- Khi thịt gần chín có thể thêm chút giấm hoặc rượu trắng để thịt trắng đẹp hơn

Hoàn thành món ăn
Sau khi chín, vớt thịt cho vào nước đá ngâm khoảng 15-20 phút để thịt săn chắc rồi thái lát mỏng, dùng kèm nước mắm chua ngọt hoặc mắm tôm.

Muốn kiểm tra thịt chín chưa thì lấy đũa xiên vào, nếu xuyên qua dễ dàng là được, chúc bạn luộc thịt ngon.
```

Câu trả lời tách từ (19 câu):

```text
Thịt_heo luộc đúng cách sẽ trắng đẹp , thịt chín tới mà không bị khô hay dai , chấm nước_mắm ăn rất hợp . Nguyên_liệu cần chuẩn_bị - Thịt_heo 1 miếng vừa_ăn - Muối 1 ít - Hành_tím hoặc hành_tây 1 ít - Gừng 1 ít - Giấm ăn tùy chọn - Rượu trắng tùy chọn Sơ_chế - Ngâm thịt_heo trong nước_muối 5-10 phút để chất bẩn_tiết ra - Chần_thịt trong hỗn_hợp nước , giấm và muối khoảng 2-3 phút rồi rửa lại bằng nước_sạch Cách chế_biến - Chuẩn_bị nồi nước lạnh , cho thịt vào - Thêm muối , hành , gừng vào nồi - Luộc thịt khoảng 20-30 phút là thịt chín - Vớt_bọt thường_xuyên để nước trong - Khi thịt gần chín có_thể thêm chút giấm hoặc rượu trắng để thịt trắng đẹp hơn Hoàn_thành món_ăn Sau khi chín , vớt thịt cho vào nước_đá ngâm khoảng 15-20 phút để thịt săn chắc rồi thái_lát mỏng , dùng kèm nước_mắm chua_ngọt hoặc mắm_tôm . Muốn kiểm_tra thịt chín chưa thì lấy đũa xiên vào , nếu xuyên qua dễ_dàng là được , chúc bạn luộc thịt ngon .
```

**ID 205**

- Câu hỏi gốc: Bò xào đậu que làm vậy có bị dai không ta
- Câu hỏi tách từ: `Bò_xào đậu_que làm_vậy có bị dai không ta`

Câu trả lời gốc:

```text
Bò xào đậu que giòn ngọt, thịt bò mềm, xào nhanh lửa lớn nên rau vẫn giữ được màu xanh đẹp mắt.

Nguyên liệu cần chuẩn bị (cho 2 người)
- Thịt bò 300g
- Đậu que 200g
- Dầu ăn 2 muỗng canh
- Gia vị hạt nêm, bột ngọt, muối

Sơ chế
- Thịt bò xát gừng để khử mùi, rửa sạch, cắt lát mỏng vừa ăn
- Đậu que tước xơ 2 bên, rửa sạch, cắt khúc dài 3-4 lóng tay, trụng sơ 1 phút trong nước có muối

Cách chế biến
Xào đậu
- Xào đậu que khoảng 3 phút
- Thêm nước và chút muối, xào thêm 5 phút
Xào thịt
- Xào thịt bò với hạt nêm, bột ngọt, muối khoảng 2 phút
- Thêm chút nước, xào thêm 3 phút
Trộn chung
- Cho đậu vào chung với thịt, xào đều 3 phút rồi nêm nếm lại

Hoàn thành món ăn
Cho ra dĩa, dùng nóng ngay để đậu que giữ được độ giòn.

Món này xào nhanh gọn, hợp cho bữa cơm ngày bận rộn.
```

Câu trả lời tách từ (17 câu):

```text
Bò_xào đậu que giòn ngọt , thịt_bò mềm , xào nhanh lửa lớn nên rau vẫn giữ được màu xanh đẹp_mắt . Nguyên_liệu cần chuẩn_bị ( cho 2 người ) - Thịt_bò 300g - Đậu que 200g - Dầu_ăn 2 muỗng_canh - Gia_vị hạt_nêm , bột_ngọt , muối Sơ_chế - Thịt_bò xát gừng để khử mùi , rửa_sạch , cắt lát mỏng vừa_ăn - Đậu_que tước xơ 2 bên , rửa_sạch , cắt khúc dài 3-4 lóng tay , trụng sơ 1 phút trong nước có muối Cách chế_biến Xào đậu - Xào đậu que khoảng 3 phút - Thêm nước và chút muối , xào thêm 5 phút Xào thịt - Xào thịt_bò với hạt_nêm , bột_ngọt , muối khoảng 2 phút - Thêm chút nước , xào thêm 3 phút Trộn chung - Cho đậu vào chung với thịt , xào đều 3 phút rồi nêm nếm lại Hoàn_thành món_ăn Cho ra dĩa , dùng nóng ngay để đậu que giữ được độ giòn . Món này xào nhanh gọn , hợp cho bữa_cơm ngày bận_rộn .
```

**ID 194**

- Câu hỏi gốc: Chỉ cách kho cánh gà kho gừng cho đậm vị đi
- Câu hỏi tách từ: `Chỉ cách kho cánh_gà kho gừng cho đậm_vị đi`

Câu trả lời gốc:

```text
Cánh gà kho gừng thơm mùi gừng nồng ấm, vị mặn ngọt vừa miệng, món này làm nhanh mà hao cơm.

Nguyên liệu cần chuẩn bị (cho 4 người)
- Cánh gà 500g
- Gừng 1 củ nhỏ
- Tỏi 4 tép
- Hành tím 4 củ
- Nước mắm 4 muỗng canh
- Dầu hào 1 muỗng canh
- Dầu ăn 2 muỗng canh
- Ớt 2 quả
- Gia vị muối, hạt nêm, đường, bột ngọt

Sơ chế
- Cánh gà rửa sạch, chặt miếng vừa ăn
- Gừng cắt sợi, ớt cắt lát, tỏi và hành tím băm nhuyễn

Cách chế biến
Ướp gà
- Ướp cánh gà với dầu hào, hạt nêm, đường, bột ngọt, nước mắm, dầu ăn, phân nửa lượng gừng cùng toàn bộ tỏi và hành tím băm
- Ướp khoảng 30 phút cho thấm
Kho gà
- Đun lửa nhỏ cho đường chuyển sang màu nâu cánh gián rồi cho gà vào
- Đảo gà khoảng 2 phút, thêm nước ngập gà
- Kho lửa vừa khoảng 20-25 phút
Hoàn thiện
- Khi nước hơi sệt lại thì nêm nếm lại gia vị
- Cho phần gừng và ớt còn lại vào, đảo thêm 5 phút rồi tắt bếp

Hoàn thành món ăn
Gắp gà ra dĩa, rưới ít nước kho lên trên, ăn nóng với cơm trắng là ngon nhất.

Món này kho không khó, chúc bạn làm thành công.
```

Câu trả lời tách từ (24 câu):

```text
Cánh gà kho gừng thơm mùi gừng nồng_ấm , vị mặn_ngọt vừa miệng , món này làm nhanh mà hao cơm . Nguyên_liệu cần chuẩn_bị ( cho 4 người ) - Cánh gà 500g - Gừng 1 củ nhỏ - Tỏi 4 tép - Hành_tím 4 củ - Nước_mắm 4 muỗng_canh - Dầu_hào 1 muỗng_canh - Dầu_ăn 2 muỗng_canh - Ớt 2 quả - Gia_vị muối , hạt_nêm , đường , bột_ngọt Sơ_chế - Cánh gà rửa_sạch , chặt miếng vừa_ăn - Gừng cắt sợi , ớt cắt lát , tỏi và hành_tím băm nhuyễn Cách chế_biến Ướp gà - Ướp cánh_gà với dầu_hào , hạt_nêm , đường , bột_ngọt , nước_mắm , dầu_ăn , phân_nửa lượng gừng cùng toàn_bộ tỏi và hành_tím băm - Ướp khoảng 30 phút cho thấm Kho gà - Đun lửa nhỏ cho đường chuyển sang màu nâu cánh_gián rồi cho gà vào - Đảo gà khoảng 2 phút , thêm nước ngập gà - Kho lửa vừa khoảng 20-25 phút Hoàn_thiện - Khi nước hơi_sệt lại thì nêm_nếm lại gia_vị - Cho phần gừng và ớt còn lại vào , đảo thêm 5 phút rồi tắt_bếp Hoàn_thành món_ăn Gắp gà ra dĩa , rưới ít nước kho lên trên , ăn_nóng với cơm_trắng là ngon nhất . Món này kho không khó , chúc bạn làm thành_công .
```

### 03_huong_dan_nau_mon_mien_tay

**ID 69**

- Câu hỏi gốc: Hủ tiếu Sa Đéc nấu như thế nào
- Câu hỏi tách từ: `Hủ tiếu_Sa Đéc_nấu như_thế_nào`

Câu trả lời gốc:

```text
Hủ tiếu Sa Đéc là đặc sản của Đồng Tháp. Sợi hủ tiếu làm từ bột gạo có màu trắng đục, sợi to, mềm và dai vừa phải, ăn với nước lèo ngọt thanh cùng tôm, gan và xá xíu.

Nguyên liệu cần chuẩn bị (cho 4 người, chuẩn bị 30 phút và nấu khoảng 40 phút)
- Hủ tiếu Sa Đéc 1kg
- Xương heo hoặc xương ống 1kg
- Thịt xay 300g
- Xá xíu 300g
- Tôm tươi 300g
- Gan 300g
- Giá 200g
- Trứng cút 30 quả
- Cải trắng 2 củ
- Cần tàu, hành lá, hẹ
- Chanh 2 trái
- Tỏi, đường, bột ngọt, gia vị nêm

Sơ chế
- Xương rửa sạch rồi trụng sơ qua nước sôi
- Tôm chẻ lưng, lột vỏ, chà muối rồi rửa sạch
- Trứng cút luộc chín, bóc vỏ
- Gan luộc với muối rồi thái miếng
- Rau cắt theo kích thước vừa ăn

Cách chế biến
Nấu nước lèo
- Nấu xương heo cùng cải trắng cắt khúc, vặn lửa nhỏ cho xương mềm
- Vớt bọt để nước lèo trong rồi nêm cho vừa ăn
Xào thịt
- Xào thịt xay với tỏi băm, thêm đường và bột ngọt rồi nêm lại cho vừa

Hoàn thành món ăn
Trụng hủ tiếu trong nước sôi cho mềm rồi để ráo, cho vào tô. Thêm thịt xay, trứng cút, tôm, gan, xá xíu, hẹ và cần cắt nhỏ rồi chan nước lèo nóng.

Vậy là đã hoàn thành tô hủ tiếu Sa Đéc, chúc bạn có bữa sáng thật ngon.
```

Câu trả lời tách từ (28 câu):

```text
Hủ_tiếu Sa_Đéc là đặc_sản của Đồng_Tháp . Sợi hủ_tiếu làm từ bột gạo có màu trắng đục , sợi to , mềm và dai vừa_phải , ăn với nước lèo ngọt_thanh cùng tôm , gan và xá_xíu . Nguyên_liệu cần chuẩn_bị ( cho 4 người , chuẩn_bị 30 phút và nấu khoảng 40 phút ) - Hủ_tiếu Sa_Đéc 1kg - Xương heo hoặc xương ống 1kg - Thịt xay 300g - Xá_xíu 300g - Tôm tươi 300g - Gan 300g - Giá 200g - Trứng cút 30 quả - Cải_trắng 2 củ - Cần tàu , hành_lá , hẹ - Chanh 2 trái - Tỏi , đường , bột_ngọt , gia_vị nêm Sơ_chế - Xương rửa_sạch rồi trụng sơ_qua nước_sôi - Tôm chẻ_lưng , lột vỏ , chà_muối rồi rửa_sạch - Trứng cút luộc chín , bóc vỏ - Gan luộc với muối rồi thái_miếng - Rau_cắt theo kích_thước vừa_ăn Cách chế_biến Nấu nước lèo - Nấu xương heo cùng cải_trắng cắt_khúc , vặn lửa nhỏ cho xương mềm - Vớt_bọt để nước lèo trong rồi nêm cho vừa_ăn Xào thịt - Xào thịt xay với tỏi_băm , thêm đường và bột_ngọt rồi nêm lại cho vừa Hoàn_thành món_ăn Trụng hủ_tiếu trong nước_sôi cho mềm rồi để ráo , cho vào tô . Thêm thịt xay , trứng cút , tôm , gan , xá_xíu , hẹ và cần cắt nhỏ rồi chan nước lèo nóng . Vậy là đã hoàn_thành tô hủ_tiếu Sa_Đéc , chúc bạn có bữa sáng thật ngon .
```

**ID 47**

- Câu hỏi gốc: Bún nước lèo Sóc Trăng nấu như thế nào
- Câu hỏi tách từ: `Bún nước lèo Sóc_Trăng nấu như_thế_nào`

Câu trả lời gốc:

```text
Bún nước lèo là đặc sản của Sóc Trăng. Nước dùng nấu từ mắm cá linh nên thơm và đậm đà, ăn cùng cá lóc, tôm và nhiều loại rau.

Nguyên liệu cần chuẩn bị (cho 3 người, chuẩn bị 30 phút và nấu khoảng 1 giờ)
- Bún tươi 500g
- Cá lóc 250g
- Tôm sú 300g
- Mắm cá linh 100ml
- Nước dừa tươi 200ml
- Bắp chuối 1 cái
- Giá đỗ 100g
- Hẹ 100g
- Húng quế 50g
- Sả 3 cây
- Ớt 10g
- Chanh 1 trái
- Nước lọc 800ml
- Hạt nêm, bột ngọt, đường vừa ăn

Sơ chế
- Cá lóc làm sạch, phi lê và bỏ xương
- Tôm bóc vỏ và rút chỉ
- Sả đập dập rồi cắt nhỏ
- Chanh cắt tư
- Bắp chuối bào sợi rồi ngâm nước muối

Cách chế biến
- Nấu 500ml nước với mắm cá linh, tôm và cá lóc cho sôi rồi hạ lửa nhỏ nấu 20 phút
- Vớt tôm và cá ra, sau đó lọc lấy nước
- Thêm 800ml nước vào, cho sả và ớt vào rồi đun sôi
- Nêm hạt nêm, bột ngọt, đường, cho nước dừa vào và nấu thêm 15 phút

Hoàn thành món ăn
Xếp bún vào tô, cho tôm và cá lên trên rồi chan nước dùng nóng. Rắc hẹ lên mặt tô và ăn kèm bắp chuối, giá, húng quế với chanh.

Vậy là đã hoàn thành tô bún nước lèo, chúc bạn nấu ăn vui vẻ.
```

Câu trả lời tách từ (29 câu):

```text
Bún nước lèo là đặc_sản của Sóc_Trăng . Nước_dùng nấu từ mắm_cá_linh nên thơm và đậm_đà , ăn cùng cá_lóc , tôm và nhiều loại rau . Nguyên_liệu cần chuẩn_bị ( cho 3 người , chuẩn_bị 30 phút và nấu khoảng 1 giờ ) - Bún tươi 500g - Cá_lóc 250g - Tôm_sú 300g - Mắm_cá_linh 100ml - Nước_dừa_tươi 200ml - Bắp chuối 1 cái - Giá đỗ 100g - Hẹ 100g - Húng quế 50g - Sả 3 cây - Ớt 10g - Chanh 1 trái - Nước_lọc 800ml - Hạt_nêm , bột_ngọt , đường vừa_ăn Sơ_chế - Cá_lóc làm sạch , phi_lê và bỏ xương - Tôm bóc vỏ và rút chỉ - Sả đập dập rồi cắt nhỏ - Chanh cắt tư - Bắp chuối_bào sợi rồi ngâm nước_muối Cách chế_biến - Nấu 500ml nước với mắm_cá_linh , tôm và cá_lóc cho sôi rồi hạ_lửa nhỏ nấu 20 phút - Vớt tôm và cá ra , sau đó lọc lấy nước - Thêm 800ml nước vào , cho sả và ớt vào rồi đun sôi - Nêm hạt_nêm , bột_ngọt , đường , cho nước_dừa vào và nấu thêm 15 phút Hoàn_thành món_ăn Xếp bún vào tô , cho tôm và cá lên trên rồi chan nước_dùng nóng . Rắc hẹ lên mặt tô và ăn_kèm bắp chuối , giá , húng_quế với chanh . Vậy là đã hoàn_thành tô bún nước lèo , chúc bạn nấu_ăn vui_vẻ .
```

**ID 111**

- Câu hỏi gốc: Cá rô kho khế nấu như thế nào
- Câu hỏi tách từ: `Cá_rô kho khế nấu như_thế_nào`

Câu trả lời gốc:

```text
Cá rô kho khế là món dân dã của miền Tây. Thịt cá rô mềm mà không nát, nước kho chua ngọt nhờ khế nên ăn rất bắt cơm.

Nguyên liệu cần chuẩn bị (cho 3 người, làm trong khoảng 45 phút)
- Cá rô 2 con
- Khế 6 trái
- Tỏi băm 10g
- Hành băm 10g
- Ớt băm 10g
- Hành lá 2 nhánh
- Dầu ăn 1 muỗng canh
- Đường 1 muỗng canh
- Nước mắm 2 muỗng canh
- Tiêu 1 muỗng cà phê
- Bột ngọt 1/2 muỗng cà phê

Sơ chế
- Cá rô bỏ ruột, rửa với nước muối loãng rồi khía vài đường trên thân
- Khế rửa sạch, cắt lát hình ngôi sao dày khoảng 1cm
- Hành lá cắt khúc 1cm

Cách chế biến
- Chiên sơ cá hai mặt trong dầu nóng cho săn lại
- Phi thơm tỏi băm rồi cho một phần khế vào xào cho săn, thêm đường, nước mắm, tiêu, bột ngọt và ớt băm
- Cho cá vào cùng 200ml nước lọc, nấu đến khi nước sôi và hơi cạn
- Thêm phần khế còn lại, đảo khoảng 5 phút
- Tắt bếp rồi cho hành lá vào

Hoàn thành món ăn
Múc cá ra bát cùng khế và nước kho, trang trí thêm hành lá.

Vậy là đã xong nồi cá rô kho khế, chúc bạn nấu ăn vui vẻ.
```

Câu trả lời tách từ (26 câu):

```text
Cá_rô kho khế là món dân_dã của miền_Tây . Thịt cá_rô mềm mà không nát , nước kho chua_ngọt nhờ khế nên ăn rất bắt cơm . Nguyên_liệu cần chuẩn_bị ( cho 3 người , làm trong khoảng 45 phút ) - Cá_rô 2 con - Khế 6 trái - Tỏi_băm 10g - Hành_băm 10g - Ớt băm 10g - Hành_lá 2 nhánh - Dầu_ăn 1 muỗng_canh - Đường 1 muỗng_canh - Nước_mắm 2 muỗng_canh - Tiêu 1 muỗng_cà_phê - Bột_ngọt 1/2 muỗng_cà_phê Sơ_chế - Cá_rô bỏ ruột , rửa với nước_muối loãng rồi khía vài đường trên thân - Khế rửa_sạch , cắt lát_hình ngôi_sao dày khoảng 1cm - Hành_lá cắt khúc 1cm Cách chế_biến - Chiên sơ_cá hai mặt trong dầu nóng cho săn lại - Phi_thơm tỏi_băm rồi cho một phần khế vào xào cho săn , thêm đường , nước_mắm , tiêu , bột_ngọt và ớt băm - Cho cá vào cùng 200ml nước_lọc , nấu đến khi nước_sôi và hơi cạn - Thêm phần khế còn lại , đảo khoảng 5 phút - Tắt_bếp rồi cho hành_lá vào Hoàn_thành món_ăn Múc cá ra bát cùng khế và nước kho , trang_trí thêm hành_lá . Vậy là đã xong nồi cá_rô kho_khế , chúc bạn nấu_ăn vui_vẻ .
```

### 04_mon_an_mien_tay

**ID 545**

- Câu hỏi gốc: Tết ở miền Tây thường ăn những gì
- Câu hỏi tách từ: `Tết ở miền_Tây thường ăn những gì`

Câu trả lời gốc:

```text
Tết ở miền Tây không thể thiếu bánh tét gói lá chuối. Thịt kho tàu (thịt kho nước dừa với trứng) là món truyền thống ngày Tết.

Dưa kiệu, củ cải muối ăn kèm với bánh tét rất hợp. Ngoài ra còn có mứt dừa, mứt me, kẹo chuối.

Lạp xưởng, nem chua, chả lạnh cũng phổ biến trong mâm Tết miền Tây
```

Câu trả lời tách từ (5 câu):

```text
Tết ở miền_Tây không_thể thiếu bánh_tét gói lá chuối . Thịt kho tàu ( thịt kho nước_dừa với trứng ) là món truyền_thống ngày Tết . Dưa_kiệu , củ cải_muối ăn_kèm với bánh_tét rất hợp . Ngoài_ra còn có mứt dừa , mứt_me , kẹo chuối . Lạp_xưởng , nem chua , chả_lạnh cũng phổ_biến trong mâm Tết miền_Tây
```

**ID 534**

- Câu hỏi gốc: Mùa nước nổi ở miền Tây có món gì đặc biệt
- Câu hỏi tách từ: `Mùa nước nổi ở miền_Tây có món gì đặc_biệt`

Câu trả lời gốc:

```text
Mùa nước nổi từ khoảng tháng 8 đến tháng 11 là mùa cá linh và bông điên điển. Canh chua cá linh bông điên điển là món đặc trưng chỉ có vào mùa này.

Cá linh non kho me, cá linh chiên giòn chấm mắm me cũng là đặc sản mùa nước. Ngoài ra còn có chuột đồng nướng, ốc lác hấp sả, rau tập tàng.

Đây là mùa ẩm thực phong phú nhất ở miền Tây
```

Câu trả lời tách từ (5 câu):

```text
Mùa nước nổi từ khoảng tháng 8 đến tháng 11 là mùa cá_linh và bông_điên_điển . Canh_chua cá_linh bông_điên_điển là món đặc_trưng chỉ có vào mùa này . Cá_linh non kho me , cá_linh chiên_giòn chấm mắm_me cũng là đặc_sản mùa nước . Ngoài_ra còn có chuột đồng_nướng , ốc_lác hấp_sả , rau tập_tàng . Đây là mùa ẩm_thực_phong_phú nhất ở miền_Tây
```

**ID 566**

- Câu hỏi gốc: Dừa miền Tây loại nào nấu ăn ngon nhất
- Câu hỏi tách từ: `Dừa miền_Tây loại nào nấu_ăn ngon nhất`

Câu trả lời gốc:

```text
Dừa xiêm nước ngọt và nhiều nên dùng uống hoặc nấu nước kho. Dừa khô (dừa già) dùng nạo lấy cơm dừa vắt nước cốt để nấu cà ri, xào lăn.

Dừa ta vỏ dày, cơm dừa nhiều nên vắt nước cốt béo hơn. Nước dừa tươi dùng kho thịt kho cá thì chọn dừa xiêm là ngọt nhất.

Mỗi loại dừa phù hợp với mục đích nấu ăn khác nhau
```

Câu trả lời tách từ (5 câu):

```text
Dừa xiêm nước_ngọt và nhiều nên dùng uống hoặc nấu nước kho . Dừa khô ( dừa già ) dùng nạo_lấy cơm dừa vắt nước_cốt để nấu cà_ri , xào_lăn . Dừa ta vỏ dày , cơm dừa nhiều nên vắt nước cốt_béo hơn . Nước_dừa_tươi dùng kho thịt kho cá thì chọn dừa xiêm là ngọt nhất . Mỗi loại dừa phù_hợp với mục_đích nấu_ăn khác nhau
```

### 05_nguyen_lieu_gia_vi

**ID 305**

- Câu hỏi gốc: Bột cà ri dùng trong nấu ăn Việt Nam sao
- Câu hỏi tách từ: `Bột cà_ri dùng trong nấu_ăn Việt_Nam sao`

Câu trả lời gốc:

```text
Bột cà ri là hỗn hợp nhiều loại gia vị xay nhuyễn, có màu vàng và mùi thơm ấm nồng. Trong nấu ăn Việt Nam thì bột cà ri hay dùng để nấu cà ri gà, cà ri bò hoặc cà ri chay.

Miền Tây cũng hay nấu cà ri vịt ăn với bánh mì. Khi nấu cà ri thì nên phi thơm bột cà ri với dầu trước khi cho nguyên liệu vào để vị thơm hơn
```

Câu trả lời tách từ (4 câu):

```text
Bột cà_ri là hỗn_hợp nhiều loại gia_vị xay_nhuyễn , có màu vàng và mùi thơm ấm nồng . Trong nấu_ăn Việt_Nam thì bột cà_ri hay dùng để nấu cà_ri gà , cà_ri bò hoặc cà_ri chay . Miền_Tây cũng hay nấu cà_ri vịt ăn với bánh_mì . Khi nấu cà_ri thì nên phi_thơm bột cà_ri với dầu trước khi cho nguyên_liệu vào để vị thơm hơn
```

**ID 294**

- Câu hỏi gốc: Nước tương là gì và dùng trong món nào
- Câu hỏi tách từ: `Nước tương_là gì và dùng trong món nào`

Câu trả lời gốc:

```text
Nước tương hay còn gọi là xì dầu, là loại nước chấm làm từ đậu nành lên men. Vị nước tương mặn hơi ngọt, màu nâu sẫm và không có mùi tanh như nước mắm.

Nước tương hay dùng trong các món xào, kho, chấm và ướp thịt. Người ăn chay thường dùng nước tương thay nước mắm để nêm nếm
```

Câu trả lời tách từ (4 câu):

```text
Nước_tương hay còn gọi_là xì_dầu , là loại nước_chấm làm từ đậu_nành lên_men . Vị nước tương_mặn hơi ngọt , màu nâu_sẫm và không có mùi tanh như nước_mắm . Nước_tương hay dùng trong các món xào , kho , chấm và ướp thịt . Người ăn_chay thường dùng nước tương_thay nước_mắm để nêm nếm
```

**ID 326**

- Câu hỏi gốc: Tía tô dùng trong món gì
- Câu hỏi tách từ: `Tía tô dùng trong món gì`

Câu trả lời gốc:

```text
Tía tô có lá màu tím đỏ ở mặt dưới, mùi thơm nồng rất đặc trưng. Tía tô hay ăn kèm với các món cháo, bún ốc, canh hoặc cuốn chung với thịt.

Ở miền Bắc thì tía tô rất phổ biến, ăn kèm hầu hết các món bún. Miền Tây thì ít dùng tía tô hơn nhưng đôi khi cũng ăn kèm với cháo hoặc lẩu
```

Câu trả lời tách từ (4 câu):

```text
Tía tô có lá màu tím đỏ ở mặt dưới , mùi thơm nồng rất đặc_trưng . Tía tô hay ăn_kèm với các món cháo , bún_ốc , canh hoặc cuốn chung với thịt . Ở miền Bắc thì tía_tô rất phổ_biến , ăn_kèm hầu_hết các món bún . Miền_Tây thì ít dùng tía_tô hơn nhưng đôi_khi cũng ăn_kèm với cháo hoặc lẩu
```

### 06_thay_the_nguyen_lieu

**ID 385**

- Câu hỏi gốc: Đường thốt nốt thay bằng gì
- Câu hỏi tách từ: `Đường_thốt_nốt thay bằng gì`

Câu trả lời gốc:

```text
Đường thốt nốt có vị ngọt thanh đặc trưng nên khó thay thế hoàn toàn. Tuy nhiên bạn có thể dùng đường nâu (brown sugar) vì có hương vị gần giống nhất.

Đường phèn cũng là lựa chọn thay thế được vì vị ngọt thanh. Đường cát trắng thì dùng được nhưng sẽ không có mùi thơm đặc trưng như đường thốt nốt
```

Câu trả lời tách từ (4 câu):

```text
Đường_thốt_nốt có vị ngọt_thanh đặc_trưng nên khó thay_thế hoàn_toàn . Tuy_nhiên bạn có_thể dùng đường nâu ( brown sugar ) vì có hương_vị gần giống nhất . Đường_phèn cũng là lựa_chọn thay_thế được vì vị ngọt_thanh . Đường cát trắng thì dùng được nhưng sẽ không có mùi thơm đặc_trưng như đường_thốt_nốt
```

**ID 374**

- Câu hỏi gốc: Không có giấm thì dùng gì thay
- Câu hỏi tách từ: `Không có giấm thì dùng gì thay`

Câu trả lời gốc:

```text
Nếu không có giấm thì bạn có thể dùng nước cốt chanh hoặc tắc để tạo vị chua. Nước chanh chua tươi hơn giấm nên phù hợp với nhiều món trộn, gỏi.

Nếu cần giấm để ngâm đồ chua thì có thể dùng nước cốt me pha loãng thay thế. Tuy nhiên mỗi loại chua có hương vị khác nhau nên món ăn sẽ hơi khác so với dùng giấm
```

Câu trả lời tách từ (4 câu):

```text
Nếu không có giấm thì bạn có_thể dùng nước cốt_chanh hoặc tắc để tạo vị chua . Nước chanh chua_tươi hơn giấm nên phù_hợp với nhiều món trộn , gỏi . Nếu cần giấm để ngâm đồ_chua thì có_thể dùng nước cốt_me pha loãng thay_thế . Tuy_nhiên mỗi loại chua có hương_vị khác nhau nên món_ăn sẽ hơi khác so với dùng giấm
```

**ID 406**

- Câu hỏi gốc: Lá dứa không có thì làm sao cho cơm thơm
- Câu hỏi tách từ: `Lá dứa không có thì làm_sao cho cơm thơm`

Câu trả lời gốc:

```text
Nếu không có lá dứa thì bạn có thể cho vài giọt nước cốt dừa vào nồi cơm để cơm thơm và dẻo hơn. Một cách khác là dùng gạo thơm Jasmine vì loại gạo này tự nhiên đã có mùi thơm.

Cho thêm chút muối vào nồi cơm cũng giúp cơm ngon hơn dù không có mùi thơm lá dứa. Lá dứa chủ yếu tạo mùi thơm nên thiếu thì cơm vẫn nấu bình thường
```

Câu trả lời tách từ (4 câu):

```text
Nếu không có lá dứa thì bạn có_thể cho vài giọt nước_cốt_dừa vào nồi cơm để cơm_thơm và dẻo hơn . Một cách khác là dùng gạo thơm_Jasmine vì loại gạo này tự_nhiên đã có mùi thơm . Cho thêm chút muối vào nồi cơm cũng giúp cơm ngon hơn dù không có mùi thơm lá dứa . Lá dứa chủ_yếu tạo mùi thơm nên thiếu thì cơm vẫn nấu bình_thường
```

### 07_dieu_chinh_cong_thuc

**ID 465**

- Câu hỏi gốc: Chả giò chiên bị mềm không giòn thì sửa sao
- Câu hỏi tách từ: `Chả giò_chiên bị mềm không giòn thì sửa sao`

Câu trả lời gốc:

```text
Chả giò chiên bị mềm thường do dầu chưa đủ nóng hoặc cho quá nhiều chả vào một lúc làm hạ nhiệt dầu. Bạn nên chiên hai lần, lần đầu chiên lửa vừa cho chín bên trong, lần hai chiên lửa lớn cho giòn vỏ.

Để chả giò trên giấy thấm dầu ngay khi vớt ra. Nếu chả giò đã mềm thì cho vào lò nướng hoặc nồi chiên không dầu ở nhiệt độ cao vài phút sẽ giòn lại
```

Câu trả lời tách từ (4 câu):

```text
Chả giò_chiên bị mềm_thường do dầu chưa đủ nóng hoặc cho quá nhiều chả vào một lúc làm hạ nhiệt_dầu . Bạn nên chiên hai lần , lần đầu chiên lửa vừa cho chín bên trong , lần hai chiên lửa lớn cho giòn vỏ . Để chả giò trên giấy thấm dầu ngay khi vớt ra . Nếu chả_giò đã mềm thì cho vào lò nướng hoặc nồi_chiên không dầu ở nhiệt_độ cao vài phút sẽ giòn lại
```

**ID 454**

- Câu hỏi gốc: Công thức ghi khẩu phần 6 nhưng nhà mình 3 người thì sao
- Câu hỏi tách từ: `Công_thức ghi khẩu_phần 6 nhưng nhà mình 3 người thì sao`

Câu trả lời gốc:

```text
Bạn chia tất cả nguyên liệu cho hai là ra khẩu phần 3 người. Hoặc bạn cứ nấu nguyên công thức cho 6 người rồi để dư cất tủ lạnh ăn bữa sau.

Nhiều món kho, hầm, canh để hôm sau hâm lại ăn vẫn ngon. Tùy món mà bạn quyết định nấu ít hay nấu dư để tiết kiệm thời gian
```

Câu trả lời tách từ (4 câu):

```text
Bạn chia tất_cả nguyên_liệu cho hai là ra khẩu_phần 3 người . Hoặc bạn cứ nấu_nguyên công_thức cho 6 người rồi để dư_cất tủ_lạnh ăn bữa sau . Nhiều món kho , hầm , canh để hôm sau hâm lại ăn vẫn ngon . Tùy món mà bạn quyết_định nấu ít hay nấu_dư để tiết_kiệm thời_gian
```

**ID 486**

- Câu hỏi gốc: Chảo không chống dính thì chiên trứng sao cho không dính
- Câu hỏi tách từ: `Chảo không chống dính thì chiên trứng sao cho không dính`

Câu trả lời gốc:

```text
Chiên trứng trên chảo thường thì bạn phải đun nóng chảo kỹ trước, cho nhiều dầu hơn bình thường. Khi dầu nóng già và bắt đầu có khói nhẹ thì mới cho trứng vào.

Không lật trứng quá sớm, đợi mặt dưới vàng đều rồi mới lật. Phết mỡ heo lên chảo thay dầu ăn cũng giúp chống dính tốt hơn
```

Câu trả lời tách từ (4 câu):

```text
Chiên trứng trên chảo thường thì bạn phải đun nóng_chảo kỹ trước , cho nhiều dầu hơn bình_thường . Khi dầu nóng_già và bắt_đầu có khói nhẹ thì mới cho trứng vào . Không lật trứng quá sớm , đợi mặt dưới vàng đều rồi mới lật . Phết mỡ heo lên chảo thay dầu_ăn cũng giúp chống dính tốt hơn
```

### 08_dinh_duong

**ID 625**

- Câu hỏi gốc: Phụ nữ mang thai cần chú ý ăn gì
- Câu hỏi tách từ: `Phụ_nữ mang thai cần chú_ý ăn gì`

Câu trả lời gốc:

```text
Phụ nữ mang thai cần ăn đa dạng để có đủ dưỡng chất cho cả mẹ và bé. Nên ăn nhiều rau xanh đậm, trái cây, thịt nạc, cá và trứng.

Uống sữa hoặc sản phẩm từ sữa để bổ sung canxi cho xương bé. Tránh ăn đồ sống, đồ tái, hải sản có thủy ngân cao.

Nên ăn đủ bữa và chia nhỏ bữa nếu bị nghén. Bổ sung sắt và axit folic theo chỉ dẫn bác sĩ
```

Câu trả lời tách từ (6 câu):

```text
Phụ_nữ mang thai cần ăn đa_dạng để có đủ dưỡng_chất cho cả mẹ và bé . Nên ăn nhiều rau_xanh đậm , trái_cây , thịt nạc , cá và trứng . Uống sữa hoặc sản_phẩm từ sữa để bổ_sung canxi cho xương bé . Tránh ăn_đồ sống , đồ tái , hải_sản có thủy ngân_cao . Nên ăn đủ bữa và chia nhỏ bữa nếu bị nghén . Bổ_sung sắt và axit_folic theo chỉ_dẫn bác_sĩ
```

**ID 614**

- Câu hỏi gốc: Ăn sáng có quan trọng không
- Câu hỏi tách từ: `Ăn sáng có quan_trọng không`

Câu trả lời gốc:

```text
Ăn sáng rất quan trọng vì cung cấp năng lượng cho cơ thể hoạt động sau một đêm dài. Bỏ bữa sáng dễ dẫn đến mệt mỏi, mất tập trung và ăn quá nhiều ở bữa trưa.

Bữa sáng nên có đủ tinh bột, chất đạm và chút rau hoặc trái cây. Một bát cháo, tô bún hoặc ổ bánh mì kèm rau là bữa sáng đơn giản nhưng đủ chất
```

Câu trả lời tách từ (4 câu):

```text
Ăn sáng rất quan_trọng vì cung_cấp năng_lượng cho cơ_thể hoạt_động sau một đêm dài . Bỏ bữa sáng dễ dẫn đến mệt_mỏi , mất tập_trung và ăn quá nhiều ở bữa trưa . Bữa sáng nên có đủ tinh_bột , chất_đạm và chút rau hoặc trái_cây . Một bát cháo , tô_bún hoặc ổ bánh_mì kèm rau là bữa sáng đơn_giản nhưng đủ chất
```

**ID 646**

- Câu hỏi gốc: Nấu cháo từ xương hầm có tốt không
- Câu hỏi tách từ: `Nấu cháo từ xương hầm có tốt không`

Câu trả lời gốc:

```text
Cháo nấu từ nước hầm xương rất thơm ngon và có thêm dưỡng chất từ xương. Nước hầm xương có chứa khoáng chất và collagen tốt cho xương khớp.

Nên hầm xương lửa nhỏ trong thời gian dài để lấy được nhiều chất. Cháo hầm xương phù hợp cho trẻ nhỏ, người lớn tuổi và người đang hồi phục sức khỏe
```

Câu trả lời tách từ (4 câu):

```text
Cháo nấu từ nước hầm xương rất thơm_ngon và có thêm dưỡng_chất từ xương . Nước hầm xương có chứa khoáng_chất và collagen tốt cho xương khớp . Nên hầm xương lửa nhỏ trong thời_gian dài để lấy_được nhiều chất . Cháo hầm xương phù_hợp cho trẻ nhỏ , người lớn_tuổi và người đang hồi_phục sức khỏe
```

### 09_goi_y_mon_theo_dinh_duong

**ID 705**

- Câu hỏi gốc: Mùa mưa nên ăn gì để tăng đề kháng
- Câu hỏi tách từ: `Mùa mưa nên ăn gì để tăng đề_kháng`

Câu trả lời gốc:

```text
Mùa mưa dễ bị cảm lạnh nên cần ăn đủ chất để tăng đề kháng. Ăn nhiều rau xanh, trái cây có nhiều vitamin như cam, bưởi, ổi.

Nấu canh gà gừng, cháo tỏi, súp hành tây đều tốt. Uống nước ấm, trà gừng thay vì nước đá lạnh.

Tỏi và gừng thêm vào món ăn hàng ngày giúp cơ thể ấm và tăng sức đề kháng tự nhiên
```

Câu trả lời tách từ (5 câu):

```text
Mùa mưa dễ bị cảm lạnh nên cần ăn đủ chất để tăng đề_kháng . Ăn nhiều rau_xanh , trái_cây có nhiều vitamin như cam , bưởi , ổi . Nấu canh gà gừng , cháo_tỏi , súp hành_tây đều tốt . Uống nước ấm , trà_gừng thay_vì nước_đá lạnh . Tỏi và gừng thêm vào món_ăn hàng ngày giúp cơ_thể ấm và tăng sức đề_kháng tự_nhiên
```

**ID 694**

- Câu hỏi gốc: Ăn gì vào buổi trưa cho người giảm cân
- Câu hỏi tách từ: `Ăn gì vào buổi trưa cho người giảm cân`

Câu trả lời gốc:

```text
Buổi trưa giảm cân vẫn nên ăn đủ no nhưng giảm phần cơm trắng và tăng rau. Có thể ăn cơm gạo lứt kèm ức gà luộc hoặc cá hấp với nhiều rau luộc.

Canh rau mồng tơi nấu tôm, đậu phụ kho sả cũng là món nhẹ mà đủ chất. Tránh cơm tấm sườn bì chả, bún bò hay phở bò vì phần ăn thường lớn
```

Câu trả lời tách từ (4 câu):

```text
Buổi trưa giảm cân vẫn nên ăn đủ no nhưng giảm phần cơm_trắng và tăng rau . Có_thể ăn cơm gạo lứt kèm_ức gà luộc hoặc cá_hấp với nhiều rau luộc . Canh rau mồng tơi nấu tôm , đậu phụ kho sả cũng là món nhẹ mà đủ chất . Tránh cơm tấm sườn bì_chả , bún_bò hay phở bò vì phần ăn thường lớn
```

**ID 726**

- Câu hỏi gốc: Gợi ý món ăn cho người không ăn được cay
- Câu hỏi tách từ: `Gợi_ý món_ăn cho người không ăn được cay`

Câu trả lời gốc:

```text
Người không ăn cay có thể ăn các món hấp, luộc, kho nhẹ. Cá hấp gừng, gà luộc, tôm hấp sả không cay mà ngon.

Canh bí đỏ nấu thịt bằm, canh bầu nấu tôm cũng rất thanh. Thịt kho trứng nước dừa ngọt nhẹ không cần ớt.

Nước chấm pha không ớt, dùng chanh tỏi tạo vị cũng rất ngon
```

Câu trả lời tách từ (5 câu):

```text
Người không ăn_cay có_thể ăn các món hấp , luộc , kho nhẹ . Cá hấp_gừng , gà luộc , tôm hấp_sả không cay mà ngon . Canh_bí đỏ nấu thịt bằm , canh bầu nấu tôm cũng rất thanh . Thịt kho trứng nước_dừa ngọt nhẹ không cần ớt . Nước_chấm pha không ớt , dùng chanh tỏi tạo_vị cũng rất ngon
```

### 10_bao_quan_che_bien

**ID 930**

- Câu hỏi gốc: Cách sơ chế tôm trước khi nấu
- Câu hỏi tách từ: `Cách sơ_chế tôm trước khi nấu`

Câu trả lời gốc:

```text
Tôm sơ chế cần rửa sạch, cắt râu, bẻ bỏ gai nhọn trên đầu tôm. Rút chỉ đen trên lưng tôm bằng cách dùng tăm hoặc dao nhỏ khứa nhẹ rồi rút ra.

Tùy món ăn mà lột vỏ hoặc để nguyên vỏ. Ướp tôm với chút muối, tiêu và tỏi băm khoảng mười lăm phút.

Tôm sơ chế xong nấu ngay hoặc cho vào tủ lạnh
```

Câu trả lời tách từ (5 câu):

```text
Tôm sơ_chế cần rửa_sạch , cắt râu , bẻ bỏ gai nhọn trên đầu tôm . Rút chỉ đen trên lưng tôm bằng cách dùng tăm hoặc dao nhỏ khứa nhẹ rồi rút ra . Tùy món_ăn mà lột vỏ hoặc để nguyên_vỏ . Ướp tôm với chút muối , tiêu và tỏi_băm khoảng mười_lăm phút . Tôm sơ_chế xong nấu ngay hoặc cho vào tủ_lạnh
```

**ID 919**

- Câu hỏi gốc: Cà chua bảo quản trong tủ lạnh hay để ngoài
- Câu hỏi tách từ: `Cà_chua bảo_quản trong tủ_lạnh hay để ngoài`

Câu trả lời gốc:

```text
Cà chua chưa chín nên để ngoài ở nhiệt độ phòng cho chín tự nhiên. Cà chua đã chín thì cho vào tủ lạnh để kéo dài thời gian sử dụng.

Tuy nhiên cà chua để tủ lạnh lâu sẽ mất bớt hương vị và bột hơn. Cà chua đã cắt thì bọc kín cho vào tủ lạnh ăn trong một đến hai ngày
```

Câu trả lời tách từ (4 câu):

```text
Cà_chua chưa chín nên để ngoài ở nhiệt_độ phòng cho chín tự_nhiên . Cà_chua đã chín thì cho vào tủ_lạnh để kéo_dài thời_gian sử_dụng . Tuy_nhiên cà_chua để tủ_lạnh lâu sẽ mất bớt hương_vị và bột hơn . Cà_chua đã cắt thì bọc kín cho vào tủ_lạnh ăn trong một đến hai ngày
```

**ID 951**

- Câu hỏi gốc: Bảo quản rau thơm tươi lâu bằng cách nào
- Câu hỏi tách từ: `Bảo_quản rau thơm tươi_lâu bằng cách nào`

Câu trả lời gốc:

```text
Rau thơm như húng quế, ngò, hành lá mua về cắt bỏ gốc hư, không rửa. Gói trong khăn giấy ẩm rồi cho vào túi ni lông để tủ lạnh giữ được bốn đến năm ngày.

Hoặc cắm rau thơm trong ly nước như cắm hoa, phủ túi ni lông lên, để tủ lạnh. Hành lá cũng bảo quản tương tự.

Rau thơm héo nhẹ vẫn dùng nấu ăn được
```

Câu trả lời tách từ (5 câu):

```text
Rau_thơm như húng_quế , ngò , hành_lá mua về cắt bỏ gốc hư , không rửa . Gói trong khăn giấy ẩm rồi cho vào túi ni_lông để tủ_lạnh giữ được bốn đến năm ngày . Hoặc cắm rau_thơm trong ly nước như cắm hoa , phủ túi ni lông lên , để tủ_lạnh . Hành_lá cũng bảo_quản tương_tự . Rau thơm héo nhẹ vẫn dùng nấu_ăn được
```

### 11_an_toan_thuc_pham

**ID 855**

- Câu hỏi gốc: Thức ăn nấu chín để ngoài bao lâu thì hư
- Câu hỏi tách từ: `Thức_ăn nấu chín để ngoài bao_lâu thì hư`

Câu trả lời gốc:

```text
Thức ăn nấu chín để ở nhiệt độ phòng không nên quá hai giờ. Trời nóng trên ba mươi lăm độ C thì chỉ nên để tối đa một giờ.

Vi khuẩn phát triển nhanh nhất ở khoảng từ năm đến sáu mươi độ C. Thức ăn thừa nên cho vào hộp kín, để tủ lạnh càng sớm càng tốt.

Khi ăn lại phải hâm nóng cho sôi lại
```

Câu trả lời tách từ (4 câu):

```text
Thức_ăn nấu chín để ở nhiệt_độ phòng_không nên quá hai giờ . Trời nóng trên ba_mươi lăm_độ C thì chỉ nên để tối_đa một giờ . Vi_khuẩn phát_triển nhanh nhất ở khoảng từ năm đến sáu mươi_độ C. Thức_ăn thừa nên cho vào hộp kín , để tủ_lạnh càng sớm càng tốt . Khi ăn lại phải hâm_nóng cho sôi lại
```

**ID 844**

- Câu hỏi gốc: Rửa rau sống sao cho sạch
- Câu hỏi tách từ: `Rửa rau_sống sao cho sạch`

Câu trả lời gốc:

```text
Rau sống cần rửa kỹ nhiều lần dưới vòi nước chảy. Ngâm rau trong nước muối loãng khoảng mười lăm phút rồi rửa lại bằng nước sạch.

Rau ăn sống nên ngâm trong nước có pha giấm loãng cũng giúp sạch hơn. Tách từng lá rau ra rửa chứ không rửa nguyên bó.

Rau sau khi rửa sạch nên ăn ngay, không để lâu ngoài nhiệt độ phòng
```

Câu trả lời tách từ (5 câu):

```text
Rau_sống cần rửa kỹ nhiều lần dưới vòi_nước chảy . Ngâm rau trong nước_muối loãng khoảng mười_lăm phút rồi rửa lại bằng nước_sạch . Rau ăn sống nên ngâm trong nước có pha giấm loãng cũng giúp sạch hơn . Tách từng lá rau ra rửa chứ không rửa nguyên_bó . Rau sau khi rửa_sạch nên ăn ngay , không để lâu ngoài nhiệt_độ phòng
```

**ID 876**

- Câu hỏi gốc: Rau quả ngâm hóa chất bảo quản nhận biết sao
- Câu hỏi tách từ: `Rau quả ngâm hóa_chất bảo_quản nhận_biết sao`

Câu trả lời gốc:

```text
Rau quả ngâm hóa chất bảo quản có thể nhận biết qua một số dấu hiệu. Rau để nhiều ngày vẫn xanh tươi bất thường thì đáng nghi.

Trái cây bóng đẹp quá mức, không có vết côn trùng cũng nên cẩn thận. Mùi hóa chất lạ trên bề mặt.

Tuy nhiên không phải lúc nào cũng nhận biết được bằng mắt thường nên mua ở nơi uy tín là cách tốt nhất
```

Câu trả lời tách từ (5 câu):

```text
Rau quả ngâm hóa_chất bảo_quản có_thể nhận_biết qua một_số dấu_hiệu . Rau để nhiều ngày vẫn xanh_tươi bất_thường thì đáng nghi . Trái_cây bóng đẹp quá mức , không có vết côn_trùng cũng_nên cẩn_thận . Mùi hóa chất lạ trên bề_mặt . Tuy_nhiên không phải lúc_nào cũng nhận_biết được bằng mắt thường nên mua ở nơi uy_tín là cách tốt nhất
```

### 12_goi_y_khi_om_met

**ID 785**

- Câu hỏi gốc: Trong kỳ kinh nguyệt nên ăn gì
- Câu hỏi tách từ: `Trong kỳ kinh_nguyệt nên ăn gì`

Câu trả lời gốc:

```text
Trong kỳ kinh nguyệt cơ thể mất máu nên cần bổ sung sắt từ thịt bò, rau xanh đậm, gan. Ăn trái cây giàu vitamin C như cam, ổi giúp hấp thu sắt tốt hơn.

Uống nước ấm, trà gừng có thể giúp giảm đau bụng. Socola đen (ăn ít) cũng có thể giúp tâm trạng tốt hơn.

Ăn chuối bổ sung kali cũng tốt trong kỳ kinh nguyệt
```

Câu trả lời tách từ (5 câu):

```text
Trong kỳ kinh_nguyệt cơ_thể mất máu nên cần bổ_sung sắt từ thịt_bò , rau_xanh đậm , gan . Ăn trái_cây giàu vitamin_C như cam , ổi giúp hấp thu sắt tốt hơn . Uống nước ấm , trà_gừng có_thể giúp giảm đau bụng . Socola đen ( ăn_ít ) cũng có_thể giúp tâm_trạng tốt hơn . Ăn chuối bổ_sung kali cũng tốt trong kỳ kinh_nguyệt
```

**ID 774**

- Câu hỏi gốc: Bị cảm uống gì cho dễ chịu
- Câu hỏi tách từ: `Bị cảm_uống gì cho dễ_chịu`

Câu trả lời gốc:

```text
Khi bị cảm nên uống nước ấm nhiều lần trong ngày. Nước gừng tươi nấu với mật ong uống ấm có thể giúp ấm họng.

Nước chanh ấm pha mật ong cũng được nhiều người dùng khi bị cảm. Trà hoa cúc uống ấm giúp thư giãn và dễ ngủ.

Tránh uống nước lạnh, nước đá và đồ uống có gas
```

Câu trả lời tách từ (5 câu):

```text
Khi bị cảm nên uống nước ấm nhiều lần trong ngày . Nước gừng tươi_nấu với mật_ong uống ấm có_thể giúp ấm_họng . Nước chanh_ấm pha mật_ong cũng được nhiều người dùng khi bị cảm . Trà hoa_cúc uống ấm giúp thư_giãn và dễ ngủ . Tránh uống nước lạnh , nước_đá và đồ uống có gas
```

**ID 806**

- Câu hỏi gốc: Ăn gì để bớt mệt khi học thi
- Câu hỏi tách từ: `Ăn gì để bớt mệt khi học thi`

Câu trả lời gốc:

```text
Khi học thi cần ăn đủ chất để não hoạt động tốt. Ăn sáng đầy đủ với cơm, xôi, bánh mì kèm trứng hoặc thịt.

Bữa phụ ăn chuối, các loại hạt, sữa chua giúp tỉnh táo. Uống đủ nước, có thể uống trà xanh nhẹ để tập trung.

Tránh ăn quá no vì buồn ngủ, tránh thức khuya ăn mì gói liên tục. Ngủ đủ giấc quan trọng hơn thức khuya nhồi bài
```

Câu trả lời tách từ (6 câu):

```text
Khi học thi cần ăn đủ chất để não hoạt_động tốt . Ăn sáng đầy_đủ với cơm , xôi , bánh_mì kèm trứng hoặc thịt . Bữa phụ ăn chuối , các loại hạt , sữa chua giúp tỉnh_táo . Uống đủ nước , có_thể uống trà xanh nhẹ để tập_trung . Tránh ăn quá no vì buồn_ngủ , tránh_thức khuya ăn mì gói liên_tục . Ngủ đủ giấc quan_trọng hơn thức khuya nhồi bài
```

## 6. Thống kê theo nhóm

| Nhóm | Số dòng | Từ TB / câu hỏi | Từ TB / câu trả lời | Câu TB / câu trả lời | Từ ghép TB / câu hỏi | Từ ghép TB / câu trả lời |
|---|---|---|---|---|---|---|
| 01_chao_hoi | 40 | 4.0 | 21.6 | 2.3 | 0.7 | 5.5 |
| 02_huong_dan_nau_an | 100 | 9.7 | 175.2 | 23.1 | 2.1 | 39.9 |
| 03_huong_dan_nau_mon_mien_tay | 150 | 5.9 | 202.0 | 27.8 | 2.0 | 43.4 |
| 04_mon_an_mien_tay | 80 | 6.8 | 52.8 | 4.5 | 2.0 | 13.3 |
| 05_nguyen_lieu_gia_vi | 80 | 6.4 | 60.3 | 4.1 | 1.4 | 10.4 |
| 06_thay_the_nguyen_lieu | 80 | 8.0 | 54.6 | 3.9 | 0.9 | 11.1 |
| 07_dieu_chinh_cong_thuc | 80 | 8.7 | 58.3 | 4.2 | 1.4 | 7.6 |
| 08_dinh_duong | 80 | 6.9 | 56.5 | 4.6 | 1.2 | 13.0 |
| 09_goi_y_mon_theo_dinh_duong | 80 | 7.3 | 54.8 | 5.1 | 1.1 | 10.5 |
| 10_bao_quan_che_bien | 78 | 6.6 | 59.3 | 5.0 | 1.3 | 8.8 |
| 11_an_toan_thuc_pham | 75 | 7.2 | 56.6 | 4.8 | 1.8 | 12.5 |
| 12_goi_y_khi_om_met | 70 | 7.2 | 57.7 | 5.5 | 1.3 | 12.4 |
