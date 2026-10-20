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
from src.extract_files import read_dataset
from src.validators import score_rows, validate_schema, split_valid_invalid
from src.transform import normalize
from src.database import ping, engine
from src.load_postgres import upsert_dataframe
from src.quality_report import build_report

log = get_logger('pipeline')

DATASETS = {
        'customers': 'customers_daily.csv',
        'products': 'products_daily.csv',
        'orders': 'orders_daily.csv',
        'order_item': 'order_items_daily.csv',
        'payments': 'payments_daily.json'
    }

def load_state():
    p = SETTINGS.metadata_dir/'pipeline_state.json'
    return {} if not p.exists() else json.loads(p.read_text(encoding='utf-8'))

def save_state(state): 
    (SETTINGS.metadata_dir/'pipeline_state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

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

def _write_state(state):
    """ Ghi de trang thai thanh cong moi cao metadata/pipeline_state.json """
    SETTINGS.metadata_dir.mkdir(parents=True, exist_ok= True)
    (SETTINGS.metadata_dir / 'pipeline_state.json').write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8'
    )

# def _file_frames(input_dir):
#     """Doc du lieu tu file cuc bo"""
#     frames = {}
#     for name in DATASETS:
#         path = input_dir / FILES[name]
#         if not path.exists():
#             raise FileNotFoundError(f'Missing input for {name}: {path}')
#         frames[name] = read_dataset(path)
#     return frames

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
    batch_key = str(input_dir.resolve()) if input_dir.exists() else str(input_dir)
    old = load_state()
    state={
        'run_id':run_id,
        'started_at':datetime.now(timezone.utc).isoformat(),
        'finished_at':None,''
        'status':'STARTED',
        'last_successful_run_id':old.get('last_successful_run_id'),
        'last_updated_checkpoint':old.get('last_updated_checkpoint'),
        'stats':[]}
    save_state(state)
    log.info('[1/8] Khoi tao phien chay (run_id=%s, source=%s)',run_id,source)
    assert ping()==1
    prepared={}; 
    stats=[]
    # state = _read_state()
    # if source in {'file', 'both'} and skip_processed_file and batch_key in state['processed_file']:
    #     log.info('Skip folder has been processed before: %s',batch_key)
    #     return []
    try:
        if source == 'file':
            for file_name in DATASETS:
                df = read_dataset(input_dir / DATASETS[file_name])
                n = len(df)
                df_nomalize = normalize(df)
                validate_schema(file_name,df_nomalize)
                valid, reject = split_valid_invalid(file_name,df_nomalize)
                valid.to_csv(SETTINGS.staging_dir / f'{file_name}_{run_id}.csv',index = False)
                if not reject.empty:
                    reject.to_csv(SETTINGS.reject_dir / f'{file_name}_{run_id}.csv',index=False)
                scores = score_rows(file_name,df_nomalize)
                for pk, score, errors in scores[:10]:
                    err_str = f"[{', '.join(errors)}]"
                    print(f"row_id={pk} score={score:<3} errors={err_str}")
                s = {'dataset':file_name,'input':n,'valid':len(valid),'rejected':len(reject)}
                prepared[file_name] = valid
                stats.append(s)
                total_in = sum(s['input'] for s in stats)
                total_rej = sum(s['rejected'] for s in stats)
                rate = 0 if total_in == 0 else total_rej/total_in
                if rate > SETTINGS.reject_rate:
                    raise RuntimeError(f'QUARANTINE_BATCH: reject_rate={rate:.2%} > threshold={SETTINGS.reject_rate:.2%}')
                state['status'] = 'LOADING'
                save_state(s)
                results = {}
                with engine.begin() as conn:
                    for name in ['customers','products','orders','order_items','payments']:
                        results[name] = upsert_dataframe(name,prepared[name])
                for s in stats:
                    s.update(results.get(s['dataset'],{'inserted':0,'updated':0}))
                build_report(stats=stats, run_id=run_id)
                max_updated=None
                for df in prepared.values():
                    if 'updated_at' in df.columns and not df.empty:
                        x=df['updated_at'].max()
                        if pd.notna(x):
                            x=x.isoformat();
                            max_updated=x if max_updated is None else max(max_updated,x)
                state.update({'status':'SUCCESS','finished_at':datetime.now(timezone.utc).isoformat(),'last_successful_run_id':run_id,'last_updated_checkpoint':max_updated or old.get('last_updated_checkpoint'),'stats':stats})
                save_state(state)
                log.info('run_id=%s status=SUCCESS input=%s rejected=%s',run_id,total_in,total_rej)   
                return 0 
    except Exception as exc:
        state.update({'status':'FAILED','finished_at':datetime.now(timezone.utc).isoformat(),'error_message':str(exc),'last_successful_run_id':old.get('last_successful_run_id'),'last_updated_checkpoint':old.get('last_updated_checkpoint')})
        save_state(state); 
        log.exception('run_id=%s status=FAILED error=%s',run_id,exc); 
        raise



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='E-Commerce trainning daily pipeline')
    parser.add_argument('--input_dir', 
                        default= SETTINGS.incremental_dir / 'day_2026-07-01', 
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
            refresh=args.refresh_mart,
            skip_processed_file=args.skip_processed_file
        )
        sys.exit(0)
    except Exception as exc:
        log.error('[ALERT] Su co nghiem trong khi chay pipeline | error_type=%s | reason=%s',
                  type(exc).__name__, str(exc),exc_info=True)
        sys.exit(1)