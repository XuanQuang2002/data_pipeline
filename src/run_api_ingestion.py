from pathlib import Path
from sqlalchemy import text
from src.database import engine
from src.config import SETTINGS
from src.logger import get_logger
logger=get_logger('refresh_mart')
def run_sql_file(path):
    sql=Path(path).read_text(encoding='utf-8'); statements=[s.strip() for s in sql.split(';') if s.strip()]
    with engine.begin() as conn:
        for stmt in statements: conn.execute(text(stmt))
def main():
    run_sql_file(SETTINGS.root/'sql/solutions/10_create_sales_data_mart.sql')
    run_sql_file(SETTINGS.root/'sql/solutions/12_load_data_mart.sql')
    logger.info('Sales Data Mart refresh completed')
if __name__=='__main__': main()