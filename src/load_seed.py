import pandas as pd
from sqlalchemy import text
from src.config import SETTINGS
from src.database import engine
from src.transform import normalize
from src.load_postgres import upsert_dataframe
from typing import Any, cast

def main():
    seed=SETTINGS.root/'data/seed'
    # cat=pd.read_csv(seed/'categories.csv')
    # cat=cat.astype(object).where(cat.notna(),None)
    # records = cast(list[dict[str, Any]], cat.to_dict(orient="records"))
    # with engine.begin() as conn:
    #     conn.execute(
    #         text(
    #             "INSERT INTO core.categories(category_id,category_name,parent_category_id,created_at,updated_at) " \
    #             "VALUES (:category_id,:category_name,NULLIF(:parent_category_id, ''),:created_at,:updated_at) " \
    #             "ON CONFLICT (category_id) DO UPDATE SET category_name=EXCLUDED.category_name,parent_category_id=EXCLUDED.parent_category_id,updated_at=EXCLUDED.updated_at"),
    #         records
    #     )
            
    for name in ['customers','products','orders','order_items','payments']:
        df=normalize(pd.read_csv(seed/f'{name}.csv'))
        with engine.begin() as conn: 
            upsert_dataframe(name,df)
# if __name__=='__main__': main()