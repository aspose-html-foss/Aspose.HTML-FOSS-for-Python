"""Tests for Element.style property and CSSStyleDeclaration.

All 21 required test cases from ADR-010 (BACK-14).
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, CSSStyleDeclaration


@pytest.fixture
def doc() -> Document:
    return Document()


# -----------------------------------------------------------------------
# AC-1: el.style returns a CSSStyleDeclaration; same object on each call
# -----------------------------------------------------------------------


def test_style_getter_returns_css_style_declaration(doc: Document) -> None:
    el = doc.create_element("div")
    assert isinstance(el.style, CSSStyleDeclaration)


def test_style_getter_cached_identity(doc: Document) -> None:
    el = doc.create_element("div")
    assert el.style is el.style


# -----------------------------------------------------------------------
# AC-2: __getitem__ — read property values
# -----------------------------------------------------------------------


def test_style_getitem_present(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("style", "color: red")
    assert el.style["color"] == "red"


def test_style_getitem_absent_returns_empty_string(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("style", "color: red")
    assert el.style["font-size"] == ""


# -----------------------------------------------------------------------
# AC-3: __setitem__ — write property values
# -----------------------------------------------------------------------


def test_style_setitem_creates_attribute(doc: Document) -> None:
    """Setting a property when no style attribute exists creates the attribute."""
    el = doc.create_element("div")
    assert not el.has_attribute("style")
    el.style["color"] = "blue"
    assert el.get_attribute("style") == "color: blue"


def test_style_setitem_adds_to_existing(doc: Document) -> None:
    """Existing properties are preserved when a new property is added."""
    el = doc.create_element("div")
    el.set_attribute("style", "color: red")
    el.style["font-size"] = "12px"
    style_attr = el.get_attribute("style")
    assert "color: red" in style_attr
    assert "font-size: 12px" in style_attr


def test_style_setitem_overwrites_existing(doc: Document) -> None:
    """Writing the same property key updates the value in-place."""
    el = doc.create_element("div")
    el.style["color"] = "red"
    el.style["color"] = "blue"
    assert el.style["color"] == "blue"
    # Only one "color" declaration in the attribute string
    assert el.get_attribute("style").count("color") == 1


# -----------------------------------------------------------------------
# AC-4: __delitem__ — remove property values
# -----------------------------------------------------------------------


def test_style_delitem_removes_property(doc: Document) -> None:
    el = doc.create_element("div")
    el.style["color"] = "red"
    del el.style["color"]
    assert el.style["color"] == ""


def test_style_delitem_noop_on_absent(doc: Document) -> None:
    """Deleting an absent property does not raise."""
    el = doc.create_element("div")
    del el.style["margin"]  # must not raise


def test_style_delitem_clears_attribute_when_empty(doc: Document) -> None:
    """When the last property is removed the style attribute is removed entirely."""
    el = doc.create_element("div")
    el.style["color"] = "red"
    del el.style["color"]
    assert not el.has_attribute("style")


# -----------------------------------------------------------------------
# __len__ — count of set properties
# -----------------------------------------------------------------------


def test_style_len_empty(doc: Document) -> None:
    el = doc.create_element("div")
    assert len(el.style) == 0


def test_style_len_with_properties(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("style", "color: red; font-size: 12px")
    assert len(el.style) == 2


# -----------------------------------------------------------------------
# __iter__ — iterate over property names
# -----------------------------------------------------------------------


def test_style_iter_yields_property_names(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("style", "color: red; font-size: 12px")
    assert list(el.style) == ["color", "font-size"]


# -----------------------------------------------------------------------
# __contains__ — membership test
# -----------------------------------------------------------------------


def test_style_contains(doc: Document) -> None:
    el = doc.create_element("div")
    el.style["margin"] = "0"
    assert "margin" in el.style
    assert "padding" not in el.style


# -----------------------------------------------------------------------
# css_text property getter and setter
# -----------------------------------------------------------------------


def test_style_css_text_getter(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("style", "color: red; margin: 0")
    assert el.style.css_text == "color: red; margin: 0"


def test_style_css_text_setter(doc: Document) -> None:
    el = doc.create_element("div")
    el.style.css_text = "color: red; margin: 0"
    assert el.get_attribute("style") == "color: red; margin: 0"
    assert el.style["color"] == "red"
    assert el.style["margin"] == "0"


# -----------------------------------------------------------------------
# CSSOM-named methods
# -----------------------------------------------------------------------


def test_style_get_property_value(doc: Document) -> None:
    el = doc.create_element("div")
    el.style["color"] = "green"
    assert el.style.get_property_value("color") == "green"
    assert el.style.get_property_value("margin") == ""


def test_style_set_property(doc: Document) -> None:
    el = doc.create_element("div")
    el.style.set_property("color", "red")
    assert el.style["color"] == "red"
    assert el.get_attribute("style") == "color: red"


def test_style_remove_property_returns_old_value(doc: Document) -> None:
    el = doc.create_element("div")
    el.style["color"] = "red"
    old = el.style.remove_property("color")
    assert old == "red"
    assert el.style["color"] == ""


# -----------------------------------------------------------------------
# AC-5: live view — external changes to style attr visible immediately
# -----------------------------------------------------------------------


def test_style_live_view(doc: Document) -> None:
    """External set_attribute changes are reflected without recreating CSSStyleDeclaration."""
    el = doc.create_element("div")
    # Capture the CSSStyleDeclaration object (this is the cached instance)
    cached_ref = el.style
    # Modify the style attribute externally
    el.set_attribute("style", "margin: 0")
    # The cached object must reflect the new value
    assert el.style is cached_ref  # still the same object
    assert el.style["margin"] == "0"


# -----------------------------------------------------------------------
# Roundtrip: set multiple properties → read css_text → copy to new element
# -----------------------------------------------------------------------


def test_style_roundtrip(doc: Document) -> None:
    el = doc.create_element("div")
    el.style["color"] = "red"
    el.style["font-size"] = "14px"
    el.style["margin"] = "0"

    css = el.style.css_text

    el2 = doc.create_element("span")
    el2.style.css_text = css

    assert el2.style["color"] == "red"
    assert el2.style["font-size"] == "14px"
    assert el2.style["margin"] == "0"


# -----------------------------------------------------------------------
# Bonus edge-case tests (recommended in ADR-010, not counted toward AC-9)
# -----------------------------------------------------------------------


def test_style_malformed_skipped(doc: Document) -> None:
    """Declarations without a colon are silently skipped."""
    el = doc.create_element("div")
    el.set_attribute("style", "color: red; no-colon-here; font-size: 12px")
    assert len(el.style) == 2
    assert "no-colon-here" not in el.style
    assert el.style["color"] == "red"
    assert el.style["font-size"] == "12px"


def test_style_empty_style_attr(doc: Document) -> None:
    """An empty style attribute value results in an empty declaration."""
    el = doc.create_element("div")
    el.set_attribute("style", "")
    assert len(el.style) == 0


def test_style_property_name_case_folded(doc: Document) -> None:
    """Property names are lowercased — 'COLOR' and 'color' access the same property."""
    el = doc.create_element("div")
    el.set_attribute("style", "color: red")
    assert el.style["COLOR"] == "red"
    assert el.style["Color"] == "red"
    assert el.style["color"] == "red"
