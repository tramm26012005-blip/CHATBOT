# Kiểm tra tách đoạn (Bài 4 – Phần I)

- Mô hình sinh vector: `bkai-foundation-models/vietnamese-bi-encoder` (PhoBERT, `can_tach_tu = true`).
- Giới hạn token mô hình: **256** (sentence_bert_config.json: max_seq_length = 256 (tokenizer.model_max_length không đặt, config.max_position_embeddings = 258 = 256 + 2)).
- Đếm token: `AutoTokenizer` của mô hình trên **bản đã tách từ** (hàm `TachTu` của `scripts/tach_tu.py`), tính cả tiêu đề cha và `<s>`, `</s>`.
- Tham số: `kich_thuoc_doan = 400`, `chong_lan = 50`, dự phòng 8 token, mục ngắn < 80 token, đoạn ngắn < 40 ký tự, ngưỡng toàn số 0.5, seed 42.
- Số cặp hỏi–đáp: 993 (Train 795, Test 198). Dòng trống đã bỏ: 0.
- Tiền xử lý: đúng hàm `tien_xu_ly` của `scripts/tach_tu.py` (NFC, thống nhất kiểu dấu, khoảng trắng lạ, nháy/gạch, dấu câu dính chữ), giữ nguyên `\n`. `noi_dung` là văn bản đã tiền xử lý.

## 0. Kích thước đoạn thực dùng

Kích thước thực dùng = `min(400, 256 − token tiêu đề cha − 8)`, tính riêng cho từng đoạn vì tiêu đề cha (Nhóm · Câu hỏi · Tên mục) dài ngắn khác nhau.

- Với tiêu đề không có tên mục: ngắn nhất **222**, trung vị **234**, lớn nhất **241** token nội dung.
- Con số 400 của slide 7 **không bao giờ được dùng**: mô hình chỉ nhận 256 token, để 400 thì phần đuôi bị mô hình cắt bỏ mà không cảnh báo.
- Chồng lấn thực dùng: cố định = `min(50, kích thước/2)`, đệ quy ≤ 50 token (theo mẩu), cấu trúc = 0.
- **Không cài cách cắt theo ngữ nghĩa** (slide 14): phải sinh vector cho từng câu để tìm điểm cắt, tốn kém, trong khi dataset đã có cấu trúc rõ (mục, tiêu đề con, gạch đầu dòng).

## Cách `cau_truc`

### 1. Phân bố độ dài (token)

| Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất | Số câu trả lời bị chia |
|---|---|---|---|---|---|
| 1208 | 21 | 91 | 118.1 | 250 | 187 |

| Nhóm | Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất |
|---|---|---|---|---|---|
| 01_chao_hoi | 40 | 21 | 33.5 | 38.8 | 74 |
| 02_huong_dan_nau_an | 169 | 58 | 178 | 172.4 | 250 |
| 03_huong_dan_nau_mon_mien_tay | 296 | 54 | 177.5 | 176.0 | 250 |
| 04_mon_an_mien_tay | 80 | 68 | 87 | 87.0 | 106 |
| 05_nguyen_lieu_gia_vi | 80 | 74 | 88 | 89.2 | 111 |
| 06_thay_the_nguyen_lieu | 80 | 38 | 79 | 79.7 | 104 |
| 07_dieu_chinh_cong_thuc | 80 | 69 | 83 | 83.4 | 105 |
| 08_dinh_duong | 80 | 72 | 81 | 81.6 | 95 |
| 09_goi_y_mon_theo_dinh_duong | 80 | 72 | 86 | 86.5 | 101 |
| 10_bao_quan_che_bien | 78 | 67 | 86 | 85.4 | 102 |
| 11_an_toan_thuc_pham | 75 | 65 | 78 | 79.0 | 93 |
| 12_goi_y_khi_om_met | 70 | 80 | 95 | 95.2 | 113 |

Nhận xét: đoạn dài nhất gấp 12 lần đoạn ngắn nhất. Chênh lệch chủ yếu do nhóm Chào hỏi rất ngắn còn công thức nấu ăn dài; các đoạn dài đều bị chặn dưới giới hạn mô hình.

### 2. Số đoạn vượt giới hạn mô hình

**0**

### 3. Không mất chữ

Ghép `noi_dung` theo `thu_tu_doan` (bỏ `so_ky_tu_chong_lan` ký tự đầu mỗi đoạn), bỏ khoảng trắng, so với câu trả lời đã tiền xử lý.

Số cặp hỏi–đáp lỗi: **0**

### 4. Đọc thử 5 đoạn ngẫu nhiên (seed 42)

**cau_truc_0049_03** (90 token)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà · Hoàn thành món ăn
Hoàn thành món ăn
Xếp hủ tiếu, giá, hẹ, hành phi vào tô rồi xếp lòng heo, tôm, thịt lên trên. Rắc hành lá, tiêu và ớt. Bạn có thể chan nước dùng để ăn hủ tiếu nước hoặc trộn với sốt để ăn hủ tiếu khô.

Vậy là đã xong nồi hủ tiếu Mỹ Tho, chúc cả nhà có bữa sáng thật ngon.
```

**cau_truc_0198_01** (230 token)

```text
Hướng dẫn nấu ăn · Canh khoai mỡ nấu tôm nấu kiểu viên chả tôm được không
Canh khoai mỡ nấu tôm có màu tím đẹp mắt, viên tôm dai ngọt, nước canh thanh nhẹ dễ ăn.

Nguyên liệu cần chuẩn bị (cho 2 người)
- Khoai mỡ 250g
- Tôm 200g
- Hành lá 1 ít
- Hành tím 3 củ
- Nước mắm 1 muỗng canh
- Dầu ăn 1 muỗng canh
- Gia vị đường, muối, bột ngọt, hạt nêm, tiêu
- Rau thơm 1 ít

Sơ chế
- Tôm lột vỏ, bỏ đầu, rút chỉ đen rồi rửa sạch
- Xay nhuyễn tôm cùng hành lá cắt nhỏ, ướp 5 phút
- Khoai mỡ gọt vỏ, cắt lát mỏng hoặc dùng muỗng nạo thành sợi

Cách chế biến
- Phi hành tím cho vàng thơm rồi xào sơ khoai mỡ
- Thêm 500ml nước, đun sôi
- Múc từng phần hỗn hợp tôm vào nồi nước sôi để tạo thành viên
- Nấu thêm 8 phút, nêm nước mắm và gia vị cho vừa ăn

Hoàn thành món ăn
Múc canh ra tô, rắc hành phi cùng rau thơm lên trên rồi dùng nóng với cơm.

Canh viên tôm khoai mỡ này ăn lạ miệng mà dễ làm, chúc bạn nấu ngon.
```

**cau_truc_0589_01** (90 token)

```text
Món ăn miền Tây · Lẩu cá kèo rau nhút ăn ở đâu ngon
Lẩu cá kèo là món ăn rất phổ biến ở các tỉnh miền Tây, đặc biệt là Cần Thơ và các tỉnh ven biển. Cá kèo rửa sạch cho vào nồi lẩu đang sôi, cá chín rất nhanh.

Rau nhút là loại rau ăn kèm đặc trưng nhất với lẩu cá kèo. Nước lẩu nấu chua nhẹ với me hoặc lá giang, nêm ít mắm cho đậm vị
```

**cau_truc_0189_01** (163 token)

```text
Hướng dẫn nấu món ăn miền Tây · Ốc bươu nhồi thịt hấp sả làm như thế nào · Giới thiệu + Nguyên liệu cần chuẩn bị (cho 4 người, chuẩn bị 20 phút và làm khoảng 1 giờ, chưa tính thời gian ngâm ốc)
Ốc bươu nhồi thịt hấp sả là món ăn lạ miệng. Thịt ốc băm trộn thịt heo, nấm mèo rồi nhồi lại vào vỏ, hấp cùng sả và gừng rất thơm.

Nguyên liệu cần chuẩn bị (cho 4 người, chuẩn bị 20 phút và làm khoảng 1 giờ, chưa tính thời gian ngâm ốc)
- Ốc bươu 1kg
- Giò sống 100g
- Thịt xay 100g
- Nấm mèo 100g
- Sả 7 nhánh
- Gừng 2 củ
- Hành tím 1 củ
- Tỏi 3 tép
- Ớt sừng 4 trái
- Nước mắm 5 muỗng canh
- Đường 2 muỗng canh
- Tiêu xay 1 muỗng canh
```

**cau_truc_0163_03** (70 token)

```text
Hướng dẫn nấu món ăn miền Tây · Bún vịt nấu tiêu đặc sản Sóc Trăng làm sao · Hoàn thành món ăn
Hoàn thành món ăn
Múc bún ra tô, cho thịt vịt và chan nước dùng. Ăn kèm hành tím ngâm chua, rau muống bào, hoa chuối và giá.

Vậy là đã hoàn thành món bún vịt nấu tiêu, chúc bạn nấu ăn vui vẻ.
```

### 5. Siêu dữ liệu đầy đủ

| Trường | Số đoạn thiếu |
|---|---|
| `nhom` | 0 |
| `id_goc` | 0 |
| `tap` | 0 |
| `nguon` | 0 |
| `cau_hoi` | 0 |

### 6. Cảnh báo

- `qua_ngan`: 0 · `toan_so`: 0 · `chia_theo_cau`: 0 · `phu_thuoc_muc_truoc`: 6
- Ranh giới đoạn nằm giữa một dòng (cắt ngang dòng nguyên liệu/bước nấu/câu), toàn bộ dữ liệu: **0**

**Đoạn quá ngắn** (không tự gộp, không tự loại; cần kiểm tay):

- Không có.

**Đoạn toàn số** (có thể là bảng dinh dưỡng bị vỡ):

- Không có.

**Đoạn chia theo tiêu đề con / dòng** (`chia_theo_cau = true`):

- Không có.

**Ngoại lệ phụ thuộc mục trước** (tên mục trước được đưa vào tiêu đề cha, không chép chồng nội dung):

| chunk_id | Tên mục | Mục trước | Câu gây phụ thuộc |
|---|---|---|---|
| cau_truc_0252_02 | Cách chế biến + Hoàn thành món ăn | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 2-3 người) + Sơ chế | …, phi tỏi băm cho vàng thơm ⏎ - Cho bí đỏ đã ướp vào xào trên lửa vừ… |
| cau_truc_0262_03 | Cách chế biến + Hoàn thành món ăn | Sơ chế | …ồi trút ra bát ⏎ - Đun sôi nước luộc ngao đã lọc ⏎ - Cho hỗn hợp ngao … |
| cau_truc_0041_03 | Cách chế biến + Hoàn thành món ăn | Sơ chế | …ước rồi cho phần me đã dằm vào ⏎ - Cho cá đã ướp vào nấu khoảng 10 p… |
| cau_truc_0052_02 | Sơ chế + Cách chế biến + Hoàn thành món ăn | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 3 đến 4 người, chuẩn bị 20 phút và nấu khoảng 40 phút) | …à gia vị vào xào cho thấm ⏎ - Đổ mắm ruốc đã lọc vào nấu 5 phút, sau… |
| cau_truc_0061_03 | Cách chế biến + Hoàn thành món ăn | Sơ chế | …tôm khô vào đảo nhanh tay ⏎ - Đổ nước sốt đã pha vào và rim tôm 1 đế… |
| cau_truc_0178_02 | Sơ chế + Cách chế biến + Hoàn thành món ăn | Giới thiệu + Nguyên liệu cần chuẩn bị (cho 4 người, làm trong khoảng 1 giờ) | …tháo nilon ⏎ - Gói từng quả bằng lá chuối đã rửa sạch ⏎ Nướng ⏎ - Nướng ở 180… |

## Cách `co_dinh`

### 1. Phân bố độ dài (token)

| Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất | Số câu trả lời bị chia |
|---|---|---|---|---|---|
| 1184 | 21 | 90 | 123.8 | 250 | 187 |

| Nhóm | Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất |
|---|---|---|---|---|---|
| 01_chao_hoi | 40 | 21 | 33.5 | 38.8 | 74 |
| 02_huong_dan_nau_an | 160 | 68 | 228 | 192.0 | 250 |
| 03_huong_dan_nau_mon_mien_tay | 281 | 67 | 244 | 193.9 | 250 |
| 04_mon_an_mien_tay | 80 | 68 | 87 | 87.0 | 106 |
| 05_nguyen_lieu_gia_vi | 80 | 74 | 88 | 89.2 | 111 |
| 06_thay_the_nguyen_lieu | 80 | 38 | 79 | 79.7 | 104 |
| 07_dieu_chinh_cong_thuc | 80 | 69 | 83 | 83.4 | 105 |
| 08_dinh_duong | 80 | 72 | 81 | 81.6 | 95 |
| 09_goi_y_mon_theo_dinh_duong | 80 | 72 | 86 | 86.5 | 101 |
| 10_bao_quan_che_bien | 78 | 67 | 86 | 85.4 | 102 |
| 11_an_toan_thuc_pham | 75 | 65 | 78 | 79.0 | 93 |
| 12_goi_y_khi_om_met | 70 | 80 | 95 | 95.2 | 113 |

Nhận xét: đoạn dài nhất gấp 12 lần đoạn ngắn nhất. Chênh lệch chủ yếu do nhóm Chào hỏi rất ngắn còn công thức nấu ăn dài; các đoạn dài đều bị chặn dưới giới hạn mô hình.

### 2. Số đoạn vượt giới hạn mô hình

**0**

### 3. Không mất chữ

Ghép `noi_dung` theo `thu_tu_doan` (bỏ `so_ky_tu_chong_lan` ký tự đầu mỗi đoạn), bỏ khoảng trắng, so với câu trả lời đã tiền xử lý.

Số cặp hỏi–đáp lỗi: **0**

### 4. Đọc thử 5 đoạn ngẫu nhiên (seed 42)

**co_dinh_0054_02** (250 token)

```text
Hướng dẫn nấu món ăn miền Tây · Hướng dẫn làm bánh tằm bì
phút

Cách chế biến
Làm sợi bánh
- Trộn đều bột nếp, bột gạo và bột năng
- Cho từ từ 150ml nước sôi vào, trộn bằng muỗng rồi nhồi tay đến khi bột mịn và không dính tay
- Nặn bột thành sợi và phủ một lớp bột áo
- Đun sôi nước rồi thả sợi bánh vào luộc. Bánh nổi lên thì vớt ra thả vào tô nước đá lạnh
Làm bì
- Luộc da heo với 1/2 muỗng cà phê hạt nêm khoảng 20 phút, vớt ra nước đá rồi cắt sợi nhỏ
- Chiên thịt cho chín đều hai mặt, cho 150ml nước dừa vào rim đến khi nước sệt
- Thịt cắt sợi rồi trộn với da heo và 150g thính gạo
Làm nước cốt dừa
- Hòa 1 muỗng canh bột bắp với 30ml nước
- Cho vào 300ml nước cốt dừa cùng 1/2 muỗng cà phê muối, nấu đến khi sôi và sệt
Làm nước mắm
- Hòa 100ml nước mắm với 150ml nước dừa và đường rồi đun sôi
- Để nguội rồi cho tỏi ớt băm và nước cốt chanh vào

Hoàn thành món ăn
Cho dưa leo và rau sống cắt nhỏ vào dĩa, thêm bánh tằm và bì lên trên. Rưới nước cốt dừa và nước mắm rồi trộn đều khi ăn.

Chúc
```

**co_dinh_0198_01** (230 token)

```text
Hướng dẫn nấu ăn · Canh khoai mỡ nấu tôm nấu kiểu viên chả tôm được không
Canh khoai mỡ nấu tôm có màu tím đẹp mắt, viên tôm dai ngọt, nước canh thanh nhẹ dễ ăn.

Nguyên liệu cần chuẩn bị (cho 2 người)
- Khoai mỡ 250g
- Tôm 200g
- Hành lá 1 ít
- Hành tím 3 củ
- Nước mắm 1 muỗng canh
- Dầu ăn 1 muỗng canh
- Gia vị đường, muối, bột ngọt, hạt nêm, tiêu
- Rau thơm 1 ít

Sơ chế
- Tôm lột vỏ, bỏ đầu, rút chỉ đen rồi rửa sạch
- Xay nhuyễn tôm cùng hành lá cắt nhỏ, ướp 5 phút
- Khoai mỡ gọt vỏ, cắt lát mỏng hoặc dùng muỗng nạo thành sợi

Cách chế biến
- Phi hành tím cho vàng thơm rồi xào sơ khoai mỡ
- Thêm 500ml nước, đun sôi
- Múc từng phần hỗn hợp tôm vào nồi nước sôi để tạo thành viên
- Nấu thêm 8 phút, nêm nước mắm và gia vị cho vừa ăn

Hoàn thành món ăn
Múc canh ra tô, rắc hành phi cùng rau thơm lên trên rồi dùng nóng với cơm.

Canh viên tôm khoai mỡ này ăn lạ miệng mà dễ làm, chúc bạn nấu ngon.
```

**co_dinh_0293_01** (88 token)

```text
Nguyên liệu và gia vị · Phân biệt nước mắm nguyên chất và nước mắm công nghiệp
Nước mắm nguyên chất được ủ từ cá và muối tự nhiên, có độ đạm cao, vị mặn đậm và mùi thơm đặc trưng. Nước mắm công nghiệp thường pha loãng thêm nước, đường, chất điều vị nên nhạt hơn và có vị ngọt hơn.

Nước mắm nguyên chất thích hợp để pha nước chấm hoặc nêm những món cần vị đậm đà. Nước mắm công nghiệp thì tiện lợi hơn cho việc nêm nếm hàng ngày vì đã cân bằng vị sẵn
```

**co_dinh_0551_01** (89 token)

```text
Món ăn miền Tây · Cháo cá lóc rau đắng ăn sao cho đúng cách
Cháo cá lóc rau đắng ăn đúng cách là múc cháo nóng ra tô, cho cá lóc phi lê xé nhỏ lên trên. Rau đắng đất rửa sạch để nguyên lá cho vào tô cháo nóng, rau sẽ tái và giữ vị đắng nhẹ.

Thêm hành phi, tiêu xay và vài giọt nước mắm. Vị đắng của rau đắng kết hợp cháo cá ngọt tạo nên hương vị rất đặc trưng
```

**co_dinh_0176_02** (190 token)

```text
Hướng dẫn nấu món ăn miền Tây · Bánh khọt miền Tây tôm thịt làm như thế nào
, cơm xay, bột nghệ, nước cốt dừa và muối
- Để bột nở khoảng 2 đến 3 giờ
Xào nhân
- Phi thơm hành tím rồi xào tôm với hạt nêm đến khi săn lại
- Xào thịt tương tự ở lửa vừa
Nấu nước cốt
- Hòa tan một ít bột gạo với nước rồi đổ vào nước cốt dừa
- Khuấy ở lửa nhỏ đến khi sôi và sánh lại
Chiên bánh
- Cho giá và hành lá vào bột
- Thoa dầu vào khuôn, đổ bột khoảng 2/3 ô rồi cho nhân vào giữa
- Đậy nắp vài phút, rưới nước cốt dừa lên mặt và chiên đến khi vàng giòn
Pha nước chấm
- Pha nước dừa với nước mắm, đường, tỏi ớt

Hoàn thành món ăn
Sắp bánh ra dĩa, ăn cùng xà lách, rau thơm, đồ chua và nước mắm chua ngọt.

Vậy là đã xong mẻ bánh khọt, chúc bạn làm bánh thật vui.
```

### 5. Siêu dữ liệu đầy đủ

| Trường | Số đoạn thiếu |
|---|---|
| `nhom` | 0 |
| `id_goc` | 0 |
| `tap` | 0 |
| `nguon` | 0 |
| `cau_hoi` | 0 |

### 6. Cảnh báo

- `qua_ngan`: 0 · `toan_so`: 0 · `chia_theo_cau`: 0 · `phu_thuoc_muc_truoc`: 0
- Ranh giới đoạn nằm giữa một dòng (cắt ngang dòng nguyên liệu/bước nấu/câu), toàn bộ dữ liệu: **356**

- Đoạn quá ngắn: không có
- Đoạn toàn số: không có

## Cách `de_quy`

### 1. Phân bố độ dài (token)

| Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất | Số câu trả lời bị chia |
|---|---|---|---|---|---|
| 1187 | 21 | 89 | 117.9 | 250 | 187 |

| Nhóm | Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất |
|---|---|---|---|---|---|
| 01_chao_hoi | 40 | 21 | 33.5 | 38.8 | 74 |
| 02_huong_dan_nau_an | 162 | 42 | 207.5 | 175.6 | 250 |
| 03_huong_dan_nau_mon_mien_tay | 282 | 33 | 189 | 177.6 | 250 |
| 04_mon_an_mien_tay | 80 | 68 | 87 | 87.0 | 106 |
| 05_nguyen_lieu_gia_vi | 80 | 74 | 88 | 89.2 | 111 |
| 06_thay_the_nguyen_lieu | 80 | 38 | 79 | 79.7 | 104 |
| 07_dieu_chinh_cong_thuc | 80 | 69 | 83 | 83.4 | 105 |
| 08_dinh_duong | 80 | 72 | 81 | 81.6 | 95 |
| 09_goi_y_mon_theo_dinh_duong | 80 | 72 | 86 | 86.5 | 101 |
| 10_bao_quan_che_bien | 78 | 67 | 86 | 85.4 | 102 |
| 11_an_toan_thuc_pham | 75 | 65 | 78 | 79.0 | 93 |
| 12_goi_y_khi_om_met | 70 | 80 | 95 | 95.2 | 113 |

Nhận xét: đoạn dài nhất gấp 12 lần đoạn ngắn nhất. Chênh lệch chủ yếu do nhóm Chào hỏi rất ngắn còn công thức nấu ăn dài; các đoạn dài đều bị chặn dưới giới hạn mô hình.

### 2. Số đoạn vượt giới hạn mô hình

**0**

### 3. Không mất chữ

Ghép `noi_dung` theo `thu_tu_doan` (bỏ `so_ky_tu_chong_lan` ký tự đầu mỗi đoạn), bỏ khoảng trắng, so với câu trả lời đã tiền xử lý.

Số cặp hỏi–đáp lỗi: **0**

### 4. Đọc thử 5 đoạn ngẫu nhiên (seed 42)

**de_quy_0053_02** (165 token)

```text
Hướng dẫn nấu món ăn miền Tây · Bún cá Châu Đốc làm như thế nào
Cách chế biến
Nấu nước lèo
- Giã nhuyễn sả, nghệ và ngãi bún
- Cho 400ml nước dừa, 1 lít nước lọc và hỗn hợp vừa giã vào nồi, đun sôi
- Cho cá vào luộc 15 phút rồi vớt ra để nguội, lọc bỏ phần xác
- Hòa mắm ruốc với nước rồi cho vào nồi cùng hạt nêm, muối, đường phèn, sả băm, hành tím và tỏi băm
Xào cá
- Gỡ thịt cá nhẹ tay để bỏ xương
- Xào cá với dầu ăn, sả, hành tím và tỏi khoảng 3 phút cho thơm

Hoàn thành món ăn
Cho bún, cá và rau vào tô rồi chan nước lèo nóng. Ăn kèm nước mắm ớt.

Vậy là đã hoàn thành tô bún cá Châu Đốc, chúc bạn ăn thật ngon miệng.
```

**de_quy_0198_01** (230 token)

```text
Hướng dẫn nấu ăn · Canh khoai mỡ nấu tôm nấu kiểu viên chả tôm được không
Canh khoai mỡ nấu tôm có màu tím đẹp mắt, viên tôm dai ngọt, nước canh thanh nhẹ dễ ăn.

Nguyên liệu cần chuẩn bị (cho 2 người)
- Khoai mỡ 250g
- Tôm 200g
- Hành lá 1 ít
- Hành tím 3 củ
- Nước mắm 1 muỗng canh
- Dầu ăn 1 muỗng canh
- Gia vị đường, muối, bột ngọt, hạt nêm, tiêu
- Rau thơm 1 ít

Sơ chế
- Tôm lột vỏ, bỏ đầu, rút chỉ đen rồi rửa sạch
- Xay nhuyễn tôm cùng hành lá cắt nhỏ, ướp 5 phút
- Khoai mỡ gọt vỏ, cắt lát mỏng hoặc dùng muỗng nạo thành sợi

Cách chế biến
- Phi hành tím cho vàng thơm rồi xào sơ khoai mỡ
- Thêm 500ml nước, đun sôi
- Múc từng phần hỗn hợp tôm vào nồi nước sôi để tạo thành viên
- Nấu thêm 8 phút, nêm nước mắm và gia vị cho vừa ăn

Hoàn thành món ăn
Múc canh ra tô, rắc hành phi cùng rau thơm lên trên rồi dùng nóng với cơm.

Canh viên tôm khoai mỡ này ăn lạ miệng mà dễ làm, chúc bạn nấu ngon.
```

**de_quy_0610_01** (86 token)

```text
Món ăn miền Tây · Chả giò miền Tây có gì khác chả giò miền Bắc
Chả giò miền Tây thường cuốn bằng bánh tráng gạo mỏng, nhân có khoai môn hoặc khoai lang bào sợi. Chả giò miền Bắc (nem rán) dùng bánh đa nem mỏng hơn, nhân chủ yếu là thịt và miến.

Chả giò miền Tây chiên lên vỏ xù giòn hơn vì bánh tráng gạo nổ bong bóng khi chiên. Ăn cuốn với rau sống và chấm nước mắm chua ngọt
```

**de_quy_0548_01** (72 token)

```text
Món ăn miền Tây · Bánh xèo miền Tây ăn với nước chấm gì
Bánh xèo miền Tây thường ăn với nước mắm chua ngọt pha tỏi ớt. Cuốn bánh xèo với rau sống gồm xà lách, rau thơm, dưa leo rồi chấm nước mắm.

Một số nơi ăn bánh xèo với nước tương pha cũng ngon. Cách ăn truyền thống là xé bánh xèo ra, cho rau vào giữa rồi cuốn lại bằng lá rau
```

**de_quy_0174_02** (59 token)

```text
Hướng dẫn nấu món ăn miền Tây · Cá bông lau chiên giòn chấm mắm gừng làm sao
Hoàn thành món ăn
Bày cá ra dĩa cùng xoài sợi. Ăn kèm xoài hoặc cuốn với bánh tráng, rau sống, bún rồi chấm nước mắm gừng.

Chúc bạn có dĩa cá bông lau chiên thật giòn.
```

### 5. Siêu dữ liệu đầy đủ

| Trường | Số đoạn thiếu |
|---|---|
| `nhom` | 0 |
| `id_goc` | 0 |
| `tap` | 0 |
| `nguon` | 0 |
| `cau_hoi` | 0 |

### 6. Cảnh báo

- `qua_ngan`: 0 · `toan_so`: 0 · `chia_theo_cau`: 0 · `phu_thuoc_muc_truoc`: 0
- Ranh giới đoạn nằm giữa một dòng (cắt ngang dòng nguyên liệu/bước nấu/câu), toàn bộ dữ liệu: **0**

- Đoạn quá ngắn: không có
- Đoạn toàn số: không có

## 7. So sánh các cách cắt trên cùng một câu dài

> Câu dài nhất nhóm 09 (ID 764) chỉ 83 token nội dung, vừa một đoạn, nên cả ba cách cho cùng một đoạn: **không có câu trả lời nào của nhóm 09 phải chia**. Thêm câu dài nhất nhóm 02 để có ví dụ thứ hai thật sự bị chia.

### ID 49 – Cách nấu hủ tiếu Mỹ Tho tại nhà (03_huong_dan_nau_mon_mien_tay, 462 token nội dung)

| # | `cau_truc` | `co_dinh` | `de_quy` |
|---|---|---|---|
| 1 | 203 tok · *Giới thiệu + Nguyên liệu cần chuẩn bị (cho 6 người, chuẩn bị 45 phút và nấu khoảng 4 giờ)*<br>«Hủ tiếu Mỹ Tho là món nước nổi tiếng của Tiền Giang. Nước dù…»<br>…« tiêu, bột ngọt, hạt nêm, dầu hào, dầu mè, bột năng, bột bắp» | 250 tok · *(không có tên mục)*<br>«Hủ tiếu Mỹ Tho là món nước nổi tiếng của Tiền Giang. Nước dù…»<br>…«ỏ ⏎  ⏎ Cách chế biến ⏎ Nướng nguyên liệu ⏎ - Nướng mía lau, hành tím» | 239 tok · *(không có tên mục)*<br>«Hủ tiếu Mỹ Tho là món nước nổi tiếng của Tiền Giang. Nước dù…»<br>…« phút rồi rửa lại ⏎ - Tôm khô ngâm 30 phút cho mềm rồi giã nhỏ» |
| 2 | 247 tok · *Sơ chế + Cách chế biến*<br>«Sơ chế ⏎ - Rửa lưỡi heo, tim và dồi trường bằng hỗn hợp muối v…»<br>…«- Rót từ từ hỗn hợp bột năng và bột bắp vào cho sốt sánh lại» | 250 tok · *(không có tên mục)*<br>«uộc sơ tim, lưỡi, dồi trường rồi ngâm vào nước đá ⏎ - Xương gi…»<br>…«iá, hẹ, hành phi vào tô rồi xếp lòng heo, tôm, thịt lên trên» | 238 tok · *(không có tên mục)*<br>«Cách chế biến ⏎ Nướng nguyên liệu ⏎ - Nướng mía lau, hành tím, m…»<br>…«dùng để ăn hủ tiếu nước hoặc trộn với sốt để ăn hủ tiếu khô.» |
| 3 | 90 tok · *Hoàn thành món ăn*<br>«Hoàn thành món ăn ⏎ Xếp hủ tiếu, giá, hẹ, hành phi vào tô rồi …»<br>…« xong nồi hủ tiếu Mỹ Tho, chúc cả nhà có bữa sáng thật ngon.» | 110 tok · *(không có tên mục)*<br>«hầm xương với đường, cho sốt vào đun sôi ⏎ - Rót từ từ hỗn hợp…»<br>…« xong nồi hủ tiếu Mỹ Tho, chúc cả nhà có bữa sáng thật ngon.» | 33 tok · *(không có tên mục)*<br>«Vậy là đã xong nồi hủ tiếu Mỹ Tho, chúc cả nhà có bữa sáng t…»<br>…« xong nồi hủ tiếu Mỹ Tho, chúc cả nhà có bữa sáng thật ngon.» |

- `cau_truc`: 0 ranh giới nằm giữa một dòng.
- `co_dinh`: 4 ranh giới nằm giữa một dòng:
    - «- Nướng mía lau, hành tím**‖**, mực khô và sá sùng trên vỉ có lót giấy bạc cho d»
    - «nh phi vào tô rồi xếp lòng heo, tôm, thịt lên trên**‖**. Rắc hành lá, tiêu và ớt. Bạn có thể chan nước dù»
    - «- L**‖**uộc sơ tim, lưỡi, dồi trường rồi ngâm vào nước đá»
    - «- Nêm nước **‖**hầm xương với đường, cho sốt vào đun sôi»
- `de_quy`: 0 ranh giới nằm giữa một dòng.

<details><summary><code>cau_truc</code>: 3 đoạn (bấm để xem nguyên văn)</summary>

**cau_truc_0049_01** (203 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà · Giới thiệu + Nguyên liệu cần chuẩn bị (cho 6 người, chuẩn bị 45 phút và nấu khoảng 4 giờ)
Hủ tiếu Mỹ Tho là món nước nổi tiếng của Tiền Giang. Nước dùng hầm từ xương cùng mực khô, sá sùng nên ngọt thanh, ăn với lòng heo, tôm và thịt. Món này làm khá công phu nhưng nấu một lần được nhiều tô.

Nguyên liệu cần chuẩn bị (cho 6 người, chuẩn bị 45 phút và nấu khoảng 4 giờ)
- Hủ tiếu 500g
- Xương giá 500g và xương cổ 500g
- Lưỡi heo 400g
- Tim heo 300g
- Thịt heo nạc 400g
- Dồi trường 300g
- Tôm sú 10 con
- Mực khô 3 con nhỏ
- Sá sùng khô 6 con
- Tôm khô 10g
- Mía lau 500g
- Hành tím, tỏi, cà chua
- Giá, xà lách, rau cần, hẹ, hành lá
- Gia vị: muối, đường, tiêu, bột ngọt, hạt nêm, dầu hào, dầu mè, bột năng, bột bắp
```

**cau_truc_0049_02** (247 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà · Sơ chế + Cách chế biến
Sơ chế
- Rửa lưỡi heo, tim và dồi trường bằng hỗn hợp muối và chanh
- Luộc sơ tim, lưỡi, dồi trường rồi ngâm vào nước đá
- Xương giá và xương cổ ngâm nước muối loãng 10 phút rồi rửa lại
- Tôm khô ngâm 30 phút cho mềm rồi giã nhỏ

Cách chế biến
Nướng nguyên liệu
- Nướng mía lau, hành tím, mực khô và sá sùng trên vỉ có lót giấy bạc cho dậy mùi thơm
Hầm nước dùng
- Cho xương vào nồi với 3 lít nước, đun lửa to 10 phút rồi vớt bọt
- Vặn lửa nhỏ, cho mía, hành tím, mực và sá sùng đã nướng vào, hầm khoảng 3 giờ
Luộc lòng và tôm
- Luộc lòng khoảng 15 phút rồi ngâm nước đá
- Luộc tôm đến khi chuyển màu cam
Làm thịt xá xíu
- Thịt heo cắt mỏng, ướp gia vị 30 phút
- Áp chảo trên lửa vừa đến khi hai mặt vàng
Làm sốt trộn cho hủ tiếu khô
- Xào tôm khô với tỏi và cà chua rồi xay nhuyễn
- Nêm nước hầm xương với đường, cho sốt vào đun sôi
- Rót từ từ hỗn hợp bột năng và bột bắp vào cho sốt sánh lại
```

**cau_truc_0049_03** (90 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà · Hoàn thành món ăn
Hoàn thành món ăn
Xếp hủ tiếu, giá, hẹ, hành phi vào tô rồi xếp lòng heo, tôm, thịt lên trên. Rắc hành lá, tiêu và ớt. Bạn có thể chan nước dùng để ăn hủ tiếu nước hoặc trộn với sốt để ăn hủ tiếu khô.

Vậy là đã xong nồi hủ tiếu Mỹ Tho, chúc cả nhà có bữa sáng thật ngon.
```

</details>

<details><summary><code>co_dinh</code>: 3 đoạn (bấm để xem nguyên văn)</summary>

**co_dinh_0049_01** (250 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà
Hủ tiếu Mỹ Tho là món nước nổi tiếng của Tiền Giang. Nước dùng hầm từ xương cùng mực khô, sá sùng nên ngọt thanh, ăn với lòng heo, tôm và thịt. Món này làm khá công phu nhưng nấu một lần được nhiều tô.

Nguyên liệu cần chuẩn bị (cho 6 người, chuẩn bị 45 phút và nấu khoảng 4 giờ)
- Hủ tiếu 500g
- Xương giá 500g và xương cổ 500g
- Lưỡi heo 400g
- Tim heo 300g
- Thịt heo nạc 400g
- Dồi trường 300g
- Tôm sú 10 con
- Mực khô 3 con nhỏ
- Sá sùng khô 6 con
- Tôm khô 10g
- Mía lau 500g
- Hành tím, tỏi, cà chua
- Giá, xà lách, rau cần, hẹ, hành lá
- Gia vị: muối, đường, tiêu, bột ngọt, hạt nêm, dầu hào, dầu mè, bột năng, bột bắp

Sơ chế
- Rửa lưỡi heo, tim và dồi trường bằng hỗn hợp muối và chanh
- Luộc sơ tim, lưỡi, dồi trường rồi ngâm vào nước đá
- Xương giá và xương cổ ngâm nước muối loãng 10 phút rồi rửa lại
- Tôm khô ngâm 30 phút cho mềm rồi giã nhỏ

Cách chế biến
Nướng nguyên liệu
- Nướng mía lau, hành tím
```

**co_dinh_0049_02** (250 token, chồng lấn 216 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà
uộc sơ tim, lưỡi, dồi trường rồi ngâm vào nước đá
- Xương giá và xương cổ ngâm nước muối loãng 10 phút rồi rửa lại
- Tôm khô ngâm 30 phút cho mềm rồi giã nhỏ

Cách chế biến
Nướng nguyên liệu
- Nướng mía lau, hành tím, mực khô và sá sùng trên vỉ có lót giấy bạc cho dậy mùi thơm
Hầm nước dùng
- Cho xương vào nồi với 3 lít nước, đun lửa to 10 phút rồi vớt bọt
- Vặn lửa nhỏ, cho mía, hành tím, mực và sá sùng đã nướng vào, hầm khoảng 3 giờ
Luộc lòng và tôm
- Luộc lòng khoảng 15 phút rồi ngâm nước đá
- Luộc tôm đến khi chuyển màu cam
Làm thịt xá xíu
- Thịt heo cắt mỏng, ướp gia vị 30 phút
- Áp chảo trên lửa vừa đến khi hai mặt vàng
Làm sốt trộn cho hủ tiếu khô
- Xào tôm khô với tỏi và cà chua rồi xay nhuyễn
- Nêm nước hầm xương với đường, cho sốt vào đun sôi
- Rót từ từ hỗn hợp bột năng và bột bắp vào cho sốt sánh lại

Hoàn thành món ăn
Xếp hủ tiếu, giá, hẹ, hành phi vào tô rồi xếp lòng heo, tôm, thịt lên trên
```

**co_dinh_0049_03** (110 token, chồng lấn 195 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà
hầm xương với đường, cho sốt vào đun sôi
- Rót từ từ hỗn hợp bột năng và bột bắp vào cho sốt sánh lại

Hoàn thành món ăn
Xếp hủ tiếu, giá, hẹ, hành phi vào tô rồi xếp lòng heo, tôm, thịt lên trên. Rắc hành lá, tiêu và ớt. Bạn có thể chan nước dùng để ăn hủ tiếu nước hoặc trộn với sốt để ăn hủ tiếu khô.

Vậy là đã xong nồi hủ tiếu Mỹ Tho, chúc cả nhà có bữa sáng thật ngon.
```

</details>

<details><summary><code>de_quy</code>: 3 đoạn (bấm để xem nguyên văn)</summary>

**de_quy_0049_01** (239 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà
Hủ tiếu Mỹ Tho là món nước nổi tiếng của Tiền Giang. Nước dùng hầm từ xương cùng mực khô, sá sùng nên ngọt thanh, ăn với lòng heo, tôm và thịt. Món này làm khá công phu nhưng nấu một lần được nhiều tô.

Nguyên liệu cần chuẩn bị (cho 6 người, chuẩn bị 45 phút và nấu khoảng 4 giờ)
- Hủ tiếu 500g
- Xương giá 500g và xương cổ 500g
- Lưỡi heo 400g
- Tim heo 300g
- Thịt heo nạc 400g
- Dồi trường 300g
- Tôm sú 10 con
- Mực khô 3 con nhỏ
- Sá sùng khô 6 con
- Tôm khô 10g
- Mía lau 500g
- Hành tím, tỏi, cà chua
- Giá, xà lách, rau cần, hẹ, hành lá
- Gia vị: muối, đường, tiêu, bột ngọt, hạt nêm, dầu hào, dầu mè, bột năng, bột bắp

Sơ chế
- Rửa lưỡi heo, tim và dồi trường bằng hỗn hợp muối và chanh
- Luộc sơ tim, lưỡi, dồi trường rồi ngâm vào nước đá
- Xương giá và xương cổ ngâm nước muối loãng 10 phút rồi rửa lại
- Tôm khô ngâm 30 phút cho mềm rồi giã nhỏ
```

**de_quy_0049_02** (238 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà
Cách chế biến
Nướng nguyên liệu
- Nướng mía lau, hành tím, mực khô và sá sùng trên vỉ có lót giấy bạc cho dậy mùi thơm
Hầm nước dùng
- Cho xương vào nồi với 3 lít nước, đun lửa to 10 phút rồi vớt bọt
- Vặn lửa nhỏ, cho mía, hành tím, mực và sá sùng đã nướng vào, hầm khoảng 3 giờ
Luộc lòng và tôm
- Luộc lòng khoảng 15 phút rồi ngâm nước đá
- Luộc tôm đến khi chuyển màu cam
Làm thịt xá xíu
- Thịt heo cắt mỏng, ướp gia vị 30 phút
- Áp chảo trên lửa vừa đến khi hai mặt vàng
Làm sốt trộn cho hủ tiếu khô
- Xào tôm khô với tỏi và cà chua rồi xay nhuyễn
- Nêm nước hầm xương với đường, cho sốt vào đun sôi
- Rót từ từ hỗn hợp bột năng và bột bắp vào cho sốt sánh lại

Hoàn thành món ăn
Xếp hủ tiếu, giá, hẹ, hành phi vào tô rồi xếp lòng heo, tôm, thịt lên trên. Rắc hành lá, tiêu và ớt. Bạn có thể chan nước dùng để ăn hủ tiếu nước hoặc trộn với sốt để ăn hủ tiếu khô.
```

**de_quy_0049_03** (33 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu món ăn miền Tây · Cách nấu hủ tiếu Mỹ Tho tại nhà
Vậy là đã xong nồi hủ tiếu Mỹ Tho, chúc cả nhà có bữa sáng thật ngon.
```

</details>

### ID 764 – Gợi ý ăn gì cho người bị thiếu máu (09_goi_y_mon_theo_dinh_duong, 83 token nội dung)

| # | `cau_truc` | `co_dinh` | `de_quy` |
|---|---|---|---|
| 1 | 101 tok · *(cả câu)*<br>«Người bị thiếu máu nên ăn thực phẩm giàu sắt như thịt bò, ga…»<br>…«u sắt. ⏎  ⏎ Nên đi khám để bác sĩ tư vấn thêm nếu thiếu máu nặng» | 101 tok · *(cả câu)*<br>«Người bị thiếu máu nên ăn thực phẩm giàu sắt như thịt bò, ga…»<br>…«u sắt. ⏎  ⏎ Nên đi khám để bác sĩ tư vấn thêm nếu thiếu máu nặng» | 101 tok · *(cả câu)*<br>«Người bị thiếu máu nên ăn thực phẩm giàu sắt như thịt bò, ga…»<br>…«u sắt. ⏎  ⏎ Nên đi khám để bác sĩ tư vấn thêm nếu thiếu máu nặng» |

- `cau_truc`: 0 ranh giới nằm giữa một dòng.
- `co_dinh`: 0 ranh giới nằm giữa một dòng.
- `de_quy`: 0 ranh giới nằm giữa một dòng.

<details><summary><code>cau_truc</code>: 1 đoạn (bấm để xem nguyên văn)</summary>

**cau_truc_0764_01** (101 token, chồng lấn 0 ký tự)

```text
Gợi ý món ăn theo nhu cầu dinh dưỡng · Gợi ý ăn gì cho người bị thiếu máu
Người bị thiếu máu nên ăn thực phẩm giàu sắt như thịt bò, gan, rau xanh đậm (rau dền, rau ngót). Ăn kèm trái cây giàu vitamin C như cam, ổi, kiwi giúp hấp thu sắt tốt hơn.

Trứng, đậu đen, đậu lăng cũng chứa sắt. Tránh uống trà, cà phê ngay sau ăn vì làm giảm hấp thu sắt.

Nên đi khám để bác sĩ tư vấn thêm nếu thiếu máu nặng
```

</details>

<details><summary><code>co_dinh</code>: 1 đoạn (bấm để xem nguyên văn)</summary>

**co_dinh_0764_01** (101 token, chồng lấn 0 ký tự)

```text
Gợi ý món ăn theo nhu cầu dinh dưỡng · Gợi ý ăn gì cho người bị thiếu máu
Người bị thiếu máu nên ăn thực phẩm giàu sắt như thịt bò, gan, rau xanh đậm (rau dền, rau ngót). Ăn kèm trái cây giàu vitamin C như cam, ổi, kiwi giúp hấp thu sắt tốt hơn.

Trứng, đậu đen, đậu lăng cũng chứa sắt. Tránh uống trà, cà phê ngay sau ăn vì làm giảm hấp thu sắt.

Nên đi khám để bác sĩ tư vấn thêm nếu thiếu máu nặng
```

</details>

<details><summary><code>de_quy</code>: 1 đoạn (bấm để xem nguyên văn)</summary>

**de_quy_0764_01** (101 token, chồng lấn 0 ký tự)

```text
Gợi ý món ăn theo nhu cầu dinh dưỡng · Gợi ý ăn gì cho người bị thiếu máu
Người bị thiếu máu nên ăn thực phẩm giàu sắt như thịt bò, gan, rau xanh đậm (rau dền, rau ngót). Ăn kèm trái cây giàu vitamin C như cam, ổi, kiwi giúp hấp thu sắt tốt hơn.

Trứng, đậu đen, đậu lăng cũng chứa sắt. Tránh uống trà, cà phê ngay sau ăn vì làm giảm hấp thu sắt.

Nên đi khám để bác sĩ tư vấn thêm nếu thiếu máu nặng
```

</details>

### ID 254 – Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với (02_huong_dan_nau_an, 398 token nội dung)

| # | `cau_truc` | `co_dinh` | `de_quy` |
|---|---|---|---|
| 1 | 150 tok · *Giới thiệu + Nguyên liệu cần chuẩn bị (cho 5 người)*<br>«Chả giò là món ăn quen thuộc trong bữa cơm Việt Nam, vỏ ngoà…»<br>…«ml ⏎ - Nước mắm 7 muỗng canh ⏎ - Gia vị tiêu xay, đường, hạt nêm» | 250 tok · *(không có tên mục)*<br>«Chả giò là món ăn quen thuộc trong bữa cơm Việt Nam, vỏ ngoà…»<br>…«ắm, 1 muỗng canh đường và 1/2 muỗng cà phê tiêu xay rồi trộn» | 188 tok · *(không có tên mục)*<br>«Chả giò là món ăn quen thuộc trong bữa cơm Việt Nam, vỏ ngoà…»<br>…«ỏng rồi băm nhỏ ⏎ - Đập trứng tách riêng lòng đỏ và lòng trắng» |
| 2 | 67 tok · *Sơ chế*<br>«Sơ chế ⏎ - Nấm mèo ngâm nước 30 phút cho nở, cắt chân rễ rửa s…»<br>…«ỏng rồi băm nhỏ ⏎ - Đập trứng tách riêng lòng đỏ và lòng trắng» | 230 tok · *(không có tên mục)*<br>«môn bào, 4 lòng đỏ trứng, hành tím và nấm mèo ⏎ - Nêm 1.5 muỗn…»<br>…«là cho chả giò vào tủ lạnh trước khi chiên, bạn thử xem nha.» | 242 tok · *(không có tên mục)*<br>«Cách chế biến ⏎ Làm nhân ⏎ - Trộn thịt heo xay với khoai môn bào…»<br>…«là cho chả giò vào tủ lạnh trước khi chiên, bạn thử xem nha.» |
| 3 | 250 tok · *Cách chế biến + Hoàn thành món ăn*<br>«Cách chế biến ⏎ Làm nhân ⏎ - Trộn thịt heo xay với khoai môn bào…»<br>…«là cho chả giò vào tủ lạnh trước khi chiên, bạn thử xem nha.» |  |  |

- `cau_truc`: 0 ranh giới nằm giữa một dòng.
- `co_dinh`: 2 ranh giới nằm giữa một dòng:
    - «g canh đường và 1/2 muỗng cà phê tiêu xay rồi trộn**‖** đều»
    - «- Trộn thịt heo xay với khoai **‖**môn bào, 4 lòng đỏ trứng, hành tím và nấm mèo»
- `de_quy`: 0 ranh giới nằm giữa một dòng.

<details><summary><code>cau_truc</code>: 3 đoạn (bấm để xem nguyên văn)</summary>

**cau_truc_0254_01** (150 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu ăn · Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với · Giới thiệu + Nguyên liệu cần chuẩn bị (cho 5 người)
Chả giò là món ăn quen thuộc trong bữa cơm Việt Nam, vỏ ngoài giòn rụm bên trong nhân thịt và khoai môn bùi béo ăn kèm rau sống và nước mắm chua ngọt rất ngon.

Nguyên liệu cần chuẩn bị (cho 5 người)
- Thịt heo xay 500g
- Trứng gà 4 quả
- Khoai môn 1 củ lớn
- Nấm mèo 150g
- Hành tím 4 củ
- Tỏi băm 3 muỗng canh
- Ớt băm 2 muỗng canh
- Bánh tráng bò bía 2 gói
- Nước cốt chanh 1 muỗng canh
- Dầu hào 1 muỗng canh
- Dầu ăn 300ml
- Nước mắm 7 muỗng canh
- Gia vị tiêu xay, đường, hạt nêm
```

**cau_truc_0254_02** (67 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu ăn · Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với · Sơ chế
Sơ chế
- Nấm mèo ngâm nước 30 phút cho nở, cắt chân rễ rửa sạch rồi cắt sợi và băm nhỏ
- Khoai môn gọt vỏ, bào nhuyễn
- Hành tím cắt mỏng rồi băm nhỏ
- Đập trứng tách riêng lòng đỏ và lòng trắng
```

**cau_truc_0254_03** (250 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu ăn · Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với · Cách chế biến + Hoàn thành món ăn
Cách chế biến
Làm nhân
- Trộn thịt heo xay với khoai môn bào, 4 lòng đỏ trứng, hành tím và nấm mèo
- Nêm 1.5 muỗng canh hạt nêm, 1 muỗng canh dầu hào, 2 muỗng canh nước mắm, 1 muỗng canh đường và 1/2 muỗng cà phê tiêu xay rồi trộn đều
Cuốn chả giò
- Đặt bánh tráng mặt láng mịn xuống dưới, cho nhân vào giữa
- Cuộn chặt và miết mép, bôi lòng trắng trứng ở mép để dính chặt
- Cho chả giò vào tủ lạnh khoảng 20 phút cho cứng lại
Chiên chả giò
- Đun nóng 300ml dầu ăn, cho thêm chút muối vào dầu
- Cho chả giò vào chiên trên lửa nhỏ vừa cho đến khi vàng đều 2 mặt
- Vớt ra lót giấy thấm dầu
Pha nước chấm
- Trộn 140g đường với 75ml nước mắm và 250ml nước sôi nguội
- Thêm 1 muỗng canh nước cốt chanh, tỏi băm và ớt băm vào khuấy đều

Hoàn thành món ăn
Chả giò chiên vàng bày ra dĩa, ăn kèm rau sống cuốn bánh tráng chấm nước mắm chua ngọt.

Bí quyết cho giòn lâu là cho chả giò vào tủ lạnh trước khi chiên, bạn thử xem nha.
```

</details>

<details><summary><code>co_dinh</code>: 2 đoạn (bấm để xem nguyên văn)</summary>

**co_dinh_0254_01** (250 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu ăn · Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với
Chả giò là món ăn quen thuộc trong bữa cơm Việt Nam, vỏ ngoài giòn rụm bên trong nhân thịt và khoai môn bùi béo ăn kèm rau sống và nước mắm chua ngọt rất ngon.

Nguyên liệu cần chuẩn bị (cho 5 người)
- Thịt heo xay 500g
- Trứng gà 4 quả
- Khoai môn 1 củ lớn
- Nấm mèo 150g
- Hành tím 4 củ
- Tỏi băm 3 muỗng canh
- Ớt băm 2 muỗng canh
- Bánh tráng bò bía 2 gói
- Nước cốt chanh 1 muỗng canh
- Dầu hào 1 muỗng canh
- Dầu ăn 300ml
- Nước mắm 7 muỗng canh
- Gia vị tiêu xay, đường, hạt nêm

Sơ chế
- Nấm mèo ngâm nước 30 phút cho nở, cắt chân rễ rửa sạch rồi cắt sợi và băm nhỏ
- Khoai môn gọt vỏ, bào nhuyễn
- Hành tím cắt mỏng rồi băm nhỏ
- Đập trứng tách riêng lòng đỏ và lòng trắng

Cách chế biến
Làm nhân
- Trộn thịt heo xay với khoai môn bào, 4 lòng đỏ trứng, hành tím và nấm mèo
- Nêm 1.5 muỗng canh hạt nêm, 1 muỗng canh dầu hào, 2 muỗng canh nước mắm, 1 muỗng canh đường và 1/2 muỗng cà phê tiêu xay rồi trộn
```

**co_dinh_0254_02** (230 token, chồng lấn 177 ký tự)

```text
Hướng dẫn nấu ăn · Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với
môn bào, 4 lòng đỏ trứng, hành tím và nấm mèo
- Nêm 1.5 muỗng canh hạt nêm, 1 muỗng canh dầu hào, 2 muỗng canh nước mắm, 1 muỗng canh đường và 1/2 muỗng cà phê tiêu xay rồi trộn đều
Cuốn chả giò
- Đặt bánh tráng mặt láng mịn xuống dưới, cho nhân vào giữa
- Cuộn chặt và miết mép, bôi lòng trắng trứng ở mép để dính chặt
- Cho chả giò vào tủ lạnh khoảng 20 phút cho cứng lại
Chiên chả giò
- Đun nóng 300ml dầu ăn, cho thêm chút muối vào dầu
- Cho chả giò vào chiên trên lửa nhỏ vừa cho đến khi vàng đều 2 mặt
- Vớt ra lót giấy thấm dầu
Pha nước chấm
- Trộn 140g đường với 75ml nước mắm và 250ml nước sôi nguội
- Thêm 1 muỗng canh nước cốt chanh, tỏi băm và ớt băm vào khuấy đều

Hoàn thành món ăn
Chả giò chiên vàng bày ra dĩa, ăn kèm rau sống cuốn bánh tráng chấm nước mắm chua ngọt.

Bí quyết cho giòn lâu là cho chả giò vào tủ lạnh trước khi chiên, bạn thử xem nha.
```

</details>

<details><summary><code>de_quy</code>: 2 đoạn (bấm để xem nguyên văn)</summary>

**de_quy_0254_01** (188 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu ăn · Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với
Chả giò là món ăn quen thuộc trong bữa cơm Việt Nam, vỏ ngoài giòn rụm bên trong nhân thịt và khoai môn bùi béo ăn kèm rau sống và nước mắm chua ngọt rất ngon.

Nguyên liệu cần chuẩn bị (cho 5 người)
- Thịt heo xay 500g
- Trứng gà 4 quả
- Khoai môn 1 củ lớn
- Nấm mèo 150g
- Hành tím 4 củ
- Tỏi băm 3 muỗng canh
- Ớt băm 2 muỗng canh
- Bánh tráng bò bía 2 gói
- Nước cốt chanh 1 muỗng canh
- Dầu hào 1 muỗng canh
- Dầu ăn 300ml
- Nước mắm 7 muỗng canh
- Gia vị tiêu xay, đường, hạt nêm

Sơ chế
- Nấm mèo ngâm nước 30 phút cho nở, cắt chân rễ rửa sạch rồi cắt sợi và băm nhỏ
- Khoai môn gọt vỏ, bào nhuyễn
- Hành tím cắt mỏng rồi băm nhỏ
- Đập trứng tách riêng lòng đỏ và lòng trắng
```

**de_quy_0254_02** (242 token, chồng lấn 0 ký tự)

```text
Hướng dẫn nấu ăn · Hướng dẫn mình cuốn chả giò giòn lâu không bị mềm với
Cách chế biến
Làm nhân
- Trộn thịt heo xay với khoai môn bào, 4 lòng đỏ trứng, hành tím và nấm mèo
- Nêm 1.5 muỗng canh hạt nêm, 1 muỗng canh dầu hào, 2 muỗng canh nước mắm, 1 muỗng canh đường và 1/2 muỗng cà phê tiêu xay rồi trộn đều
Cuốn chả giò
- Đặt bánh tráng mặt láng mịn xuống dưới, cho nhân vào giữa
- Cuộn chặt và miết mép, bôi lòng trắng trứng ở mép để dính chặt
- Cho chả giò vào tủ lạnh khoảng 20 phút cho cứng lại
Chiên chả giò
- Đun nóng 300ml dầu ăn, cho thêm chút muối vào dầu
- Cho chả giò vào chiên trên lửa nhỏ vừa cho đến khi vàng đều 2 mặt
- Vớt ra lót giấy thấm dầu
Pha nước chấm
- Trộn 140g đường với 75ml nước mắm và 250ml nước sôi nguội
- Thêm 1 muỗng canh nước cốt chanh, tỏi băm và ớt băm vào khuấy đều

Hoàn thành món ăn
Chả giò chiên vàng bày ra dĩa, ăn kèm rau sống cuốn bánh tráng chấm nước mắm chua ngọt.

Bí quyết cho giòn lâu là cho chả giò vào tủ lạnh trước khi chiên, bạn thử xem nha.
```

</details>

## 8. Kết luận sơ bộ

Cách `cau_truc` giữ nguyên 806/993 cặp hỏi–đáp thành một đoạn, và khi phải chia thì ranh giới trùng ranh giới mục/tiêu đề con/dòng nên không cắt ngang dòng nguyên liệu hay bước nấu (0 ranh giới giữa dòng, so với 356 của `co_dinh` và 0 của `de_quy`); mỗi đoạn có tên mục nên dẫn nguồn được tới từng phần của câu trả lời. Cách `co_dinh` cắt ngang dòng, có khi cắt giữa một từ; cách `de_quy` ít cắt ngang hơn nhưng phần chồng lấn làm nội dung bị lặp giữa các đoạn. Với giới hạn 256 token, cả ba cách đều phải chia đúng 187 câu trả lời dài (chủ yếu nhóm 02, 03). `cau_truc` **có thể thua** khi: (1) đoạn rất ngắn (nhóm Chào hỏi, mục ngắn) mang ít thông tin nên vector kém phân biệt; (2) câu hỏi cần ghép nhiều cặp hỏi–đáp (ví dụ "gợi ý thực đơn ít béo cho người tiểu đường") — khi đó không cách cắt nào trong ba cách tự giải quyết được, phải dựa vào truy hồi nhiều đoạn; (3) đoạn dài gần giới hạn bị loãng nghĩa so với đoạn nhỏ của `de_quy`. **Phần V sẽ đo bằng số liệu, chưa kết luận cuối.**

