from src.api_client import fetch_all_pages
import pandas as pd
from src.transform import normalize
from src.load_postgres import upsert_dataframe
from src.config import SETTINGS
from src.logger import get_logger

log = get_logger("test_api")
tables = {
    "customers" : "customers", 
    "products" : "products",
    "orders" : "orders",
    "order-items" : "order_items",
    "payments" : "payments"}

# rows = fetch_all_pages(
#     "customers",
#     page_size=25,
# )
# print(len(rows))
# print(rows[:2])

# resources = {
#     "customers": 100,
#     "products": 50,
#     "orders": 600,
#     "order-items": 1533,
#     "payments": 536,
# }

# for resource, expected in resources.items():
#     rows = fetch_all_pages(
#         resource,
#         page_size=100,
#     )
#     print(resource,len(rows),"expected=",expected)

for resource in tables:
    rows = fetch_all_pages(
        resource,
    )
    log.info("resource=%s rows=%d", resource, len(rows))

    # SAVE RAW Ở ĐÂY
    df = normalize(
        pd.DataFrame(rows)
    )
    result = upsert_dataframe(
        tables[resource],df
    )
    df.to_csv(SETTINGS.raw_dir / "api" / ""f"{resource}_raw.csv", index=False)
    log.info("resource=%s upserted=%s", resource, result)