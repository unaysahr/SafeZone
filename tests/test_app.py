import json

import pytest

from app import create_app
from safezone.providers.base import OffenderRecord


class StubProvider:
    name = "Stub Registry"
    source_url = "https://example.gov/registry"
    attribution = "Data: Stub"

    def __init__(self, records=None, states=("DC",)):
        self._records = records or []
        self._states = states

    def covers(self, zip_code, state):
        return state in self._states

    def lookup(self, zip_code, state):
        return self._records


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    app = create_app()
    app.config["PROVIDERS"] = []
    app.config["TESTING"] = True
    return app.test_client()


def search(client, zip_code):
    return client.post("/search", json={"zip_code": zip_code})


def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"SafeZone" in response.data


def test_missing_secret_refuses_to_start(monkeypatch):
    monkeypatch.delenv("SESSION_SECRET", raising=False)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    with pytest.raises(RuntimeError, match="SESSION_SECRET"):
        create_app()


@pytest.mark.parametrize("zip_code", ["", "1234", "123456", "abcde", "1234x"])
def test_invalid_zip_rejected(client, zip_code):
    response = search(client, zip_code)
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_non_json_body_is_a_400_not_a_500(client):
    response = client.post("/search", data="not json", content_type="text/plain")
    assert response.status_code == 400


def test_json_array_body_rejected(client):
    response = client.post("/search", json=["not", "a", "dict"])
    assert response.status_code == 400


def test_uncovered_area_hands_off_to_official_registry(client):
    body = search(client, "60614").get_json()
    assert body["success"] is True
    assert body["covered"] is False
    assert body["offenders"] == []
    assert "nsopw.gov" in body["official_search_url"]
    assert "Illinois" in body["message"]


def test_uncovered_response_never_claims_offenders(client):
    body = search(client, "60614").get_json()
    assert body["has_offenders"] is False
    assert body["count"] == 0


def test_same_zip_returns_identical_results(client):
    """Regression: results must be deterministic, never randomly generated."""
    first = search(client, "60614").get_json()
    for _ in range(5):
        assert search(client, "60614").get_json() == first


def test_covered_area_reports_records_and_source(client, monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    app = create_app()
    app.config["PROVIDERS"] = [
        StubProvider([OffenderRecord(source_id="1", name="Jane Doe", source="Stub")])
    ]
    body = app.test_client().post("/search", json={"zip_code": "20001"}).get_json()

    assert body["covered"] is True
    assert body["count"] == 1
    assert body["has_offenders"] is True
    assert body["source"] == "Stub Registry"
    assert body["offenders"][0]["name"] == "Jane Doe"


def test_covered_area_with_zero_records_says_none_listed(client, monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    app = create_app()
    app.config["PROVIDERS"] = [StubProvider([])]
    body = app.test_client().post("/search", json={"zip_code": "20001"}).get_json()
    assert body["covered"] is True
    assert body["has_offenders"] is False
    assert "no registered offenders" in body["message"]


def test_security_headers_present(client):
    headers = client.get("/").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"


def test_rate_limit_engages(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    monkeypatch.setattr("app.RATE_LIMIT_REQUESTS", 3)
    import app as app_module
    app_module._hits.clear()

    app = create_app()
    app.config["PROVIDERS"] = []
    client = app.test_client()

    codes = [client.post("/search", json={"zip_code": "60614"}).status_code for _ in range(5)]
    assert 429 in codes, f"expected a 429 among {codes}"


def test_unknown_page_returns_index(client):
    assert client.get("/does-not-exist").status_code == 404


def test_unknown_api_path_returns_json(client):
    response = client.get("/search/nope")
    assert response.status_code == 404
    assert response.is_json
