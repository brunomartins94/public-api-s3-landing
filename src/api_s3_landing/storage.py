from __future__ import annotations

import json
from datetime import date

import boto3
from botocore.exceptions import ClientError


class S3LandingWriter:
    def __init__(self, bucket: str, region: str, endpoint_url: str | None = None, s3_client=None) -> None:
        self.bucket = bucket
        self.s3_client = s3_client or boto3.client("s3", region_name=region, endpoint_url=endpoint_url)

    @staticmethod
    def key_for(ingested_on: date, page: int) -> str:
        return f"raw/open_brewery_db/ingested_date={ingested_on.isoformat()}/page={page:04d}.json"

    def write_page(self, records: list[dict], page: int, ingested_on: date) -> bool:
        key = self.key_for(ingested_on, page)
        if self._exists(key):
            return False

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(records, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            Metadata={"source": "open-brewery-db", "page": str(page), "record-count": str(len(records))},
        )
        return True

    def _exists(self, key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as error:
            status_code = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            error_code = error.response.get("Error", {}).get("Code")
            if status_code == 404 or error_code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise
