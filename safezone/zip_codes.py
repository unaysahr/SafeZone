"""ZIP code -> US state resolution.

Uses the standard 3-digit ZIP prefix ranges published by the USPS. This is
enough to route a search to the right jurisdiction's registry provider and to
build a correct deep link to the official registry when no provider covers the
area. It deliberately does not attempt to geocode: coordinates come from the
registry providers themselves, never from us.
"""

from __future__ import annotations

# (inclusive_start, inclusive_end, state) over the first three ZIP digits.
_PREFIX_RANGES: list[tuple[int, int, str]] = [
    (5, 5, "NY"), (10, 27, "MA"), (28, 29, "RI"), (30, 38, "NH"),
    (39, 49, "ME"), (50, 54, "VT"), (55, 55, "MA"), (56, 59, "VT"),
    (60, 69, "CT"), (70, 89, "NJ"), (100, 149, "NY"), (150, 196, "PA"),
    (197, 199, "DE"), (200, 200, "DC"), (201, 201, "VA"), (202, 205, "DC"),
    (206, 219, "MD"), (220, 246, "VA"), (247, 268, "WV"), (270, 289, "NC"),
    (290, 299, "SC"), (300, 319, "GA"), (320, 339, "FL"), (341, 342, "FL"),
    (344, 344, "FL"), (346, 347, "FL"), (349, 349, "FL"), (350, 352, "AL"),
    (354, 369, "AL"), (370, 385, "TN"), (386, 397, "MS"), (398, 399, "GA"),
    (400, 427, "KY"), (430, 459, "OH"), (460, 479, "IN"), (480, 499, "MI"),
    (500, 528, "IA"), (530, 549, "WI"), (550, 567, "MN"), (569, 569, "DC"),
    (570, 577, "SD"), (580, 588, "ND"), (590, 599, "MT"), (600, 629, "IL"),
    (630, 658, "MO"), (660, 679, "KS"), (680, 693, "NE"), (700, 701, "LA"),
    (703, 708, "LA"), (710, 714, "LA"), (716, 729, "AR"), (730, 731, "OK"),
    (733, 733, "TX"), (734, 749, "OK"), (750, 799, "TX"), (800, 816, "CO"),
    (820, 831, "WY"), (832, 838, "ID"), (840, 847, "UT"), (850, 850, "AZ"),
    (852, 853, "AZ"), (855, 857, "AZ"), (859, 860, "AZ"), (863, 865, "AZ"),
    (870, 884, "NM"), (885, 885, "TX"), (889, 891, "NV"), (893, 898, "NV"),
    (900, 908, "CA"), (910, 928, "CA"), (930, 961, "CA"), (967, 968, "HI"),
    (970, 979, "OR"), (980, 994, "WA"), (995, 999, "AK"),
]

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DC": "District of Columbia", "DE": "Delaware", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}


def is_valid_zip(zip_code: str) -> bool:
    """True for a syntactically valid 5-digit ZIP code."""
    return isinstance(zip_code, str) and len(zip_code) == 5 and zip_code.isdigit()


def state_for_zip(zip_code: str) -> str | None:
    """Return the 2-letter state for a ZIP, or None if it maps to no state.

    Roughly 4% of the 00000-99999 space is unassigned; those return None
    rather than being guessed at.
    """
    if not is_valid_zip(zip_code):
        return None
    prefix = int(zip_code[:3])
    for start, end, state in _PREFIX_RANGES:
        if start <= prefix <= end:
            return state
    return None


def state_name(code: str | None) -> str | None:
    return STATE_NAMES.get(code) if code else None
