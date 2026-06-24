"""test_template.py — tests for <template> element handling."""
import pytest
from aspose_html.tree import parse_html
from aspose_html.dom import DocumentFragment


def test_template_content_is_document_fragment():
    """<template> element has _template_content set to a DocumentFragment."""
    doc = parse_html("<!DOCTYPE html><head><template><p>inside</p></template></head>")
    head = list(doc.document_element.children)[0]
    templates = [el for el in head.children if el.tag_name == "TEMPLATE"]
    assert len(templates) == 1
    tmpl = templates[0]
    content = tmpl._template_content
    assert isinstance(content, DocumentFragment)


def test_nodes_in_template_not_in_body():
    """Nodes inside <template> must not appear in the document body."""
    doc = parse_html(
        "<!DOCTYPE html><head><template><div>inside template</div></template></head>"
        "<body><p>outside</p></body>"
    )
    body = list(doc.document_element.children)[1]
    assert body.tag_name == "BODY"
    # <div> inside template must not be in body
    div_in_body = [el for el in body.children if el.tag_name == "DIV"]
    assert len(div_in_body) == 0

    # But the <div> must be in the template content
    head = list(doc.document_element.children)[0]
    templates = [el for el in head.children if el.tag_name == "TEMPLATE"]
    assert len(templates) == 1
    content = templates[0]._template_content
    assert content is not None
    frag_children = list(content.child_nodes)
    assert len(frag_children) == 1
    assert frag_children[0].tag_name == "DIV"  # type: ignore[union-attr]


def test_template_nested():
    """Nested <template> elements each have their own _template_content."""
    doc = parse_html(
        "<!DOCTYPE html><head>"
        "<template id='outer'>"
        "<template id='inner'><span>deep</span></template>"
        "</template>"
        "</head>"
    )
    head = list(doc.document_element.children)[0]
    templates = [el for el in head.children if el.tag_name == "TEMPLATE"]
    assert len(templates) == 1
    outer = templates[0]
    outer_content = outer._template_content
    assert isinstance(outer_content, DocumentFragment)
    # The inner template should be in outer's content
    inner_templates = [
        n for n in outer_content.child_nodes
        if n.node_type == 1 and n.tag_name == "TEMPLATE"  # type: ignore[union-attr]
    ]
    assert len(inner_templates) == 1


def test_template_content_fragment_ownership():
    """Template content fragment must be owned by the same document."""
    doc = parse_html("<!DOCTYPE html><head><template><p>test</p></template></head>")
    head = list(doc.document_element.children)[0]
    tmpl = list(head.children)[0]
    content = tmpl._template_content
    assert content is not None
    # Children of content should be owned by the document
    for child in content.child_nodes:
        assert child.owner_document is doc
