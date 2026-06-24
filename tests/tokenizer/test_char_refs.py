"""Character reference resolver unit tests —  test strategy.

Covers AC-5, AC-6, and unit tests for resolve_named_char_ref,
resolve_numeric_char_ref, and the NAMED_CHAR_REFS table.
"""
from __future__ import annotations

from aspose_html.tokenizer import Tokenizer, CharacterToken
from aspose_html.tokenizer._char_refs import (
    resolve_named_char_ref,
    resolve_numeric_char_ref,
)
from aspose_html.tokenizer._char_ref_data import NAMED_CHAR_REFS


# ---------------------------------------------------------------------------
# AC-5: Named character reference in data state
# ---------------------------------------------------------------------------

def test_named_char_ref_amp_in_data() -> None:
    """AC-5: &amp; in data → CharacterToken('&')."""
    tokens = list(Tokenizer("&amp;").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    data = "".join(t.data for t in char_tokens)
    assert data == "&"


def test_named_char_ref_lt() -> None:
    """&lt; in data → CharacterToken('<')."""
    tokens = list(Tokenizer("&lt;").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    data = "".join(t.data for t in char_tokens)
    assert data == "<"


def test_named_char_ref_gt() -> None:
    """&gt; in data → CharacterToken('>')."""
    tokens = list(Tokenizer("&gt;").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    data = "".join(t.data for t in char_tokens)
    assert data == ">"


# ---------------------------------------------------------------------------
# AC-6: Numeric character references
# ---------------------------------------------------------------------------

def test_numeric_hex_char_ref() -> None:
    """AC-6: &#x1F600; → CharacterToken('😀')."""
    tokens = list(Tokenizer("&#x1F600;").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    data = "".join(t.data for t in char_tokens)
    assert data == "\U0001F600"


def test_numeric_decimal_char_ref() -> None:
    """&#38; → CharacterToken('&')."""
    tokens = list(Tokenizer("&#38;").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    data = "".join(t.data for t in char_tokens)
    assert data == "&"


def test_numeric_hex_char_ref_uppercase() -> None:
    """&#X41; → CharacterToken('A') — uppercase X."""
    tokens = list(Tokenizer("&#X41;").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    data = "".join(t.data for t in char_tokens)
    assert data == "A"


def test_numeric_decimal_char_ref_65() -> None:
    """&#65; → CharacterToken('A')."""
    tokens = list(Tokenizer("&#65;").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    data = "".join(t.data for t in char_tokens)
    assert data == "A"


def test_hex_char_ref_lowercase() -> None:
    """&#x41; → CharacterToken('A')."""
    tokens = list(Tokenizer("&#x41;").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    data = "".join(t.data for t in char_tokens)
    assert data == "A"


# ---------------------------------------------------------------------------
# Unit tests for resolve_named_char_ref
# ---------------------------------------------------------------------------

def test_resolve_named_char_ref_amp() -> None:
    """resolve_named_char_ref('amp;') == '&'."""
    result = resolve_named_char_ref("amp;")
    assert result == "&"


def test_resolve_named_char_ref_lt() -> None:
    """resolve_named_char_ref('lt;') == '<'."""
    result = resolve_named_char_ref("lt;")
    assert result == "<"


def test_resolve_named_char_ref_unknown() -> None:
    """resolve_named_char_ref with unknown name returns None."""
    result = resolve_named_char_ref("notAName")
    assert result is None


def test_resolve_named_char_ref_case_sensitive() -> None:
    """Named char refs table matches WHATWG html5 table exactly.

    The WHATWG table (via Python html.entities.html5) includes legacy
    case variants like AMP; for backward compatibility — these are valid.
    Truly unknown names must return None.
    """
    assert resolve_named_char_ref("amp;") == "&"
    # WHATWG html5 table includes AMP; as a legacy entry
    assert resolve_named_char_ref("AMP;") == "&"
    # Completely unknown names return None
    assert resolve_named_char_ref("NOTANENTITY;") is None
    assert resolve_named_char_ref("xyzzy;") is None


# ---------------------------------------------------------------------------
# Unit tests for resolve_numeric_char_ref
# ---------------------------------------------------------------------------

def test_resolve_numeric_null_char_ref() -> None:
    """resolve_numeric_char_ref(0) returns replacement char and error."""
    char, errs = resolve_numeric_char_ref(0)
    assert errs == ["null-character-reference"]
    assert char == "\uFFFD"


def test_resolve_numeric_surrogate_char_ref() -> None:
    """resolve_numeric_char_ref(0xD800) returns replacement and error."""
    char, errs = resolve_numeric_char_ref(0xD800)
    assert "surrogate-character-reference" in errs
    assert char == "\uFFFD"


def test_resolve_numeric_out_of_range() -> None:
    """resolve_numeric_char_ref(0x10FFFF + 1) returns replacement and error."""
    char, errs = resolve_numeric_char_ref(0x110000)
    assert "character-reference-outside-unicode-range" in errs
    assert char == "\uFFFD"


def test_resolve_numeric_normal_code_point() -> None:
    """resolve_numeric_char_ref(65) returns ('A', [])."""
    char, errs = resolve_numeric_char_ref(65)
    assert char == "A"
    assert errs == []


def test_resolve_numeric_amp_code_point() -> None:
    """resolve_numeric_char_ref(38) returns ('&', [])."""
    char, errs = resolve_numeric_char_ref(38)
    assert char == "&"
    assert errs == []


# ---------------------------------------------------------------------------
# NAMED_CHAR_REFS table size —  compliance
# ---------------------------------------------------------------------------

def test_named_char_ref_table_size() -> None:
    """len(NAMED_CHAR_REFS) >= 2000 — guards against truncated table."""
    # Python's html.entities.html5 contains all WHATWG entities
    assert len(NAMED_CHAR_REFS) >= 2000, (
        f"NAMED_CHAR_REFS has only {len(NAMED_CHAR_REFS)} entries — "
        "table appears truncated"
    )


def test_named_char_ref_table_has_basic_entries() -> None:
    """The table contains the most common HTML entities."""
    required = ["amp;", "lt;", "gt;", "quot;", "nbsp;"]
    for name in required:
        assert name in NAMED_CHAR_REFS, f"Missing required entity: {name!r}"


def test_named_char_ref_table_values_are_strings() -> None:
    """All values in NAMED_CHAR_REFS are non-empty strings."""
    for key, val in NAMED_CHAR_REFS.items():
        assert isinstance(val, str), f"Value for {key!r} is not a str"
        assert len(val) >= 1, f"Empty value for {key!r}"
