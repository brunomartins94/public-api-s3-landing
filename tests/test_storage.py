from datetime import date

from botocore.exceptions import ClientError

from api_s3_landing.storage import S3LandingWriter


class FakeS3:
    def __init__(self):
        self.objects = {}

    def head_object(self, Bucket, Key):
        if Key not in self.objects:
            raise ClientError({"Error": {"Code": "404"}, "ResponseMetadata": {"HTTPStatusCode": 404}}, "HeadObject")
        return {}

    def put_object(self, Bucket, Key, **kwargs):
        self.objects[Key] = kwargs


def test_writer_uses_a_deterministic_key_and_skips_reprocessing():
    s3 = FakeS3()
    writer = S3LandingWriter("landing-bucket", "us-east-1", s3_client=s3)
    ingested_on = date(2026, 9, 26)

    assert writer.write_page([{"id": 1}], page=1, ingested_on=ingested_on) is True
    assert writer.write_page([{"id": 1}], page=1, ingested_on=ingested_on) is False
    assert list(s3.objects) == ["raw/open_brewery_db/ingested_date=2026-09-26/page=0001.json"]
