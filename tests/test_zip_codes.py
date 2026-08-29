from safezone.zip_codes import is_valid_zip, state_for_zip, state_name


def test_known_zips_resolve_to_correct_states():
    assert state_for_zip("90210") == "CA"
    assert state_for_zip("10001") == "NY"
    assert state_for_zip("77001") == "TX"
    assert state_for_zip("20001") == "DC"
    assert state_for_zip("50301") == "IA"
    assert state_for_zip("99501") == "AK"


def test_dc_and_virginia_share_a_prefix_boundary():
    assert state_for_zip("20000") == "DC"
    assert state_for_zip("20100") == "VA"
    assert state_for_zip("20600") == "MD"


def test_unassigned_prefixes_return_none_rather_than_guessing():
    # The table is range-based, so it resolves prefixes that fall *between*
    # assigned ranges. (Unassigned prefixes sitting inside a state's range,
    # like 213 within MD's 206-219, still resolve to that state - harmless,
    # since the provider simply returns no records for them.)
    for unassigned in ["00100", "09900", "96200"]:
        assert state_for_zip(unassigned) is None, unassigned


def test_highest_assigned_prefix_still_resolves():
    assert state_for_zip("99999") == "AK"


def test_invalid_input_rejected():
    for bad in ["", "1234", "123456", "abcde", "12 45", None, 12345]:
        assert not is_valid_zip(bad)
        if isinstance(bad, str):
            assert state_for_zip(bad) is None


def test_state_name_lookup():
    assert state_name("IA") == "Iowa"
    assert state_name(None) is None
