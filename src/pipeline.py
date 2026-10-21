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
from datetime import datetime,timezone
from src.config import SETTINGS,API_RESOURCES
from src.api_client import fetch_all_pages
from src.logger import get_logger
from src.extract_files import read_dataset, profile
from src.validators import score_rows, validate_schema, split_valid_invalid, split_cross_table_invalid
from src.transform import normalize
from src.database import ping, engine
from src.load_postgres import upsert_dataframe
from src.quality_report import build_report
from src.refresh_mart import refresh as refresh_mart

log = get_logger('pipeline')

DATASETS = ['customers', 'products', 'orders', 'order_items', 'payments']
FILES = {
    'customers': 'customers_daily.csv',
    'products': 'products_daily.csv',
    'orders': 'orders_daily.csv',
    'order_items': 'order_items_daily.csv',
    'payments': 'payments_daily.json',
}
API_RESOURCES = {
    'customers': 'customers',
    'products': 'products',
    'orders': 'orders',
    'order_items': 'order-items',
    'payments': 'payments',
}
PK = {
    'customers': 'customer_id',
    'products': 'product_id',
    'orders': 'order_id',
    'order_items': 'order_item_id',
    'payments': 'payment_id',
}

def _read_state():
    """Đọc trạng thái pipeline từ metadata/pipeline_state.json."""
    path = SETTINGS.metadata_dir / 'pipeline_state.json'
    if not path.exists():
        return {
            'last_run_id': None,
            'last_successful_at': None,
            'last_source': None,
            'status': None,
            'api_watermarks': {},
            'processed_file_batches': [],
        }
    try:
        state = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        state = {}
    state.setdefault('last_run_id', None)
    state.setdefault('last_successful_at', None)
    state.setdefault('last_source', None)
    state.setdefault('status', None)
    state.setdefault('api_watermarks', {})
    state.setdefault('processed_file_batches', [])
    return state

def _write_state(state):
    """Ghi đè trạng thái thành công mới vào metadata/pipeline_state.json."""
    SETTINGS.metadata_dir.mkdir(parents=True, exist_ok=True)
    (SETTINGS.metadata_dir / 'pipeline_state.json').write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8'
    )

def _file_frames(input_dir):
    """Đọc dữ liệu từ file cục bộ (CSV/JSON)."""
    frames = {}
    for name in DATASETS:
        path = input_dir / FILES[name]
        if not path.exists():
            raise FileNotFoundError(f'Missing input for {name}: {path}')
        frames[name] = read_dataset(path)
    return frames

def _api_frames(run_id, state, datasets=None):
    """Thu thập dữ liệu phân trang từ REST API và lưu snapshot thô RAW."""
    raw_dir = SETTINGS.raw_dir / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    frames = {}
    watermarks = {}
    datasets = list(datasets or DATASETS)
    for name in datasets:
        cutoff = state.get('api_watermarks', {}).get(name)
        rows = fetch_all_pages(API_RESOURCES[name], updated_after=cutoff)
        # Lưu trữ dữ liệu thô nguyên bản (RAW Immutability)
        (raw_dir / f'{name}.json').write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        frames[name] = pd.DataFrame(rows)
        if rows:
            candidates = [r.get('updated_at') or r.get('created_at') for r in rows]
            candidates = [x for x in candidates if x]
            if candidates:
                watermarks[name] = max(candidates)
    return frames, watermarks

def _source_frames(source, input_dir, run_id, state):
    """Phân luồng trích xuất dữ liệu theo nguồn chỉ định."""
    if source == 'file':
        return _file_frames(input_dir), {}
    if source == 'api':
        return _api_frames(run_id, state)
    if source == 'both':
        file_frames = _file_frames(input_dir)
        api_frames, watermarks = _api_frames(
            run_id, state, datasets=['orders', 'order_items', 'payments']
        )
        # Master data nạp từ file hàng ngày, Transactional data nạp từ REST API
        frames = {
            'customers': file_frames['customers'],
            'products': file_frames['products'],
            'orders': api_frames['orders'],
            'order_items': api_frames['order_items'],
            'payments': api_frames['payments'],
        }
        return frames, watermarks
    raise ValueError(f'Unsupported source: {source}')

def _append_reject(*parts):
    """Gộp các DataFrame vi phạm từ nhiều tầng kiểm định."""
    parts = [p for p in parts if p is not None and not p.empty]
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True, sort=False)

def _split_duplicate_pk(name, df):
    """Kiểm tra và tách các bản ghi trùng khóa chính trong batch."""
    pk = PK[name]
    duplicate_mask = df.duplicated(pk, keep=False)
    rejected = df[duplicate_mask].copy()
    if not rejected.empty:
        rejected['error_code'] = 'DUPLICATE_ID'
    return df[~duplicate_mask].copy(), rejected

def _save_reject(run_id, name, reject):
    """Lưu trữ dữ liệu vi phạm vào thư mục data/rejected/."""
    out_dir = SETTINGS.reject_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'{name}_reject.csv'
    reject.to_csv(path, index=False)
    # Bản sao tiện lợi để đối soát nhanh trong lớp
    SETTINGS.reject_dir.mkdir(parents=True, exist_ok=True)
    reject.to_csv(SETTINGS.reject_dir / f'{name}_reject.csv', index=False)
    return path


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

def run(input_dir=Path('data/incremental/day_2026-07-01'), source='file', refresh=False, skip_processed_file=False):
    """Quy trình điều phối 8 bước tuần tự của pipeline."""
    input_dir = Path(input_dir)
    run_id = str(uuid.uuid4())
    log.info('[1/8] Khởi tạo phiên chạy (run_id=%s, source=%s)', run_id, source)
    state = _read_state()
    batch_key = str(input_dir.resolve()) if input_dir.exists() else str(input_dir)

    if source in {'file', 'both'} and skip_processed_file and batch_key in state['processed_file_batches']:
        log.info('Bỏ qua thư mục file đã từng xử lý: %s', batch_key)
        return []

    log.info('[2/8] Trích xuất dữ liệu từ nguồn: %s', source)
    raw_frames, pending_watermarks = _source_frames(source, input_dir, run_id, state)
    stats = []

    for name in DATASETS:
        raw_df = raw_frames.get(name, pd.DataFrame())
        if raw_df.empty:
            stats.append({
                'run_id': run_id,
                'dataset': name,
                'input': 0,
                'valid': 0,
                'rejected': 0,
                'inserted': 0,
                'updated': 0,
                'inserted_or_updated': 0,
            })
            continue

        log.info('[3/8] Chuẩn hóa & Kiểm tra Schema: %s (input=%d dòng)', name, len(raw_df))
        log.info('%s profile=%s', name, profile(raw_df))
        df = normalize(raw_df)
        validate_schema(name, df)

        log.info('[4/8] Kiểm tra Chất lượng & Tách dòng lỗi: %s', name)
        row_valid, row_reject = split_valid_invalid(name, df)
        dedup_valid, dup_reject = _split_duplicate_pk(name, row_valid)
        fk_valid, fk_reject = split_cross_table_invalid(name, dedup_valid)
        reject = _append_reject(row_reject, dup_reject, fk_reject)

        log.info('[5/8] Lưu Rejects & Nạp Core Database: %s (valid=%d, reject=%d)', name, len(fk_valid), len(reject))
        _save_reject(run_id, name, reject)
        result = upsert_dataframe(name, fk_valid)
        record = {
            'run_id': run_id,
            'dataset': name,
            'input': len(df),
            'valid': len(fk_valid),
            'rejected': len(reject),
            **result,
        }

        # [6/8] Đối soát nguyên tắc bất biến (Invariant Reconciliation)
        if record['input'] != record['valid'] + record['rejected']:
            raise AssertionError(f"Đối soát bất biến thất bại tại {name}: {record}")
        stats.append(record)
        log.info('%s input=%s valid=%s reject=%s inserted=%s updated=%s',
                 name, len(df), len(fk_valid), len(reject), result['inserted'], result['updated'])

    log.info('[6/8] Xuất báo cáo chất lượng dữ liệu (DQ Report)')
    build_report(stats, run_id=run_id, out_dir=SETTINGS.report_dir)

    if refresh:
        log.info('[7/8] Làm mới Sales Data Mart')
        refresh_mart()
        log.info('Làm mới Sales Data Mart thành công')
    else:
        log.info('[7/8] Làm mới Sales Data Mart: SKIPPED (không truyền cờ --refresh-mart)')

    log.info('[8/8] Cập nhật Checkpoint State')
    state['last_run_id'] = run_id
    state['last_successful_run_id'] = run_id
    state['last_successful_at'] = datetime.now(timezone.utc).isoformat()
    state['last_source'] = source
    state['status'] = 'success'
    if source in {'api', 'both'}:
        state['api_watermarks'].update(pending_watermarks)
    if source in {'file', 'both'} and batch_key not in state['processed_file_batches']:
        state['processed_file_batches'].append(batch_key)
    _write_state(state)

    log.info('Pipeline hoàn thành thành công trọn vẹn (run_id=%s)', run_id)
    return stats



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='E-commerce training daily pipeline')
    parser.add_argument('--input-dir', default='data/incremental/day_2026-07-01',
                        help='Thư mục dữ liệu file gia tăng')
    parser.add_argument('--source', choices=['file', 'api', 'both'], default='file',
                        help='Nguồn dữ liệu: file, api, hoặc both')
    parser.add_argument('--refresh-mart', action='store_true',
                        help='Làm mới Sales Data Mart sau khi nạp xong')
    parser.add_argument('--skip-processed-file', action='store_true',
                        help='Bỏ qua thư mục file nếu đã từng xử lý thành công')
    args = parser.parse_args()

    try:
        run(
            Path(args.input_dir),
            source=args.source,
            refresh=args.refresh_mart,
            skip_processed_file=args.skip_processed_file,
        )
        sys.exit(0)
    except Exception as exc:
        log.error('[ALERT] Sự cố nghiêm trọng khi chạy pipeline | error_type=%s | reason=%s',
                  type(exc).__name__, str(exc), exc_info=True)
        sys.exit(1)