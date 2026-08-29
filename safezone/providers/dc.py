"""District of Columbia - Open Data DC (ArcGIS REST).

Free, no API key. MPD publishes the DC registry as a hosted feature layer.
Docs: https://opendata.dc.gov/datasets/sex-offender-registry
"""

from __future__ import annotations

import logging

from .base import OffenderRecord, ProviderError
from .http import get_json

logger = logging.getLogger(__name__)

# Open Data DC hosted feature layer. Override via SAFEZONE_DC_LAYER_URL if the
# layer id is rotated - ArcGIS item ids are not guaranteed stable forever.
DEFAULT_LAYER_URL = (
    "https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/MPD/MapServer/6/query"
)


class DCProvider:
    name = "Open Data DC (Metropolitan Police Department)"
    source_url = "https://opendata.dc.gov/datasets/sex-offender-registry"
    attribution = "Data: Open Data DC / DC Metropolitan Police Department"

    def __init__(self, layer_url: str = DEFAULT_LAYER_URL, timeout: float = 10.0):
        self.layer_url = layer_url
        self.timeout = timeout

    def covers(self, zip_code: str, state: str | None) -> bool:
        return state == "DC"

    def lookup(self, zip_code: str, state: str | None) -> list[OffenderRecord]:
        params = {
            "where": f"ZIP='{zip_code}'",
            "outFields": "*",
            "outSR": "4326",
            "f": "json",
            "resultRecordCount": "200",
        }
        payload = get_json(self.layer_url, params=params, timeout=self.timeout)

        if "error" in payload:
            raise ProviderError(f"ArcGIS error: {payload['error']}")

        features = payload.get("features") or []
        return [self._to_record(f, zip_code) for f in features]

    def _to_record(self, feature: dict, zip_code: str) -> OffenderRecord:
        attrs = feature.get("attributes") or {}
        geom = feature.get("geometry") or {}

        first = (attrs.get("FIRSTNAME") or "").strip()
        last = (attrs.get("LASTNAME") or "").strip()
        name = " ".join(p for p in (first, last) if p) or "Name not published"

        return OffenderRecord(
            source_id=str(attrs.get("OBJECTID") or attrs.get("REGISTRYID") or ""),
            name=name,
            source=self.name,
            source_url=self.source_url,
            address=(attrs.get("BLOCKSITEADDRESS") or attrs.get("ADDRESS") or None),
            city="Washington",
            state="DC",
            zip_code=str(attrs.get("ZIP") or zip_code),
            offense=(attrs.get("OFFENSE") or attrs.get("CLASSIFICATION") or None),
            lat=_coord(geom.get("y")),
            lng=_coord(geom.get("x")),
        )


def _coord(value) -> float | None:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if f != 0 else None
