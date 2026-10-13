import requests
from .config import SETTINGS
from .logger import get_logger
from .helper import build_session

log = get_logger("api")
session = build_session()

def fetch_all_pages(
        resource, 
        updated_after = None,
        page_size = 100,
        timeout = 10,
):
    page = 1
    rows = []
    while True:
        params = {
        "page": page,
        "page_size": page_size,
        }
        if updated_after: 
            params["updated_after"] = updated_after
        response = requests.get(
            f"{SETTINGS.api_url}/{resource}",
            params=params,
            headers={
                "X-API-Key": SETTINGS.api_key
            },
            timeout=timeout,
        )
        # test_reponse = session.get(
        #     f"{SETTINGS.api_url}/{resource}",
        #     params=params,
        #     headers={
        #         "X-API-Key": SETTINGS.api_key
        #     },
        #     timeout= (3.05,15),
        # )
        response.raise_for_status()
        payload = response.json()
        rows.extend(payload["data"])
        log.info(
            "resource=%s page=%s rows=%s",
            resource,
            page,
            len(payload["data"]),
        )
        if not payload.get("has_next"):
            break
        page += 1
    return rows
