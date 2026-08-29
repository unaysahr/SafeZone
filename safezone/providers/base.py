"""Provider interface for registry lookups.

Design rule, and the reason this module exists: a provider either returns
records it actually received from an official or licensed source, or it
raises / declines coverage. There is no code path anywhere in this package
that synthesises an offender record. Falsely associating a real address with
a sex offence is defamatory and dangerous, so "we don't know" must always be
representable and must never degrade into a fabricated answer.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from typing import Protocol

logger = logging.getLogger(__name__)


class ProviderError(RuntimeError):
    """The provider was reachable in principle but the lookup failed."""


@dataclass(frozen=True)
class OffenderRecord:
    """One registry record, normalised across providers.

    Every field is optional except those the source actually supplied. Missing
    data stays missing - it is never filled with a plausible-looking default.
    """

    source_id: str
    name: str
    source: str
    source_url: str | None = None
    age: int | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    offense: str | None = None
    conviction_date: str | None = None
    lat: float | None = None
    lng: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LookupResult:
    """Outcome of a ZIP lookup.

    ``covered`` False means no provider serves this jurisdiction - the app
    must then hand the user off to the official registry rather than guess.
    """

    zip_code: str
    covered: bool
    records: list[OffenderRecord] = field(default_factory=list)
    source: str | None = None
    source_url: str | None = None
    attribution: str | None = None
    state: str | None = None
    degraded: bool = False
    """True when a provider does serve this area but the lookup failed.

    Distinguishes "we have no source for Illinois" from "our DC source is
    down right now" - the user needs different advice in each case."""

    @property
    def count(self) -> int:
        return len(self.records)

    def to_dict(self) -> dict:
        return {
            "zip_code": self.zip_code,
            "covered": self.covered,
            "count": self.count,
            "has_offenders": self.covered and self.count > 0,
            "offenders": [r.to_dict() for r in self.records],
            "source": self.source,
            "source_url": self.source_url,
            "attribution": self.attribution,
            "state": self.state,
            "degraded": self.degraded,
        }


class RegistryProvider(Protocol):
    """A source of real registry records for some set of jurisdictions."""

    name: str
    source_url: str
    attribution: str

    def covers(self, zip_code: str, state: str | None) -> bool:
        """True if this provider can authoritatively answer for this ZIP."""
        ...

    def lookup(self, zip_code: str, state: str | None) -> list[OffenderRecord]:
        """Return real records, or raise ProviderError. Never fabricates."""
        ...


def nsopw_search_url(state: str | None = None) -> str:
    """Deep link to the official national registry search.

    Used whenever we cannot answer authoritatively. NSOPW has no public API,
    so handing the user to the real search is the honest fallback.
    """
    base = "https://www.nsopw.gov/search-public-sex-offender-registries"
    return f"{base}?state={state}" if state else base
