import pandas as pd


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names, strings, email/enums, numerics and timestamps without mutating RAW."""
    out = df.copy()

    # 1. Column names: trim & lowercase
    out.columns = [c.strip().lower() for c in out.columns]

    # 2. String trimming for object columns
    for col in out.columns:
        if out[col].dtype == 'object':
            out[col] = out[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # 3. Email lowercasing
    if 'email' in out.columns:
        out['email'] = out['email'].str.lower()

    # 4. Enums lowercasing (khớp PostgreSQL CHECK constraints)
    for col in ['status', 'payment_status', 'payment_method', 'channel']:
        if col in out.columns:
            out[col] = out[col].str.lower()

    # 5. Numerics casting with controlled NaN on failure
    numeric_cols = [
        'unit_price',
        'cost_price',
        'order_total',
        'discount_amount',
        'amount',
        'quantity',
    ]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors='coerce')

    # 6. Datetime casting with UTC conversion
    for col in [c for c in out.columns if c.endswith('_at') or c.endswith('_date')]:  # type: ignore
        out[col] = pd.to_datetime(out[col], errors='coerce', utc=True)

    return out