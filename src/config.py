from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

PK = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
}

API_RESOURCES = {
    'customers' : 'customers',
    'products': 'products',
    'orders': 'orders',
    'order_items': 'order-items',  # Mapping tên resource chuẩn có dấu gạch ngang
    'payments': 'payments',
}

@dataclass(frozen=True)
class Settings:
    root: Path = Path(__file__).resolve().parents[1]
    database_url: str = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg://de_user:de_password@localhost:5433/ecommerce',
    )
    api_url: str = os.getenv('MOCK_API_URL', 'http://localhost:8000')
    api_key: str = os.getenv('MOCK_API_KEY', 'training-key')
    raw_dir: Path = root / 'data' / 'raw'
    incremental_dir: Path = root / 'data' / 'incremental'
    dirty_dir: Path = root / 'data' / 'dirty'
    staging_dir: Path = root / 'data' / 'staging'
    reject_dir: Path = root / 'data' / 'reject'
    metadata_dir: Path = root / 'metadata'
    report_dir: Path = root / 'reports'
    metadata_dir: Path = root/ 'metadata'
    reject_rate: float = float(os.getenv('REJECT_RATE_THRESHOLD','0.10'))



SETTINGS = Settings()