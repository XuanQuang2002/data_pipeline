from .config import SETTINGS
from .database import engine
from src.logger import get_logger
logger=get_logger('refresh_mart')

def refresh():
    """Thực thi script SQL làm mới Sales Data Mart."""
    sql_path = SETTINGS.root / 'sql' / 'solutions' / '12_load_data_mart.sql'
    sql = sql_path.read_text(encoding='utf-8')
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        try:
            cur.execute(sql)
        finally:
            cur.close()
        raw.commit()
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


if __name__ == '__main__':
    refresh()
