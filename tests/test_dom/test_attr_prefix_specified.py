"""Tests for Attr.prefix and Attr.specified (WHATWG DOM §4.6, BACK-295)."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document

XLINK_NS = "http://www.w3.org/1999/xlink"
MATHML_NS = "http://www.w3.org/1998/Math/MathML"


def _make_doc() -> Document:
    return Document()


def test_attr_prefix_namespaced() -> None:
    """set_attribute_ns with xlink:href → prefix == 'xlink'."""
    doc = _make_doc()
    el = doc.create_element("svg")
    el.set_attribute_ns(XLINK_NS, "xlink:href", "#foo")
    attr = el.get_attribute_node("xlink:href")
    assert attr is not None
    assert attr.prefix == "xlink"


def test_attr_prefix_plain() -> None:
    """Plain (non-namespaced) attribute → prefix is None."""
    doc = _make_doc()
    el = doc.create_element("div")
    el.set_attribute("class", "foo")
    attr = el.get_attribute_node("class")
    assert attr is not None
    assert attr.prefix is None


def test_attr_specified_always_true() -> None:
    """Attr.specified returns True for both namespaced and plain attributes."""
    doc = _make_doc()
    el = doc.create_element("div")
    el.set_attribute("id", "main")
    plain_attr = el.get_attribute_node("id")
    assert plain_attr is not None
    assert plain_attr.specified is True

    el.set_attribute_ns(XLINK_NS, "xlink:href", "#foo")
    ns_attr = el.get_attribute_node("xlink:href")
    assert ns_attr is not None
    assert ns_attr.specified is True


def test_attr_local_name_namespaced() -> None:
    """Namespaced attr local_name returns only the local part, not the full qualified name."""
    doc = _make_doc()
    el = doc.create_element("svg")
    el.set_attribute_ns(XLINK_NS, "xlink:href", "#bar")
    attr = el.get_attribute_node("xlink:href")
    assert attr is not None
    assert attr.local_name == "href", f"Expected 'href', got {attr.local_name!r}"


def test_attr_local_name_plain() -> None:
    """Plain attribute local_name returns the full attribute name."""
    doc = _make_doc()
    el = doc.create_element("div")
    el.set_attribute("class", "box")
    attr = el.get_attribute_node("class")
    assert attr is not None
    assert attr.local_name == "class"


def test_attr_prefix_mathml() -> None:
    """MathML namespaced attribute m:type → prefix == 'm'."""
    doc = _make_doc()
    el = doc.create_element("math")
    el.set_attribute_ns(MATHML_NS, "m:type", "integer")
    attr = el.get_attribute_node("m:type")
    assert attr is not None
    assert attr.prefix == "m"
