"""Tests for HTML list element subclasses — BACK-36 / ADR-032."""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    Element,
    HTMLElement,
    HTMLUListElement,
    HTMLOListElement,
    HTMLLIElement,
    HTMLDListElement,
)


@pytest.fixture()
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# Dispatch: create_element returns correct subclass
# ---------------------------------------------------------------------------

def test_ul_dispatch(doc: Document) -> None:
    el = doc.create_element("ul")
    assert isinstance(el, HTMLUListElement)
    assert type(el) is HTMLUListElement


def test_ol_dispatch(doc: Document) -> None:
    el = doc.create_element("ol")
    assert isinstance(el, HTMLOListElement)
    assert type(el) is HTMLOListElement


def test_li_dispatch(doc: Document) -> None:
    el = doc.create_element("li")
    assert isinstance(el, HTMLLIElement)
    assert type(el) is HTMLLIElement


def test_dl_dispatch(doc: Document) -> None:
    el = doc.create_element("dl")
    assert isinstance(el, HTMLDListElement)
    assert type(el) is HTMLDListElement


# ---------------------------------------------------------------------------
# isinstance hierarchy
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tag,cls", [
    ("ul", HTMLUListElement),
    ("ol", HTMLOListElement),
    ("li", HTMLLIElement),
    ("dl", HTMLDListElement),
])
def test_isinstance_chain(doc: Document, tag: str, cls: type) -> None:
    el = doc.create_element(tag)
    assert isinstance(el, cls)
    assert isinstance(el, HTMLElement)
    assert isinstance(el, Element)


# ---------------------------------------------------------------------------
# __slots__ = ()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cls", [
    HTMLUListElement, HTMLOListElement, HTMLLIElement, HTMLDListElement,
])
def test_slots_empty(cls: type) -> None:
    assert cls.__slots__ == ()


# ---------------------------------------------------------------------------
# IDL properties: HTMLOListElement
# ---------------------------------------------------------------------------

def test_ol_start_default(doc: Document) -> None:
    ol = doc.create_element("ol")
    assert ol.start == 1  # type: ignore[attr-defined]


def test_ol_start_setter(doc: Document) -> None:
    ol = doc.create_element("ol")
    ol.start = 5  # type: ignore[attr-defined]
    assert ol.get_attribute("start") == "5"
    assert ol.start == 5  # type: ignore[attr-defined]


def test_ol_reversed_default(doc: Document) -> None:
    ol = doc.create_element("ol")
    assert ol.reversed is False  # type: ignore[attr-defined]


def test_ol_reversed_setter_true(doc: Document) -> None:
    ol = doc.create_element("ol")
    ol.reversed = True  # type: ignore[attr-defined]
    assert ol.has_attribute("reversed")
    assert ol.reversed is True  # type: ignore[attr-defined]


def test_ol_reversed_setter_false(doc: Document) -> None:
    ol = doc.create_element("ol")
    ol.reversed = True  # type: ignore[attr-defined]
    ol.reversed = False  # type: ignore[attr-defined]
    assert not ol.has_attribute("reversed")


def test_ol_type_default(doc: Document) -> None:
    ol = doc.create_element("ol")
    assert ol.type_ == ""  # type: ignore[attr-defined]


def test_ol_type_setter(doc: Document) -> None:
    ol = doc.create_element("ol")
    ol.type_ = "A"  # type: ignore[attr-defined]
    assert ol.get_attribute("type") == "A"


# ---------------------------------------------------------------------------
# IDL properties: HTMLLIElement
# ---------------------------------------------------------------------------

def test_li_value_default(doc: Document) -> None:
    li = doc.create_element("li")
    assert li.value == 0  # type: ignore[attr-defined]


def test_li_value_setter(doc: Document) -> None:
    li = doc.create_element("li")
    li.value = 3  # type: ignore[attr-defined]
    assert li.get_attribute("value") == "3"
    assert li.value == 3  # type: ignore[attr-defined]


def test_li_type_default(doc: Document) -> None:
    li = doc.create_element("li")
    assert li.type_ == ""  # type: ignore[attr-defined]


def test_li_type_setter(doc: Document) -> None:
    li = doc.create_element("li")
    li.type_ = "disc"  # type: ignore[attr-defined]
    assert li.get_attribute("type") == "disc"


# ---------------------------------------------------------------------------
# Exported from aspose_html.dom
# ---------------------------------------------------------------------------

def test_exports_from_dom() -> None:
    import aspose_html.dom as dom
    for name in [
        "HTMLUListElement", "HTMLOListElement", "HTMLLIElement", "HTMLDListElement",
    ]:
        assert name in dom.__all__
        assert hasattr(dom, name)
