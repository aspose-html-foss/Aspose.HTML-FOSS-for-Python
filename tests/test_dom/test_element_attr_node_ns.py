"""Tests for BACK-191 — Element.get_attribute_node_ns / set_attribute_node_ns /
remove_attribute_node_ns (ADR-174, SPEC-099 Group B).
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, MutationObserver


_XLINK = "http://www.w3.org/1999/xlink"


def _doc_el() -> tuple[Document, object]:
    doc = Document()
    el = doc.create_element("svg")
    doc.append_child(el)
    return doc, el


# ---------------------------------------------------------------------------
# AC#1 — get_attribute_node_ns returns correct Attr after set_attribute_ns
# ---------------------------------------------------------------------------

def test_get_attribute_node_ns_found():
    doc, el = _doc_el()
    el.set_attribute_ns(_XLINK, "xlink:href", "#a")
    attr = el.get_attribute_node_ns(_XLINK, "href")
    assert attr is not None
    assert attr.value == "#a"
    assert attr.local_name == "href"
    assert attr._namespace_uri == _XLINK


# ---------------------------------------------------------------------------
# AC#2 — get_attribute_node_ns returns None when attribute absent
# ---------------------------------------------------------------------------

def test_get_attribute_node_ns_absent():
    _, el = _doc_el()
    assert el.get_attribute_node_ns(_XLINK, "href") is None


# ---------------------------------------------------------------------------
# AC#3 — empty string namespace treated same as None for lookup
# ---------------------------------------------------------------------------

def test_get_attribute_node_ns_empty_vs_none():
    doc = Document()
    el = doc.create_element("div")
    # Set a non-namespaced attribute via set_attribute_ns(None, ...)
    el.set_attribute_ns(None, "data-x", "1")
    # Should be found with both None and ""
    attr_none = el.get_attribute_node_ns(None, "data-x")
    attr_empty = el.get_attribute_node_ns("", "data-x")
    assert attr_none is not None
    assert attr_empty is not None
    assert attr_none is attr_empty


# ---------------------------------------------------------------------------
# AC#4 — set_attribute_node_ns insert returns None (no displaced attr)
# ---------------------------------------------------------------------------

def test_set_attribute_node_ns_insert_returns_none():
    doc, el = _doc_el()
    attr = doc.create_attribute_ns(_XLINK, "xlink:href")
    attr.value = "#b"
    displaced = el.set_attribute_node_ns(attr)
    assert displaced is None
    assert el.get_attribute_ns(_XLINK, "href") == "#b"
    assert attr._owner_element is el


# ---------------------------------------------------------------------------
# AC#5 — set_attribute_node_ns replace returns the displaced Attr
# ---------------------------------------------------------------------------

def test_set_attribute_node_ns_replace_returns_displaced():
    doc, el = _doc_el()
    # Insert first
    attr1 = doc.create_attribute_ns(_XLINK, "xlink:href")
    attr1.value = "#first"
    el.set_attribute_node_ns(attr1)

    # Replace with a new attr of same (ns, local_name)
    attr2 = doc.create_attribute_ns(_XLINK, "xlink:href")
    attr2.value = "#second"
    displaced = el.set_attribute_node_ns(attr2)

    assert displaced is attr1
    assert displaced._owner_element is None
    assert attr2._owner_element is el
    assert el.get_attribute_ns(_XLINK, "href") == "#second"


# ---------------------------------------------------------------------------
# AC#6 — set_attribute_node_ns raises WrongDocumentError when attr owned
#         by different element
# ---------------------------------------------------------------------------

def test_set_attribute_node_ns_wrong_document_error():
    from aspose_html.dom._exceptions import WrongDocumentError

    doc = Document()
    el1 = doc.create_element("svg")
    el2 = doc.create_element("svg")
    doc.append_child(el1)

    attr = doc.create_attribute_ns(_XLINK, "xlink:href")
    el1.set_attribute_node_ns(attr)  # attr is now owned by el1

    with pytest.raises(WrongDocumentError):
        el2.set_attribute_node_ns(attr)


# ---------------------------------------------------------------------------
# AC#7 — remove_attribute_node_ns returns the removed Attr with correct value
# ---------------------------------------------------------------------------

def test_remove_attribute_node_ns_found():
    doc, el = _doc_el()
    el.set_attribute_ns(_XLINK, "xlink:href", "#c")
    attr = el.remove_attribute_node_ns(_XLINK, "href")
    assert attr.value == "#c"
    assert attr._owner_element is None
    assert el.has_attribute_ns(_XLINK, "href") is False


# ---------------------------------------------------------------------------
# AC#8 — remove_attribute_node_ns raises NotFoundError when attribute absent
# ---------------------------------------------------------------------------

def test_remove_attribute_node_ns_not_found():
    from aspose_html.dom._exceptions import NotFoundError

    _, el = _doc_el()
    with pytest.raises(NotFoundError):
        el.remove_attribute_node_ns(_XLINK, "href")


# ---------------------------------------------------------------------------
# AC#9 — mutation observer records for set and remove
# ---------------------------------------------------------------------------

def test_set_attribute_node_ns_mutation_observer():
    doc, el = _doc_el()
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(el, attributes=True)

    attr = doc.create_attribute_ns(_XLINK, "xlink:href")
    attr.value = "#mo"
    el.set_attribute_node_ns(attr)

    assert len(got) == 1
    assert got[0].type == "attributes"


def test_remove_attribute_node_ns_mutation_observer():
    doc, el = _doc_el()
    el.set_attribute_ns(_XLINK, "xlink:href", "#x")

    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(el, attributes=True)

    el.remove_attribute_node_ns(_XLINK, "href")

    assert len(got) == 1
    assert got[0].type == "attributes"


# ---------------------------------------------------------------------------
# AC#10 — docstring examples are covered by pytest --doctest-modules
#          (tested implicitly; this test confirms the logic works end-to-end)
# ---------------------------------------------------------------------------

def test_docstring_scenario_get():
    doc = Document()
    el = doc.create_element("svg")
    el.set_attribute_ns(_XLINK, "xlink:href", "#a")
    attr = el.get_attribute_node_ns(_XLINK, "href")
    assert attr.value == "#a"


def test_docstring_scenario_set():
    doc = Document()
    el = doc.create_element("svg")
    attr = doc.create_attribute_ns(_XLINK, "xlink:href")
    attr.value = "#b"
    displaced = el.set_attribute_node_ns(attr)
    assert displaced is None
    assert el.get_attribute_ns(_XLINK, "href") == "#b"


def test_docstring_scenario_remove():
    doc = Document()
    el = doc.create_element("svg")
    el.set_attribute_ns(_XLINK, "xlink:href", "#c")
    attr = el.remove_attribute_node_ns(_XLINK, "href")
    assert attr.value == "#c"
    assert el.has_attribute_ns(_XLINK, "href") is False
