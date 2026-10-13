from src.api_client import fetch_all_pages
import pandas as pd
from src.transform import normalize
from src.load_postgres import upsert_dataframe

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

# fullload: doc toan bo, don gian, ton I/O hon
rows = fetch_all_pages(
    "customers",
)

# Increamental Load: 
# chi lay record moi/thay doi
# can check point/watermark
rows_temp = fetch_all_pages(
    "customers",
    updated_after="2023-01-01T00:00:00Z",
)
df = normalize(
    pd.DataFrame(rows)
)
result = upsert_dataframe(
    "customers",df,
)
print(result)