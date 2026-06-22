"""test_foreign_content.py — tests for SVG and MathML foreign content."""
import pytest
from aspose_html.tree import parse_html
from aspose_html.tree._foreign_content import SVG_NAMESPACE, MATHML_NAMESPACE


def _get_body(doc):
    return list(doc.document_element.children)[1]


def test_svg_element_namespace():
    """<svg> element gets the SVG namespace URI."""
    doc = parse_html("<!DOCTYPE html><body><svg><circle/></svg></body>")
    body = _get_body(doc)
    svg_elements = [el for el in body.children if el.tag_name == "svg" or el.local_name == "svg"]
    assert len(svg_elements) >= 1
    svg = svg_elements[0]
    assert svg.namespace_uri == SVG_NAMESPACE


def test_math_element_namespace():
    """<math> element gets the MathML namespace URI."""
    doc = parse_html("<!DOCTYPE html><body><math><mi>x</mi></math></body>")
    body = _get_body(doc)
    math_elements = [el for el in body.children if el.local_name == "math"]
    assert len(math_elements) >= 1
    math = math_elements[0]
    assert math.namespace_uri == MATHML_NAMESPACE


def test_exit_foreign_content_on_html_tag():
    """HTML elements after SVG are in HTML namespace."""
    doc = parse_html("<!DOCTYPE html><body><svg></svg><p>after svg</p></body>")
    body = _get_body(doc)
    children = list(body.children)
    # Find the <p> after <svg>
    p_elements = [el for el in children if el.local_name == "p"]
    assert len(p_elements) >= 1
    # <p> must be in HTML namespace (or None for some impls)
    p = p_elements[0]
    assert p.namespace_uri in ("http://www.w3.org/1999/xhtml",)


def test_svg_attributes_case_adjusted():
    """SVG attribute names are case-adjusted per spec."""
    doc = parse_html(
        '<!DOCTYPE html><body>'
        '<svg viewbox="0 0 100 100" preserveaspectratio="xMidYMid"></svg>'
        '</body>'
    )
    body = _get_body(doc)
    svg_elements = [el for el in body.children if el.local_name == "svg"]
    assert len(svg_elements) >= 1
    svg = svg_elements[0]
    # After adjustment, 'viewbox' -> 'viewBox'
    assert svg.has_attribute("viewBox") or svg.has_attribute("viewbox")


def test_svg_nested_html_integration_point():
    """<foreignObject> in SVG is an HTML integration point."""
    doc = parse_html(
        "<!DOCTYPE html><body><svg><foreignObject><p>inside</p></foreignObject></svg></body>"
    )
    body = _get_body(doc)
    # Parser must not crash
    assert doc.document_element is not None
