import pandas as pd
from pathlib import Path
from src.config import SETTINGS

DATA_DIR = Path(SETTINGS.dirty_dir / "day_2026-07-02")

customers = pd.read_csv(DATA_DIR / "customers_daily.csv")
products = pd.read_csv(DATA_DIR / "products_daily.csv")
orders = pd.read_csv(DATA_DIR / "orders_daily.csv")
order_items = pd.read_csv(DATA_DIR / "order_items_daily.csv")
payments = pd.read_json(DATA_DIR / "payments_daily.json")

# for name, df in {
#     "customers": customers,
#     "products": products,
#     "orders": orders,
#     "order_items": order_items,
#     "payments": payments,
# }.items():
#     print("=" * 60)
#     print(name)
#     print("shape:", df.shape)
#     print("\nnull counts:")
#     print(df.isna().sum())
#     print("\ndtypes:")
#     print(df.dtypes)
#     print("\nhead:")
#     print(df.head())

print(
    customers[
        customers.duplicated(
            subset=["customer_id"],
            keep=False
        )
    ]
)

print(
    products[
        products.duplicated(
            subset=["product_id"],
            keep=False
        )
    ]
)

print(
    orders[
        orders.duplicated(
            subset=["order_id"],
            keep=False
        )
    ]
)

from src.validators.schema_validator import validate_schema

validate_schema("customers", customers)