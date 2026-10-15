# Lần 1: Chạy nạp cold start

python -c "
import json, pandas as pd
from src.load_postgres import upsert_dataframe
data = json.load(open('data/raw/run_20260701_100000/orders.json', encoding='utf-8'))
df = pd.DataFrame(data)
res1 = upsert_dataframe('orders', df)
print('RUN 1 RESULT:', res1)
"

Database connection successful: 1
Traceback (most recent call last):
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1912, in \_exec_single_context
self.dialect.do_executemany(
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 1189, in do_executemany
cursor.executemany(statement, parameters)
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 148, in executemany
raise ex.with_traceback(None)
psycopg.errors.ForeignKeyViolation: insert or update on table "orders" violates foreign key constraint "fk_orders_customer"
DETAIL: Key (customer_id)=(CUS00000021) is not present in table "customers".

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
File "<string>", line 6, in <module>
File "/Volumes/Data/Developer/PythonProject/data_pipeline/src/load_postgres.py", line 71, in upsert_dataframe
conn.execute(sql, records)
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1448, in execute
return meth(
^^^^^
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/sql/elements.py", line 533, in \_execute_on_connection
return connection.\_execute_clauseelement(
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1668, in \_execute_clauseelement
ret = self.\_execute_context(
^^^^^^^^^^^^^^^^^^^^^^
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1822, in \_execute_context
return self.\_exec_single_context(
^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1962, in \_exec_single_context
self.\_handle_dbapi_exception(
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 2332, in \_handle_dbapi_exception
raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1912, in \_exec_single_context
self.dialect.do_executemany(
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 1189, in do_executemany
cursor.executemany(statement, parameters)
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 148, in executemany
raise ex.with_traceback(None)
sqlalchemy.exc.IntegrityError: (psycopg.errors.ForeignKeyViolation) insert or update on table "orders" violates foreign key constraint "fk_orders_customer"
DETAIL: Key (customer_id)=(CUS00000021) is not present in table "customers".
[SQL: INSERT INTO core.orders (order_id,customer_id,order_date,status,shipping_city,channel,order_total,source_system,created_at,updated_at) VALUES (%(order_id)s, %(customer_id)s, %(order_date)s, %(status)s, %(shipping_city)s, %(channel)s, %(order_total)s, %(source_system)s, %(created_at)s, %(updated_at)s) ON CONFLICT (order_id) DO UPDATE SET customer_id=EXCLUDED.customer_id, order_date=EXCLUDED.order_date, status=EXCLUDED.status, shipping_city=EXCLUDED.shipping_city, channel=EXCLUDED.channel, order_total=EXCLUDED.order_total, source_system=EXCLUDED.source_system, created_at=EXCLUDED.created_at, updated_at=EXCLUDED.updated_at]
[parameters: [{'order_id': 'ORD00000001', 'customer_id': 'CUS00000021', 'order_date': '2026-06-25T14:20:00Z', 'status': 'completed', 'shipping_city': 'Hà Nội', 'channel': 'mobile_app', 'order_total': 450000.0, 'source_system': 'mock_api', 'created_at': '2026-06-25T14:20:00Z', 'updated_at': '2026-07-01T08:30:00Z'}, {'order_id': 'ORD00000002', 'customer_id': 'CUS00000045', 'order_date': '2026-06-25T15:10:00Z', 'status': 'shipped', 'shipping_city': 'Đà Nẵng', 'channel': 'web', 'order_total': 1250000.0, 'source_system': 'mock_api', 'created_at': '2026-06-25T15:10:00Z', 'updated_at': '2026-07-01T09:15:00Z'}]]
(Background on this error at: https://sqlalche.me/e/21/gkpj)

# Lần 2: Nạp lại cùng tập dữ liệu

python -c "
import json, pandas as pd
from src.load_postgres import upsert_dataframe
data = json.load(open('data/raw/run_20260701_100000/orders.json', encoding='utf-8'))
df = pd.DataFrame(data)
res2 = upsert_dataframe('orders', df)
print('RUN 2 RESULT:', res2)
"

Database connection successful: 1
Traceback (most recent call last):
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1912, in \_exec_single_context
self.dialect.do_executemany(
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 1189, in do_executemany
cursor.executemany(statement, parameters)
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 148, in executemany
raise ex.with_traceback(None)
psycopg.errors.ForeignKeyViolation: insert or update on table "orders" violates foreign key constraint "fk_orders_customer"
DETAIL: Key (customer_id)=(CUS00000021) is not present in table "customers".

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
File "<string>", line 6, in <module>
File "/Volumes/Data/Developer/PythonProject/data_pipeline/src/load_postgres.py", line 71, in upsert_dataframe
conn.execute(sql, records)
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1448, in execute
return meth(
^^^^^
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/sql/elements.py", line 533, in \_execute_on_connection
return connection.\_execute_clauseelement(
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1668, in \_execute_clauseelement
ret = self.\_execute_context(
^^^^^^^^^^^^^^^^^^^^^^
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1822, in \_execute_context
return self.\_exec_single_context(
^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1962, in \_exec_single_context
self.\_handle_dbapi_exception(
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 2332, in \_handle_dbapi_exception
raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 1912, in \_exec_single_context
self.dialect.do_executemany(
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 1189, in do_executemany
cursor.executemany(statement, parameters)
File "/Volumes/Data/Developer/PythonProject/data_pipeline/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 148, in executemany
raise ex.with_traceback(None)
sqlalchemy.exc.IntegrityError: (psycopg.errors.ForeignKeyViolation) insert or update on table "orders" violates foreign key constraint "fk_orders_customer"
DETAIL: Key (customer_id)=(CUS00000021) is not present in table "customers".
[SQL: INSERT INTO core.orders (order_id,customer_id,order_date,status,shipping_city,channel,order_total,source_system,created_at,updated_at) VALUES (%(order_id)s, %(customer_id)s, %(order_date)s, %(status)s, %(shipping_city)s, %(channel)s, %(order_total)s, %(source_system)s, %(created_at)s, %(updated_at)s) ON CONFLICT (order_id) DO UPDATE SET customer_id=EXCLUDED.customer_id, order_date=EXCLUDED.order_date, status=EXCLUDED.status, shipping_city=EXCLUDED.shipping_city, channel=EXCLUDED.channel, order_total=EXCLUDED.order_total, source_system=EXCLUDED.source_system, created_at=EXCLUDED.created_at, updated_at=EXCLUDED.updated_at]
[parameters: [{'order_id': 'ORD00000001', 'customer_id': 'CUS00000021', 'order_date': '2026-06-25T14:20:00Z', 'status': 'completed', 'shipping_city': 'Hà Nội', 'channel': 'mobile_app', 'order_total': 450000.0, 'source_system': 'mock_api', 'created_at': '2026-06-25T14:20:00Z', 'updated_at': '2026-07-01T08:30:00Z'}, {'order_id': 'ORD00000002', 'customer_id': 'CUS00000045', 'order_date': '2026-06-25T15:10:00Z', 'status': 'shipped', 'shipping_city': 'Đà Nẵng', 'channel': 'web', 'order_total': 1250000.0, 'source_system': 'mock_api', 'created_at': '2026-06-25T15:10:00Z', 'updated_at': '2026-07-01T09:15:00Z'}]]
(Background on this error at: https://sqlalche.me/e/21/gkpj)
