"""Tests for Text.split_text() and Document.create_processing_instruction().

Covers  acceptance criteria (AC-1 through AC-10) and 
test cases (1 through 15).
"""
import pytest

from aspose_html.dom import Document
from aspose_html.dom._exceptions import IndexSizeError, InvalidCharacterError


# ---------------------------------------------------------------------------
# Text.split_text
# ---------------------------------------------------------------------------


def test_split_text_basic():
    """AC-1: split at middle — correct data on both sides."""
    doc = Document()
    t = doc.create_text_node("hello")
    new_t = t.split_text(3)
    assert t.data == "hel"
    assert new_t.data == "lo"


def test_split_text_at_zero():
    """AC-4: split at 0 moves all data to the new node."""
    doc = Document()
    t = doc.create_text_node("hello")
    new_t = t.split_text(0)
    assert t.data == ""
    assert new_t.data == "hello"


def test_split_text_at_end():
    """AC-5: split at length returns an empty new node."""
    doc = Document()
    t = doc.create_text_node("hello")
    new_t = t.split_text(5)
    assert t.data == "hello"
    assert new_t.data == ""


def test_split_text_inserts_after_in_parent():
    """AC-2: after split, new node is next sibling of original when attached."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    t = doc.create_text_node("hello")
    parent.append_child(t)
    new_t = t.split_text(3)
    # new_t must be directly after t
    assert t.next_sibling is new_t
    assert new_t.previous_sibling is t
    assert new_t.parent_node is parent


def test_split_text_detached_no_insert():
    """AC-3: detached node — new node has no parent."""
    doc = Document()
    t = doc.create_text_node("hello")
    # t is not appended to any parent
    new_t = t.split_text(3)
    assert new_t.parent_node is None
    # original also has no parent
    assert t.parent_node is None


def test_split_text_raises_index_size_error():
    """AC-5 / AC-6: offset > length raises IndexSizeError."""
    doc = Document()
    t = doc.create_text_node("hello")
    with pytest.raises(IndexSizeError):
        t.split_text(6)


def test_split_text_owner_document_preserved():
    """owner_document of new node matches original."""
    doc = Document()
    t = doc.create_text_node("hello")
    new_t = t.split_text(3)
    assert new_t.owner_document is doc


def test_split_text_sibling_order_in_parent():
    """Verify parent child list contains both nodes in correct order."""
    doc = Document()
    parent = doc.create_element("p")
    doc.append_child(parent)
    t = doc.create_text_node("abcde")
    parent.append_child(t)
    new_t = t.split_text(2)
    children = list(parent.child_nodes)
    assert children[0] is t
    assert children[1] is new_t
    assert t.data == "ab"
    assert new_t.data == "cde"


def test_split_text_existing_next_sibling_pushed_right():
    """After split, the pre-existing next sibling moves to the right."""
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    t = doc.create_text_node("hello")
    comment = doc.create_comment("end")
    parent.append_child(t)
    parent.append_child(comment)
    new_t = t.split_text(3)
    children = list(parent.child_nodes)
    assert children[0] is t
    assert children[1] is new_t
    assert children[2] is comment


# ---------------------------------------------------------------------------
# Document.create_processing_instruction
# ---------------------------------------------------------------------------


def test_create_pi_basic():
    """AC-6: valid target and data — PI node returned."""
    doc = Document()
    pi = doc.create_processing_instruction("xml-stylesheet", 'href="a.css"')
    assert pi is not None


def test_create_pi_target_and_data_preserved():
    """target and data are set correctly on the returned node."""
    doc = Document()
    pi = doc.create_processing_instruction("xml-stylesheet", 'href="a.css"')
    assert pi.target == "xml-stylesheet"
    assert pi.data == 'href="a.css"'


def test_create_pi_owner_document():
    """AC-9: owner_document of created PI is the creating document."""
    doc = Document()
    pi = doc.create_processing_instruction("xml-stylesheet", "")
    assert pi.owner_document is doc


def test_create_pi_detached_by_default():
    """Created PI node has no parent."""
    doc = Document()
    pi = doc.create_processing_instruction("xml-stylesheet", "")
    assert pi.parent_node is None


def test_create_pi_invalid_target():
    """AC-7: colon in target raises InvalidCharacterError."""
    doc = Document()
    with pytest.raises(InvalidCharacterError):
        doc.create_processing_instruction("bad:target", "")


def test_create_pi_data_contains_close():
    """AC-8: '?>' in data raises InvalidCharacterError."""
    doc = Document()
    with pytest.raises(InvalidCharacterError):
        doc.create_processing_instruction("pi", "bad?> end")


def test_create_pi_can_be_appended_to_document():
    """PI can be appended to the Document (document allows PI children)."""
    doc = Document()
    pi = doc.create_processing_instruction("xml-stylesheet", "")
    doc.append_child(pi)
    assert pi.parent_node is doc


def test_create_pi_empty_data():
    """PI can be created with empty data string."""
    doc = Document()
    pi = doc.create_processing_instruction("php", "")
    assert pi.target == "php"
    assert pi.data == ""


def test_create_pi_hyphen_in_target():
    """Hyphens in target do not contain ':' — should succeed."""
    doc = Document()
    pi = doc.create_processing_instruction("xml-stylesheet", "")
    assert pi.target == "xml-stylesheet"
