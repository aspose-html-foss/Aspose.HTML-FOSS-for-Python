"""Tests for Element.insert_adjacent_html, insert_adjacent_text, and
insert_adjacent_element; also webkit_matches_selector.

Covers BACK-109 / ADR-093 and BACK-186 / ADR-169.
"""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    NoModificationAllowedError,
    NodeType,
    SyntaxError as DOMSyntaxError,
)


@pytest.fixture
def doc() -> Document:
    return Document()


@pytest.fixture
def host_child(doc: Document):
    """Return (doc, host, child) — child inside host inside doc."""
    host = doc.create_element("div")
    doc.append_child(host)
    child = doc.create_element("span")
    host.append_child(child)
    return doc, host, child


# ---------------------------------------------------------------------------
# TestInsertAdjacentHtml
# ---------------------------------------------------------------------------


class TestInsertAdjacentHtml:
    def test_beforebegin_inserts_before_self(self, host_child):
        """AC-1: beforebegin inserts node before self, not inside."""
        doc, host, child = host_child
        child.insert_adjacent_html("beforebegin", "<b>A</b>")
        # host children should be: [<B>, <span>]
        assert host.first_child is not child
        assert host.first_child.node_name == "B"
        assert host.first_child.next_sibling is child

    def test_afterend_inserts_after_self(self, host_child):
        """AC-2: afterend inserts node as next_sibling of self."""
        doc, host, child = host_child
        child.insert_adjacent_html("afterend", "<i>Z</i>")
        assert child.next_sibling is not None
        assert child.next_sibling.node_name == "I"

    def test_afterbegin_inserts_as_first_child(self, host_child):
        """AC-3: afterbegin inserts fragment at start of self.children."""
        doc, host, child = host_child
        child.insert_adjacent_html("afterbegin", "<u>1</u>")
        assert child.first_child.node_name == "U"

    def test_beforeend_appends_as_last_child(self, host_child):
        """AC-4: beforeend appends fragment at end of self.children."""
        doc, host, child = host_child
        child.insert_adjacent_html("beforeend", "<s>2</s>")
        assert child.last_child.node_name == "S"

    def test_multiple_nodes_in_fragment(self, host_child):
        """AC-5: multi-node fragment inserted in correct order."""
        doc, host, child = host_child
        child.insert_adjacent_html("beforeend", "<b>1</b><i>2</i>")
        children = list(child.child_nodes)
        assert len(children) == 2
        assert children[0].node_name == "B"
        assert children[1].node_name == "I"

    def test_beforebegin_no_parent_raises(self, doc: Document):
        """AC-6: detached element + beforebegin raises NoModificationAllowedError."""
        el = doc.create_element("p")
        with pytest.raises(NoModificationAllowedError):
            el.insert_adjacent_html("beforebegin", "<b>x</b>")

    def test_afterend_no_parent_raises(self, doc: Document):
        """AC-7: detached element + afterend raises NoModificationAllowedError."""
        el = doc.create_element("p")
        with pytest.raises(NoModificationAllowedError):
            el.insert_adjacent_html("afterend", "<b>x</b>")

    def test_invalid_position_raises_syntax_error(self, host_child):
        """AC-8: unknown position raises DOMSyntaxError."""
        doc, host, child = host_child
        with pytest.raises(DOMSyntaxError):
            child.insert_adjacent_html("middle", "<b>x</b>")

    def test_position_is_case_insensitive(self, host_child):
        """AC-9: position comparison is case-insensitive; BeforeEnd works."""
        doc, host, child = host_child
        child.insert_adjacent_html("BeforeEnd", "<em>x</em>")
        assert child.last_child.node_name == "EM"

    def test_empty_html_is_no_op(self, host_child):
        """AC-10: html='' with any valid position leaves tree unchanged."""
        doc, host, child = host_child
        child_count_before = len(list(child.child_nodes))
        child.insert_adjacent_html("beforeend", "")
        assert len(list(child.child_nodes)) == child_count_before


# ---------------------------------------------------------------------------
# TestInsertAdjacentText
# ---------------------------------------------------------------------------


class TestInsertAdjacentText:
    def test_beforebegin_text_node_before_self(self, host_child):
        """AC-11: beforebegin creates Text node before self (not inside)."""
        doc, host, child = host_child
        child.insert_adjacent_text("beforebegin", "hello ")
        first = host.first_child
        assert first.node_type == NodeType.TEXT_NODE
        assert first.node_value == "hello "
        assert first.next_sibling is child

    def test_afterend_text_node_after_self(self, host_child):
        """AC-12: afterend creates Text node as next_sibling."""
        doc, host, child = host_child
        child.insert_adjacent_text("afterend", " world")
        sibling = child.next_sibling
        assert sibling is not None
        assert sibling.node_type == NodeType.TEXT_NODE
        assert sibling.node_value == " world"

    def test_afterbegin_text_node_first_child(self, host_child):
        """AC-13: afterbegin inserts Text as first_child of self."""
        doc, host, child = host_child
        child.insert_adjacent_text("afterbegin", "inner-start")
        assert child.first_child.node_type == NodeType.TEXT_NODE
        assert child.first_child.node_value == "inner-start"

    def test_beforeend_text_node_last_child(self, host_child):
        """AC-14: beforeend appends Text as last_child of self."""
        doc, host, child = host_child
        child.insert_adjacent_text("beforeend", "inner-end")
        assert child.last_child.node_type == NodeType.TEXT_NODE
        assert child.last_child.node_value == "inner-end"

    def test_text_not_parsed_as_html(self, host_child):
        """AC-15: raw HTML tags are not parsed — inserted as literal text."""
        doc, host, child = host_child
        child.insert_adjacent_text("beforeend", "<b>raw</b>")
        last = child.last_child
        # Must be a Text node, not a B element
        assert last.node_type == NodeType.TEXT_NODE
        assert last.node_value == "<b>raw</b>"

    def test_text_no_parent_raises_before_begin(self, doc: Document):
        """AC-16: detached + beforebegin raises NoModificationAllowedError."""
        el = doc.create_element("span")
        with pytest.raises(NoModificationAllowedError):
            el.insert_adjacent_text("beforebegin", "hi")

    def test_text_no_parent_raises_after_end(self, doc: Document):
        """AC-17: detached + afterend raises NoModificationAllowedError."""
        el = doc.create_element("span")
        with pytest.raises(NoModificationAllowedError):
            el.insert_adjacent_text("afterend", "hi")

    def test_text_invalid_position_raises_syntax_error(self, host_child):
        """AC-18: unknown position raises DOMSyntaxError."""
        doc, host, child = host_child
        with pytest.raises(DOMSyntaxError):
            child.insert_adjacent_text("start", "hi")

    def test_text_position_case_insensitive(self, host_child):
        """AC-19: AFTERBEGIN in uppercase works correctly."""
        doc, host, child = host_child
        child.insert_adjacent_text("AFTERBEGIN", "top")
        assert child.first_child.node_type == NodeType.TEXT_NODE
        assert child.first_child.node_value == "top"

    def test_afterbegin_on_detached_element_creates_standalone_text(self):
        """AC-20: detached element (no owner_doc) + afterbegin creates standalone Text."""
        from aspose_html.dom import Document
        # Create element but do NOT attach to any document
        doc = Document()
        el = doc.create_element("p")
        # el is owned by doc (create_element sets _owner_document), so use a
        # truly standalone element constructed from the class directly to hit
        # the owner_doc is None branch.
        from aspose_html.dom._element import Element
        standalone = Element.__new__(Element)
        standalone._node_type = NodeType.ELEMENT_NODE
        standalone._tag_name = "DIV"
        standalone._namespace_uri = None
        standalone._prefix = None
        standalone._local_name = "div"
        standalone._children = []
        standalone._parent = None
        standalone._owner_document = None
        standalone._attributes = {}
        standalone._event_listeners = {}
        standalone.insert_adjacent_text("afterbegin", "detached-text")
        assert standalone.first_child is not None
        assert standalone.first_child.node_value == "detached-text"


# ---------------------------------------------------------------------------
# TestInsertAdjacentElement — BACK-186 / ADR-169
# ---------------------------------------------------------------------------


class TestInsertAdjacentElement:
    def test_beforeend_inserts_as_last_child(self, host_child):
        """AC-1: beforeend inserts child as last child and returns it."""
        doc, host, child = host_child
        new = doc.create_element("b")
        result = host.insert_adjacent_element("beforeend", new)
        assert result is new
        assert host.last_child is new

    def test_afterbegin_inserts_as_first_child(self, host_child):
        """AC-2: afterbegin inserts element as first child of self."""
        doc, host, child = host_child
        new = doc.create_element("b")
        result = host.insert_adjacent_element("afterbegin", new)
        assert result is new
        assert host.first_child is new

    def test_beforebegin_inserts_before_self(self, host_child):
        """AC-3: beforebegin inserts other before self when self has a parent."""
        doc, host, child = host_child
        new = doc.create_element("b")
        result = child.insert_adjacent_element("beforebegin", new)
        assert result is new
        assert host.first_child is new
        assert new.next_sibling is child

    def test_afterend_inserts_after_self(self, host_child):
        """AC-4: afterend inserts other after self when self has a parent."""
        doc, host, child = host_child
        new = doc.create_element("b")
        result = child.insert_adjacent_element("afterend", new)
        assert result is new
        assert child.next_sibling is new

    def test_beforebegin_detached_raises(self, doc: Document):
        """AC-5: beforebegin on detached element raises NoModificationAllowedError."""
        el = doc.create_element("div")
        other = doc.create_element("span")
        with pytest.raises(NoModificationAllowedError):
            el.insert_adjacent_element("beforebegin", other)

    def test_afterend_detached_raises(self, doc: Document):
        """AC-5b: afterend on detached element raises NoModificationAllowedError."""
        el = doc.create_element("div")
        other = doc.create_element("span")
        with pytest.raises(NoModificationAllowedError):
            el.insert_adjacent_element("afterend", other)

    def test_invalid_position_raises_syntax_error(self, host_child):
        """AC-6: unknown position raises DOMSyntaxError."""
        doc, host, child = host_child
        new = doc.create_element("b")
        with pytest.raises(DOMSyntaxError):
            child.insert_adjacent_element("bad", new)

    def test_none_element_returns_none(self, host_child):
        """AC-7: passing None returns None without any tree mutation."""
        doc, host, child = host_child
        child_count = len(list(host.child_nodes))
        result = host.insert_adjacent_element("beforeend", None)
        assert result is None
        assert len(list(host.child_nodes)) == child_count

    def test_position_case_insensitive(self, host_child):
        """AC-1 variant: position comparison is case-insensitive."""
        doc, host, child = host_child
        new = doc.create_element("i")
        result = host.insert_adjacent_element("BeforeEnd", new)
        assert result is new
        assert host.last_child is new

    def test_returns_the_inserted_element(self, host_child):
        """Return value must be the same object as the element argument."""
        doc, host, child = host_child
        new = doc.create_element("em")
        assert host.insert_adjacent_element("afterbegin", new) is new


# ---------------------------------------------------------------------------
# TestWebkitMatchesSelector — BACK-186 / ADR-169
# ---------------------------------------------------------------------------


class TestWebkitMatchesSelector:
    def test_returns_true_for_matching_tag(self, doc: Document):
        """AC-8: webkit_matches_selector returns True for <div> matched with 'div'."""
        el = doc.create_element("div")
        assert el.webkit_matches_selector("div") is True

    def test_returns_false_for_non_matching_tag(self, doc: Document):
        """AC-9: webkit_matches_selector returns False for <div> matched with 'span'."""
        el = doc.create_element("div")
        assert el.webkit_matches_selector("span") is False

    def test_equals_matches_result(self, doc: Document):
        """AC-10: webkit_matches_selector(s) == matches(s) for the same input."""
        el = doc.create_element("div")
        el.set_attribute("class", "active")
        for selector in ("div", "span", ".active", ".inactive", "*"):
            assert el.webkit_matches_selector(selector) == el.matches(selector)
