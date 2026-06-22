"""Track 37 integration tests — cascade + CSSOM + QuickJS cross-component.

Groups A–D cover end-to-end interactions across the four Track 37
implementation tasks.  Group E (doctest sweep) is exercised by running
``pytest --doctest-modules`` on the module paths listed in the ADR.

All QuickJS-backed assertions (Group D) require the optional ``quickjs``
package.  The entire module is skipped cleanly when ``quickjs`` is absent
via ``pytest.importorskip``.

ADR: ADR-142 — Track 37 integration hardening.
Spec: SPEC-084 — CSS full cascade and QuickJS CSSOM integration.
"""
from __future__ import annotations

import pytest

# Skip the entire module when quickjs is not installed.
# This satisfies AC-6 (Group E): skip-safe when quickjs absent.
quickjs = pytest.importorskip("quickjs")

from aspose_html.dom import Document                  # noqa: E402
from aspose_html.cssom import CSSStyleSheet, CSSMediaRule  # noqa: E402
from aspose_html.js import JSContext                  # noqa: E402


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def doc_with_author_color():
    """Document with author stylesheet ``div { color: red }``."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: red }")
    doc.attach_style_sheet(sheet)
    return doc, el


@pytest.fixture()
def parent_child_doc():
    """Document with parent div and child span, author stylesheet on parent."""
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)
    return doc, parent, child


# ---------------------------------------------------------------------------
# Group A — Cascade origin correctness  (assertions 1–5)
# ---------------------------------------------------------------------------


class TestGroupACascadeOrigin:
    """Cascade origin ordering per CSS Cascading Level 4 §4."""

    def test_a1_author_color_no_inline(self, doc_with_author_color):
        """Author ``color: red``, no inline → computed color == ``red``."""
        _doc, el = doc_with_author_color
        style = el.get_computed_style()
        assert style.get_property_value("color") == "red"

    def test_a2_inline_beats_author(self, doc_with_author_color):
        """Inline ``color: blue`` beats author ``color: red``."""
        _doc, el = doc_with_author_color
        el.style.set_property("color", "blue")
        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue"

    def test_a3_author_important_beats_inline(self):
        """Author ``color: red !important`` beats inline ``color: blue``."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: red !important }")
        doc.attach_style_sheet(sheet)
        el.style.set_property("color", "blue")
        style = el.get_computed_style()
        assert style.get_property_value("color") == "red"

    def test_a4_higher_specificity_wins(self):
        """Class selector (.foo) wins over type selector (div) at same source order."""
        doc = Document()
        el = doc.create_element("div")
        el.set_attribute("class", "foo")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        # .foo has specificity (0,1,0); div has (0,0,1); .foo wins.
        sheet.replace_sync("div { color: green } .foo { color: blue }")
        doc.attach_style_sheet(sheet)
        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue"

    def test_a5_later_source_order_wins_on_tie(self):
        """Later rule wins when specificity is equal (same selector)."""
        doc = Document()
        el = doc.create_element("p")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("p { color: red } p { color: navy }")
        doc.attach_style_sheet(sheet)
        style = el.get_computed_style()
        assert style.get_property_value("color") == "navy"


# ---------------------------------------------------------------------------
# Group B — Inheritance correctness  (assertions 6–10)
# ---------------------------------------------------------------------------


class TestGroupBInheritance:
    """Full inheritance engine per CSS Cascading Level 4 Appendix A."""

    def test_b6_color_inherits_to_child(self, parent_child_doc):
        """Parent ``color: green``, child has no own rule → child gets ``green``."""
        doc, parent, child = parent_child_doc
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: green }")
        doc.attach_style_sheet(sheet)
        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "green"

    def test_b7_text_align_inherits_to_child(self, parent_child_doc):
        """Parent ``text-align: center`` inherits to child span."""
        doc, parent, child = parent_child_doc
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { text-align: center }")
        doc.attach_style_sheet(sheet)
        child_style = child.get_computed_style()
        assert child_style.get_property_value("text-align") == "center"

    def test_b8_list_style_type_inherits_to_child(self):
        """``list-style-type: circle`` on ``<ul>`` inherits to child ``<li>``."""
        doc = Document()
        ul = doc.create_element("ul")
        li = doc.create_element("li")
        doc.append_child(ul)
        ul.append_child(li)
        sheet = CSSStyleSheet()
        sheet.replace_sync("ul { list-style-type: circle }")
        doc.attach_style_sheet(sheet)
        child_style = li.get_computed_style()
        assert child_style.get_property_value("list-style-type") == "circle"

    def test_b9_background_color_does_not_inherit(self, parent_child_doc):
        """``background-color`` is NOT an inherited property."""
        doc, parent, child = parent_child_doc
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { background-color: yellow }")
        doc.attach_style_sheet(sheet)
        child_style = child.get_computed_style()
        # background-color should not cascade down
        assert child_style.get_property_value("background-color") == ""

    def test_b10_inherit_keyword_forces_inheritance(self, parent_child_doc):
        """``color: inherit`` on child forces inheritance of non-default parent color."""
        doc, parent, child = parent_child_doc
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: purple }")
        doc.attach_style_sheet(sheet)
        # Explicitly set inherit keyword on child
        child.style.set_property("color", "inherit")
        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "purple"


# ---------------------------------------------------------------------------
# Group C — CSSOM object correctness  (assertions 11–15)
# ---------------------------------------------------------------------------


class TestGroupCCSSOM:
    """CSSOM rule objects per CSSOM §6.4–§6.6."""

    def test_c11_css_rules_length(self):
        """Parsed stylesheet with 3 rules → ``len(sheet.css_rules) == 3``."""
        sheet = CSSStyleSheet.from_text("p { color: red } div { color: blue } span { font-size: 14px }")
        assert len(sheet.css_rules) == 3

    def test_c12_selector_text_matches_input(self):
        """``sheet.css_rules[0].selector_text`` matches the parsed selector."""
        sheet = CSSStyleSheet.from_text("div.foo { color: red }")
        assert sheet.css_rules[0].selector_text == "div.foo"

    def test_c13_item_same_as_index(self):
        """``sheet.css_rules.item(0)`` is the same object as ``sheet.css_rules[0]``."""
        sheet = CSSStyleSheet.from_text("div { color: red }")
        rl = sheet.css_rules
        assert rl.item(0) is rl[0]

    def test_c14_item_out_of_range_returns_none(self):
        """``sheet.css_rules.item(999)`` returns ``None`` — no IndexError."""
        sheet = CSSStyleSheet.from_text("div { color: red }")
        rl = sheet.css_rules
        assert rl.item(999) is None
        assert rl.item(-1) is None

    def test_c15_media_rule_css_rules_length(self):
        """``CSSMediaRule.css_rules`` length equals the number of enclosed rules."""
        sheet = CSSStyleSheet.from_text(
            "@media screen { p { color: red } div { color: blue } }"
        )
        assert len(sheet.css_rules) == 1
        media_rule = sheet.css_rules[0]
        assert isinstance(media_rule, CSSMediaRule)
        assert len(media_rule.css_rules) == 2


# ---------------------------------------------------------------------------
# Group D — QuickJS bridge correctness  (assertions 16–20)
# ---------------------------------------------------------------------------


class TestGroupDQuickJS:
    """QuickJS bridge end-to-end tests per ADR-141."""

    @pytest.fixture()
    def styled_doc(self):
        """Document with ``<h1 id='x'>`` and ``<p>`` with author color stylesheet."""
        doc = Document()
        h1 = doc.create_element("h1")
        h1.set_attribute("id", "x")
        doc.append_child(h1)
        p = doc.create_element("p")
        doc.append_child(p)
        sheet = CSSStyleSheet()
        sheet.replace_sync("p { color: navy }")
        doc.attach_style_sheet(sheet)
        return doc

    def test_d16_query_selector_tag_name(self, styled_doc):
        """``document.querySelector('h1').tagName`` returns ``'H1'``."""
        with JSContext(styled_doc) as ctx:
            result = ctx.evaluate("document.querySelector('h1').tagName")
        assert result == "H1"

    def test_d17_get_element_by_id(self, styled_doc):
        """``document.getElementById('x').id`` returns ``'x'``."""
        with JSContext(styled_doc) as ctx:
            result = ctx.evaluate("document.getElementById('x').id")
        assert result == "x"

    def test_d18_get_computed_style_matches_python(self, styled_doc):
        """JS ``window.getComputedStyle`` result matches Python-side cascade."""
        # Python side
        from aspose_html.css import select
        elements = select(styled_doc, "p", first_only=True)
        assert elements, "fixture must have a <p> element"
        py_color = elements[0].get_computed_style().get_property_value("color")

        with JSContext(styled_doc) as ctx:
            js_color = ctx.evaluate(
                "window.getComputedStyle(document.querySelector('p'))"
                ".getPropertyValue('color')"
            )
        assert js_color == py_color
        assert py_color == "navy"

    def test_d19_query_selector_missing_returns_none(self, styled_doc):
        """``document.querySelector('.missing')`` returns Python ``None``."""
        with JSContext(styled_doc) as ctx:
            result = ctx.evaluate("document.querySelector('.missing')")
        assert result is None

    def test_d20_sanity_arithmetic(self, styled_doc):
        """Sanity: ``1 + 1 == 2`` in the QuickJS context."""
        with JSContext(styled_doc) as ctx:
            result = ctx.evaluate("1 + 1")
        assert result == 2

    # ---------------------------------------------------------------------------
    # Bonus: cascade + JS combined round-trip
    # ---------------------------------------------------------------------------

    def test_d_bonus_author_important_reflected_in_js(self):
        """Author ``!important`` rule is reflected in JS ``getComputedStyle``."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: teal !important }")
        doc.attach_style_sheet(sheet)
        el.style.set_property("color", "red")  # should lose to !important

        with JSContext(doc) as ctx:
            js_color = ctx.evaluate(
                "window.getComputedStyle(document.querySelector('div'))"
                ".getPropertyValue('color')"
            )
        assert js_color == "teal"

    def test_d_bonus_query_selector_all_count(self):
        """``document.querySelectorAll`` returns the correct element count."""
        doc = Document()
        for _ in range(3):
            li = doc.create_element("li")
            doc.append_child(li)
        with JSContext(doc) as ctx:
            count = ctx.evaluate("document.querySelectorAll('li').length")
        assert count == 3

    def test_d_bonus_element_get_attribute(self):
        """JS ``getAttribute`` returns the Python-side attribute value."""
        doc = Document()
        el = doc.create_element("span")
        el.set_attribute("data-value", "42")
        doc.append_child(el)
        with JSContext(doc) as ctx:
            val = ctx.evaluate("document.querySelector('span').getAttribute('data-value')")
        assert val == "42"
