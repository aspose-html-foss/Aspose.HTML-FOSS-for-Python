"""Fragment tokenisation tests — ADR-002 test strategy.

Tests Tokenizer.tokenize_fragment() per WHATWG §13.2.6 initial state rules.
"""
from __future__ import annotations

from aspose_html.tokenizer import (
    Tokenizer,
    StartTagToken,
    EndTagToken,
    CharacterToken,
    EofToken,
)


# ---------------------------------------------------------------------------
# test_fragment_div_context
# ---------------------------------------------------------------------------

def test_fragment_div_context() -> None:
    """tokenize_fragment('div', '<b>Hi</b>') → StartTag, Char, EndTag, Eof."""
    tokens = list(Tokenizer.tokenize_fragment("div", "<b>Hi</b>"))
    start_tags = [t for t in tokens if isinstance(t, StartTagToken)]
    end_tags = [t for t in tokens if isinstance(t, EndTagToken)]
    chars = [t for t in tokens if isinstance(t, CharacterToken)]

    assert any(t.tag_name == "b" for t in start_tags), "Expected <b> start tag"
    assert any(t.tag_name == "b" for t in end_tags), "Expected </b> end tag"
    char_data = "".join(t.data for t in chars)
    assert "Hi" in char_data
    assert isinstance(tokens[-1], EofToken)


def test_fragment_div_initial_state() -> None:
    """tokenize_fragment('div', ...) starts in DATA state — tags parsed normally."""
    # Fragment with div context should use DATA state
    # Verify by checking that tags are parsed as tags, not text
    tokens = list(Tokenizer.tokenize_fragment("div", "<p>text</p>"))
    start_tags = [t for t in tokens if isinstance(t, StartTagToken)]
    assert any(t.tag_name == "p" for t in start_tags)


# ---------------------------------------------------------------------------
# test_fragment_textarea_context
# ---------------------------------------------------------------------------

def test_fragment_textarea_context() -> None:
    """tokenize_fragment('textarea', '<b>Hi</b>') → RCDATA: <b> is text."""
    tokens = list(Tokenizer.tokenize_fragment("textarea", "<b>Hi</b>"))
    # In RCDATA state, < does not start a real tag (unless it's the appropriate
    # end tag). So <b> should appear as character data, not a StartTagToken.
    start_tags = [t for t in tokens if isinstance(t, StartTagToken)]
    # No start tags for 'b' should be emitted in RCDATA
    b_starts = [t for t in start_tags if t.tag_name == "b"]
    assert len(b_starts) == 0, (
        "In RCDATA context, <b> should not produce a StartTagToken"
    )
    # The text should appear as character data
    chars = [t for t in tokens if isinstance(t, CharacterToken)]
    char_data = "".join(t.data for t in chars)
    assert "Hi" in char_data or "<b>" in char_data


# ---------------------------------------------------------------------------
# test_fragment_script_context
# ---------------------------------------------------------------------------

def test_fragment_script_context() -> None:
    """tokenize_fragment('script', 'x < y') → CharacterToken data."""
    tokens = list(Tokenizer.tokenize_fragment("script", "x < y"))
    # In SCRIPT_DATA state, < is treated as literal text
    chars = [t for t in tokens if isinstance(t, CharacterToken)]
    char_data = "".join(t.data for t in chars)
    # The literal text 'x < y' should appear as character data
    assert "<" in char_data or "x" in char_data
    # No tags should be emitted
    tag_tokens = [t for t in tokens if isinstance(t, (StartTagToken, EndTagToken))]
    assert len(tag_tokens) == 0


# ---------------------------------------------------------------------------
# test_fragment_title_context
# ---------------------------------------------------------------------------

def test_fragment_title_context() -> None:
    """tokenize_fragment('title', ...) starts in RCDATA state."""
    # title elements use RCDATA — same as textarea
    tokens = list(Tokenizer.tokenize_fragment("title", "Hello <b>world</b>"))
    start_tags = [t for t in tokens if isinstance(t, StartTagToken)]
    b_starts = [t for t in start_tags if t.tag_name == "b"]
    assert len(b_starts) == 0, (
        "In RCDATA context (title), <b> should not produce a StartTagToken"
    )


# ---------------------------------------------------------------------------
# test_fragment_style_context
# ---------------------------------------------------------------------------

def test_fragment_style_context() -> None:
    """tokenize_fragment('style', 'a { color: red }') → CharacterToken data."""
    tokens = list(Tokenizer.tokenize_fragment("style", "a { color: red }"))
    chars = [t for t in tokens if isinstance(t, CharacterToken)]
    char_data = "".join(t.data for t in chars)
    assert "color" in char_data


# ---------------------------------------------------------------------------
# test_fragment_unknown_context
# ---------------------------------------------------------------------------

def test_fragment_unknown_context() -> None:
    """tokenize_fragment('span', ...) falls back to DATA state."""
    tokens = list(Tokenizer.tokenize_fragment("span", "<em>text</em>"))
    start_tags = [t for t in tokens if isinstance(t, StartTagToken)]
    assert any(t.tag_name == "em" for t in start_tags)


# ---------------------------------------------------------------------------
# test_fragment_eof
# ---------------------------------------------------------------------------

def test_fragment_always_ends_with_eof() -> None:
    """tokenize_fragment always yields EofToken as the last token."""
    for element, text in [
        ("div", "<p>hi</p>"),
        ("script", "var x = 1;"),
        ("textarea", "some text"),
        ("title", "Page Title"),
    ]:
        tokens = list(Tokenizer.tokenize_fragment(element, text))
        assert isinstance(tokens[-1], EofToken), (
            f"No EofToken for element={element!r}"
        )
