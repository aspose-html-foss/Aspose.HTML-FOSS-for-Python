"""Acceptance tests for BACK-5 — HTMLDocument parse API.

All test cases are specified in ADR-005-html-parse-api.md § Testing.
"""
from __future__ import annotations

import doctest

import pytest

import aspose_html.html_document
from aspose_html.dom import Document, DocumentFragment
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Input type handling
# ---------------------------------------------------------------------------

def test_parse_str_returns_document() -> None:
    doc = HTMLDocument.parse("<p>hi</p>")
    assert isinstance(doc, Document)


def test_parse_bytes_returns_document() -> None:
    doc = HTMLDocument.parse(b"<p>hi</p>")
    assert isinstance(doc, Document)


def test_parse_invalid_type_raises_typeerror() -> None:
    with pytest.raises(TypeError):
        HTMLDocument.parse(123)  # type: ignore[arg-type]


def test_parse_list_raises_typeerror() -> None:
    with pytest.raises(TypeError):
        HTMLDocument.parse(["<p>"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Encoding parameter guarding
# ---------------------------------------------------------------------------

def test_encoding_with_str_raises_typeerror() -> None:
    with pytest.raises(TypeError):
        HTMLDocument.parse("<p>hi</p>", encoding="utf-8")


def test_encoding_none_with_str_is_ok() -> None:
    # Must not raise — encoding=None is the default and is always allowed.
    doc = HTMLDocument.parse("<p>hi</p>", encoding=None)
    assert isinstance(doc, Document)


# ---------------------------------------------------------------------------
# Bytes input: encoding detection pipeline
# ---------------------------------------------------------------------------

def test_bytes_utf8_bom_detected() -> None:
    """UTF-8 BOM (\xef\xbb\xbf) is consumed; BOM bytes are not in text content."""
    bom = b"\xef\xbb\xbf"
    doc = HTMLDocument.parse(bom + b"<p>hi</p>")
    assert isinstance(doc, Document)
    # BOM must not appear as text content
    body = list(doc.document_element.children)[1]
    text_nodes = [n.data for n in body.child_nodes if n.node_type == 3]  # type: ignore[union-attr]
    text_content = "".join(text_nodes)
    assert "\ufeff" not in text_content


def test_bytes_utf8_no_bom() -> None:
    """Plain UTF-8 bytes (no BOM) parse correctly."""
    doc = HTMLDocument.parse(b"<p>hello</p>")
    assert isinstance(doc, Document)
    assert doc.document_element.tag_name == "HTML"


def test_bytes_meta_charset_prescan() -> None:
    """windows-1252 detected from <meta charset>; 0xE9 decodes as U+00E9 (é)."""
    data = b'<meta charset="windows-1252"><p>caf\xe9</p>'
    doc = HTMLDocument.parse(data)
    assert isinstance(doc, Document)
    body = list(doc.document_element.children)[1]
    # Collect text from all descendant text nodes
    p = list(body.children)[0]
    text = "".join(n.data for n in p.child_nodes if n.node_type == 3)  # type: ignore[union-attr]
    assert "\xe9" in text  # U+00E9 — é


def test_bytes_encoding_override() -> None:
    """Caller-supplied encoding='windows-1252' decodes 0xE9 as U+00E9."""
    doc = HTMLDocument.parse(b"<p>caf\xe9</p>", encoding="windows-1252")
    assert isinstance(doc, Document)
    body = list(doc.document_element.children)[1]
    p = list(body.children)[0]
    text = "".join(n.data for n in p.child_nodes if n.node_type == 3)  # type: ignore[union-attr]
    assert "\xe9" in text


def test_bytes_invalid_encoding_raises_valueerror() -> None:
    """An unrecognised WHATWG encoding label propagates as ValueError."""
    with pytest.raises(ValueError):
        HTMLDocument.parse(b"<p>x</p>", encoding="not-real")


def test_bytes_empty() -> None:
    """Empty bytes input produces a valid Document without raising."""
    doc = HTMLDocument.parse(b"")
    assert isinstance(doc, Document)


# ---------------------------------------------------------------------------
# Document structure (integration)
# ---------------------------------------------------------------------------

def test_parse_produces_html_element() -> None:
    """Any input produces a Document whose document_element.tag_name == 'HTML'."""
    doc = HTMLDocument.parse("<div>test</div>")
    assert doc.document_element.tag_name == "HTML"


def test_parse_body_content() -> None:
    """<p>Hello</p> → body contains a <P> element."""
    doc = HTMLDocument.parse("<p>Hello</p>")
    body = list(doc.document_element.children)[1]
    children = list(body.children)
    tag_names = [el.tag_name for el in children]
    assert "P" in tag_names


def test_parse_errors_on_document() -> None:
    """Malformed HTML collects parse errors on document.parse_errors."""
    # Deliberately malformed: unclosed tags, mis-nesting.
    doc = HTMLDocument.parse("</b></b></b>")
    assert hasattr(doc, "parse_errors")
    # The parser should record at least one error for each bogus end tag.
    assert len(doc.parse_errors) > 0


def test_parse_errors_empty_for_valid() -> None:
    """Well-formed HTML produces an empty parse_errors list."""
    doc = HTMLDocument.parse("<!DOCTYPE html><html><head></head><body></body></html>")
    assert hasattr(doc, "parse_errors")
    assert len(doc.parse_errors) == 0


# ---------------------------------------------------------------------------
# base_url parameter
# ---------------------------------------------------------------------------

def test_base_url_accepted() -> None:
    """base_url keyword argument is accepted without raising."""
    doc = HTMLDocument.parse("<p>x</p>", base_url="https://example.com")
    assert isinstance(doc, Document)


def test_base_url_none_is_default() -> None:
    """Omitting base_url is equivalent to base_url=None."""
    doc1 = HTMLDocument.parse("<p>x</p>")
    doc2 = HTMLDocument.parse("<p>x</p>", base_url=None)
    # Both must return valid Documents; structural equality is not required.
    assert isinstance(doc1, Document)
    assert isinstance(doc2, Document)


# ---------------------------------------------------------------------------
# Public API contract
# ---------------------------------------------------------------------------

def test_import_from_package() -> None:
    """from aspose_html import HTMLDocument must work."""
    from aspose_html import HTMLDocument as HD  # noqa: PLC0415
    assert HD is HTMLDocument


def test_import_from_module() -> None:
    """from aspose_html.html_document import HTMLDocument must work."""
    from aspose_html.html_document import HTMLDocument as HD  # noqa: PLC0415
    assert HD is HTMLDocument


def test_parse_is_classmethod() -> None:
    """HTMLDocument.parse is callable without an instance."""
    # classmethod descriptors are callable on the class itself.
    assert callable(HTMLDocument.parse)
    # Confirm it works as a classmethod (no self/instance needed).
    doc = HTMLDocument.parse("<p>test</p>")
    assert isinstance(doc, Document)


def test_doctest_passes() -> None:
    """All docstring examples in html_document.py must pass (INV-003)."""
    results = doctest.testmod(aspose_html.html_document, verbose=False)
    assert results.failed == 0, f"{results.failed} doctest(s) failed in html_document"


# ---------------------------------------------------------------------------
# parse_fragment API
# ---------------------------------------------------------------------------

def test_parse_fragment_str_returns_document_fragment() -> None:
    frag = HTMLDocument.parse_fragment("<p>Hello</p>")
    assert isinstance(frag, DocumentFragment)


def test_parse_fragment_bytes_returns_document_fragment() -> None:
    frag = HTMLDocument.parse_fragment(b"<p>Hello</p>")
    assert isinstance(frag, DocumentFragment)


def test_parse_fragment_invalid_type_raises_typeerror() -> None:
    with pytest.raises(TypeError):
        HTMLDocument.parse_fragment(42)  # type: ignore[arg-type]


def test_parse_fragment_encoding_with_str_raises_typeerror() -> None:
    with pytest.raises(TypeError):
        HTMLDocument.parse_fragment("<p>x</p>", encoding="utf-8")
