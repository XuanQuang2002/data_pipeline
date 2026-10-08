from pathlib import Path
from src.config import Settings
from src.extract_files import read_dataset, profile
from src.transform import normalize
from src.logger import get_logger
import pandas as pd
from pathlib import Path

logger = get_logger()
staging = Settings().staging_dir

FILES = [
    "customers_daily.csv",
    "products_daily.csv",
    "orders_daily.csv",
    "order_items_daily.csv",
    "payments_daily.json",
]


def process_one(path: Path):
    logger.info("start dataset=%s", path.name)

    raw_df = read_dataset(path)
    before = profile(raw_df)

    logger.info(
        "profile dataset=%s rows=%s missing=%s duplicates=%s",
        path.name,
        before["rows"],
        sum(before["missing"].values()),
        before["duplicates"],
    )

    clean_df = normalize(raw_df)
    output_path = Settings().staging_dir / f"{path.stem}_clean.csv"
    clean_df.to_csv(output_path, index=False)

    logger.info(
        "success dataset=%s rows_in=%d rows_out=%d output=%s",
        path.name,
        len(raw_df),
        len(clean_df),
        output_path,
    )


def main():
    logger.info("pipeline started")

    for file_name in FILES:
        path = Settings().staging_dir / file_name
        try:
            process_one(path)
        except FileNotFoundError:
            logger.exception("file not found dataset=%s", file_name)
            raise
        except Exception:
            logger.exception("failed dataset=%s", file_name)
            raise

    for path in sorted(staging.glob("*_clean.csv")):
        df = pd.read_csv(path)
        print(path.name, len(df))
        check_parse_failure(df, path)

    logger.info("pipeline success")

def check_parse_failure(clean_df: pd.DataFrame, path: Path):
    for col in clean_df.columns:
        if col.endswith("_date") or col.endswith("_at"):
            n_invalid = clean_df[col].isna().sum()
            logger.info(
                "dataset=%s column=%s null_after_parse=%d",
                path.name,
                col,
                n_invalid,
            )
    for col in clean_df.columns:
        if col in {"quantity", "unit_price", "discount_amount", "order_total", "amount", "cost_price"}:
            n_invalid = clean_df[col].isna().sum()
            logger.info(
                "dataset=%s column=%s null_after_parse=%d",
                path.name,
                col,
                n_invalid,
            )

if __name__ == "__main__":
    main()