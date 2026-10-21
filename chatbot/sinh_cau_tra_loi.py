"""Trả lời một lượt hỏi bằng truy hồi: lấy NGUYÊN VĂN câu trả lời gốc trong dữ liệu, không dùng mô hình sinh.

Luồng một lượt hỏi:
  1. Câu hỏi nối tiếp ("món đó nấu bao lâu") → ghép chủ đề của lượt trước (lượt đầu không viết lại).
  2. Truy hồi các đoạn liên quan.
  3. Định tuyến:
     - chào / cảm ơn / tạm biệt → câu trả lời mẫu trong nhóm Chào hỏi;
     - điểm cao nhất < nguong_ngoai_pham_vi → từ chối lịch sự (ngoài phạm vi);
     - điểm cao nhất < nguong_tin_cay → chưa chắc: gợi ý các câu hỏi gần nhất để người dùng chọn;
     - còn lại → trả nguyên văn câu trả lời gốc của câu hỏi khớp nhất, kèm nguồn và câu hỏi liên quan.
  4. Câu hỏi về sức khỏe → thêm lời nhắc tham khảo bác sĩ / chuyên gia dinh dưỡng.
  5. Ghi nhật ký logs/hoi_thoai.jsonl (mặc định không ghi nguyên văn câu hỏi).
"""
import hashlib
import json
import re
import time
from datetime import datetime

from chatbot.cau_hinh import ROOT, doc_cau_hinh
from chatbot.truy_hoi import nap_kho, truy_hoi

NHOM_CHAO_HOI = "01_chao_hoi"
# từ chỉ trỏ mạnh: chắc chắn đang nói về món ở lượt trước; từ yếu: chỉ ghép khi câu gốc tìm không chắc
TU_NOI_TIEP_MANH = re.compile(r"\b(món đó|món này|món kia|món trên|cái đó|cái này|nó|đó|này)\b", re.IGNORECASE)
TU_NOI_TIEP_YEU = re.compile(r"\b(vậy|thế|còn|luôn|nữa)\b", re.IGNORECASE)
TU_SUC_KHOE = re.compile(r"\b(tiểu đường|đái tháo đường|huyết áp|gout|gút|mang thai|có bầu|bà bầu|mẹ bầu|"
                         r"bệnh|ốm|sốt|ho|cảm cúm|kinh nguyệt|dạ dày|mỡ máu|cholesterol|thận|gan|tim mạch|"
                         r"dị ứng|ăn kiêng|giảm cân)\b", re.IGNORECASE)
# phân loại ý định xã giao bằng quy tắc (mô hình vector phân biệt kém các câu rất ngắn như "xin chào")
Y_DINH_XA_GIAO = [
    ("cảm ơn", re.compile(r"\b(cảm ơn|cám ơn|cam on|thank|thanks|tks)\b", re.IGNORECASE)),
    ("tạm biệt", re.compile(r"\b(tạm biệt|tam biet|bye|hẹn gặp lại|hen gap lai|gặp lại sau)\b", re.IGNORECASE)),
    # "chao" không dấu chỉ tính khi cả câu là lời chào, vì còn có thể là "cháo" (cach nau chao ga)
    ("chào", re.compile(r"\b(xin chào|chào|xin chao|hello|hi|alo)\b|^chao( ban| bot| nha| em| anh| chi| shop)?\W*$",
                        re.IGNORECASE)),
]

CAU_NGOAI_PHAM_VI = ("Xin lỗi bạn nha, câu này nằm ngoài phạm vi của mình rồi. Mình là trợ lý nấu ăn, "
                     "có thể giúp bạn:\n\n- Hướng dẫn nấu món ăn, nhất là món miền Tây\n"
                     "- Giải thích nguyên liệu, gia vị và cách thay thế\n"
                     "- Gợi ý món theo nhu cầu dinh dưỡng\n- Mẹo bảo quản và an toàn thực phẩm")
CAU_KHONG_CHAC = ("Mình chưa tìm được câu trả lời đủ chắc chắn cho câu này. "
                  "Có phải bạn muốn hỏi một trong các câu dưới đây không?")
CAU_KHONG_DAU = "Mẹo: bạn gõ có dấu thì mình tìm chính xác hơn nhiều nha. "
CAU_NHAC_SUC_KHOE = ("\n\n> Lưu ý: thông tin trên chỉ là gợi ý món ăn theo dữ liệu tham khảo. "
                     "Bạn nên hỏi bác sĩ hoặc chuyên gia dinh dưỡng cho tình trạng sức khỏe cụ thể của mình.")


# ------------------------------------------------------------------ tiện ích

def nhan_dien_xa_giao(cau_hoi):
    """Câu ngắn (≤ 8 từ) chỉ để chào / cảm ơn / tạm biệt → trả về từ khóa ý định, ngược lại None."""
    if len(cau_hoi.split()) > 8:
        return None
    return next((tu for tu, mau in Y_DINH_XA_GIAO if mau.search(cau_hoi)), None)


def tra_loi_xa_giao(y_dinh, kho):
    """Lấy câu trả lời mẫu trong nhóm Chào hỏi có câu hỏi gốc chứa đúng từ khóa ý định."""
    _, sieu, _ = nap_kho(kho)
    return next((d for d in sieu if d["nhom_folder"] == NHOM_CHAO_HOI and y_dinh in d["cau_hoi"].lower()), None)


def chu_de_truoc(lich_su):
    """Chủ đề gần nhất {cau_hoi, id_goc} (câu hỏi gốc khớp nhất của lượt trước), không có thì None."""
    return next((l["chu_de"] for l in reversed(lich_su) if l.get("chu_de")), None)


def noi_dung_day_du(kho, id_goc):
    """Toàn bộ câu trả lời gốc của một id_goc (nối mọi đoạn theo thu_tu_doan)."""
    _, sieu, _ = nap_kho(kho)
    cac_doan = sorted((d for d in sieu if d["id_goc"] == id_goc), key=lambda d: d["thu_tu_doan"])
    return "\n".join(d["noi_dung"] for d in cac_doan)


def dinh_dang(van_ban):
    """Câu trả lời gốc → Markdown: dòng tiêu đề mục (ngay trên danh sách gạch đầu dòng) in đậm,
    các đoạn văn tách bằng dòng trống để không bị dính vào danh sách."""
    dong = [d.rstrip() for d in van_ban.split("\n")]
    ra = []
    for i, d in enumerate(dong):
        if not d:
            continue
        la_muc = d.startswith("- ")
        sau = next((x for x in dong[i + 1:] if x), "")
        if not la_muc and sau.startswith("- ") and len(d) <= 90:
            ra.append(f"\n**{d}**\n")
        elif la_muc:
            ra.append(d)
        else:
            ra.append(f"\n{d}\n")
    return "\n".join(ra).strip()


def mo_ta_nguon(d):
    return {
        "id_goc": d["id_goc"], "cau_hoi": d["cau_hoi"], "ten_muc": d["ten_muc"], "nhom": d["nhom"],
        "diem": d["diem"], "nguon": d["nguon"] if str(d["nguon"]).startswith("http") else "",
    }


def cau_hoi_khac_nhau(cac_doan, bo_qua=(), toi_da=3):
    """Các câu hỏi gốc khác nhau (theo thứ tự xếp hạng) để gợi ý cho người dùng bấm hỏi tiếp."""
    da_co, kq = set(bo_qua), []
    for d in cac_doan:
        if d["id_goc"] not in da_co and d["nhom_folder"] != NHOM_CHAO_HOI:
            da_co.add(d["id_goc"])
            kq.append(d["cau_hoi"])
        if len(kq) == toi_da:
            break
    return kq


def ghi_nhat_ky(ban_ghi):
    """Ghi một dòng vào logs/hoi_thoai.jsonl. Mặc định không ghi nguyên văn câu hỏi (chỉ mã băm + độ dài)."""
    ch = doc_cau_hinh()
    if not ch.get("ghi_nhat_ky", True):
        return
    if not ch.get("ghi_nguyen_van_cau_hoi", False):
        for khoa in ("cau_hoi", "cau_hoi_viet_lai"):
            if ban_ghi.get(khoa):
                van_ban = ban_ghi.pop(khoa)
                ban_ghi[khoa + "_bam"] = hashlib.sha256(van_ban.encode("utf-8")).hexdigest()[:12]
                ban_ghi[khoa + "_do_dai"] = len(van_ban)
    thu_muc = ROOT / "logs"
    thu_muc.mkdir(exist_ok=True)
    with open(thu_muc / "hoi_thoai.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ hàm chính

def tra_loi(cau_hoi, lich_su=None, tuy_chon=None):
    """Trả lời một lượt hỏi.

    lich_su: các lượt trước [{cau_hoi, cau_tra_loi, chu_de}] (chỉ giữ so_luot_nho lượt gần nhất),
             chu_de là giá trị "chu_de" mà hàm này trả về ở lượt đó.
    tuy_chon: ghi đè cấu hình cho lượt này: k, che_do_truy_hoi ("vector" | "lai" | "bm25"), loc_nhom, kho.
    Trả về dict: cau_tra_loi (Markdown), loai, nguon, goi_y, doan_truy_hoi, chu_de, giai_thich.
    loai ∈ chao_hoi | ngoai_pham_vi | khong_chac | tra_loi.
    """
    t0 = time.perf_counter()
    ch = doc_cau_hinh()
    tc = tuy_chon or {}
    lich_su = (lich_su or [])[-ch["so_luot_nho"]:]
    tim = lambda q: truy_hoi(q, k=tc.get("k"), loc_nhom=tc.get("loc_nhom"),
                             che_do=tc.get("che_do_truy_hoi"), kho=tc.get("kho"))

    # 1–2. viết lại câu nối tiếp (lượt đầu không viết lại) rồi truy hồi
    tr, cau_viet_lai, theo_chu_de = tim(cau_hoi), None, False
    chu_de = chu_de_truoc(lich_su)
    if chu_de and len(cau_hoi.split()) <= 15 and not nhan_dien_xa_giao(cau_hoi):
        manh = TU_NOI_TIEP_MANH.search(cau_hoi)
        yeu = TU_NOI_TIEP_YEU.search(cau_hoi) and tr["diem_cao_nhat"] < tr["nguong_tin_cay"]
        if manh or yeu:
            cau_viet_lai = f"{chu_de['cau_hoi']}: {cau_hoi}"
            tr = tim(cau_viet_lai)
            # "món đó / món này" chỉ đúng món của lượt trước → món đó có trong top-k thì đưa lên đầu
            vi_tri = next((i for i, d in enumerate(tr["doan"]) if d["id_goc"] == chu_de["id_goc"]), None)
            if manh and vi_tri is not None:
                tr["doan"].insert(0, tr["doan"].pop(vi_tri))
                theo_chu_de = True
    cac_doan = tr["doan"]
    dau = cac_doan[0] if cac_doan else None

    # 3. định tuyến
    nguon, goi_y, chu_de_moi = [], [], None
    y_dinh = nhan_dien_xa_giao(cau_hoi)
    mau = tra_loi_xa_giao(y_dinh, tr["kho"]) if y_dinh else None
    if mau is None and dau and dau["nhom_folder"] == NHOM_CHAO_HOI and dau["diem"] >= ch["nguong_chao_hoi"]:
        mau = dau
    if mau is not None:
        loai, van_ban = "chao_hoi", mau["noi_dung"]
    elif tr["ngoai_pham_vi"] or not cac_doan:
        loai, van_ban = "ngoai_pham_vi", CAU_NGOAI_PHAM_VI
    elif dau["diem"] < tr["nguong_tin_cay"] and not theo_chu_de:
        # vẫn nhớ chủ đề đoán tốt nhất để câu nối tiếp ("món này nấu mấy người") còn hiểu được
        loai, van_ban, goi_y = "khong_chac", CAU_KHONG_CHAC, cau_hoi_khac_nhau(cac_doan)
        if tr["che_do_truy_hoi"] == "khong_dau":
            van_ban = CAU_KHONG_DAU + van_ban
        chu_de_moi = {"cau_hoi": dau["cau_hoi"], "id_goc": dau["id_goc"]}
    else:
        loai, chu_de_moi = "tra_loi", {"cau_hoi": dau["cau_hoi"], "id_goc": dau["id_goc"]}
        van_ban = dinh_dang(noi_dung_day_du(tr["kho"], dau["id_goc"]))
        nguon = [mo_ta_nguon(dau)]
        goi_y = [q for q in cau_hoi_khac_nhau(cac_doan, bo_qua={dau["id_goc"]})]

    # 4. lời nhắc sức khỏe
    if loai == "tra_loi" and (TU_SUC_KHOE.search(cau_viet_lai or cau_hoi) or dau["nhom_folder"].startswith("12_")):
        van_ban += CAU_NHAC_SUC_KHOE

    thoi_gian = round(time.perf_counter() - t0, 3)
    giai_thich = {"cau_hoi_sach": tr["cau_hoi_sach"], "cau_hoi_vao_mo_hinh": tr["cau_hoi_vao_mo_hinh"],
                  "cau_hoi_viet_lai": cau_viet_lai, "che_do_truy_hoi": tr["che_do_truy_hoi"], "kho": tr["kho"],
                  "diem_cao_nhat": tr["diem_cao_nhat"], "nguong_ngoai_pham_vi": tr["nguong"],
                  "nguong_tin_cay": tr["nguong_tin_cay"], "thoi_gian_giay": thoi_gian}

    # 5. nhật ký
    ghi_nhat_ky({
        "thoi_gian": datetime.now().isoformat(timespec="seconds"),
        "cau_hoi": cau_hoi, "cau_hoi_viet_lai": cau_viet_lai,
        "che_do_truy_hoi": tr["che_do_truy_hoi"], "kho": tr["kho"],
        "doan": [{"chunk_id": d["chunk_id"], "diem": d["diem"]} for d in cac_doan],
        "loai": loai, "nguon_id_goc": [n["id_goc"] for n in nguon], "thoi_gian_xu_ly_giay": thoi_gian,
    })
    return {"cau_tra_loi": van_ban, "loai": loai, "nguon": nguon, "goi_y": goi_y, "doan_truy_hoi": cac_doan,
            "chu_de": chu_de_moi, "giai_thich": giai_thich}
