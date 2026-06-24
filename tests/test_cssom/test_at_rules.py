"""Tests for CSSOM at-rule stubs and CSSStyleSheet.css_text ().

Covers  acceptance criteria AC-1 through AC-16.
Test groups:
  A — @keyframes
  B — @font-face
  C — @supports
  D — @import
  E — unknown at-rules (silently skipped)
  F — CSSStyleSheet.css_text
  G — cascade unaffected
  H — existing paths (insert_rule rejects at-rules, @media still works)
  I — @layer cascade ordering ( / )
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import (
    CSSFontFaceRule,
    CSSImportRule,
    CSSKeyframeRule,
    CSSKeyframesRule,
    CSSLayerStatementRule,
    CSSMediaRule,
    CSSPageRule,
    CSSPropertyRule,
    CSSRule,
    CSSStyleRule,
    CSSStyleSheet,
    CSSSupportsRule,
)
from aspose_html.dom import IndexSizeError


# ---------------------------------------------------------------------------
# Group A — @keyframes
# ---------------------------------------------------------------------------


def test_keyframes_parse_does_not_raise() -> None:
    """AC-1: @keyframes parse succeeds without raising."""
    sheet = CSSStyleSheet.from_text(
        "@keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
    )
    assert sheet.css_rules.length == 1


def test_keyframes_rule_type_and_name() -> None:
    """AC-2: result is CSSKeyframesRule with correct name and type."""
    sheet = CSSStyleSheet.from_text(
        "@keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
    )
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSKeyframesRule)
    assert rule.name == "slide"
    assert rule.type == CSSRule.KEYFRAMES_RULE
    assert CSSRule.KEYFRAMES_RULE == 7


def test_keyframes_nested_rule_count_and_first_key_text() -> None:
    """AC-3: nested css_rules has two items; first has key_text 'from'."""
    sheet = CSSStyleSheet.from_text(
        "@keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
    )
    rule = sheet.css_rules[0]
    assert rule.css_rules.length == 2
    first = rule.css_rules.item(0)
    assert isinstance(first, CSSKeyframeRule)
    assert first.key_text == "from"
    assert first.type == CSSRule.KEYFRAME_RULE
    assert CSSRule.KEYFRAME_RULE == 8


def test_keyframes_second_frame_key_text_and_style() -> None:
    sheet = CSSStyleSheet.from_text(
        "@keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
    )
    rule = sheet.css_rules[0]
    second = rule.css_rules.item(1)
    assert isinstance(second, CSSKeyframeRule)
    assert second.key_text == "to"
    assert second.style.get_property_value("opacity") == "1"


def test_keyframes_percentage_key_text() -> None:
    sheet = CSSStyleSheet.from_text(
        "@keyframes grow { 0% { width: 0 } 50% { width: 50px } 100% { width: 100px } }"
    )
    rule = sheet.css_rules[0]
    assert rule.css_rules.length == 3
    assert rule.css_rules.item(0).key_text == "0%"
    assert rule.css_rules.item(1).key_text == "50%"
    assert rule.css_rules.item(2).key_text == "100%"


def test_keyframes_css_text_round_trip() -> None:
    sheet = CSSStyleSheet.from_text(
        "@keyframes fade { from { opacity: 0 } to { opacity: 1 } }"
    )
    ct = sheet.css_rules[0].css_text
    assert ct.startswith("@keyframes fade")
    assert "from" in ct
    assert "to" in ct


def test_webkit_keyframes_parsed() -> None:
    sheet = CSSStyleSheet.from_text(
        "@-webkit-keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
    )
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSKeyframesRule)
    assert rule.name == "slide"


# ---------------------------------------------------------------------------
# Group B — @font-face
# ---------------------------------------------------------------------------


def test_font_face_parse_does_not_raise() -> None:
    """AC-4: @font-face parse succeeds without raising."""
    sheet = CSSStyleSheet.from_text(
        "@font-face { font-family: MyFont; src: url(f.woff2); }"
    )
    assert sheet.css_rules.length == 1


def test_font_face_rule_type_and_style() -> None:
    """AC-5: result is CSSFontFaceRule with correct type and style access."""
    sheet = CSSStyleSheet.from_text(
        "@font-face { font-family: MyFont; src: url(f.woff2); }"
    )
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSFontFaceRule)
    assert rule.type == CSSRule.FONT_FACE_RULE
    assert CSSRule.FONT_FACE_RULE == 5
    assert rule.style.get_property_value("font-family") == "MyFont"


def test_font_face_css_text() -> None:
    sheet = CSSStyleSheet.from_text(
        "@font-face { font-family: MyFont; src: url(f.woff2); }"
    )
    ct = sheet.css_rules[0].css_text
    assert ct.startswith("@font-face")
    assert "font-family: MyFont" in ct


# ---------------------------------------------------------------------------
# Group C — @supports
# ---------------------------------------------------------------------------


def test_supports_parse_does_not_raise() -> None:
    """AC-6: @supports parse succeeds without raising."""
    sheet = CSSStyleSheet.from_text(
        "@supports (display: grid) { div { color: red } }"
    )
    assert sheet.css_rules.length == 1


def test_supports_condition_text_and_type() -> None:
    """AC-7: result is CSSSupportsRule with correct condition_text and type."""
    sheet = CSSStyleSheet.from_text(
        "@supports (display: grid) { div { color: red } }"
    )
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSSupportsRule)
    assert rule.condition_text == "(display: grid)"
    assert rule.type == CSSRule.SUPPORTS_RULE
    assert CSSRule.SUPPORTS_RULE == 12


def test_supports_nested_style_rule_access() -> None:
    sheet = CSSStyleSheet.from_text(
        "@supports (display: grid) { div { color: red } }"
    )
    rule = sheet.css_rules[0]
    assert rule.css_rules.length == 1
    nested = rule.css_rules.item(0)
    assert isinstance(nested, CSSStyleRule)
    assert nested.selector_text == "div"
    assert nested.style.get_property_value("color") == "red"


def test_supports_css_text() -> None:
    sheet = CSSStyleSheet.from_text(
        "@supports (display: grid) { div { color: red } }"
    )
    ct = sheet.css_rules[0].css_text
    assert "@supports (display: grid)" in ct
    assert "div" in ct


# ---------------------------------------------------------------------------
# Group D — @import
# ---------------------------------------------------------------------------


def test_import_quoted_url_does_not_raise() -> None:
    """AC-8: @import with quoted URL parses without raising."""
    sheet = CSSStyleSheet.from_text('@import "reset.css"')
    assert sheet.css_rules.length == 1


def test_import_rule_href_and_type() -> None:
    """AC-9: result is CSSImportRule with correct href and type."""
    sheet = CSSStyleSheet.from_text('@import "reset.css"')
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.href == "reset.css"
    assert rule.media == ""
    assert rule.type == CSSRule.IMPORT_RULE
    assert CSSRule.IMPORT_RULE == 3


def test_import_single_quoted_url() -> None:
    sheet = CSSStyleSheet.from_text("@import 'styles.css'")
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.href == "styles.css"


def test_import_url_function_syntax() -> None:
    sheet = CSSStyleSheet.from_text("@import url(reset.css)")
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.href == "reset.css"


def test_import_with_media_query() -> None:
    sheet = CSSStyleSheet.from_text('@import "reset.css" screen')
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.href == "reset.css"
    assert rule.media == "screen"


def test_import_css_text_without_media() -> None:
    sheet = CSSStyleSheet.from_text('@import "reset.css"')
    ct = sheet.css_rules[0].css_text
    assert ct == '@import "reset.css"'


def test_import_css_text_with_media() -> None:
    sheet = CSSStyleSheet.from_text('@import "reset.css" screen')
    ct = sheet.css_rules[0].css_text
    assert ct == '@import "reset.css" screen'


def test_import_resolved_href_for_absolute_input_is_identity() -> None:
    sheet = CSSStyleSheet.from_text('@import "https://cdn.example.com/reset.css"')
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.resolved_href == "https://cdn.example.com/reset.css"


def test_import_resolved_href_uses_stylesheet_base_when_valid() -> None:
    sheet = CSSStyleSheet.from_text(
        '@import "css/reset.css"',
        href="https://example.com/assets/site.css",
    )
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.resolved_href == "https://example.com/assets/css/reset.css"


@pytest.mark.parametrize("base", [None, "http://%"])
def test_import_resolved_href_falls_back_to_raw_when_base_missing_or_invalid(
    base: str | None,
) -> None:
    sheet = CSSStyleSheet.from_text('@import "css/reset.css"')
    sheet._base_url = base
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.resolved_href == "css/reset.css"


def test_import_resolved_href_does_not_mutate_css_text() -> None:
    sheet = CSSStyleSheet.from_text(
        '@import "css/reset.css" screen',
        href="https://example.com/assets/site.css",
    )
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.resolved_href == "https://example.com/assets/css/reset.css"
    assert rule.css_text == '@import "css/reset.css" screen'


# ---------------------------------------------------------------------------
# Group E — unknown at-rules silently skipped
# ---------------------------------------------------------------------------


def test_charset_statement_rule_skipped() -> None:
    """AC-10: @charset does not raise and is not in css_rules."""
    sheet = CSSStyleSheet.from_text('@charset "UTF-8"; p { color: red }')
    assert sheet.css_rules.length == 1
    assert sheet.css_rules[0].selector_text == "p"


def test_namespace_statement_rule_preserved() -> None:
    """@namespace is now parsed into a CSSNamespaceRule ( / ).

    Prior to  this rule was silently skipped; it is now preserved as
    a typed CSSNamespaceRule object — the first rule in the sheet.
    """
    from aspose_html.cssom import CSSNamespaceRule  # noqa: PLC0415
    sheet = CSSStyleSheet.from_text(
        "@namespace url(http://www.w3.org/1999/xhtml); p { color: red }"
    )
    assert sheet.css_rules.length == 2
    assert isinstance(sheet.css_rules[0], CSSNamespaceRule)
    assert sheet.css_rules[0].namespace_uri == "http://www.w3.org/1999/xhtml"
    assert sheet.css_rules[1].selector_text == "p"


def test_vendor_prefixed_unknown_at_rule_skipped() -> None:
    sheet = CSSStyleSheet.from_text(
        "@-moz-document url-prefix() { p { color: red } } div { margin: 0 }"
    )
    # The unknown @-moz-document block is skipped; only div rule survives.
    assert sheet.css_rules.length == 1
    assert sheet.css_rules[0].selector_text == "div"


def test_page_rule_now_parsed() -> None:
    """@page is now a known at-rule ( / ) — it is no longer skipped."""
    from aspose_html.cssom import CSSPageRule  # noqa: PLC0415
    sheet = CSSStyleSheet.from_text("@page { margin: 0 } p { color: red }")
    assert sheet.css_rules.length == 2
    assert isinstance(sheet.css_rules[0], CSSPageRule)
    assert sheet.css_rules[1].selector_text == "p"


# ---------------------------------------------------------------------------
# Group F — CSSStyleSheet.css_text
# ---------------------------------------------------------------------------


def test_css_text_single_style_rule() -> None:
    """AC-12: css_text on a single-rule sheet contains selector and declaration."""
    sheet = CSSStyleSheet.from_text("p { color: red; }")
    ct = sheet.css_text
    assert "p" in ct
    assert "color" in ct


def test_css_text_mixed_rules() -> None:
    """AC-13: css_text on mixed-rule sheet contains all four rules."""
    css = (
        "p { color: red } "
        "@keyframes slide { from { opacity: 0 } to { opacity: 1 } } "
        "@font-face { font-family: MyFont; src: url(f.woff2); } "
        "div { margin: 0 }"
    )
    sheet = CSSStyleSheet.from_text(css)
    assert sheet.css_rules.length == 4
    ct = sheet.css_text
    assert "p {" in ct
    assert "@keyframes slide" in ct
    assert "@font-face" in ct
    assert "div {" in ct


def test_css_text_is_newline_separated() -> None:
    sheet = CSSStyleSheet.from_text("p { color: red } div { margin: 0 }")
    ct = sheet.css_text
    assert "\n" in ct


def test_css_text_consistent_with_css_rules() -> None:
    """AC-12 / AC-13: css_text always reflects current css_rules (not cached)."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    ct1 = sheet.css_text
    sheet.insert_rule("div { margin: 0 }")
    ct2 = sheet.css_text
    assert "div" not in ct1
    assert "div" in ct2


def test_css_text_round_trip_same_rule_count() -> None:
    """parse → css_text → parse produces same rule count."""
    css = (
        "@keyframes fade { from { opacity: 0 } to { opacity: 1 } } "
        "p { color: red } "
        "@font-face { font-family: F; src: url(f.woff2); }"
    )
    sheet = CSSStyleSheet.from_text(css)
    ct = sheet.css_text
    sheet2 = CSSStyleSheet.from_text(ct)
    assert sheet2.css_rules.length == sheet.css_rules.length


# ---------------------------------------------------------------------------
# Group G — cascade unaffected
# ---------------------------------------------------------------------------


def test_cascade_unaffected_by_keyframes_in_sheet() -> None:
    """AC-14: get_computed_style returns correct values despite @keyframes in sheet."""
    from aspose_html.dom import Document

    doc = Document()
    p_el = doc.create_element("p")
    doc.append_child(p_el)

    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "@keyframes slide { from { opacity: 0 } to { opacity: 1 } } "
        "p { color: red }"
    )
    doc.attach_style_sheet(sheet)

    style = p_el.get_computed_style()
    assert style.get_property_value("color") == "red"


# ---------------------------------------------------------------------------
# Group H — existing paths
# ---------------------------------------------------------------------------


def test_insert_rule_rejects_keyframes() -> None:
    """AC (Group H): insert_rule still raises SyntaxError for @keyframes."""
    sheet = CSSStyleSheet.from_text("p { color: red }")
    with pytest.raises(SyntaxError, match="Unsupported at-rule"):
        sheet.insert_rule(
            "@keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
        )


def test_insert_rule_rejects_font_face() -> None:
    sheet = CSSStyleSheet.from_text("p { color: red }")
    with pytest.raises(SyntaxError, match="Unsupported at-rule"):
        sheet.insert_rule("@font-face { font-family: F; src: url(f.woff2); }")


def test_insert_rule_rejects_supports() -> None:
    sheet = CSSStyleSheet.from_text("p { color: red }")
    with pytest.raises(SyntaxError, match="Unsupported at-rule"):
        sheet.insert_rule("@supports (display: grid) { div { color: red } }")


def test_media_rule_still_works() -> None:
    """@media parsing is not broken by the new at-rule dispatch."""
    sheet = CSSStyleSheet.from_text(
        "@media screen { p { color: red } div { margin: 0 } }"
    )
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSMediaRule)
    assert rule.media_text == "screen"
    assert rule.css_rules.length == 2


def test_mixed_sheet_source_order() -> None:
    """AC-11: sheet with mixed rules has 4 items in source order."""
    css = (
        "p { color: red } "
        "@keyframes slide { from { opacity: 0 } to { opacity: 1 } } "
        "@font-face { font-family: MyFont; src: url(f.woff2); } "
        "div { margin: 0 }"
    )
    sheet = CSSStyleSheet.from_text(css)
    assert sheet.css_rules.length == 4
    assert isinstance(sheet.css_rules[0], CSSStyleRule)
    assert isinstance(sheet.css_rules[1], CSSKeyframesRule)
    assert isinstance(sheet.css_rules[2], CSSFontFaceRule)
    assert isinstance(sheet.css_rules[3], CSSStyleRule)


def test_style_rule_css_text_unchanged() -> None:
    """CSSStyleRule.css_text format is unchanged."""
    sheet = CSSStyleSheet.from_text("div.foo { color: red }")
    assert sheet.css_rules[0].css_text == "div.foo { color: red }"


# ---------------------------------------------------------------------------
# Group I — @layer cascade ordering ( / )
# ---------------------------------------------------------------------------


def _doc_with_css(css: str) -> tuple[object, object]:
    """Return (document, element) with a single <p> and a sheet containing *css*."""
    from aspose_html.dom import Document

    doc = Document()
    el = doc.create_element("p")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(css)
    doc.attach_style_sheet(sheet)
    return doc, el


def test_layer_order_first_layer_wins() -> None:
    """AC-1 (): same property/specificity — rule from first @layer wins."""
    _doc, el = _doc_with_css(
        "@layer base { p { color: red } } @layer theme { p { color: blue } }"
    )
    style = el.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_unlayered_beats_layer() -> None:
    """AC-2 (): unlayered rule beats any same-specificity @layer rule."""
    _doc, el = _doc_with_css(
        "@layer base { p { color: blue } } p { color: green }"
    )
    style = el.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_unlayered_loses_to_higher_specificity_in_layer() -> None:
    """AC-3 (): higher specificity inside a layer still wins over unlayered lower specificity."""
    from aspose_html.dom import Document

    doc = Document()
    el = doc.create_element("p")
    el.set_attribute("class", "foo")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    # Inside the layer: selector p.foo has specificity (0,1,1) — beats unlayered p (0,0,1)
    sheet.replace_sync("@layer base { p.foo { color: red } } p { color: blue }")
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_layer_source_order_within_same_layer() -> None:
    """AC-4 (): within the same @layer block, later rule wins (standard source order)."""
    _doc, el = _doc_with_css(
        "@layer base { p { color: red } p { color: blue } }"
    )
    style = el.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_no_layer_blocks_unchanged() -> None:
    """AC-5 (): stylesheet without @layer produces the same result as before."""
    _doc, el = _doc_with_css("p { color: red } p { color: blue }")
    style = el.get_computed_style()
    # Later rule wins (standard source order)
    assert style.get_property_value("color") == "blue"


def test_layer_plus_media_combination() -> None:
    """AC-6 (): @media rule containing a style rule respects unlayered > layered ordering."""
    _doc, el = _doc_with_css(
        "@layer base { p { color: blue } } @media screen { p { color: green } }"
    )
    style = el.get_computed_style()
    # @media screen matches; the unlayered media rule (tier=2) beats the layer rule (tier=0)
    assert style.get_property_value("color") == "green"


def test_three_layers_priority_order() -> None:
    """Three @layer blocks: first has highest priority, last has lowest."""
    _doc, el = _doc_with_css(
        "@layer a { p { color: red } } "
        "@layer b { p { color: green } } "
        "@layer c { p { color: blue } }"
    )
    style = el.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_unlayered_beats_all_layers() -> None:
    """Unlayered rule beats every @layer rule regardless of order."""
    _doc, el = _doc_with_css(
        "p { color: purple } "
        "@layer a { p { color: red } } "
        "@layer b { p { color: green } }"
    )
    style = el.get_computed_style()
    assert style.get_property_value("color") == "purple"


# ---------------------------------------------------------------------------
# Group J —  (): @page, @property, CSSRule constants, outline
# ---------------------------------------------------------------------------


def test_page_rule_bare_at_page() -> None:
    """AC-1/#1: bare @page rule is parsed into a CSSPageRule instance."""
    sheet = CSSStyleSheet.from_text("@page { margin: 1cm }")
    rules = list(sheet.css_rules)
    assert len(rules) == 1
    rule = rules[0]
    assert isinstance(rule, CSSPageRule)
    assert rule.type == CSSRule.PAGE_RULE == 6
    assert rule.selector_text == ""
    assert rule.style.get_property_value("margin") == "1cm"


def test_page_rule_with_pseudo_selector() -> None:
    """AC-2/#2: @page :first stores selector_text == ':first'."""
    sheet = CSSStyleSheet.from_text("@page :first { margin-top: 2cm }")
    rule = list(sheet.css_rules)[0]
    assert isinstance(rule, CSSPageRule)
    assert rule.selector_text == ":first"


def test_page_rule_cover_named_page() -> None:
    """Named page selectors are stored verbatim."""
    sheet = CSSStyleSheet.from_text("@page cover { margin: 0 }")
    rule = list(sheet.css_rules)[0]
    assert isinstance(rule, CSSPageRule)
    assert rule.selector_text == "cover"


def test_page_rule_css_text_contains_at_page() -> None:
    """AC-3: css_text contains '@page'."""
    sheet = CSSStyleSheet.from_text("@page { margin: 1cm }")
    rule = list(sheet.css_rules)[0]
    assert "@page" in rule.css_text


def test_page_rule_css_text_with_selector() -> None:
    """css_text includes the page selector when present."""
    sheet = CSSStyleSheet.from_text("@page :first { margin-top: 2cm }")
    rule = list(sheet.css_rules)[0]
    assert "@page :first" in rule.css_text


def test_page_rule_style_is_css_declaration_block() -> None:
    """AC-3/#3: rule.style is a CSSDeclarationBlock with the page declarations."""
    from aspose_html.cssom._declarations import CSSDeclarationBlock  # noqa: PLC0415
    sheet = CSSStyleSheet.from_text("@page { margin: 1cm }")
    rule = list(sheet.css_rules)[0]
    assert isinstance(rule.style, CSSDeclarationBlock)


def test_page_rule_mixed_with_style_rule() -> None:
    """@page rule and a style rule co-exist in source order."""
    sheet = CSSStyleSheet.from_text("@page { margin: 0 } p { color: red }")
    assert sheet.css_rules.length == 2
    assert isinstance(sheet.css_rules[0], CSSPageRule)
    assert isinstance(sheet.css_rules[1], CSSStyleRule)


def test_property_rule_full() -> None:
    """AC-4/#4/#5: @property rule is parsed with all descriptor fields."""
    sheet = CSSStyleSheet.from_text(
        '@property --color { syntax: "<color>"; inherits: false; initial-value: red }'
    )
    rules = list(sheet.css_rules)
    assert len(rules) == 1
    rule = rules[0]
    assert isinstance(rule, CSSPropertyRule)
    assert rule.type == 16
    assert rule.name == "--color"
    assert "color" in rule.syntax
    assert rule.inherits == "false"
    assert rule.initial_value == "red"


def test_property_rule_in_stylesheet_with_style_rule() -> None:
    """@property rule and a style rule co-exist in source order."""
    sheet = CSSStyleSheet.from_text(
        "@property --gap { syntax: '<length>'; inherits: true; initial-value: 0px }\n"
        "p { color: red }"
    )
    rules = list(sheet.css_rules)
    assert len(rules) == 2
    assert isinstance(rules[0], CSSPropertyRule)
    assert isinstance(rules[1], CSSStyleRule)


def test_property_rule_name() -> None:
    """CSSPropertyRule.name returns the custom property name."""
    sheet = CSSStyleSheet.from_text(
        "@property --my-size { syntax: '<length>'; inherits: false; initial-value: 0px }"
    )
    rule = list(sheet.css_rules)[0]
    assert rule.name == "--my-size"


def test_property_rule_css_text_contains_at_property() -> None:
    """CSSPropertyRule.css_text contains '@property --color'."""
    sheet = CSSStyleSheet.from_text(
        "@property --color { syntax: '<color>'; inherits: false; initial-value: red }"
    )
    rule = list(sheet.css_rules)[0]
    assert "@property --color" in rule.css_text


def test_property_rule_empty_body() -> None:
    """@property with no recognised descriptors produces a stub with empty fields."""
    sheet = CSSStyleSheet.from_text("@property --x {}")
    rule = list(sheet.css_rules)[0]
    assert isinstance(rule, CSSPropertyRule)
    assert rule.name == "--x"
    assert rule.syntax == ""
    assert rule.inherits == ""
    assert rule.initial_value == ""


def test_layer_statement_rule_constant_on_cssrule() -> None:
    """AC-6/#6: CSSRule.LAYER_STATEMENT_RULE == 1001 (no AttributeError)."""
    assert CSSRule.LAYER_STATEMENT_RULE == 1001


def test_font_feature_values_rule_constant() -> None:
    """AC-7/#7: CSSRule.FONT_FEATURE_VALUES_RULE == 14 (no AttributeError)."""
    assert CSSRule.FONT_FEATURE_VALUES_RULE == 14


def test_layer_statement_rule_constant_matches_instance() -> None:
    """AC-8/#8: CSSLayerStatementRule instance .type == CSSRule.LAYER_STATEMENT_RULE."""
    sheet = CSSStyleSheet.from_text("@layer base;")
    rule = list(sheet.css_rules)[0]
    assert isinstance(rule, CSSLayerStatementRule)
    assert rule.type == CSSRule.LAYER_STATEMENT_RULE == 1001


def test_outline_shorthand_expands() -> None:
    """AC-9/10/11/#9/10/11: outline: 2px solid red expands to three longhands."""
    from aspose_html.dom import Document  # noqa: PLC0415

    doc = Document()
    el = doc.create_element("p")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync("p { outline: 2px solid red }")
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("outline-width") == "2px"
    assert style.get_property_value("outline-style") == "solid"
    assert style.get_property_value("outline-color") == "red"


def test_outline_shorthand_offset_uses_initial() -> None:
    """outline shorthand does not set outline-offset; it stays at the initial value."""
    from aspose_html.dom import Document  # noqa: PLC0415

    doc = Document()
    el = doc.create_element("p")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync("p { outline: 2px solid red }")
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    # outline-offset initial value is '' in _INITIAL_VALUE_BASELINE (no layout engine)
    # Confirm the shorthand did not accidentally write outline-offset
    assert style.get_property_value("outline-offset") == ""


def test_outline_shorthand_style_only() -> None:
    """outline: dashed — single keyword token is classified as outline-style."""
    from aspose_html.dom._cascade_shorthands import _expand_outline_shorthand  # noqa: PLC0415
    result = _expand_outline_shorthand("dashed")
    assert result.get("outline-style") == "dashed"
    assert "outline-width" not in result


def test_outline_shorthand_two_tokens() -> None:
    """outline: 1px solid — two tokens: width + style."""
    from aspose_html.dom._cascade_shorthands import _expand_outline_shorthand  # noqa: PLC0415
    result = _expand_outline_shorthand("1px solid")
    assert result.get("outline-width") == "1px"
    assert result.get("outline-style") == "solid"
