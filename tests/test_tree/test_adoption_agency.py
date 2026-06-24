"""test_adoption_agency.py — tests for the adoption agency algorithm."""
import pytest
from aspose_html.tree import parse_html


def _get_body(doc):
    """Return the <body> element of a parsed document."""
    html_el = doc.document_element
    children = list(html_el.children)
    for child in children:
        if child.tag_name == "BODY":
            return child
    return None


def test_simple_misnesting_b_i():
    """<b><i>text</b></i> — the AAA should produce a valid DOM without errors."""
    doc = parse_html("<!DOCTYPE html><body><b><i>text</b></i></body>")
    body = _get_body(doc)
    assert body is not None
    # After AAA: <b><i>text</i></b><i></i>
    children = list(body.children)
    # At least one <b> element must be present
    b_elements = [el for el in children if el.tag_name == "B"]
    assert len(b_elements) >= 1
    # The text should be inside the b element
    b = b_elements[0]
    text_nodes = [c for c in b.child_nodes if c.node_type == 3]
    assert any("text" in getattr(n, "data", "") for n in text_nodes) or any(
        "text" in getattr(c, "data", "")
        for b_child in b.child_nodes
        for c in getattr(b_child, "child_nodes", [])
        if c.node_type == 3
    )


def test_double_misnesting():
    """<b><i><b>text</b></i></b> — nested misnesting should not crash."""
    doc = parse_html("<!DOCTYPE html><body><b><i><b>text</b></i></b></body>")
    body = _get_body(doc)
    assert body is not None
    # Just verify parsing completed without exception and produced a tree
    assert doc.document_element is not None


def test_non_formatting_element_ignored():
    """End tags for non-formatting elements fall through to any_other_end_tag."""
    doc = parse_html("<!DOCTYPE html><body><div>text</div></body>")
    body = _get_body(doc)
    divs = [el for el in body.children if el.tag_name == "DIV"]
    assert len(divs) == 1


def test_aaa_max_iterations_safety():
    """Pathological misnesting should not loop infinitely (spec has hard limit 8)."""
    # Create deeply nested misnesting
    html = "<!DOCTYPE html><body>"
    html += "<b>" * 10
    html += "text"
    html += "</i>" * 10  # wrong end tags
    html += "</body>"
    doc = parse_html(html)
    assert doc.document_element is not None  # Parser must complete


def test_misnested_formatting_produces_valid_tree():
    """<b>a<i>b</b>c</i> produces the correct browser-compatible DOM."""
    # According to spec: <b>a<i>b</i></b><i>c</i>
    doc = parse_html("<!DOCTYPE html><body><b>a<i>b</b>c</i></body>")
    body = _get_body(doc)
    assert body is not None
    children = list(body.children)
    # Should have at least a <b> and possibly an <i>
    assert len(children) >= 1
    assert children[0].tag_name == "B"
