"""Tests for Node.normalize() — , , .

All six acceptance criteria from  are covered here.
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# AC-1: Adjacent Text siblings are merged left-to-right
# ---------------------------------------------------------------------------


def test_normalize_merges_adjacent_text_nodes() -> None:
    """Three consecutive Text siblings are merged into one (AC-1)."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    t1 = doc.create_text_node("foo")
    t2 = doc.create_text_node("bar")
    t3 = doc.create_text_node("baz")
    parent.append_child(t1)
    parent.append_child(t2)
    parent.append_child(t3)

    parent.normalize()

    assert len(parent.child_nodes) == 1
    assert parent.first_child.data == "foobarbaz"
    # First node absorbs the rest (left-to-right merge).
    assert parent.first_child is t1


def test_normalize_merges_two_adjacent_text_nodes() -> None:
    """Two consecutive Text siblings are merged into one (AC-1)."""
    doc = Document()
    parent = doc.create_element("p")
    doc.append_child(parent)
    t1 = doc.create_text_node("hello ")
    t2 = doc.create_text_node("world")
    parent.append_child(t1)
    parent.append_child(t2)

    parent.normalize()

    assert len(parent.child_nodes) == 1
    assert parent.first_child.data == "hello world"
    assert parent.first_child is t1


def test_normalize_separate_runs_stay_separate() -> None:
    """Two runs of Text separated by an element node stay as two nodes (AC-1)."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    t1 = doc.create_text_node("a")
    t2 = doc.create_text_node("b")
    mid = doc.create_element("span")
    t3 = doc.create_text_node("c")
    t4 = doc.create_text_node("d")
    parent.append_child(t1)
    parent.append_child(t2)
    parent.append_child(mid)
    parent.append_child(t3)
    parent.append_child(t4)

    parent.normalize()

    # t1+t2 merge, t3+t4 merge; mid stays; total 3 children.
    assert len(parent.child_nodes) == 3
    assert parent.child_nodes[0].data == "ab"
    assert parent.child_nodes[1] is mid
    assert parent.child_nodes[2].data == "cd"


# ---------------------------------------------------------------------------
# AC-2: Empty Text nodes are removed
# ---------------------------------------------------------------------------


def test_normalize_removes_single_empty_text_node() -> None:
    """A standalone empty Text node is removed (AC-2)."""
    doc = Document()
    parent = doc.create_element("p")
    doc.append_child(parent)
    empty = doc.create_text_node("")
    parent.append_child(empty)

    parent.normalize()

    assert len(parent.child_nodes) == 0
    assert empty.parent_node is None


def test_normalize_removes_empty_result_after_merge() -> None:
    """If two empty Text nodes merge, the empty surviving node is also removed (AC-2)."""
    doc = Document()
    parent = doc.create_element("p")
    doc.append_child(parent)
    parent.append_child(doc.create_text_node(""))
    parent.append_child(doc.create_text_node(""))

    parent.normalize()

    assert len(parent.child_nodes) == 0


def test_normalize_keeps_non_empty_text_alone() -> None:
    """A single non-empty Text node is not removed (AC-2 boundary)."""
    doc = Document()
    parent = doc.create_element("p")
    doc.append_child(parent)
    t = doc.create_text_node("hello")
    parent.append_child(t)

    parent.normalize()

    assert len(parent.child_nodes) == 1
    assert parent.first_child is t
    assert parent.first_child.data == "hello"


# ---------------------------------------------------------------------------
# AC-3: Normalization recurses into descendant elements
# ---------------------------------------------------------------------------


def test_normalize_recurses_into_children() -> None:
    """normalize() called on ancestor normalizes Text nodes in a grandchild (AC-3)."""
    doc = Document()
    grandparent = doc.create_element("div")
    doc.append_child(grandparent)
    child_el = doc.create_element("span")
    grandparent.append_child(child_el)
    t1 = doc.create_text_node("a")
    t2 = doc.create_text_node("b")
    child_el.append_child(t1)
    child_el.append_child(t2)

    # Called on ancestor, not on child_el directly.
    grandparent.normalize()

    assert len(child_el.child_nodes) == 1
    assert child_el.first_child.data == "ab"


def test_normalize_recurses_deeply() -> None:
    """normalize() recurses through multiple levels of nesting (AC-3)."""
    doc = Document()
    root = doc.create_element("div")
    doc.append_child(root)
    level1 = doc.create_element("section")
    level2 = doc.create_element("p")
    root.append_child(level1)
    level1.append_child(level2)
    level2.append_child(doc.create_text_node("x"))
    level2.append_child(doc.create_text_node("y"))
    level2.append_child(doc.create_text_node("z"))

    root.normalize()

    assert len(level2.child_nodes) == 1
    assert level2.first_child.data == "xyz"


# ---------------------------------------------------------------------------
# AC-4: The operation is idempotent
# ---------------------------------------------------------------------------


def test_normalize_is_idempotent() -> None:
    """Calling normalize() twice produces the same result as calling it once (AC-4)."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    parent.append_child(doc.create_text_node("x"))
    parent.append_child(doc.create_text_node("y"))

    parent.normalize()
    first_child_after_first = parent.first_child
    data_after_first = first_child_after_first.data

    parent.normalize()
    first_child_after_second = parent.first_child

    assert first_child_after_first is first_child_after_second
    assert first_child_after_second.data == "xy"
    assert data_after_first == "xy"
    assert len(parent.child_nodes) == 1


def test_normalize_already_normalized_no_op() -> None:
    """A tree already in normalized form is unchanged by normalize() (AC-4)."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    t = doc.create_text_node("hello")
    span = doc.create_element("span")
    parent.append_child(t)
    parent.append_child(span)

    parent.normalize()

    assert len(parent.child_nodes) == 2
    assert parent.child_nodes[0] is t
    assert parent.child_nodes[1] is span
    assert t.data == "hello"


# ---------------------------------------------------------------------------
# AC-5: Non-Text nodes are not affected
# ---------------------------------------------------------------------------


def test_normalize_does_not_alter_non_text_nodes() -> None:
    """Span and Comment siblings are untouched by normalize() (AC-5)."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    span = doc.create_element("span")
    comment = doc.create_comment("note")
    parent.append_child(span)
    parent.append_child(comment)

    parent.normalize()

    assert len(parent.child_nodes) == 2
    assert parent.child_nodes[0] is span
    assert parent.child_nodes[1] is comment


def test_normalize_interleaved_elements_not_merged() -> None:
    """Text nodes separated by an element node are not merged (AC-5)."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    t1 = doc.create_text_node("first")
    mid = doc.create_element("br")
    t2 = doc.create_text_node("second")
    parent.append_child(t1)
    parent.append_child(mid)
    parent.append_child(t2)

    parent.normalize()

    # Three children remain; no merging across the element node.
    assert len(parent.child_nodes) == 3
    assert parent.child_nodes[0] is t1
    assert parent.child_nodes[0].data == "first"
    assert parent.child_nodes[1] is mid
    assert parent.child_nodes[2] is t2
    assert parent.child_nodes[2].data == "second"


# ---------------------------------------------------------------------------
# AC-6: Parent pointer is cleared on removed nodes
# ---------------------------------------------------------------------------


def test_normalize_clears_parent_on_merged_nodes() -> None:
    """Nodes absorbed during merge have parent_node set to None (AC-2 / remove_child)."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    t1 = doc.create_text_node("a")
    t2 = doc.create_text_node("b")
    t3 = doc.create_text_node("c")
    parent.append_child(t1)
    parent.append_child(t2)
    parent.append_child(t3)

    parent.normalize()

    # t2 and t3 were removed; their parent pointers must be cleared.
    assert t2.parent_node is None
    assert t3.parent_node is None
    # t1 is still in the tree.
    assert t1.parent_node is parent
