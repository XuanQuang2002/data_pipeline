from pandas import DataFrame
from sqlalchemy import text
from .database import engine


PK = {
    'customers':'customer_id', 'products':'product_id', 'orders':'order_id',
    'order_items':'order_item_id', 'payments':'payment_id'
}


def upsert_dataframe(name: str, df: DataFrame):
    """TODO Buổi 6: INSERT ... ON CONFLICT ... DO UPDATE. Trả inserted/updated stats."""
    if df.empty:
        return {
            "inserted_or_updated": 0
        }
    pk = PK[name]
    cols = [ 
        c 
        for c in df.columns
        if c not in [
            "error_code"
        ]
    ]
    placeholders = ",".join(
        ":" + c
        for c in cols
    )
    updates = ",".join(
        f"{c}=EXCLUDED.{c}"
        for c in cols
        if c != pk
    )
    sql = text(
        f"""
        INSERT INTO core.{name}
        ({",".join(cols)})
        VALUES ({placeholders})
        ON CONFLICT ({pk})
        DO UPDATE SET
        {updates}
        """
    )
    records = []
    for row in (
        df[cols]
        .to_dict("records")
    ):
        records.append({
            k: (
                None
                if str(v) == "NaT"
                else (
                    v.to_pydatetime()
                    if hasattr(
                        v,
                        "to_pydatetime"
                    )
                    else v
                )
            )
            for k, v in row.items()
        })
        with engine.begin() as conn:
            conn.execute(
                sql,
                records,
            )
        return {
            "inserted_or_updated": len(records)
        }
