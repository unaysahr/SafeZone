import pytest

from safezone.providers import lookup_zip
from safezone.providers.base import OffenderRecord, ProviderError
from safezone.providers.dc import DCProvider


class StubProvider:
    """Provider double: returns fixed records without touching the network."""

    name = "Stub Registry"
    source_url = "https://example.gov/registry"
    attribution = "Data: Stub"

    def __init__(self, records=None, states=("DC",), error=None):
        self._records = records or []
        self._states = states
        self._error = error

    def covers(self, zip_code, state):
        return state in self._states

    def lookup(self, zip_code, state):
        if self._error:
            raise self._error
        return self._records


def record(name="Jane Doe"):
    return OffenderRecord(source_id="1", name=name, source="Stub")


def test_covered_zip_returns_records():
    result = lookup_zip("20001", [StubProvider([record()])])
    assert result.covered is True
    assert result.count == 1
    assert result.source == "Stub Registry"
    assert result.degraded is False


def test_covered_zip_with_no_records_is_still_covered():
    result = lookup_zip("20001", [StubProvider([])])
    assert result.covered is True
    assert result.count == 0
    assert result.to_dict()["has_offenders"] is False


def test_uncovered_state_is_reported_not_guessed():
    result = lookup_zip("60614", [StubProvider([record()], states=("DC",))])
    assert result.covered is False
    assert result.records == []
    assert result.degraded is False, "no provider serves IL - that is not an outage"


def test_provider_failure_degrades_instead_of_fabricating():
    result = lookup_zip("20001", [StubProvider(error=ProviderError("boom"))])
    assert result.covered is False
    assert result.records == []
    assert result.degraded is True, "a covering provider failed - that is an outage"


def test_unexpected_exception_is_contained():
    result = lookup_zip("20001", [StubProvider(error=ValueError("unexpected"))])
    assert result.covered is False
    assert result.degraded is True


def test_first_covering_provider_wins():
    first = StubProvider([record("First")], states=("DC",))
    second = StubProvider([record("Second")], states=("DC",))
    result = lookup_zip("20001", [first, second])
    assert result.records[0].name == "First"


def test_failing_provider_falls_through_to_next():
    broken = StubProvider(error=ProviderError("down"), states=("DC",))
    working = StubProvider([record("Backup")], states=("DC",))
    result = lookup_zip("20001", [broken, working])
    assert result.covered is True
    assert result.records[0].name == "Backup"


def test_empty_provider_chain_is_supported():
    result = lookup_zip("20001", [])
    assert result.covered is False
    assert result.degraded is False


def test_invalid_zip_rejected():
    with pytest.raises(ValueError):
        lookup_zip("abc", [])


def test_dc_provider_maps_arcgis_feature_to_record():
    provider = DCProvider()
    feature = {
        "attributes": {
            "OBJECTID": 42,
            "FIRSTNAME": "Jane",
            "LASTNAME": "Doe",
            "BLOCKSITEADDRESS": "1200 block of Example St NW",
            "ZIP": "20001",
            "OFFENSE": "Example offense",
        },
        "geometry": {"x": -77.02, "y": 38.90},
    }
    rec = provider._to_record(feature, "20001")
    assert rec.name == "Jane Doe"
    assert rec.address == "1200 block of Example St NW"
    assert rec.lat == 38.90 and rec.lng == -77.02
    assert rec.state == "DC"


def test_dc_provider_handles_missing_fields_without_inventing_them():
    rec = DCProvider()._to_record({"attributes": {"OBJECTID": 1}, "geometry": {}}, "20001")
    assert rec.name == "Name not published"
    assert rec.address is None
    assert rec.lat is None and rec.lng is None


def test_dc_provider_only_covers_dc():
    provider = DCProvider()
    assert provider.covers("20001", "DC") is True
    assert provider.covers("60614", "IL") is False
