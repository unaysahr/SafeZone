"""Optional national coverage via a commercial registry API.

There is no free national API - NSOPW is a federated search portal with no
public programmatic interface. Several vendors resell aggregated registry
data (offenders.io, OffenderList, Zyla). This provider talks to one of them,
configured entirely by environment variable so no vendor is hardcoded and no
key is ever committed.

Disabled unless SAFEZONE_NATIONAL_API_URL and SAFEZONE_NATIONAL_API_KEY are
both set. When disabled it simply declines coverage and the app falls back to
the official-registry handoff.
"""

from __future__ import annotations

import logging

from .base import OffenderRecord, ProviderError
from .http import get_json

logger = logging.getLogger(__name__)


class NationalAPIProvider:
    name = "National registry API"
    source_url = "https://www.nsopw.gov"
    attribution = "Data via licensed national registry aggregator"

    def __init__(
        self,
        api_url: str,
        api_key: str,
        zip_param: str = "zip",
        auth_header: str = "X-Api-Key",
        results_key: str = "offenders",
        timeout: float = 10.0,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.zip_param = zip_param
        self.auth_header = auth_header
        self.results_key = results_key
        self.timeout = timeout

    def covers(self, zip_code: str, state: str | None) -> bool:
        # A national aggregator covers anywhere we could resolve to a state.
        return state is not None

    def lookup(self, zip_code: str, state: str | None) -> list[OffenderRecord]:
        payload = get_json(
            self.api_url,
            params={self.zip_param: zip_code},
            headers={self.auth_header: self.api_key},
            timeout=self.timeout,
        )

        rows = payload.get(self.results_key)
        if rows is None and isinstance(payload, list):
            rows = payload
        if rows is None:
            raise ProviderError(
                f"Response had no '{self.results_key}' key; set SAFEZONE_NATIONAL_RESULTS_KEY"
            )

        return [self._to_record(row, zip_code, state) for row in rows]

    def _to_record(self, row: dict, zip_code: str, state: str | None) -> OffenderRecord:
        name = (
            _first(row, "name", "full_name", "offender_name")
            or " ".join(
                p for p in (_first(row, "first_name", "firstName"), _first(row, "last_name", "lastName")) if p
            ).strip()
            or "Name not published"
        )
        return OffenderRecord(
            source_id=str(_first(row, "id", "offender_id", "registry_id") or ""),
            name=name,
            source=self.name,
            source_url=_first(row, "source_url", "url", "profile_url") or self.source_url,
            age=_as_int(_first(row, "age")),
            address=_first(row, "address", "street", "address_line_1"),
            city=_first(row, "city"),
            state=_first(row, "state") or state,
            zip_code=str(_first(row, "zip", "zip_code", "postal_code") or zip_code),
            offense=_first(row, "offense", "offense_type", "crime", "conviction"),
            conviction_date=_first(row, "conviction_date", "convictionDate", "date"),
            lat=_as_float(_first(row, "lat", "latitude")),
            lng=_as_float(_first(row, "lng", "lon", "longitude")),
        )


def _first(row: dict, *keys):
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_float(value):
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if f != 0 else None
