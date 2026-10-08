import pandas as pd

NUMERIC_COLUMNS = {
    "quantity",
    "unit_price",
    "discount_amount",
    "order_total",
    "amount",
    "cost_price",
}

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy() # Khong sua truc tiep dataframe goc de tranh anh huong den cac bien khac
    out.columns = [c.strip().lower() for c in out.columns]

    for col in out.columns:
        if out[col].dtype == "object":
            out[col] = out[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

    if "email" in out:
        out["email"] = out["email"].str.lower() # Chuyen tat ca cac chu cai trong cot email thanh chu thuong

    for col in ["status", "payment_status", "payment_method", "channel"]:
        if col in out:
            out[col] = out[col].str.lower() # Chuyen tat ca cac chu cai trong cot thanh chu thuong

    date_cols: list[str] = [
        c for c in out.columns if c.endswith(("_at", "_date")) or c.endswith("_date") # type: ignore
    ]

    for col in date_cols:
        out[col] = pd.to_datetime(out[col], errors="coerce", utc=True)
        # Chuyen cac gia tri trong cot thanh kieu datetime, neu co loi thi tra ve NaT
    
    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    out["source_system"] = "file_batch" # source_system: record den tu nguon nao
    out["ingested_at"] = pd.Timestamp.now(tz="UTC") #ingested_at: pipeline ingest luc nao

    return out