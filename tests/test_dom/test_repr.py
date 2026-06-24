"""Tests for __repr__ / __str__ on each concrete node type."""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    DocumentType,
    DocumentFragment,
)
from aspose_html.dom._attr import Attr
from aspose_html.dom._character_data import CDATASection
from aspose_html.dom._processing_instruction import ProcessingInstruction


@pytest.fixture
def doc() -> Document:
    return Document()


def test_document_repr(doc: Document) -> None:
    r = repr(doc)
    assert "Document" in r
    assert str(doc) == r


def test_element_repr_basic(doc: Document) -> None:
    el = doc.create_element("div")
    r = repr(el)
    assert "Element" in r
    assert "DIV" in r
    assert str(el) == r


def test_element_repr_with_id_and_class(doc: Document) -> None:
    el = doc.create_element("span")
    el.set_attribute("id", "main")
    el.set_attribute("class", "box")
    r = repr(el)
    assert "id=" in r
    assert "main" in r
    assert "class=" in r


def test_text_repr(doc: Document) -> None:
    t = doc.create_text_node("hello")
    r = repr(t)
    assert "Text" in r
    assert "hello" in r
    assert str(t) == r


def test_comment_repr(doc: Document) -> None:
    c = doc.create_comment("note")
    r = repr(c)
    assert "Comment" in r
    assert "note" in r
    assert str(c) == r


def test_cdata_section_repr(doc: Document) -> None:
    cds = CDATASection("raw", owner_document=doc)
    r = repr(cds)
    assert "CDATASection" in r
    assert "raw" in r


def test_processing_instruction_repr(doc: Document) -> None:
    pi = ProcessingInstruction("xml-stylesheet", "type='text/css'", owner_document=doc)
    r = repr(pi)
    assert "ProcessingInstruction" in r
    assert "xml-stylesheet" in r
    assert str(pi) == r


def test_document_type_repr(doc: Document) -> None:
    dt = DocumentType("html")
    r = repr(dt)
    assert "DocumentType" in r
    assert "html" in r
    assert str(dt) == r


def test_document_fragment_repr(doc: Document) -> None:
    frag = doc.create_document_fragment()
    r = repr(frag)
    assert "DocumentFragment" in r
    assert str(frag) == r


def test_attr_repr(doc: Document) -> None:
    attr = Attr("id", "main", owner_document=doc)
    r = repr(attr)
    assert "Attr" in r
    assert "id" in r
    assert "main" in r
    assert str(attr) == r
