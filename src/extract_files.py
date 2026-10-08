from pathlib import Path
import json
import pandas as pd

def profile(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "missing": df.isna().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
    }

def read_dataset(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)

    if path.suffix.lower() == ".json":
        obj = json.loads(path.read_text(encoding="utf-8"))
        return pd.DataFrame(
            obj if isinstance(obj, list)
            else obj.get("data", [])
        )

    raise ValueError(f"Unsupported file: {path}")