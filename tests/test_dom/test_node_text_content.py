"""Tests for Node.text_content getter and setter (, , )."""
from __future__ import annotations

from aspose_html.dom import Document
from aspose_html.dom._character_data import Text


# ---------------------------------------------------------------------------
# AC-1 / AC-2: Element getter
# ---------------------------------------------------------------------------


def test_element_getter_empty_when_no_text_nodes() -> None:
    """Element with no children returns '' (AC-2)."""
    doc = Document()
    el = doc.create_element("div")
    assert el.text_content == ""


def test_element_getter_concatenates_text_nodes() -> None:
    """Element with mixed Text+Element children returns concatenated text only (AC-1)."""
    doc = Document()
    div = doc.create_element("div")
    doc.append_child(div)
    span = doc.create_element("span")
    div.append_child(span)
    span.append_child(doc.create_text_node("hello"))
    div.append_child(doc.create_text_node(" world"))
    assert div.text_content == "hello world"


def test_element_getter_dfs_nested_structure() -> None:
    """Deeply nested structure: <div><p>a</p><p>b</p></div> → 'ab' (FR-2)."""
    doc = Document()
    div = doc.create_element("div")
    doc.append_child(div)
    p1 = doc.create_element("p")
    p2 = doc.create_element("p")
    div.append_child(p1)
    div.append_child(p2)
    p1.append_child(doc.create_text_node("a"))
    p2.append_child(doc.create_text_node("b"))
    assert div.text_content == "ab"


def test_element_getter_excludes_comment_nodes() -> None:
    """Comment children are not included in text_content (AC-6)."""
    doc = Document()
    el = doc.create_element("p")
    doc.append_child(el)
    el.append_child(doc.create_comment("this is a comment"))
    assert el.text_content == ""


# ---------------------------------------------------------------------------
# AC-3 / AC-4 / AC-5: Element setter
# ---------------------------------------------------------------------------


def test_element_setter_replaces_children_with_text() -> None:
    """element.text_content = 'hello' results in exactly one Text child (AC-3)."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    child = doc.create_element("span")
    el.append_child(child)
    el.text_content = "hello"
    assert len(el._children) == 1
    text_node = el._children[0]
    assert isinstance(text_node, Text)
    assert text_node.data == "hello"


def test_element_setter_empty_removes_all_children() -> None:
    """element.text_content = '' removes all children, adds no Text node (AC-4)."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    el.append_child(doc.create_text_node("some text"))
    el.text_content = ""
    assert len(el._children) == 0


def test_element_setter_roundtrip() -> None:
    """After set, getter returns the same string (AC-5)."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    el.text_content = "roundtrip"
    assert el.text_content == "roundtrip"


def test_element_setter_with_none_value() -> None:
    """element.text_content = None removes all children, adds no Text node (FR-3)."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    el.append_child(doc.create_text_node("data"))
    el.append_child(doc.create_element("span"))
    el.text_content = None
    assert len(el._children) == 0


# ---------------------------------------------------------------------------
# AC-7 / AC-8: Text node (CharacterData)
# ---------------------------------------------------------------------------


def test_text_node_getter_equals_data() -> None:
    """text_node.text_content == text_node.data (AC-7)."""
    doc = Document()
    t = doc.create_text_node("hello")
    assert t.text_content == t.data
    assert t.text_content == "hello"


def test_text_node_setter_sets_data() -> None:
    """text_node.text_content = 'x' sets data to 'x' (AC-8)."""
    doc = Document()
    t = doc.create_text_node("old")
    t.text_content = "x"
    assert t.data == "x"


def test_comment_text_content_returns_data() -> None:
    """comment.text_content == comment.data (FR-5)."""
    doc = Document()
    c = doc.create_comment("my comment")
    assert c.text_content == c.data
    assert c.text_content == "my comment"


# ---------------------------------------------------------------------------
# AC-9: Document returns None
# ---------------------------------------------------------------------------


def test_document_returns_none() -> None:
    """doc.text_content is None (AC-9)."""
    doc = Document()
    assert doc.text_content is None


# ---------------------------------------------------------------------------
# AC-11: DocumentFragment follows Element rules
# ---------------------------------------------------------------------------


def test_document_fragment_getter_concatenates_text() -> None:
    """DocumentFragment getter returns concatenated text of descendant Text nodes (AC-11)."""
    doc = Document()
    frag = doc.create_document_fragment()
    frag.append_child(doc.create_text_node("foo"))
    frag.append_child(doc.create_text_node("bar"))
    assert frag.text_content == "foobar"


def test_document_fragment_setter_replaces_children() -> None:
    """DocumentFragment setter removes all children and inserts one Text node (AC-11)."""
    doc = Document()
    frag = doc.create_document_fragment()
    frag.append_child(doc.create_text_node("old"))
    frag.text_content = "new"
    assert len(frag._children) == 1
    assert isinstance(frag._children[0], Text)
    assert frag._children[0].data == "new"


def test_document_fragment_text_content_roundtrip() -> None:
    """Set then read text_content on a DocumentFragment works correctly."""
    doc = Document()
    frag = doc.create_document_fragment()
    frag.text_content = "fragment text"
    assert frag.text_content == "fragment text"


# ---------------------------------------------------------------------------
# Additional: detached element (no owner document)
# ---------------------------------------------------------------------------


def test_element_setter_detached_no_owner_document() -> None:
    """Setter works on a detached element (no owner document) via direct Text()."""
    # : if _owner_document is None, create Text() directly
    doc = Document()
    el = doc.create_element("div")
    el._owner_document = None  # simulate detached
    el.text_content = "detached"
    assert el.text_content == "detached"
    assert isinstance(el._children[0], Text)
