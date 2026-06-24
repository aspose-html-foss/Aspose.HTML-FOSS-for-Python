"""Tests for TreeWalker, NodeIterator, and NodeFilter.

Per  /  acceptance criteria:
  AC-1   create_tree_walker(body, SHOW_ELEMENT) creates a TreeWalker
  AC-2   next_node() visits all element descendants in document order
  AC-3   FILTER_REJECT on a div prevents descent into that div's children
  AC-4   first_child() moves current_node to the first accepted child
  AC-5   parent_node() returns None at root boundary
  AC-6   create_node_iterator(body, SHOW_TEXT) visits only Text nodes
  AC-7   next_node() / previous_node() on iterator — forward/backward
  AC-8   detach() is a no-op
  AC-9   NodeFilter.SHOW_ELEMENT, FILTER_ACCEPT etc. importable from aspose_html.dom
  AC-10  TreeWalker, NodeIterator importable from aspose_html.dom
  AC-11  All public APIs have type hints and docstring examples ()
  AC-12  All existing tests continue to pass
  Extra  what_to_show=SHOW_TEXT skips element nodes without calling filter
  Extra  current_node setter repositions walker; next_node continues from there
"""
import pytest
from aspose_html.dom import (
    Document,
    NodeFilter,
    NodeIterator,
    TreeWalker,
    NodeType,
)
from aspose_html.dom._traversal import (
    _filter_node,
    _next_node_in_tree,
    _previous_node_in_tree,
    _last_descendant,
    _get_next_sibling,
    _get_previous_sibling,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_doc():
    """Build a simple DOM:

        <body>
          <div>
            <p>hello</p>
            <span>world</span>
          </div>
          <section>
            <h1>title</h1>
          </section>
        </body>

    Returns (doc, body, div, p, t_hello, span, t_world, section, h1, t_title).
    """
    doc = Document()
    body = doc.create_element("body")
    div = doc.create_element("div")
    p = doc.create_element("p")
    t_hello = doc.create_text_node("hello")
    span = doc.create_element("span")
    t_world = doc.create_text_node("world")
    section = doc.create_element("section")
    h1 = doc.create_element("h1")
    t_title = doc.create_text_node("title")

    p.append_child(t_hello)
    span.append_child(t_world)
    div.append_child(p)
    div.append_child(span)
    h1.append_child(t_title)
    section.append_child(h1)
    body.append_child(div)
    body.append_child(section)
    doc.append_child(body)

    return doc, body, div, p, t_hello, span, t_world, section, h1, t_title


# ---------------------------------------------------------------------------
# AC-9: NodeFilter constants importable from aspose_html.dom
# ---------------------------------------------------------------------------

class TestNodeFilterConstants:
    """WHATWG DOM §6.1 — NodeFilter constants. ."""

    def test_show_all(self):
        assert NodeFilter.SHOW_ALL == 0xFFFFFFFF

    def test_show_element(self):
        assert NodeFilter.SHOW_ELEMENT == 0x1

    def test_show_attribute(self):
        assert NodeFilter.SHOW_ATTRIBUTE == 0x2

    def test_show_text(self):
        assert NodeFilter.SHOW_TEXT == 0x4

    def test_show_cdata_section(self):
        assert NodeFilter.SHOW_CDATA_SECTION == 0x8

    def test_show_processing_instruction(self):
        assert NodeFilter.SHOW_PROCESSING_INSTRUCTION == 0x40

    def test_show_comment(self):
        assert NodeFilter.SHOW_COMMENT == 0x80

    def test_show_document(self):
        assert NodeFilter.SHOW_DOCUMENT == 0x100

    def test_show_document_type(self):
        assert NodeFilter.SHOW_DOCUMENT_TYPE == 0x200

    def test_show_document_fragment(self):
        assert NodeFilter.SHOW_DOCUMENT_FRAGMENT == 0x400

    def test_filter_accept(self):
        assert NodeFilter.FILTER_ACCEPT == 1

    def test_filter_reject(self):
        assert NodeFilter.FILTER_REJECT == 2

    def test_filter_skip(self):
        assert NodeFilter.FILTER_SKIP == 3


# ---------------------------------------------------------------------------
# AC-10: TreeWalker and NodeIterator importable
# ---------------------------------------------------------------------------

class TestImports:
    def test_treewalker_importable(self):
        assert TreeWalker is not None

    def test_nodeiterator_importable(self):
        assert NodeIterator is not None

    def test_nodefilter_importable(self):
        assert NodeFilter is not None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_get_next_sibling_last(self):
        doc = Document()
        parent = doc.create_element("div")
        a = doc.create_element("a")
        b = doc.create_element("b")
        parent.append_child(a)
        parent.append_child(b)
        assert _get_next_sibling(a) is b
        assert _get_next_sibling(b) is None

    def test_get_previous_sibling(self):
        doc = Document()
        parent = doc.create_element("div")
        a = doc.create_element("a")
        b = doc.create_element("b")
        parent.append_child(a)
        parent.append_child(b)
        assert _get_previous_sibling(b) is a
        assert _get_previous_sibling(a) is None

    def test_last_descendant_no_children(self):
        doc = Document()
        leaf = doc.create_element("p")
        assert _last_descendant(leaf) is leaf

    def test_last_descendant_nested(self):
        doc = Document()
        outer = doc.create_element("div")
        inner = doc.create_element("p")
        text = doc.create_text_node("x")
        inner.append_child(text)
        outer.append_child(inner)
        assert _last_descendant(outer) is text

    def test_next_node_in_tree_first_child(self):
        """_next_node_in_tree descends into first child for DFS pre-order."""
        doc = Document()
        parent = doc.create_element("div")
        child = doc.create_element("p")
        parent.append_child(child)
        # Within root=parent, the next node after parent (root) is its first child.
        assert _next_node_in_tree(parent, parent) is child
        # The child is a leaf with no next sibling within root → exhausted.
        assert _next_node_in_tree(child, parent) is None

    def test_next_node_in_tree_sibling(self):
        doc = Document()
        root = doc.create_element("div")
        a = doc.create_element("a")
        b = doc.create_element("b")
        root.append_child(a)
        root.append_child(b)
        assert _next_node_in_tree(a, root) is b

    def test_filter_node_show_bit_not_set(self):
        """what_to_show excludes element → FILTER_SKIP without calling filter."""
        doc = Document()
        el = doc.create_element("div")
        called = []
        def my_filter(n):
            called.append(n)
            return NodeFilter.FILTER_ACCEPT
        result = _filter_node(el, NodeFilter.SHOW_TEXT, my_filter)
        assert result == NodeFilter.FILTER_SKIP
        assert called == []  # filter must not be called

    def test_filter_node_no_filter_fn(self):
        doc = Document()
        el = doc.create_element("div")
        result = _filter_node(el, NodeFilter.SHOW_ELEMENT, None)
        assert result == NodeFilter.FILTER_ACCEPT

    def test_filter_node_with_filter_fn(self):
        doc = Document()
        el = doc.create_element("div")
        result = _filter_node(el, NodeFilter.SHOW_ELEMENT, lambda n: NodeFilter.FILTER_REJECT)
        assert result == NodeFilter.FILTER_REJECT


# ---------------------------------------------------------------------------
# AC-1: create_tree_walker factory
# ---------------------------------------------------------------------------

class TestCreateTreeWalker:
    def test_returns_treewalker(self):
        doc, body, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        assert isinstance(walker, TreeWalker)

    def test_current_node_starts_at_root(self):
        doc, body, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        assert walker.current_node is body

    def test_root_is_set(self):
        doc, body, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        assert walker.root is body

    def test_what_to_show_set(self):
        doc, body, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_TEXT)
        assert walker.what_to_show == NodeFilter.SHOW_TEXT

    def test_filter_none_by_default(self):
        doc, body, *_ = _make_doc()
        walker = doc.create_tree_walker(body)
        assert walker.filter is None


# ---------------------------------------------------------------------------
# AC-2: next_node() visits all element descendants in document order
# ---------------------------------------------------------------------------

class TestTreeWalkerNextNode:
    def test_visits_all_elements_in_order(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        names = []
        node = walker.next_node()
        while node is not None:
            names.append(node.node_name)
            node = walker.next_node()
        # body is the root; next_node() from root starts with children
        assert names == ["DIV", "P", "SPAN", "SECTION", "H1"]

    def test_stops_at_root_boundary(self):
        doc, body, div, p, *_ = _make_doc()
        walker = doc.create_tree_walker(div, NodeFilter.SHOW_ELEMENT)
        names = []
        node = walker.next_node()
        while node is not None:
            names.append(node.node_name)
            node = walker.next_node()
        assert names == ["P", "SPAN"]

    def test_returns_none_on_empty_root(self):
        doc = Document()
        leaf = doc.create_element("div")
        doc.append_child(leaf)
        walker = doc.create_tree_walker(leaf, NodeFilter.SHOW_ELEMENT)
        assert walker.next_node() is None

    def test_show_all_includes_text_nodes(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ALL)
        collected = []
        node = walker.next_node()
        while node is not None:
            collected.append(node)
            node = walker.next_node()
        assert t_hello in collected
        assert t_world in collected


# ---------------------------------------------------------------------------
# AC-3: FILTER_REJECT prevents descent into div's children
# ---------------------------------------------------------------------------

class TestTreeWalkerFilterReject:
    def test_reject_div_skips_children(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()

        def my_filter(node):
            if node.node_name == "DIV":
                return NodeFilter.FILTER_REJECT
            return NodeFilter.FILTER_ACCEPT

        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT, my_filter)
        names = []
        node = walker.next_node()
        while node is not None:
            names.append(node.node_name)
            node = walker.next_node()
        # DIV is rejected → neither DIV nor its children (P, SPAN) are visited
        assert "DIV" not in names
        assert "P" not in names
        assert "SPAN" not in names
        # SECTION and H1 are still visited
        assert "SECTION" in names
        assert "H1" in names

    def test_reject_section_skips_h1(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()

        def reject_section(node):
            if node.node_name == "SECTION":
                return NodeFilter.FILTER_REJECT
            return NodeFilter.FILTER_ACCEPT

        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT, reject_section)
        names = []
        node = walker.next_node()
        while node is not None:
            names.append(node.node_name)
            node = walker.next_node()
        assert "SECTION" not in names
        assert "H1" not in names
        assert "DIV" in names


# ---------------------------------------------------------------------------
# AC-4: first_child() moves current_node to first accepted child
# ---------------------------------------------------------------------------

class TestTreeWalkerFirstChild:
    def test_first_child_element(self):
        doc, body, div, p, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        result = walker.first_child()
        assert result is div
        assert walker.current_node is div

    def test_first_child_after_skip(self):
        """FILTER_SKIP on div → descend into div's children to find first ACCEPT."""
        doc, body, div, p, *_ = _make_doc()

        def skip_div(node):
            if node.node_name == "DIV":
                return NodeFilter.FILTER_SKIP
            return NodeFilter.FILTER_ACCEPT

        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT, skip_div)
        result = walker.first_child()
        # div is SKIPped → walker descends into div's children; first is P
        assert result is p
        assert walker.current_node is p

    def test_first_child_none_when_no_children(self):
        doc = Document()
        leaf = doc.create_element("p")
        doc.append_child(leaf)
        walker = doc.create_tree_walker(leaf, NodeFilter.SHOW_ELEMENT)
        assert walker.first_child() is None
        assert walker.current_node is leaf  # unchanged

    def test_last_child(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        result = walker.last_child()
        assert result is section
        assert walker.current_node is section


# ---------------------------------------------------------------------------
# AC-5: parent_node() returns None at root boundary
# ---------------------------------------------------------------------------

class TestTreeWalkerParentNode:
    def test_parent_node_moves_up(self):
        doc, body, div, p, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        walker.current_node = p
        result = walker.parent_node()
        assert result is div
        assert walker.current_node is div

    def test_parent_node_returns_none_at_root(self):
        doc, body, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        assert walker.parent_node() is None
        assert walker.current_node is body  # unchanged

    def test_parent_node_skips_non_accepted(self):
        """parent_node() skips ancestors rejected by filter, finds next ACCEPT."""
        doc, body, div, p, *_ = _make_doc()

        def skip_div(node):
            if node.node_name == "DIV":
                return NodeFilter.FILTER_SKIP
            return NodeFilter.FILTER_ACCEPT

        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT, skip_div)
        walker.current_node = p
        result = walker.parent_node()
        # div is SKIP → parent_node continues up and finds body (ACCEPT)
        assert result is body

    def test_parent_node_within_sub_root(self):
        doc, body, div, p, *_ = _make_doc()
        walker = doc.create_tree_walker(div, NodeFilter.SHOW_ELEMENT)
        walker.current_node = p
        result = walker.parent_node()
        assert result is div
        # At div (which is root), calling parent_node() again returns None
        assert walker.parent_node() is None


# ---------------------------------------------------------------------------
# TreeWalker: next_sibling / previous_sibling
# ---------------------------------------------------------------------------

class TestTreeWalkerSiblings:
    def test_next_sibling(self):
        doc, body, div, p, t_hello, span, *_ = _make_doc()
        walker = doc.create_tree_walker(div, NodeFilter.SHOW_ELEMENT)
        walker.current_node = p
        result = walker.next_sibling()
        assert result is span
        assert walker.current_node is span

    def test_previous_sibling(self):
        doc, body, div, p, t_hello, span, *_ = _make_doc()
        walker = doc.create_tree_walker(div, NodeFilter.SHOW_ELEMENT)
        walker.current_node = span
        result = walker.previous_sibling()
        assert result is p

    def test_next_sibling_returns_none_at_last(self):
        doc, body, div, p, t_hello, span, *_ = _make_doc()
        walker = doc.create_tree_walker(div, NodeFilter.SHOW_ELEMENT)
        walker.current_node = span
        assert walker.next_sibling() is None

    def test_previous_sibling_returns_none_at_first(self):
        doc, body, div, p, t_hello, span, *_ = _make_doc()
        walker = doc.create_tree_walker(div, NodeFilter.SHOW_ELEMENT)
        walker.current_node = p
        assert walker.previous_sibling() is None

    def test_next_sibling_at_root_returns_none(self):
        doc, body, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        # current_node is root
        assert walker.next_sibling() is None


# ---------------------------------------------------------------------------
# TreeWalker: previous_node()
# ---------------------------------------------------------------------------

class TestTreeWalkerPreviousNode:
    def test_previous_node_after_traversal(self):
        """WHATWG DOM §6.3.7: previous_node walks DFS pre-order in reverse.

        After visiting div, p via next_node, previous_node from p yields div
        (the previous node in document order, i.e. p's filtered ancestor).
        From div, previous_node yields body (the root) — per §6.3.7 the root
        IS reachable via previous_node (asymmetric with next_node which never
        returns the root).
        """
        doc, body, div, p, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        assert walker.next_node() is div
        assert walker.next_node() is p
        # Go back: p → div (parent of p, no previous sibling)
        assert walker.previous_node() is div
        # div → body (parent = root; spec allows returning root from previous_node)
        assert walker.previous_node() is body
        # body is root → outer "while node is not root" exits, return None
        assert walker.previous_node() is None

    def test_previous_node_at_root_returns_none(self):
        doc, body, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        assert walker.previous_node() is None


# ---------------------------------------------------------------------------
# TreeWalker: current_node setter
# ---------------------------------------------------------------------------

class TestTreeWalkerCurrentNodeSetter:
    def test_set_current_node_repositions(self):
        doc, body, div, p, t_hello, span, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        walker.current_node = p
        assert walker.current_node is p

    def test_next_node_continues_from_repositioned(self):
        doc, body, div, p, t_hello, span, *_ = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        walker.current_node = p
        # After repositioning to p, next_node should give span
        result = walker.next_node()
        assert result is span


# ---------------------------------------------------------------------------
# AC-6 / AC-7: NodeIterator
# ---------------------------------------------------------------------------

class TestCreateNodeIterator:
    def test_returns_nodeiterator(self):
        doc, body, *_ = _make_doc()
        it = doc.create_node_iterator(body, NodeFilter.SHOW_TEXT)
        assert isinstance(it, NodeIterator)

    def test_reference_node_starts_at_root(self):
        doc, body, *_ = _make_doc()
        it = doc.create_node_iterator(body, NodeFilter.SHOW_TEXT)
        assert it.reference_node is body

    def test_pointer_before_starts_true(self):
        doc, body, *_ = _make_doc()
        it = doc.create_node_iterator(body)
        assert it.pointer_before_reference_node is True


class TestNodeIteratorNextNode:
    def test_show_text_visits_only_text(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        it = doc.create_node_iterator(body, NodeFilter.SHOW_TEXT)
        nodes = []
        node = it.next_node()
        while node is not None:
            nodes.append(node)
            node = it.next_node()
        assert nodes == [t_hello, t_world, t_title]

    def test_show_element_visits_elements_in_order(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        it = doc.create_node_iterator(body, NodeFilter.SHOW_ELEMENT)
        names = []
        node = it.next_node()
        while node is not None:
            names.append(node.node_name)
            node = it.next_node()
        assert names == ["BODY", "DIV", "P", "SPAN", "SECTION", "H1"]

    def test_returns_none_when_exhausted(self):
        doc = Document()
        leaf = doc.create_element("div")
        doc.append_child(leaf)
        it = doc.create_node_iterator(leaf, NodeFilter.SHOW_TEXT)
        assert it.next_node() is None

    def test_reject_treated_as_skip(self):
        """NodeIterator: FILTER_REJECT = FILTER_SKIP (no subtree concept)."""
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()

        def reject_div(node):
            if node.node_name == "DIV":
                return NodeFilter.FILTER_REJECT
            return NodeFilter.FILTER_ACCEPT

        it = doc.create_node_iterator(body, NodeFilter.SHOW_ELEMENT, reject_div)
        names = []
        node = it.next_node()
        while node is not None:
            names.append(node.node_name)
            node = it.next_node()
        # FILTER_REJECT on DIV = skip DIV only; children P and SPAN are still visited
        assert "DIV" not in names
        assert "P" in names
        assert "SPAN" in names


class TestNodeIteratorPreviousNode:
    def test_previous_node_retreats(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        it = doc.create_node_iterator(body, NodeFilter.SHOW_TEXT)
        n1 = it.next_node()
        n2 = it.next_node()
        assert n1 is t_hello
        assert n2 is t_world
        # Retreat
        assert it.previous_node() is t_world
        assert it.previous_node() is t_hello
        assert it.previous_node() is None  # before first text node (at root)

    def test_previous_node_before_any_advance(self):
        doc, body, *_ = _make_doc()
        it = doc.create_node_iterator(body, NodeFilter.SHOW_ELEMENT)
        # pointer_before_reference_node is True, reference is body
        # previous_node should return None (nothing before root)
        assert it.previous_node() is None

    def test_roundtrip_forward_backward(self):
        doc, body, div, p, *_ = _make_doc()
        it = doc.create_node_iterator(body, NodeFilter.SHOW_ELEMENT)
        all_forward = []
        node = it.next_node()
        while node is not None:
            all_forward.append(node)
            node = it.next_node()
        # Now retreat back
        all_backward = []
        node = it.previous_node()
        while node is not None:
            all_backward.append(node)
            node = it.previous_node()
        assert all_backward == list(reversed(all_forward))


# ---------------------------------------------------------------------------
# AC-8: detach() is a no-op
# ---------------------------------------------------------------------------

class TestDetach:
    def test_detach_does_not_raise(self):
        doc, body, *_ = _make_doc()
        it = doc.create_node_iterator(body)
        it.detach()  # must not raise

    def test_detach_returns_none(self):
        doc, body, *_ = _make_doc()
        it = doc.create_node_iterator(body)
        result = it.detach()
        assert result is None

    def test_iterator_still_works_after_detach(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        it = doc.create_node_iterator(body, NodeFilter.SHOW_TEXT)
        it.detach()
        assert it.next_node() is t_hello


# ---------------------------------------------------------------------------
# Extra: what_to_show skips elements without calling filter
# ---------------------------------------------------------------------------

class TestWhatToShowSkipsWithoutFilter:
    def test_show_text_skips_elements_no_filter_call(self):
        doc, body, div, p, t_hello, *_ = _make_doc()
        called_on = []

        def recording_filter(node):
            called_on.append(node)
            return NodeFilter.FILTER_ACCEPT

        walker = doc.create_tree_walker(body, NodeFilter.SHOW_TEXT, recording_filter)
        node = walker.next_node()
        while node is not None:
            node = walker.next_node()
        # Elements have bit 0x1, which is not in SHOW_TEXT (0x4)
        # → filter must never be called on element nodes
        for n in called_on:
            assert n.node_type == NodeType.TEXT_NODE, (
                f"Filter was called on non-text node: {n!r}"
            )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_single_text_child(self):
        doc = Document()
        root = doc.create_element("div")
        t = doc.create_text_node("only")
        root.append_child(t)
        doc.append_child(root)

        it = doc.create_node_iterator(root, NodeFilter.SHOW_TEXT)
        assert it.next_node() is t
        assert it.next_node() is None

    def test_treewalker_single_element_root(self):
        doc = Document()
        leaf = doc.create_element("span")
        doc.append_child(leaf)
        walker = doc.create_tree_walker(leaf, NodeFilter.SHOW_ELEMENT)
        assert walker.next_node() is None

    def test_treewalker_deeply_nested(self):
        """Verify DFS order in a 4-level deep tree."""
        doc = Document()
        root = doc.create_element("div")
        level1 = doc.create_element("ul")
        level2 = doc.create_element("li")
        level3 = doc.create_element("span")
        level2.append_child(level3)
        level1.append_child(level2)
        root.append_child(level1)
        doc.append_child(root)

        walker = doc.create_tree_walker(root, NodeFilter.SHOW_ELEMENT)
        order = []
        node = walker.next_node()
        while node is not None:
            order.append(node.node_name)
            node = walker.next_node()
        assert order == ["UL", "LI", "SPAN"]

    def test_iterator_text_only_children(self):
        """Root with multiple text children — iterator visits them all."""
        doc = Document()
        root = doc.create_element("p")
        t1 = doc.create_text_node("a")
        t2 = doc.create_text_node("b")
        t3 = doc.create_text_node("c")
        root.append_child(t1)
        root.append_child(t2)
        root.append_child(t3)
        doc.append_child(root)

        it = doc.create_node_iterator(root, NodeFilter.SHOW_TEXT)
        assert it.next_node() is t1
        assert it.next_node() is t2
        assert it.next_node() is t3
        assert it.next_node() is None

    def test_custom_filter_callable(self):
        """Custom filter accepting only nodes with specific tag name."""
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()

        def only_p(node):
            if node.node_name == "P":
                return NodeFilter.FILTER_ACCEPT
            return NodeFilter.FILTER_SKIP

        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT, only_p)
        result = walker.next_node()
        assert result is p
        assert walker.next_node() is None

    def test_treewalker_first_and_last_child_consistency(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        first = walker.first_child()
        walker.current_node = body  # reset
        last = walker.last_child()
        assert first is div
        assert last is section

    def test_nodeiterator_no_filter_visits_root(self):
        """NodeIterator next_node() first call includes root if accepted."""
        doc = Document()
        root = doc.create_element("div")
        doc.append_child(root)
        it = doc.create_node_iterator(root, NodeFilter.SHOW_ELEMENT)
        assert it.next_node() is root

    def test_treewalker_show_all_visits_text(self):
        doc, body, div, p, t_hello, span, t_world, section, h1, t_title = _make_doc()
        walker = doc.create_tree_walker(p, NodeFilter.SHOW_ALL)
        node = walker.next_node()
        assert node is t_hello
        assert walker.next_node() is None
