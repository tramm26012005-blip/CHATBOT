"""Giao diện web của chatbot nấu ăn (Streamlit).

Chatbot KHÔNG dùng mô hình sinh câu trả lời: tìm câu hỏi gần nhất trong dữ liệu rồi trả nguyên văn câu trả lời gốc.
Chạy: python -m streamlit run app.py   (hoặc bấm đúp chay_web.bat)
Mở trình duyệt: http://localhost:8501
"""
import json

import streamlit as st

from chatbot.cau_hinh import ROOT, doc_cau_hinh

st.set_page_config(page_title="Bếp Miền Tây – Trợ lý nấu ăn", page_icon="🍲", layout="centered")

CAU_GOI_Y = [
    "Cách nấu canh chua cá lóc miền Tây",
    "Cách làm bánh xèo miền Tây",
    "Lẩu mắm cần nguyên liệu gì",
    "Bữa sáng nên ăn gì để giảm cân",
    "Không có me thì nấu canh chua bằng gì",
    "Bị cảm cúm nên ăn gì cho mau khỏi",
]
TEN_CACH_CAT = {"cau_truc": "Theo cấu trúc", "co_dinh": "Cố định", "de_quy": "Đệ quy"}
TEN_CHE_DO = {"vector": "Vector (tìm theo nghĩa)", "lai": "Lai (vector + BM25)", "bm25": "BM25 (theo từ khóa)"}
GIOI_HAN = ("Trợ lý chỉ trả lời về nấu ăn và ăn uống, lấy nguyên văn từ bộ dữ liệu của đồ án · có thể chọn nhầm câu, "
            "hãy xem nguồn · không thay lời khuyên của bác sĩ hay chuyên gia dinh dưỡng · không dùng cho dị ứng nặng "
            "hay bệnh cần điều trị · không tra cứu thông tin mới trên mạng · đừng nhập thông tin cá nhân.")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 760px;}
div[data-testid="stChatMessage"] {border-radius: 14px;}
.stButton > button {border-radius: 999px; text-align: left;}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ tải tài nguyên một lần

@st.cache_resource(show_spinner="Đang tải kho dữ liệu (chỉ lần đầu)...")
def khoi_dong(thu_muc_kho, che_do_truy_hoi):
    """Nạp kho (và mô hình sinh vector nếu chế độ cần) vào bộ nhớ một lần cho mọi phiên."""
    from chatbot.truy_hoi import nap_bm25, nap_kho
    nap_kho(thu_muc_kho)
    if che_do_truy_hoi == "bm25":
        nap_bm25(thu_muc_kho)
    else:
        from chatbot.mo_hinh_vector import nap_mo_hinh
        nap_mo_hinh()
        if che_do_truy_hoi == "lai":
            nap_bm25(thu_muc_kho)


def kho_co_san():
    goc = ROOT / doc_cau_hinh()["thu_muc_kho"]
    return [c for c in TEN_CACH_CAT if (goc / f"{c}_tat_ca" / "index.faiss").exists()]


@st.cache_data(show_spinner=False)
def danh_sach_nhom(thu_muc_kho):
    nhom = {}
    for dong in (ROOT / thu_muc_kho / "sieu_du_lieu.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(dong)
        nhom[d["nhom_folder"]] = d["nhom"]
    return dict(sorted(nhom.items()))


def hoi(cau):
    """Nút gợi ý / câu hỏi liên quan: đặt câu chờ, lượt chạy kế tiếp sẽ trả lời."""
    st.session_state.cau_cho = cau


# ------------------------------------------------------------------ thanh bên

ch = doc_cau_hinh()
cac_kho = kho_co_san()
if not cac_kho:
    st.error("Chưa có kho dữ liệu. Hãy chạy `python scripts/tao_kho_vector.py --cach tat_ca --tap tat_ca` trước.")
    st.stop()

with st.sidebar:
    st.header("⚙️ Tùy chỉnh")
    mac_dinh_cach = ch["cach_cat"] if ch["cach_cat"] in cac_kho else cac_kho[0]
    cach_cat = st.selectbox("Kho dữ liệu (cách cắt đoạn)", cac_kho, index=cac_kho.index(mac_dinh_cach),
                            format_func=lambda c: TEN_CACH_CAT[c])
    thu_muc_kho = f"{ch['thu_muc_kho']}/{cach_cat}_tat_ca"
    che_do_truy_hoi = st.radio("Cách tìm", list(TEN_CHE_DO), index=list(TEN_CHE_DO).index(ch["che_do_truy_hoi"]),
                               format_func=TEN_CHE_DO.get,
                               help="Câu gõ không dấu luôn tự dùng chỉ mục phụ không dấu (BM25)")
    k = st.slider("Số kết quả truy hồi (k)", 1, 10, ch["k"])
    nhom = danh_sach_nhom(thu_muc_kho)
    loc_nhom = st.multiselect("Lọc theo nhóm (để trống = tất cả)", list(nhom), format_func=lambda x: nhom[x])
    giai_thich = st.toggle("Chế độ giải thích", value=False,
                           help="Hiện câu hỏi sau tiền xử lý / tách từ, câu hỏi viết lại, top-k và ngưỡng")
    if st.button("🗨️ Cuộc trò chuyện mới", width="stretch"):
        st.session_state.tin_nhan = []
        st.rerun()

try:
    khoi_dong(thu_muc_kho, che_do_truy_hoi)
except Exception as e:  # thiếu kho, không tải được mô hình sinh vector...
    st.error(f"Không khởi động được chatbot: {e}")
    st.stop()

st.session_state.setdefault("tin_nhan", [])


# ------------------------------------------------------------------ hiển thị

def hien_nguon(kq):
    for n in kq["nguon"]:
        with st.expander("📚 Nguồn tham khảo"):
            dong = f"**ID {n['id_goc']} – {n['cau_hoi']}**  \nNhóm: {n['nhom']} · độ khớp {n['diem']:.3f}"
            if n["nguon"]:
                dong += f"  \n[Mở bài viết gốc]({n['nguon']})"
            st.markdown(dong)


def hien_giai_thich(kq):
    g = kq["giai_thich"]
    with st.expander("🔍 Giải thích (cho vấn đáp)"):
        st.markdown(
            f"- Loại xử lý: `{kq['loai']}` · kho `{g['kho']}` · cách tìm `{g['che_do_truy_hoi']}` · {g['thoi_gian_giay']} giây\n"
            f"- Điểm cao nhất **{g['diem_cao_nhat']:.3f}** · ngưỡng ngoài phạm vi {g['nguong_ngoai_pham_vi']} "
            f"· ngưỡng tin cậy {g['nguong_tin_cay']}\n"
            f"- Sau tiền xử lý: `{g['cau_hoi_sach']}`\n- Sau tách từ: `{g['cau_hoi_vao_mo_hinh']}`"
            + (f"\n- Câu hỏi viết lại (ghép chủ đề lượt trước): **{g['cau_hoi_viet_lai']}**" if g["cau_hoi_viet_lai"] else ""))
        st.dataframe([{"#": d["xep_hang"], "điểm": d["diem"], **({"RRF": d["diem_rrf"]} if "diem_rrf" in d else {}),
                       "ID": d["id_goc"], "nhóm": d["nhom_folder"], "câu hỏi gốc": d["cau_hoi"],
                       "tên mục": d["ten_muc"]} for d in kq["doan_truy_hoi"]],
                     hide_index=True, width="stretch")


def hien_tra_loi(kq, vi_tri, cuoi):
    st.markdown(kq["cau_tra_loi"])
    hien_nguon(kq)
    if giai_thich:
        hien_giai_thich(kq)
    # nút câu hỏi gợi ý chỉ bấm được ở câu trả lời mới nhất
    if kq["goi_y"] and cuoi:
        st.caption("Câu hỏi liên quan:" if kq["loai"] == "tra_loi" else "Bấm để chọn:")
        for j, cau in enumerate(kq["goi_y"]):
            st.button(cau, key=f"lq_{vi_tri}_{j}", on_click=hoi, args=(cau,))


st.title("🍲 Bếp Miền Tây")
st.caption("Trợ lý hướng dẫn nấu ăn và gợi ý món theo nhu cầu dinh dưỡng, ưu tiên món miền Tây")

so_tin = len(st.session_state.tin_nhan)
for vi_tri, tn in enumerate(st.session_state.tin_nhan):
    with st.chat_message(tn["vai"], avatar="🧑‍🍳" if tn["vai"] == "assistant" else None):
        if tn["vai"] == "assistant":
            hien_tra_loi(tn["ket_qua"], vi_tri, cuoi=vi_tri == so_tin - 1)
        else:
            st.markdown(tn["noi_dung"])

if not st.session_state.tin_nhan:
    st.markdown("#### Bạn muốn nấu gì hôm nay?")
    cot = st.columns(2)
    for i, cau in enumerate(CAU_GOI_Y):
        cot[i % 2].button(cau, key=f"goi_y_{i}", on_click=hoi, args=(cau,), width="stretch")

cau_hoi = st.chat_input("Hỏi mình về món ăn, nguyên liệu, dinh dưỡng...") or st.session_state.pop("cau_cho", None)
st.caption(f"ℹ️ {GIOI_HAN}")

if cau_hoi:
    from chatbot.sinh_cau_tra_loi import tra_loi

    lich_su = [{"cau_hoi": tn["cau_hoi"], "cau_tra_loi": tn["ket_qua"]["cau_tra_loi"], "chu_de": tn["ket_qua"]["chu_de"]}
               for tn in st.session_state.tin_nhan if tn["vai"] == "assistant"]
    with st.spinner("Mình đang lục lại sổ tay nấu ăn..."):
        kq = tra_loi(cau_hoi, lich_su, {"k": k, "che_do_truy_hoi": che_do_truy_hoi,
                                        "loc_nhom": loc_nhom or None, "kho": thu_muc_kho})
    st.session_state.tin_nhan += [{"vai": "user", "noi_dung": cau_hoi},
                                  {"vai": "assistant", "cau_hoi": cau_hoi, "ket_qua": kq}]
    st.rerun()  # vẽ lại từ lịch sử (ẩn câu gợi ý màn hình đầu, hiện nút câu hỏi liên quan)
