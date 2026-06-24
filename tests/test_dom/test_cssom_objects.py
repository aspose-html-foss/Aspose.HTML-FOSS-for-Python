"""Tests for CSSOM IDL completeness: CSSRule constants, CSSRuleList.item(),
CSSStyleRule.selector_text, CSSStyleSheet metadata (, )."""
from __future__ import annotations

from aspose_html.cssom import (
    CSSMediaRule,
    CSSRule,
    CSSRuleList,
    CSSStyleRule,
    CSSStyleSheet,
)


# ---------------------------------------------------------------------------
# CSSRule type constants
# ---------------------------------------------------------------------------


def test_css_rule_type_constants() -> None:
    """All nine CSSOM §6.6 Table 1 type constants must be present on CSSRule."""
    assert CSSRule.STYLE_RULE == 1
    assert CSSRule.CHARSET_RULE == 2
    assert CSSRule.IMPORT_RULE == 3
    assert CSSRule.MEDIA_RULE == 4
    assert CSSRule.FONT_FACE_RULE == 5
    assert CSSRule.PAGE_RULE == 6
    assert CSSRule.KEYFRAMES_RULE == 7
    assert CSSRule.KEYFRAME_RULE == 8
    assert CSSRule.NAMESPACE_RULE == 10
    assert CSSRule.SUPPORTS_RULE == 12


# ---------------------------------------------------------------------------
# CSSRuleList.item()
# ---------------------------------------------------------------------------


def test_css_rule_list_item_in_range() -> None:
    """item(0) returns the first rule when the list has at least one rule."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    rl = sheet.css_rules
    assert rl.item(0) is rl[0]


def test_css_rule_list_item_out_of_range() -> None:
    """item() returns None for out-of-range indices — no IndexError."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    rl = sheet.css_rules
    assert rl.item(99) is None
    assert rl.item(-1) is None


# ---------------------------------------------------------------------------
# CSSStyleRule.selector_text
# ---------------------------------------------------------------------------


def test_css_style_rule_selector_text() -> None:
    """selector_text equals the selector string used in the input CSS."""
    sheet = CSSStyleSheet.from_text("div.foo { color: red; }")
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSStyleRule)
    assert rule.selector_text == "div.foo"


def test_css_style_rule_selector_text_is_read_only() -> None:
    """selector_text is a read-only property — assignment must raise AttributeError."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSStyleRule)
    try:
        rule.selector_text = "span"  # type: ignore[misc]
        raise AssertionError("Expected AttributeError")
    except AttributeError:
        pass


# ---------------------------------------------------------------------------
# CSSStyleSheet metadata — title
# ---------------------------------------------------------------------------


def test_css_style_sheet_title() -> None:
    """CSSStyleSheet.from_text(..., title='T').title == 'T'."""
    sheet = CSSStyleSheet.from_text("p { color: red }", title="T")
    assert sheet.title == "T"


def test_css_style_sheet_title_default() -> None:
    """title defaults to empty string when not specified."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    assert sheet.title == ""


# ---------------------------------------------------------------------------
# CSSStyleSheet metadata — href
# ---------------------------------------------------------------------------


def test_css_style_sheet_href() -> None:
    """CSSStyleSheet.from_text(..., href='/a.css').href == '/a.css'."""
    sheet = CSSStyleSheet.from_text("p { color: red }", href="/a.css")
    assert sheet.href == "/a.css"


def test_css_style_sheet_href_default_none() -> None:
    """href defaults to None for inline sheets."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    assert sheet.href is None


# ---------------------------------------------------------------------------
# CSSStyleSheet metadata — media
# ---------------------------------------------------------------------------


def test_css_style_sheet_media() -> None:
    """CSSStyleSheet.from_text(..., media='screen').media == 'screen'."""
    sheet = CSSStyleSheet.from_text("p { color: red }", media="screen")
    assert sheet.media == "screen"


def test_css_style_sheet_media_default() -> None:
    """media defaults to empty string when not specified."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    assert sheet.media == ""


# ---------------------------------------------------------------------------
# CSSStyleSheet metadata — disabled / owner_rule
# ---------------------------------------------------------------------------


def test_css_style_sheet_disabled_default() -> None:
    """disabled is always False (read-only; sheet enabling not implemented)."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    assert sheet.disabled is False


def test_css_style_sheet_owner_rule_none() -> None:
    """owner_rule is always None (no @import ownership in this impl)."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    assert sheet.owner_rule is None


# ---------------------------------------------------------------------------
# CSSMediaRule — css_rules type
# ---------------------------------------------------------------------------


def test_css_media_rule_css_rules_type() -> None:
    """A CSSMediaRule's css_rules attribute is a CSSRuleList."""
    sheet = CSSStyleSheet.from_text("@media screen { p { color: red } }")
    media = sheet.css_rules[0]
    assert isinstance(media, CSSMediaRule)
    assert isinstance(media.css_rules, CSSRuleList)


# ---------------------------------------------------------------------------
# parent_style_sheet and parent_rule linkage
# ---------------------------------------------------------------------------


def test_css_style_rule_parent_style_sheet() -> None:
    """Top-level rules reference their containing stylesheet."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    rule = sheet.css_rules[0]
    assert rule.parent_style_sheet is sheet


def test_css_rule_parent_rule_top_level_is_none() -> None:
    """Top-level rules have parent_rule == None."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    rule = sheet.css_rules[0]
    assert rule.parent_rule is None
