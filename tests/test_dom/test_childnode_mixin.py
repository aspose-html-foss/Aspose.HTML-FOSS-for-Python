"""Tests for ChildNode mixin —  / ."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document


@pytest.fixture()
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# Element.remove()
# ---------------------------------------------------------------------------

def test_element_remove_detaches_from_parent(doc: Document) -> None:
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)
    child.remove()
    assert child.parent_node is None
    assert len(parent.child_nodes) == 0


def test_element_remove_noop_when_detached(doc: Document) -> None:
    child = doc.create_element("span")
    child.remove()  # should not raise
    assert child.parent_node is None


def test_element_remove_middle_child(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    c = doc.create_element("c")
    doc.append_child(parent)
    parent.append_child(a)
    parent.append_child(b)
    parent.append_child(c)
    b.remove()
    assert len(parent.child_nodes) == 2
    assert parent.child_nodes[0] is a
    assert parent.child_nodes[1] is c


# ---------------------------------------------------------------------------
# Element.before()
# ---------------------------------------------------------------------------

def test_element_before_inserts_element_before_self(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    doc.append_child(parent)
    parent.append_child(a)
    parent.append_child(b)
    x = doc.create_element("x")
    b.before(x)
    assert parent.child_nodes[0] is a
    assert parent.child_nodes[1] is x
    assert parent.child_nodes[2] is b


def test_element_before_inserts_string_as_text_node(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    el.before("hello")
    assert parent.first_child.data == "hello"  # type: ignore[union-attr]


def test_element_before_multiple_nodes(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    x = doc.create_element("x")
    y = doc.create_element("y")
    el.before(x, "t", y)
    assert parent.child_nodes[0] is x
    assert parent.child_nodes[1].data == "t"  # type: ignore[union-attr]
    assert parent.child_nodes[2] is y
    assert parent.child_nodes[3] is el


def test_element_before_noop_when_no_parent(doc: Document) -> None:
    el = doc.create_element("span")
    x = doc.create_element("x")
    el.before(x)
    assert x.parent_node is None


def test_element_before_noop_when_empty_args(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    el.before()
    assert len(parent.child_nodes) == 1


# ---------------------------------------------------------------------------
# Element.after()
# ---------------------------------------------------------------------------

def test_element_after_inserts_element_after_self(doc: Document) -> None:
    parent = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    doc.append_child(parent)
    parent.append_child(a)
    parent.append_child(b)
    x = doc.create_element("x")
    a.after(x)
    assert parent.child_nodes[0] is a
    assert parent.child_nodes[1] is x
    assert parent.child_nodes[2] is b


def test_element_after_inserts_string_as_text_node(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    el.after("tail")
    assert parent.last_child.data == "tail"  # type: ignore[union-attr]


def test_element_after_multiple_nodes_in_order(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    x = doc.create_element("x")
    y = doc.create_element("y")
    el.after(x, "t", y)
    assert parent.child_nodes[0] is el
    assert parent.child_nodes[1] is x
    assert parent.child_nodes[2].data == "t"  # type: ignore[union-attr]
    assert parent.child_nodes[3] is y


def test_element_after_when_self_is_last_child(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    x = doc.create_element("x")
    el.after(x)
    assert parent.child_nodes[0] is el
    assert parent.child_nodes[1] is x


def test_element_after_noop_when_no_parent(doc: Document) -> None:
    el = doc.create_element("span")
    x = doc.create_element("x")
    el.after(x)
    assert x.parent_node is None


# ---------------------------------------------------------------------------
# Element.replace_with()
# ---------------------------------------------------------------------------

def test_element_replace_with_replaces_with_element(doc: Document) -> None:
    parent = doc.create_element("div")
    old = doc.create_element("span")
    sibling = doc.create_element("p")
    doc.append_child(parent)
    parent.append_child(old)
    parent.append_child(sibling)
    new = doc.create_element("b")
    old.replace_with(new)
    assert parent.child_nodes[0] is new
    assert parent.child_nodes[1] is sibling
    assert old.parent_node is None


def test_element_replace_with_replaces_with_text(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    el.replace_with("text")
    assert parent.first_child.data == "text"  # type: ignore[union-attr]
    assert el.parent_node is None


def test_element_replace_with_multiple_nodes(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    a = doc.create_element("a")
    b = doc.create_element("b")
    el.replace_with(a, "t", b)
    assert parent.child_nodes[0] is a
    assert parent.child_nodes[1].data == "t"  # type: ignore[union-attr]
    assert parent.child_nodes[2] is b
    assert el.parent_node is None


def test_element_replace_with_noop_when_no_parent(doc: Document) -> None:
    el = doc.create_element("span")
    x = doc.create_element("x")
    el.replace_with(x)  # no exception


def test_element_replace_with_no_args_removes_self(doc: Document) -> None:
    parent = doc.create_element("div")
    el = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(el)
    el.replace_with()
    assert len(parent.child_nodes) == 0
    assert el.parent_node is None


# ---------------------------------------------------------------------------
# CharacterData.remove()
# ---------------------------------------------------------------------------

def test_character_data_remove_detaches_text_node(doc: Document) -> None:
    parent = doc.create_element("div")
    text = doc.create_text_node("hello")
    doc.append_child(parent)
    parent.append_child(text)
    text.remove()
    assert text.parent_node is None
    assert len(parent.child_nodes) == 0


def test_character_data_remove_noop_when_detached(doc: Document) -> None:
    text = doc.create_text_node("x")
    text.remove()  # no exception
    assert text.parent_node is None


def test_character_data_remove_works_on_comment(doc: Document) -> None:
    parent = doc.create_element("div")
    comment = doc.create_comment("note")
    doc.append_child(parent)
    parent.append_child(comment)
    comment.remove()
    assert len(parent.child_nodes) == 0
