"""Tests for TokenizerState enum — ADR-002 test strategy."""
from __future__ import annotations

from aspose_html.tokenizer import TokenizerState


def test_state_enum_has_data() -> None:
    """TokenizerState.DATA exists and is an integer."""
    assert TokenizerState.DATA == 0
    assert isinstance(TokenizerState.DATA, int)


def test_state_enum_count() -> None:
    """At least 80 members — guards against accidental deletion (INV-004)."""
    assert len(TokenizerState) >= 80


def test_state_enum_names_match_spec() -> None:
    """Spot-check 10 state names against WHATWG §13.2.5 names."""
    expected = [
        "DATA",
        "RCDATA",
        "RAWTEXT",
        "SCRIPT_DATA",
        "PLAINTEXT",
        "TAG_OPEN",
        "TAG_NAME",
        "BEFORE_ATTRIBUTE_NAME",
        "ATTRIBUTE_NAME",
        "COMMENT",
    ]
    names = {s.name for s in TokenizerState}
    for name in expected:
        assert name in names, f"Missing state: {name}"


def test_state_enum_character_reference_states() -> None:
    """Character reference states from §13.2.5.72–80 exist."""
    cr_states = [
        "CHARACTER_REFERENCE",
        "NAMED_CHARACTER_REFERENCE",
        "AMBIGUOUS_AMPERSAND",
        "NUMERIC_CHARACTER_REFERENCE",
        "HEXADECIMAL_CHARACTER_REFERENCE_START",
        "DECIMAL_CHARACTER_REFERENCE_START",
        "HEXADECIMAL_CHARACTER_REFERENCE",
        "DECIMAL_CHARACTER_REFERENCE",
        "NUMERIC_CHARACTER_REFERENCE_END",
    ]
    names = {s.name for s in TokenizerState}
    for name in cr_states:
        assert name in names, f"Missing char ref state: {name}"


def test_state_enum_values_are_ints() -> None:
    """All states are integer-valued (IntEnum)."""
    for state in TokenizerState:
        assert isinstance(state, int)
