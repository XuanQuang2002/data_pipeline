"""Buổi 8 - orchestration skeleton.

Mục tiêu cuối:
Source(file/API) -> RAW -> normalize -> validate -> reject/valid -> upsert CORE
-> DQ report -> checkpoint/watermark -> optional refresh MART.
"""
import json
import uuid
import pandas as pd
from pathlib import Path
from config import SETTINGS
from api_client import fetch_all_pages
from logger import get_logger

log = get_logger('pipeline')

API_RESOURCES = {
    'customers' : 'customers',
    'products': 'products',
    'orders': 'orders',
    'order_items': 'order-items',  # Mapping tên resource chuẩn có dấu gạch ngang
    'payments': 'payments',
}

def run(input_dir=Path('data/incremental/day_2026-07-01'), source='file', refresh=False):
    # TODO 1: tạo run_id và đọc checkpoint.
    # TODO 2: đọc file/API; API phải lưu RAW trước transform.
    # TODO 3: xử lý theo dependency order customers -> products -> orders -> order_items -> payments.
    # TODO 4: schema/business/cross-table validation + duplicate PK.
    # TODO 5: tách reject; upsert valid.
    # TODO 6: DQ report, watermark/checkpoint chỉ ghi sau successful run.
    # TODO 7: nếu refresh=True thì refresh Data Mart.
    raise NotImplementedError('Implement end-to-end pipeline')

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
