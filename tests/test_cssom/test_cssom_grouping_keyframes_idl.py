"""Track 87 — CSSOM grouping-rule and keyframes mutation IDL tail (BACK-308 / ADR-286 / SPEC-140).

Groups
------
A — CSSRule constants (3 tests)
B — CSSMediaRule.condition_text (2 tests)
C — CSSSupportsRule insert_rule / delete_rule (2 tests)
D — CSSLayerBlockRule insert_rule / delete_rule (2 tests)
E — CSSKeyframesRule mutation (5 tests)
F — CSSStyleDeclaration.set_property_priority (3 tests)
"""
from __future__ import annotations

import aspose_html
from aspose_html.cssom import CSSStyleSheet
from aspose_html.cssom._rules import CSSRule


# ---------------------------------------------------------------------------
# Group A — CSSRule constants
# ---------------------------------------------------------------------------


class TestCSSRuleConstants:
    def test_unknown_rule(self) -> None:
        """CSSRule.UNKNOWN_RULE == 0 (CSSOM §5.4)."""
        assert CSSRule.UNKNOWN_RULE == 0

    def test_layer_block_rule(self) -> None:
        """CSSRule.LAYER_BLOCK_RULE == 17 (CSS Cascade 5 / CSSOM-Extensions §2.1)."""
        assert CSSRule.LAYER_BLOCK_RULE == 17

    def test_counter_style_rule_corrected(self) -> None:
        """CSSRule.COUNTER_STYLE_RULE == 11 (corrected from 20 per CSSOM §5.4)."""
        assert CSSRule.COUNTER_STYLE_RULE == 11


# ---------------------------------------------------------------------------
# Group B — CSSMediaRule.condition_text
# ---------------------------------------------------------------------------


class TestCSSMediaRuleConditionText:
    def test_condition_text_returns_media_query(self) -> None:
        """condition_text returns the media query string (CSSOM §6.8.1 alias)."""
        sheet = CSSStyleSheet.from_text("@media (max-width: 600px) { p { color: red } }")
        assert sheet.css_rules[0].condition_text == "(max-width: 600px)"

    def test_condition_text_equals_media_text(self) -> None:
        """condition_text == media_text; neither property is removed."""
        sheet = CSSStyleSheet.from_text("@media screen { p { color: red } }")
        rule = sheet.css_rules[0]
        assert rule.media_text == "screen"
        assert rule.condition_text == "screen"
        assert rule.condition_text == rule.media_text


# ---------------------------------------------------------------------------
# Group C — CSSSupportsRule insert_rule / delete_rule
# ---------------------------------------------------------------------------


class TestCSSSupportsRuleMutation:
    def test_insert_rule_returns_index_and_grows_list(self) -> None:
        """insert_rule returns the insertion index and the nested list grows."""
        sheet = CSSStyleSheet.from_text("@supports (display: flex) { p { color: red } }")
        sr = sheet.css_rules[0]
        idx = sr.insert_rule("div { margin: 0 }", 0)
        assert idx == 0
        assert len(sr.css_rules) == 2

    def test_delete_rule_removes_nested_rule(self) -> None:
        """delete_rule removes the nested rule, leaving an empty css_rules."""
        sheet = CSSStyleSheet.from_text("@supports (display: flex) { p { color: red } }")
        sr = sheet.css_rules[0]
        sr.delete_rule(0)
        assert len(sr.css_rules) == 0


# ---------------------------------------------------------------------------
# Group D — CSSLayerBlockRule insert_rule / delete_rule
# ---------------------------------------------------------------------------


class TestCSSLayerBlockRuleMutation:
    def test_insert_rule_returns_index_and_grows_list(self) -> None:
        """insert_rule on @layer block returns the insertion index and the list grows."""
        sheet = CSSStyleSheet.from_text("@layer utilities { p { color: red } }")
        lr = sheet.css_rules[0]
        idx = lr.insert_rule("div { margin: 0 }", 0)
        assert idx == 0
        assert len(lr.css_rules) == 2

    def test_delete_rule_removes_nested_rule(self) -> None:
        """delete_rule on @layer block removes the nested rule."""
        sheet = CSSStyleSheet.from_text("@layer utilities { p { color: red } }")
        lr = sheet.css_rules[0]
        lr.delete_rule(0)
        assert len(lr.css_rules) == 0


# ---------------------------------------------------------------------------
# Group E — CSSKeyframesRule mutation
# ---------------------------------------------------------------------------


class TestCSSKeyframesRuleMutation:
    def test_append_rule_grows_keyframe_list(self) -> None:
        """append_rule parses and appends a new keyframe; list length increases by 1."""
        sheet = CSSStyleSheet.from_text("@keyframes s { from { opacity: 0 } }")
        kr = sheet.css_rules[0]
        kr.append_rule("to { opacity: 1 }")
        assert len(kr.css_rules) == 2

    def test_find_rule_returns_matching_keyframe(self) -> None:
        """find_rule returns the CSSKeyframeRule with matching key_text."""
        sheet = CSSStyleSheet.from_text(
            "@keyframes s { from { opacity: 0 } to { opacity: 1 } }"
        )
        kr = sheet.css_rules[0]
        found = kr.find_rule("from")
        assert found is not None
        assert found.key_text == "from"

    def test_find_rule_returns_none_for_missing(self) -> None:
        """find_rule returns None when the key_text is not present."""
        sheet = CSSStyleSheet.from_text("@keyframes s { from { opacity: 0 } }")
        assert sheet.css_rules[0].find_rule("missing") is None

    def test_delete_rule_removes_keyframe(self) -> None:
        """delete_rule removes the matching keyframe; the list shrinks."""
        sheet = CSSStyleSheet.from_text("@keyframes s { from { opacity: 0 } }")
        kr = sheet.css_rules[0]
        kr.delete_rule("from")
        assert len(kr.css_rules) == 0

    def test_delete_rule_missing_key_is_noop(self) -> None:
        """delete_rule on a missing key_text is a silent no-op."""
        sheet = CSSStyleSheet.from_text("@keyframes s { from { opacity: 0 } }")
        kr = sheet.css_rules[0]
        kr.delete_rule("missing")  # no-op, no exception
        assert len(kr.css_rules) == 1


# ---------------------------------------------------------------------------
# Group F — CSSStyleDeclaration.set_property_priority
# ---------------------------------------------------------------------------


class TestCSSStyleDeclarationSetPropertyPriority:
    def test_set_priority_updates_get_property_priority(self) -> None:
        """set_property_priority('color', 'important') causes get_property_priority to return 'important'."""
        doc = aspose_html.HTMLDocument.parse('<p style="color: red">hi</p>')
        p = doc.query_selector("p")
        p.style.set_property_priority("color", "important")
        assert p.style.get_property_priority("color") == "important"

    def test_set_priority_absent_property_is_noop(self) -> None:
        """set_property_priority on an absent property is silently ignored."""
        doc = aspose_html.HTMLDocument.parse('<p style="color: red">hi</p>')
        p = doc.query_selector("p")
        p.style.set_property_priority("margin", "important")  # no-op
        # margin is still absent
        assert p.style.get_property_priority("margin") == ""

    def test_clear_priority_with_empty_string(self) -> None:
        """set_property_priority('color', '') clears !important."""
        doc = aspose_html.HTMLDocument.parse('<p style="color: red !important">hi</p>')
        p = doc.query_selector("p")
        assert p.style.get_property_priority("color") == "important"
        p.style.set_property_priority("color", "")
        assert p.style.get_property_priority("color") == ""
