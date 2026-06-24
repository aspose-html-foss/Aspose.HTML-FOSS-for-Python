"""Tests for clone_node — shallow and deep cloning."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document


@pytest.fixture
def doc() -> Document:
    return Document()


def test_clone_deep_true(doc: Document) -> None:
    """AC-7: deep clone copies the entire subtree."""
    parent = doc.create_element("div")
    child = doc.create_element("span")
    grandchild = doc.create_text_node("hello")
    doc.append_child(parent)
    parent.append_child(child)
    child.append_child(grandchild)

    clone = parent.clone_node(deep=True)

    assert clone is not parent
    assert clone.parent_node is None
    assert len(clone._children) == 1
    cloned_child = clone._children[0]
    assert cloned_child is not child
    assert cloned_child.tag_name == "SPAN"  # type: ignore[union-attr]
    assert len(cloned_child._children) == 1
    assert cloned_child._children[0].data == "hello"  # type: ignore[union-attr]


def test_clone_deep_false(doc: Document) -> None:
    """AC-8: shallow clone does not copy children."""
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)

    clone = parent.clone_node(deep=False)

    assert clone is not parent
    assert clone.parent_node is None
    assert len(clone._children) == 0


def test_clone_has_no_parent(doc: Document) -> None:
    """Cloned node has no parent regardless of original's position."""
    el = doc.create_element("div")
    doc.append_child(el)
    assert el.parent_node is doc

    clone = el.clone_node()
    assert clone.parent_node is None


def test_clone_attributes_independent(doc: Document) -> None:
    """Cloned element's attributes are independent of the original's."""
    el = doc.create_element("div")
    el.set_attribute("id", "original")
    doc.append_child(el)

    clone = el.clone_node(deep=False)
    clone.set_attribute("id", "clone")  # type: ignore[union-attr]

    # Original should not have changed.
    assert el.get_attribute("id") == "original"
    assert clone.get_attribute("id") == "clone"  # type: ignore[union-attr]


def test_clone_text_node(doc: Document) -> None:
    t = doc.create_text_node("hello")
    clone = t.clone_node()
    assert clone is not t
    assert clone.data == "hello"  # type: ignore[union-attr]
    assert clone.parent_node is None
