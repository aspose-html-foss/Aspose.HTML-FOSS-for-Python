""" integration tests (, , ).

Cross-component integration tests covering all  groups:

- Group A — CSSOM at-rules + cascade coexistence: sheet with mixed at-rules
  and style rules; cascade resolves style rules; rule counts and types correct.
- Group B — @supports + cascade: CSSSupportsRule parsed; cascade does NOT apply
  nested rules (correct stub behaviour).
- Group C — @import + mixed sheet: CSSImportRule at index 0; style rule at index 1;
  cascade applies style rule; import is not fetched.
- Group D — Node.is_connected + HTMLInputElement IDL: attachment/detachment
  reflects correctly; new IDL attributes (step, min, max, multiple, value_as_number)
  work from a parsed document.
- Group E — Document stub properties: cookie, hidden, visibility_state, has_focus
  all return expected values without raising.
- Group F — Doctest sweep: all >>> blocks in the six source files pass with
  zero failures ( compliance).
"""
from __future__ import annotations

import doctest

import pytest

from aspose_html.cssom import (
    CSSFontFaceRule,
    CSSImportRule,
    CSSKeyframesRule,
    CSSRule,
    CSSStyleRule,
    CSSStyleSheet,
    CSSSupportsRule,
)
from aspose_html.dom import Document
from aspose_html.html_document import HTMLDocument


# ===========================================================================
# Group A — CSSOM at-rules + cascade coexistence
# ===========================================================================


class TestGroupAAtRulesCascadeCoexistence:
    """Sheet with mixed at-rules and a style rule; cascade resolves correctly."""

    CSS_TEXT = (
        "@keyframes slide { from { opacity: 0 } to { opacity: 1 } } "
        "@font-face { font-family: MyFont; src: url(f.woff2); } "
        "p { color: red }"
    )

    def _sheet_and_doc(self):
        doc = HTMLDocument.parse("<html><body><p id='p1'>hello</p></body></html>")
        sheet = CSSStyleSheet.from_text(self.CSS_TEXT)
        doc.attach_style_sheet(sheet)
        return doc, sheet

    def test_css_rules_length_is_three(self):
        """AC-1: sheet with @keyframes + @font-face + p rule has length 3."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules.length == 3

    def test_first_rule_is_css_keyframes_rule(self):
        """AC-1: css_rules[0] is CSSKeyframesRule."""
        _, sheet = self._sheet_and_doc()
        assert isinstance(sheet.css_rules[0], CSSKeyframesRule)

    def test_keyframes_rule_type_constant(self):
        """CSSKeyframesRule has correct type constant KEYFRAMES_RULE (7)."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules[0].type == CSSRule.KEYFRAMES_RULE

    def test_second_rule_is_css_font_face_rule(self):
        """AC-1: css_rules[1] is CSSFontFaceRule."""
        _, sheet = self._sheet_and_doc()
        assert isinstance(sheet.css_rules[1], CSSFontFaceRule)

    def test_font_face_rule_type_constant(self):
        """CSSFontFaceRule has correct type constant FONT_FACE_RULE (5)."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules[1].type == CSSRule.FONT_FACE_RULE

    def test_third_rule_is_css_style_rule(self):
        """AC-1: css_rules[2] is CSSStyleRule (the p { color: red } rule)."""
        _, sheet = self._sheet_and_doc()
        assert isinstance(sheet.css_rules[2], CSSStyleRule)

    def test_cascade_resolves_color_from_style_rule(self):
        """AC-1: cascade applies p { color: red } despite at-rules in the sheet."""
        doc, _ = self._sheet_and_doc()
        p_el = doc.get_element_by_id("p1")
        assert p_el is not None
        cs = p_el.get_computed_style()
        assert cs.get_property_value("color") == "red"

    def test_css_text_contains_keyframes(self):
        """AC-1: css_text serialises @keyframes rule."""
        _, sheet = self._sheet_and_doc()
        assert "@keyframes slide" in sheet.css_text

    def test_css_text_contains_font_face(self):
        """AC-1: css_text serialises @font-face rule."""
        _, sheet = self._sheet_and_doc()
        assert "@font-face" in sheet.css_text

    def test_css_text_contains_style_rule(self):
        """AC-1: css_text serialises p { color: red } style rule."""
        _, sheet = self._sheet_and_doc()
        assert "color: red" in sheet.css_text


# ===========================================================================
# Group B — @supports + cascade
# ===========================================================================


class TestGroupBSupportsAndCascade:
    """@supports rule with unknown property is present but cascade does NOT apply its inner rules."""

    #  (/) added 'display' to _KNOWN_PROPERTIES, so
    # @supports (display: grid) now evaluates to True and its inner rules ARE
    # applied.  This group uses a genuinely unknown property to test that the
    # cascade correctly skips @supports rules whose condition is False.
    CSS_TEXT = "@supports (unknown-bogus-prop: grid) { div { color: blue } }"

    def _sheet_and_doc(self):
        doc = HTMLDocument.parse("<html><body><div id='d1'>test</div></body></html>")
        sheet = CSSStyleSheet.from_text(self.CSS_TEXT)
        doc.attach_style_sheet(sheet)
        return doc, sheet

    def test_supports_rule_present_in_css_rules(self):
        """AC-2: CSSSupportsRule is present in css_rules."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules.length == 1
        assert isinstance(sheet.css_rules[0], CSSSupportsRule)

    def test_supports_rule_condition_text(self):
        """AC-2: condition_text is '(unknown-bogus-prop: grid)'."""
        _, sheet = self._sheet_and_doc()
        rule = sheet.css_rules[0]
        assert rule.condition_text == "(unknown-bogus-prop: grid)"

    def test_supports_rule_has_inner_rule(self):
        """AC-2: CSSSupportsRule contains one inner style rule."""
        _, sheet = self._sheet_and_doc()
        rule = sheet.css_rules[0]
        assert isinstance(rule, CSSSupportsRule)
        assert rule.css_rules.length == 1

    def test_cascade_does_not_apply_supports_inner_rule(self):
        """AC-2: cascade skips @supports with unknown property — div color remains ''."""
        doc, _ = self._sheet_and_doc()
        div_el = doc.get_element_by_id("d1")
        assert div_el is not None
        cs = div_el.get_computed_style()
        # Cascade evaluates @supports conditions; unknown property → False → inner rule skipped.
        assert cs.get_property_value("color") == ""

    def test_supports_rule_type_constant(self):
        """CSSSupportsRule type is SUPPORTS_RULE (12)."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules[0].type == CSSRule.SUPPORTS_RULE


# ===========================================================================
# Group C — @import + mixed sheet
# ===========================================================================


class TestGroupCImportAndMixedSheet:
    """@import + style rule coexist; cascade applies style rule; import not fetched."""

    CSS_TEXT = '@import "reset.css"; body { font-size: 16px }'

    def _sheet_and_doc(self):
        doc = HTMLDocument.parse("<html><body><p>hi</p></body></html>")
        sheet = CSSStyleSheet.from_text(self.CSS_TEXT)
        doc.attach_style_sheet(sheet)
        return doc, sheet

    def test_css_rules_length_is_two(self):
        """AC-3: @import + style rule → length == 2."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules.length == 2

    def test_first_rule_is_import_rule(self):
        """AC-3: css_rules[0] is CSSImportRule."""
        _, sheet = self._sheet_and_doc()
        assert isinstance(sheet.css_rules[0], CSSImportRule)

    def test_import_rule_href(self):
        """AC-3: CSSImportRule.href == 'reset.css'."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules[0].href == "reset.css"

    def test_import_rule_type_constant(self):
        """CSSImportRule.type == IMPORT_RULE (3)."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules[0].type == CSSRule.IMPORT_RULE

    def test_second_rule_is_style_rule(self):
        """AC-3: css_rules[1] is CSSStyleRule."""
        _, sheet = self._sheet_and_doc()
        assert isinstance(sheet.css_rules[1], CSSStyleRule)

    def test_second_rule_selector(self):
        """AC-3: CSSStyleRule selector is 'body'."""
        _, sheet = self._sheet_and_doc()
        assert sheet.css_rules[1].selector_text == "body"

    def test_css_text_contains_import(self):
        """AC-3: css_text serialises @import rule."""
        _, sheet = self._sheet_and_doc()
        assert '@import "reset.css"' in sheet.css_text

    def test_css_text_contains_body_rule(self):
        """AC-3: css_text serialises body { font-size: 16px } rule."""
        _, sheet = self._sheet_and_doc()
        assert "font-size: 16px" in sheet.css_text

    def test_cascade_applies_body_font_size(self):
        """AC-3: cascade applies font-size: 16px from the style rule."""
        doc, _ = self._sheet_and_doc()
        body_el = doc.query_selector("body")
        assert body_el is not None
        cs = body_el.get_computed_style()
        assert cs.get_property_value("font-size") == "16px"


# ===========================================================================
# Group D — Node.is_connected + HTMLInputElement IDL
# ===========================================================================


class TestGroupDIsConnectedAndHTMLInputIDL:
    """Node.is_connected reflects DOM state; HTMLInputElement new IDL works in parsed doc."""

    def _parsed_doc(self):
        return HTMLDocument.parse(
            "<html><body>"
            "<form><input id='inp1' type='number' min='0' max='10' step='1' multiple></form>"
            "</body></html>"
        )

    def test_input_is_connected_true_when_in_document(self):
        """AC-4: inp.is_connected is True when element is in the document tree."""
        doc = self._parsed_doc()
        inp = doc.get_element_by_id("inp1")
        assert inp is not None
        assert inp.is_connected is True

    def test_input_min_reflects_attribute(self):
        """AC-4: inp.min == '0' from parsed HTML."""
        doc = self._parsed_doc()
        inp = doc.get_element_by_id("inp1")
        assert inp.min == "0"

    def test_input_max_reflects_attribute(self):
        """AC-4: inp.max == '10' from parsed HTML."""
        doc = self._parsed_doc()
        inp = doc.get_element_by_id("inp1")
        assert inp.max == "10"

    def test_input_step_reflects_attribute(self):
        """AC-4: inp.step == '1' from parsed HTML."""
        doc = self._parsed_doc()
        inp = doc.get_element_by_id("inp1")
        assert inp.step == "1"

    def test_input_multiple_reflects_attribute(self):
        """AC-4: inp.multiple is True from parsed HTML (boolean presence)."""
        doc = self._parsed_doc()
        inp = doc.get_element_by_id("inp1")
        assert inp.multiple is True

    def test_input_value_as_number_round_trip(self):
        """AC-4: setting value to '5' gives value_as_number == 5.0."""
        doc = self._parsed_doc()
        inp = doc.get_element_by_id("inp1")
        inp.value = "5"
        assert inp.value_as_number == 5.0

    def test_input_is_connected_false_after_remove(self):
        """AC-4: inp.is_connected is False after inp.remove()."""
        doc = self._parsed_doc()
        inp = doc.get_element_by_id("inp1")
        assert inp.is_connected is True
        inp.remove()
        assert inp.is_connected is False

    def test_detached_element_is_not_connected(self):
        """Freshly created element not appended to document is not connected."""
        doc = Document()
        el = doc.create_element("div")
        assert el.is_connected is False

    def test_appended_element_becomes_connected(self):
        """Element becomes connected after append_child."""
        doc = Document()
        el = doc.create_element("span")
        assert el.is_connected is False
        doc.append_child(el)
        assert el.is_connected is True


# ===========================================================================
# Group E — Document stub properties
# ===========================================================================


class TestGroupEDocumentStubs:
    """Document.cookie, hidden, visibility_state, has_focus — all return stubs without raising."""

    def test_cookie_returns_empty_string(self):
        """AC-5: doc.cookie == '' without raising."""
        doc = Document()
        assert doc.cookie == ""

    def test_cookie_parsed_document_returns_empty_string(self):
        """AC-5: cookie is '' on a parsed HTMLDocument."""
        doc = HTMLDocument.parse("<html><body></body></html>")
        assert doc.cookie == ""

    def test_hidden_returns_false(self):
        """AC-5: doc.hidden is False (headless — no rendering surface)."""
        doc = Document()
        assert doc.hidden is False

    def test_visibility_state_returns_visible(self):
        """AC-5: doc.visibility_state == 'visible' in headless mode."""
        doc = Document()
        assert doc.visibility_state == "visible"

    def test_has_focus_returns_false(self):
        """AC-5: doc.has_focus() is False (headless — no focus management)."""
        doc = Document()
        assert doc.has_focus() is False

    def test_all_stubs_on_parsed_document(self):
        """AC-5: all four stubs work together on a parsed HTMLDocument."""
        doc = HTMLDocument.parse("<html><body><p>x</p></body></html>")
        assert doc.cookie == ""
        assert doc.hidden is False
        assert doc.visibility_state == "visible"
        assert doc.has_focus() is False


# ===========================================================================
# Group F — Doctest sweep ( compliance)
# ===========================================================================


class TestGroupFDoctestSweep:
    """Verify all >>> blocks in six  source files pass with 0 failures.

    Each test imports the module and runs doctest.testmod(). Satisfies
    : public API docstring examples must execute in CI.
    """

    def test_rules_py_doctests_pass(self):
        """All doctests in cssom/_rules.py must pass."""
        import aspose_html.cssom._rules as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_rules.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )

    def test_parser_py_doctests_pass(self):
        """All doctests in cssom/_parser.py must pass."""
        import aspose_html.cssom._parser as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_parser.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )

    def test_stylesheet_py_doctests_pass(self):
        """All doctests in cssom/_stylesheet.py must pass."""
        import aspose_html.cssom._stylesheet as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_stylesheet.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )

    def test_node_py_doctests_pass(self):
        """All doctests in dom/_node.py must pass."""
        import aspose_html.dom._node as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_node.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )

    def test_document_py_doctests_pass(self):
        """All doctests in dom/_document.py must pass."""
        import aspose_html.dom._document as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_document.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )

    def test_elements_py_doctests_pass(self):
        """All doctests in dom/html/_elements.py must pass."""
        import aspose_html.dom.html._elements as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_elements.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )
