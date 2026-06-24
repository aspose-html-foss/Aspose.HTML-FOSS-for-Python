"""Tests for ParentNode mixin —  / ."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, DocumentFragment


@pytest.fixture()
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# Element.prepend()
# ---------------------------------------------------------------------------

def test_element_prepend_single_element(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    b = doc.create_element("b")
    parent.prepend(b)
    assert parent.child_nodes[0] is b
    assert parent.child_nodes[1] is a


def test_element_prepend_string_becomes_text(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    parent.prepend("hello")
    assert parent.first_child.data == "hello"  # type: ignore[union-attr]


def test_element_prepend_multiple_nodes_in_order(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    x = doc.create_element("x")
    y = doc.create_element("y")
    parent.prepend(x, "t", y)
    assert parent.child_nodes[0] is x
    assert parent.child_nodes[1].data == "t"  # type: ignore[union-attr]
    assert parent.child_nodes[2] is y
    assert parent.child_nodes[3] is a


def test_element_prepend_noop_when_empty_args(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    parent.prepend()
    assert len(parent.child_nodes) == 1


def test_element_prepend_on_empty_parent(doc: Document) -> None:
    parent = doc.create_element("div")
    doc.append_child(parent)
    a = doc.create_element("a")
    parent.prepend(a)
    assert parent.first_child is a


# ---------------------------------------------------------------------------
# Element.append()
# ---------------------------------------------------------------------------

def test_element_append_single_element(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    b = doc.create_element("b")
    parent.append(b)
    assert parent.child_nodes[0] is a
    assert parent.child_nodes[1] is b


def test_element_append_string_becomes_text(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    parent.append("tail")
    assert parent.last_child.data == "tail"  # type: ignore[union-attr]


def test_element_append_multiple_nodes_in_order(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    x = doc.create_element("x")
    y = doc.create_element("y")
    parent.append(x, "t", y)
    assert parent.child_nodes[0] is a
    assert parent.child_nodes[1] is x
    assert parent.child_nodes[2].data == "t"  # type: ignore[union-attr]
    assert parent.child_nodes[3] is y


def test_element_append_noop_when_empty_args(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    parent.append()
    assert len(parent.child_nodes) == 1


def test_element_append_does_not_shadow_append_child(doc: Document) -> None:
    parent = doc.create_element("div")
    doc.append_child(parent)
    a = doc.create_element("a")
    result = parent.append_child(a)
    assert result is a
    parent.append("text")
    assert len(parent.child_nodes) == 2


# ---------------------------------------------------------------------------
# Element.replace_children()
# ---------------------------------------------------------------------------

def test_element_replace_children_replaces_all(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    doc.append_child(parent)
    parent.append_child(a)
    parent.append_child(b)
    c = doc.create_element("c")
    parent.replace_children(c)
    assert len(parent.child_nodes) == 1
    assert parent.first_child is c
    assert a.parent_node is None
    assert b.parent_node is None


def test_element_replace_children_no_args_clears(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    doc.append_child(parent)
    parent.append_child(a)
    parent.append_child(b)
    parent.replace_children()
    assert len(parent.child_nodes) == 0


def test_element_replace_children_with_string(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    doc.append_child(parent)
    parent.append_child(a)
    parent.replace_children("new")
    assert parent.first_child.data == "new"  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Document ParentNode methods
# ---------------------------------------------------------------------------

def test_document_append_appends_last(doc: Document) -> None:
    el = doc.create_element("html")
    doc.append(el)
    assert doc.last_child is el


def test_document_prepend_inserts_before_first_child(doc: Document) -> None:
    # Use Comment nodes — always valid as direct Document children.
    first = doc.create_comment("first")
    doc.append_child(first)
    newcomer = doc.create_comment("newcomer")
    doc.prepend(newcomer)
    assert doc.first_child is newcomer
    assert doc.child_nodes[1] is first


def test_document_replace_children_clears(doc: Document) -> None:
    el = doc.create_element("html")
    doc.append_child(el)
    doc.replace_children()
    assert len(doc.child_nodes) == 0


# ---------------------------------------------------------------------------
# DocumentFragment ParentNode methods
# ---------------------------------------------------------------------------

def test_fragment_prepend_inserts_before_first_child(doc: Document) -> None:
    frag = doc.create_document_fragment()
    a = doc.create_element("a")
    frag.append_child(a)
    b = doc.create_element("b")
    frag.prepend(b)
    assert frag.first_child is b


def test_fragment_append_appends_last(doc: Document) -> None:
    frag = doc.create_document_fragment()
    a = doc.create_element("a")
    frag.append(a)
    assert frag.last_child is a


def test_fragment_replace_children_clears_and_appends(doc: Document) -> None:
    frag = doc.create_document_fragment()
    a = doc.create_element("a")
    b = doc.create_element("b")
    frag.append_child(a)
    frag.append_child(b)
    c = doc.create_element("c")
    frag.replace_children(c)
    assert len(frag.child_nodes) == 1
    assert frag.first_child is c


def test_fragment_append_with_string(doc: Document) -> None:
    frag = doc.create_document_fragment()
    frag.append("text")
    assert frag.first_child.data == "text"  # type: ignore[union-attr]


def test_fragment_replace_children_no_args_clears(doc: Document) -> None:
    frag = doc.create_document_fragment()
    a = doc.create_element("a")
    frag.append_child(a)
    frag.replace_children()
    assert len(frag.child_nodes) == 0
