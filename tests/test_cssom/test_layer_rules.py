"""Tests for CSSLayerBlockRule and CSSLayerStatementRule (BACK-171 / SPEC-092 / ADR-154).

Groups
------
A — CSSLayerBlockRule construction and properties (3 tests)
B — CSSLayerStatementRule construction and properties (3 tests)
C — Parser dispatch (2 tests)
D — Cascade integration (2 tests)
E — No regression (2 tests)
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import (
    CSSLayerBlockRule,
    CSSLayerStatementRule,
    CSSStyleSheet,
)
from aspose_html.cssom._parser import parse_stylesheet
from aspose_html.cssom._rules import CSSStyleRule
from aspose_html.dom import Document
from aspose_html.dom._cascade import _iter_applicable_style_rules


# ---------------------------------------------------------------------------
# Group A — CSSLayerBlockRule construction and properties
# ---------------------------------------------------------------------------


class TestCSSLayerBlockRule:
    def test_layer_block_rule_name(self) -> None:
        """Parsed @layer block rule exposes correct name, type, and child count."""
        rules = parse_stylesheet("@layer base { p { color: red } }")
        assert len(rules) == 1
        rule = rules[0]
        assert isinstance(rule, CSSLayerBlockRule)
        assert rule.name == "base"
        assert rule.type == 1000
        assert rule.type == CSSLayerBlockRule.LAYER_BLOCK_RULE
        assert len(rule.css_rules) == 1

    def test_layer_block_rule_css_text(self) -> None:
        """css_text serialises the @layer block rule correctly."""
        rules = parse_stylesheet("@layer base { p { color: red } }")
        rule = rules[0]
        assert isinstance(rule, CSSLayerBlockRule)
        assert rule.css_text == "@layer base { p { color: red } }"

    def test_anonymous_layer_block(self) -> None:
        """Anonymous @layer block (no name) yields name='' and css_text starting '@layer {'."""
        rules = parse_stylesheet("@layer { div { margin: 0 } }")
        assert len(rules) == 1
        rule = rules[0]
        assert isinstance(rule, CSSLayerBlockRule)
        assert rule.name == ""
        assert rule.css_text.startswith("@layer {")


# ---------------------------------------------------------------------------
# Group B — CSSLayerStatementRule construction and properties
# ---------------------------------------------------------------------------


class TestCSSLayerStatementRule:
    def test_layer_statement_rule_names(self) -> None:
        """Parsed @layer statement rule exposes correct name_list and type."""
        rules = parse_stylesheet("@layer base, layout, utilities;")
        assert len(rules) == 1
        rule = rules[0]
        assert isinstance(rule, CSSLayerStatementRule)
        assert rule.name_list == ["base", "layout", "utilities"]
        assert rule.type == 1001
        assert rule.type == CSSLayerStatementRule.LAYER_STATEMENT_RULE

    def test_layer_statement_rule_css_text(self) -> None:
        """css_text serialises the @layer statement rule correctly."""
        rules = parse_stylesheet("@layer base, layout, utilities;")
        rule = rules[0]
        assert isinstance(rule, CSSLayerStatementRule)
        assert rule.css_text == "@layer base, layout, utilities;"

    def test_layer_statement_single_name(self) -> None:
        """@layer with a single name produces a one-element name_list."""
        rules = parse_stylesheet("@layer reset;")
        assert len(rules) == 1
        rule = rules[0]
        assert isinstance(rule, CSSLayerStatementRule)
        assert rule.name_list == ["reset"]


# ---------------------------------------------------------------------------
# Group C — Parser dispatch
# ---------------------------------------------------------------------------


class TestLayerParserDispatch:
    def test_layer_statement_before_block(self) -> None:
        """Stylesheet with both @layer forms: first is statement, second is block."""
        css = "@layer base, layout; @layer base { p { color: red } }"
        rules = parse_stylesheet(css)
        assert len(rules) == 2
        assert isinstance(rules[0], CSSLayerStatementRule)
        assert isinstance(rules[1], CSSLayerBlockRule)

    def test_layer_parent_rule_set(self) -> None:
        """Child rules inside a @layer block have parent_rule pointing to the block."""
        rules = parse_stylesheet("@layer base { p { color: red } }")
        block = rules[0]
        assert isinstance(block, CSSLayerBlockRule)
        child = block.css_rules[0]
        assert child.parent_rule is block


# ---------------------------------------------------------------------------
# Group D — Cascade integration
# ---------------------------------------------------------------------------


class TestLayerCascadeIntegration:
    def test_layer_block_participates_in_cascade(self) -> None:
        """Styles inside @layer block participate; explicit rule after the block wins (source order)."""
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        sheet = CSSStyleSheet()
        # @layer rule comes first in source, then explicit div rule — explicit wins
        sheet.replace_sync("@layer base { div { color: blue } } div { color: red }")
        doc.attach_style_sheet(sheet)
        style = div.get_computed_style()
        assert style.get_property_value("color") == "red"

    def test_layer_block_rules_yielded_by_iterator(self) -> None:
        """_iter_applicable_style_rules yields CSSStyleRule children of a @layer block."""
        doc = Document()
        para = doc.create_element("p")
        doc.append_child(para)
        sheet = CSSStyleSheet()
        sheet.replace_sync("@layer base { p { color: red } }")
        doc.attach_style_sheet(sheet)
        yielded = list(_iter_applicable_style_rules(para))
        assert len(yielded) == 1
        style_sheet_idx, layer_tier, rule_idx, child_idx, rule = yielded[0]
        assert isinstance(rule, CSSStyleRule)
        assert rule.selector_text == "p"
        # The rule is inside a @layer block: layer_tier < unlayered sentinel
        assert layer_tier == 0  # one layer block, k=0: total-1-k = 1-1-0 = 0


# ---------------------------------------------------------------------------
# Group E — No regression
# ---------------------------------------------------------------------------


class TestLayerNoRegression:
    def test_existing_at_rules_unaffected(self) -> None:
        """Stylesheet mixing @keyframes, @supports, @media, @import, and @layer parses cleanly."""
        css = (
            '@import "reset.css"; '
            "@keyframes fade { from { opacity: 0 } to { opacity: 1 } } "
            "@supports (display: grid) { div { color: red } } "
            "@media screen { p { margin: 0 } } "
            "@layer base { span { font-size: 1em } } "
            "@layer reset, base; "
            "body { background: white }"
        )
        rules = parse_stylesheet(css)
        # @import, @keyframes, @supports, @media, @layer block, @layer statement, body style
        assert len(rules) == 7

    def test_layer_does_not_break_insert_rule(self) -> None:
        """insert_rule still raises SyntaxError for @layer rules (unchanged behaviour)."""
        sheet = CSSStyleSheet()
        sheet.replace_sync("")
        with pytest.raises(SyntaxError):
            sheet.insert_rule("@layer base { }", 0)
