from api_s3_landing.client import PublicApiClient


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append(params)
        return Response(next(self.responses))


def test_pages_stops_after_a_partial_page():
    session = Session([[{"id": 1}, {"id": 2}], [{"id": 3}]])
    client = PublicApiClient("https://example.test/breweries", per_page=2, session=session)

    assert list(client.pages()) == [(1, [{"id": 1}, {"id": 2}]), (2, [{"id": 3}])]
    assert session.calls == [{"page": 1, "per_page": 2}, {"page": 2, "per_page": 2}]
