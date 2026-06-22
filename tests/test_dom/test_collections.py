"""Tests for NodeList, HTMLCollection, NamedNodeMap — liveness and access."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, NodeList, HTMLCollection, NamedNodeMap


@pytest.fixture
def doc() -> Document:
    return Document()


def test_node_list_live_reflects_mutation(doc: Document) -> None:
    """NodeList wraps the live _children list — mutations are visible."""
    el = doc.create_element("div")
    doc.append_child(el)
    nl = doc.child_nodes
    assert len(nl) == 1
    # Add a comment (valid in Document)
    c = doc.create_comment("note")
    doc.append_child(c)
    assert len(nl) == 2  # same NodeList object, now reflects the new child


def test_html_collection_filters_elements_only(doc: Document) -> None:
    parent = doc.create_element("div")
    doc.append_child(parent)
    span = doc.create_element("span")
    txt = doc.create_text_node("text")
    parent.append_child(span)
    parent.append_child(txt)

    coll = parent.children
    assert len(coll) == 1
    assert list(coll)[0] is span


def test_html_collection_live(doc: Document) -> None:
    """children HTMLCollection reflects mutations."""
    parent = doc.create_element("div")
    doc.append_child(parent)
    coll = parent.children
    assert len(coll) == 0
    child = doc.create_element("p")
    parent.append_child(child)
    assert len(coll) == 1  # same object, now reflects new child


def test_named_node_map_string_and_index_access(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("id", "main")
    el.set_attribute("class", "box")

    attrs = el.attributes
    assert attrs["id"].value == "main"  # type: ignore[union-attr]
    assert attrs[0].value == "main"  # type: ignore[union-attr]
    assert attrs[1].value == "box"  # type: ignore[union-attr]
    assert "id" in attrs
    assert "missing" not in attrs


def test_html_collection_len_iter(doc: Document) -> None:
    parent = doc.create_element("ul")
    doc.append_child(parent)
    for i in range(3):
        li = doc.create_element("li")
        parent.append_child(li)

    coll = parent.children
    assert len(coll) == 3
    tags = [n.tag_name for n in coll]  # type: ignore[union-attr]
    assert tags == ["LI", "LI", "LI"]


def test_child_nodes_same_object(doc: Document) -> None:
    """child_nodes returns the same NodeList object on every call."""
    el = doc.create_element("div")
    assert el.child_nodes is el.child_nodes


def test_children_same_object(doc: Document) -> None:
    """children returns the same HTMLCollection object on every call."""
    el = doc.create_element("div")
    assert el.children is el.children
