"""Integration tests for  — CSS var() paren-depth-aware shorthand tokeniser
and env() fallback resolution.

Covers  acceptance criteria:
- _tokenize_css_value unit tests
- _expand_shorthand_value with var() as single token
- End-to-end get_computed_style() resolution with var() in shorthand

Covers  acceptance criteria:
- _resolve_env_function unit tests
- _looks_like_full_value_env_call unit tests
- End-to-end get_computed_style() resolution with env() in regular and shorthand values
"""
from __future__ import annotations

import pytest

from aspose_html.dom._cascade_shorthands import (
    _tokenize_css_value,
    _expand_shorthand_value,
    _resolve_env_function,
    _looks_like_full_value_env_call,
)


# ---------------------------------------------------------------------------
# Unit tests: _tokenize_css_value
# ---------------------------------------------------------------------------


def test_split_respecting_parens_simple():
    """Plain whitespace-separated values split normally."""
    assert _tokenize_css_value("4px 8px") == ["4px", "8px"]


def test_split_respecting_parens_var():
    """var() with comma inside stays as single token."""
    assert _tokenize_css_value("var(--x, 4px) 8px") == ["var(--x, 4px)", "8px"]


def test_split_respecting_parens_calc():
    """calc() with internal spaces stays as single token."""
    assert _tokenize_css_value("calc(100% - 2em) auto") == ["calc(100% - 2em)", "auto"]


def test_split_respecting_parens_empty():
    """Empty string returns empty list."""
    assert _tokenize_css_value("") == []


def test_tokenize_single_token():
    """Single token (no spaces) returns a one-element list."""
    assert _tokenize_css_value("single") == ["single"]


def test_tokenize_var_single_token():
    """var() with no surrounding tokens returns one-element list."""
    assert _tokenize_css_value("var(--space, 8px)") == ["var(--space, 8px)"]


def test_tokenize_var_no_fallback():
    """var() without comma inside stays as single token."""
    assert _tokenize_css_value("var(--w) auto") == ["var(--w)", "auto"]


def test_tokenize_mixed_prefix_and_suffix():
    """var() embedded between plain tokens."""
    assert _tokenize_css_value("4px var(--gap, 2px) 4px") == ["4px", "var(--gap, 2px)", "4px"]


def test_tokenize_four_plain():
    """Four plain tokens — same as raw_value.split()."""
    result = _tokenize_css_value("1px 2px 3px 4px")
    assert result == ["1px", "2px", "3px", "4px"]


def test_tokenize_whitespace_variants():
    """Tabs and multiple spaces between tokens are treated as separators."""
    assert _tokenize_css_value("4px\t8px") == ["4px", "8px"]
    assert _tokenize_css_value("  4px  8px  ") == ["4px", "8px"]


# ---------------------------------------------------------------------------
# Unit tests: _expand_shorthand_value — var() stays atomic
# ---------------------------------------------------------------------------


def test_padding_var_single_token():
    """padding: var(--p, 4px) — single-token broadcast to all four longhands."""
    result = _expand_shorthand_value("padding", "var(--p, 4px)")
    assert result is not None
    assert result != {}
    for longhand in ("padding-top", "padding-right", "padding-bottom", "padding-left"):
        assert longhand in result
        assert result[longhand] != ""
        assert "var(--p, 4px)" in result[longhand] or result[longhand] == "var(--p, 4px)"


def test_margin_var_with_fallback():
    """margin: var(--m, 8px) auto — two tokens, first is atomic var()."""
    result = _expand_shorthand_value("margin", "var(--m, 8px) auto")
    assert result is not None
    assert result != {}
    # Two-token pattern: top=t[0], right=t[1], bottom=t[0], left=t[1]
    assert result["margin-top"] == "var(--m, 8px)"
    assert result["margin-right"] == "auto"
    assert result["margin-bottom"] == "var(--m, 8px)"
    assert result["margin-left"] == "auto"


def test_border_var_not_split():
    """border: var(--b, 1px solid red) — single var() token broadcast."""
    result = _expand_shorthand_value("border", "var(--b, 1px solid red)")
    assert result is not None
    assert result != {}
    # _expand_border_shorthand with 1 token that looks like var() broadcasts
    for key in result:
        assert result[key] == "var(--b, 1px solid red)"


def test_existing_shorthand_margin_unaffected():
    """Regression: margin: 4px 8px still expands correctly."""
    result = _expand_shorthand_value("margin", "4px 8px")
    assert result == {
        "margin-top": "4px",
        "margin-right": "8px",
        "margin-bottom": "4px",
        "margin-left": "8px",
    }


def test_existing_shorthand_padding_four_values():
    """Regression: padding: 1px 2px 3px 4px still expands correctly."""
    result = _expand_shorthand_value("padding", "1px 2px 3px 4px")
    assert result == {
        "padding-top": "1px",
        "padding-right": "2px",
        "padding-bottom": "3px",
        "padding-left": "4px",
    }


# ---------------------------------------------------------------------------
# Integration tests: get_computed_style() with var() in shorthand
# ---------------------------------------------------------------------------


def _make_doc_with_style(css: str):
    """Helper: create a Document with one div and the given stylesheet."""
    from aspose_html.cssom import CSSStyleSheet
    from aspose_html.dom import Document

    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(css)
    doc.attach_style_sheet(sheet)
    return doc, el


def test_padding_var_with_fallback_no_custom_prop():
    """padding: var(--p, 4px) with --p unset → all longhands resolve to 4px."""
    doc, el = _make_doc_with_style("div { padding: var(--p, 4px); }")
    style = el.get_computed_style()
    assert style.get_property_value("padding-top") == "4px"
    assert style.get_property_value("padding-right") == "4px"
    assert style.get_property_value("padding-bottom") == "4px"
    assert style.get_property_value("padding-left") == "4px"


def test_padding_var_with_custom_prop_set():
    """padding: var(--p, 4px) with --p: 16px → all longhands resolve to 16px."""
    doc, el = _make_doc_with_style("div { --p: 16px; padding: var(--p, 4px); }")
    style = el.get_computed_style()
    assert style.get_property_value("padding-top") == "16px"
    assert style.get_property_value("padding-right") == "16px"
    assert style.get_property_value("padding-bottom") == "16px"
    assert style.get_property_value("padding-left") == "16px"


def test_margin_var_no_custom_prop():
    """margin: var(--m, 8px) with no custom prop → all longhands to 8px."""
    doc, el = _make_doc_with_style("div { margin: var(--m, 8px); }")
    style = el.get_computed_style()
    assert style.get_property_value("margin-top") == "8px"
    assert style.get_property_value("margin-right") == "8px"
    assert style.get_property_value("margin-bottom") == "8px"
    assert style.get_property_value("margin-left") == "8px"


def test_margin_var_custom_prop_set():
    """margin: var(--m) with --m: 16px → all longhands to 16px."""
    doc, el = _make_doc_with_style("div { --m: 16px; margin: var(--m); }")
    style = el.get_computed_style()
    assert style.get_property_value("margin-top") == "16px"
    assert style.get_property_value("margin-right") == "16px"
    assert style.get_property_value("margin-bottom") == "16px"
    assert style.get_property_value("margin-left") == "16px"


def test_padding_var_two_tokens():
    """padding: var(--w) auto — two-token distribution with atomic var()."""
    doc, el = _make_doc_with_style("div { --w: 4px; padding: var(--w) auto; }")
    style = el.get_computed_style()
    # top and bottom use var(--w) → resolves to 4px
    assert style.get_property_value("padding-top") == "4px"
    assert style.get_property_value("padding-bottom") == "4px"
    # right and left use "auto"
    assert style.get_property_value("padding-right") == "auto"
    assert style.get_property_value("padding-left") == "auto"


def test_existing_shorthand_integration_unaffected():
    """Regression: margin: 4px 8px still resolves correctly end-to-end."""
    doc, el = _make_doc_with_style("div { margin: 4px 8px; }")
    style = el.get_computed_style()
    assert style.get_property_value("margin-top") == "4px"
    assert style.get_property_value("margin-right") == "8px"
    assert style.get_property_value("margin-bottom") == "4px"
    assert style.get_property_value("margin-left") == "8px"


# ---------------------------------------------------------------------------
# Unit tests: _resolve_env_function ()
# ---------------------------------------------------------------------------


def test_resolve_env_with_fallback():
    """env(name, fallback) returns the fallback string."""
    assert _resolve_env_function("env(safe-area-inset-top, 12px)") == "12px"


def test_resolve_env_no_fallback_returns_none():
    """env(name) with no fallback returns None."""
    assert _resolve_env_function("env(safe-area-inset-top)") is None


def test_resolve_env_custom_name_with_fallback():
    """env(--brand, red) returns the fallback 'red'."""
    assert _resolve_env_function("env(--brand, red)") == "red"


def test_resolve_env_non_env_value_returns_none():
    """Non-env value returns None (caller skips env path)."""
    assert _resolve_env_function("4px") is None


def test_resolve_env_empty_fallback_returns_none():
    """env(name, ) with empty fallback returns None."""
    assert _resolve_env_function("env(--x, )") is None


def test_resolve_env_multi_word_fallback():
    """env(--bd, 1px solid blue) returns the full fallback string."""
    assert _resolve_env_function("env(--bd, 1px solid blue)") == "1px solid blue"


def test_resolve_env_case_insensitive():
    """ENV(...) is recognized case-insensitively."""
    assert _resolve_env_function("ENV(safe-area-inset-top, 8px)") == "8px"


# ---------------------------------------------------------------------------
# Unit tests: _looks_like_full_value_env_call ()
# ---------------------------------------------------------------------------


def test_looks_like_env_call_true():
    """env(safe-area-inset-top, 12px) is recognized as an env() call."""
    assert _looks_like_full_value_env_call("env(safe-area-inset-top, 12px)") is True


def test_looks_like_env_call_no_fallback_true():
    """env(safe-area-inset-top) is recognized as an env() call."""
    assert _looks_like_full_value_env_call("env(safe-area-inset-top)") is True


def test_looks_like_env_call_uppercase_true():
    """ENV(...) case-insensitive match."""
    assert _looks_like_full_value_env_call("ENV(x)") is True


def test_looks_like_env_call_var_false():
    """var(--x) is not an env() call."""
    assert _looks_like_full_value_env_call("var(--x)") is False


def test_looks_like_env_call_plain_false():
    """4px is not an env() call."""
    assert _looks_like_full_value_env_call("4px") is False


# ---------------------------------------------------------------------------
# Integration tests: get_computed_style() with env() (, Group B)
# ---------------------------------------------------------------------------


def test_env_with_fallback_resolves_to_fallback():
    """padding: env(safe-area-inset-top, 8px) → all longhands == '8px'."""
    doc, el = _make_doc_with_style("div { padding: env(safe-area-inset-top, 8px); }")
    style = el.get_computed_style()
    assert style.get_property_value("padding-top") == "8px"
    assert style.get_property_value("padding-right") == "8px"
    assert style.get_property_value("padding-bottom") == "8px"
    assert style.get_property_value("padding-left") == "8px"


def test_env_without_fallback_resolves_empty():
    """margin: env(unknown-var) with no fallback → margin longhands not set (empty)."""
    doc, el = _make_doc_with_style("div { margin: env(unknown-var); }")
    style = el.get_computed_style()
    # Declaration dropped — get_property_value returns the initial value or ""
    assert style.get_property_value("margin-top") == ""
    assert style.get_property_value("margin-bottom") == ""


def test_env_color_property():
    """color: env(--brand, red) → 'red'."""
    doc, el = _make_doc_with_style("div { color: env(--brand, red); }")
    style = el.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_env_positioning_property():
    """top: env(--defined, 5em) → 'top' == '5em'."""
    doc, el = _make_doc_with_style("div { top: env(--defined, 5em); }")
    style = el.get_computed_style()
    assert style.get_property_value("top") == "5em"


def test_env_in_shorthand_tokenized_correctly():
    """padding: env(safe-area, 4px) 8px — two tokens extracted correctly."""
    # _tokenize_css_value must keep env(...) as one atomic token
    tokens = _tokenize_css_value("env(safe-area, 4px) 8px")
    assert len(tokens) == 2
    assert tokens[0] == "env(safe-area, 4px)"
    assert tokens[1] == "8px"


def test_env_border_broadcast():
    """border: env(--bd, 1px solid blue) — single-token broadcast to all border longhands."""
    result = _expand_shorthand_value("border", "env(--bd, 1px solid blue)")
    assert result is not None
    assert result != {}
    for key in result:
        assert result[key] == "env(--bd, 1px solid blue)"


def test_var_and_env_combined():
    """padding: var(--p, env(safe-area, 4px)) — non-crash with string result."""
    # var(--p, env(safe-area, 4px)): --p is unset, fallback is "env(safe-area, 4px)"
    # The cascade will use the fallback string directly (it is not re-resolved
    # through the env() path because the fallback is used as a raw string value).
    doc, el = _make_doc_with_style("div { padding: var(--p, env(safe-area, 4px)); }")
    style = el.get_computed_style()
    # Must not crash; result is a string (either resolved env fallback or raw fallback)
    val = style.get_property_value("padding-top")
    assert isinstance(val, str)


def test_existing_var_shorthand_still_works():
    """Regression: padding: var(--p, 4px) still works after env() addition."""
    doc, el = _make_doc_with_style("div { padding: var(--p, 4px); }")
    style = el.get_computed_style()
    assert style.get_property_value("padding-top") == "4px"
    assert style.get_property_value("padding-right") == "4px"
    assert style.get_property_value("padding-bottom") == "4px"
    assert style.get_property_value("padding-left") == "4px"
