"""Tests for match_media() real evaluation and CSSStyleDeclaration priority.

 /  —  Group A.

Covers:
- MediaQueryList.matches real evaluation against _MEDIA_BASELINE_ENV
- Window.match_media() delegation
- CSSStyleDeclaration.get_property_priority()
- CSSStyleDeclaration.set_property() 3-arg form with priority
- Round-trip !important via css_text
- Cascade resolution: inline !important beats normal author rule
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document
from aspose_html.dom._window import MediaQueryList, Window


# ---------------------------------------------------------------------------
# MediaQueryList.matches — real evaluation
# ---------------------------------------------------------------------------

def test_match_media_screen_default():
    """MediaQueryList("screen").matches is True in default screen env (AC #1)."""
    assert MediaQueryList("screen").matches is True


def test_match_media_print_default():
    """MediaQueryList("print").matches is False in default screen env (AC #2)."""
    assert MediaQueryList("print").matches is False


def test_match_media_prefers_color_scheme_light():
    """MediaQueryList matches prefers-color-scheme: light (AC #3)."""
    assert MediaQueryList("(prefers-color-scheme: light)").matches is True


def test_match_media_prefers_color_scheme_dark():
    """MediaQueryList does not match prefers-color-scheme: dark by default."""
    assert MediaQueryList("(prefers-color-scheme: dark)").matches is False


def test_match_media_all():
    """`all` matches in every valid media environment."""
    assert MediaQueryList("all").matches is True


def test_match_media_unsupported_returns_false():
    """Unsupported feature queries (e.g. width) return False."""
    assert MediaQueryList("(width: 300px)").matches is False


def test_window_match_media_delegates():
    """Window.match_media delegates to _media_query_matches (AC #1 via Window)."""
    doc = Document()
    win = doc.default_view
    assert win.match_media("screen").matches is True
    assert win.match_media("print").matches is False


# ---------------------------------------------------------------------------
# CSSStyleDeclaration.get_property_priority
# ---------------------------------------------------------------------------

def test_get_property_priority_absent():
    """get_property_priority returns '' for a property that was never set."""
    doc = Document()
    el = doc.create_element("div")
    assert el.style.get_property_priority("color") == ""


def test_get_property_priority_normal():
    """set_property without priority arg → get_property_priority returns ''."""
    doc = Document()
    el = doc.create_element("div")
    el.style.set_property("color", "red")
    assert el.style.get_property_priority("color") == ""


def test_get_property_priority_important():
    """set_property with priority='important' → get_property_priority returns 'important' (AC #5)."""
    doc = Document()
    el = doc.create_element("div")
    el.style.set_property("color", "red", "important")
    assert el.style.get_property_priority("color") == "important"


# ---------------------------------------------------------------------------
# CSSStyleDeclaration.set_property — 3-arg form
# ---------------------------------------------------------------------------

def test_set_property_important_written_to_attribute():
    """set_property with priority writes !important to the style attribute (AC #4)."""
    doc = Document()
    el = doc.create_element("div")
    el.style.set_property("color", "red", "important")
    attr = el.get_attribute("style")
    assert attr is not None
    assert "!important" in attr
    assert "color" in attr
    assert "red" in attr


def test_set_property_important_beats_normal_author():
    """Inline !important declaration wins over a normal author stylesheet rule (AC #6)."""
    from aspose_html import HTMLDocument
    from aspose_html.cssom import CSSStyleSheet

    doc = HTMLDocument.parse('<div id="x">hi</div>')
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: blue; }")
    doc.attach_style_sheet(sheet)

    el = doc.get_element_by_id("x")
    # Without !important the stylesheet rule wins (there's only one candidate)
    assert el.get_computed_style().get_property_value("color") == "blue"

    # Set inline !important — must beat the normal author rule
    el.style.set_property("color", "red", "important")
    assert el.get_computed_style().get_property_value("color") == "red"


def test_parse_important_roundtrip():
    """css_text assignment with !important → get_property_priority returns 'important' (AC test 13)."""
    doc = Document()
    el = doc.create_element("div")
    el.style.css_text = "color: red !important"
    assert el.style.get_property_priority("color") == "important"
    assert el.style["color"] == "red"


def test_set_property_invalid_priority_treated_as_normal():
    """Unrecognised priority string is treated as '' — no error raised (AC test 14)."""
    doc = Document()
    el = doc.create_element("div")
    el.style.set_property("color", "red", "maybe")
    # Priority not 'important' → stored as normal
    assert el.style.get_property_priority("color") == ""
    assert el.style["color"] == "red"
