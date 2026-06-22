"""Tests for CSS Cascade Level 4 origin ordering and !important precedence.

ADR-138: Cascade origin & importance ordering — phase 6.

Covers BACK-155 acceptance criteria:
  AC-1  Inline style beats author rule (non-!important)
  AC-2  Author !important beats inline non-!important
  AC-3  Class selector beats type selector (specificity)
  AC-4  Later source-order rule wins at equal specificity
  AC-5  All existing cascade tests continue to pass (guarded by the full
        test suite; this file adds only net-new cases)
  AC-6  pytest --doctest-modules passes for _cascade.py
"""
from __future__ import annotations

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# AC-1: Inline beats author (non-!important case)
# ---------------------------------------------------------------------------


class TestInlineBeatsAuthorNormal:
    def test_inline_beats_type_selector_author_rule(self) -> None:
        """Inline color:blue wins over author stylesheet div { color:red }.

        Inline declarations are origin='author' with specificity (1,0,0).
        The type selector 'div' has specificity (0,0,1) which is lower,
        so the inline declaration wins.
        """
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: red }")
        doc.attach_style_sheet(sheet)

        el.style.set_property("color", "blue")

        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue", (
            "Inline declaration (author origin, specificity (1,0,0)) must beat "
            "author stylesheet type selector rule (specificity (0,0,1))"
        )

    def test_inline_beats_class_selector_author_rule(self) -> None:
        """Inline color:blue wins over author stylesheet .foo { color:red }.

        A class selector has specificity (0,1,0) which is less than the
        inline specificity (1,0,0), so inline wins.
        """
        doc = Document()
        el = doc.create_element("div")
        el.set_attribute("class", "foo")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync(".foo { color: red }")
        doc.attach_style_sheet(sheet)

        el.style.set_property("color", "blue")

        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue", (
            "Inline (1,0,0) must beat class selector (0,1,0)"
        )


# ---------------------------------------------------------------------------
# AC-2: Author !important beats inline non-!important
# ---------------------------------------------------------------------------


class TestAuthorImportantBeatsInlineNormal:
    def test_author_important_beats_inline_normal(self) -> None:
        """Author !important color:red wins over inline color:blue.

        !important flag (importance=1) beats non-important (importance=0)
        regardless of origin or specificity.
        """
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: red !important }")
        doc.attach_style_sheet(sheet)

        el.style.set_property("color", "blue")

        style = el.get_computed_style()
        assert style.get_property_value("color") == "red", (
            "Author !important (importance=1) must outrank inline non-!important "
            "(importance=0) regardless of specificity"
        )

    def test_inline_important_beats_author_important_by_specificity(self) -> None:
        """Inline !important beats author-stylesheet !important via specificity.

        Per CSS Cascade Level 4 §6.4.2, inline is author origin with
        specificity (1,0,0).  Author stylesheet type-selector specificity
        is (0,0,1).  When both are !important and share origin='author',
        the higher specificity wins: inline (1,0,0) > stylesheet (0,0,1).
        """
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: red !important }")
        doc.attach_style_sheet(sheet)

        # Inline style value includes !important — _normalize_declaration strips it.
        el.style.set_property("color", "blue !important")

        style = el.get_computed_style()
        # Inline !important (1,0,0) beats stylesheet !important (0,0,1)
        assert style.get_property_value("color") == "blue", (
            "Inline !important with specificity (1,0,0) must beat author "
            "stylesheet !important with type-selector specificity (0,0,1)"
        )


# ---------------------------------------------------------------------------
# AC-3: Higher specificity wins (class vs type selector)
# ---------------------------------------------------------------------------


class TestHigherSpecificityWins:
    def test_class_beats_type_selector(self) -> None:
        """Class selector .foo (0,1,0) beats type selector div (0,0,1)."""
        doc = Document()
        el = doc.create_element("div")
        el.set_attribute("class", "foo")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        # Both rules in the same stylesheet; .foo has higher specificity.
        sheet.replace_sync("div { color: red } .foo { color: blue }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue", (
            "Class selector (0,1,0) must beat type selector (0,0,1)"
        )

    def test_id_beats_class_selector(self) -> None:
        """ID selector #bar (1,0,0) beats class selector .foo (0,1,0)."""
        doc = Document()
        el = doc.create_element("div")
        el.set_attribute("class", "foo")
        el.set_attribute("id", "bar")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync(".foo { color: red } #bar { color: blue }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue", (
            "ID selector (1,0,0) must beat class selector (0,1,0)"
        )

    def test_compound_selector_beats_type_selector(self) -> None:
        """div.foo (0,1,1) beats div (0,0,1)."""
        doc = Document()
        el = doc.create_element("div")
        el.set_attribute("class", "foo")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: red } div.foo { color: blue }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue", (
            "Compound selector div.foo (0,1,1) must beat type selector div (0,0,1)"
        )


# ---------------------------------------------------------------------------
# AC-4: Source order tiebreak — later rule wins
# ---------------------------------------------------------------------------


class TestSourceOrderTiebreak:
    def test_later_rule_wins_same_specificity(self) -> None:
        """When specificity is equal, the later source-order rule wins."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        # Two type-selector rules with equal specificity (0,0,1).
        sheet.replace_sync("div { color: red } div { color: blue }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue", (
            "Later source-order rule must win when specificity is equal"
        )

    def test_later_stylesheet_wins_same_specificity(self) -> None:
        """When specificity is equal, a rule from a later stylesheet wins."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet1 = CSSStyleSheet()
        sheet1.replace_sync("div { color: red }")
        sheet2 = CSSStyleSheet()
        sheet2.replace_sync("div { color: blue }")
        doc.attach_style_sheet(sheet1)
        doc.attach_style_sheet(sheet2)

        style = el.get_computed_style()
        assert style.get_property_value("color") == "blue", (
            "Rule from later-attached stylesheet must win when specificity is equal"
        )


# ---------------------------------------------------------------------------
# Regression: existing behaviours still work after origin rename
# ---------------------------------------------------------------------------


class TestRegressions:
    def test_no_rule_no_property(self) -> None:
        """Element with no matching rules has no color in computed style."""
        doc = Document()
        el = doc.create_element("span")
        doc.append_child(el)
        style = el.get_computed_style()
        assert style.get_property_value("color") == ""

    def test_inline_only_resolves(self) -> None:
        """Inline-only declaration resolves without a stylesheet."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style.set_property("color", "green")
        style = el.get_computed_style()
        assert style.get_property_value("color") == "green"

    def test_shorthand_expansion_still_works(self) -> None:
        """Shorthand margin expansion is unaffected by the origin change."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync("div { margin: 4px 8px }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("margin-top") == "4px"
        assert style.get_property_value("margin-right") == "8px"
        assert style.get_property_value("margin-bottom") == "4px"
        assert style.get_property_value("margin-left") == "8px"

    def test_important_without_inline(self) -> None:
        """Author !important rule wins over a later non-important author rule."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: red !important } div { color: blue }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("color") == "red"

    def test_author_stylesheet_property_resolves(self) -> None:
        """Renaming origin from 'stylesheet' to 'author' does not break normal stylesheet cascade."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: teal }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("color") == "teal"
