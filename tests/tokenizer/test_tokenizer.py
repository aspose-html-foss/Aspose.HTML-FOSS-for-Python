"""Main tokeniser integration tests —  acceptance criteria.

Covers AC-1 through AC-11 plus structural/generator tests.
"""
from __future__ import annotations

import doctest
import types
import pytest

from aspose_html.tokenizer import (
    Tokenizer,
    TokenizerState,
    DoctypeToken,
    StartTagToken,
    EndTagToken,
    CommentToken,
    CharacterToken,
    EofToken,
)
import aspose_html.tokenizer._tokens as _tokens_mod
import aspose_html.tokenizer._states as _states_mod
import aspose_html.tokenizer._tokenizer as _tokenizer_mod


# ---------------------------------------------------------------------------
# AC-1: Attribute order preserved
# ---------------------------------------------------------------------------

def test_start_tag_attribute_order() -> None:
    """AC-1: <div class="foo" id="bar"> preserves attribute order."""
    tokens = list(Tokenizer('<div class="foo" id="bar">').tokenize())
    start = tokens[0]
    assert isinstance(start, StartTagToken)
    assert start.tag_name == "div"
    assert start.attributes == (("class", "foo"), ("id", "bar"))


# ---------------------------------------------------------------------------
# AC-2: End tag token
# ---------------------------------------------------------------------------

def test_end_tag_token() -> None:
    """AC-2: </div> → EndTagToken(tag_name='div')."""
    tokens = list(Tokenizer("</div>").tokenize())
    end = tokens[0]
    assert isinstance(end, EndTagToken)
    assert end.tag_name == "div"


# ---------------------------------------------------------------------------
# AC-3: DOCTYPE token
# ---------------------------------------------------------------------------

def test_doctype_html() -> None:
    """AC-3: <!DOCTYPE html> → DoctypeToken."""
    tokens = list(Tokenizer("<!DOCTYPE html>").tokenize())
    doctype = tokens[0]
    assert isinstance(doctype, DoctypeToken)
    assert doctype.name == "html"
    assert doctype.public_id is None
    assert doctype.system_id is None
    assert doctype.force_quirks is False


# ---------------------------------------------------------------------------
# AC-4: Comment token
# ---------------------------------------------------------------------------

def test_comment_token() -> None:
    """AC-4: <!-- comment --> → CommentToken(data=' comment ')."""
    tokens = list(Tokenizer("<!-- comment -->").tokenize())
    comment = tokens[0]
    assert isinstance(comment, CommentToken)
    assert comment.data == " comment "


# ---------------------------------------------------------------------------
# AC-8: Script data state (state injection)
# ---------------------------------------------------------------------------

def test_script_data_state() -> None:
    """AC-8: <script> content is CharacterToken data after state injection."""
    tok = Tokenizer("<script>if (x < y)</script>")
    gen = tok.tokenize()
    script_start = next(gen)
    assert isinstance(script_start, StartTagToken)
    assert script_start.tag_name == "script"

    # Tree constructor would inject SCRIPT_DATA here
    tok.set_state(TokenizerState.SCRIPT_DATA)

    tokens = list(gen)
    # Collect all character data
    char_data = "".join(
        t.data for t in tokens if isinstance(t, CharacterToken)
    )
    assert "if (x < y)" in char_data
    # The '<' inside the script must not be parsed as a tag
    tag_names = [t.tag_name for t in tokens if isinstance(t, (StartTagToken, EndTagToken))]
    # Only the closing </script> should appear as a tag
    assert tag_names == ["script"]


# ---------------------------------------------------------------------------
# EOF token is always last
# ---------------------------------------------------------------------------

def test_eof_token_is_last() -> None:
    """The last token from any tokenize call is always EofToken."""
    for html in ("", "<p>", "text", "<!DOCTYPE html><html>"):
        tokens = list(Tokenizer(html).tokenize())
        assert isinstance(tokens[-1], EofToken), f"Failed for: {html!r}"


# ---------------------------------------------------------------------------
# Self-closing flag
# ---------------------------------------------------------------------------

def test_self_closing_flag() -> None:
    """<br/> → StartTagToken(self_closing=True)."""
    tokens = list(Tokenizer("<br/>").tokenize())
    br = tokens[0]
    assert isinstance(br, StartTagToken)
    assert br.self_closing is True


# ---------------------------------------------------------------------------
# Empty string
# ---------------------------------------------------------------------------

def test_empty_string() -> None:
    """Tokenizer('').tokenize() yields only EofToken."""
    tokens = list(Tokenizer("").tokenize())
    assert len(tokens) == 1
    assert isinstance(tokens[0], EofToken)


# ---------------------------------------------------------------------------
# AC-10: No exception on invalid HTML
# ---------------------------------------------------------------------------

def test_no_exception_on_invalid_html() -> None:
    """AC-10: broken HTML does not raise exceptions."""
    broken_inputs = [
        "<",
        ">",
        "</",
        "<!",
        "<!--",
        "<!DOCTYPE",
        "<div id=",
        "<div id='",
        '&amp',
        "&#;",
        "&#x;",
        "<\x00>",
        "< invalid>",
        "<?xml?>",
        "<br id='a' id='b'>",
    ]
    for html in broken_inputs:
        try:
            tokens = list(Tokenizer(html).tokenize())
            assert any(isinstance(t, EofToken) for t in tokens), \
                f"No EofToken for: {html!r}"
        except Exception as exc:
            pytest.fail(f"Exception for {html!r}: {exc}")


# ---------------------------------------------------------------------------
# Line/column tracking
# ---------------------------------------------------------------------------

def test_line_column_tracking() -> None:
    """Multi-line input produces tokens with correct line/column fields."""
    html = "<p>\nHello\n</p>"
    tokens = list(Tokenizer(html).tokenize())

    start = tokens[0]
    assert isinstance(start, StartTagToken)
    assert start.line == 1

    end_tags = [t for t in tokens if isinstance(t, EndTagToken)]
    assert end_tags
    # </p> is on line 3
    assert end_tags[0].line == 3


# ---------------------------------------------------------------------------
# set_state changes tokenizer state
# ---------------------------------------------------------------------------

def test_set_state_changes_tokenizer_state() -> None:
    """set_state(RAWTEXT) changes tok.state."""
    tok = Tokenizer("<style>")
    assert tok.state == TokenizerState.DATA
    tok.set_state(TokenizerState.RAWTEXT)
    assert tok.state == TokenizerState.RAWTEXT


# ---------------------------------------------------------------------------
# tokenize() returns a generator
# ---------------------------------------------------------------------------

def test_tokenize_is_generator() -> None:
    """tokenize() returns a generator, not a list."""
    import types as _types
    tok = Tokenizer("<p>")
    gen = tok.tokenize()
    assert isinstance(gen, _types.GeneratorType)


# ---------------------------------------------------------------------------
# Character buffering
# ---------------------------------------------------------------------------

def test_character_buffering() -> None:
    """Consecutive characters in data state are buffered into one CharacterToken."""
    tokens = list(Tokenizer("Hello World").tokenize())
    char_tokens = [t for t in tokens if isinstance(t, CharacterToken)]
    # All text should be in a small number of tokens (not 11 individual ones)
    total = "".join(t.data for t in char_tokens)
    assert total == "Hello World"
    # Should be 1 or 2 tokens at most (buffering)
    assert len(char_tokens) <= 2


# ---------------------------------------------------------------------------
# Nested tags — no exception
# ---------------------------------------------------------------------------

def test_nested_tags_no_exception() -> None:
    """Deeply nested tags tokenise without exception."""
    depth = 100
    html = "<div>" * depth + "x" + "</div>" * depth
    tokens = list(Tokenizer(html).tokenize())
    assert isinstance(tokens[-1], EofToken)


# ---------------------------------------------------------------------------
# AC-11: Docstring examples pass doctest
# ---------------------------------------------------------------------------

def test_public_api_doctest() -> None:
    """AC-11: all docstring examples in the tokenizer modules pass."""
    results = doctest.testmod(_tokens_mod, verbose=False)
    assert results.failed == 0, f"_tokens.py doctests: {results.failed} failures"

    results = doctest.testmod(_states_mod, verbose=False)
    assert results.failed == 0, f"_states.py doctests: {results.failed} failures"

    results = doctest.testmod(_tokenizer_mod, verbose=False)
    assert results.failed == 0, f"_tokenizer.py doctests: {results.failed} failures"


# ---------------------------------------------------------------------------
# Tag name lowercasing
# ---------------------------------------------------------------------------

def test_tag_name_lowercased() -> None:
    """Tag names are lowercased per WHATWG spec."""
    tokens = list(Tokenizer("<DIV>text</DIV>").tokenize())
    start = tokens[0]
    assert isinstance(start, StartTagToken)
    assert start.tag_name == "div"
    end = [t for t in tokens if isinstance(t, EndTagToken)][0]
    assert end.tag_name == "div"


# ---------------------------------------------------------------------------
# Full document
# ---------------------------------------------------------------------------

def test_full_document_sequence() -> None:
    """<!DOCTYPE html><html><head></head><body><p>Hi</p></body></html>"""
    html = "<!DOCTYPE html><html><head></head><body><p>Hi</p></body></html>"
    tokens = list(Tokenizer(html).tokenize())
    assert isinstance(tokens[0], DoctypeToken)
    tag_names = [t.tag_name for t in tokens if isinstance(t, StartTagToken)]
    assert "html" in tag_names
    assert "p" in tag_names
