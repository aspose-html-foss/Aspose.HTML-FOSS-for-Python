"""Tests for Node.compare_document_position() and DocumentFragment query methods.

Covers BACK-40 / ADR-036 / SPEC-037.
"""
import pytest

from aspose_html.dom import Document, DocumentPosition, NodeList


# ---------------------------------------------------------------------------
# DocumentPosition constant values
# ---------------------------------------------------------------------------

class TestDocumentPositionConstants:
    def test_document_position_constants_importable(self):
        """DocumentPosition constants must be importable from aspose_html.dom
        and have the correct WHATWG DOM §4.4.3 values.
        """
        assert DocumentPosition.DOCUMENT_POSITION_DISCONNECTED == 1
        assert DocumentPosition.DOCUMENT_POSITION_PRECEDING == 2
        assert DocumentPosition.DOCUMENT_POSITION_FOLLOWING == 4
        assert DocumentPosition.DOCUMENT_POSITION_CONTAINS == 8
        assert DocumentPosition.DOCUMENT_POSITION_CONTAINED_BY == 16
        assert DocumentPosition.DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC == 32


# ---------------------------------------------------------------------------
# compare_document_position — same node
# ---------------------------------------------------------------------------

class TestCompareDocumentPositionSameNode:
    def test_same_node_returns_zero(self):
        """node.compare_document_position(node) must return 0."""
        doc = Document()
        el = doc.create_element("div")
        assert el.compare_document_position(el) == 0

    def test_same_document_returns_zero(self):
        """Document compared to itself returns 0."""
        doc = Document()
        assert doc.compare_document_position(doc) == 0


# ---------------------------------------------------------------------------
# compare_document_position — ancestor/descendant
# ---------------------------------------------------------------------------

class TestCompareDocumentPositionContainment:
    def test_child_contains_parent(self):
        """child.compare_document_position(parent) has CONTAINS | PRECEDING bits.

        When other (parent) is an ancestor of self (child), other CONTAINS self
        and precedes self in document order.
        """
        doc = Document()
        parent = doc.create_element("div")
        child = doc.create_element("span")
        doc.append_child(parent)
        parent.append_child(child)

        result = child.compare_document_position(parent)
        CONTAINS = DocumentPosition.DOCUMENT_POSITION_CONTAINS
        PRECEDING = DocumentPosition.DOCUMENT_POSITION_PRECEDING
        assert bool(result & CONTAINS), f"Expected CONTAINS bit; got {result}"
        assert bool(result & PRECEDING), f"Expected PRECEDING bit; got {result}"

    def test_parent_contained_by_child(self):
        """parent.compare_document_position(child) has CONTAINED_BY | FOLLOWING bits.

        When other (child) is a descendant of self (parent), other is
        CONTAINED_BY self and follows self in document order.
        """
        doc = Document()
        parent = doc.create_element("div")
        child = doc.create_element("span")
        doc.append_child(parent)
        parent.append_child(child)

        result = parent.compare_document_position(child)
        CONTAINED_BY = DocumentPosition.DOCUMENT_POSITION_CONTAINED_BY
        FOLLOWING = DocumentPosition.DOCUMENT_POSITION_FOLLOWING
        assert bool(result & CONTAINED_BY), f"Expected CONTAINED_BY bit; got {result}"
        assert bool(result & FOLLOWING), f"Expected FOLLOWING bit; got {result}"

    def test_deep_tree_contains_preceding(self):
        """Deep nesting: p.compare_document_position(doc) has CONTAINS and PRECEDING."""
        doc = Document()
        div = doc.create_element("div")
        section = doc.create_element("section")
        p = doc.create_element("p")
        doc.append_child(div)
        div.append_child(section)
        section.append_child(p)

        result = p.compare_document_position(doc)
        CONTAINS = DocumentPosition.DOCUMENT_POSITION_CONTAINS
        PRECEDING = DocumentPosition.DOCUMENT_POSITION_PRECEDING
        assert bool(result & CONTAINS)
        assert bool(result & PRECEDING)

    def test_deep_tree_contained_by_following(self):
        """Deep nesting: doc.compare_document_position(p) has CONTAINED_BY and FOLLOWING."""
        doc = Document()
        div = doc.create_element("div")
        section = doc.create_element("section")
        p = doc.create_element("p")
        doc.append_child(div)
        div.append_child(section)
        section.append_child(p)

        result = doc.compare_document_position(p)
        CONTAINED_BY = DocumentPosition.DOCUMENT_POSITION_CONTAINED_BY
        FOLLOWING = DocumentPosition.DOCUMENT_POSITION_FOLLOWING
        assert bool(result & CONTAINED_BY)
        assert bool(result & FOLLOWING)


# ---------------------------------------------------------------------------
# compare_document_position — siblings
# ---------------------------------------------------------------------------

class TestCompareDocumentPositionSiblings:
    def _build_siblings(self):
        doc = Document()
        parent = doc.create_element("div")
        a = doc.create_element("a")
        b = doc.create_element("b")
        doc.append_child(parent)
        parent.append_child(a)
        parent.append_child(b)
        return doc, parent, a, b

    def test_preceding_sibling(self):
        """b.compare_document_position(a) returns PRECEDING when a comes before b."""
        _, _, a, b = self._build_siblings()
        result = b.compare_document_position(a)
        PRECEDING = DocumentPosition.DOCUMENT_POSITION_PRECEDING
        FOLLOWING = DocumentPosition.DOCUMENT_POSITION_FOLLOWING
        assert bool(result & PRECEDING), f"Expected PRECEDING bit; got {result}"
        assert not bool(result & FOLLOWING), f"Expected no FOLLOWING bit; got {result}"

    def test_following_sibling(self):
        """a.compare_document_position(b) returns FOLLOWING when b comes after a."""
        _, _, a, b = self._build_siblings()
        result = a.compare_document_position(b)
        FOLLOWING = DocumentPosition.DOCUMENT_POSITION_FOLLOWING
        PRECEDING = DocumentPosition.DOCUMENT_POSITION_PRECEDING
        assert bool(result & FOLLOWING), f"Expected FOLLOWING bit; got {result}"
        assert not bool(result & PRECEDING), f"Expected no PRECEDING bit; got {result}"

    def test_preceding_contains_not_set_for_siblings(self):
        """Sibling result must not have CONTAINS or CONTAINED_BY bits set."""
        _, _, a, b = self._build_siblings()
        CONTAINS = DocumentPosition.DOCUMENT_POSITION_CONTAINS
        CONTAINED_BY = DocumentPosition.DOCUMENT_POSITION_CONTAINED_BY
        r1 = a.compare_document_position(b)
        r2 = b.compare_document_position(a)
        assert not bool(r1 & CONTAINS)
        assert not bool(r1 & CONTAINED_BY)
        assert not bool(r2 & CONTAINS)
        assert not bool(r2 & CONTAINED_BY)


# ---------------------------------------------------------------------------
# compare_document_position — disconnected nodes
# ---------------------------------------------------------------------------

class TestCompareDocumentPositionDisconnected:
    def test_disconnected_nodes_have_disconnected_bit(self):
        """Nodes in different documents return DISCONNECTED | IMPLEMENTATION_SPECIFIC."""
        doc1 = Document()
        doc2 = Document()
        a = doc1.create_element("a")
        b = doc2.create_element("b")
        result = a.compare_document_position(b)
        DISCONNECTED = DocumentPosition.DOCUMENT_POSITION_DISCONNECTED
        IMPL_SPECIFIC = DocumentPosition.DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC
        assert bool(result & DISCONNECTED), f"Expected DISCONNECTED bit; got {result}"
        assert bool(result & IMPL_SPECIFIC), f"Expected IMPL_SPECIFIC bit; got {result}"

    def test_disconnected_nodes_deterministic(self):
        """Same disconnected pair always returns the same result (stable tiebreaker)."""
        doc1 = Document()
        doc2 = Document()
        a = doc1.create_element("a")
        b = doc2.create_element("b")
        result1 = a.compare_document_position(b)
        result2 = a.compare_document_position(b)
        assert result1 == result2

    def test_disconnected_nodes_complementary(self):
        """If a.compare_document_position(b) has PRECEDING, b has FOLLOWING."""
        doc1 = Document()
        doc2 = Document()
        a = doc1.create_element("a")
        b = doc2.create_element("b")
        r_ab = a.compare_document_position(b)
        r_ba = b.compare_document_position(a)
        PRECEDING = DocumentPosition.DOCUMENT_POSITION_PRECEDING
        FOLLOWING = DocumentPosition.DOCUMENT_POSITION_FOLLOWING
        # The two results must use opposite PRECEDING/FOLLOWING bits.
        ab_preceding = bool(r_ab & PRECEDING)
        ab_following = bool(r_ab & FOLLOWING)
        ba_preceding = bool(r_ba & PRECEDING)
        ba_following = bool(r_ba & FOLLOWING)
        # Exactly one of PRECEDING/FOLLOWING set in each.
        assert ab_preceding != ab_following
        assert ba_preceding != ba_following
        # They must be complementary.
        assert ab_preceding == ba_following
        assert ab_following == ba_preceding


# ---------------------------------------------------------------------------
# DocumentFragment.query_selector
# ---------------------------------------------------------------------------

class TestDocumentFragmentQuerySelector:
    def test_fragment_query_selector_match(self):
        """frag.query_selector('p') returns the first <p> element."""
        doc = Document()
        frag = doc.create_document_fragment()
        p = doc.create_element("p")
        frag.append_child(p)
        assert frag.query_selector("p") is p

    def test_fragment_query_selector_none(self):
        """frag.query_selector returns None when no element matches."""
        doc = Document()
        frag = doc.create_document_fragment()
        p = doc.create_element("p")
        frag.append_child(p)
        assert frag.query_selector("div") is None

    def test_fragment_query_selector_nested(self):
        """frag.query_selector finds elements nested below the fragment root."""
        doc = Document()
        frag = doc.create_document_fragment()
        div = doc.create_element("div")
        p = doc.create_element("p")
        frag.append_child(div)
        div.append_child(p)
        assert frag.query_selector("p") is p

    def test_fragment_query_selector_first_only(self):
        """frag.query_selector returns only the first match in document order."""
        doc = Document()
        frag = doc.create_document_fragment()
        p1 = doc.create_element("p")
        p2 = doc.create_element("p")
        frag.append_child(p1)
        frag.append_child(p2)
        assert frag.query_selector("p") is p1

    def test_fragment_query_selector_empty_fragment(self):
        """query_selector on an empty fragment returns None."""
        doc = Document()
        frag = doc.create_document_fragment()
        assert frag.query_selector("p") is None


# ---------------------------------------------------------------------------
# DocumentFragment.query_selector_all
# ---------------------------------------------------------------------------

class TestDocumentFragmentQuerySelectorAll:
    def test_fragment_query_selector_all_multiple(self):
        """frag.query_selector_all returns all matching elements."""
        doc = Document()
        frag = doc.create_document_fragment()
        p1 = doc.create_element("p")
        p2 = doc.create_element("p")
        frag.append_child(p1)
        frag.append_child(p2)
        results = frag.query_selector_all("p")
        assert len(results) == 2

    def test_fragment_query_selector_all_empty(self):
        """frag.query_selector_all returns empty NodeList when no match."""
        doc = Document()
        frag = doc.create_document_fragment()
        p = doc.create_element("p")
        frag.append_child(p)
        results = frag.query_selector_all("div")
        assert len(results) == 0

    def test_fragment_query_selector_all_returns_nodelist(self):
        """query_selector_all returns a NodeList instance."""
        doc = Document()
        frag = doc.create_document_fragment()
        p = doc.create_element("p")
        frag.append_child(p)
        result = frag.query_selector_all("p")
        assert isinstance(result, NodeList)

    def test_fragment_query_selector_all_nested(self):
        """query_selector_all finds elements at any nesting depth."""
        doc = Document()
        frag = doc.create_document_fragment()
        div = doc.create_element("div")
        p1 = doc.create_element("p")
        p2 = doc.create_element("p")
        frag.append_child(div)
        div.append_child(p1)
        div.append_child(p2)
        results = frag.query_selector_all("p")
        assert len(results) == 2
