"""Tests for Element.get_elements_by_tag_name() and get_elements_by_class_name().

Covers acceptance criteria from  / .
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document


@pytest.fixture
def doc() -> Document:
    return Document()


# AC-1: get_elements_by_tag_name returns matching descendants
def test_get_elements_by_tag_name_returns_matching_descendants(doc: Document) -> None:
    """Descendants with the given tag name are returned in tree order."""
    div = doc.create_element("div")
    p1 = doc.create_element("p")
    p2 = doc.create_element("p")
    span = doc.create_element("span")
    doc.append_child(div)
    div.append_child(p1)
    div.append_child(p2)
    p1.append_child(span)

    result = div.get_elements_by_tag_name("p")
    assert len(result) == 2
    assert list(result) == [p1, p2]


def test_get_elements_by_tag_name_no_match_returns_empty(doc: Document) -> None:
    """A tag name with no matching descendants yields an empty collection."""
    div = doc.create_element("div")
    doc.append_child(div)
    div.append_child(doc.create_element("p"))

    result = div.get_elements_by_tag_name("article")
    assert len(result) == 0
    assert list(result) == []


# AC-2: case-insensitive matching and "*" wildcard
def test_get_elements_by_tag_name_case_insensitive_and_wildcard(doc: Document) -> None:
    """Tag-name matching is case-insensitive; '*' returns all descendants."""
    div = doc.create_element("div")
    p = doc.create_element("p")
    span = doc.create_element("span")
    doc.append_child(div)
    div.append_child(p)
    div.append_child(span)

    assert len(div.get_elements_by_tag_name("P")) == 1      # uppercase input
    assert len(div.get_elements_by_tag_name("SPAN")) == 1
    assert len(div.get_elements_by_tag_name("p")) == 1      # lowercase input
    assert len(div.get_elements_by_tag_name("*")) == 2      # wildcard


# AC-3: get_elements_by_class_name requires all tokens
def test_get_elements_by_class_name_all_tokens_required(doc: Document) -> None:
    """Only descendants carrying ALL requested class tokens are returned."""
    div = doc.create_element("div")
    a = doc.create_element("span")
    b = doc.create_element("span")
    a.set_attribute("class", "foo bar")
    b.set_attribute("class", "foo")
    doc.append_child(div)
    div.append_child(a)
    div.append_child(b)

    assert len(div.get_elements_by_class_name("foo")) == 2
    assert len(div.get_elements_by_class_name("foo bar")) == 1
    assert list(div.get_elements_by_class_name("foo bar")) == [a]
    assert len(div.get_elements_by_class_name("baz")) == 0


def test_get_elements_by_class_name_no_class_attribute(doc: Document) -> None:
    """Elements without a class attribute do not match any non-empty token set."""
    div = doc.create_element("div")
    span = doc.create_element("span")  # no class attribute
    doc.append_child(div)
    div.append_child(span)

    assert len(div.get_elements_by_class_name("foo")) == 0


def test_get_elements_by_class_name_empty_string_matches_all(doc: Document) -> None:
    """An empty class_names string matches every descendant element."""
    div = doc.create_element("div")
    p = doc.create_element("p")
    span = doc.create_element("span")
    doc.append_child(div)
    div.append_child(p)
    div.append_child(span)

    # set().issubset(anything) is True — all descendants returned
    result = div.get_elements_by_class_name("")
    assert len(result) == 2


# AC-4: results are in tree order (depth-first pre-order)
def test_get_elements_by_tag_name_tree_order(doc: Document) -> None:
    """Results are yielded in depth-first pre-order."""
    root = doc.create_element("div")
    child1 = doc.create_element("p")
    child2 = doc.create_element("p")
    grandchild = doc.create_element("p")
    doc.append_child(root)
    root.append_child(child1)
    child1.append_child(grandchild)
    root.append_child(child2)

    result = list(root.get_elements_by_tag_name("p"))
    # depth-first pre-order: child1, grandchild, child2
    assert result == [child1, grandchild, child2]


def test_get_elements_by_class_name_tree_order(doc: Document) -> None:
    """Class-name results are yielded in depth-first pre-order."""
    root = doc.create_element("div")
    child1 = doc.create_element("span")
    child2 = doc.create_element("span")
    grandchild = doc.create_element("span")
    child1.set_attribute("class", "note")
    grandchild.set_attribute("class", "note")
    child2.set_attribute("class", "note")
    doc.append_child(root)
    root.append_child(child1)
    child1.append_child(grandchild)
    root.append_child(child2)

    result = list(root.get_elements_by_class_name("note"))
    # depth-first pre-order: child1, grandchild, child2
    assert result == [child1, grandchild, child2]


# AC-5: results are consistent with Document equivalents when scoped to same subtree
def test_element_query_consistent_with_document_query(doc: Document) -> None:
    """Element-scoped queries equal Document-scoped queries for the same subtree."""
    root = doc.create_element("div")
    p = doc.create_element("p")
    p.set_attribute("class", "note")
    doc.append_child(root)
    root.append_child(p)

    assert list(root.get_elements_by_tag_name("p")) == list(
        doc.get_elements_by_tag_name("p")
    )
    assert list(root.get_elements_by_class_name("note")) == list(
        doc.get_elements_by_class_name("note")
    )


def test_element_query_excludes_elements_outside_subtree(doc: Document) -> None:
    """Element-scoped query must not return elements outside its subtree."""
    root = doc.create_element("div")
    inner = doc.create_element("p")
    sibling = doc.create_element("p")  # outside root's subtree
    container = doc.create_element("section")
    doc.append_child(container)
    container.append_child(root)
    container.append_child(sibling)
    root.append_child(inner)

    # root-scoped must only see inner; doc-scoped sees both
    assert list(root.get_elements_by_tag_name("p")) == [inner]
    assert len(doc.get_elements_by_tag_name("p")) == 2


def test_detached_element_query_works() -> None:
    """Subtree queries work on detached elements (no owner_document required)."""
    doc = Document()
    root = doc.create_element("div")   # detached — not appended to doc
    child = doc.create_element("p")
    root.append_child(child)

    result = root.get_elements_by_tag_name("p")
    assert list(result) == [child]
