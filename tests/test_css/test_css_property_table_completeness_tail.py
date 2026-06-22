"""Tests for CSS property table completeness tail — Track 94, ADR-293.

Covers text-overflow, scroll-margin/padding, mask, touch-action, accent-color,
caret-color, scrollbar-width, and scrollbar-color additions to
_INITIAL_VALUE_BASELINE and _SHORTHAND_EXPANSIONS in _cascade.py.

AC map (see SPEC-147):
  AC-1  — CSS.supports("text-overflow", "ellipsis") is True
  AC-2  — CSS.supports for all 4 scroll-margin longhands is True
  AC-3  — scroll-margin shorthand expands to 4 longhands
  AC-4  — CSS.supports for all 4 scroll-padding longhands is True
  AC-5  — scroll-padding shorthand expands to 4 longhands
  AC-6  — CSS.supports for all 8 mask longhands is True
  AC-7  — CSS.supports("touch-action", "none") is True
  AC-8  — CSS.supports("accent-color", "red") is True
  AC-9  — CSS.supports("caret-color", "auto") is True
  AC-10 — CSS.supports("scrollbar-width", "thin") is True
  AC-11 — CSS.supports("scrollbar-color", "red blue") is True
  AC-12 — _INITIAL_VALUE_BASELINE has exactly 286 entries
  AC-13 — full test suite passes with 0 new failures (checked at CI level)
  AC-14 — pytest tests/test_css/ -x passes (checked at CI level)
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSS, CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE


def _make_element(css: str) -> object:
    """Create a document with a single <div> styled by *css* and return it."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(f"div {{ {css} }}")
    doc.attach_style_sheet(sheet)
    return el


def _make_element_with_inline(prop: str, value: str) -> object:
    """Create a <div> with *prop* set as inline style and return it."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    el.style[prop] = value
    return el


# ---------------------------------------------------------------------------
# AC-1: text-overflow
# ---------------------------------------------------------------------------


def test_supports_text_overflow() -> None:
    """CSS.supports("text-overflow", "ellipsis") returns True (AC-1)."""
    assert CSS.supports("text-overflow", "ellipsis") is True


def test_text_overflow_via_stylesheet() -> None:
    """Stylesheet text-overflow is stored and retrieved from computed style (AC-1)."""
    el = _make_element("text-overflow: ellipsis")
    assert el.get_computed_style().get_property_value("text-overflow") == "ellipsis"


# ---------------------------------------------------------------------------
# AC-2: scroll-margin longhands
# ---------------------------------------------------------------------------


def test_supports_scroll_margin_top() -> None:
    """CSS.supports("scroll-margin-top", "10px") returns True (AC-2)."""
    assert CSS.supports("scroll-margin-top", "10px") is True


def test_supports_scroll_margin_right() -> None:
    """CSS.supports("scroll-margin-right", "10px") returns True (AC-2)."""
    assert CSS.supports("scroll-margin-right", "10px") is True


def test_supports_scroll_margin_bottom() -> None:
    """CSS.supports("scroll-margin-bottom", "10px") returns True (AC-2)."""
    assert CSS.supports("scroll-margin-bottom", "10px") is True


def test_supports_scroll_margin_left() -> None:
    """CSS.supports("scroll-margin-left", "10px") returns True (AC-2)."""
    assert CSS.supports("scroll-margin-left", "10px") is True


# ---------------------------------------------------------------------------
# AC-3: scroll-margin shorthand expansion
# ---------------------------------------------------------------------------


def test_scroll_margin_shorthand_two_tokens() -> None:
    """scroll-margin: 10px 20px expands top/bottom=10px, right/left=20px (AC-3)."""
    el = _make_element_with_inline("scroll-margin", "10px 20px")
    style = el.get_computed_style()
    assert style.get_property_value("scroll-margin-top") == "10px"
    assert style.get_property_value("scroll-margin-right") == "20px"
    assert style.get_property_value("scroll-margin-bottom") == "10px"
    assert style.get_property_value("scroll-margin-left") == "20px"


def test_scroll_margin_shorthand_one_token() -> None:
    """scroll-margin: 5px broadcasts to all four longhands (AC-3)."""
    el = _make_element_with_inline("scroll-margin", "5px")
    style = el.get_computed_style()
    assert style.get_property_value("scroll-margin-top") == "5px"
    assert style.get_property_value("scroll-margin-right") == "5px"
    assert style.get_property_value("scroll-margin-bottom") == "5px"
    assert style.get_property_value("scroll-margin-left") == "5px"


def test_scroll_margin_shorthand_four_tokens() -> None:
    """scroll-margin: 1px 2px 3px 4px maps top/right/bottom/left individually (AC-3)."""
    el = _make_element_with_inline("scroll-margin", "1px 2px 3px 4px")
    style = el.get_computed_style()
    assert style.get_property_value("scroll-margin-top") == "1px"
    assert style.get_property_value("scroll-margin-right") == "2px"
    assert style.get_property_value("scroll-margin-bottom") == "3px"
    assert style.get_property_value("scroll-margin-left") == "4px"


# ---------------------------------------------------------------------------
# AC-4: scroll-padding longhands
# ---------------------------------------------------------------------------


def test_supports_scroll_padding_top() -> None:
    """CSS.supports("scroll-padding-top", "5px") returns True (AC-4)."""
    assert CSS.supports("scroll-padding-top", "5px") is True


def test_supports_scroll_padding_right() -> None:
    """CSS.supports("scroll-padding-right", "5px") returns True (AC-4)."""
    assert CSS.supports("scroll-padding-right", "5px") is True


def test_supports_scroll_padding_bottom() -> None:
    """CSS.supports("scroll-padding-bottom", "5px") returns True (AC-4)."""
    assert CSS.supports("scroll-padding-bottom", "5px") is True


def test_supports_scroll_padding_left() -> None:
    """CSS.supports("scroll-padding-left", "5px") returns True (AC-4)."""
    assert CSS.supports("scroll-padding-left", "5px") is True


# ---------------------------------------------------------------------------
# AC-5: scroll-padding shorthand expansion
# ---------------------------------------------------------------------------


def test_scroll_padding_shorthand_two_tokens() -> None:
    """scroll-padding: 5px 10px expands top/bottom=5px, right/left=10px (AC-5)."""
    el = _make_element_with_inline("scroll-padding", "5px 10px")
    style = el.get_computed_style()
    assert style.get_property_value("scroll-padding-top") == "5px"
    assert style.get_property_value("scroll-padding-right") == "10px"
    assert style.get_property_value("scroll-padding-bottom") == "5px"
    assert style.get_property_value("scroll-padding-left") == "10px"


def test_scroll_padding_shorthand_one_token() -> None:
    """scroll-padding: auto broadcasts to all four longhands (AC-5)."""
    el = _make_element_with_inline("scroll-padding", "auto")
    style = el.get_computed_style()
    assert style.get_property_value("scroll-padding-top") == "auto"
    assert style.get_property_value("scroll-padding-right") == "auto"
    assert style.get_property_value("scroll-padding-bottom") == "auto"
    assert style.get_property_value("scroll-padding-left") == "auto"


# ---------------------------------------------------------------------------
# AC-6: mask longhands
# ---------------------------------------------------------------------------


def test_supports_mask_image() -> None:
    """CSS.supports("mask-image", "none") returns True (AC-6)."""
    assert CSS.supports("mask-image", "none") is True


def test_supports_mask_mode() -> None:
    """CSS.supports("mask-mode", "match-source") returns True (AC-6)."""
    assert CSS.supports("mask-mode", "match-source") is True


def test_supports_mask_position() -> None:
    """CSS.supports("mask-position", "center") returns True (AC-6)."""
    assert CSS.supports("mask-position", "center") is True


def test_supports_mask_size() -> None:
    """CSS.supports("mask-size", "auto") returns True (AC-6)."""
    assert CSS.supports("mask-size", "auto") is True


def test_supports_mask_repeat() -> None:
    """CSS.supports("mask-repeat", "no-repeat") returns True (AC-6)."""
    assert CSS.supports("mask-repeat", "no-repeat") is True


def test_supports_mask_origin() -> None:
    """CSS.supports("mask-origin", "border-box") returns True (AC-6)."""
    assert CSS.supports("mask-origin", "border-box") is True


def test_supports_mask_clip() -> None:
    """CSS.supports("mask-clip", "border-box") returns True (AC-6)."""
    assert CSS.supports("mask-clip", "border-box") is True


def test_supports_mask_composite() -> None:
    """CSS.supports("mask-composite", "add") returns True (AC-6)."""
    assert CSS.supports("mask-composite", "add") is True


def test_mask_shorthand_single_token() -> None:
    """mask: none broadcasts to all 8 longhands (AC-6, positional broadcast)."""
    el = _make_element_with_inline("mask", "none")
    style = el.get_computed_style()
    assert style.get_property_value("mask-image") == "none"


def test_mask_shorthand_multi_token() -> None:
    """mask: url(m.svg) no-repeat expands positionally to mask-image and mask-mode (AC-6)."""
    el = _make_element_with_inline("mask", "url(m.svg) no-repeat")
    style = el.get_computed_style()
    assert style.get_property_value("mask-image") == "url(m.svg)"
    assert style.get_property_value("mask-mode") == "no-repeat"


# ---------------------------------------------------------------------------
# AC-7: touch-action
# ---------------------------------------------------------------------------


def test_supports_touch_action() -> None:
    """CSS.supports("touch-action", "none") returns True (AC-7)."""
    assert CSS.supports("touch-action", "none") is True


def test_touch_action_via_stylesheet() -> None:
    """Stylesheet touch-action is stored and retrieved from computed style (AC-7)."""
    el = _make_element("touch-action: none")
    assert el.get_computed_style().get_property_value("touch-action") == "none"


# ---------------------------------------------------------------------------
# AC-8: accent-color
# ---------------------------------------------------------------------------


def test_supports_accent_color() -> None:
    """CSS.supports("accent-color", "red") returns True (AC-8)."""
    assert CSS.supports("accent-color", "red") is True


# ---------------------------------------------------------------------------
# AC-9: caret-color
# ---------------------------------------------------------------------------


def test_supports_caret_color() -> None:
    """CSS.supports("caret-color", "auto") returns True (AC-9)."""
    assert CSS.supports("caret-color", "auto") is True


# ---------------------------------------------------------------------------
# AC-10: scrollbar-width
# ---------------------------------------------------------------------------


def test_supports_scrollbar_width() -> None:
    """CSS.supports("scrollbar-width", "thin") returns True (AC-10)."""
    assert CSS.supports("scrollbar-width", "thin") is True


# ---------------------------------------------------------------------------
# AC-11: scrollbar-color
# ---------------------------------------------------------------------------


def test_supports_scrollbar_color() -> None:
    """CSS.supports("scrollbar-color", "red blue") returns True (AC-11)."""
    assert CSS.supports("scrollbar-color", "red blue") is True


# ---------------------------------------------------------------------------
# AC-12: _INITIAL_VALUE_BASELINE count
# ---------------------------------------------------------------------------


def test_initial_value_baseline_count() -> None:
    """_INITIAL_VALUE_BASELINE must have exactly 416 entries after Track 114 (AC-12).

    Track 94 established 286; Track 96 (ADR-295, BACK-317) added 48 more (334);
    Track 98 (ADR-297, BACK-319) added 19 shorthand registrations (353);
    Track 108 (ADR-307, BACK-328) added 14 longhands + 1 shorthand sentinel (368);
    Track 109 (ADR-308, BACK-329) added 2 inherited longhands (370);
    Track 110 (ADR-309, BACK-330) added 10 CSS property longhands (380);
    Track 111 (ADR-310, BACK-331) added 8 longhands + 1 shorthand sentinel (389);
    Track 112 (ADR-311, BACK-333) added 9 longhands (398);
    Track 113 (ADR-312, BACK-334) added 11 entries (409);
    Track 114 (ADR-313, BACK-335) added 7 entries (416).
    """
    assert len(_INITIAL_VALUE_BASELINE) == 416


# ---------------------------------------------------------------------------
# AC-13 variant: stylesheet path for touch-action, accent-color, text-overflow
# ---------------------------------------------------------------------------


def test_stylesheet_path_new_properties() -> None:
    """get_computed_style returns values for touch-action, accent-color, text-overflow (AC-13)."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("class", "c")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(".c { touch-action: none; accent-color: red; text-overflow: ellipsis }")
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("touch-action") == "none"
    assert style.get_property_value("accent-color") == "red"
    assert style.get_property_value("text-overflow") == "ellipsis"
