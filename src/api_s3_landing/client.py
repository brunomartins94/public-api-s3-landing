from __future__ import annotations

import logging
from collections.abc import Iterator

import requests


LOGGER = logging.getLogger(__name__)


class PublicApiClient:
    def __init__(self, base_url: str, per_page: int, session: requests.Session | None = None) -> None:
        self.base_url = base_url
        self.per_page = per_page
        self.session = session or requests.Session()

    def pages(self, max_pages: int | None = None) -> Iterator[tuple[int, list[dict]]]:
        page = 1
        while max_pages is None or page <= max_pages:
            response = self.session.get(
                self.base_url,
                params={"page": page, "per_page": self.per_page},
                timeout=30,
            )
            response.raise_for_status()
            records = response.json()
            if not isinstance(records, list):
                raise ValueError("Expected the API response to be a JSON list")
            if not records:
                return

            LOGGER.info("api_page_received", extra={"page": page, "record_count": len(records)})
            yield page, records
            if len(records) < self.per_page:
                return
            page += 1
