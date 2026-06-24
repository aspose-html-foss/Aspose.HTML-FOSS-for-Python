"""Tests for HTMLElement base class ().

Covers acceptance criteria AC-1 through AC-8 from  / .
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, Element, HTMLElement


@pytest.fixture
def doc() -> Document:
    return Document()


# AC-1, AC-5: create_element returns HTMLElement for HTML-namespace
def test_create_element_returns_html_element(doc: Document) -> None:
    """doc.create_element() returns an HTMLElement instance for any tag."""
    el = doc.create_element("div")
    assert isinstance(el, HTMLElement)


# AC-2, AC-6: backward compatibility — HTMLElement is also an Element
def test_create_element_backward_compat_is_element(doc: Document) -> None:
    """HTMLElement is a subclass of Element; existing isinstance checks still hold."""
    el = doc.create_element("div")
    assert isinstance(el, Element)


# AC-3: create_element_ns with HTML namespace returns plain Element (not HTMLElement).
# create_element_ns() is not modified in  — only create_element() dispatches
# through the registry. See  clarification section.
def test_create_element_ns_html_ns_returns_plain_element(doc: Document) -> None:
    """create_element_ns with HTML namespace remains a plain Element in ."""
    el = doc.create_element_ns("http://www.w3.org/1999/xhtml", "div")
    assert isinstance(el, Element)
    assert not isinstance(el, HTMLElement)


# AC-3: create_element_ns with SVG namespace returns plain Element, not HTMLElement
def test_create_element_ns_svg_returns_plain_element(doc: Document) -> None:
    """create_element_ns with SVG namespace returns Element, not HTMLElement."""
    el = doc.create_element_ns("http://www.w3.org/2000/svg", "g")
    assert isinstance(el, Element)
    assert not isinstance(el, HTMLElement)


# AC-4: HTMLElement is exported from aspose_html.dom
def test_html_element_exported_from_dom() -> None:
    """HTMLElement is importable from aspose_html.dom and is a subclass of Element."""
    from aspose_html.dom import HTMLElement as HE
    assert HE is not None
    assert issubclass(HE, Element)


# AC-7: __slots__ = () on HTMLElement — no __dict__ introduced
def test_html_element_slots(doc: Document) -> None:
    """HTMLElement carries __slots__ = () — no new __dict__ on the class."""
    el = doc.create_element("p")
    assert type(el).__slots__ == ()


# Integration: the tree builder automatically produces HTMLElement instances
# because it calls document.create_element() — no tree builder modifications needed.
def test_tree_builder_creates_html_elements() -> None:
    """Parsed HTML elements are HTMLElement instances (integration test)."""
    from aspose_html.tree import parse_html

    doc = parse_html("<div><p>text</p></div>")
    # document_element is <html>, which is also parsed via create_element()
    html_el = doc.document_element
    assert html_el is not None
    assert isinstance(html_el, HTMLElement)

    # Descend: body → div → p all go through create_element()
    div = doc.query_selector("div")
    assert div is not None
    assert isinstance(div, HTMLElement)

    p = doc.query_selector("p")
    assert p is not None
    assert isinstance(p, HTMLElement)


# ---------------------------------------------------------------------------
#  — HTMLElement IDL tail (, )
# AC-1 through AC-8
# ---------------------------------------------------------------------------

def test_htmlelement_spellcheck() -> None:
    """AC-1/AC-2: spellcheck default is True; setter sets the attribute to 'false'."""
    doc = Document()
    el = doc.create_element("div")
    # AC-1: default (absent) is True per WHATWG HTML §6.8.1
    assert el.spellcheck is True
    # AC-2: setter stores 'false' attribute
    el.spellcheck = False
    assert el.get_attribute("spellcheck") == "false"
    # Getting back should be False now
    assert el.spellcheck is False
    # spell_check alias still works and shares the same attribute
    el.spell_check = True
    assert el.spellcheck is True
    assert el.get_attribute("spellcheck") == "true"


def test_htmlelement_autocapitalize() -> None:
    """AC-3: autocapitalize returns '' when absent; setter round-trips."""
    doc = Document()
    el = doc.create_element("input")
    assert el.autocapitalize == ""
    el.autocapitalize = "sentences"
    assert el.get_attribute("autocapitalize") == "sentences"
    assert el.autocapitalize == "sentences"


def test_htmlelement_nonce() -> None:
    """AC-4: nonce returns '' when absent; setter round-trips."""
    doc = Document()
    el = doc.create_element("script")
    assert el.nonce == ""
    el.nonce = "abc123"
    assert el.nonce == "abc123"
    assert el.get_attribute("nonce") == "abc123"


def test_htmlelement_autofocus() -> None:
    """AC-5: autofocus returns False when absent; setter adds/removes boolean attribute."""
    doc = Document()
    el = doc.create_element("div")
    assert el.autofocus is False
    el.autofocus = True
    assert el.autofocus is True
    assert el.has_attribute("autofocus")
    el.autofocus = False
    assert el.autofocus is False
    assert not el.has_attribute("autofocus")


def test_htmlelement_access_key_label() -> None:
    """AC-6: access_key_label is always '' (read-only stub)."""
    doc = Document()
    el = doc.create_element("button")
    assert el.access_key_label == ""
    # Property is read-only — no setter should exist
    assert not hasattr(type(el).access_key_label, "fset") or \
        type(el).access_key_label.fset is None  # type: ignore[union-attr]


def test_htmlelement_input_mode() -> None:
    """AC-7: input_mode returns '' when absent; setter sets inputmode attribute."""
    doc = Document()
    el = doc.create_element("input")
    assert el.input_mode == ""
    el.input_mode = "numeric"
    assert el.get_attribute("inputmode") == "numeric"
    assert el.input_mode == "numeric"


def test_htmlelement_enter_key_hint() -> None:
    """AC-8: enter_key_hint returns '' when absent; setter sets enterkeyhint attribute."""
    doc = Document()
    el = doc.create_element("input")
    assert el.enter_key_hint == ""
    el.enter_key_hint = "search"
    assert el.get_attribute("enterkeyhint") == "search"
    assert el.enter_key_hint == "search"


# ---------------------------------------------------------------------------
#  — Popover API stubs ()
# ---------------------------------------------------------------------------


def test_htmlelement_show_popover() -> None:
    """AC-7a: show_popover executes without error."""
    doc = Document()
    el = doc.create_element("div")
    el.show_popover()


def test_htmlelement_hide_popover() -> None:
    """AC-7b: hide_popover executes without error."""
    doc = Document()
    el = doc.create_element("div")
    el.hide_popover()


def test_htmlelement_toggle_popover() -> None:
    """AC-8: toggle_popover returns False regardless of force argument."""
    doc = Document()
    el = doc.create_element("div")
    assert el.toggle_popover() is False
    assert el.toggle_popover(force=True) is False
    assert el.toggle_popover(force=False) is False
