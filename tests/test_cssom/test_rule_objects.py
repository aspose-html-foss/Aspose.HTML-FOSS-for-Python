from __future__ import annotations

import pytest

from aspose_html.cssom import CSSMediaRule, CSSRule, CSSStyleRule, CSSStyleSheet
from aspose_html.dom import IndexSizeError


def test_style_rule_parse_and_css_text_serialization() -> None:
    sheet = CSSStyleSheet()
    sheet.replace_sync("p { color: red; margin: 0 }")

    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSStyleRule)
    assert rule.type == CSSRule.STYLE_RULE
    assert rule.selector_text == "p"
    assert rule.style.css_text == "color: red; margin: 0"
    assert rule.css_text == "p { color: red; margin: 0 }"


def test_media_rule_parse_scaffold_and_nested_order() -> None:
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media screen { p { color: red } div { margin: 0 } }")

    media = sheet.css_rules[0]
    assert isinstance(media, CSSMediaRule)
    assert media.type == CSSRule.MEDIA_RULE
    assert media.media_text == "screen"
    assert media.css_rules.length == 2
    assert [r.selector_text for r in media.css_rules] == ["p", "div"]
    assert media.css_text == "@media screen { p { color: red } div { margin: 0 } }"


def test_css_rule_list_item_and_deterministic_iteration() -> None:
    sheet = CSSStyleSheet()
    sheet.replace_sync("p { color: red } span { color: blue }")

    assert sheet.css_rules.length == 2
    assert sheet.css_rules.item(-1) is None
    assert sheet.css_rules.item(3) is None
    assert [rule.selector_text for rule in sheet.css_rules] == ["p", "span"]


def test_stylesheet_insert_delete_rule_and_index_errors() -> None:
    sheet = CSSStyleSheet()
    idx0 = sheet.insert_rule("p { color: red }")
    idx1 = sheet.insert_rule("div { margin: 0 }", index=0)

    assert idx0 == 0
    assert idx1 == 0
    assert [rule.selector_text for rule in sheet.css_rules] == ["div", "p"]

    sheet.delete_rule(0)
    assert [rule.selector_text for rule in sheet.css_rules] == ["p"]

    with pytest.raises(IndexSizeError):
        sheet.insert_rule("span { color: black }", index=5)
    with pytest.raises(IndexSizeError):
        sheet.delete_rule(5)


def test_media_insert_delete_rule_and_index_errors() -> None:
    media = CSSMediaRule("screen")
    assert media.insert_rule("p { color: red }") == 0
    assert media.insert_rule("div { color: blue }", index=1) == 1
    assert [rule.selector_text for rule in media.css_rules] == ["p", "div"]

    media.delete_rule(0)
    assert [rule.selector_text for rule in media.css_rules] == ["div"]

    with pytest.raises(IndexSizeError):
        media.insert_rule("span { color: black }", index=9)
    with pytest.raises(IndexSizeError):
        media.delete_rule(9)


def test_namespace_at_rule_preserved_as_typed_rule() -> None:
    # @namespace is now a known at-rule (BACK-297 / ADR-275); it is preserved as
    # a CSSNamespaceRule instead of being silently skipped.
    from aspose_html.cssom import CSSNamespaceRule  # noqa: PLC0415
    sheet = CSSStyleSheet()
    sheet.replace_sync("@namespace url(http://www.w3.org/1999/xhtml); p { color: red }")
    # Two rules: the @namespace and the style rule.
    assert sheet.css_rules.length == 2
    assert isinstance(sheet.css_rules[0], CSSNamespaceRule)
    assert sheet.css_rules[0].namespace_uri == "http://www.w3.org/1999/xhtml"
    assert sheet.css_rules[1].selector_text == "p"


def test_insert_rule_rejects_at_rules() -> None:
    # insert_rule still rejects @keyframes and other non-@media at-rules.
    sheet = CSSStyleSheet()
    sheet.replace_sync("p { color: red }")
    with pytest.raises(SyntaxError, match="Unsupported at-rule in BACK-81 baseline"):
        sheet.insert_rule("@keyframes slide { from { opacity: 0 } to { opacity: 1 } }")


def test_invalid_selector_rejected() -> None:
    sheet = CSSStyleSheet()
    with pytest.raises(SyntaxError, match="Invalid selector in style rule"):
        sheet.replace_sync("div>>p { color: red }")


def test_nested_at_rule_inside_media_rejected() -> None:
    sheet = CSSStyleSheet()
    with pytest.raises(SyntaxError, match="Invalid CSS rule syntax"):
        sheet.replace_sync("@media screen { @media print { p { color: red } } }")
