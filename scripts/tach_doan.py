"""Tách đoạn (chunking) kho hỏi–đáp nấu ăn (Bài 4 – Phần I).

Cách chạy (từ thư mục gốc project):
    .venv\\Scripts\\python.exe scripts/tach_doan.py                                   # cả ba cách, mọi nhóm
    .venv\\Scripts\\python.exe scripts/tach_doan.py --cach cau_truc
    .venv\\Scripts\\python.exe scripts/tach_doan.py --cach tat_ca --nhom 03_huong_dan_nau_mon_mien_tay

Đầu vào : data/groups/*/all.csv, cau_hinh/tach_doan.json
Đầu ra  : data/doan/doan_<cach>.jsonl, data/doan/_toan_bo.json (cách cau_truc), reports/kiem_tra_tach_doan.md
          Chạy một nhóm thì thêm đuôi _<nhom> vào tên file đầu ra và báo cáo, không ghi đè _toan_bo.json.
          Chạy một cách (khác tat_ca) thì báo cáo có đuôi _<cach>.
Chỉ tách đoạn: không sinh vector, không dựng kho vector, không truy hồi. Không dùng thư viện tách đoạn dựng sẵn.
"""
import argparse
import json
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tach_tu import TachTu, doc_csv, doc_tu_dien, tien_xu_ly, tim_dau_vao  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CAU_HINH_PATH = ROOT / "cau_hinh" / "tach_doan.json"
OUT_DIR = ROOT / "data" / "doan"
REPORTS = ROOT / "reports"
CAC_CACH = ["cau_truc", "co_dinh", "de_quy"]
BAT_BUOC = ["nhom", "id_goc", "tap", "nguon", "cau_hoi"]

CH = json.loads(CAU_HINH_PATH.read_text(encoding="utf-8"))
GIOI_HAN = CH["gioi_han_token_mo_hinh"]
KICH_THUOC = CH["kich_thuoc_doan"]
CHONG_LAN = CH["chong_lan"]
DU_PHONG = CH["du_phong_token"]
MUC_NGAN = CH["nguong_muc_ngan_token"]
CAN_TACH_TU = CH["can_tach_tu"]

# ------------------------------------------------------------ mô hình đếm token


def nap_tokenizer(ten):
    """Ưu tiên bản đã tải về máy, không có thì tải từ Hugging Face."""
    from transformers import AutoTokenizer
    try:
        return AutoTokenizer.from_pretrained(ten, local_files_only=True)
    except Exception:
        return AutoTokenizer.from_pretrained(ten)


class BoDem:
    """Đếm token bằng tokenizer của mô hình sinh vector; tách từ trước nếu mô hình cần."""

    def __init__(self):
        self.tok = nap_tokenizer(CH["ten_mo_hinh"])
        self.tach = TachTu(doc_tu_dien()) if CAN_TACH_TU else None
        self._tieu_de = {}
        self._dem = {}

    def dem(self, text):
        """Số token (không tính <s> </s>)."""
        if text not in self._dem:
            self._dem[text] = len(self.tok.tokenize(text)) if text.strip() else 0
        return self._dem[text]

    def dem_day_du(self, text):
        """Số token thật sự đưa vào mô hình (có <s> </s>)."""
        return len(self.tok(text)["input_ids"])

    def tieu_de_mo_hinh(self, tieu_de):
        """Bản tiêu đề đưa vào mô hình (đã tách từ nếu cần)."""
        if tieu_de not in self._tieu_de:
            # tách từ từng phần riêng: tách cả dòng thì underthesea nối "·" vào từ sau ("·_Bò" → <unk>)
            self._tieu_de[tieu_de] = (" · ".join(self.tach.tach_cau_hoi(p) for p in tieu_de.split(" · "))
                                      if CAN_TACH_TU else tieu_de)
        return self._tieu_de[tieu_de]


def tieu_de(cap, ten_muc, muc_truoc=""):
    """<Nhóm> · <Câu hỏi> · <Tên mục>, thêm tên mục trước khi đoạn phụ thuộc mục trước."""
    s = " · ".join(x for x in (cap.nhom, cap.cau_hoi, ten_muc) if x)
    return f"{s} (tiếp theo mục: {muc_truoc})" if muc_truoc else s


# ------------------------------------------------------------ một cặp hỏi–đáp


class CapHoiDap:
    def __init__(self, r, folder, bd, thong_ke):
        self.bd = bd
        self.id = int(r["ID"])
        self.nhom = r["Nhóm"].strip()
        self.folder = folder
        self.tap = r["Tập"].strip()
        self.nguon = r["Nguồn"].strip()
        self.cau_hoi = " ".join(tien_xu_ly(r["Câu hỏi"], thong_ke).split())
        self.tl = tien_xu_ly(r["Câu trả lời"], thong_ke)  # giữ \n làm ranh giới cấu trúc
        if CAN_TACH_TU:
            self.mo_hinh = bd.tach.tach_cau_tra_loi(self.tl)[0]
        else:
            self.mo_hinh = self.tl
        self._can_chinh()
        self._spans = None

    def _can_chinh(self):
        """Ghép từng ký tự (không phải khoảng trắng) của bản gốc với bản đưa vào mô hình.

        Bản tách từ chỉ khác bản gốc ở khoảng trắng và dấu _ nối âm tiết, nên ghép theo thứ tự là đủ.
        """
        g, m = self.tl, self.mo_hinh
        self.g2m, self.m2g = [-1] * len(g), [-1] * len(m)
        j = 0
        for i, c in enumerate(g):
            if c.isspace():
                continue
            while j < len(m) and (m[j].isspace() or (CAN_TACH_TU and m[j] == "_" and c != "_")):
                j += 1
            if j >= len(m) or m[j] != c:
                sys.exit(f"ID {self.id}: không căn được bản gốc và bản tách từ tại ký tự {i} ({c!r})")
            self.g2m[i], self.m2g[j] = j, i
            j += 1

    def cat_trang(self, a, b):
        """Bỏ khoảng trắng hai đầu khoảng [a, b)."""
        while a < b and self.tl[a].isspace():
            a += 1
        while b > a and self.tl[b - 1].isspace():
            b -= 1
        return a, b

    def mo_hinh_doan(self, a, b):
        """Phần văn bản đưa vào mô hình ứng với bản gốc [a, b)."""
        idx = [self.g2m[i] for i in range(a, b) if self.g2m[i] >= 0]
        if not idx:
            return ""
        return self.mo_hinh[idx[0]:idx[-1] + 1].strip("_ ")

    def dem(self, a, b):
        return self.bd.dem(self.mo_hinh_doan(a, b))

    def ngan_sach(self, ten_muc, muc_truoc=""):
        """Kích thước thực dùng = min(kich_thuoc_doan, giới hạn − token tiêu đề − dự phòng)."""
        hdr = self.bd.tieu_de_mo_hinh(tieu_de(self, ten_muc, muc_truoc))
        return min(KICH_THUOC, GIOI_HAN - self.bd.dem(hdr) - DU_PHONG)

    def vua(self, a, b, ten_muc, muc_truoc=""):
        return self.dem(a, b) <= self.ngan_sach(ten_muc, muc_truoc)

    def spans(self):
        """Chuỗi token của cả câu trả lời, mỗi token kèm khoảng ký tự [a, b) trong bản gốc."""
        if self._spans is not None:
            return self._spans
        out = []
        for m in re.finditer(r"\S+", self.mo_hinh):
            pos = m.start()
            for p in self.bd.tok.tokenize(m.group()):
                p = p[:-2] if p.endswith("@@") else p
                goc = [self.m2g[x] for x in range(pos, pos + len(p)) if self.m2g[x] >= 0]
                pos += len(p)
                out.append((min(goc), max(goc) + 1) if goc else None)
            if pos != m.end():
                sys.exit(f"ID {self.id}: mảnh token không ghép lại được thành từ {m.group()!r}")
        # token chỉ gồm dấu _ thì không có ký tự gốc: cho dài 0, dính vào token trước
        truoc = 0
        for i, s in enumerate(out):
            out[i] = s if s else (truoc, truoc)
            truoc = out[i][1]
        self._spans = out
        return out


# ------------------------------------------------------------ đệ quy theo dấu phân cách

# (tên, regex) theo thứ tự ưu tiên; mọi dấu phân cách chỉ là khoảng trắng nên cắt không mất chữ
PHAN_CACH = [
    ("\\n\\n (hết mục)", re.compile(r"\n[ \t]*\n\s*")),
    ("\\n trước tiêu đề con", re.compile(r"\n(?=[^-\n][^\n]*(?<![.!?;,])(?:\n|$))")),
    ("\\n- (gạch đầu dòng)", re.compile(r"\n(?=-\s)")),
    ("\\n", re.compile(r"\n")),
    (". ! ?", re.compile(r"(?<=[.!?])[ \t]+")),
    (", ", re.compile(r"(?<=,)[ \t]+")),
    ("dấu cách", re.compile(r"\s+")),
]
CAP_CAU = 4  # vị trí của ". ! ?" trong PHAN_CACH
SO_THU_TU = re.compile(r"(?:^|\s)(?:[Bb]ước\s+)?\d+[.)]$")
DONG = re.compile(r"[^\n]+")


def diem_cat_hop_le(tl, cap_do, pos):
    """Không cắt sau số thứ tự (1. / Bước 1.) và không tách số khỏi chữ ngay sau nó (1.5 lít, Bước 1).

    Số thập phân (1.5, 2,5) và giờ (7:30) không có khoảng trắng nên không bao giờ bị cắt.
    """
    truoc = tl[max(0, pos - 12):pos]
    if PHAN_CACH[cap_do][0] == ". ! ?" and SO_THU_TU.search(truoc):
        return False
    if PHAN_CACH[cap_do][0] == "dấu cách" and (truoc[-1:].isdigit() or re.search(r"[Bb]ước$", truoc)):
        return False
    return True


def tach_manh(cap, a, b, cap_do):
    manh, s = [], a
    for m in PHAN_CACH[cap_do][1].finditer(cap.tl, a, b):
        if m.start() <= s or not diem_cat_hop_le(cap.tl, cap_do, m.start()):
            continue
        manh.append((s, m.start()))
        s = m.end()
    manh.append((s, b))
    return [cap.cat_trang(x, y) for x, y in manh if cap.tl[x:y].strip()]


def cat_cung(cap, a, b, B):
    """Phương án cuối: một 'từ' dài hơn B token thì cắt theo token."""
    sp = [s for s in cap.spans() if s[0] >= a and s[1] <= b]
    return [cap.cat_trang(sp[i][0], sp[min(i + B, len(sp)) - 1][1]) for i in range(0, len(sp), B)] or [(a, b)]


def gop_manh(cap, manh, B, O):
    """Gộp các mẩu liền kề khi tổng chưa vượt B; đoạn mới mang theo đuôi đoạn trước ≤ O token."""
    doan, cur = [], []
    for p in manh:
        if cur and cap.dem(cur[0][0], p[1]) > B:
            doan.append((cur[0][0], cur[-1][1]))
            while cur and (cap.dem(cur[0][0], cur[-1][1]) > O or cap.dem(cur[0][0], p[1]) > B):
                cur.pop(0)
        cur.append(p)
    if cur:
        doan.append((cur[0][0], cur[-1][1]))
    return doan


def chia_de_quy(cap, a, b, B, O, cap_do=0):
    if cap.dem(a, b) <= B:
        return [(a, b)]
    while cap_do < len(PHAN_CACH):
        manh = tach_manh(cap, a, b, cap_do)
        if len(manh) > 1:
            break
        cap_do += 1
    else:
        return cat_cung(cap, a, b, B)
    out, tot = [], []
    for p in manh:
        if cap.dem(*p) <= B:
            tot.append(p)
            continue
        if tot:
            out += gop_manh(cap, tot, B, O)
            tot = []
        out += chia_de_quy(cap, p[0], p[1], B, O, cap_do + 1)
    if tot:
        out += gop_manh(cap, tot, B, O)
    return out


def doan_moi(a, b, ten_muc="", chia=False, muc_truoc=""):
    return {"a": a, "b": b, "ten_muc": ten_muc, "chia_theo_cau": chia, "muc_truoc": muc_truoc}


def cat_de_quy(cap):
    a, b = cap.cat_trang(0, len(cap.tl))
    B = cap.ngan_sach("")
    return [doan_moi(x, y) for x, y in chia_de_quy(cap, a, b, B, CHONG_LAN)]


# ------------------------------------------------------------ cố định theo số token


def cat_co_dinh(cap):
    """Cắt chuỗi token mỗi B token, chồng lấn O token, bất kể giữa câu hay giữa mục."""
    sp = cap.spans()
    B = cap.ngan_sach("")
    O = min(CHONG_LAN, B // 2)
    out, s = [], 0
    while sp:
        e = min(s + B, len(sp))
        # mẩu cắt giữa từ khi token hóa lại có thể ra nhiều mảnh hơn: lùi điểm cắt đến khi vừa thật
        while e - s > 1 and cap.dem(sp[s][0], sp[e - 1][1]) > B:
            e -= 1
        out.append(doan_moi(*cap.cat_trang(sp[s][0], sp[e - 1][1])))
        if e >= len(sp):
            break
        s = max(e - O, s + 1)
    return out or [doan_moi(0, len(cap.tl))]


# ------------------------------------------------------------ theo cấu trúc văn bản

PHU_THUOC = re.compile(r"\bđã (sơ chế|ướp|nướng|luộc|chiên|rang|chuẩn bị|làm sạch|rửa sạch|xào|hầm|ngâm|cắt|thái|băm|"
                       r"pha|trộn|phi|nấu|hấp|xay|giã|lọc)\b|\b(?:nêu|như) trên\b|\btrên đây\b", re.I)

def la_tieu_de_muc(dong, so_dong):
    return so_dong > 1 and not dong.startswith("-") and not re.search(r"[.!?;,]$", dong) and len(dong) <= 120


def la_tieu_de_con(dong, dong_sau):
    return (dong_sau is not None and dong_sau.startswith("-") and not dong.startswith("-")
            and not re.search(r"[.!?;,]$", dong) and len(dong) <= 80)


def ten_gon(dong):
    return dong.strip().rstrip(":").strip()


def doc_muc(cap):
    """Các mục (ngăn bằng dòng trống), mỗi mục: khoảng ký tự, danh sách dòng, tên mục."""
    muc, s = [], 0
    for m in re.finditer(r"\n[ \t]*\n\s*", cap.tl):
        muc.append((s, m.start()))
        s = m.end()
    muc.append((s, len(cap.tl)))
    out = []
    for a, b in muc:
        dong = [cap.cat_trang(m.start(), m.end()) for m in DONG.finditer(cap.tl, a, b)]
        dong = [d for d in dong if d[0] < d[1]]
        if not dong:
            continue
        dau = cap.tl[dong[0][0]:dong[0][1]]
        out.append({"a": dong[0][0], "b": dong[-1][1], "dong": dong,
                    "ten": ten_gon(dau) if la_tieu_de_muc(dau, len(dong)) else ""})
    # mục không có dòng tiêu đề: mục đầu là phần giới thiệu, mục cuối là lời kết, ở giữa là ghi chú
    for i, mc in enumerate(out):
        mc["co_dong_tieu_de"] = bool(mc["ten"])
        if not mc["ten"]:
            mc["ten"] = "Giới thiệu" if i == 0 else "Lời kết" if i == len(out) - 1 else "Ghi chú"
    return out


def ten_nhom_muc(nhom):
    """Tên của nhóm mục; bỏ 'Lời kết'/'Ghi chú' khi đã có mục mang tên thật."""
    ten = [m["ten"] for m in nhom if m["co_dong_tieu_de"] or m["ten"] == "Giới thiệu"]
    return " + ".join(ten or [m["ten"] for m in nhom])


def gop_dong(cap, dong, ten_dau, ten_tiep, muc_truoc=""):
    """Gộp các dòng liền nhau thành đoạn; không bao giờ cắt giữa một dòng trừ khi riêng dòng đó quá dài."""
    out, cur = [], []

    def ten():
        return ten_dau if not out else ten_tiep

    for d in dong:
        if cur and cap.vua(cur[0][0], d[1], ten(), muc_truoc):
            cur.append(d)
            continue
        if cur:
            out.append(doan_moi(cur[0][0], cur[-1][1], ten(), True, muc_truoc))
            cur = []
        if cap.vua(d[0], d[1], ten(), muc_truoc):
            cur = [d]
        else:  # một dòng vẫn quá dài: cắt theo câu → dấu phẩy → dấu cách, không chồng lấn
            B = cap.ngan_sach(ten_tiep, muc_truoc)
            for x, y in chia_de_quy(cap, d[0], d[1], B, 0, CAP_CAU):
                out.append(doan_moi(x, y, ten(), True, muc_truoc))
    if cur:
        out.append(doan_moi(cur[0][0], cur[-1][1], ten(), True, muc_truoc))
    return out


def chia_muc(cap, mc):
    """Mục quá dài: chia theo tiêu đề con, rồi theo dòng. Tên mục được lặp lại ở tiêu đề mọi đoạn con."""
    dong = mc["dong"]
    txt = [cap.tl[a:b] for a, b in dong]
    khoi = []  # [tên tiêu đề con, [dòng]]
    for i, d in enumerate(dong):
        sau = txt[i + 1] if i + 1 < len(dong) else None
        if i > 0 and la_tieu_de_con(txt[i], sau):
            if len(khoi) == 1 and khoi[0][1] == [dong[0]] and mc["co_dong_tieu_de"] and not khoi[0][0]:
                khoi[0] = [ten_gon(txt[i]), khoi[0][1] + [d]]  # dòng tên mục đi cùng tiêu đề con đầu tiên
            else:
                khoi.append([ten_gon(txt[i]), [d]])
        elif khoi:
            khoi[-1][1].append(d)
        else:
            khoi.append(["", [d]])

    def ten(ds_khoi):
        con = [k[0] for k in ds_khoi if k[0]]
        return f"{mc['ten']} – {', '.join(con)}" if con else mc["ten"]

    out, cur = [], []
    for k in khoi:
        if cur and cap.vua(cur[0][1][0][0], k[1][-1][1], ten(cur + [k])):
            cur.append(k)
            continue
        if cur:
            out.append(doan_moi(cur[0][1][0][0], cur[-1][1][-1][1], ten(cur), True))
            cur = []
        if cap.vua(k[1][0][0], k[1][-1][1], ten([k])):
            cur = [k]
        else:
            out += gop_dong(cap, k[1], ten([k]), ten([k]) + " (tiếp)")
    if cur:
        out.append(doan_moi(cur[0][1][0][0], cur[-1][1][-1][1], ten(cur), True))
    return out


def tim_muc_truoc(cap, ds, k):
    """Đoạn k nhắc tới kết quả của bước trước ('đã sơ chế', 'đã nướng'...) mà bước đó nằm ở đoạn trước."""
    nd = cap.tl[ds[k]["a"]:ds[k]["b"]]
    for m in PHU_THUOC.finditer(nd):
        dong_tu = (m.group(1) or "").lower()
        if dong_tu and dong_tu in nd[:m.start()].lower().replace("đã " + dong_tu, ""):
            continue  # bước được nhắc nằm ngay trong đoạn này
        for j in range(k - 1, -1, -1):  # đoạn trước gần nhất có tên hoặc nội dung chứa bước đó
            if dong_tu and (dong_tu in ds[j]["ten_muc"].lower() or dong_tu in cap.tl[ds[j]["a"]:ds[j]["b"]].lower()):
                return ds[j]["ten_muc"]
        return ds[k - 1]["ten_muc"]
    return ""


def cat_cau_truc(cap):
    a, b = cap.cat_trang(0, len(cap.tl))
    if cap.vua(a, b, ""):
        return [doan_moi(a, b)]  # cả cặp hỏi–đáp vừa một đoạn
    muc = doc_muc(cap)
    nhom = [[m] for m in muc]

    def vua_nhom(g):
        return cap.vua(g[0]["a"], g[-1]["b"], ten_nhom_muc(g))

    def ngan(g):
        return cap.dem(g[0]["a"], g[-1]["b"]) < MUC_NGAN

    # mục quá ngắn gộp với mục liền sau (cùng câu trả lời) nếu vẫn vừa
    i = 0
    while i < len(nhom):
        if i + 1 < len(nhom) and ngan(nhom[i]) and vua_nhom(nhom[i] + nhom[i + 1]):
            nhom[i] += nhom.pop(i + 1)
        else:
            i += 1
    if len(nhom) > 1 and ngan(nhom[-1]) and vua_nhom(nhom[-2] + nhom[-1]):  # mục cuối không có mục sau
        cuoi = nhom.pop()
        nhom[-1] += cuoi

    ds = []
    for g in nhom:
        if vua_nhom(g):
            ds.append(doan_moi(g[0]["a"], g[-1]["b"], ten_nhom_muc(g)))
        else:  # nhóm không vừa luôn chỉ có một mục (chỉ gộp khi vừa)
            ds += chia_muc(cap, g[0])

    # ngoại lệ phụ thuộc mục trước: không chép chồng nội dung, chỉ đưa tên mục trước vào tiêu đề
    kq = []
    for k, d in enumerate(ds):
        muc_truoc = tim_muc_truoc(cap, ds, k) if k > 0 else ""
        if muc_truoc and not cap.vua(d["a"], d["b"], d["ten_muc"], muc_truoc):
            dong = [cap.cat_trang(m.start(), m.end()) for m in DONG.finditer(cap.tl, d["a"], d["b"])]
            kq += gop_dong(cap, [x for x in dong if x[0] < x[1]], d["ten_muc"], d["ten_muc"] + " (tiếp)", muc_truoc)
        else:
            d["muc_truoc"] = muc_truoc
            kq.append(d)
    return kq


CAT = {"cau_truc": cat_cau_truc, "co_dinh": cat_co_dinh, "de_quy": cat_de_quy}

# ------------------------------------------------------------ bản ghi đoạn


def ty_le_chu_so(text):
    s = re.sub(r"\s", "", text)
    return sum(c.isdigit() for c in s) / len(s) if s else 0.0


def tao_ban_ghi(cap, cach, ds):
    out, truoc_b = [], None
    for k, d in enumerate(ds, 1):
        a, b = d["a"], d["b"]
        noi_dung = cap.tl[a:b]
        hdr = tieu_de(cap, d["ten_muc"], d["muc_truoc"])
        bg = {"chunk_id": f"{cach}_{cap.id:04d}_{k:02d}", "cach_cat": cach, "id_goc": cap.id,
              "nhom": cap.nhom, "nhom_folder": cap.folder, "tap": cap.tap, "cau_hoi": cap.cau_hoi,
              "ten_muc": d["ten_muc"], "muc_truoc": d["muc_truoc"],
              "thu_tu_doan": k, "tong_so_doan_cua_cau": len(ds), "nguon": cap.nguon,
              "noi_dung": noi_dung, "noi_dung_kem_tieu_de": f"{hdr}\n{noi_dung}"}
        if CAN_TACH_TU:
            # PhoBERT đổi \n thành <unk> nên tiêu đề và nội dung nối bằng dấu cách
            bg["noi_dung_kem_tieu_de_tach_tu"] = f"{cap.bd.tieu_de_mo_hinh(hdr)} {cap.mo_hinh_doan(a, b)}"
            vao = bg["noi_dung_kem_tieu_de_tach_tu"]
        else:
            vao = bg["noi_dung_kem_tieu_de"]
        canh_bao = []
        if len(noi_dung) < CH["nguong_doan_ngan_ky_tu"]:
            canh_bao.append("qua_ngan")
        if ty_le_chu_so(noi_dung) > CH["nguong_ty_le_chu_so"]:
            canh_bao.append("toan_so")
        if d["muc_truoc"]:
            canh_bao.append("phu_thuoc_muc_truoc")
        so_token = cap.bd.dem_day_du(vao)
        if so_token > GIOI_HAN:
            canh_bao.append("vuot_gioi_han")
        bg.update({"so_token": so_token, "so_ky_tu": len(noi_dung), "vi_tri_ky_tu": [a, b],
                   "so_ky_tu_chong_lan": max(0, truoc_b - a) if truoc_b is not None else 0,
                   "chia_theo_cau": d["chia_theo_cau"], "canh_bao": canh_bao})
        out.append(bg)
        truoc_b = b
    return out


# ------------------------------------------------------------ báo cáo


def bo_trang(s):
    return re.sub(r"\s+", "", s)


def kiem_mat_chu(doan, caps):
    theo_id = defaultdict(list)
    for d in doan:
        theo_id[d["id_goc"]].append(d)
    loi = []
    for cid, cap in caps.items():
        ds = sorted(theo_id.get(cid, []), key=lambda d: d["thu_tu_doan"])
        ghep = "".join(d["noi_dung"][d["so_ky_tu_chong_lan"]:] for d in ds)
        if bo_trang(ghep) != bo_trang(cap.tl):
            loi.append(cid)
    return loi


def thong_ke_token(ds):
    t = [d["so_token"] for d in ds]
    if not t:
        return 0, 0, 0, 0, 0.0
    return len(t), min(t), max(t), statistics.median(t), statistics.mean(t)


def o_bang(s, n=None):
    s = s.replace("|", "\\|").replace("\n", " ⏎ ")
    return s if n is None or len(s) <= n else s[:n] + "…"


def cat_ngang_dong(cap, d, cuoi):
    """Ranh giới đoạn nằm giữa một dòng? Trả về (phần dòng trước ranh giới, phần sau) hoặc None."""
    tl = cap.tl
    pos = d["vi_tri_ky_tu"][1] if cuoi else d["vi_tri_ky_tu"][0]
    if pos <= 0 or pos >= len(tl) or "\n" in (tl[pos - 1], tl[pos]):
        return None
    dau = tl.rfind("\n", 0, pos) + 1
    het = tl.find("\n", pos)
    het = len(tl) if het < 0 else het
    return tl[dau:pos], tl[pos:het]


def ds_cat_ngang(cap, ds):
    """Mọi ranh giới (cuối đoạn trước, đầu đoạn sau) của một cặp hỏi–đáp nằm giữa một dòng."""
    out = [x for d in ds[:-1] for x in [cat_ngang_dong(cap, d, True)] if x]
    return out + [x for d in ds[1:] for x in [cat_ngang_dong(cap, d, False)] if x]


def viet_bao_cao(path, kq, caps, thong_ke, nhom_chay):
    cfg = CH
    L = ["# Kiểm tra tách đoạn (Bài 4 – Phần I)", "",
         f"- Mô hình sinh vector: `{cfg['ten_mo_hinh']}` (PhoBERT, `can_tach_tu = {str(CAN_TACH_TU).lower()}`).",
         f"- Giới hạn token mô hình: **{GIOI_HAN}** ({cfg['nguon_gioi_han_token']}).",
         "- Đếm token: `AutoTokenizer` của mô hình trên **bản đã tách từ** (hàm `TachTu` của `scripts/tach_tu.py`), "
         "tính cả tiêu đề cha và `<s>`, `</s>`.",
         f"- Tham số: `kich_thuoc_doan = {KICH_THUOC}`, `chong_lan = {CHONG_LAN}`, dự phòng {DU_PHONG} token, "
         f"mục ngắn < {MUC_NGAN} token, đoạn ngắn < {cfg['nguong_doan_ngan_ky_tu']} ký tự, "
         f"ngưỡng toàn số {cfg['nguong_ty_le_chu_so']}, seed {cfg['seed']}.",
         f"- Số cặp hỏi–đáp: {len(caps)} (Train {sum(c.tap == 'Train' for c in caps.values())}, "
         f"Test {sum(c.tap == 'Test' for c in caps.values())}). Dòng trống đã bỏ: {thong_ke['dong_trong']}.",
         "- Tiền xử lý: đúng hàm `tien_xu_ly` của `scripts/tach_tu.py` (NFC, thống nhất kiểu dấu, khoảng trắng lạ, "
         "nháy/gạch, dấu câu dính chữ), giữ nguyên `\\n`. `noi_dung` là văn bản đã tiền xử lý.", ""]
    if nhom_chay:
        L += [f"> Chỉ chạy nhóm `{nhom_chay}`.", ""]

    # kích thước thực dùng
    ns = sorted(c.ngan_sach("") for c in caps.values())
    L += ["## 0. Kích thước đoạn thực dùng", "",
          f"Kích thước thực dùng = `min({KICH_THUOC}, {GIOI_HAN} − token tiêu đề cha − {DU_PHONG})`, tính riêng cho từng "
          "đoạn vì tiêu đề cha (Nhóm · Câu hỏi · Tên mục) dài ngắn khác nhau.", "",
          f"- Với tiêu đề không có tên mục: ngắn nhất **{ns[0]}**, trung vị **{statistics.median(ns):g}**, "
          f"lớn nhất **{ns[-1]}** token nội dung.",
          f"- Con số {KICH_THUOC} của slide 7 **không bao giờ được dùng**: mô hình chỉ nhận {GIOI_HAN} token, "
          f"để {KICH_THUOC} thì phần đuôi bị mô hình cắt bỏ mà không cảnh báo.",
          f"- Chồng lấn thực dùng: cố định = `min({CHONG_LAN}, kích thước/2)`, đệ quy ≤ {CHONG_LAN} token (theo mẩu), "
          "cấu trúc = 0.",
          "- **Không cài cách cắt theo ngữ nghĩa** (slide 14): phải sinh vector cho từng câu để tìm điểm cắt, tốn kém, "
          "trong khi dataset đã có cấu trúc rõ (mục, tiêu đề con, gạch đầu dòng).", ""]

    tong_hop = {}
    for cach, doan in kq.items():
        n, mn, mx, med, mean = thong_ke_token(doan)
        vuot = [d["chunk_id"] for d in doan if d["so_token"] > GIOI_HAN]
        loi = kiem_mat_chu(doan, caps)
        thieu = {f: sum(1 for d in doan if d.get(f) in (None, "")) for f in BAT_BUOC}
        cb = Counter(c for d in doan for c in d["canh_bao"])
        chia = [d for d in doan if d["chia_theo_cau"]]
        theo_id = defaultdict(list)
        for d in doan:
            theo_id[d["id_goc"]].append(d)
        cat_ngang = sum(len(ds_cat_ngang(caps[i], ds)) for i, ds in theo_id.items())
        tong_hop[cach] = {"cat_ngang": cat_ngang,"so_doan": n, "min": mn, "trung_vi": med, "max": mx, "vuot": len(vuot), "mat_chu": len(loi),
                          "qua_ngan": cb["qua_ngan"], "toan_so": cb["toan_so"], "vuot_ids": vuot,
                          "so_cau_bi_chia": len({d["id_goc"] for d in doan if d["tong_so_doan_cua_cau"] > 1})}

        L += [f"## Cách `{cach}`", "",
              "### 1. Phân bố độ dài (token)", "",
              "| Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất | Số câu trả lời bị chia |", "|---|---|---|---|---|---|",
              f"| {n} | {mn} | {med:g} | {mean:.1f} | {mx} | {tong_hop[cach]['so_cau_bi_chia']} |", "",
              "| Nhóm | Số đoạn | Ngắn nhất | Trung vị | Trung bình | Dài nhất |", "|---|---|---|---|---|---|"]
        theo_nhom = defaultdict(list)
        for d in doan:
            theo_nhom[d["nhom_folder"]].append(d)
        for f in sorted(theo_nhom):
            a = thong_ke_token(theo_nhom[f])
            L.append(f"| {f} | {a[0]} | {a[1]} | {a[3]:g} | {a[4]:.1f} | {a[2]} |")
        L += ["", f"Nhận xét: đoạn dài nhất gấp {mx / max(mn, 1):.0f} lần đoạn ngắn nhất. Chênh lệch chủ yếu do "
              "nhóm Chào hỏi rất ngắn còn công thức nấu ăn dài; các đoạn dài đều bị chặn dưới giới hạn mô hình.", ""]

        L += ["### 2. Số đoạn vượt giới hạn mô hình", "", f"**{len(vuot)}**" + (": " + ", ".join(vuot) if vuot else ""), ""]
        L += ["### 3. Không mất chữ", "",
              "Ghép `noi_dung` theo `thu_tu_doan` (bỏ `so_ky_tu_chong_lan` ký tự đầu mỗi đoạn), bỏ khoảng trắng, "
              "so với câu trả lời đã tiền xử lý.", "",
              f"Số cặp hỏi–đáp lỗi: **{len(loi)}**" + (": " + ", ".join(map(str, loi)) if loi else ""), ""]

        L += [f"### 4. Đọc thử 5 đoạn ngẫu nhiên (seed {cfg['seed']})", ""]
        for d in random.Random(cfg["seed"]).sample(doan, min(5, len(doan))):
            L += [f"**{d['chunk_id']}** ({d['so_token']} token)", "", "```text", d["noi_dung_kem_tieu_de"], "```", ""]

        L += ["### 5. Siêu dữ liệu đầy đủ", "", "| Trường | Số đoạn thiếu |", "|---|---|"]
        L += [f"| `{f}` | {v} |" for f, v in thieu.items()] + [""]

        L += ["### 6. Cảnh báo", "",
              f"- `qua_ngan`: {cb['qua_ngan']} · `toan_so`: {cb['toan_so']} · `chia_theo_cau`: {len(chia)} · "
              f"`phu_thuoc_muc_truoc`: {cb['phu_thuoc_muc_truoc']}",
              f"- Ranh giới đoạn nằm giữa một dòng (cắt ngang dòng nguyên liệu/bước nấu/câu), toàn bộ dữ liệu: **{cat_ngang}**", ""]
        if cach == "cau_truc":
            ngan = [d for d in doan if "qua_ngan" in d["canh_bao"]]
            L += ["**Đoạn quá ngắn** (không tự gộp, không tự loại; cần kiểm tay):", ""]
            if ngan:
                L += ["| chunk_id | Nhóm | Câu hỏi | Nội dung |", "|---|---|---|---|"]
                L += [f"| {d['chunk_id']} | {d['nhom_folder']} | {o_bang(d['cau_hoi'])} | {o_bang(d['noi_dung'])} |" for d in ngan]
            else:
                L.append("- Không có.")
            so = [d for d in doan if "toan_so" in d["canh_bao"]]
            L += ["", "**Đoạn toàn số** (có thể là bảng dinh dưỡng bị vỡ):", ""]
            L += [f"- {d['chunk_id']}: `{o_bang(d['noi_dung'], 150)}`" for d in so] or ["- Không có."]
            L += ["", "**Đoạn chia theo tiêu đề con / dòng** (`chia_theo_cau = true`):", ""]
            if chia:
                L += ["| chunk_id | Câu hỏi | Tên mục | Token |", "|---|---|---|---|"]
                L += [f"| {d['chunk_id']} | {o_bang(d['cau_hoi'], 60)} | {o_bang(d['ten_muc'])} | {d['so_token']} |" for d in chia]
            else:
                L.append("- Không có.")
            pt = [d for d in doan if d["muc_truoc"]]
            L += ["", "**Ngoại lệ phụ thuộc mục trước** (tên mục trước được đưa vào tiêu đề cha, không chép chồng nội dung):", ""]
            if pt:
                L += ["| chunk_id | Tên mục | Mục trước | Câu gây phụ thuộc |", "|---|---|---|---|"]
                for d in pt:
                    m = PHU_THUOC.search(d["noi_dung"])
                    cau = d["noi_dung"][max(0, m.start() - 40):m.end() + 20] if m else ""
                    L.append(f"| {d['chunk_id']} | {o_bang(d['ten_muc'])} | {o_bang(d['muc_truoc'])} | …{o_bang(cau)}… |")
            else:
                L.append("- Không có.")
            L.append("")
        else:
            ids = [d["chunk_id"] for d in doan if "qua_ngan" in d["canh_bao"]]
            L += [f"- Đoạn quá ngắn: {', '.join(ids) if ids else 'không có'}",
                  f"- Đoạn toàn số: {', '.join(d['chunk_id'] for d in doan if 'toan_so' in d['canh_bao']) or 'không có'}", ""]

    # 7. so sánh ba cách trên cùng một câu dài
    if len(kq) > 1:
        L += ["## 7. So sánh các cách cắt trên cùng một câu dài", ""]
        def dai_nhat(tien_to):
            ds = [c for c in caps.values() if c.folder.startswith(tien_to)]
            return max(ds, key=lambda c: (c.dem(0, len(c.tl)), -c.id)) if ds else None

        chon = [i for i in (49,) if i in caps]
        c09 = dai_nhat("09_")
        if c09:
            chon.append(c09.id)
            if c09.dem(0, len(c09.tl)) <= c09.ngan_sach(""):
                L += [f"> Câu dài nhất nhóm 09 (ID {c09.id}) chỉ {c09.dem(0, len(c09.tl))} token nội dung, vừa một đoạn, "
                      "nên cả ba cách cho cùng một đoạn: **không có câu trả lời nào của nhóm 09 phải chia**. "
                      "Thêm câu dài nhất nhóm 02 để có ví dụ thứ hai thật sự bị chia.", ""]
                c02 = dai_nhat("02_")
                if c02:
                    chon.append(c02.id)
        for cid in chon:
            cap = caps[cid]
            theo = {c: [d for d in kq[c] if d["id_goc"] == cid] for c in kq}
            L += [f"### ID {cid} – {cap.cau_hoi} ({cap.folder}, {cap.dem(0, len(cap.tl))} token nội dung)", "",
                  "| # | " + " | ".join(f"`{c}`" for c in kq) + " |", "|---|" + "---|" * len(kq)]
            for k in range(max(len(v) for v in theo.values())):
                o = []
                for c in kq:
                    if k < len(theo[c]):
                        d = theo[c][k]
                        nd = d["noi_dung"]
                        dau, cuoi = o_bang(nd[:60]), o_bang(nd[-60:])
                        ten = o_bang(d["ten_muc"]) or ("(cả câu)" if d["tong_so_doan_cua_cau"] == 1 else "(không có tên mục)")
                        o.append(f"{d['so_token']} tok · *{ten}*<br>«{dau}…»<br>…«{cuoi}»")
                    else:
                        o.append("")
                L.append(f"| {k + 1} | " + " | ".join(o) + " |")
            L.append("")
            for c in kq:
                cat = ds_cat_ngang(cap, theo[c])
                L.append(f"- `{c}`: {len(cat)} ranh giới nằm giữa một dòng" + (":" if cat else "."))
                L += [f"    - «{o_bang(t[-50:])}**‖**{o_bang(s[:50])}»" for t, s in cat]
            L.append("")
            for c in kq:
                L += [f"<details><summary><code>{c}</code>: {len(theo[c])} đoạn (bấm để xem nguyên văn)</summary>", ""]
                for d in theo[c]:
                    L += [f"**{d['chunk_id']}** ({d['so_token']} token, chồng lấn {d['so_ky_tu_chong_lan']} ký tự)", "",
                          "```text", d["noi_dung_kem_tieu_de"], "```", ""]
                L += ["</details>", ""]

    # 8. kết luận sơ bộ
    if len(kq) == 3:
        th = tong_hop
        L += ["## 8. Kết luận sơ bộ", "",
              f"Cách `cau_truc` giữ nguyên {len(caps) - th['cau_truc']['so_cau_bi_chia']}/{len(caps)} cặp hỏi–đáp thành "
              "một đoạn, và khi phải chia thì ranh giới trùng ranh giới mục/tiêu đề con/dòng nên không cắt ngang dòng "
              f"nguyên liệu hay bước nấu ({th['cau_truc']['cat_ngang']} ranh giới giữa dòng, so với "
              f"{th['co_dinh']['cat_ngang']} của `co_dinh` và {th['de_quy']['cat_ngang']} của `de_quy`); mỗi đoạn có tên mục "
              "nên dẫn nguồn được tới từng phần của câu trả lời. "
              "Cách `co_dinh` cắt ngang dòng, có khi cắt giữa một từ; cách `de_quy` ít cắt ngang hơn nhưng phần chồng lấn "
              "làm nội dung bị lặp giữa các đoạn. Với giới hạn 256 token, cả ba cách đều phải chia đúng "
              f"{th['cau_truc']['so_cau_bi_chia']} câu trả lời dài (chủ yếu nhóm 02, 03). "
              "`cau_truc` **có thể thua** khi: (1) đoạn rất ngắn (nhóm Chào hỏi, mục ngắn) mang ít "
              "thông tin nên vector kém phân biệt; (2) câu hỏi cần ghép nhiều cặp hỏi–đáp (ví dụ \"gợi ý thực đơn ít "
              "béo cho người tiểu đường\") — khi đó không cách cắt nào trong ba cách tự giải quyết được, phải dựa vào "
              "truy hồi nhiều đoạn; (3) đoạn dài gần giới hạn bị loãng nghĩa so với đoạn nhỏ của `de_quy`. "
              "**Phần V sẽ đo bằng số liệu, chưa kết luận cuối.**", ""]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
    return tong_hop


# ------------------------------------------------------------ main


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Tách đoạn kho hỏi–đáp (Bài 4 – Phần I)")
    ap.add_argument("--cach", choices=CAC_CACH + ["tat_ca"], default="tat_ca")
    ap.add_argument("--nhom", help="tên thư mục nhóm, ví dụ 03_huong_dan_nau_mon_mien_tay")
    args = ap.parse_args()
    cac_cach = CAC_CACH if args.cach == "tat_ca" else [args.cach]

    bd = BoDem()
    thong_ke = Counter()
    caps = {}
    for folder, path in tim_dau_vao(args.nhom):
        rows, trong, _ = doc_csv(path)
        thong_ke["dong_trong"] += trong
        for r in rows:
            cap = CapHoiDap(r, folder, bd, thong_ke)
            caps[cap.id] = cap
        print(f"Đã đọc {folder}: {len(rows)} cặp hỏi–đáp")

    kq = {}
    duoi = f"_{args.nhom}" if args.nhom else ""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for cach in cac_cach:
        doan = [bg for cap in caps.values() for bg in tao_ban_ghi(cap, cach, CAT[cach](cap))]
        kq[cach] = doan
        with (OUT_DIR / f"doan_{cach}{duoi}.jsonl").open("w", encoding="utf-8", newline="\n") as f:
            for d in doan:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        if cach == "cau_truc" and not args.nhom:
            (OUT_DIR / "_toan_bo.json").write_text(json.dumps(doan, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8", newline="\n")
        print(f"Đã cắt {cach}: {len(doan)} đoạn")

    ten_bc = "kiem_tra_tach_doan" + ("" if args.cach == "tat_ca" else f"_{args.cach}") + duoi + ".md"
    th = viet_bao_cao(REPORTS / ten_bc, kq, caps, thong_ke, args.nhom)

    print()
    print(f"{'Cách':<10} {'Số đoạn':>8} {'Min':>5} {'TV':>6} {'Max':>5} {'Vượt':>5} {'Mất chữ':>8} {'Ngắn':>5} "
          f"{'Số':>4} {'Cắt ngang':>10}")
    for cach, t in th.items():
        print(f"{cach:<10} {t['so_doan']:>8} {t['min']:>5} {t['trung_vi']:>6g} {t['max']:>5} {t['vuot']:>5} "
              f"{t['mat_chu']:>8} {t['qua_ngan']:>5} {t['toan_so']:>4} {t['cat_ngang']:>10}")
    print(f"\nBáo cáo: {(REPORTS / ten_bc).relative_to(ROOT)}")
    vuot = [i for t in th.values() for i in t["vuot_ids"]]
    if vuot or any(t["mat_chu"] for t in th.values()):
        print("CHƯA XONG: còn đoạn vượt giới hạn hoặc lỗi mất chữ:", ", ".join(vuot))
        sys.exit(1)


if __name__ == "__main__":
    main()
