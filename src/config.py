from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "data" / "incremental" / "day_2026-07-01"
STAGING_DIR = ROOT / "data" / "staging"
LOG_DIR = ROOT / "logs"

STAGING_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)