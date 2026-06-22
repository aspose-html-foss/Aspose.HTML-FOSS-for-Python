"""Tests for Track 88 CSS shorthand expansion: font, list-style, text-decoration, inset.

ADR-287 / SPEC-141 / BACK-309.

Each test function creates a Document, attaches a CSSStyleSheet with the
shorthand declaration, and asserts get_computed_style().get_property_value()
on the expected longhands.  This is the same integration pattern used by the
existing cascade test suite.
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_doc_with_style(css: str) -> tuple[Document, object]:
    """Return (doc, div_element) with *css* attached as a stylesheet."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(f"div {{ {css} }}")
    doc.attach_style_sheet(sheet)
    return doc, el


# ---------------------------------------------------------------------------
# font shorthand — AC-1, AC-2, AC-9 (part), AC-10
# ---------------------------------------------------------------------------


def test_font_shorthand_weight_size_family() -> None:
    """AC-1: font: bold 16px Arial expands weight/size/family longhands."""
    _doc, el = _make_doc_with_style("font: bold 16px Arial")
    style = el.get_computed_style()
    assert style.get_property_value("font-size") == "16px"
    assert style.get_property_value("font-weight") == "bold"
    assert style.get_property_value("font-family") == "Arial"


def test_font_shorthand_all_components() -> None:
    """AC-2: font: italic bold 24px/1.5 Georgia, serif expands all five longhands."""
    _doc, el = _make_doc_with_style("font: italic bold 24px/1.5 Georgia, serif")
    style = el.get_computed_style()
    assert style.get_property_value("font-style") == "italic"
    assert style.get_property_value("font-weight") == "bold"
    assert style.get_property_value("font-size") == "24px"
    assert style.get_property_value("line-height") == "1.5"
    assert style.get_property_value("font-family") == "Georgia, serif"


def test_font_shorthand_size_only() -> None:
    """font: 16px (size-only form) expands to font-size and nothing else."""
    _doc, el = _make_doc_with_style("font: 16px")
    style = el.get_computed_style()
    assert style.get_property_value("font-size") == "16px"
    # No family, weight, or style set from this shorthand
    assert style.get_property_value("font-family") == ""


def test_font_shorthand_system_keyword_sets_no_longhands() -> None:
    """FR-9: system-font keywords (caption etc.) must produce no longhand values."""
    _doc, el = _make_doc_with_style("font: caption")
    style = el.get_computed_style()
    # System fonts are not expanded; computed longhands remain at initial ("")
    assert style.get_property_value("font-size") == ""
    assert style.get_property_value("font-weight") == ""


# ---------------------------------------------------------------------------
# list-style shorthand — AC-3, AC-4
# ---------------------------------------------------------------------------


def test_list_style_type_and_position() -> None:
    """AC-3: list-style: disc inside expands list-style-type and list-style-position."""
    _doc, el = _make_doc_with_style("list-style: disc inside")
    style = el.get_computed_style()
    assert style.get_property_value("list-style-type") == "disc"
    assert style.get_property_value("list-style-position") == "inside"


def test_list_style_type_only() -> None:
    """AC-4: list-style: circle expands to list-style-type only, no position override."""
    _doc, el = _make_doc_with_style("list-style: circle")
    style = el.get_computed_style()
    assert style.get_property_value("list-style-type") == "circle"
    assert style.get_property_value("list-style-position") == ""


def test_list_style_none() -> None:
    """list-style: none sets list-style-type=none (not position)."""
    _doc, el = _make_doc_with_style("list-style: none")
    style = el.get_computed_style()
    assert style.get_property_value("list-style-type") == "none"
    assert style.get_property_value("list-style-position") == ""


# ---------------------------------------------------------------------------
# text-decoration shorthand — AC-5, AC-6
# ---------------------------------------------------------------------------


def test_text_decoration_line_only() -> None:
    """AC-5: text-decoration: underline expands text-decoration-line."""
    _doc, el = _make_doc_with_style("text-decoration: underline")
    style = el.get_computed_style()
    assert style.get_property_value("text-decoration-line") == "underline"


def test_text_decoration_line_style_color() -> None:
    """AC-6: text-decoration: underline solid red expands all three longhands."""
    _doc, el = _make_doc_with_style("text-decoration: underline solid red")
    style = el.get_computed_style()
    assert style.get_property_value("text-decoration-line") == "underline"
    assert style.get_property_value("text-decoration-style") == "solid"
    assert style.get_property_value("text-decoration-color") == "red"


def test_text_decoration_line_only_none() -> None:
    """text-decoration: none expands to text-decoration-line=none."""
    _doc, el = _make_doc_with_style("text-decoration: none")
    style = el.get_computed_style()
    assert style.get_property_value("text-decoration-line") == "none"


# ---------------------------------------------------------------------------
# inset shorthand — AC-7, AC-8
# ---------------------------------------------------------------------------


def test_inset_two_values() -> None:
    """AC-7: inset: 10px 20px applies two-value box-model rule (top=bottom, right=left)."""
    _doc, el = _make_doc_with_style("inset: 10px 20px")
    style = el.get_computed_style()
    assert style.get_property_value("top") == "10px"
    assert style.get_property_value("right") == "20px"
    assert style.get_property_value("bottom") == "10px"
    assert style.get_property_value("left") == "20px"


def test_inset_four_values() -> None:
    """AC-8: inset: 5px 10px 15px 20px sets each side independently."""
    _doc, el = _make_doc_with_style("inset: 5px 10px 15px 20px")
    style = el.get_computed_style()
    assert style.get_property_value("top") == "5px"
    assert style.get_property_value("right") == "10px"
    assert style.get_property_value("bottom") == "15px"
    assert style.get_property_value("left") == "20px"


def test_inset_single_value() -> None:
    """inset: 8px broadcasts to all four sides."""
    _doc, el = _make_doc_with_style("inset: 8px")
    style = el.get_computed_style()
    assert style.get_property_value("top") == "8px"
    assert style.get_property_value("right") == "8px"
    assert style.get_property_value("bottom") == "8px"
    assert style.get_property_value("left") == "8px"


# ---------------------------------------------------------------------------
# BACK-310 / ADR-288: overflow + grid sub-shorthands
# ---------------------------------------------------------------------------


def test_overflow_single_value() -> None:
    """AC-6 (BACK-310): overflow:hidden gives overflow-x='hidden' and overflow-y='hidden'."""
    _doc, el = _make_doc_with_style("overflow: hidden")
    style = el.get_computed_style()
    assert style.get_property_value("overflow-x") == "hidden"
    assert style.get_property_value("overflow-y") == "hidden"


def test_overflow_two_value() -> None:
    """AC-7 (BACK-310): overflow:scroll auto gives overflow-x='scroll', overflow-y='auto'."""
    _doc, el = _make_doc_with_style("overflow: scroll auto")
    style = el.get_computed_style()
    assert style.get_property_value("overflow-x") == "scroll"
    assert style.get_property_value("overflow-y") == "auto"


def test_grid_column_slash() -> None:
    """AC-8 (BACK-310): grid-column:1/3 gives grid-column-start='1', grid-column-end='3'."""
    _doc, el = _make_doc_with_style("grid-column: 1 / 3")
    style = el.get_computed_style()
    assert style.get_property_value("grid-column-start") == "1"
    assert style.get_property_value("grid-column-end") == "3"


def test_grid_column_single() -> None:
    """grid-column single value broadcasts to both start and end."""
    _doc, el = _make_doc_with_style("grid-column: 2")
    style = el.get_computed_style()
    assert style.get_property_value("grid-column-start") == "2"
    assert style.get_property_value("grid-column-end") == "2"


def test_grid_row_slash() -> None:
    """AC-9 (BACK-310): grid-row:2/span 2 gives grid-row-start='2', grid-row-end='span 2'."""
    _doc, el = _make_doc_with_style("grid-row: 2 / span 2")
    style = el.get_computed_style()
    assert style.get_property_value("grid-row-start") == "2"
    assert style.get_property_value("grid-row-end") == "span 2"


def test_grid_area_single() -> None:
    """AC-10 (BACK-310): grid-area:header sets all four grid placement longhands to 'header'."""
    _doc, el = _make_doc_with_style("grid-area: header")
    style = el.get_computed_style()
    assert style.get_property_value("grid-row-start") == "header"
    assert style.get_property_value("grid-column-start") == "header"
    assert style.get_property_value("grid-row-end") == "header"
    assert style.get_property_value("grid-column-end") == "header"


def test_grid_area_four_part() -> None:
    """AC-11 (BACK-310): grid-area:1/2/3/4 sets each placement longhand independently."""
    _doc, el = _make_doc_with_style("grid-area: 1 / 2 / 3 / 4")
    style = el.get_computed_style()
    assert style.get_property_value("grid-row-start") == "1"
    assert style.get_property_value("grid-column-start") == "2"
    assert style.get_property_value("grid-row-end") == "3"
    assert style.get_property_value("grid-column-end") == "4"


def test_grid_template_slash() -> None:
    """AC-12 (BACK-310): grid-template:auto/1fr 2fr sets rows and columns longhands."""
    _doc, el = _make_doc_with_style("grid-template: auto / 1fr 2fr")
    style = el.get_computed_style()
    assert style.get_property_value("grid-template-rows") == "auto"
    assert style.get_property_value("grid-template-columns") == "1fr 2fr"
