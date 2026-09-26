from __future__ import annotations

import argparse
import logging
from datetime import date

from .client import PublicApiClient
from .config import Settings
from .storage import S3LandingWriter


def run(settings: Settings, ingested_on: date | None = None) -> dict[str, int]:
    ingested_on = ingested_on or date.today()
    client = PublicApiClient(settings.api_base_url, settings.per_page)
    writer = S3LandingWriter(settings.bucket, settings.region, endpoint_url=settings.s3_endpoint_url)
    result = {"written_pages": 0, "skipped_pages": 0, "records": 0}

    for page, records in client.pages(settings.max_pages):
        if writer.write_page(records, page, ingested_on):
            result["written_pages"] += 1
            result["records"] += len(records)
            logging.info("page_landed", extra={"page": page, "record_count": len(records)})
        else:
            result["skipped_pages"] += 1
            logging.info("page_already_landed", extra={"page": page})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Land a paginated public API in S3")
    parser.add_argument("--max-pages", type=int, help="Limit pages for an execution")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = Settings.from_environment()
    if args.max_pages:
        settings = Settings(**{**settings.__dict__, "max_pages": args.max_pages})
    logging.info("pipeline_finished %s", run(settings))


if __name__ == "__main__":
    main()
