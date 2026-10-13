import json
from src.config import SETTINGS

STATE_FILE = (
    SETTINGS.metadata_dir
    / "pipeline_state.json"
)

def read_state():
    if not STATE_FILE.exists():
        return {}
    return json.loads(
        STATE_FILE.read_text(encoding="utf-8")
    )

def get_watermark(resource):
    state = read_state()
    return (
        state
        .get(resource, {})
        .get("last_updated_at")
    )

def save_watermark(
    resource,
    value,
):
    SETTINGS.metadata_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    state = read_state()
    state.setdefault(
        resource,
        {}
    )
    state[resource]["last_updated_at"] = value
    STATE_FILE.write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )