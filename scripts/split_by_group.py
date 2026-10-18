"""Tách, làm sạch và kiểm tra chất lượng dataset chatbot nấu ăn theo 12 nhóm.

Chạy từ thư mục gốc project:
    python scripts/split_by_group.py [đường_dẫn_csv]

Mặc định đọc `Dataset_1000.csv`; nếu không có thì dùng `câu hoi .csv`.
File gốc chỉ được đọc, không bao giờ bị sửa.
"""

import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
DEFAULT_INPUTS = ["Dataset_1000.csv", "câu hoi .csv"]

HEADER = ["ID", "Nhóm", "Tập", "Câu hỏi", "Câu trả lời", "Nguồn"]
SPLITS = ("Train", "Test")
NO_SOURCE = "Không áp dụng"

# (tên nhóm gốc, tên thư mục) — thứ tự quyết định số thứ tự thư mục
GROUPS = [
    ("Chào hỏi, cảm ơn, tạm biệt", "01_chao_hoi"),
    ("Hướng dẫn nấu ăn", "02_huong_dan_nau_an"),
    ("Hướng dẫn nấu món ăn miền Tây", "03_huong_dan_nau_mon_mien_tay"),
    ("Món ăn miền Tây", "04_mon_an_mien_tay"),
    ("Nguyên liệu và gia vị", "05_nguyen_lieu_gia_vi"),
    ("Thay thế nguyên liệu", "06_thay_the_nguyen_lieu"),
    ("Phân tích và điều chỉnh công thức", "07_dieu_chinh_cong_thuc"),
    ("Dinh dưỡng trong ăn uống", "08_dinh_duong"),
    ("Gợi ý món ăn theo nhu cầu dinh dưỡng", "09_goi_y_mon_theo_dinh_duong"),
    ("Bảo quản và chế biến thực phẩm", "10_bao_quan_che_bien"),
    ("An toàn thực phẩm", "11_an_toan_thuc_pham"),
    ("Gợi ý ăn uống khi cảm, ho, sốt, mệt mỏi hoặc trong thời kỳ kinh nguyệt", "12_goi_y_khi_om_met"),
]
FOLDER_OF = dict(GROUPS)
HEALTH_GROUP = GROUPS[11][0]

TEST_RATIO_MIN, TEST_RATIO_MAX = 15.0, 25.0
ANSWER_MIN, ANSWER_MAX = 30, 1500

# Dấu hiệu có lời khuyên đi khám / hỏi bác sĩ trong câu trả lời nhóm 12
DOCTOR_PATTERN = re.compile(r"bác sĩ|bác sỹ|đi khám|khám bệnh|cơ sở y tế|bệnh viện|nhân viên y tế|dược sĩ|chuyên gia y tế", re.IGNORECASE)

URL_PATTERN = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
# Chữ thường + (khoảng trắng thừa) + "." dính liền chữ IN HOA → lỗi thiếu khoảng trắng.
# Không khớp số thập phân (2.5), viết tắt kiểu TP.HCM / v.v vì cần chữ thường trước, chữ hoa sau.
MISSING_SPACE_PATTERN = re.compile(r"(?<=[^\W\d_])[ \t]*\.(?=[^\W\d_])")


def find_input():
    """Chọn file CSV đầu vào: tham số dòng lệnh hoặc tên mặc định."""
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        return path if path.is_absolute() else ROOT / path
    for name in DEFAULT_INPUTS:
        if (ROOT / name).exists():
            return ROOT / name
    sys.exit(f"Không tìm thấy file đầu vào ({', '.join(DEFAULT_INPUTS)}) trong {ROOT}")


def detect_newline(raw_bytes):
    """Giữ kiểu xuống dòng giống file gốc khi ghi CSV con."""
    return "\r\n" if b"\r\n" in raw_bytes else "\n"


def fix_missing_space(text):
    """Thêm khoảng trắng sau dấu chấm bị dính chữ (bạn.Mình → bạn. Mình), bỏ qua URL."""
    def fix_chunk(chunk):
        return MISSING_SPACE_PATTERN.sub(
            lambda m: ". " if _is_sentence_break(chunk, m) else m.group(0), chunk
        )

    out, last = [], 0
    for m in URL_PATTERN.finditer(text):
        out.append(fix_chunk(text[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(fix_chunk(text[last:]))
    return "".join(out)


def _is_sentence_break(chunk, m):
    """Chỉ coi là hết câu khi trước dấu chấm là chữ thường và sau là chữ in hoa."""
    before = chunk[:m.start()].rstrip()[-1:]
    after = chunk[m.end():m.end() + 1]
    return before.islower() and after.isupper()


def load_rows(path):
    """Đọc CSV gốc, bỏ dòng trống, strip ô và sửa lỗi khoảng trắng sau dấu chấm."""
    rows, blank, fixes = [], 0, []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        header = [h.strip() for h in next(reader)]
        if header != HEADER:
            sys.exit(f"Header không khớp: {header}")
        for raw in reader:
            cells = [c.strip() for c in raw]
            if not any(cells):
                blank += 1
                continue
            cells = (cells + [""] * len(HEADER))[:len(HEADER)]
            row = dict(zip(HEADER, cells))
            fixed = fix_missing_space(row["Câu trả lời"])
            if fixed != row["Câu trả lời"]:
                fixes.append(row["ID"])
                row["Câu trả lời"] = fixed
            rows.append(row)
    return rows, blank, fixes


def id_key(row):
    """Khoá sắp xếp theo ID số; ID không phải số xếp cuối."""
    try:
        return (0, int(row["ID"]), "")
    except ValueError:
        return (1, 0, row["ID"])


def write_csv(path, rows, newline):
    """Ghi CSV đúng định dạng gốc: utf-8-sig, dấu ';', cùng header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER, delimiter=";", lineterminator=newline)
        writer.writeheader()
        writer.writerows(rows)


def normalize_question(text):
    """Chuẩn hoá câu hỏi để so trùng: chữ thường, bỏ dấu câu, gộp khoảng trắng."""
    text = unicodedata.normalize("NFC", text).lower()
    text = "".join(" " if unicodedata.category(ch).startswith(("P", "S")) else ch for ch in text)
    return re.sub(r"\s+", " ", text).strip()


def write_outputs(rows, by_group, newline):
    """Ghi file theo nhóm (all/train/test) và các file gộp trong data/merged."""
    for name, folder in GROUPS:
        group_rows = by_group.get(name, [])
        base = DATA / "groups" / folder
        write_csv(base / "all.csv", group_rows, newline)
        for split in SPLITS:
            write_csv(base / f"{split.lower()}.csv", [r for r in group_rows if r["Tập"] == split], newline)

    ordered = sorted(rows, key=id_key)
    merged = DATA / "merged"
    for split in SPLITS:
        write_csv(merged / f"{split.lower()}.csv", [r for r in ordered if r["Tập"] == split], newline)
    with (merged / "dataset.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in ordered:
            f.write(json.dumps({
                "id": r["ID"],
                "group": r["Nhóm"],
                "group_folder": FOLDER_OF.get(r["Nhóm"], ""),
                "split": r["Tập"],
                "question": r["Câu hỏi"],
                "answer": r["Câu trả lời"],
                "source": r["Nguồn"],
            }, ensure_ascii=False) + "\n")


def check_quality(rows, by_group):
    """Chạy toàn bộ kiểm tra chất lượng, trả về dict kết quả theo nhóm và toàn cục."""
    issues = defaultdict(lambda: defaultdict(list))  # issues[nhóm][loại] = [mô tả]

    # Nhóm / Tập không hợp lệ
    unknown_groups = [r["ID"] for r in rows if r["Nhóm"] not in FOLDER_OF]
    for r in rows:
        if r["Tập"] not in SPLITS:
            issues[r["Nhóm"]]["Tập không hợp lệ"].append(f'ID {r["ID"]}: "{r["Tập"]}"')

    # Thiếu dữ liệu
    for r in rows:
        missing = [col for col in ("Câu hỏi", "Câu trả lời", "Nguồn") if not r[col]]
        if missing:
            issues[r["Nhóm"]]["Thiếu dữ liệu"].append(f'ID {r["ID"]}: thiếu {", ".join(missing)}')

    # Độ dài câu trả lời
    for r in rows:
        n = len(r["Câu trả lời"])
        if r["Câu trả lời"] and n < ANSWER_MIN:
            issues[r["Nhóm"]]["Trả lời quá ngắn"].append(f'ID {r["ID"]} ({n} ký tự): {r["Câu trả lời"]}')
        elif n > ANSWER_MAX:
            issues[r["Nhóm"]]["Trả lời quá dài"].append(f'ID {r["ID"]} ({n} ký tự): {r["Câu hỏi"]}')

    # Câu hỏi trùng lặp (trong nhóm / giữa nhóm) và rò rỉ Train–Test
    by_norm = defaultdict(list)
    for r in rows:
        if r["Câu hỏi"]:
            by_norm[normalize_question(r["Câu hỏi"])].append(r)
    for norm, dup in by_norm.items():
        if len(dup) < 2:
            continue
        ids = ", ".join(f'{d["ID"]}({d["Tập"]})' for d in dup)
        groups_in = sorted({d["Nhóm"] for d in dup}, key=lambda g: FOLDER_OF.get(g, g))
        for g in groups_in:
            in_group = [d for d in dup if d["Nhóm"] == g]
            if len(in_group) > 1:
                issues[g]["Trùng trong nhóm"].append(
                    f'"{in_group[0]["Câu hỏi"]}" — ID ' + ", ".join(d["ID"] for d in in_group))
            if len(groups_in) > 1:
                others = [FOLDER_OF.get(x, x) for x in groups_in if x != g]
                issues[g]["Trùng giữa các nhóm"].append(
                    f'"{in_group[0]["Câu hỏi"]}" — ID {ids} (cùng với {", ".join(others)})')
        if {d["Tập"] for d in dup} >= set(SPLITS):
            for g in groups_in:
                issues[g]["Rò rỉ Train/Test"].append(f'"{dup[0]["Câu hỏi"]}" — ID {ids}')

    # ID trùng / không phải số / nhảy số (toàn cục)
    id_counts = Counter(r["ID"] for r in rows)
    dup_ids = sorted((i for i, c in id_counts.items() if c > 1), key=lambda x: (len(x), x))
    numeric_ids = sorted({int(i) for i in id_counts if i.isdigit()})
    bad_ids = sorted(i for i in id_counts if not i.isdigit())
    gaps = []
    for a, b in zip(numeric_ids, numeric_ids[1:]):
        if b - a > 1:
            gaps.append(f"{a + 1}" if b - a == 2 else f"{a + 1}–{b - 1}")
    for i in dup_ids:
        for r in rows:
            if r["ID"] == i:
                issues[r["Nhóm"]]["ID trùng"].append(f"ID {i}")

    # Nhóm 12: thiếu lời khuyên đi khám
    no_doctor = [r for r in by_group.get(HEALTH_GROUP, []) if not DOCTOR_PATTERN.search(r["Câu trả lời"])]

    # Top 5 nguồn URL mỗi nhóm
    top_sources = {}
    for name, _ in GROUPS:
        urls = Counter(r["Nguồn"] for r in by_group.get(name, []) if r["Nguồn"].lower().startswith(("http", "www")))
        top_sources[name] = urls.most_common(5)

    return {
        "issues": issues,
        "unknown_groups": unknown_groups,
        "dup_ids": dup_ids,
        "bad_ids": bad_ids,
        "gaps": gaps,
        "id_range": (numeric_ids[0], numeric_ids[-1]) if numeric_ids else (None, None),
        "no_doctor": no_doctor,
        "top_sources": top_sources,
    }


def group_stats(by_group):
    """Tính số câu, train, test, % test, id_min, id_max cho mỗi nhóm."""
    stats = []
    for name, folder in GROUPS:
        g = by_group.get(name, [])
        train = sum(r["Tập"] == "Train" for r in g)
        test = sum(r["Tập"] == "Test" for r in g)
        ids = [int(r["ID"]) for r in g if r["ID"].isdigit()]
        stats.append({
            "folder": folder,
            "ten_nhom": name,
            "so_cau": len(g),
            "train": train,
            "test": test,
            "ti_le_test": round(100 * test / len(g), 1) if g else 0.0,
            "id_min": min(ids) if ids else None,
            "id_max": max(ids) if ids else None,
        })
    return stats


def build_report(src, rows, blank, fixes, stats, q):
    """Tạo nội dung báo cáo Markdown và bảng tóm tắt."""
    issues = q["issues"]
    L = [
        "# Báo cáo chất lượng dataset",
        "",
        f"- File nguồn: `{src.name}`",
        f"- Dòng hợp lệ: **{len(rows)}** — dòng trống đã bỏ: **{blank}**",
        f"- Câu trả lời đã sửa thiếu khoảng trắng sau dấu chấm: **{len(fixes)}**"
        + (f" (ID: {', '.join(fixes)})" if fixes else ""),
        f"- Khoảng ID: {q['id_range'][0]}–{q['id_range'][1]}",
        f"- ID trùng: {', '.join(q['dup_ids']) or 'không có'}",
        f"- ID nhảy số (bị thiếu): {', '.join(q['gaps']) or 'không có'}",
        f"- ID không phải số: {', '.join(q['bad_ids']) or 'không có'}",
        f"- Dòng có tên nhóm lạ: {', '.join(q['unknown_groups']) or 'không có'}",
        "",
        "## Tổng quan theo nhóm",
        "",
        "| Nhóm | Số câu | Train | Test | % Test | Số lỗi | Cảnh báo |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for s in stats:
        n_err = sum(len(v) for v in issues[s["ten_nhom"]].values())
        s["so_loi"] = n_err
        warn = "" if TEST_RATIO_MIN <= s["ti_le_test"] <= TEST_RATIO_MAX else f"⚠ Test ngoài {TEST_RATIO_MIN:g}–{TEST_RATIO_MAX:g}%"
        L.append(f'| {s["folder"]} | {s["so_cau"]} | {s["train"]} | {s["test"]} | {s["ti_le_test"]} | {n_err} | {warn} |')
    tot_train = sum(s["train"] for s in stats)
    tot_test = sum(s["test"] for s in stats)
    L.append(f"| **Tổng** | **{len(rows)}** | **{tot_train}** | **{tot_test}** | "
             f"**{round(100 * tot_test / len(rows), 1) if rows else 0}** | "
             f"**{sum(s['so_loi'] for s in stats)}** | |")
    L += ["", "> Số lỗi = trùng trong nhóm + trùng giữa nhóm + rò rỉ Train/Test + thiếu dữ liệu + "
          "trả lời quá ngắn/dài + ID trùng + Tập không hợp lệ. Danh sách nhóm 12 thiếu lời khuyên đi khám tính riêng.", ""]

    L += ["## Chi tiết theo nhóm", ""]
    for s in stats:
        L.append(f'### {s["folder"]} — {s["ten_nhom"]}')
        L.append("")
        g_issues = issues[s["ten_nhom"]]
        if not any(g_issues.values()):
            L.append("Không phát hiện lỗi.")
        for kind, items in g_issues.items():
            if items:
                L.append(f"**{kind}** ({len(items)})")
                L.extend(f"- {it}" for it in items)
                L.append("")
        tops = q["top_sources"][s["ten_nhom"]]
        L.append("")
        L.append("**Top 5 nguồn URL:**" if tops else "**Top 5 nguồn URL:** không có URL")
        L.extend(f"- {c} lần — {u}" for u, c in tops)
        L.append("")

    L += [f"## Nhóm 12: câu trả lời chưa có lời khuyên đi khám / hỏi bác sĩ ({len(q['no_doctor'])})", "",
          "_Chỉ liệt kê để xem tay, script không sửa._", ""]
    L.extend(f'- ID {r["ID"]} ({r["Tập"]}): {r["Câu hỏi"]}' for r in q["no_doctor"])
    L.append("")
    return "\n".join(L)


def print_summary(stats, q, fixes, blank, total):
    """In bảng tóm tắt ra màn hình."""
    print(f"Dòng hợp lệ: {total} | Dòng trống bỏ qua: {blank} | Sửa dấu chấm: {len(fixes)} câu")
    print(f"{'Nhóm':32} {'Số câu':>6} {'Train':>6} {'Test':>5} {'%Test':>6} {'Lỗi':>4}")
    for s in stats:
        flag = "" if TEST_RATIO_MIN <= s["ti_le_test"] <= TEST_RATIO_MAX else "  ⚠"
        print(f'{s["folder"]:32} {s["so_cau"]:>6} {s["train"]:>6} {s["test"]:>5} {s["ti_le_test"]:>6} {s["so_loi"]:>4}{flag}')
    print(f"ID trùng: {len(q['dup_ids'])} | ID nhảy số: {', '.join(q['gaps']) or 'không'} | "
          f"Nhóm 12 thiếu lời khuyên đi khám: {len(q['no_doctor'])}")
    print("Chi tiết: reports/quality_report.md")


def main():
    """Chạy toàn bộ quy trình: copy raw, làm sạch, tách nhóm, kiểm tra, ghi manifest."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    src = find_input()
    raw_bytes = src.read_bytes()
    newline = detect_newline(raw_bytes)

    raw_dst = DATA / "raw" / "Dataset_1000.csv"
    raw_dst.parent.mkdir(parents=True, exist_ok=True)
    raw_dst.write_bytes(raw_bytes)

    rows, blank, fixes = load_rows(src)
    by_group = defaultdict(list)
    for r in rows:
        by_group[r["Nhóm"]].append(r)

    write_outputs(rows, by_group, newline)
    stats = group_stats(by_group)
    q = check_quality(rows, by_group)

    REPORTS.mkdir(parents=True, exist_ok=True)
    report = build_report(src, rows, blank, fixes, stats, q)
    (REPORTS / "quality_report.md").write_text(report, encoding="utf-8")

    manifest = {
        "ngay_tao": date.today().isoformat(),
        "file_nguon": src.name,
        "tong_so_dong_hop_le": len(rows),
        "so_dong_trong_da_bo": blank,
        "so_cau_tra_loi_da_sua_dau_cham": len(fixes),
        "nhom": [{k: s[k] for k in ("folder", "ten_nhom", "so_cau", "train", "test", "id_min", "id_max")} for s in stats],
    }
    (DATA / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print_summary(stats, q, fixes, blank, len(rows))


if __name__ == "__main__":
    main()
