# Kiểm tra tách đoạn (Bài 4 – Phần I)

- Mô hình sinh vector: `bkai-foundation-models/vietnamese-bi-encoder` (PhoBERT, `can_tach_tu = true`).
- Giới hạn token mô hình: **256** (sentence_bert_config.json: max_seq_length = 256 (tokenizer.model_max_length không đặt, config.max_position_embeddings = 258 = 256 + 2)).
- Đếm token: `AutoTokenizer` của mô hình trên **bản đã tách từ** (hàm `TachTu` của `scripts/tach_tu.py`), tính cả tiêu đề cha và `<s>`, `</s>`.
- Tham số: `kich_thuoc_doan = 400`, `chong_lan = 50`, dự phòng 8 token, mục ngắn < 80 token, đoạn ngắn < 40 ký tự, ngưỡng toàn số 0.5, seed 42.
- Số cặp hỏi–đáp: 40 (Train 32, Test 8). Dòng trống đã bỏ: 0.
- Tiền xử lý: đúng hàm `tien_xu_ly` của `scripts/tach_tu.py` (NFC, thống nhất kiểu dấu, khoảng trắng lạ, nháy/gạch, dấu câu dính chữ), giữ nguyên `\n`. `noi_dung` là văn bản đã tiền xử lý.

> Chỉ chạy nhóm `01_chao_hoi`.

## 0. Kích thước đoạn thực dùng

Kích thước thực dùng = `min(400, 256 − token tiêu đề cha − 8)`, tính riêng cho từng đoạn vì tiêu đề cha (Nhóm · Câu hỏi · Tên mục) dài ngắn khác nhau.

- Với tiêu đề không có tên mục: ngắn nhất **231**, trung vị **237**, lớn nhất **240** token nội dung.
- Con số 400 của slide 7 **không bao giờ được dùng**: mô hình chỉ nhận 256 token, để 400 thì phần đuôi bị mô hình cắt bỏ mà không cảnh báo.
- Chồng lấn thực dùng: cố định = `min(50, kích thước/2)`, đệ quy ≤ 50 token (theo mẩu), cấu trúc = 0.
- **Không cài cách cắt theo ngữ nghĩa** (slide 14): phải sinh vector cho từng câu để tìm điểm cắt, tốn kém, trong khi dataset đã có cấu trúc rõ (mục, tiêu đề con, gạch đầu dòng).

## Cách `cau_truc`

### 1. Phân bố độ dài (token)

| Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất | Số câu trả lời bị chia |
|---|---|---|---|---|---|
| 40 | 21 | 33.5 | 38.8 | 74 | 0 |

| Nhóm | Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất |
|---|---|---|---|---|---|
| 01_chao_hoi | 40 | 21 | 33.5 | 38.8 | 74 |

Nhận xét: đoạn dài nhất gấp 4 lần đoạn ngắn nhất. Chênh lệch chủ yếu do nhóm Chào hỏi rất ngắn còn công thức nấu ăn dài; các đoạn dài đều bị chặn dưới giới hạn mô hình.

### 2. Số đoạn vượt giới hạn mô hình

**0**

### 3. Không mất chữ

Ghép `noi_dung` theo `thu_tu_doan` (bỏ `so_ky_tu_chong_lan` ký tự đầu mỗi đoạn), bỏ khoảng trắng, so với câu trả lời đã tiền xử lý.

Số cặp hỏi–đáp lỗi: **0**

### 4. Đọc thử 5 đoạn ngẫu nhiên (seed 42)

**cau_truc_0008_01** (53 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Bạn biết nấu món miền Tây không
Biết chứ bạn. Món miền Tây là phần mình ưu tiên như canh chua cá lóc, cá kho tộ, lẩu mắm hay bánh xèo. Bạn muốn học món nào thì nói mình nhé
```

**cau_truc_0002_01** (46 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Chào bot
Chào bạn nha. Mình là chatbot hướng dẫn nấu ăn và gợi ý món ăn theo nhu cầu dinh dưỡng. Bạn cần mình chỉ cách nấu món nào hay muốn mình gợi ý món cho bữa hôm nay
```

**cau_truc_0018_01** (27 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Cảm ơn đã gợi ý món
Không có gì bạn. Mong bạn và gia đình có bữa cơm thật ngon
```

**cau_truc_0016_01** (23 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Thanks
Không có chi bạn. Chúc bạn có bữa ăn ngon miệng
```

**cau_truc_0015_01** (33 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Cám ơn công thức hay quá
Cảm ơn bạn nhiều. Lúc nấu thử mà muốn chỉnh vị mặn ngọt hay đổi nguyên liệu thì cứ nói mình
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

**Đoạn quá ngắn** (không tự gộp, không tự loại; cần kiểm tay):

- Không có.

**Đoạn toàn số** (có thể là bảng dinh dưỡng bị vỡ):

- Không có.

**Đoạn chia theo tiêu đề con / dòng** (`chia_theo_cau = true`):

- Không có.

**Ngoại lệ phụ thuộc mục trước** (tên mục trước được đưa vào tiêu đề cha, không chép chồng nội dung):

- Không có.

## Cách `co_dinh`

### 1. Phân bố độ dài (token)

| Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất | Số câu trả lời bị chia |
|---|---|---|---|---|---|
| 40 | 21 | 33.5 | 38.8 | 74 | 0 |

| Nhóm | Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất |
|---|---|---|---|---|---|
| 01_chao_hoi | 40 | 21 | 33.5 | 38.8 | 74 |

Nhận xét: đoạn dài nhất gấp 4 lần đoạn ngắn nhất. Chênh lệch chủ yếu do nhóm Chào hỏi rất ngắn còn công thức nấu ăn dài; các đoạn dài đều bị chặn dưới giới hạn mô hình.

### 2. Số đoạn vượt giới hạn mô hình

**0**

### 3. Không mất chữ

Ghép `noi_dung` theo `thu_tu_doan` (bỏ `so_ky_tu_chong_lan` ký tự đầu mỗi đoạn), bỏ khoảng trắng, so với câu trả lời đã tiền xử lý.

Số cặp hỏi–đáp lỗi: **0**

### 4. Đọc thử 5 đoạn ngẫu nhiên (seed 42)

**co_dinh_0008_01** (53 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Bạn biết nấu món miền Tây không
Biết chứ bạn. Món miền Tây là phần mình ưu tiên như canh chua cá lóc, cá kho tộ, lẩu mắm hay bánh xèo. Bạn muốn học món nào thì nói mình nhé
```

**co_dinh_0002_01** (46 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Chào bot
Chào bạn nha. Mình là chatbot hướng dẫn nấu ăn và gợi ý món ăn theo nhu cầu dinh dưỡng. Bạn cần mình chỉ cách nấu món nào hay muốn mình gợi ý món cho bữa hôm nay
```

**co_dinh_0018_01** (27 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Cảm ơn đã gợi ý món
Không có gì bạn. Mong bạn và gia đình có bữa cơm thật ngon
```

**co_dinh_0016_01** (23 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Thanks
Không có chi bạn. Chúc bạn có bữa ăn ngon miệng
```

**co_dinh_0015_01** (33 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Cám ơn công thức hay quá
Cảm ơn bạn nhiều. Lúc nấu thử mà muốn chỉnh vị mặn ngọt hay đổi nguyên liệu thì cứ nói mình
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

## Cách `de_quy`

### 1. Phân bố độ dài (token)

| Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất | Số câu trả lời bị chia |
|---|---|---|---|---|---|
| 40 | 21 | 33.5 | 38.8 | 74 | 0 |

| Nhóm | Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất |
|---|---|---|---|---|---|
| 01_chao_hoi | 40 | 21 | 33.5 | 38.8 | 74 |

Nhận xét: đoạn dài nhất gấp 4 lần đoạn ngắn nhất. Chênh lệch chủ yếu do nhóm Chào hỏi rất ngắn còn công thức nấu ăn dài; các đoạn dài đều bị chặn dưới giới hạn mô hình.

### 2. Số đoạn vượt giới hạn mô hình

**0**

### 3. Không mất chữ

Ghép `noi_dung` theo `thu_tu_doan` (bỏ `so_ky_tu_chong_lan` ký tự đầu mỗi đoạn), bỏ khoảng trắng, so với câu trả lời đã tiền xử lý.

Số cặp hỏi–đáp lỗi: **0**

### 4. Đọc thử 5 đoạn ngẫu nhiên (seed 42)

**de_quy_0008_01** (53 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Bạn biết nấu món miền Tây không
Biết chứ bạn. Món miền Tây là phần mình ưu tiên như canh chua cá lóc, cá kho tộ, lẩu mắm hay bánh xèo. Bạn muốn học món nào thì nói mình nhé
```

**de_quy_0002_01** (46 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Chào bot
Chào bạn nha. Mình là chatbot hướng dẫn nấu ăn và gợi ý món ăn theo nhu cầu dinh dưỡng. Bạn cần mình chỉ cách nấu món nào hay muốn mình gợi ý món cho bữa hôm nay
```

**de_quy_0018_01** (27 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Cảm ơn đã gợi ý món
Không có gì bạn. Mong bạn và gia đình có bữa cơm thật ngon
```

**de_quy_0016_01** (23 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Thanks
Không có chi bạn. Chúc bạn có bữa ăn ngon miệng
```

**de_quy_0015_01** (33 token)

```text
Chào hỏi, cảm ơn, tạm biệt · Cám ơn công thức hay quá
Cảm ơn bạn nhiều. Lúc nấu thử mà muốn chỉnh vị mặn ngọt hay đổi nguyên liệu thì cứ nói mình
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

## 8. Kết luận sơ bộ

Cách `cau_truc` giữ nguyên 40/40 cặp hỏi–đáp thành một đoạn, và khi phải chia thì ranh giới trùng ranh giới mục/tiêu đề con/dòng nên không cắt ngang dòng nguyên liệu hay bước nấu (0 ranh giới giữa dòng, so với 0 của `co_dinh` và 0 của `de_quy`); mỗi đoạn có tên mục nên dẫn nguồn được tới từng phần của câu trả lời. Cách `co_dinh` cắt ngang dòng, có khi cắt giữa một từ; cách `de_quy` ít cắt ngang hơn nhưng phần chồng lấn làm nội dung bị lặp giữa các đoạn. Với giới hạn 256 token, cả ba cách đều phải chia đúng 0 câu trả lời dài (chủ yếu nhóm 02, 03). `cau_truc` **có thể thua** khi: (1) đoạn rất ngắn (nhóm Chào hỏi, mục ngắn) mang ít thông tin nên vector kém phân biệt; (2) câu hỏi cần ghép nhiều cặp hỏi–đáp (ví dụ "gợi ý thực đơn ít béo cho người tiểu đường") — khi đó không cách cắt nào trong ba cách tự giải quyết được, phải dựa vào truy hồi nhiều đoạn; (3) đoạn dài gần giới hạn bị loãng nghĩa so với đoạn nhỏ của `de_quy`. **Phần V sẽ đo bằng số liệu, chưa kết luận cuối.**

