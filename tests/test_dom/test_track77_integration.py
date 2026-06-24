""" integration matrix — Attr.prefix/specified, VisualViewport,
CSSNamespaceRule, CSSCounterStyleRule ( /  / ).

Groups:
  A - Attr IDL (prefix, specified, local_name) — FR-1, FR-2, AC-1..3
  B - VisualViewport — FR-3, FR-4, FR-5, AC-4..7
  C - CSSNamespaceRule — FR-6, FR-8, AC-8..10
  D - CSSCounterStyleRule — FR-7, FR-8, AC-11..14
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, VisualViewport
from aspose_html.cssom import (
    CSSCounterStyleRule,
    CSSNamespaceRule,
    CSSRule,
    CSSStyleSheet,
)

XLINK_NS = "http://www.w3.org/1999/xlink"
SVG_NS = "http://www.w3.org/2000/svg"
XHTML_NS = "http://www.w3.org/1999/xhtml"


# ---------------------------------------------------------------------------
# Group A — Attr.prefix and Attr.specified (FR-1, FR-2)
# ---------------------------------------------------------------------------


def test_attr_prefix_xlink_via_set_attribute_ns() -> None:
    """AC-1: xlink:href attribute → prefix == 'xlink'."""
    doc = Document()
    el = doc.create_element("svg")
    el.set_attribute_ns(XLINK_NS, "xlink:href", "#target")
    attr = el.get_attribute_node("xlink:href")
    assert attr is not None
    assert attr.prefix == "xlink"


def test_attr_specified_true() -> None:
    """AC-3: Attr.specified is always True (DOM3 legacy H-1)."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("class", "box")
    attr = el.get_attribute_node("class")
    assert attr is not None
    assert attr.specified is True  # always True per WHATWG DOM §4.6


def test_attr_local_name_strip_prefix() -> None:
    """AC-1: namespaced attribute local_name returns only the local part."""
    doc = Document()
    el = doc.create_element("svg")
    el.set_attribute_ns(XLINK_NS, "xlink:href", "#foo")
    attr = el.get_attribute_node("xlink:href")
    assert attr is not None
    assert attr.local_name == "href"


def test_attr_prefix_none_for_plain() -> None:
    """AC-2: plain (non-namespaced) attribute → prefix is None."""
    doc = Document()
    el = doc.create_element("p")
    el.set_attribute("id", "main")
    attr = el.get_attribute_node("id")
    assert attr is not None
    assert attr.prefix is None


def test_attr_specified_true_for_namespaced() -> None:
    """AC-3: specified is True for namespaced attributes too."""
    doc = Document()
    el = doc.create_element("use")
    el.set_attribute_ns(XLINK_NS, "xlink:href", "#a")
    attr = el.get_attribute_node("xlink:href")
    assert attr is not None
    assert attr.specified is True


# ---------------------------------------------------------------------------
# Group B — VisualViewport (FR-3, FR-4, FR-5)
# ---------------------------------------------------------------------------


def test_visual_viewport_scale_is_one() -> None:
    """AC-6: visual_viewport.scale == 1.0 in headless mode (H-2)."""
    doc = Document()
    vv = doc.default_view.visual_viewport
    assert vv.scale == 1.0


def test_visual_viewport_geometry_zero() -> None:
    """AC-6: width, height, offset_left, offset_top are 0 in headless mode."""
    doc = Document()
    vv = doc.default_view.visual_viewport
    assert vv.width == 0
    assert vv.height == 0
    assert vv.offset_left == 0.0
    assert vv.offset_top == 0.0
    assert vv.page_left == 0.0
    assert vv.page_top == 0.0


def test_visual_viewport_singleton() -> None:
    """AC-5: window.visual_viewport returns the same object on repeated access."""
    doc = Document()
    w = doc.default_view
    assert w.visual_viewport is w.visual_viewport


def test_visual_viewport_accessible_from_window() -> None:
    """AC-4: window.visual_viewport is not None and is a VisualViewport."""
    doc = Document()
    vv = doc.default_view.visual_viewport
    assert vv is not None
    assert isinstance(vv, VisualViewport)


def test_visual_viewport_importable() -> None:
    """AC-7: VisualViewport importable from aspose_html.dom."""
    from aspose_html.dom import VisualViewport as VV  # noqa: PLC0415
    assert VV is VisualViewport


# ---------------------------------------------------------------------------
# Group C — CSSNamespaceRule (FR-6, FR-8, AC-8..10)
# ---------------------------------------------------------------------------


def test_css_namespace_rule_namespace_uri() -> None:
    """AC-9: CSSNamespaceRule.namespace_uri returns the URI."""
    rule = CSSNamespaceRule(XHTML_NS)
    assert rule.namespace_uri == XHTML_NS


def test_css_namespace_rule_prefix() -> None:
    """AC-10: CSSNamespaceRule.prefix returns the prefix string."""
    rule = CSSNamespaceRule(SVG_NS, "svg")
    assert rule.prefix == "svg"


def test_css_namespace_rule_css_text_prefixed() -> None:
    """AC-10: css_text for a prefixed @namespace rule."""
    rule = CSSNamespaceRule(SVG_NS, "svg")
    assert rule.css_text == '@namespace svg "http://www.w3.org/2000/svg";'


def test_css_namespace_rule_css_text_default() -> None:
    """AC-9: css_text for a default @namespace rule (no prefix)."""
    rule = CSSNamespaceRule(XHTML_NS)
    assert rule.css_text == f'@namespace "{XHTML_NS}";'


def test_css_namespace_rule_type() -> None:
    """AC-8: CSSNamespaceRule.css_type == 10 == CSSRule.NAMESPACE_RULE."""
    rule = CSSNamespaceRule(XHTML_NS)
    assert rule.css_type == 10
    assert rule.css_type == CSSRule.NAMESPACE_RULE


def test_css_namespace_rule_from_parser_default() -> None:
    """AC-8: parse_stylesheet produces CSSNamespaceRule for default @namespace."""
    sheet = CSSStyleSheet.from_text(f'@namespace "{XHTML_NS}";')
    assert sheet.css_rules.length == 1
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSNamespaceRule)
    assert rule.namespace_uri == XHTML_NS
    assert rule.prefix is None


def test_css_namespace_rule_from_parser_prefixed() -> None:
    """AC-10: parse_stylesheet produces CSSNamespaceRule with prefix for prefixed @namespace."""
    sheet = CSSStyleSheet.from_text(f'@namespace svg "{SVG_NS}";')
    assert sheet.css_rules.length == 1
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSNamespaceRule)
    assert rule.namespace_uri == SVG_NS
    assert rule.prefix == "svg"


# ---------------------------------------------------------------------------
# Group D — CSSCounterStyleRule (FR-7, FR-8, AC-11..14)
# ---------------------------------------------------------------------------


def test_css_counter_style_rule_name() -> None:
    """AC-12: CSSCounterStyleRule.name returns the counter style name."""
    rule = CSSCounterStyleRule("thumbs")
    assert rule.name == "thumbs"


def test_css_counter_style_rule_empty_body() -> None:
    """CSSCounterStyleRule with no body has empty style and valid css_text."""
    rule = CSSCounterStyleRule("lower-roman")
    assert rule.style == ""
    assert "lower-roman" in rule.css_text


def test_css_counter_style_rule_with_body() -> None:
    """CSSCounterStyleRule preserves body text in .style property."""
    rule = CSSCounterStyleRule("thumbs", "system: cyclic; symbols: A")
    assert "system: cyclic" in rule.style


def test_css_counter_style_rule_css_text() -> None:
    """CSSCounterStyleRule.css_text includes name and body."""
    rule = CSSCounterStyleRule("thumbs", "system: cyclic")
    assert "@counter-style thumbs" in rule.css_text
    assert "system: cyclic" in rule.css_text


def test_css_counter_style_rule_type() -> None:
    """AC-11: CSSCounterStyleRule.css_type == 11 == CSSRule.COUNTER_STYLE_RULE (CSSOM §5.4)."""
    rule = CSSCounterStyleRule("lower-greek")
    assert rule.css_type == 11
    assert rule.css_type == CSSRule.COUNTER_STYLE_RULE


def test_css_counter_style_rule_from_parser() -> None:
    """AC-11, AC-12: parse_stylesheet produces CSSCounterStyleRule for @counter-style."""
    sheet = CSSStyleSheet.from_text(
        '@counter-style thumbs { system: cyclic; symbols: "A"; suffix: " "; }'
    )
    assert sheet.css_rules.length == 1
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSCounterStyleRule)
    assert rule.name == "thumbs"
    assert rule.css_type == 11


def test_mixed_sheet_three_rules() -> None:
    """AC-13: @namespace + @counter-style + p rule → 3 rules in css_rules."""
    css = (
        f'@namespace "{XHTML_NS}"; '
        '@counter-style thumbs { system: cyclic; } '
        "p { color: red; }"
    )
    sheet = CSSStyleSheet.from_text(css)
    assert sheet.css_rules.length == 3
    assert isinstance(sheet.css_rules[0], CSSNamespaceRule)
    assert isinstance(sheet.css_rules[1], CSSCounterStyleRule)
    from aspose_html.cssom import CSSStyleRule  # noqa: PLC0415
    assert isinstance(sheet.css_rules[2], CSSStyleRule)


def test_cascade_unaffected_by_new_rules() -> None:
    """AC-14: get_computed_style is unaffected by @namespace + @counter-style stubs.

    A stylesheet mixing @namespace, @counter-style, and a regular style rule
    must produce correct cascade results — the new rule stubs must be transparent
    to the cascade pipeline (H-3, ).
    """
    doc = Document()
    p = doc.create_element("p")
    doc.append_child(p)

    sheet = CSSStyleSheet()
    sheet.replace_sync(
        f'@namespace "{XHTML_NS}"; '
        f"@counter-style custom {{ system: cyclic; }} "
        f"p {{ color: blue; }}"
    )
    doc.attach_style_sheet(sheet)

    cs = p.get_computed_style()
    # The @namespace and @counter-style stubs must not corrupt cascade;
    # 'p { color: blue }' must still resolve.
    assert cs.get_property_value("color") == "blue"
