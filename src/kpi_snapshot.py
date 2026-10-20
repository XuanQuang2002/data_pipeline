import json
from sqlalchemy import text
from src.database import engine
SQL={'customers':'SELECT COUNT(*) FROM core.customers','products':'SELECT COUNT(*) FROM core.products','orders':'SELECT COUNT(*) FROM core.orders','order_items':'SELECT COUNT(*) FROM core.order_items','payments':'SELECT COUNT(*) FROM core.payments','completed_orders':"SELECT COUNT(*) FROM core.orders WHERE status='completed'",'revenue':"SELECT COALESCE(SUM(order_total),0) FROM core.orders WHERE status='completed'",'active_customers':"SELECT COUNT(DISTINCT customer_id) FROM core.orders WHERE status='completed'"}
def snapshot():
    out={}
    with engine.connect() as conn:
        for k,sql in SQL.items(): 
            out[k]=int(
                conn.execute(text(sql)).scalar_one()
            )
    return out
# if __name__=='__main__': print(json.dumps(snapshot(),indent=2))