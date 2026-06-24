""" integration matrix —  /  /  / .

Groups:
  A — create_element_ns qualified-name split ( end-to-end)
  B — serialiser namespace-aware tag emission ()
  C — doc/milestone validation (invariants, round-trips, stability)
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document
from aspose_html.serialiser import serialise, inner_html, outer_html

SVG_NS = "http://www.w3.org/2000/svg"
MATHML_NS = "http://www.w3.org/1998/Math/MathML"
HTML_NS = "http://www.w3.org/1999/xhtml"
XLINK_NS = "http://www.w3.org/1999/xlink"
UNKNOWN_NS = "urn:example:foo"


@pytest.fixture
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# Group A — create_element_ns qualified-name split (≥ 6 tests)
# ---------------------------------------------------------------------------


def test_svg_path_prefix_and_local_name(doc: Document) -> None:
    """create_element_ns with 'svg:path' yields prefix='svg', local_name='path'."""
    el = doc.create_element_ns(SVG_NS, "svg:path")
    assert el.prefix == "svg"
    assert el.local_name == "path"
    assert el.namespace_uri == SVG_NS


def test_svg_circle_no_prefix(doc: Document) -> None:
    """create_element_ns with unqualified name 'circle' yields prefix=None."""
    el = doc.create_element_ns(SVG_NS, "circle")
    assert el.prefix is None
    assert el.local_name == "circle"
    assert el.namespace_uri == SVG_NS


def test_mathml_math_qualified_name(doc: Document) -> None:
    """create_element_ns with 'math:mrow' yields prefix='math', local_name='mrow'."""
    el = doc.create_element_ns(MATHML_NS, "math:mrow")
    assert el.prefix == "math"
    assert el.local_name == "mrow"
    assert el.namespace_uri == MATHML_NS


def test_html_div_no_namespace_prefix(doc: Document) -> None:
    """HTML-namespace element created without prefix has prefix=None."""
    el = doc.create_element_ns(HTML_NS, "div")
    assert el.prefix is None
    assert el.local_name == "div"
    assert el.namespace_uri == HTML_NS


def test_qualified_name_tag_name_roundtrip(doc: Document) -> None:
    """tag_name returns the full qualified name (prefix:local_name) for prefixed elements."""
    el = doc.create_element_ns(SVG_NS, "svg:path")
    # WHATWG DOM §4.6: tag_name is the qualified name
    assert el.tag_name == "svg:path"


def test_svg_elements_retrievable_by_tag_name(doc: Document) -> None:
    """SVG elements created via create_element_ns are findable by tag name."""
    svg = doc.create_element_ns(SVG_NS, "svg:svg")
    path = doc.create_element_ns(SVG_NS, "svg:path")
    svg.append_child(path)
    doc.append_child(svg)

    # get_elements_by_tag_name uses local_name for matching
    results = doc.get_elements_by_tag_name("path")
    assert len(results) == 1
    assert results[0] is path


# ---------------------------------------------------------------------------
# Group B — serialiser namespace-aware tag emission (≥ 6 tests)
# ---------------------------------------------------------------------------


def test_svg_element_serialises_lowercase(doc: Document) -> None:
    """SVG element with prefix 'svg:circle' serialises as <circle></circle>."""
    el = doc.create_element_ns(SVG_NS, "svg:circle")
    assert serialise(el) == "<circle></circle>"


def test_svg_element_with_prefix_serialises_qualified(doc: Document) -> None:
    """Unknown-namespace element with prefix serialises as <foo:bar></foo:bar>."""
    el = doc.create_element_ns(UNKNOWN_NS, "foo:bar")
    assert serialise(el) == "<foo:bar></foo:bar>"


def test_html_element_still_correct(doc: Document) -> None:
    """HTML-namespace elements are unaffected by the namespace-aware change."""
    div = doc.create_element("div")
    span = doc.create_element("span")
    div.append_child(span)
    assert serialise(div) == "<div><span></span></div>"


def test_mathml_element_serialises_lowercase(doc: Document) -> None:
    """MathML element serialises using local_name only, no prefix."""
    mi = doc.create_element_ns(MATHML_NS, "mi")
    text = doc.create_text_node("x")
    mi.append_child(text)
    assert serialise(mi) == "<mi>x</mi>"


def test_void_element_no_close_tag(doc: Document) -> None:
    """HTML void elements do not emit a closing tag (regression guard)."""
    br = doc.create_element("br")
    assert serialise(br) == "<br>"


def test_outer_html_svg_round_trip(doc: Document) -> None:
    """outer_html and serialise agree for SVG elements."""
    el = doc.create_element_ns(SVG_NS, "svg:rect")
    assert outer_html(el) == serialise(el) == "<rect></rect>"


def test_svg_no_prefix_element_serialises_lowercase(doc: Document) -> None:
    """SVG element without prefix also serialises using local_name."""
    el = doc.create_element_ns(SVG_NS, "path")
    assert serialise(el) == "<path></path>"


def test_unknown_ns_no_prefix_serialises_local_name(doc: Document) -> None:
    """Unknown-namespace element without prefix serialises as local_name only."""
    el = doc.create_element_ns(UNKNOWN_NS, "bar")
    assert serialise(el) == "<bar></bar>"


def test_mathml_prefixed_element_serialises_local_name(doc: Document) -> None:
    """MathML element with prefix serialises using local_name only (not qualified)."""
    el = doc.create_element_ns(MATHML_NS, "m:msup")
    # MathML namespace → use local_name regardless of prefix
    assert serialise(el) == "<msup></msup>"


# ---------------------------------------------------------------------------
# Group C — doc/milestone validation (≥ 4 tests)
# ---------------------------------------------------------------------------


def test_create_element_ns_docstring_example_works(doc: Document) -> None:
    """The create_element_ns docstring example: prefix/local_name values are correct."""
    el = doc.create_element_ns("http://www.w3.org/2000/svg", "svg:path")
    assert el.local_name == "path"
    assert el.prefix == "svg"
    assert el.namespace_uri == "http://www.w3.org/2000/svg"


def test_serialiser_svg_consistent_with_dom(doc: Document) -> None:
    """serialise() emits local_name, consistent with element.local_name for SVG."""
    el = doc.create_element_ns(SVG_NS, "svg:circle")
    emitted = serialise(el)
    # The tag in the emitted HTML should be exactly local_name
    assert emitted == f"<{el.local_name}></{el.local_name}>"


def test_namespace_uri_preserved_on_element(doc: Document) -> None:
    """namespace_uri is stored and retrieved unchanged after create_element_ns."""
    el = doc.create_element_ns(SVG_NS, "svg:g")
    assert el.namespace_uri == SVG_NS
    assert el.prefix == "svg"
    assert el.local_name == "g"


def test_prefix_preserved_after_append_child(doc: Document) -> None:
    """Element prefix/local_name are not mutated by append_child into a tree."""
    parent = doc.create_element_ns(SVG_NS, "svg:svg")
    child = doc.create_element_ns(SVG_NS, "svg:path")
    doc.append_child(parent)
    parent.append_child(child)

    assert child.prefix == "svg"
    assert child.local_name == "path"
    # And serialisation still correct after tree insertion
    assert serialise(child) == "<path></path>"


def test_inner_html_svg_children(doc: Document) -> None:
    """inner_html serialises SVG children using local names."""
    container = doc.create_element_ns(SVG_NS, "svg:svg")
    circle = doc.create_element_ns(SVG_NS, "svg:circle")
    rect = doc.create_element_ns(SVG_NS, "svg:rect")
    container.append_child(circle)
    container.append_child(rect)

    assert inner_html(container) == "<circle></circle><rect></rect>"


def test_html_regression_div_with_attrs(doc: Document) -> None:
    """HTML div with attributes serialises unchanged —  regression guard."""
    div = doc.create_element("div")
    div.set_attribute("class", "box")
    div.set_attribute("id", "main")
    span = doc.create_element("span")
    span.append_child(doc.create_text_node("hello"))
    div.append_child(span)
    assert serialise(div) == '<div class="box" id="main"><span>hello</span></div>'
