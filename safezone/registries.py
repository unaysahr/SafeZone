"""Official registry destinations, per jurisdiction.

Where SafeZone has no data provider for an area - which is most areas - it
sends the user to the authoritative registry instead of guessing. A
state-scoped NSOPW search always works as a fallback, but linking straight to
the state's own registry is a better destination where we know it.

Adding an entry: only add a URL you have actually opened and confirmed is the
official state registry. A wrong link here sends someone looking for safety
information to the wrong place, and a plausible-looking guess is worse than
the NSOPW fallback, which is always correct.
"""

from __future__ import annotations

from dataclasses import dataclass

NSOPW_SEARCH = "https://www.nsopw.gov/search-public-sex-offender-registries"


@dataclass(frozen=True)
class OfficialRegistry:
    """Where to send a user for authoritative information."""

    name: str
    url: str
    note: str | None = None
    """Jurisdiction-specific caveat the user needs in order to read a result
    correctly - not general boilerplate."""

    def to_dict(self) -> dict:
        return {"name": self.name, "url": self.url, "note": self.note}


# Verified entries only. Everything absent here falls back to NSOPW.
STATE_REGISTRIES: dict[str, OfficialRegistry] = {
    "CA": OfficialRegistry(
        name="California Megan's Law (CA DOJ)",
        url="https://www.meganslaw.ca.gov/",
        note=(
            "California law lets some registrants be excluded from public "
            "disclosure, so this registry is incomplete by design - an empty "
            "result does not mean no registered offenders live in the area. "
            "California also restricts use of this information to protecting "
            "someone at risk."
        ),
    ),
    "NY": OfficialRegistry(
        name="New York State Sex Offender Registry (DCJS)",
        url="https://www.criminaljustice.ny.gov/nsor/",
    ),
    "IA": OfficialRegistry(
        name="Iowa Sex Offender Registry",
        url="https://www.iowasexoffender.gov/",
    ),
    "MS": OfficialRegistry(
        name="Mississippi Sex Offender Registry (MDPS)",
        url="https://state.sor.dps.ms.gov/",
    ),
}


def official_registry(state: str | None) -> OfficialRegistry:
    """Best authoritative destination for a state.

    Falls back to a state-scoped NSOPW search, which covers every US
    jurisdiction, when we have no verified state-specific URL.
    """
    known = STATE_REGISTRIES.get(state) if state else None
    if known:
        return known

    if state:
        return OfficialRegistry(
            name="National Sex Offender Public Website",
            url=f"{NSOPW_SEARCH}?state={state}",
        )

    return OfficialRegistry(
        name="National Sex Offender Public Website",
        url=NSOPW_SEARCH,
    )
