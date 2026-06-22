"""Tests for CharacterData methods (Text, Comment, CDATASection)."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, IndexSizeError


@pytest.fixture
def doc() -> Document:
    return Document()


def test_text_node_data_length(doc: Document) -> None:
    """AC-11: Text node data and length are correct."""
    t = doc.create_text_node("hello")
    assert t.data == "hello"
    assert t.length == 5


def test_substring_data(doc: Document) -> None:
    t = doc.create_text_node("hello world")
    assert t.substring_data(6, 5) == "world"
    assert t.substring_data(0, 5) == "hello"


def test_substring_data_bad_offset(doc: Document) -> None:
    t = doc.create_text_node("hi")
    with pytest.raises(IndexSizeError):
        t.substring_data(100, 1)


def test_append_data(doc: Document) -> None:
    t = doc.create_text_node("hello")
    t.append_data(" world")
    assert t.data == "hello world"


def test_insert_data(doc: Document) -> None:
    t = doc.create_text_node("helo")
    t.insert_data(3, "l")
    assert t.data == "hello"


def test_delete_data(doc: Document) -> None:
    t = doc.create_text_node("hello world")
    t.delete_data(5, 6)
    assert t.data == "hello"


def test_replace_data(doc: Document) -> None:
    t = doc.create_text_node("hello world")
    t.replace_data(6, 5, "there")
    assert t.data == "hello there"


def test_index_size_error_on_bad_offset(doc: Document) -> None:
    t = doc.create_text_node("hi")
    with pytest.raises(IndexSizeError):
        t.insert_data(100, "x")


def test_comment_data(doc: Document) -> None:
    c = doc.create_comment("a comment")
    assert c.data == "a comment"
    c.append_data("!")
    assert c.data == "a comment!"


def test_cdata_section(doc: Document) -> None:
    from aspose_html.dom import CDATASection
    cds = CDATASection("raw data", owner_document=doc)
    assert cds.data == "raw data"
    assert cds.node_name == "#cdata-section"
    assert cds.node_type == 4


# Text.whole_text (BACK-133)

def test_whole_text_lone_node(doc: Document) -> None:
    """AC-4: lone Text node returns its own data."""
    t = doc.create_text_node("hello")
    assert t.whole_text == "hello"


def test_whole_text_two_adjacent_siblings(doc: Document) -> None:
    """AC-5: two adjacent Text siblings both return full concatenation."""
    parent = doc.create_element("div")
    t1 = doc.create_text_node("foo")
    t2 = doc.create_text_node("bar")
    parent.append_child(t1)
    parent.append_child(t2)
    assert t1.whole_text == "foobar"
    assert t2.whole_text == "foobar"


def test_whole_text_three_adjacent_siblings(doc: Document) -> None:
    """AC-5: three adjacent Text siblings — middle node returns all three."""
    parent = doc.create_element("div")
    t1 = doc.create_text_node("a")
    t2 = doc.create_text_node("b")
    t3 = doc.create_text_node("c")
    parent.append_child(t1)
    parent.append_child(t2)
    parent.append_child(t3)
    assert t2.whole_text == "abc"
    assert t1.whole_text == "abc"
    assert t3.whole_text == "abc"


def test_whole_text_element_sibling_is_boundary(doc: Document) -> None:
    """AC-6: Element sibling terminates the run."""
    parent = doc.create_element("div")
    t1 = doc.create_text_node("left")
    sep = doc.create_element("span")
    t2 = doc.create_text_node("right")
    parent.append_child(t1)
    parent.append_child(sep)
    parent.append_child(t2)
    assert t1.whole_text == "left"
    assert t2.whole_text == "right"


def test_whole_text_cdata_sibling_is_boundary(doc: Document) -> None:
    """AC-6: CDATASection sibling acts as boundary (excluded by type(sib) is Text)."""
    from aspose_html.dom import CDATASection
    parent = doc.create_element("div")
    t1 = doc.create_text_node("before")
    cds = CDATASection("cdata", owner_document=doc)
    t2 = doc.create_text_node("after")
    parent.append_child(t1)
    parent.append_child(cds)
    parent.append_child(t2)
    assert t1.whole_text == "before"
    assert t2.whole_text == "after"


def test_whole_text_orphaned_node(doc: Document) -> None:
    """AC-4: orphaned Text node (no parent) returns its own data."""
    t = doc.create_text_node("solo")
    assert t.whole_text == "solo"
