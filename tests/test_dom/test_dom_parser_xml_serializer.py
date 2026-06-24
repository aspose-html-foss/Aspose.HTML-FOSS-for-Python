"""Tests for DOMParser and XMLSerializer wrappers."""

from aspose_html import serialise
from aspose_html.dom import DOMException, DOMParser, Document, NotSupportedError, XMLSerializer


def test_domparser_importable_from_dom_and_top_level() -> None:
    """AC-1: DOMParser import surface."""
    from aspose_html import DOMParser as TopLevelDOMParser  # noqa: PLC0415
    from aspose_html.dom import DOMParser as DomDOMParser  # noqa: PLC0415

    assert TopLevelDOMParser is DomDOMParser


def test_domparser_parse_text_html_returns_document_with_body_content() -> None:
    """AC-2: text/html parsing delegates to HTMLDocument.parse()."""
    parser = DOMParser()

    document = parser.parse_from_string("<p>hello</p>", "text/html")

    assert isinstance(document, Document)
    assert document.body is not None
    assert document.body.first_element_child is not None
    assert document.body.first_element_child.tag_name == "P"
    assert document.body.first_element_child.text_content == "hello"


def test_domparser_parse_xml_type_raises_not_supported_error() -> None:
    """AC-3: XML MIME types are out of scope and must raise."""
    parser = DOMParser()

    try:
        parser.parse_from_string("<root/>", "application/xml")
        raise AssertionError("Expected NotSupportedError for XML parsing")
    except NotSupportedError as exc:
        assert isinstance(exc, DOMException)
        assert "not supported" in str(exc).lower()


def test_domparser_unknown_mime_type_raises_not_supported_error() -> None:
    """AC-8 negative case: unsupported MIME type should raise cleanly."""
    parser = DOMParser()

    try:
        parser.parse_from_string("<p>hello</p>", "application/json")
        raise AssertionError("Expected NotSupportedError for unsupported MIME type")
    except NotSupportedError as exc:
        assert isinstance(exc, DOMException)
        assert "text/html" in str(exc)


def test_xmlserializer_importable_from_dom_and_top_level() -> None:
    """AC-4: XMLSerializer import surface."""
    from aspose_html import XMLSerializer as TopLevelXMLSerializer  # noqa: PLC0415
    from aspose_html.dom import XMLSerializer as DomXMLSerializer  # noqa: PLC0415

    assert TopLevelXMLSerializer is DomXMLSerializer


def test_xmlserializer_serialize_document_matches_serialise_function() -> None:
    """AC-5: serialize_to_string(document) matches aspose_html.serialise."""
    parser = DOMParser()
    document = parser.parse_from_string("<!doctype html><html><body><p>x</p></body></html>", "text/html")

    assert XMLSerializer().serialize_to_string(document) == serialise(document)


def test_xmlserializer_serialize_element_matches_outer_html() -> None:
    """AC-6: serialize_to_string(element) matches element.outer_html."""
    document = Document()
    element = document.create_element("div")
    element.set_attribute("class", "box")
    element.append_child(document.create_text_node("content"))

    assert XMLSerializer().serialize_to_string(element) == element.outer_html
