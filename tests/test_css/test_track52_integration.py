""" integration test suite — :nth-child(An+B of S) full cross-behavior matrix.

Covers  Group C /  acceptance criteria (integration hardening):

  AC-1  test_track52_integration.py passes with 0 failures
  AC-2  All 9 scenario groups have at least one test case
  AC-3  Regression: existing :nth-child and :nth-of-type tests still pass

Nine scenario groups exercised end-to-end via HTMLDocument.parse() +
query_selector_all() / css.select():

  Group 1 — Flat list with class filter (boundary positions 1, 2, 3, beyond-end)
  Group 2 — Mixed sibling types (only certain tag types match the filter)
  Group 3 — :nth-last-child(of S) — from-end filtering
  Group 4 — Multi-selector filter (:nth-child(1 of p, .item))
  Group 5 — Interaction with combinators (div > :nth-child(2 of span))
  Group 6 — Specificity-driven cascade (specificity values)
  Group 7 — Regression: existing :nth-child/nth-of-type still work
  Group 8 — Edge: 0n+1 is equivalent to 1 of .x
  Group 9 — Edge: empty filtered set matches nothing
"""
from __future__ import annotations

import pytest

from aspose_html import HTMLDocument
from aspose_html.css import select


# ============================================================================
# Group 1 — Flat list with class filter
# ============================================================================
#
# HTML: <ul><li class='x'>A</li><li>B</li><li class='x'>C</li><li class='x'>D</li></ul>
# Filtered set (by .x): A, C, D (positions 1, 2, 3 in filtered set).
# ============================================================================


class TestGroup1FlatListClassFilter:
    """Flat <ul>/<li> with class filter — positional boundary checks."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.doc = HTMLDocument.parse(
            "<ul>"
            "<li class='x'>A</li>"
            "<li>B</li>"
            "<li class='x'>C</li>"
            "<li class='x'>D</li>"
            "</ul>"
        )
        self.ul = self.doc.query_selector("ul")

    def test_first_class_element(self):
        """:nth-child(1 of .x) selects A — first element with class x."""
        result = select(self.ul, "li:nth-child(1 of .x)")
        assert len(result) == 1
        assert result[0].text_content == "A"

    def test_second_class_element(self):
        """:nth-child(2 of .x) selects C — second element with class x."""
        result = select(self.ul, "li:nth-child(2 of .x)")
        assert len(result) == 1
        assert result[0].text_content == "C"

    def test_third_class_element(self):
        """:nth-child(3 of .x) selects D — third element with class x."""
        result = select(self.ul, "li:nth-child(3 of .x)")
        assert len(result) == 1
        assert result[0].text_content == "D"

    def test_beyond_end_matches_nothing(self):
        """:nth-child(4 of .x) matches nothing — only 3 elements have class x."""
        result = select(self.ul, "li:nth-child(4 of .x)")
        assert result == []

    def test_query_selector_all_consistent(self):
        """query_selector_all at document level returns the same first-match result."""
        result = self.doc.query_selector_all("li:nth-child(1 of .x)")
        texts = [el.text_content for el in result]
        assert texts == ["A"]


# ============================================================================
# Group 2 — Mixed sibling types
# ============================================================================
#
# HTML: <div><p>P1</p><span>S1</span><p>P2</p><span>S2</span></div>
# :nth-child(N of p) counts only <p> siblings; same for <span>.
# ============================================================================


class TestGroup2MixedSiblingTypes:
    """Mixed tag types — filter selects only elements of a specific type."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.doc = HTMLDocument.parse(
            "<div><p>P1</p><span>S1</span><p>P2</p><span>S2</span></div>"
        )
        self.div = self.doc.query_selector("div")

    def test_first_p_element(self):
        """:nth-child(1 of p) selects P1."""
        result = select(self.div, "p:nth-child(1 of p)")
        assert len(result) == 1
        assert result[0].text_content == "P1"

    def test_second_p_element(self):
        """:nth-child(2 of p) selects P2."""
        result = select(self.div, "p:nth-child(2 of p)")
        assert len(result) == 1
        assert result[0].text_content == "P2"

    def test_first_span_element(self):
        """:nth-child(1 of span) selects S1."""
        result = select(self.div, "span:nth-child(1 of span)")
        assert len(result) == 1
        assert result[0].text_content == "S1"

    def test_second_span_element(self):
        """:nth-child(2 of span) selects S2."""
        result = select(self.div, "span:nth-child(2 of span)")
        assert len(result) == 1
        assert result[0].text_content == "S2"

    def test_p_filter_does_not_select_span(self):
        """:nth-child(1 of p) must not select <span> elements."""
        result = select(self.div, "span:nth-child(1 of p)")
        assert result == []


# ============================================================================
# Group 3 — :nth-last-child(of S) — from-end filtering
# ============================================================================
#
# HTML: <ul><li class='x'>A</li><li>B</li><li class='x'>C</li></ul>
# Filtered set (by .x) from-end: C (pos 1), A (pos 2).
# ============================================================================


class TestGroup3NthLastChildOfS:
    """:nth-last-child(An+B of S) counts filtered siblings from the end."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.doc = HTMLDocument.parse(
            "<ul><li class='x'>A</li><li>B</li><li class='x'>C</li></ul>"
        )
        self.ul = self.doc.query_selector("ul")

    def test_last_class_element(self):
        """:nth-last-child(1 of .x) selects C — last element with class x."""
        result = select(self.ul, "li:nth-last-child(1 of .x)")
        assert len(result) == 1
        assert result[0].text_content == "C"

    def test_second_from_last_class_element(self):
        """:nth-last-child(2 of .x) selects A — second-to-last element with class x."""
        result = select(self.ul, "li:nth-last-child(2 of .x)")
        assert len(result) == 1
        assert result[0].text_content == "A"

    def test_beyond_end_no_match(self):
        """:nth-last-child(3 of .x) matches nothing — only 2 filtered elements."""
        result = select(self.ul, "li:nth-last-child(3 of .x)")
        assert result == []

    def test_query_selector_all_nth_last_child(self):
        """query_selector_all with :nth-last-child(1 of .x) returns correct element."""
        result = self.doc.query_selector_all("li:nth-last-child(1 of .x)")
        assert len(result) == 1
        assert result[0].text_content == "C"


# ============================================================================
# Group 4 — Multi-selector filter
# ============================================================================
#
# HTML: <div><p class='item'>P1</p><span>S1</span><p>P2</p><li class='item'>L1</li></div>
# Filter: "p, .item" — union: elements matching <p> OR class item.
# Filtered set: P1 (p + .item), P2 (p), L1 (.item) — positions 1, 2, 3.
# S1 (span without .item) is excluded from the filtered set.
# ============================================================================


class TestGroup4MultiSelectorFilter:
    """Selector list filter 'p, .item' — union matching across element types."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.doc = HTMLDocument.parse(
            "<div>"
            "<p class='item'>P1</p>"
            "<span>S1</span>"
            "<p>P2</p>"
            "<li class='item'>L1</li>"
            "</div>"
        )
        self.div = self.doc.query_selector("div")

    def test_first_in_filter_union(self):
        """:nth-child(1 of p, .item) selects P1 (matches both p and .item)."""
        result = select(self.div, ":nth-child(1 of p, .item)")
        assert len(result) == 1
        assert result[0].text_content == "P1"

    def test_second_in_filter_union(self):
        """:nth-child(2 of p, .item) selects P2 (matches p)."""
        result = select(self.div, ":nth-child(2 of p, .item)")
        assert len(result) == 1
        assert result[0].text_content == "P2"

    def test_third_in_filter_union(self):
        """:nth-child(3 of p, .item) selects L1 (matches .item)."""
        result = select(self.div, ":nth-child(3 of p, .item)")
        assert len(result) == 1
        assert result[0].text_content == "L1"

    def test_span_excluded_from_filter_union(self):
        """S1 (<span> without .item) is not in the filtered set — no 4th element."""
        result = select(self.div, ":nth-child(4 of p, .item)")
        assert result == []


# ============================================================================
# Group 5 — Interaction with combinators
# ============================================================================
#
# HTML: <div><span>S1</span><p>P1</p><span>S2</span></div>
# "div > :nth-child(2 of span)" — descendant combinator + child combinator.
# Filtered set (by span among children of div): S1 (pos 1), S2 (pos 2).
# ============================================================================


class TestGroup5Combinators:
    """Child combinator restricts scope; :nth-child(of S) applies within that scope."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.doc = HTMLDocument.parse(
            "<div><span>S1</span><p>P1</p><span>S2</span></div>"
        )

    def test_second_span_child_of_div(self):
        """:nth-child(2 of span) within div> combinator selects S2."""
        result = self.doc.query_selector_all("div > :nth-child(2 of span)")
        assert len(result) == 1
        assert result[0].text_content == "S2"

    def test_first_span_child_of_div(self):
        """:nth-child(1 of span) within div> combinator selects S1."""
        result = self.doc.query_selector_all("div > :nth-child(1 of span)")
        assert len(result) == 1
        assert result[0].text_content == "S1"

    def test_p_element_excluded_from_span_filter(self):
        """:nth-child(1 of span) must not select <p> P1."""
        result = self.doc.query_selector_all("div > p:nth-child(1 of span)")
        assert len(result) == 0


# ============================================================================
# Group 6 — Specificity-driven cascade verification
# ============================================================================
#
# CSS Selectors Level 4 §16: specificity of :nth-child(An+B of S) is
# (0,1,0) for the pseudo-class itself PLUS max specificity of the filter S.
#
# Rule A: li:nth-child(2) → specificity (0,1,1)  [0-class + 1-pseudo + 1-type]
# Rule B: li:nth-child(2 of .x) → specificity (0,2,1) [0-class + 2-pseudo/class + 1-type]
#
# Rule B (higher specificity) wins for a <li class='x'> at child position 2.
# ============================================================================


class TestGroup6SpecificityDrivenCascade:
    """Specificity of :nth-child(An+B of S) is pseudo + max(filter specificity)."""

    def test_nth_child_without_filter_specificity(self):
        """li:nth-child(2) has specificity (0,1,1) — one pseudo-class + one type."""
        from aspose_html.css._parser import parse
        from aspose_html.css._specificity import specificity
        sel = parse("li:nth-child(2)").selectors[0]
        assert specificity(sel) == (0, 1, 1)

    def test_nth_child_with_class_filter_specificity(self):
        """li:nth-child(2 of .x) has specificity (0,2,1) — higher than plain nth-child."""
        from aspose_html.css._parser import parse
        from aspose_html.css._specificity import specificity
        sel = parse("li:nth-child(2 of .x)").selectors[0]
        assert specificity(sel) == (0, 2, 1)

    def test_nth_child_with_id_filter_specificity(self):
        """:nth-child(2 of #id) has specificity (1,1,0)."""
        from aspose_html.css._parser import parse
        from aspose_html.css._specificity import specificity
        sel = parse(":nth-child(2 of #id)").selectors[0]
        assert specificity(sel) == (1, 1, 0)

    def test_filtered_specificity_exceeds_plain(self):
        """Filtered selector always has strictly greater specificity than plain nth-child."""
        from aspose_html.css._parser import parse
        from aspose_html.css._specificity import specificity
        plain = specificity(parse("li:nth-child(2)").selectors[0])
        filtered = specificity(parse("li:nth-child(2 of .x)").selectors[0])
        assert filtered > plain

    def test_multi_selector_filter_max_specificity(self):
        """:nth-child(2 of p, #id) uses max specificity of filter — (1,1,0)."""
        from aspose_html.css._parser import parse
        from aspose_html.css._specificity import specificity
        # filter "p, #id": p specificity (0,0,1); #id specificity (1,0,0)
        # max is (1,0,0); total = (0,1,0) + (1,0,0) = (1,1,0)
        sel = parse(":nth-child(2 of p, #id)").selectors[0]
        assert specificity(sel) == (1, 1, 0)


# ============================================================================
# Group 7 — Regression: existing :nth-child and :nth-of-type
# ============================================================================
#
# All pre-Track-52 positional pseudo-classes must continue to work exactly
# as before. The :nth-child(of S) extension must not affect the common path.
# ============================================================================


class TestGroup7Regression:
    """Regression check — pre-Track-52 positional selectors unchanged."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.doc_list = HTMLDocument.parse(
            "<ul><li>A</li><li>B</li><li>C</li><li>D</li></ul>"
        )
        self.ul = self.doc_list.query_selector("ul")

    def test_nth_child_integer_unchanged(self):
        """:nth-child(2) still selects second child (B) — no filter."""
        result = select(self.ul, "li:nth-child(2)")
        assert len(result) == 1
        assert result[0].text_content == "B"

    def test_nth_child_odd_unchanged(self):
        """:nth-child(odd) still selects positions 1, 3 (A, C)."""
        result = select(self.ul, "li:nth-child(odd)")
        texts = [el.text_content for el in result]
        assert texts == ["A", "C"]

    def test_nth_child_2n_plus_1_unchanged(self):
        """:nth-child(2n+1) equals :nth-child(odd) — A, C."""
        result = select(self.ul, "li:nth-child(2n+1)")
        texts = [el.text_content for el in result]
        assert texts == ["A", "C"]

    def test_nth_child_even_unchanged(self):
        """:nth-child(even) selects positions 2, 4 (B, D)."""
        result = select(self.ul, "li:nth-child(even)")
        texts = [el.text_content for el in result]
        assert texts == ["B", "D"]

    def test_nth_of_type_unchanged(self):
        """:nth-of-type(2) among mixed siblings selects second <p> (P2)."""
        doc = HTMLDocument.parse("<div><p>P1</p><span>S1</span><p>P2</p><span>S2</span></div>")
        div = doc.query_selector("div")
        result = select(div, "p:nth-of-type(2)")
        assert len(result) == 1
        assert result[0].text_content == "P2"

    def test_nth_last_of_type_unchanged(self):
        """:nth-last-of-type(1) selects the last sibling of each type."""
        doc = HTMLDocument.parse("<div><p>P1</p><span>S1</span><p>P2</p><span>S2</span></div>")
        div = doc.query_selector("div")
        result = select(div, "p:nth-last-of-type(1)")
        assert len(result) == 1
        assert result[0].text_content == "P2"

    def test_nth_last_child_unchanged(self):
        """:nth-last-child(1) without filter selects the last child (D)."""
        result = select(self.ul, "li:nth-last-child(1)")
        assert len(result) == 1
        assert result[0].text_content == "D"


# ============================================================================
# Group 8 — Edge: 0n+1 equivalence
# ============================================================================
#
# HTML: <ul><li class='x'>A</li><li>B</li><li class='x'>C</li></ul>
# :nth-child(0n+1 of .x) and :nth-child(1 of .x) must return the same element.
# ============================================================================


class TestGroup8ZeroNEquivalence:
    """0n+B is algebraically identical to position B in the filtered set."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.doc = HTMLDocument.parse(
            "<ul><li class='x'>A</li><li>B</li><li class='x'>C</li></ul>"
        )
        self.ul = self.doc.query_selector("ul")

    def test_zero_n_plus_1_equals_1(self):
        """:nth-child(0n+1 of .x) is equivalent to :nth-child(1 of .x) — both return A."""
        r_form1 = select(self.ul, "li:nth-child(0n+1 of .x)")
        r_form2 = select(self.ul, "li:nth-child(1 of .x)")
        assert len(r_form1) == 1
        assert len(r_form2) == 1
        assert r_form1[0].text_content == r_form2[0].text_content == "A"

    def test_zero_n_plus_2_equals_2(self):
        """:nth-child(0n+2 of .x) is equivalent to :nth-child(2 of .x) — both return C."""
        r_form1 = select(self.ul, "li:nth-child(0n+2 of .x)")
        r_form2 = select(self.ul, "li:nth-child(2 of .x)")
        assert len(r_form1) == 1
        assert len(r_form2) == 1
        assert r_form1[0].text_content == r_form2[0].text_content == "C"


# ============================================================================
# Group 9 — Edge: empty filtered set
# ============================================================================
#
# HTML: <ul><li>A</li><li>B</li></ul>
# No <li> has class 'x' — filtered set is empty, selector matches nothing.
# ============================================================================


class TestGroup9EmptyFilteredSet:
    """When no siblings match filter S, :nth-child(N of S) matches nothing."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.doc = HTMLDocument.parse("<ul><li>A</li><li>B</li></ul>")
        self.ul = self.doc.query_selector("ul")

    def test_nth_child_no_match_in_empty_filter(self):
        """:nth-child(1 of .x) with no .x elements returns empty list."""
        result = select(self.ul, "li:nth-child(1 of .x)")
        assert result == []

    def test_nth_last_child_no_match_in_empty_filter(self):
        """:nth-last-child(1 of .x) with no .x elements returns empty list."""
        result = select(self.ul, "li:nth-last-child(1 of .x)")
        assert result == []

    def test_query_selector_all_empty_filter(self):
        """query_selector_all with empty-filter selector also returns empty list."""
        result = self.doc.query_selector_all("li:nth-child(1 of .x)")
        assert list(result) == []

    def test_nth_child_any_position_no_match(self):
        """:nth-child(100 of .x) also matches nothing when filter is empty."""
        result = select(self.ul, "li:nth-child(100 of .x)")
        assert result == []
