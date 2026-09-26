from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_API_URL = "https://api.openbrewerydb.org/v1/breweries"


@dataclass(frozen=True)
class Settings:
    bucket: str
    region: str
    api_base_url: str
    per_page: int
    max_pages: int | None
    s3_endpoint_url: str | None

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()
        bucket = os.getenv("S3_BUCKET", "").strip()
        if not bucket:
            raise ValueError("S3_BUCKET must be configured")

        max_pages = os.getenv("MAX_PAGES", "").strip()
        endpoint_url = os.getenv("S3_ENDPOINT_URL", "").strip()
        return cls(
            bucket=bucket,
            region=os.getenv("AWS_REGION", "us-east-1"),
            api_base_url=os.getenv("API_BASE_URL", DEFAULT_API_URL),
            per_page=int(os.getenv("PER_PAGE", "50")),
            max_pages=int(max_pages) if max_pages else None,
            s3_endpoint_url=endpoint_url or None,
        )
