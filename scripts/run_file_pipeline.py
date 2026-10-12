import argparse
from pathlib import Path
from src.config import SETTINGS
from src.extract_files import profile, read_dataset
from src.logger import get_logger
from src.transform import normalize

log = get_logger('file_pipeline')

FILES = {
    'customers': 'customers_daily.csv',
    'products': 'products_daily.csv',
    'orders': 'orders_daily.csv',
    'order_items': 'order_items_daily.csv',
    'payments': 'payments_daily.json',
}


def run_batch(input_dir: Path):
    input_dir = Path(input_dir)
    log.info('=== Starting Batch File Pipeline: %s ===', input_dir)
    SETTINGS.staging_dir.mkdir(parents=True, exist_ok=True)

    for dataset_name, file_name in FILES.items():
        file_path = input_dir / file_name
        try:
            log.info('Extracting %s from %s', dataset_name, file_path)
            raw_df = read_dataset(file_path)

            prof = profile(raw_df)
            log.info(
                '%s Profile: rows=%d, cols=%d, dups=%d',
                dataset_name,
                prof['rows'],
                len(prof['columns']),
                prof['duplicates'],
            )

            clean_df = normalize(raw_df)
            out_path = SETTINGS.staging_dir / f'{dataset_name}_clean.csv'
            clean_df.to_csv(out_path, index=False)
            log.info('Saved cleaned staging file: %s (%d rows)', out_path, len(clean_df))

        except FileNotFoundError:
            log.error('Missing input file for %s: %s', dataset_name, file_path)
            raise
        except ValueError as exc:
            log.error('Validation error for %s: %s', dataset_name, exc)
            raise

    log.info('=== Batch File Pipeline completed successfully ===')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch File Pipeline Runner')
    parser.add_argument(
        '--input-dir',
        default=str(SETTINGS.root / 'data' / 'incremental' / 'day_2026-07-01'),
        help='Input directory containing daily CSV/JSON files',
    )
    args = parser.parse_args()
    run_batch(Path(args.input_dir))