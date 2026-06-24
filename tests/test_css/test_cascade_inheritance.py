"""Tests for the full inheritance engine —  / .

Covers CSS Cascade Level 4 Appendix A inherited-property set and CSS-wide
keyword completeness (inherit, initial, unset, revert).

Acceptance criteria:
  AC-1  color inherits from parent when child has no color rule
  AC-2  text-align inherits (newly added to inherited set)
  AC-3  list-style-type inherits from parent ul to child li
  AC-4  background-color does NOT inherit (non-inherited property)
  AC-5  inherit keyword on background-color forces inheritance from parent
  AC-6  initial keyword resets color to "" regardless of parent
  AC-7  unset on inherited property acts as inherit
  AC-8  unset on non-inherited property acts as initial
  AC-9  revert behaves same as unset (no UA stylesheet)
  AC-10 Three-level inheritance chain resolves correctly
  AC-11 All existing cascade tests pass with zero regressions
  AC-12 pytest --doctest-modules src/aspose_html/dom/_cascade.py passes
"""
from __future__ import annotations

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _doc_with_parent_child(
    parent_tag: str = "div",
    child_tag: str = "span",
) -> tuple[Document, object, object]:
    """Return (doc, parent_el, child_el) already attached to the document."""
    doc = Document()
    parent = doc.create_element(parent_tag)
    child = parent.owner_document.create_element(child_tag)
    doc.append_child(parent)
    parent.append_child(child)
    return doc, parent, child


def _doc_with_grandparent_parent_child() -> tuple[Document, object, object, object]:
    """Return (doc, grandparent, parent, child) all attached."""
    doc = Document()
    grandparent = doc.create_element("div")
    parent = doc.create_element("div")
    child = doc.create_element("div")
    doc.append_child(grandparent)
    grandparent.append_child(parent)
    parent.append_child(child)
    return doc, grandparent, parent, child


# ---------------------------------------------------------------------------
# AC-1: color inherits from parent when child has no color rule
# ---------------------------------------------------------------------------


class TestColorInherits:
    def test_color_inherits_to_child(self) -> None:
        """Parent color: red propagates to child with no local color rule."""
        doc, parent, child = _doc_with_parent_child()
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: red }")
        doc.attach_style_sheet(sheet)

        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "red", (
            "color is an inherited property; child must receive parent value"
        )

    def test_local_color_overrides_inherited(self) -> None:
        """Child local color rule beats parent inherited value."""
        doc, parent, child = _doc_with_parent_child()
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: red } span { color: navy }")
        doc.attach_style_sheet(sheet)

        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "navy"


# ---------------------------------------------------------------------------
# AC-2: text-align inherits (newly added in )
# ---------------------------------------------------------------------------


class TestTextAlignInherits:
    def test_text_align_inherits_to_child(self) -> None:
        """text-align is in _INHERITED_PROPERTIES; child must receive parent value."""
        doc, parent, child = _doc_with_parent_child()
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { text-align: center }")
        doc.attach_style_sheet(sheet)

        child_style = child.get_computed_style()
        assert child_style.get_property_value("text-align") == "center"

    def test_word_spacing_inherits(self) -> None:
        """word-spacing is an inherited property (CSS Level 4 Appendix A)."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("word-spacing", "4px")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("word-spacing") == "4px"

    def test_visibility_inherits(self) -> None:
        """visibility is an inherited property."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("visibility", "hidden")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("visibility") == "hidden"


# ---------------------------------------------------------------------------
# AC-3: list-style-type inherits from parent ul to child li
# ---------------------------------------------------------------------------


class TestListStyleInherits:
    def test_list_style_type_inherits_to_child(self) -> None:
        """list-style-type is an inherited property; li inherits from ul."""
        doc = Document()
        ul = doc.create_element("ul")
        li = doc.create_element("li")
        doc.append_child(ul)
        ul.append_child(li)

        sheet = CSSStyleSheet()
        sheet.replace_sync("ul { list-style-type: square }")
        doc.attach_style_sheet(sheet)

        li_style = li.get_computed_style()
        assert li_style.get_property_value("list-style-type") == "square"

    def test_list_style_position_inherits(self) -> None:
        """list-style-position inherits (part of the list category in Level 4)."""
        doc, parent, child = _doc_with_parent_child("ul", "li")
        parent.style.set_property("list-style-position", "inside")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("list-style-position") == "inside"


# ---------------------------------------------------------------------------
# AC-4: background-color does NOT inherit (non-inherited property)
# ---------------------------------------------------------------------------


class TestNonInheritedDoesNotInherit:
    def test_background_color_does_not_inherit(self) -> None:
        """background-color is non-inherited; child gets '' when parent has it."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("background-color", "red")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("background-color") == "", (
            "background-color is non-inherited; must not appear on child"
        )

    def test_margin_top_does_not_inherit(self) -> None:
        """margin-top is non-inherited; child should not receive parent margin."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("margin-top", "20px")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("margin-top") == ""


# ---------------------------------------------------------------------------
# AC-5: inherit keyword on background-color forces inheritance from parent
# ---------------------------------------------------------------------------


class TestInheritKeywordForcesInheritance:
    def test_inherit_keyword_on_non_inherited_property(self) -> None:
        """background-color: inherit forces propagation even for non-inherited props."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("background-color", "blue")
        child.style.set_property("background-color", "inherit")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("background-color") == "blue", (
            "inherit keyword must force inheritance regardless of property class"
        )

    def test_inherit_keyword_on_inherited_property(self) -> None:
        """inherit on an already-inherited property also uses parent value."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("color", "green")
        child.style.set_property("color", "inherit")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "green"

    def test_inherit_keyword_on_root_returns_initial(self) -> None:
        """inherit on a root element (no parent) returns initial value ('')."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style.set_property("color", "inherit")

        style = el.get_computed_style()
        assert style.get_property_value("color") == ""


# ---------------------------------------------------------------------------
# AC-6: initial keyword resets color to "" regardless of parent
# ---------------------------------------------------------------------------


class TestInitialKeyword:
    def test_initial_on_inherited_resets_to_empty(self) -> None:
        """color: initial ignores parent color and returns initial value ('')."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("color", "red")
        child.style.set_property("color", "initial")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "", (
            "initial must return the CSS initial value ('' in this implementation)"
        )

    def test_initial_on_non_inherited_returns_empty(self) -> None:
        """background-color: initial returns '' (the CSS initial value here)."""
        doc, _parent, child = _doc_with_parent_child()
        child.style.set_property("background-color", "initial")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("background-color") == ""


# ---------------------------------------------------------------------------
# AC-7: unset on inherited property acts as inherit
# ---------------------------------------------------------------------------


class TestUnsetOnInherited:
    def test_unset_on_color_acts_as_inherit(self) -> None:
        """color: unset on a child acts as inherit when parent has a color rule."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("color", "green")
        child.style.set_property("color", "unset")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "green", (
            "unset on inherited property must act as inherit"
        )

    def test_unset_on_text_align_acts_as_inherit(self) -> None:
        """text-align: unset acts as inherit (newly inherited property in )."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("text-align", "right")
        child.style.set_property("text-align", "unset")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("text-align") == "right"


# ---------------------------------------------------------------------------
# AC-8: unset on non-inherited property acts as initial
# ---------------------------------------------------------------------------


class TestUnsetOnNonInherited:
    def test_unset_on_background_color_acts_as_initial(self) -> None:
        """background-color: unset returns '' (non-inherited → initial)."""
        doc, _parent, child = _doc_with_parent_child()
        child.style.set_property("background-color", "unset")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("background-color") == "", (
            "unset on non-inherited property must act as initial ('' here)"
        )

    def test_unset_on_margin_top_acts_as_initial(self) -> None:
        """margin-top: unset returns '' (non-inherited → initial)."""
        doc, _parent, child = _doc_with_parent_child()
        child.style.set_property("margin-top", "unset")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("margin-top") == ""


# ---------------------------------------------------------------------------
# AC-9: revert behaves same as unset (no UA stylesheet)
# ---------------------------------------------------------------------------


class TestRevertActsAsUnset:
    def test_revert_on_inherited_property_acts_as_inherit(self) -> None:
        """color: revert acts as inherit when parent has a color rule (no UA sheet)."""
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("color", "navy")
        child.style.set_property("color", "revert")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "navy", (
            "revert with no UA stylesheet falls back to unset semantics → inherit"
        )

    def test_revert_on_non_inherited_acts_as_initial(self) -> None:
        """background-color: revert returns '' (non-inherited → initial, no UA sheet)."""
        doc, _parent, child = _doc_with_parent_child()
        child.style.set_property("background-color", "revert")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("background-color") == ""

    def test_revert_on_text_align_on_root_returns_initial(self) -> None:
        """revert on root element (no parent) returns '' regardless of inherited status."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style.set_property("text-align", "revert")

        style = el.get_computed_style()
        assert style.get_property_value("text-align") == ""


# ---------------------------------------------------------------------------
# AC-10: Three-level inheritance chain resolves correctly
# ---------------------------------------------------------------------------


class TestDeepInheritanceChain:
    def test_color_propagates_through_two_ancestor_levels(self) -> None:
        """grandparent color propagates via parent to child (two hops)."""
        doc, grandparent, parent, child = _doc_with_grandparent_parent_child()
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: teal }")
        doc.attach_style_sheet(sheet)

        # The grandparent rule sets color: teal; parent inherits it; child inherits
        # from parent (which already resolved teal from grandparent).
        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "teal"

    def test_nearest_ancestor_wins_in_deep_chain(self) -> None:
        """Parent color beats grandparent color in a two-level inheritance chain."""
        doc, grandparent, parent, child = _doc_with_grandparent_parent_child()
        grandparent.style.set_property("color", "blue")
        parent.style.set_property("color", "red")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "red", (
            "nearest ancestor value must win over more-distant ancestor"
        )

    def test_text_align_propagates_through_two_levels(self) -> None:
        """text-align set on grandparent propagates through parent to grandchild."""
        doc, grandparent, parent, child = _doc_with_grandparent_parent_child()
        grandparent.style.set_property("text-align", "justify")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("text-align") == "justify"

    def test_child_local_rule_overrides_deep_inherited_value(self) -> None:
        """child local rule overrides value inherited from grandparent."""
        doc, grandparent, parent, child = _doc_with_grandparent_parent_child()
        grandparent.style.set_property("color", "blue")
        child.style.set_property("color", "orange")

        child_style = child.get_computed_style()
        assert child_style.get_property_value("color") == "orange"


# ---------------------------------------------------------------------------
# Additional coverage: expanded inherited-property set
# ---------------------------------------------------------------------------


class TestExpandedInheritedPropertySet:
    def test_letter_spacing_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("letter-spacing", "2px")
        assert child.get_computed_style().get_property_value("letter-spacing") == "2px"

    def test_white_space_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("white-space", "nowrap")
        assert child.get_computed_style().get_property_value("white-space") == "nowrap"

    def test_word_break_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("word-break", "break-all")
        assert child.get_computed_style().get_property_value("word-break") == "break-all"

    def test_cursor_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("cursor", "pointer")
        assert child.get_computed_style().get_property_value("cursor") == "pointer"

    def test_pointer_events_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("pointer-events", "none")
        assert child.get_computed_style().get_property_value("pointer-events") == "none"

    def test_border_collapse_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child("table", "tr")
        parent.style.set_property("border-collapse", "collapse")
        assert child.get_computed_style().get_property_value("border-collapse") == "collapse"

    def test_writing_mode_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("writing-mode", "vertical-rl")
        assert child.get_computed_style().get_property_value("writing-mode") == "vertical-rl"

    def test_direction_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("direction", "rtl")
        assert child.get_computed_style().get_property_value("direction") == "rtl"

    def test_font_variant_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("font-variant", "small-caps")
        assert child.get_computed_style().get_property_value("font-variant") == "small-caps"

    def test_quotes_inherits(self) -> None:
        doc, parent, child = _doc_with_parent_child()
        parent.style.set_property("quotes", "none")
        assert child.get_computed_style().get_property_value("quotes") == "none"
