import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import SETTINGS
from .logger import get_logger

log = get_logger("api")

def build_session():
    retry=Retry(
        total=3,
        status_forcelist=[500,502,503,504],
        allowed_methods=['GET'],
        backoff_factor=1,
        raise_on_status=False)
    s=requests.Session()
    a=HTTPAdapter(max_retries=retry)
    s.mount('http://',a)
    s.mount('https://',a)
    return s

def fetch_all_pages(
        resource: str, 
        updated_after: str | None = None,
        page_size: int = 100,
        timeout = 10,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
) -> list[dict]:
    """
    Thu thập toàn bộ các trang dữ liệu từ một tài nguyên REST API với cơ chế
    Bounded Exponential Retry, kiểm soát timeout và bảo mật API key.
    """
    page = 1
    rows = []
    while True:
        params: dict[str, int | str] = {'page': page,'page_size': page_size,}
        if updated_after: 
            params["updated_after"] = updated_after

        last_error = None
        payload = None

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(
                    f"{SETTINGS.api_url}/{resource}",
                    params=params,
                    headers={
                        "X-API-Key": SETTINGS.api_key
                    },
                    timeout=timeout, # Ngan treo network vo han
                )
                response.raise_for_status() # Phat hien loi 4xx/5xx va nem exception
                payload = response.json()
                break  # Exit the retry loop if successful
            except requests.RequestException as exc:
                last_error = exc
                log.warning(
                    "resource=%s page=%s attempt=%s/%s error=%s",
                    resource,
                    page,
                    attempt,
                    max_retries,
                    last_error,
                )
                if attempt == max_retries:
                    # Het luot retry -> nem RuntimeError co ngu canh ro rang
                    raise RuntimeError(
                        f"API failed after {max_retries} attempts: {resource} page {page}"
                    ) from last_error

                # Thoi gian break tang theo cap so nhan 1s -> 2s -> 4s
                sleep_time = backoff_seconds * (2 ** (attempt - 1))
                time.sleep(sleep_time)

        if payload is None:
            raise RuntimeError(f"API returned no payload: {resource} page {page}")

        page_rows = payload.get('data', [])
        rows.extend(page_rows)
        log.info(
            "resource=%s page=%s rows=%s total_so_far=%s",
            resource,
            page,
            len(page_rows),
            len(rows),
        )
        # Dieu kien dung phan trang: has_next = False
        if not payload.get('has_next'):
            break
        page += 1
    return rows
