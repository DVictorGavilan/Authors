from src import openlibrary
from assertpy import assert_that


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload
        self.raise_for_status_called = False

    def raise_for_status(self) -> None:
        self.raise_for_status_called = True

    def json(self) -> dict:
        return self.payload


class FakeSession:
    def __init__(self):
        self.headers = {}
        self.calls = []

    def get(self, url: str, params: dict | None = None, timeout=None):
        self.calls.append({
            "url": url,
            "params": params,
            "timeout": timeout,
        })

        if url.endswith("/search/authors.json"):
            return FakeResponse({
                "docs": [
                    {"key": "OL1A", "name": "Jane Austen", "work_count": 1000}
                ]
            })

        return FakeResponse({
            "key": "OL1A",
            "name": "Jane Austen",
        })


def test_search_author_candidates_calls_openlibrary_search_endpoint(monkeypatch):
    fake_session = FakeSession()

    monkeypatch.setattr(
        openlibrary.requests,
        "Session",
        lambda: fake_session,
    )

    client = openlibrary.OpenLibraryClient()
    result = client.search_author_candidates("Jane Austen")

    assert_that(result).is_length(1)
    assert_that(result[0]["key"]).is_equal_to("OL1A")

    call = fake_session.calls[0]
    assert_that(call["url"]).ends_with("/search/authors.json")
    assert_that(call["params"]).is_equal_to({"q": "Jane Austen"})
    assert_that(call["timeout"]).is_equal_to((15, 30))


def test_get_author_details_calls_openlibrary_author_endpoint(monkeypatch):
    fake_session = FakeSession()

    monkeypatch.setattr(
        openlibrary.requests,
        "Session",
        lambda: fake_session,
    )

    client = openlibrary.OpenLibraryClient()
    result = client.get_author_details("OL1A")

    assert_that(result["key"]).is_equal_to("OL1A")

    call = fake_session.calls[0]
    assert_that(call["url"]).ends_with("/authors/OL1A.json")
    assert_that(call["timeout"]).is_equal_to((15, 30))
