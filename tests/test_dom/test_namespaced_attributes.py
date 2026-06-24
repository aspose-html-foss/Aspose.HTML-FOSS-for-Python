"""Tests for Element namespaced attribute methods —  / ."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, Attr

XLINK = "http://www.w3.org/1999/xlink"
XML_NS = "http://www.w3.org/XML/1998/namespace"


@pytest.fixture()
def doc() -> Document:
    return Document()


@pytest.fixture()
def el(doc: Document) -> object:
    return doc.create_element("svg")


# ---------------------------------------------------------------------------
# set_attribute_ns / get_attribute_ns
# ---------------------------------------------------------------------------

class TestSetAndGetAttributeNS:
    def test_set_and_get_attribute_ns(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#id")
        assert el.get_attribute_ns(XLINK, "href") == "#id"

    def test_get_attribute_ns_absent_returns_none(self, doc: Document, el: object) -> None:
        assert el.get_attribute_ns(XLINK, "href") is None

    def test_set_attribute_ns_updates_existing(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#first")
        el.set_attribute_ns(XLINK, "xlink:href", "#second")
        assert el.get_attribute_ns(XLINK, "href") == "#second"
        # Only one attribute should exist
        assert len(el.attributes) == 1

    def test_set_attribute_ns_no_prefix(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(None, "lang", "en")
        assert el.get_attribute_ns(None, "lang") == "en"

    def test_set_attribute_ns_different_namespaces(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#xlink")
        el.set_attribute_ns(XML_NS, "xml:lang", "en")
        assert el.get_attribute_ns(XLINK, "href") == "#xlink"
        assert el.get_attribute_ns(XML_NS, "lang") == "en"


# ---------------------------------------------------------------------------
# has_attribute_ns
# ---------------------------------------------------------------------------

class TestHasAttributeNS:
    def test_has_attribute_ns_true(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#id")
        assert el.has_attribute_ns(XLINK, "href") is True

    def test_has_attribute_ns_false(self, doc: Document, el: object) -> None:
        assert el.has_attribute_ns(XLINK, "href") is False

    def test_has_attribute_ns_wrong_namespace(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#id")
        assert el.has_attribute_ns("http://other.ns/", "href") is False


# ---------------------------------------------------------------------------
# remove_attribute_ns
# ---------------------------------------------------------------------------

class TestRemoveAttributeNS:
    def test_remove_attribute_ns(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#id")
        el.remove_attribute_ns(XLINK, "href")
        assert el.has_attribute_ns(XLINK, "href") is False

    def test_remove_attribute_ns_noop(self, doc: Document, el: object) -> None:
        # No exception when absent
        el.remove_attribute_ns(XLINK, "href")

    def test_remove_attribute_ns_clears_owner_element(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#id")
        attr = el.get_attribute_node("xlink:href")
        el.remove_attribute_ns(XLINK, "href")
        assert attr.owner_element is None


# ---------------------------------------------------------------------------
# Coexistence: namespaced and non-namespaced on same element
# ---------------------------------------------------------------------------

class TestNSAndNonNSCoexist:
    def test_coexist_without_interference(self, doc: Document, el: object) -> None:
        el.set_attribute("href", "plain")
        el.set_attribute_ns(XLINK, "xlink:href", "#ns")
        assert el.get_attribute("href") == "plain"
        assert el.get_attribute_ns(XLINK, "href") == "#ns"
        assert len(el.attributes) == 2

    def test_non_namespaced_get_unaffected(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#ns")
        # Non-namespaced lookup by qualified name still works
        assert el.get_attribute("xlink:href") == "#ns"
        # Non-namespaced lookup for a plain "href" still returns None
        assert el.get_attribute("href") is None


# ---------------------------------------------------------------------------
# Attr.namespace_uri and Attr.local_name properties
# ---------------------------------------------------------------------------

class TestAttrProperties:
    def test_attr_namespace_uri(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#id")
        attr = el.get_attribute_node("xlink:href")
        assert attr.namespace_uri == XLINK

    def test_attr_local_name_ns(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#id")
        attr = el.get_attribute_node("xlink:href")
        assert attr.local_name == "href"

    def test_attr_local_name_non_namespaced(self, doc: Document) -> None:
        el = doc.create_element("div")
        el.set_attribute("class", "x")
        attr = el.get_attribute_node("class")
        assert attr.local_name == "class"
        assert attr.namespace_uri is None

    def test_attr_namespace_uri_non_namespaced_is_none(self, doc: Document) -> None:
        el = doc.create_element("div")
        el.set_attribute("id", "main")
        attr = el.get_attribute_node("id")
        assert attr.namespace_uri is None


# ---------------------------------------------------------------------------
# Document.create_attribute_ns
# ---------------------------------------------------------------------------

class TestCreateAttributeNS:
    def test_create_attribute_ns(self, doc: Document) -> None:
        attr = doc.create_attribute_ns(XLINK, "xlink:href")
        assert attr.namespace_uri == XLINK
        assert attr.local_name == "href"
        assert attr.name == "xlink:href"
        assert attr.value == ""
        assert attr.owner_element is None

    def test_create_attribute_ns_no_prefix(self, doc: Document) -> None:
        attr = doc.create_attribute_ns(None, "lang")
        assert attr.namespace_uri is None
        assert attr.local_name == "lang"
        assert attr.name == "lang"

    def test_create_attribute_ns_owner_document(self, doc: Document) -> None:
        attr = doc.create_attribute_ns(XLINK, "xlink:title")
        assert attr.owner_document is doc


# ---------------------------------------------------------------------------
# Attr clone preserves namespace fields
# ---------------------------------------------------------------------------

class TestAttrClone:
    def test_attr_clone_preserves_namespace(self, doc: Document, el: object) -> None:
        el.set_attribute_ns(XLINK, "xlink:href", "#x")
        attr = el.get_attribute_node("xlink:href")
        clone = attr.clone_node()
        assert clone.namespace_uri == XLINK
        assert clone.local_name == "href"
        assert clone.value == "#x"
        assert clone.owner_element is None

    def test_non_ns_attr_clone_has_none_namespace(self, doc: Document) -> None:
        el = doc.create_element("div")
        el.set_attribute("data-x", "1")
        attr = el.get_attribute_node("data-x")
        clone = attr.clone_node()
        assert clone.namespace_uri is None
        assert clone.local_name == "data-x"


# ---------------------------------------------------------------------------
# is_equal_node with namespace fields
# ---------------------------------------------------------------------------

class TestAttrIsEqualNodeNS:
    def test_equal_ns_attrs(self, doc: Document) -> None:
        a = doc.create_attribute_ns(XLINK, "xlink:href")
        a.value = "#x"
        b = doc.create_attribute_ns(XLINK, "xlink:href")
        b.value = "#x"
        assert a.is_equal_node(b)

    def test_different_namespace_not_equal(self, doc: Document) -> None:
        a = doc.create_attribute_ns(XLINK, "xlink:href")
        a.value = "#x"
        b = doc.create_attribute_ns("http://other.ns/", "xlink:href")
        b.value = "#x"
        assert not a.is_equal_node(b)

    def test_different_local_name_not_equal(self, doc: Document) -> None:
        a = doc.create_attribute_ns(XLINK, "xlink:href")
        a.value = "#x"
        b = doc.create_attribute_ns(XLINK, "xlink:title")
        b.value = "#x"
        assert not a.is_equal_node(b)

    def test_equal_non_namespaced_attrs_unchanged(self, doc: Document) -> None:
        e1 = doc.create_element("div")
        e2 = doc.create_element("div")
        e1.set_attribute("data-x", "1")
        e2.set_attribute("data-x", "1")
        a = e1.get_attribute_node("data-x")
        b = e2.get_attribute_node("data-x")
        assert a.is_equal_node(b)
