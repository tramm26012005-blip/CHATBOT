"""Gộp lại tất cả data/groups/*/all.csv thành data/merged/dataset.csv (sắp theo ID).

Dùng sau khi sửa riêng một nhóm để build lại dataset tổng:
    python scripts/merge_groups.py
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUPS_DIR = ROOT / "data" / "groups"
OUTPUT = ROOT / "data" / "merged" / "dataset.csv"
MANIFEST = ROOT / "data" / "manifest.json"
HEADER = ["ID", "Nhóm", "Tập", "Câu hỏi", "Câu trả lời", "Nguồn"]


def read_group(path):
    """Đọc một file all.csv của nhóm, kiểm tra header, bỏ dòng trống."""
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if reader.fieldnames != HEADER:
            sys.exit(f"Header sai trong {path}: {reader.fieldnames}")
        return [r for r in reader if any((v or "").strip() for v in r.values())]


def id_key(row):
    """Khoá sắp xếp theo ID số; ID không phải số xếp cuối."""
    return (0, int(row["ID"]), "") if row["ID"].isdigit() else (1, 0, row["ID"])


def main():
    """Gộp các nhóm, báo lỗi nếu ID trùng, ghi file và so với manifest."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    files = sorted(GROUPS_DIR.glob("*/all.csv"))
    if not files:
        sys.exit(f"Không tìm thấy file all.csv nào trong {GROUPS_DIR}")

    rows, origin = [], {}
    for path in files:
        group_rows = read_group(path)
        for r in group_rows:
            origin.setdefault(r["ID"], []).append(path.parent.name)
        rows.extend(group_rows)
        print(f"{path.parent.name:32} {len(group_rows):>5} dòng")

    dups = {i: g for i, g in origin.items() if len(g) > 1}
    if dups:
        for i, g in sorted(dups.items()):
            print(f"ID trùng {i}: {', '.join(g)}")
        sys.exit(f"Dừng: có {len(dups)} ID trùng, chưa ghi file gộp.")

    rows.sort(key=id_key)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER, delimiter=";", lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)

    splits = Counter(r["Tập"] for r in rows)
    print(f"Đã ghi {OUTPUT.relative_to(ROOT)}: {len(rows)} dòng "
          f"(Train {splits.get('Train', 0)}, Test {splits.get('Test', 0)})")

    if MANIFEST.exists():
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["tong_so_dong_hop_le"]
        status = "KHỚP" if expected == len(rows) else "KHÁC (đã sửa nhóm sau khi tách?)"
        print(f"So với manifest ({expected} dòng): {status}")


if __name__ == "__main__":
    main()
