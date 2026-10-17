"""Buổi 8 - orchestration skeleton.

Mục tiêu cuối:
Source(file/API) -> RAW -> normalize -> validate -> reject/valid -> upsert CORE
-> DQ report -> checkpoint/watermark -> optional refresh MART.
"""
import json
import uuid
import pandas as pd
import argparse
import sys
from pathlib import Path
from config import SETTINGS,API_RESOURCES
from api_client import fetch_all_pages
from logger import get_logger

log = get_logger('pipeline')

def ingest_api_raw(resource_name: str, run_id: str) -> Path:
    """
    Thu thập phân trang và lưu dữ liệu nguyên bản (RAW) trước khi transform.
    Tuân thủ nguyên tắc RAW Immutability.
    """
    api_endpoint = API_RESOURCES[resource_name]
    raw_dir = SETTINGS.raw_dir / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch tat ca cac trang du lieu tu API
    rows = fetch_all_pages(api_endpoint, page_size=100)

    # 2. Luu du lieu truc tiep vao file JSON tho
    raw_file = raw_dir / f"{resource_name}.json"
    raw_file.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    log.info("Saved RAW snapshot: %s (%d records)", raw_file, len(rows))
    return raw_file

def run(input_dir=Path('data/incremental/day_2026-07-01'), source='file', refresh=False, skip_processed_file= False):
    # TODO 1: tạo run_id và đọc checkpoint.
    # TODO 2: đọc file/API; API phải lưu RAW trước transform.
    # TODO 3: xử lý theo dependency order customers -> products -> orders -> order_items -> payments.
    # TODO 4: schema/business/cross-table validation + duplicate PK.
    # TODO 5: tách reject; upsert valid.
    # TODO 6: DQ report, watermark/checkpoint chỉ ghi sau successful run.
    # TODO 7: nếu refresh=True thì refresh Data Mart.
    """ Quy trinh dieu phoi 8 buoc tuan tu cua pipeline """
    input_dir = Path(input_dir)
    run_id = str(uuid.uuid4())
    log.info('[1/8] Khoi tao phien chay (run_id=%s, source=%s)',run_id,source)
    # state = _read_state()
    batch_key = str(input_dir.resolve() if input_dir.exists() else str(input_dir))
    # if source in {'file', 'api'}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='E-Commerce trainning daily pipeline')
    parser.add_argument('--input_dir', 
                        default= SETTINGS.incremental_dir, 
                        help='Thu muc gia tri gia tang')
    parser.add_argument('--source', 
                        choices=['file','api','both'], 
                        default='file',
                        help='Nguon du lieu: file, api hoac ca hai')
    parser.add_argument('--refresh-mart',
                        action='store_true',
                        help='lam moi du lieu Sales Data Mart sau khi nap xong')
    parser.add_argument('--skip-processed-file',
                        action='store_true',
                        help='Bo qua thu muc file neu tung xu ly thanh cong')
    args = parser.parse_args()

    try:
        run(
            Path(args.input_dir),
            source=args.source,
            refresh=args.refesh_mart,
            skip_processed_file=args.skip_process_file
        )
        sys.exit(0)
    except Exception as exc:
        log.error('[ALERT] Su co nghiem trong khi chay pipeline | error_type=%s | reason=%s',
                  type(exc).__name__, str(exc),exc_info=True)
        sys.exit(1)