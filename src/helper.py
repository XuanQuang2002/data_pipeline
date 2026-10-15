import requests
import json
from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import SETTINGS, PK

def build_session():
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[
            500,
            502,
            503,
            504,
        ],
        allowed_methods=[
            "GET",
        ],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retry
    )
    session = requests.Session()
    session.mount(
        "http://",
        adapter
    )
    return session


def save_raw_rows(
        resource,
        rows,
        run_id=None,
    ):
    if run_id is None:
        run_id = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S"
        )
        folder = (
            SETTINGS.raw_dir
            / "api"
            / resource
        )
        folder.mkdir(parents=True,exist_ok=True,)
        path = folder / f"run_{run_id}.json"
        payload = {
            "resource": resource,
            "run_id": run_id,
            "data": rows,
        }
        path.write_text(
            json.dumps(
                payload,
                ensure_ascii = False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        return path

def clean_blank_values(df):
    out = df.copy()

    for col in out.columns:
        if out[col].dtype == "object":
            out[col] = out[col].replace(
                r"^\s*$",
                None,
                regex=True
            )

    return out

def split_duplicate_pk(
    name,
    df,
):

    pk = PK[name]

    dup_mask = df.duplicated(
        subset=[pk],
        keep="first"
    )

    valid = df[
        ~dup_mask
    ].copy()

    reject = df[
        dup_mask
    ].copy()

    if not reject.empty:

        reject[
            "error_code"
        ] = "DUPLICATE_ID"

        reject[
            "error_message"
        ] = (
            f"{pk} duplicated "
            "inside current batch"
        )

    return valid, reject