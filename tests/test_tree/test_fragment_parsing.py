"""test_fragment_parsing.py — tests for parse_fragment()."""
import pytest
from aspose_html.tree import parse_html, parse_fragment
from aspose_html.dom import DocumentFragment, Document


def test_fragment_body_context():
    """Parsing in a body context produces body-level elements."""
    doc = parse_html("<!DOCTYPE html><body></body>")
    body = list(doc.document_element.children)[1]
    frag = parse_fragment("<p>Hello</p><div>World</div>", body)
    assert isinstance(frag, DocumentFragment)
    nodes = list(frag.child_nodes)
    # Both <p> and <div> should be in the fragment
    tags = [n.tag_name for n in nodes if n.node_type == 1]  # type: ignore[union-attr]
    assert "P" in tags
    assert "DIV" in tags


def test_fragment_table_context():
    """Parsing in a table context produces table-level elements."""
    doc = parse_html("<!DOCTYPE html><body><table></table></body>")
    # Find the table element
    body = list(doc.document_element.children)[1]
    table = list(body.children)[0]
    assert table.tag_name == "TABLE"
    frag = parse_fragment("<tr><td>cell</td></tr>", table)
    assert isinstance(frag, DocumentFragment)


def test_fragment_empty_input():
    """Parsing an empty string returns an empty DocumentFragment."""
    doc = parse_html("<!DOCTYPE html><body></body>")
    body = list(doc.document_element.children)[1]
    frag = parse_fragment("", body)
    assert isinstance(frag, DocumentFragment)


def test_fragment_returns_document_fragment_type():
    """parse_fragment() always returns a DocumentFragment."""
    doc = parse_html("<!DOCTYPE html><body></body>")
    body = list(doc.document_element.children)[1]
    frag = parse_fragment("<span>test</span>", body)
    assert isinstance(frag, DocumentFragment)


def test_fragment_no_context_element():
    """parse_fragment() with no context element defaults to body context."""
    frag = parse_fragment("<p>test</p>")
    assert isinstance(frag, DocumentFragment)
    nodes = list(frag.child_nodes)
    tags = [n.tag_name for n in nodes if n.node_type == 1]  # type: ignore[union-attr]
    assert "P" in tags


def test_fragment_raises_on_non_str():
    """parse_fragment() raises TypeError for non-str input."""
    with pytest.raises(TypeError):
        parse_fragment(42)  # type: ignore[arg-type]


def test_fragment_preserves_nesting():
    """Nested HTML in a fragment preserves structure."""
    doc = parse_html("<!DOCTYPE html><body></body>")
    body = list(doc.document_element.children)[1]
    frag = parse_fragment("<ul><li>a</li><li>b</li></ul>", body)
    ul_nodes = [n for n in frag.child_nodes if n.node_type == 1 and n.tag_name == "UL"]  # type: ignore
    assert len(ul_nodes) == 1
    ul = ul_nodes[0]
    li_nodes = list(ul.children)
    assert len(li_nodes) == 2
    assert all(li.tag_name == "LI" for li in li_nodes)
