"""Tests for all hierarchy violation cases."""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    DocumentType,
    HierarchyRequestError,
    WrongDocumentError,
)


@pytest.fixture
def doc() -> Document:
    return Document()


def test_document_cannot_have_two_element_children(doc: Document) -> None:
    a = doc.create_element("html")
    b = doc.create_element("body")
    doc.append_child(a)
    with pytest.raises(HierarchyRequestError):
        doc.append_child(b)


def test_document_cannot_have_two_doctype_children(doc: Document) -> None:
    dt1 = DocumentType("html")
    dt2 = DocumentType("html")
    doc.append_child(dt1)
    with pytest.raises(HierarchyRequestError):
        doc.append_child(dt2)


def test_attr_cannot_be_child_of_element(doc: Document) -> None:
    """Attr must not be insertable as a child of an Element."""
    from aspose_html.dom import Attr
    el = doc.create_element("div")
    doc.append_child(el)
    attr = Attr("id", "x", owner_document=doc)
    with pytest.raises(HierarchyRequestError):
        el.append_child(attr)


def test_doctype_cannot_have_children(doc: Document) -> None:
    dt = DocumentType("html")
    doc.append_child(dt)
    el = doc.create_element("p")
    with pytest.raises(HierarchyRequestError):
        dt.append_child(el)


def test_text_cannot_have_children(doc: Document) -> None:
    t = doc.create_text_node("hi")
    el = doc.create_element("p")
    with pytest.raises(HierarchyRequestError):
        t.append_child(el)


def test_wrong_document_error(doc: Document) -> None:
    """Inserting a node from a different document raises WrongDocumentError."""
    doc2 = Document()
    el1 = doc.create_element("div")
    el2 = doc2.create_element("span")
    doc.append_child(el1)
    with pytest.raises(WrongDocumentError):
        el1.append_child(el2)


def test_element_cannot_contain_document(doc: Document) -> None:
    el = doc.create_element("div")
    doc.append_child(el)
    doc2 = Document()
    with pytest.raises(HierarchyRequestError):
        el.append_child(doc2)  # type: ignore[arg-type]
