"""Tests for structural HTMLElement subclasses —  / ."""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    Element,
    HTMLElement,
    HTMLDivElement,
    HTMLSpanElement,
    HTMLParagraphElement,
    HTMLHeadingElement,
)


@pytest.fixture()
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# AC-1 through AC-4: create_element returns correct subclass
# ---------------------------------------------------------------------------

def test_create_element_div_returns_htmldivelement(doc: Document) -> None:
    """AC-1: create_element('div') returns HTMLDivElement."""
    el = doc.create_element("div")
    assert isinstance(el, HTMLDivElement)
    assert type(el) is HTMLDivElement


def test_create_element_span_returns_htmlspanelement(doc: Document) -> None:
    """AC-2: create_element('span') returns HTMLSpanElement."""
    el = doc.create_element("span")
    assert isinstance(el, HTMLSpanElement)
    assert type(el) is HTMLSpanElement


def test_create_element_p_returns_htmlparagraphelement(doc: Document) -> None:
    """AC-3: create_element('p') returns HTMLParagraphElement."""
    el = doc.create_element("p")
    assert isinstance(el, HTMLParagraphElement)
    assert type(el) is HTMLParagraphElement


@pytest.mark.parametrize("tag", ["h1", "h2", "h3", "h4", "h5", "h6"])
def test_create_element_headings_return_htmlheadingelement(
    doc: Document, tag: str
) -> None:
    """AC-4: h1–h6 all return HTMLHeadingElement."""
    el = doc.create_element(tag)
    assert isinstance(el, HTMLHeadingElement)
    assert type(el) is HTMLHeadingElement


# ---------------------------------------------------------------------------
# AC-5: isinstance hierarchy
# ---------------------------------------------------------------------------

def test_structural_elements_isinstance_hierarchy(doc: Document) -> None:
    """AC-5: All new classes are isinstance-compatible with HTMLElement and Element."""
    for tag, cls in [
        ("div", HTMLDivElement),
        ("span", HTMLSpanElement),
        ("p", HTMLParagraphElement),
        ("h1", HTMLHeadingElement),
    ]:
        el = doc.create_element(tag)
        assert isinstance(el, HTMLElement)
        assert isinstance(el, Element)
        assert isinstance(el, cls)


# ---------------------------------------------------------------------------
# AC-6: exported from aspose_html.dom
# ---------------------------------------------------------------------------

def test_new_classes_exported_from_aspose_html_dom() -> None:
    """AC-6: All new classes are in dom.__all__ and accessible as attributes."""
    import aspose_html.dom as dom_module
    for name in [
        "HTMLDivElement",
        "HTMLSpanElement",
        "HTMLParagraphElement",
        "HTMLHeadingElement",
    ]:
        assert name in dom_module.__all__, f"{name} missing from __all__"
        assert hasattr(dom_module, name), f"{name} not accessible on dom"


# ---------------------------------------------------------------------------
# AC-7: __slots__ = ()
# ---------------------------------------------------------------------------

def test_new_classes_have_empty_slots() -> None:
    """AC-7: All new structural subclasses have __slots__ = ()."""
    for cls in [
        HTMLDivElement,
        HTMLSpanElement,
        HTMLParagraphElement,
        HTMLHeadingElement,
    ]:
        assert cls.__slots__ == (), f"{cls.__name__} does not have __slots__ = ()"


# ---------------------------------------------------------------------------
# Tag name preservation for headings
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tag", ["h1", "h2", "h3", "h4", "h5", "h6"])
def test_heading_tag_name_preserved(doc: Document, tag: str) -> None:
    """Heading elements preserve their exact tag name."""
    el = doc.create_element(tag)
    assert el.local_name == tag
    assert el.tag_name == tag.upper()
