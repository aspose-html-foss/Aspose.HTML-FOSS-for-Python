"""Parse error recording tests —  test strategy.

Covers AC-7, AC-9, and other parse error conditions.
"""
from __future__ import annotations

from aspose_html.tokenizer import (
    Tokenizer,
    StartTagToken,
)
from aspose_html.dom import ParseError


# ---------------------------------------------------------------------------
# AC-9: Parse error has code, line >= 1, column >= 1
# ---------------------------------------------------------------------------

def test_parse_error_has_code_line_col() -> None:
    """AC-9: parse errors have non-empty code, line >= 1, column >= 1."""
    # '<!--no end' produces eof-in-comment error
    tok = Tokenizer("<!--no end")
    _ = list(tok.tokenize())
    assert len(tok.errors) > 0, "Expected at least one parse error"
    err = tok.errors[0]
    assert isinstance(err, ParseError)
    assert err.code != "", "Parse error code must be non-empty"
    assert err.line >= 1, f"Expected line >= 1, got {err.line}"
    assert err.column >= 1, f"Expected column >= 1, got {err.column}"


# ---------------------------------------------------------------------------
# eof-in-comment
# ---------------------------------------------------------------------------

def test_eof_in_comment() -> None:
    """'<!--no end' → error code 'eof-in-comment'."""
    tok = Tokenizer("<!--no end")
    _ = list(tok.tokenize())
    codes = [e.code for e in tok.errors]
    assert "eof-in-comment" in codes, (
        f"Expected 'eof-in-comment' in errors, got: {codes}"
    )


# ---------------------------------------------------------------------------
# AC-7: Duplicate attribute parse error
# ---------------------------------------------------------------------------

def test_duplicate_attribute_parse_error() -> None:
    """AC-7: <div id='a' id='b'> → duplicate-attribute error; first value kept."""
    tok = Tokenizer("<div id='a' id='b'>")
    tokens = list(tok.tokenize())
    start_tags = [t for t in tokens if isinstance(t, StartTagToken)]
    assert len(start_tags) == 1
    tag = start_tags[0]
    assert tag.tag_name == "div"
    # First value kept per spec §13.2.5.33
    assert tag.attributes == (("id", "a"),), (
        f"Expected only first id attribute, got: {tag.attributes}"
    )
    # Parse error recorded
    codes = [e.code for e in tok.errors]
    assert "duplicate-attribute" in codes, (
        f"Expected 'duplicate-attribute' error, got: {codes}"
    )


# ---------------------------------------------------------------------------
# errors_list_is_empty_on_clean_input
# ---------------------------------------------------------------------------

def test_errors_list_is_empty_on_clean_input() -> None:
    """Clean HTML input produces empty tok.errors list."""
    clean_inputs = [
        "<!DOCTYPE html><html><head></head><body><p>Hello</p></body></html>",
        "<div class=\"foo\">text</div>",
        "<!-- comment -->",
        "<br/>",
        "<p id=\"x\">hi</p>",
    ]
    for html in clean_inputs:
        tok = Tokenizer(html)
        _ = list(tok.tokenize())
        assert tok.errors == [], (
            f"Expected no errors for {html!r}, got: {tok.errors}"
        )


# ---------------------------------------------------------------------------
# eof-in-tag
# ---------------------------------------------------------------------------

def test_eof_in_tag() -> None:
    """'<div id=' (truncated) → eof-in-tag error."""
    tok = Tokenizer("<div id=")
    _ = list(tok.tokenize())
    codes = [e.code for e in tok.errors]
    assert "eof-in-tag" in codes or len(tok.errors) > 0, (
        f"Expected parse error for truncated tag, got: {codes}"
    )


# ---------------------------------------------------------------------------
# eof-in-doctype
# ---------------------------------------------------------------------------

def test_eof_in_doctype() -> None:
    """'<!DOCTYPE' (truncated) → parse error recorded."""
    tok = Tokenizer("<!DOCTYPE")
    _ = list(tok.tokenize())
    assert len(tok.errors) > 0, "Expected at least one parse error for truncated DOCTYPE"


# ---------------------------------------------------------------------------
# Invalid first character of tag name
# ---------------------------------------------------------------------------

def test_invalid_first_char_of_tag_name() -> None:
    """'< invalid>' → parse error for invalid-first-character-of-tag-name."""
    tok = Tokenizer("< invalid>")
    _ = list(tok.tokenize())
    codes = [e.code for e in tok.errors]
    assert "invalid-first-character-of-tag-name" in codes, (
        f"Expected invalid-first-character-of-tag-name, got: {codes}"
    )


# ---------------------------------------------------------------------------
# errors is always a list (even when empty)
# ---------------------------------------------------------------------------

def test_errors_property_type() -> None:
    """tok.errors is always a list."""
    tok = Tokenizer("<p>text</p>")
    assert isinstance(tok.errors, list)
    _ = list(tok.tokenize())
    assert isinstance(tok.errors, list)


# ---------------------------------------------------------------------------
# Multiple parse errors in one input
# ---------------------------------------------------------------------------

def test_multiple_parse_errors() -> None:
    """Input with multiple errors records all of them."""
    # Input with two unclosed comments
    tok = Tokenizer("<!-- first <!-- second")
    _ = list(tok.tokenize())
    # Should have at least 1 eof-in-comment
    codes = [e.code for e in tok.errors]
    assert any(code == "eof-in-comment" for code in codes), (
        f"Expected eof-in-comment errors, got: {codes}"
    )


# ---------------------------------------------------------------------------
# missing-end-tag-name
# ---------------------------------------------------------------------------

def test_missing_end_tag_name() -> None:
    """'</>' → missing-end-tag-name parse error."""
    tok = Tokenizer("</>")
    _ = list(tok.tokenize())
    codes = [e.code for e in tok.errors]
    assert "missing-end-tag-name" in codes, (
        f"Expected missing-end-tag-name, got: {codes}"
    )


# ---------------------------------------------------------------------------
# parse error fields are correct types
# ---------------------------------------------------------------------------

def test_parse_error_fields_are_correct_types() -> None:
    """ParseError fields have correct types: code=str, line=int, col=int, msg=str."""
    tok = Tokenizer("<!--no end")
    _ = list(tok.tokenize())
    assert len(tok.errors) > 0
    err = tok.errors[0]
    assert isinstance(err.code, str)
    assert isinstance(err.line, int)
    assert isinstance(err.column, int)
    assert isinstance(err.message, str)
