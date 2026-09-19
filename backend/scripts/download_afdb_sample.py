#!/usr/bin/env python3
"""Tải một số bản ghi mẫu từ MIT-BIH AFDB (Atrial Fibrillation Database).

Mục đích:
- lấy dữ liệu đánh giá/hiệu chỉnh ngưỡng cho screening rung nhĩ (AFib)
- không cần train lại toàn bộ model
- phù hợp để kiểm tra chất lượng phát hiện R-peak, tính irregularity, và
  calibrate các ngưỡng AFib bằng các bản ghi thực tế.

Ví dụ:
    python backend/scripts/download_afdb_sample.py
    python backend/scripts/download_afdb_sample.py --records 04015 04043 04936
    python backend/scripts/download_afdb_sample.py --records 04015 --dl-dir data/raw
"""

from __future__ import annotations

import argparse
from pathlib import Path

import wfdb

DEFAULT_RECORDS = [
    "04015",
    "04043",
    "04936",
    "05121",
    "07859",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tải vài bản ghi AFDB từ PhysioNet để kiểm tra/hiệu chỉnh AFib screening."
    )
    parser.add_argument(
        "--records",
        nargs="+",
        default=DEFAULT_RECORDS,
        help="Danh sách record ID cần tải, ví dụ: --records 04015 04043 04936",
    )
    parser.add_argument(
        "--dl-dir",
        type=str,
        default=None,
        help="Thư mục lưu dữ liệu, mặc định là <repo>/data/raw/afdb",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    # BUG ĐÃ SỬA: `wfdb.dl_database(db_dir, dl_dir, ...)` ghi file THẲNG vào `dl_dir`,
    # KHÔNG tự tạo thư mục con tên `db_dir` như code cũ giả định — bản trước truyền
    # `dl_dir=data/raw` nên mọi file .hea/.dat/.atr rơi thẳng vào data/raw/, lẫn với
    # các bộ dữ liệu khác (kaggle_csv/, physionet_mitdb/, svdb/...), và script hiệu
    # chỉnh (`calibrate_afib_thresholds.py`, mặc định tìm ở data/raw/afdb/) không bao
    # giờ thấy được. Giờ mặc định đích tải thẳng là data/raw/afdb đúng như nơi script
    # hiệu chỉnh tìm.
    dl_dir = Path(args.dl_dir).resolve() if args.dl_dir else repo_root / "data" / "raw" / "afdb"
    dl_dir.mkdir(parents=True, exist_ok=True)

    records = [str(r).strip() for r in args.records if str(r).strip()]
    if not records:
        raise ValueError("Cần ít nhất 1 record AFDB để tải.")

    print(f"[AFDB] Đang tải các record: {', '.join(records)}")
    print(f"[AFDB] Đích lưu: {dl_dir}")

    try:
        wfdb.dl_database("afdb", dl_dir=str(dl_dir), records=records)
    except Exception as exc:  # pragma: no cover - chỉ để in lỗi rõ hơn
        raise RuntimeError(f"Không thể tải dữ liệu AFDB: {exc}") from exc

    print("[AFDB] Tải xong.")
    children = sorted(p.name for p in dl_dir.iterdir())[:10]
    print(f"[AFDB] Ví dụ nội dung trong {dl_dir}: {children}")


if __name__ == "__main__":
    main()
