"""Tests for CSS border sub-shorthand expansion — Track 93, ADR-292.

Covers border-width, border-style, and border-color 1/2/3/4 token positional
expansion, CSS.supports checks, and regression coverage for the border/border-top
shorthands that must continue to work unchanged.
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSS, CSSStyleSheet
from aspose_html.dom import Document


def _make_element(css: str) -> object:
    """Create a document with one <div> styled by *css* and return the element."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(f"div {{ {css} }}")
    doc.attach_style_sheet(sheet)
    return el


# ---------------------------------------------------------------------------
# border-width expansion (AC-1, AC-2, AC-3)
# ---------------------------------------------------------------------------


def test_border_width_single_token() -> None:
    """border-width: 2px broadcasts to all four border-*-width longhands (AC-1)."""
    el = _make_element("border-width: 2px")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-width") == "2px"
    assert style.get_property_value("border-right-width") == "2px"
    assert style.get_property_value("border-bottom-width") == "2px"
    assert style.get_property_value("border-left-width") == "2px"


def test_border_width_four_tokens() -> None:
    """border-width: 1px 2px 3px 4px assigns top/right/bottom/left individually (AC-2)."""
    el = _make_element("border-width: 1px 2px 3px 4px")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-width") == "1px"
    assert style.get_property_value("border-right-width") == "2px"
    assert style.get_property_value("border-bottom-width") == "3px"
    assert style.get_property_value("border-left-width") == "4px"


def test_border_width_two_tokens() -> None:
    """border-width: 1px 2px → top/bottom '1px', right/left '2px' (AC-3)."""
    el = _make_element("border-width: 1px 2px")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-width") == "1px"
    assert style.get_property_value("border-right-width") == "2px"
    assert style.get_property_value("border-bottom-width") == "1px"
    assert style.get_property_value("border-left-width") == "2px"


def test_border_width_three_tokens() -> None:
    """border-width: 1px 2px 3px → top '1px', right/left '2px', bottom '3px'."""
    el = _make_element("border-width: 1px 2px 3px")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-width") == "1px"
    assert style.get_property_value("border-right-width") == "2px"
    assert style.get_property_value("border-bottom-width") == "3px"
    assert style.get_property_value("border-left-width") == "2px"


# ---------------------------------------------------------------------------
# border-style expansion (AC-4, AC-5)
# ---------------------------------------------------------------------------


def test_border_style_single_token() -> None:
    """border-style: solid broadcasts to all four border-*-style longhands (AC-4)."""
    el = _make_element("border-style: solid")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-style") == "solid"
    assert style.get_property_value("border-right-style") == "solid"
    assert style.get_property_value("border-bottom-style") == "solid"
    assert style.get_property_value("border-left-style") == "solid"


def test_border_style_two_tokens() -> None:
    """border-style: solid dashed → top/bottom 'solid', right/left 'dashed' (AC-5)."""
    el = _make_element("border-style: solid dashed")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-style") == "solid"
    assert style.get_property_value("border-right-style") == "dashed"
    assert style.get_property_value("border-bottom-style") == "solid"
    assert style.get_property_value("border-left-style") == "dashed"


def test_border_style_four_tokens() -> None:
    """border-style: solid dashed dotted double → all four individually."""
    el = _make_element("border-style: solid dashed dotted double")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-style") == "solid"
    assert style.get_property_value("border-right-style") == "dashed"
    assert style.get_property_value("border-bottom-style") == "dotted"
    assert style.get_property_value("border-left-style") == "double"


def test_border_style_three_tokens() -> None:
    """border-style: solid dashed dotted → top 'solid', right/left 'dashed', bottom 'dotted'."""
    el = _make_element("border-style: solid dashed dotted")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-style") == "solid"
    assert style.get_property_value("border-right-style") == "dashed"
    assert style.get_property_value("border-bottom-style") == "dotted"
    assert style.get_property_value("border-left-style") == "dashed"


# ---------------------------------------------------------------------------
# border-color expansion (AC-6, AC-7)
# ---------------------------------------------------------------------------


def test_border_color_single_token() -> None:
    """border-color: red broadcasts to all four border-*-color longhands (AC-6)."""
    el = _make_element("border-color: red")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-color") == "red"
    assert style.get_property_value("border-right-color") == "red"
    assert style.get_property_value("border-bottom-color") == "red"
    assert style.get_property_value("border-left-color") == "red"


def test_border_color_four_tokens() -> None:
    """border-color: red green blue yellow → top/right/bottom/left individually (AC-7)."""
    el = _make_element("border-color: red green blue yellow")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-color") == "red"
    assert style.get_property_value("border-right-color") == "green"
    assert style.get_property_value("border-bottom-color") == "blue"
    assert style.get_property_value("border-left-color") == "yellow"


def test_border_color_two_tokens() -> None:
    """border-color: red green → top/bottom 'red', right/left 'green'."""
    el = _make_element("border-color: red green")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-color") == "red"
    assert style.get_property_value("border-right-color") == "green"
    assert style.get_property_value("border-bottom-color") == "red"
    assert style.get_property_value("border-left-color") == "green"


def test_border_color_three_tokens() -> None:
    """border-color: red green blue → top 'red', right/left 'green', bottom 'blue'."""
    el = _make_element("border-color: red green blue")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-color") == "red"
    assert style.get_property_value("border-right-color") == "green"
    assert style.get_property_value("border-bottom-color") == "blue"
    assert style.get_property_value("border-left-color") == "green"


# ---------------------------------------------------------------------------
# CSS.supports (AC-8, AC-9, AC-10)
# ---------------------------------------------------------------------------


def test_css_supports_border_width() -> None:
    """CSS.supports('border-width', '1px') returns True (AC-8)."""
    assert CSS.supports("border-width", "1px") is True


def test_css_supports_border_style() -> None:
    """CSS.supports('border-style', 'solid') returns True (AC-9)."""
    assert CSS.supports("border-style", "solid") is True


def test_css_supports_border_color() -> None:
    """CSS.supports('border-color', 'red') returns True (AC-10)."""
    assert CSS.supports("border-color", "red") is True


# ---------------------------------------------------------------------------
# Regression — border and border-top must still work (AC-11)
# ---------------------------------------------------------------------------


def test_border_shorthand_regression() -> None:
    """border: 2px solid red still expands to all twelve longhands."""
    el = _make_element("border: 2px solid red")
    style = el.get_computed_style()
    for side in ("top", "right", "bottom", "left"):
        assert style.get_property_value(f"border-{side}-width") == "2px", (
            f"border-{side}-width should be '2px'"
        )
        assert style.get_property_value(f"border-{side}-style") == "solid", (
            f"border-{side}-style should be 'solid'"
        )
        assert style.get_property_value(f"border-{side}-color") == "red", (
            f"border-{side}-color should be 'red'"
        )


def test_border_top_shorthand_regression() -> None:
    """border-top: 1px dashed blue still expands to its three longhands."""
    el = _make_element("border-top: 1px dashed blue")
    style = el.get_computed_style()
    assert style.get_property_value("border-top-width") == "1px"
    assert style.get_property_value("border-top-style") == "dashed"
    assert style.get_property_value("border-top-color") == "blue"
