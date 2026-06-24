"""Tests for CSSStyleSheet.insert_rule / delete_rule (, ).

13 test cases covering CSSOM §6.4 write path.
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSSStyleSheet, CSSStyleRule
from aspose_html.dom import IndexSizeError


# ---------------------------------------------------------------------------
# insert_rule — append and return value
# ---------------------------------------------------------------------------


def test_insert_rule_appends_by_default() -> None:
    """insert_rule on empty sheet appends the rule and returns index 0."""
    sheet = CSSStyleSheet()
    idx = sheet.insert_rule("p { color: red }")
    assert idx == 0
    assert sheet.css_rules.length == 1


def test_insert_rule_at_index_zero() -> None:
    """insert_rule at index 0 puts the new rule first; existing rule shifts."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    sheet.insert_rule("div { margin: 0 }", 0)
    assert sheet.css_rules.length == 2
    assert isinstance(sheet.css_rules[0], CSSStyleRule)
    assert sheet.css_rules[0].selector_text == "div"
    assert sheet.css_rules[1].selector_text == "p"


def test_insert_rule_returns_index() -> None:
    """Return value of insert_rule equals the actual insertion position."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    # Append
    idx_append = sheet.insert_rule("div { margin: 0 }")
    assert idx_append == 1
    # Insert at beginning
    idx_head = sheet.insert_rule("span { font-size: 1em }", 0)
    assert idx_head == 0
    # Insert in middle
    idx_mid = sheet.insert_rule("em { color: blue }", 1)
    assert idx_mid == 1


# ---------------------------------------------------------------------------
# insert_rule — error cases
# ---------------------------------------------------------------------------


def test_insert_rule_out_of_range_raises() -> None:
    """insert_rule with index > len(css_rules) raises IndexSizeError."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    with pytest.raises(IndexSizeError):
        sheet.insert_rule("div { margin: 0 }", 99)


def test_insert_rule_negative_index_raises() -> None:
    """insert_rule with a negative index raises IndexSizeError."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    with pytest.raises(IndexSizeError):
        sheet.insert_rule("div { margin: 0 }", -1)


# ---------------------------------------------------------------------------
# delete_rule — removal and length
# ---------------------------------------------------------------------------


def test_delete_rule_removes_first() -> None:
    """delete_rule(0) removes the first rule; the former second rule is now first."""
    sheet = CSSStyleSheet.from_text("p { color: red } div { margin: 0 }")
    assert sheet.css_rules.length == 2
    sheet.delete_rule(0)
    assert sheet.css_rules.length == 1
    assert sheet.css_rules[0].selector_text == "div"


def test_delete_rule_removes_last() -> None:
    """delete_rule at the last index removes only the last rule."""
    sheet = CSSStyleSheet.from_text("p { color: red } div { margin: 0 }")
    last = sheet.css_rules.length - 1
    sheet.delete_rule(last)
    assert sheet.css_rules.length == 1
    assert sheet.css_rules[0].selector_text == "p"


# ---------------------------------------------------------------------------
# delete_rule — error cases
# ---------------------------------------------------------------------------


def test_delete_rule_out_of_range_raises() -> None:
    """delete_rule with index beyond the last rule raises IndexSizeError."""
    sheet = CSSStyleSheet.from_text("p { color: red } div { margin: 0 }")
    with pytest.raises(IndexSizeError):
        sheet.delete_rule(5)


def test_delete_rule_empty_sheet_raises() -> None:
    """delete_rule on an empty sheet raises IndexSizeError."""
    sheet = CSSStyleSheet()
    with pytest.raises(IndexSizeError):
        sheet.delete_rule(0)


# ---------------------------------------------------------------------------
# Round-trip and live list
# ---------------------------------------------------------------------------


def test_insert_then_delete_roundtrip() -> None:
    """insert_rule followed by delete_rule leaves the original sheet unchanged."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    original_rule = sheet.css_rules[0]
    idx = sheet.insert_rule("div { margin: 0 }")
    sheet.delete_rule(idx)
    assert sheet.css_rules.length == 1
    assert sheet.css_rules[0] is original_rule


def test_css_rules_live_after_insert() -> None:
    """A reference to css_rules captured before insert reflects the change."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    rules = sheet.css_rules  # capture before mutation
    assert len(rules) == 1
    sheet.insert_rule("div { margin: 0 }")
    # Live provider — same reference reflects new length
    assert len(rules) == 2


# ---------------------------------------------------------------------------
# parent_style_sheet linkage
# ---------------------------------------------------------------------------


def test_parent_style_sheet_set_on_insert() -> None:
    """rule.parent_style_sheet is set to the sheet after insert_rule."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    sheet.insert_rule("div { margin: 0 }")
    rule = sheet.css_rules[1]
    assert rule.parent_style_sheet is sheet


def test_parent_style_sheet_cleared_on_delete() -> None:
    """rule.parent_style_sheet is cleared to None after delete_rule."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    rule = sheet.css_rules[0]
    assert rule.parent_style_sheet is sheet
    sheet.delete_rule(0)
    assert rule.parent_style_sheet is None
