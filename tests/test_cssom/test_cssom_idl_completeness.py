"""Tests for CSSOM IDL completeness —  / .

Covers: CSSDeclarationBlock (length, item, parent_rule, get/set_property_priority),
CSSStyleSheet (parent_style_sheet, rules, add_rule, remove_rule),
CSSStyleDeclaration (parent_rule).
"""
import pytest

from aspose_html.cssom._declarations import CSSDeclarationBlock
from aspose_html.cssom import CSSStyleSheet


# ---------------------------------------------------------------------------
# CSSDeclarationBlock — length
# ---------------------------------------------------------------------------

def test_declaration_block_length():
    b = CSSDeclarationBlock.parse("color: red; font-weight: bold")
    assert b.length == 2


def test_declaration_block_length_empty():
    b = CSSDeclarationBlock()
    assert b.length == 0


# ---------------------------------------------------------------------------
# CSSDeclarationBlock — item
# ---------------------------------------------------------------------------

def test_declaration_block_item():
    b = CSSDeclarationBlock.parse("color: red; margin: 0")
    assert b.item(0) == "color"
    assert b.item(1) == "margin"
    assert b.item(99) == ""
    assert b.item(-1) == ""


# ---------------------------------------------------------------------------
# CSSDeclarationBlock — parent_rule
# ---------------------------------------------------------------------------

def test_declaration_block_parent_rule_default_none():
    b = CSSDeclarationBlock()
    assert b.parent_rule is None


def test_declaration_block_parent_rule_wired_from_style_rule():
    sheet = CSSStyleSheet.from_text("p { color: red }")
    rule = sheet.css_rules[0]
    assert rule.style.parent_rule is rule


# ---------------------------------------------------------------------------
# CSSDeclarationBlock — get_property_priority / set_property_priority
# ---------------------------------------------------------------------------

def test_declaration_block_set_get_priority():
    b = CSSDeclarationBlock()
    b.set_property("color", "red")
    b.set_property_priority("color", "important")
    assert b.get_property_priority("color") == "important"
    assert "!important" in b.css_text
    # unknown property: silent no-op
    b.set_property_priority("margin", "important")  # no KeyError


def test_declaration_block_priority_in_css_text():
    b = CSSDeclarationBlock()
    b.set_property("color", "red")
    b.set_property_priority("color", "important")
    assert b.css_text == "color: red !important"


def test_declaration_block_priority_reset():
    b = CSSDeclarationBlock()
    b.set_property("color", "red")
    b.set_property_priority("color", "important")
    assert b.get_property_priority("color") == "important"
    b.set_property_priority("color", "")
    assert b.get_property_priority("color") == ""
    assert "!important" not in b.css_text


# ---------------------------------------------------------------------------
# CSSDeclarationBlock — existing API regression after _properties format change
# ---------------------------------------------------------------------------

def test_declaration_block_existing_api_unchanged():
    b = CSSDeclarationBlock.parse("color: red; margin: 8px")
    assert b.get_property_value("color") == "red"
    assert b.remove_property("margin") == "8px"
    b.set_property("font-size", "12px")
    assert b.get_property_value("font-size") == "12px"
    assert len(b) == 2  # color, font-size


def test_declaration_block_iter_yields_names():
    b = CSSDeclarationBlock.parse("color: red; margin: 0")
    assert list(b) == ["color", "margin"]


def test_declaration_block_getitem_setitem_delitem():
    b = CSSDeclarationBlock()
    b["color"] = "blue"
    assert b["color"] == "blue"
    del b["color"]
    assert b["color"] == ""


def test_declaration_block_len_dunder_equals_length():
    b = CSSDeclarationBlock.parse("color: red; padding: 4px")
    assert len(b) == b.length == 2


def test_declaration_block_css_text_round_trip():
    b = CSSDeclarationBlock.parse("color: red; margin: 0")
    assert b.css_text == "color: red; margin: 0"


def test_declaration_block_remove_property_absent():
    b = CSSDeclarationBlock()
    # must return '' and not raise
    assert b.remove_property("nonexistent") == ""


# ---------------------------------------------------------------------------
# CSSStyleSheet — parent_style_sheet
# ---------------------------------------------------------------------------

def test_stylesheet_parent_style_sheet_none():
    sheet = CSSStyleSheet.from_text("p { color: red }")
    assert sheet.parent_style_sheet is None


# ---------------------------------------------------------------------------
# CSSStyleSheet — rules alias
# ---------------------------------------------------------------------------

def test_stylesheet_rules_alias():
    sheet = CSSStyleSheet.from_text("p { color: red }")
    assert sheet.rules is sheet.css_rules


# ---------------------------------------------------------------------------
# CSSStyleSheet — add_rule
# ---------------------------------------------------------------------------

def test_stylesheet_add_rule_returns_minus_one():
    sheet = CSSStyleSheet.from_text("p { color: red }")
    result = sheet.add_rule("div", "margin: 0")
    assert result == -1


def test_stylesheet_add_rule_increases_length():
    sheet = CSSStyleSheet.from_text("p { color: red }")
    sheet.add_rule("div", "margin: 0")
    assert len(sheet.css_rules) == 2


def test_stylesheet_add_rule_appends_by_default():
    sheet = CSSStyleSheet.from_text("p { color: red }")
    sheet.add_rule("div", "margin: 0")
    assert sheet.css_rules[1].selector_text == "div"


def test_stylesheet_add_rule_with_index():
    sheet = CSSStyleSheet.from_text("p { color: red }")
    sheet.add_rule("div", "margin: 0", 0)
    assert sheet.css_rules[0].selector_text == "div"


# ---------------------------------------------------------------------------
# CSSStyleSheet — remove_rule
# ---------------------------------------------------------------------------

def test_stylesheet_remove_rule():
    sheet = CSSStyleSheet.from_text("p { color: red }")
    sheet.remove_rule(0)
    assert len(sheet.css_rules) == 0


def test_stylesheet_remove_rule_default_index():
    sheet = CSSStyleSheet.from_text("p { color: red } div { margin: 0 }")
    sheet.remove_rule()  # default index=0
    assert sheet.css_rules[0].selector_text == "div"


# ---------------------------------------------------------------------------
# CSSStyleDeclaration — parent_rule
# ---------------------------------------------------------------------------

def test_style_declaration_parent_rule_none():
    from aspose_html.dom import Document
    doc = Document()
    el = doc.create_element("div")
    assert el.style.parent_rule is None
