from pathlib import Path
import json
import pandas as pd

def profile(df: pd.DataFrame) -> dict:
    """Thống kê baseline kỹ thuật: số dòng, danh sách cột, 
    missing per column, duplicate toàn dòng."""
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "missing": df.isna().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
    }

def read_dataset(path: Path) -> pd.DataFrame:
    """Đọc dữ liệu từ file CSV hoặc JSON, trả về DataFrame Pandas."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    suffix = path.suffix.lower()
    if suffix == '.csv':
        try:
            df = pd.read_csv(path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding='utf-8-sig')
    elif suffix == '.json':
        obj = json.loads(path.read_text(encoding='utf-8'))
        df = pd.DataFrame(obj if isinstance(obj, list) else obj.get('data', []))
    else:
        raise ValueError(f"Unsupported file: {path}")

    if len(df) == 0:
        raise ValueError(f"Empty dataset: {path}")

    return df