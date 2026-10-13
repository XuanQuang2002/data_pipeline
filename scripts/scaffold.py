import pandas as pd
from src.api_client import fetch_all_pages
from src.transform import normalize
from src.load_postgres import upsert_dataframe
from src.state_manager import (
    get_watermark,
    save_watermark,
)

# RESOURCE_TABLE = {
#     "customers": "customers",
#     "products": "products",
#     "orders": "orders",
#     "order-items": "order_items",
#     "payments": "payments",
# }

# for resource, table in RESOURCE_TABLE.items():
#     rows = fetch_all_pages(
#         resource,
#         page_size=100,
#     )

#     print(resource,"rows=",len(rows))

#     # SAVE RAW Ở ĐÂY
#     df = normalize(
#         pd.DataFrame(rows)
#     )
#     result = upsert_dataframe(
#         table,df
#     )
#     print(table,result)


def ingest_resource(resource,table):
    old_watermark = (
        get_watermark(resource)
    )

    rows = fetch_all_pages(
        resource,
        updated_after=old_watermark,
        page_size=100,
    )
    if not rows:
        print(resource, "no new rows")
        return
    
    # SAVE RAW Ở ĐÂY
    # TRƯỚC normalize.
    df = normalize(
        pd.DataFrame(rows)
    )
    new_watermark = None
    if (
        "updated_at"
        in df.columns
        and not df.empty
    ):
        new_watermark = (
            df["updated_at"]
            .max()
        )
    result = upsert_dataframe(
        table, df
    )
    # Khi function return bình thường,
    # engine.begin() đã commit.
    if (
        new_watermark
        is not None
    ):
        save_watermark(
            resource,
            new_watermark.isoformat()
        )
    print(
        resource,
        result
    )