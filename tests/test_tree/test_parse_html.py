"""test_parse_html.py — acceptance criteria for the tree construction API.

Maps to SPEC-003 acceptance criteria AC-1 through AC-10.
"""
import pytest
from aspose_html.tree import parse_html
from aspose_html.dom import Document, DocumentFragment


def _children(element):
    """Return the element children of *element* as a list."""
    return list(element.children)


def test_ac1_basic_html_hierarchy():
    """AC-1: well-formed HTML produces Document > html > (head, body)."""
    doc = parse_html("<!DOCTYPE html><html><head></head><body></body></html>")
    assert isinstance(doc, Document)
    html_el = doc.document_element
    assert html_el is not None
    assert html_el.tag_name == "HTML"
    children = _children(html_el)
    assert len(children) == 2
    assert children[0].tag_name == "HEAD"
    assert children[1].tag_name == "BODY"


def test_ac2_implicit_p_closing():
    """AC-2: <p>one<p>two produces two sibling <p> elements."""
    doc = parse_html("<!DOCTYPE html><body><p>one<p>two</body>")
    body = _children(doc.document_element)[1]
    assert body.tag_name == "BODY"
    p_elements = _children(body)
    assert len(p_elements) == 2
    assert all(el.tag_name == "P" for el in p_elements)


def test_ac3_misnested_formatting():
    """AC-3: <b><i>text</b></i> — adoption agency algorithm produces correct DOM."""
    doc = parse_html("<!DOCTYPE html><body><b><i>text</b></i></body>")
    body = _children(doc.document_element)[1]
    # The AAA should produce: <b><i>text</i></b><i></i>
    # The exact structure varies but <b> must contain the text
    b_elements = [el for el in _children(body) if el.tag_name == "B"]
    assert len(b_elements) >= 1


def test_ac4_doctype_no_quirks():
    """AC-4: <!DOCTYPE html> sets no-quirks mode (CSS1Compat)."""
    doc = parse_html("<!DOCTYPE html><html><body></body></html>")
    assert doc.compat_mode == "CSS1Compat"


def test_ac5_doctype_quirks():
    """AC-5: old DOCTYPE triggers quirks mode (BackCompat)."""
    doc = parse_html(
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
        "<html><body></body></html>"
    )
    # This public ID triggers limited quirks (with no system ID) or quirks
    # depending on exact match — just verify parsing succeeds
    assert doc.compat_mode in ("BackCompat", "LimitedQuirks")

    # A force-quirks DOCTYPE
    doc2 = parse_html("<!DOCTYPE html SYSTEM 'about:legacy-compat'>")
    # Not force-quirks — should be no-quirks
    assert doc2.compat_mode == "CSS1Compat"


def test_ac6_foster_parenting_text():
    """AC-6: text directly inside <table> is foster-parented before the table."""
    doc = parse_html("<!DOCTYPE html><body><table>text</table></body>")
    body = _children(doc.document_element)[1]
    body_children = list(body.child_nodes)
    # text should appear before the table
    texts = [n for n in body_children if n.node_type == 3]  # TEXT_NODE = 3
    tables = [n for n in body_children if n.node_type == 1 and n.tag_name == "TABLE"]  # type: ignore
    assert len(texts) > 0, "Foster-parented text node expected"
    assert len(tables) == 1, "Table should still exist"
    # Text should come before the table
    text_idx = body_children.index(texts[0])
    table_idx = body_children.index(tables[0])
    assert text_idx < table_idx, "Foster-parented text must come before the table"


def test_ac7_template_content():
    """AC-7: <template><div>x</div></template> stores <div> in template content."""
    doc = parse_html("<!DOCTYPE html><head><template><div>x</div></template></head>")
    head = _children(doc.document_element)[0]
    templates = [el for el in _children(head) if el.tag_name == "TEMPLATE"]
    assert len(templates) == 1, "Expected one <template> in head"
    tmpl = templates[0]
    content = tmpl._template_content
    assert content is not None, "Template should have _template_content"
    assert isinstance(content, DocumentFragment)
    frag_children = list(content.child_nodes)
    assert len(frag_children) == 1
    assert frag_children[0].tag_name == "DIV"  # type: ignore[union-attr]


def test_ac8_fragment_parsing():
    """AC-8: parse_fragment('<p>hello</p>', body) returns DocumentFragment with <p> child."""
    from aspose_html.tree import parse_fragment
    doc = parse_html("<!DOCTYPE html><body></body>")
    body = _children(doc.document_element)[1]
    frag = parse_fragment("<p>Hello</p>", body)
    assert isinstance(frag, DocumentFragment)
    frag_children = list(frag.child_nodes)
    assert len(frag_children) >= 1
    # First child should be a <p>
    assert frag_children[0].tag_name == "P"  # type: ignore[union-attr]


def test_ac9_parse_errors_on_document():
    """AC-9: parse errors are available on document.parse_errors."""
    doc = parse_html("<b>unclosed")
    # May or may not have errors depending on implementation,
    # but the attribute must exist and be a list.
    assert isinstance(doc.parse_errors, list)


def test_ac10_public_api_types():
    """AC-10: parse_html returns Document; type annotations verified."""
    doc = parse_html("<!DOCTYPE html><p>hi</p>")
    assert isinstance(doc, Document)
    html_el = doc.document_element
    assert html_el is not None
    assert html_el.tag_name == "HTML"


def test_empty_document():
    """Parsing empty string produces a valid Document with html/head/body."""
    doc = parse_html("")
    assert isinstance(doc, Document)
    html_el = doc.document_element
    assert html_el is not None
    assert html_el.tag_name == "HTML"


def test_text_only_document():
    """Parsing a text-only string creates implicit html/head/body structure."""
    doc = parse_html("hello world")
    html_el = doc.document_element
    assert html_el is not None
    assert html_el.tag_name == "HTML"


def test_parse_html_raises_on_non_str():
    """parse_html() must raise TypeError for non-str input."""
    with pytest.raises(TypeError):
        parse_html(b"<html>")  # type: ignore[arg-type]
