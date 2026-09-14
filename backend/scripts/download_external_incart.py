#!/usr/bin/env python3
"""Tải vài bản ghi mẫu từ St Petersburg INCART 12-lead Arrhythmia Database (PhysioNet).

Mục đích: có 1 bộ dữ liệu HOÀN TOÀN độc lập với MIT-BIH (khác bệnh viện Nga, khác máy đo,
khác fs=257Hz, 12 đạo trình) để kiểm chứng generalization thật của model đã train/val/test
chỉ trên MIT-BIH — xem backend/scripts/validate_external_incart.py.

Ví dụ:
    python backend/scripts/download_external_incart.py
    python backend/scripts/download_external_incart.py --records I01 I15 I30
"""
from __future__ import annotations

import argparse
from pathlib import Path

import wfdb

DEFAULT_RECORDS = ["I01", "I15", "I30", "I45", "I60"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tải vài bản ghi INCART từ PhysioNet để kiểm chứng generalization ngoài MIT-BIH."
    )
    parser.add_argument("--records", nargs="+", default=DEFAULT_RECORDS,
                         help="Danh sách record ID cần tải, ví dụ: --records I01 I15 I30")
    parser.add_argument("--dl-dir", type=str, default=None,
                         help="Thư mục lưu dữ liệu, mặc định là <repo>/data/raw/incartdb")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    dl_dir = Path(args.dl_dir).resolve() if args.dl_dir else repo_root / "data" / "raw" / "incartdb"
    dl_dir.mkdir(parents=True, exist_ok=True)

    records = [str(r).strip() for r in args.records if str(r).strip()]
    if not records:
        raise ValueError("Cần ít nhất 1 record INCART để tải.")

    print(f"[INCART] Đang tải các record: {', '.join(records)}")
    print(f"[INCART] Đích lưu: {dl_dir}")

    try:
        wfdb.dl_database("incartdb", dl_dir=str(dl_dir), records=records)
    except Exception as exc:  # pragma: no cover - chỉ để in lỗi rõ hơn
        raise RuntimeError(f"Không thể tải dữ liệu INCART: {exc}") from exc

    print("[INCART] Tải xong.")


if __name__ == "__main__":
    main()
