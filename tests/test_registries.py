from urllib.parse import urlsplit

import pytest

from safezone.registries import STATE_REGISTRIES, official_registry


def test_known_state_returns_its_own_registry():
    ca = official_registry("CA")
    assert "meganslaw.ca.gov" in ca.url
    assert "California" in ca.name


def test_unknown_state_falls_back_to_state_scoped_nsopw():
    il = official_registry("IL")
    assert "nsopw.gov" in il.url
    assert il.url.endswith("?state=IL")
    assert il.note is None


def test_unresolvable_state_falls_back_to_national_search():
    result = official_registry(None)
    assert "nsopw.gov" in result.url
    assert "state=" not in result.url


def test_california_note_warns_the_listing_is_incomplete():
    """CA excludes some registrants by law, so 'none listed' is not 'none present'."""
    note = official_registry("CA").note
    assert note is not None
    assert "incomplete" in note.lower()


def test_only_california_carries_a_note_today():
    noted = {code for code, reg in STATE_REGISTRIES.items() if reg.note}
    assert noted == {"CA"}


@pytest.mark.parametrize("code,registry", sorted(STATE_REGISTRIES.items()))
def test_seeded_entries_are_well_formed(code, registry):
    parts = urlsplit(registry.url)
    assert parts.scheme == "https", f"{code} must use https"
    assert parts.netloc, f"{code} needs a host"
    assert registry.name.strip(), f"{code} needs a display name"


def test_every_state_gets_a_usable_destination():
    from safezone.zip_codes import STATE_NAMES

    for code in STATE_NAMES:
        registry = official_registry(code)
        assert registry.url.startswith("https://")
        assert registry.name.strip()


def test_to_dict_shape():
    assert set(official_registry("CA").to_dict()) == {"name", "url", "note"}
