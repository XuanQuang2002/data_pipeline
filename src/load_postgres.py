from pandas import DataFrame
from sqlalchemy import text
from .database import engine
import pandas as pd


PK = {
    'customers':'customer_id', 
    'products':'product_id', 
    'orders':'order_id',
    'order_items':'order_item_id', 
    'payments':'payment_id'
}

def _python_value(value):
    """Xử lý triệt để NaN, NaT và numpy types thành None cho PostgreSQL driver."""
    if value is None:
        return None
    try:
        if str(value) in {'NaT', 'nan', '<NA>'}:
            return None
    except Exception:
        pass
    if hasattr(value, 'to_pydatetime'):
        return value.to_pydatetime()
    if hasattr(value, 'item'):
        try:
            return value.item()
        except Exception:
            pass
    return value

def upsert_dataframe(name: str, df: pd.DataFrame) -> dict:
    """
    Nạp dữ liệu vào bảng core.<name> thông qua mệnh đề ON CONFLICT DO UPDATE.
    Sử dụng transaction boundary (engine.begin()) và trả về số lượng inserted/updated.
    """
    if df.empty:
        return {'inserted': 0, 'updated': 0, 'inserted_or_updated': 0}

    pk = PK[name]
    # Loại trừ cột kỹ thuật không nằm trong schema vật lý (nếu có)
    cols = [c for c in df.columns if c != 'error_code']
    incoming_ids = set(df[pk].astype(str))

    # 1. Truy vấn các ID đã tồn tại để phân định chính xác inserted vs updated
    with engine.connect() as conn:
        existing_ids = set(
            map(str, conn.execute(text(f"SELECT {pk} FROM core.{name}")).scalars().all())
        )

    inserted = len(incoming_ids - existing_ids)
    updated = len(incoming_ids & existing_ids)

    # 2. Xây dựng câu lệnh PostgreSQL UPSERT
    placeholders = ', '.join(':' + c for c in cols)
    updates = ', '.join(f"{c}=EXCLUDED.{c}" for c in cols if c != pk)
    sql = text(
        f"INSERT INTO core.{name} ({','.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT ({pk}) DO UPDATE SET {updates}"
    )

    # Chuẩn hóa giá trị sang kiểu dữ liệu thuần Python
    records: list[dict] = [
        {k: _python_value(v) for k, v in row.items()}
        for row in df[cols].to_dict('records')
    ]

    # 3. Thực thi trong Transaction Boundary (ACID commit/rollback)
    with engine.begin() as conn:
        conn.execute(sql, records)

    return {
        'inserted': inserted,
        'updated': updated,
        'inserted_or_updated': len(records),
    }
