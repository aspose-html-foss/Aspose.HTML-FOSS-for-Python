"""Acceptance tests for BACK-6 — HTML serialiser.

All test cases specified in ADR-006-html-serialiser.md § Testing.
"""
from __future__ import annotations

import doctest

import pytest

import aspose_html.serialiser
from aspose_html.dom import (
    CDATASection,
    Comment,
    Document,
    DocumentFragment,
    DocumentType,
    NodeType,
    ProcessingInstruction,
    Text,
)
from aspose_html.html_document import HTMLDocument
from aspose_html.serialiser import inner_html, outer_html, serialise


# ---------------------------------------------------------------------------
# AC-1 — Import tests
# ---------------------------------------------------------------------------


def test_import_serialise() -> None:
    """from aspose_html.serialiser import serialise works."""
    from aspose_html.serialiser import serialise as _s

    assert callable(_s)


def test_import_inner_html() -> None:
    """from aspose_html.serialiser import inner_html works."""
    from aspose_html.serialiser import inner_html as _ih

    assert callable(_ih)


def test_import_outer_html() -> None:
    """from aspose_html.serialiser import outer_html works."""
    from aspose_html.serialiser import outer_html as _oh

    assert callable(_oh)


def test_import_from_package() -> None:
    """from aspose_html import serialise works."""
    from aspose_html import serialise as _s

    assert callable(_s)


# ---------------------------------------------------------------------------
# AC-2 — Element serialisation
# ---------------------------------------------------------------------------


def test_empty_element() -> None:
    """serialise(doc.create_element('div')) returns '<div></div>'."""
    doc = Document()
    el = doc.create_element("div")
    assert serialise(el) == "<div></div>"


def test_element_with_text_child() -> None:
    """Element containing a text node serialises correctly."""
    doc = Document()
    p = doc.create_element("p")
    t = doc.create_text_node("Hello")
    p.append_child(t)
    assert serialise(p) == "<p>Hello</p>"


def test_element_with_attribute() -> None:
    """Single attribute: <p class=\"x\"> serialised correctly."""
    doc = Document()
    p = doc.create_element("p")
    p.set_attribute("class", "x")
    assert serialise(p) == '<p class="x"></p>'


def test_element_multiple_attributes() -> None:
    """Multiple attributes appear in insertion order."""
    doc = Document()
    el = doc.create_element("a")
    el.set_attribute("href", "http://example.com")
    el.set_attribute("target", "_blank")
    result = serialise(el)
    assert result == '<a href="http://example.com" target="_blank"></a>'


def test_nested_elements() -> None:
    """<ul><li>a</li><li>b</li></ul> serialises correctly."""
    doc = Document()
    ul = doc.create_element("ul")
    li1 = doc.create_element("li")
    li1.append_child(doc.create_text_node("a"))
    li2 = doc.create_element("li")
    li2.append_child(doc.create_text_node("b"))
    ul.append_child(li1)
    ul.append_child(li2)
    assert serialise(ul) == "<ul><li>a</li><li>b</li></ul>"


# ---------------------------------------------------------------------------
# AC-3 — Void elements (INV-008)
# ---------------------------------------------------------------------------


def test_void_br() -> None:
    """serialise(br_element) returns '<br>' (no closing tag)."""
    doc = Document()
    br = doc.create_element("br")
    assert serialise(br) == "<br>"


def test_void_img() -> None:
    """<img src='x.png'> serialised without closing tag."""
    doc = Document()
    img = doc.create_element("img")
    img.set_attribute("src", "x.png")
    assert serialise(img) == '<img src="x.png">'


def test_void_input() -> None:
    """<input type='text'> serialised without closing tag."""
    doc = Document()
    inp = doc.create_element("input")
    inp.set_attribute("type", "text")
    assert serialise(inp) == '<input type="text">'


@pytest.mark.parametrize("tag", sorted([
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]))
def test_all_void_elements(tag: str) -> None:
    """All 14 void elements produce no closing tag (INV-008)."""
    doc = Document()
    el = doc.create_element(tag)
    result = serialise(el)
    assert result == f"<{tag}>"
    assert f"</{tag}>" not in result


# ---------------------------------------------------------------------------
# AC-4 — Text escaping (INV-009)
# ---------------------------------------------------------------------------


def test_text_escape_ampersand() -> None:
    """& in text → &amp;."""
    doc = Document()
    t = doc.create_text_node("a & b")
    assert serialise(t) == "a &amp; b"


def test_text_escape_lt() -> None:
    """< in text → &lt;."""
    doc = Document()
    t = doc.create_text_node("a < b")
    assert serialise(t) == "a &lt; b"


def test_text_escape_gt() -> None:
    """> in text → &gt;."""
    doc = Document()
    t = doc.create_text_node("a > b")
    assert serialise(t) == "a &gt; b"


def test_text_escape_nbsp() -> None:
    r"""Non-breaking space \u00a0 in text → &nbsp;."""
    doc = Document()
    t = doc.create_text_node("a\u00a0b")
    assert serialise(t) == "a&nbsp;b"


def test_text_no_escaping_in_script() -> None:
    """<script> content is NOT escaped (raw text element — §13.3)."""
    doc = Document()
    script = doc.create_element("script")
    script.append_child(doc.create_text_node("if (a < b && c > d) {}"))
    result = serialise(script)
    assert result == "<script>if (a < b && c > d) {}</script>"


def test_text_no_escaping_in_style() -> None:
    """<style> content is NOT escaped (raw text element — §13.3)."""
    doc = Document()
    style = doc.create_element("style")
    style.append_child(doc.create_text_node("div > p { color: red; }"))
    result = serialise(style)
    assert result == "<style>div > p { color: red; }</style>"


# ---------------------------------------------------------------------------
# AC-5 — Attribute escaping (INV-009)
# ---------------------------------------------------------------------------


def test_attr_escape_quote() -> None:
    """Attribute value with \" → &quot;."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("data-val", 'say "hello"')
    result = serialise(el)
    assert 'data-val="say &quot;hello&quot;"' in result


def test_attr_escape_ampersand() -> None:
    """Attribute value with & → &amp;."""
    doc = Document()
    el = doc.create_element("a")
    el.set_attribute("href", "?a=1&b=2")
    result = serialise(el)
    assert 'href="?a=1&amp;b=2"' in result


def test_attr_escape_nbsp() -> None:
    r"""Non-breaking space \u00a0 in attribute value → &nbsp;."""
    doc = Document()
    el = doc.create_element("span")
    el.set_attribute("title", "a\u00a0b")
    result = serialise(el)
    assert 'title="a&nbsp;b"' in result


def test_attr_no_escape_lt_gt() -> None:
    """< and > in attribute values survive the round-trip (valid HTML)."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("data-x", "<value>")
    result = serialise(el)
    # Result must be a valid attribute value string (not bare < or > adjacent
    # to quotes — either escaped or left as-is, both are acceptable per spec).
    assert "data-x=" in result
    assert "value" in result


# ---------------------------------------------------------------------------
# AC-6 — Comment, DocumentType, ProcessingInstruction
# ---------------------------------------------------------------------------


def test_comment_serialise() -> None:
    """doc.create_comment('hello') → '<!--hello-->'."""
    doc = Document()
    c = doc.create_comment("hello")
    assert serialise(c) == "<!--hello-->"


def test_doctype_no_ids() -> None:
    """DocumentType(name='html') → '<!DOCTYPE html>'."""
    dt = DocumentType("html")
    assert serialise(dt) == "<!DOCTYPE html>"


def test_doctype_with_public_system_ids() -> None:
    """public + system IDs produce correct PUBLIC '...' '...' form."""
    dt = DocumentType(
        "html",
        public_id="-//W3C//DTD XHTML 1.0//EN",
        system_id="http://www.w3.org/TR/xhtml1/DTD/xhtml1.dtd",
    )
    result = serialise(dt)
    assert result == (
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0//EN"'
        ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1.dtd">'
    )


def test_doctype_system_id_only() -> None:
    """system_id only (no public_id) produces SYSTEM '...' form."""
    dt = DocumentType("html", system_id="about:legacy-compat")
    result = serialise(dt)
    assert result == '<!DOCTYPE html SYSTEM "about:legacy-compat">'


def test_processing_instruction() -> None:
    """Processing instruction serialises correctly."""
    pi = ProcessingInstruction("xml", 'version="1.0"')
    result = serialise(pi)
    assert result == '<?xml version="1.0"?>'


# ---------------------------------------------------------------------------
# AC-7 — Document and DocumentFragment
# ---------------------------------------------------------------------------


def test_document_serialise_includes_doctype() -> None:
    """Document with doctype child includes '<!DOCTYPE html>' prefix."""
    doc = Document()
    dt = DocumentType("html", owner_document=doc)
    doc.append_child(dt)
    html_el = doc.create_element("html")
    doc.append_child(html_el)
    result = serialise(doc)
    assert result.startswith("<!DOCTYPE html>")
    assert "<html></html>" in result


def test_document_fragment_serialise() -> None:
    """Fragment with two children serialises both."""
    doc = Document()
    frag = doc.create_document_fragment()
    frag.append_child(doc.create_element("p"))
    frag.append_child(doc.create_element("div"))
    result = serialise(frag)
    assert result == "<p></p><div></div>"


def test_inner_html_returns_children_only() -> None:
    """inner_html(element) returns children without the wrapping element tag."""
    doc = Document()
    div = doc.create_element("div")
    div.append_child(doc.create_element("span"))
    div.append_child(doc.create_text_node("text"))
    result = inner_html(div)
    assert result == "<span></span>text"
    assert "<div>" not in result


def test_outer_html_equals_serialise() -> None:
    """outer_html(el) == serialise(el) for element nodes."""
    doc = Document()
    el = doc.create_element("section")
    el.set_attribute("id", "main")
    el.append_child(doc.create_text_node("content"))
    assert outer_html(el) == serialise(el)


# ---------------------------------------------------------------------------
# AC-8 — CDATASection
# ---------------------------------------------------------------------------


def test_cdata_section_treated_as_text() -> None:
    """CDATASection content is escaped like text in HTML mode (§13.3)."""
    doc = Document()
    cds = CDATASection("a < b & c", owner_document=doc)
    result = serialise(cds)
    assert result == "a &lt; b &amp; c"


# ---------------------------------------------------------------------------
# AC-9 — TypeError
# ---------------------------------------------------------------------------


def test_non_node_raises_typeerror() -> None:
    """serialise('not a node') raises TypeError."""
    with pytest.raises(TypeError, match="serialise\\(\\) expects a Node"):
        serialise("not a node")  # type: ignore[arg-type]


def test_non_node_int_raises_typeerror() -> None:
    """serialise(42) raises TypeError."""
    with pytest.raises(TypeError, match="serialise\\(\\) expects a Node"):
        serialise(42)  # type: ignore[arg-type]


def test_inner_html_non_node_raises_typeerror() -> None:
    """inner_html(42) raises TypeError."""
    with pytest.raises(TypeError, match="inner_html\\(\\) expects a Node"):
        inner_html(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC-10 — Doctest (INV-003)
# ---------------------------------------------------------------------------


def test_doctest_serialiser() -> None:
    """doctest.testmod on aspose_html.serialiser passes with 0 failures."""
    results = doctest.testmod(aspose_html.serialiser, verbose=False)
    assert results.failed == 0, (
        f"{results.failed} doctest(s) failed in aspose_html.serialiser"
    )


# ---------------------------------------------------------------------------
# AC-11 — Round-trip smoke tests (INV-010)
# ---------------------------------------------------------------------------


def test_round_trip_simple() -> None:
    """parse '<p class=\"x\">hello</p>' → serialise → re-parse → same structure."""
    original_html = '<p class="x">hello</p>'
    doc = HTMLDocument.parse(original_html)

    # The parser wraps in html/head/body — find the <p> via body
    body = list(doc.document_element.children)[1]  # <body>
    p_elements = [c for c in body.child_nodes if c.node_type == NodeType.ELEMENT_NODE]
    assert p_elements, "Expected a <p> element inside <body>"
    p_el = p_elements[0]

    # Serialise the <p> element
    serialised = serialise(p_el)
    assert serialised == '<p class="x">hello</p>'

    # Re-parse the serialised output
    doc2 = HTMLDocument.parse(serialised)
    body2 = list(doc2.document_element.children)[1]
    p2_elements = [c for c in body2.child_nodes if c.node_type == NodeType.ELEMENT_NODE]
    assert p2_elements
    p2 = p2_elements[0]

    # Structural equivalence: tag, attribute, text content
    assert p2.local_name == "p"
    assert p2.get_attribute("class") == "x"
    text_children = [c for c in p2.child_nodes if c.node_type == NodeType.TEXT_NODE]
    assert text_children
    assert text_children[0].data == "hello"


def test_round_trip_nested() -> None:
    """parse '<ul><li>a</li><li>b</li></ul>' → serialise → re-parse → same structure."""
    original_html = "<ul><li>a</li><li>b</li></ul>"
    doc = HTMLDocument.parse(original_html)

    body = list(doc.document_element.children)[1]
    ul_elements = [c for c in body.child_nodes if c.node_type == NodeType.ELEMENT_NODE]
    assert ul_elements
    ul_el = ul_elements[0]
    assert ul_el.local_name == "ul"

    serialised = serialise(ul_el)
    assert serialised == "<ul><li>a</li><li>b</li></ul>"

    doc2 = HTMLDocument.parse(serialised)
    body2 = list(doc2.document_element.children)[1]
    ul2_elements = [c for c in body2.child_nodes if c.node_type == NodeType.ELEMENT_NODE]
    assert ul2_elements
    ul2 = ul2_elements[0]
    assert ul2.local_name == "ul"

    li_elements = [c for c in ul2.child_nodes if c.node_type == NodeType.ELEMENT_NODE]
    assert len(li_elements) == 2
    assert li_elements[0].local_name == "li"
    assert li_elements[1].local_name == "li"


def test_round_trip_entities() -> None:
    """Text with & → serialise → re-parse preserves text (INV-010)."""
    doc = HTMLDocument.parse("<p>a &amp; b</p>")
    body = list(doc.document_element.children)[1]
    p_elements = [c for c in body.child_nodes if c.node_type == NodeType.ELEMENT_NODE]
    p_el = p_elements[0]

    # After parsing, the text node data is the unescaped value
    text_nodes = [c for c in p_el.child_nodes if c.node_type == NodeType.TEXT_NODE]
    assert text_nodes
    assert text_nodes[0].data == "a & b"

    # Serialise re-escapes it
    serialised = serialise(p_el)
    assert "&amp;" in serialised

    # Re-parse — text is preserved
    doc2 = HTMLDocument.parse(serialised)
    body2 = list(doc2.document_element.children)[1]
    p2_elements = [c for c in body2.child_nodes if c.node_type == NodeType.ELEMENT_NODE]
    p2 = p2_elements[0]
    text_nodes2 = [c for c in p2.child_nodes if c.node_type == NodeType.TEXT_NODE]
    assert text_nodes2
    assert text_nodes2[0].data == "a & b"


def test_serialise_empty_document() -> None:
    """HTMLDocument.parse('') serialises without error."""
    doc = HTMLDocument.parse("")
    result = serialise(doc)
    assert isinstance(result, str)
    # An empty parse still produces an html/head/body skeleton
    assert "<html>" in result or "<HTML>" in result.upper()


def test_serialise_full_document() -> None:
    """Serialise a full document includes html/head/body."""
    doc = HTMLDocument.parse("<!DOCTYPE html><html><head></head><body><p>Hi</p></body></html>")
    result = serialise(doc)
    assert "<!DOCTYPE html>" in result
    assert "<html>" in result
    assert "<head>" in result
    assert "<body>" in result
    assert "<p>Hi</p>" in result


def test_serialise_comment_in_document() -> None:
    """<!--foo --> round-trips correctly through parse → serialise."""
    doc = HTMLDocument.parse("<!-- foo -->")
    result = serialise(doc)
    assert "<!-- foo -->" in result
