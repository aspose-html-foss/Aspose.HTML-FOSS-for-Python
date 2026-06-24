"""Tests for the UA default stylesheet ( / , ).

Covers:
* the transcribed ``_UA_DISPLAY`` table and ``ua_display_for`` / the
  ``ua_declarations_for`` special case (FR-1, FR-2, AC-1, AC-2);
* cascade composition — author/inline override the UA default, and the
  ``input[type=hidden i]`` ``!important`` rule beats author styles
  (FR-3, AC-3, AC-4);
* the immutability discipline (, AC-8);
* the leaf-module discipline (AC-10).

Box-tree downstream effects (FR-5 / FR-6, AC-5) are covered in
``tests/test_layout/test_box_tree.py``.
"""
from __future__ import annotations

import types

import pytest

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.dom._ua_stylesheet import (
    _UA_DISPLAY,
    ua_declarations_for,
    ua_display_for,
)


def _styled(tag: str):
    doc = Document()
    el = doc.create_element(tag)
    doc.append_child(el)
    return doc, el


# --- transcribed table (FR-2 / AC-1) -------------------------------------

# Every tag → expected default display, transcribed verbatim from WHATWG
# HTML §15.3 (see _ua_stylesheet.py for the per-subsection citations). The
# expected values here mirror the spec listings exactly.
_EXPECTED_DISPLAY = {
    # §15.3.1 Hidden elements → none
    "area": "none", "base": "none", "basefont": "none", "datalist": "none",
    "head": "none", "link": "none", "meta": "none", "noembed": "none",
    "noframes": "none", "param": "none", "rp": "none", "script": "none",
    "style": "none", "template": "none", "title": "none",
    # §15.3.2 The page → block
    "html": "block", "body": "block",
    # §15.3.3 Flow content → block (+ slot → contents)
    "address": "block", "blockquote": "block", "center": "block",
    "dialog": "block", "div": "block", "figure": "block",
    "figcaption": "block", "footer": "block", "form": "block",
    "header": "block", "hr": "block", "legend": "block", "listing": "block",
    "main": "block", "p": "block", "plaintext": "block", "pre": "block",
    "search": "block", "xmp": "block", "slot": "contents",
    # §15.3.4 Phrasing content → ruby / ruby-text
    "ruby": "ruby", "rt": "ruby-text",
    # §15.3.6 Sections and headings → block (:heading == h1-h6)
    "article": "block", "aside": "block", "h1": "block", "h2": "block",
    "h3": "block", "h4": "block", "h5": "block", "h6": "block",
    "hgroup": "block", "nav": "block", "section": "block",
    # §15.3.7 Lists → block (+ li → list-item)
    "dir": "block", "dd": "block", "dl": "block", "dt": "block",
    "menu": "block", "ol": "block", "ul": "block", "li": "list-item",
    # §15.3.8 Tables
    "table": "table", "caption": "table-caption",
    "colgroup": "table-column-group", "col": "table-column",
    "thead": "table-header-group", "tbody": "table-row-group",
    "tfoot": "table-footer-group", "tr": "table-row",
    "td": "table-cell", "th": "table-cell",
}


@pytest.mark.parametrize("tag,expected", sorted(_EXPECTED_DISPLAY.items()))
def test_ua_display_table_matches_spec(tag: str, expected: str) -> None:
    """Every FR-2 tag maps to its verbatim §15.3 display value."""
    assert ua_display_for(tag) == expected


def test_ua_display_table_covers_exactly_the_spec_tags() -> None:
    """No extra (hand-invented) entries, and every spec tag present (AC-1)."""
    assert set(_UA_DISPLAY) == set(_EXPECTED_DISPLAY)


@pytest.mark.parametrize("tag", ["span", "a", "em", "strong", "cite", "i", "b",
                                 "code", "sub", "sup", "my-custom-element"])
def test_unmatched_tags_have_no_ua_display(tag: str) -> None:
    """§15.3 defines no display for these → fall through to initial inline (FR-4)."""
    assert ua_display_for(tag) is None


def test_ua_display_is_case_insensitive() -> None:
    assert ua_display_for("DIV") == "block"
    assert ua_display_for("Td") == "table-cell"


# --- ua_declarations_for + input[type=hidden i] (AC-2) -------------------


def test_declarations_for_type_selector() -> None:
    _, div = _styled("div")
    assert list(ua_declarations_for(div)) == [("display", "block", False)]


def test_declarations_for_unmatched_tag_is_empty() -> None:
    _, span = _styled("span")
    assert list(ua_declarations_for(span)) == []


def test_input_hidden_yields_none_important() -> None:
    _, inp = _styled("input")
    inp.set_attribute("type", "hidden")
    assert list(ua_declarations_for(inp)) == [("display", "none", True)]


def test_input_hidden_is_ascii_case_insensitive() -> None:
    _, inp = _styled("input")
    inp.set_attribute("type", "HiDDeN")
    assert list(ua_declarations_for(inp)) == [("display", "none", True)]


def test_input_non_hidden_has_no_ua_display() -> None:
    # `input` is not a type-selector entry and only the hidden type has an
    # in-scope rule → text inputs fall through to the §2 initial.
    _, inp = _styled("input")
    inp.set_attribute("type", "text")
    assert list(ua_declarations_for(inp)) == []


def test_input_without_type_has_no_ua_display() -> None:
    _, inp = _styled("input")
    assert list(ua_declarations_for(inp)) == []


# --- cascade composition (FR-1, FR-3, AC-3, AC-4) ------------------------


def test_get_computed_style_returns_ua_default() -> None:
    _, div = _styled("div")
    assert div.get_computed_style().get_property_value("display") == "block"


def test_author_rule_overrides_ua_default() -> None:
    doc, div = _styled("div")
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { display: flex }")
    doc.attach_style_sheet(sheet)
    assert div.get_computed_style().get_property_value("display") == "flex"


def test_inline_style_overrides_ua_default() -> None:
    _, div = _styled("div")
    div.style.set_property("display", "inline")
    assert div.get_computed_style().get_property_value("display") == "inline"


def test_ua_important_beats_author_display() -> None:
    """input[type=hidden] none !important beats an author display:block (AC-4)."""
    doc, inp = _styled("input")
    inp.set_attribute("type", "hidden")
    sheet = CSSStyleSheet()
    sheet.replace_sync("input { display: block }")
    doc.attach_style_sheet(sheet)
    assert inp.get_computed_style().get_property_value("display") == "none"


def test_author_important_loses_to_ua_important() -> None:
    """ua !important (origin tier 2) outranks author !important (tier 1)."""
    doc, inp = _styled("input")
    inp.set_attribute("type", "hidden")
    sheet = CSSStyleSheet()
    sheet.replace_sync("input { display: block !important }")
    doc.attach_style_sheet(sheet)
    assert inp.get_computed_style().get_property_value("display") == "none"


def test_unmatched_element_resolves_to_no_display() -> None:
    """span has no UA display → resolves to the §2 initial (absent => '')."""
    _, span = _styled("span")
    # No author rule, no UA rule → display not surfaced in the snapshot.
    assert span.get_computed_style().get_property_value("display") == ""


# ---  immutability (AC-8) -----------------------------------------


def test_ua_display_table_is_immutable() -> None:
    assert isinstance(_UA_DISPLAY, types.MappingProxyType)
    with pytest.raises(TypeError):
        _UA_DISPLAY["div"] = "inline"  # type: ignore[index]
