# from pathlib import Path
# from sqlalchemy import text
# from src.config import SETTINGS
# from src.database import engine
# from src.load_seed import main as load_seed
# from src.refresh_mart import main as refresh_mart
# def execute_script(path):
#     sql=Path(path).read_text(encoding='utf-8'); statements=[s.strip() for s in sql.split(';') if s.strip()]
#     with engine.begin() as conn:
#         for stmt in statements: conn.execute(text(stmt))
# def main():
#     with engine.begin() as conn:
#         conn.execute(text('DROP SCHEMA IF EXISTS mart CASCADE')); conn.execute(text('DROP SCHEMA IF EXISTS core CASCADE'))
#     execute_script(SETTINGS.root/'sql/solutions/01_create_oltp.sql'); load_seed(); refresh_mart(); print('RESET COMPLETE: seed baseline + mart ready.')
# if __name__=='__main__': main()