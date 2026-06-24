"""Tests for _SHORTHAND_EXPANSIONS additions from , .

Each test verifies that setting a shorthand property on an element causes the
expected longhand sub-properties to appear in the computed style.  Tests use
single-token values to match the same-value broadcast semantics of the
cascade engine (no value-grammar decomposition).

 () adds semantic dispatch for ``transition``, ``flex``, and
``background`` — correcting wrong longhand values that the generic broadcaster
produced.  Wrong-behavior tests are replaced with correct-behavior tests here.
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.dom._cascade_shorthands import (
    _expand_flex_shorthand,
    _expand_transition_shorthand,
    _expand_background_shorthand,
)


def _make_element(selector: str, css: str) -> object:
    """Create a document with one styled element and return (element, style)."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(f"{selector} {{ {css} }}")
    doc.attach_style_sheet(sheet)
    return el


# ---------------------------------------------------------------------------
# background shorthand — semantic dispatch (, )
# ---------------------------------------------------------------------------

def test_background_color_only() -> None:
    """background: red — only background-color is set (not all 8 longhands)."""
    el = _make_element("div", "background: red")
    style = el.get_computed_style()
    assert style.get_property_value("background-color") == "red"
    assert style.get_property_value("background-image") == ""
    assert style.get_property_value("background-position") == ""


def test_background_url_only() -> None:
    """background: url(a.png) — only background-image is set."""
    el = _make_element("div", "background: url(a.png)")
    style = el.get_computed_style()
    assert style.get_property_value("background-image") == "url(a.png)"
    assert style.get_property_value("background-color") == ""


def test_background_url_and_color() -> None:
    """background: url(a.png) red — image + color are both set."""
    el = _make_element("div", "background: url(a.png) red")
    style = el.get_computed_style()
    assert style.get_property_value("background-image") == "url(a.png)"
    assert style.get_property_value("background-color") == "red"


# Unit-level helpers
def test_expand_background_shorthand_color_unit() -> None:
    assert _expand_background_shorthand("red") == {"background-color": "red"}


def test_expand_background_shorthand_url_unit() -> None:
    assert _expand_background_shorthand("url(a.png)") == {"background-image": "url(a.png)"}


def test_expand_background_shorthand_url_color_unit() -> None:
    assert _expand_background_shorthand("url(a.png) red") == {
        "background-image": "url(a.png)",
        "background-color": "red",
    }


def test_expand_background_shorthand_slash_form_unit() -> None:
    result = _expand_background_shorthand("center/cover no-repeat")
    assert result.get("background-position") == "center"
    assert result.get("background-size") == "cover"
    assert result.get("background-repeat") == "no-repeat"


# ---------------------------------------------------------------------------
# flex shorthand — semantic dispatch (, )
# ---------------------------------------------------------------------------

def test_flex_shorthand_expands_to_longhands() -> None:
    """flex: auto → flex-grow:1, flex-shrink:1, flex-basis:auto (semantic)."""
    el = _make_element("div", "flex: auto")
    style = el.get_computed_style()
    assert style.get_property_value("flex-grow") == "1"
    assert style.get_property_value("flex-shrink") == "1"
    assert style.get_property_value("flex-basis") == "auto"


def test_flex_shorthand_none() -> None:
    """flex: none → flex-grow:0, flex-shrink:0, flex-basis:auto."""
    el = _make_element("div", "flex: none")
    style = el.get_computed_style()
    assert style.get_property_value("flex-grow") == "0"
    assert style.get_property_value("flex-shrink") == "0"
    assert style.get_property_value("flex-basis") == "auto"


def test_flex_shorthand_single_number() -> None:
    """flex: 1 → flex-grow:1, flex-shrink:1, flex-basis:0%."""
    el = _make_element("div", "flex: 1")
    style = el.get_computed_style()
    assert style.get_property_value("flex-grow") == "1"
    assert style.get_property_value("flex-shrink") == "1"
    assert style.get_property_value("flex-basis") == "0%"


def test_flex_shorthand_two_numbers() -> None:
    """flex: 2 3 → flex-grow:2, flex-shrink:3, flex-basis:0%."""
    el = _make_element("div", "flex: 2 3")
    style = el.get_computed_style()
    assert style.get_property_value("flex-grow") == "2"
    assert style.get_property_value("flex-shrink") == "3"
    assert style.get_property_value("flex-basis") == "0%"


def test_flex_shorthand_three_values() -> None:
    """flex: 2 3 50% → flex-grow:2, flex-shrink:3, flex-basis:50%."""
    el = _make_element("div", "flex: 2 3 50%")
    style = el.get_computed_style()
    assert style.get_property_value("flex-grow") == "2"
    assert style.get_property_value("flex-shrink") == "3"
    assert style.get_property_value("flex-basis") == "50%"


# Unit-level helper tests
def test_expand_flex_shorthand_none_unit() -> None:
    assert _expand_flex_shorthand("none") == {"flex-grow": "0", "flex-shrink": "0", "flex-basis": "auto"}


def test_expand_flex_shorthand_auto_unit() -> None:
    assert _expand_flex_shorthand("auto") == {"flex-grow": "1", "flex-shrink": "1", "flex-basis": "auto"}


def test_expand_flex_shorthand_single_number_unit() -> None:
    assert _expand_flex_shorthand("1") == {"flex-grow": "1", "flex-shrink": "1", "flex-basis": "0%"}


def test_expand_flex_shorthand_two_numbers_unit() -> None:
    assert _expand_flex_shorthand("2 3") == {"flex-grow": "2", "flex-shrink": "3", "flex-basis": "0%"}


def test_expand_flex_shorthand_three_values_unit() -> None:
    assert _expand_flex_shorthand("2 3 50%") == {"flex-grow": "2", "flex-shrink": "3", "flex-basis": "50%"}


def test_expand_flex_shorthand_number_basis_unit() -> None:
    assert _expand_flex_shorthand("1 30px") == {"flex-grow": "1", "flex-shrink": "1", "flex-basis": "30px"}


def test_flex_flow_shorthand_expands() -> None:
    """flex-flow: row broadcasts to flex-direction and flex-wrap."""
    el = _make_element("div", "flex-flow: row")
    style = el.get_computed_style()

    assert style.get_property_value("flex-direction") == "row"
    assert style.get_property_value("flex-wrap") == "row"


def test_gap_shorthand_expands() -> None:
    """gap: 10px causes row-gap and column-gap to both be '10px'."""
    el = _make_element("div", "gap: 10px")
    style = el.get_computed_style()

    assert style.get_property_value("row-gap") == "10px"
    assert style.get_property_value("column-gap") == "10px"


# ---------------------------------------------------------------------------
# transition shorthand — semantic dispatch (, )
# ---------------------------------------------------------------------------

def test_transition_shorthand_three_tokens() -> None:
    """transition: opacity 0.3s ease — semantic expansion, delay defaults to 0s."""
    el = _make_element("div", "transition: opacity 0.3s ease")
    style = el.get_computed_style()
    assert style.get_property_value("transition-property") == "opacity"
    assert style.get_property_value("transition-duration") == "0.3s"
    assert style.get_property_value("transition-timing-function") == "ease"
    assert style.get_property_value("transition-delay") == "0s"


def test_transition_shorthand_two_tokens() -> None:
    """transition: all 0.5s — property + duration; easing and delay at initial."""
    el = _make_element("div", "transition: all 0.5s")
    style = el.get_computed_style()
    assert style.get_property_value("transition-property") == "all"
    assert style.get_property_value("transition-duration") == "0.5s"
    assert style.get_property_value("transition-timing-function") == "ease"
    assert style.get_property_value("transition-delay") == "0s"


def test_transition_shorthand_four_tokens() -> None:
    """transition: opacity 0.3s ease 0.1s — all four slots explicit."""
    el = _make_element("div", "transition: opacity 0.3s ease 0.1s")
    style = el.get_computed_style()
    assert style.get_property_value("transition-property") == "opacity"
    assert style.get_property_value("transition-duration") == "0.3s"
    assert style.get_property_value("transition-timing-function") == "ease"
    assert style.get_property_value("transition-delay") == "0.1s"


# Unit-level helper tests
def test_expand_transition_shorthand_three_tokens_unit() -> None:
    result = _expand_transition_shorthand("opacity 0.3s ease")
    assert result == {
        "transition-property": "opacity",
        "transition-duration": "0.3s",
        "transition-timing-function": "ease",
        "transition-delay": "0s",
    }


def test_expand_transition_shorthand_two_tokens_unit() -> None:
    result = _expand_transition_shorthand("all 0.5s")
    assert result == {
        "transition-property": "all",
        "transition-duration": "0.5s",
        "transition-timing-function": "ease",
        "transition-delay": "0s",
    }


def test_expand_transition_shorthand_four_tokens_unit() -> None:
    result = _expand_transition_shorthand("opacity 0.3s ease 0.1s")
    assert result["transition-delay"] == "0.1s"


def test_expand_transition_shorthand_multi_comma_unit() -> None:
    assert _expand_transition_shorthand("opacity 0.3s, transform 0.5s") == {}


def test_transition_shorthand_expands() -> None:
    """transition: all (single keyword) — semantic dispatch; property=all, duration/delay at 0s."""
    el = _make_element("div", "transition: all")
    style = el.get_computed_style()

    # After semantic dispatch, "all" is the transition-property.
    # Duration, delay use initial values (0s); timing-function uses "ease".
    assert style.get_property_value("transition-property") == "all"
    assert style.get_property_value("transition-duration") == "0s"
    assert style.get_property_value("transition-timing-function") == "ease"
    assert style.get_property_value("transition-delay") == "0s"


def test_border_radius_shorthand_expands() -> None:
    """border-radius: 4px causes all four corner longhands to be '4px'."""
    el = _make_element("div", "border-radius: 4px")
    style = el.get_computed_style()

    assert style.get_property_value("border-top-left-radius") == "4px"
    assert style.get_property_value("border-top-right-radius") == "4px"
    assert style.get_property_value("border-bottom-right-radius") == "4px"
    assert style.get_property_value("border-bottom-left-radius") == "4px"


def test_place_items_shorthand_expands() -> None:
    """place-items: center broadcasts to align-items and justify-items."""
    el = _make_element("div", "place-items: center")
    style = el.get_computed_style()

    assert style.get_property_value("align-items") == "center"
    assert style.get_property_value("justify-items") == "center"


def test_animation_shorthand_expands_to_longhands() -> None:
    """animation: none — semantic dispatch: animation-name=none, rest at initial values."""
    el = _make_element("div", "animation: none")
    style = el.get_computed_style()

    # The animation shorthand semantic helper () routes 'none' as the
    # animation-name; all other longhands receive their initial values.
    assert style.get_property_value("animation-name") == "none"
    assert style.get_property_value("animation-duration") == "0s"
    assert style.get_property_value("animation-timing-function") == "ease"
    assert style.get_property_value("animation-delay") == "0s"
    assert style.get_property_value("animation-iteration-count") == "1"
    assert style.get_property_value("animation-direction") == "normal"
    assert style.get_property_value("animation-fill-mode") == "none"
    assert style.get_property_value("animation-play-state") == "running"


def test_columns_shorthand_expands() -> None:
    """columns: auto broadcasts to column-count and column-width."""
    el = _make_element("div", "columns: auto")
    style = el.get_computed_style()

    assert style.get_property_value("column-count") == "auto"
    assert style.get_property_value("column-width") == "auto"


def test_column_rule_shorthand_expands() -> None:
    """column-rule: solid broadcasts to column-rule-color, style, width."""
    el = _make_element("div", "column-rule: solid")
    style = el.get_computed_style()

    assert style.get_property_value("column-rule-color") == "solid"
    assert style.get_property_value("column-rule-style") == "solid"
    assert style.get_property_value("column-rule-width") == "solid"


def test_place_content_shorthand_expands() -> None:
    """place-content: center broadcasts to align-content and justify-content."""
    el = _make_element("div", "place-content: center")
    style = el.get_computed_style()

    assert style.get_property_value("align-content") == "center"
    assert style.get_property_value("justify-content") == "center"


def test_place_self_shorthand_expands() -> None:
    """place-self: auto broadcasts to align-self and justify-self."""
    el = _make_element("div", "place-self: auto")
    style = el.get_computed_style()

    assert style.get_property_value("align-self") == "auto"
    assert style.get_property_value("justify-self") == "auto"


def test_overscroll_behavior_shorthand_expands() -> None:
    """overscroll-behavior: auto broadcasts to overscroll-behavior-x/y."""
    el = _make_element("div", "overscroll-behavior: auto")
    style = el.get_computed_style()

    assert style.get_property_value("overscroll-behavior-x") == "auto"
    assert style.get_property_value("overscroll-behavior-y") == "auto"


def test_gap_two_token_expands() -> None:
    """gap: 10px 20px: row-gap gets '10px' (first token), column-gap gets '20px'."""
    el = _make_element("div", "gap: 10px 20px")
    style = el.get_computed_style()

    assert style.get_property_value("row-gap") == "10px"
    assert style.get_property_value("column-gap") == "20px"


def test_flex_flow_two_token_expands() -> None:
    """flex-flow: row wrap: flex-direction gets 'row', flex-wrap gets 'wrap'."""
    el = _make_element("div", "flex-flow: row wrap")
    style = el.get_computed_style()

    assert style.get_property_value("flex-direction") == "row"
    assert style.get_property_value("flex-wrap") == "wrap"


def test_border_radius_two_token_expands() -> None:
    """border-radius: 4px 8px applies 4-value CSS box-model pattern to 4 corners."""
    el = _make_element("div", "border-radius: 4px 8px")
    style = el.get_computed_style()

    # 2-token CSS pattern maps to (T-L, T-R, B-R, B-L) = (t0, t1, t0, t1)
    assert style.get_property_value("border-top-left-radius") == "4px"
    assert style.get_property_value("border-top-right-radius") == "8px"
    assert style.get_property_value("border-bottom-right-radius") == "4px"
    assert style.get_property_value("border-bottom-left-radius") == "8px"


def test_existing_margin_shorthand_unaffected() -> None:
    """Existing margin shorthand still expands correctly after  additions."""
    el = _make_element("div", "margin: 5px")
    style = el.get_computed_style()

    assert style.get_property_value("margin-top") == "5px"
    assert style.get_property_value("margin-right") == "5px"
    assert style.get_property_value("margin-bottom") == "5px"
    assert style.get_property_value("margin-left") == "5px"
