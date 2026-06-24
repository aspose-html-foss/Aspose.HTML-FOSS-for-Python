"""Tests for Node.contains() and Node.is_equal_node() —  / ."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, DocumentFragment


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def doc() -> Document:
    return Document()


# ===========================================================================
# Node.contains()
# ===========================================================================

def test_contains_self(doc: Document) -> None:
    """A node contains itself."""
    el = doc.create_element("div")
    assert el.contains(el) is True


def test_contains_direct_child(doc: Document) -> None:
    """A parent contains its direct child."""
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)
    assert parent.contains(child) is True


def test_contains_deep_descendant(doc: Document) -> None:
    """A node contains a deeply nested descendant."""
    parent = doc.create_element("div")
    child = doc.create_element("p")
    grandchild = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)
    child.append_child(grandchild)
    assert parent.contains(grandchild) is True


def test_contains_none_returns_false(doc: Document) -> None:
    """contains(None) always returns False."""
    el = doc.create_element("div")
    assert el.contains(None) is False


def test_contains_non_descendant_returns_false(doc: Document) -> None:
    """A node does not contain a sibling or unrelated node."""
    parent = doc.create_element("div")
    child1 = doc.create_element("span")
    child2 = doc.create_element("p")
    doc.append_child(parent)
    parent.append_child(child1)
    parent.append_child(child2)
    assert child1.contains(child2) is False


def test_contains_ancestor_returns_false(doc: Document) -> None:
    """A child does not contain its parent."""
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)
    assert child.contains(parent) is False


def test_contains_text_child(doc: Document) -> None:
    """contains() works for Text node children."""
    el = doc.create_element("p")
    doc.append_child(el)
    text = doc.create_text_node("hello")
    el.append_child(text)
    assert el.contains(text) is True


# ===========================================================================
# Node.is_equal_node()
# ===========================================================================

def test_is_equal_node_none_returns_false(doc: Document) -> None:
    """is_equal_node(None) always returns False."""
    el = doc.create_element("div")
    assert el.is_equal_node(None) is False


def test_is_equal_node_same_tag(doc: Document) -> None:
    """Two elements with the same tag name are equal."""
    a = doc.create_element("p")
    b = doc.create_element("p")
    assert a.is_equal_node(b) is True


def test_is_equal_node_different_tag(doc: Document) -> None:
    """Elements with different tag names are not equal."""
    a = doc.create_element("div")
    b = doc.create_element("span")
    assert a.is_equal_node(b) is False


def test_is_equal_node_same_attributes(doc: Document) -> None:
    """Elements with the same attributes are equal."""
    a = doc.create_element("div")
    b = doc.create_element("div")
    a.set_attribute("id", "x")
    b.set_attribute("id", "x")
    assert a.is_equal_node(b) is True


def test_is_equal_node_different_attributes(doc: Document) -> None:
    """Elements with different attributes are not equal."""
    a = doc.create_element("div")
    b = doc.create_element("div")
    a.set_attribute("id", "x")
    b.set_attribute("id", "y")
    assert a.is_equal_node(b) is False


def test_is_equal_node_attribute_count_differs(doc: Document) -> None:
    """Elements with different attribute counts are not equal."""
    a = doc.create_element("div")
    b = doc.create_element("div")
    a.set_attribute("id", "x")
    assert a.is_equal_node(b) is False


def test_is_equal_node_text_nodes(doc: Document) -> None:
    """Two Text nodes with the same data are equal."""
    a = doc.create_text_node("hello")
    b = doc.create_text_node("hello")
    assert a.is_equal_node(b) is True


def test_is_equal_node_text_nodes_different(doc: Document) -> None:
    """Two Text nodes with different data are not equal."""
    a = doc.create_text_node("hello")
    b = doc.create_text_node("world")
    assert a.is_equal_node(b) is False


def test_is_equal_node_recursive_children(doc: Document) -> None:
    """Two elements with identical subtrees are equal."""
    a = doc.create_element("div")
    b = doc.create_element("div")
    a.append_child(doc.create_element("span"))
    b.append_child(doc.create_element("span"))
    assert a.is_equal_node(b) is True


def test_is_equal_node_different_child_count(doc: Document) -> None:
    """Elements with different child counts are not equal."""
    a = doc.create_element("div")
    b = doc.create_element("div")
    a.append_child(doc.create_element("span"))
    assert a.is_equal_node(b) is False


def test_is_equal_node_self(doc: Document) -> None:
    """A node is equal to itself."""
    el = doc.create_element("div")
    el.set_attribute("class", "foo")
    el.append_child(doc.create_element("p"))
    assert el.is_equal_node(el) is True
