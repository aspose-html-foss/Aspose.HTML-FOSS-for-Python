"""Tests for DOMImplementation legacy feature probes."""

from __future__ import annotations

import pytest

from aspose_html.serialiser import serialise
from aspose_html.dom import DOMImplementation, Document, DocumentType
from aspose_html.dom._exceptions import InvalidCharacterError, WrongDocumentError


def test_has_feature_known_features_return_true_for_supported_versions() -> None:
    """Known legacy features return True for baseline versions."""
    impl = DOMImplementation()

    assert impl.has_feature("Core") is True
    assert impl.has_feature("XML", "1.0") is True
    assert impl.has_feature("html", "2.0") is True
    assert impl.has_feature("xhtml", "3.0") is True


def test_has_feature_unknown_feature_returns_false() -> None:
    """Unknown features return False."""
    impl = DOMImplementation()

    assert impl.has_feature("Unknown") is False
    assert impl.has_feature("Unknown", "1.0") is False


def test_has_feature_version_handling_is_deterministic() -> None:
    """Version handling is deterministic for known features."""
    impl = DOMImplementation()

    assert impl.has_feature("Core", None) is True
    assert impl.has_feature("Core", "") is True
    assert impl.has_feature("Core", "9.9") is False


def test_get_feature_supported_probe_returns_self() -> None:
    impl = DOMImplementation()

    assert impl.get_feature("Core") is impl
    assert impl.get_feature("XML", "3.0") is impl


def test_get_feature_unsupported_probe_returns_none() -> None:
    impl = DOMImplementation()

    assert impl.get_feature("Unknown") is None
    assert impl.get_feature("Core", "9.9") is None


def test_get_feature_does_not_change_has_feature_semantics() -> None:
    impl = DOMImplementation()

    before_true = impl.has_feature("html", "2.0")
    before_false = impl.has_feature("html", "9.9")
    _ = impl.get_feature("html", "2.0")
    _ = impl.get_feature("html", "9.9")

    assert impl.has_feature("html", "2.0") is before_true
    assert impl.has_feature("html", "9.9") is before_false


@pytest.mark.parametrize(
    ("feature", "version"),
    [
        ("Core", None),
        ("core", ""),
        ("XML", "3.0"),
        ("Unknown", None),
        ("xhtml", "9.9"),
    ],
)
def test_has_feature_get_feature_interop_contract(
    feature: str,
    version: str | None,
) -> None:
    impl = DOMImplementation()

    supported = impl.has_feature(feature, version)
    feature_obj = impl.get_feature(feature, version)

    if supported:
        assert feature_obj is impl
    else:
        assert feature_obj is None


def test_create_document_type_returns_expected_values() -> None:
    """create_document_type returns a detached DocumentType with values set."""
    impl = DOMImplementation()
    doctype = impl.create_document_type("html", "-//W3C//DTD HTML 5//EN", "about:legacy-compat")

    assert isinstance(doctype, DocumentType)
    assert doctype.name == "html"
    assert doctype.public_id == "-//W3C//DTD HTML 5//EN"
    assert doctype.system_id == "about:legacy-compat"
    assert doctype.parent_node is None


def test_create_document_type_rejects_invalid_qualified_name() -> None:
    """create_document_type rejects empty and whitespace-containing names."""
    impl = DOMImplementation()

    with pytest.raises(InvalidCharacterError):
        impl.create_document_type("", "", "")
    with pytest.raises(InvalidCharacterError):
        impl.create_document_type("html doc", "", "")


def test_create_document_wires_doctype_and_root_with_ownership() -> None:
    """create_document wires optional doctype and root into a new document."""
    impl = DOMImplementation()
    doctype = impl.create_document_type("html", "", "")

    doc = impl.create_document("http://www.w3.org/1999/xhtml", "html", doctype)

    assert isinstance(doc, Document)
    assert doc.document_type is doctype
    assert doc.document_type.owner_document is doc
    assert doc.document_element is not None
    assert doc.document_element.owner_document is doc
    assert doc.document_element.tag_name == "HTML"


def test_create_document_with_foreign_doctype_raises_wrong_document_error() -> None:
    """create_document rejects a doctype already owned by a different document."""
    impl = DOMImplementation()
    foreign = Document()
    doctype = DocumentType("html", owner_document=foreign)

    with pytest.raises(WrongDocumentError):
        impl.create_document("http://www.w3.org/1999/xhtml", "html", doctype)


def test_create_html_document_builds_baseline_structure() -> None:
    impl = DOMImplementation()

    doc = impl.create_html_document()

    assert isinstance(doc, Document)
    assert doc.document_element is not None
    assert doc.document_element.tag_name == "HTML"
    assert doc.document_element.owner_document is doc
    assert doc.head is not None
    assert doc.head.parent_node is doc.document_element
    assert doc.body is not None
    assert doc.body.parent_node is doc.document_element


def test_create_html_document_with_none_or_empty_title_adds_no_title_node() -> None:
    impl = DOMImplementation()

    doc_none = impl.create_html_document(None)
    doc_empty = impl.create_html_document("")

    assert doc_none.title == ""
    assert doc_empty.title == ""
    assert doc_none.head is not None
    assert doc_empty.head is not None
    assert len(list(doc_none.head.get_elements_by_tag_name("title"))) == 0
    assert len(list(doc_empty.head.get_elements_by_tag_name("title"))) == 0


def test_create_html_document_with_non_empty_title_creates_single_title() -> None:
    impl = DOMImplementation()

    doc = impl.create_html_document("Hello world")

    assert doc.title == "Hello world"
    assert doc.head is not None
    titles = list(doc.head.get_elements_by_tag_name("title"))
    assert len(titles) == 1
    assert titles[0].text_content == "Hello world"


def test_create_html_document_returns_new_document_each_call() -> None:
    impl = DOMImplementation()

    first = impl.create_html_document("A")
    second = impl.create_html_document("B")

    assert first is not second
    assert first.document_element is not second.document_element
    assert first.title == "A"
    assert second.title == "B"


def test_create_html_document_is_serialisable_with_expected_baseline_markup() -> None:
    impl = DOMImplementation()

    doc = impl.create_html_document("Hello")

    html = serialise(doc)
    assert html.startswith("<html><head><title>Hello</title></head><body></body></html>")


def test_create_html_document_does_not_regress_legacy_factories() -> None:
    impl = DOMImplementation()

    html_doc = impl.create_html_document("Title")
    doctype = impl.create_document_type("html", "", "")
    legacy_doc = impl.create_document("http://www.w3.org/1999/xhtml", "html", doctype)

    assert html_doc.title == "Title"
    assert legacy_doc.document_type is doctype
    assert legacy_doc.document_element is not None
    assert legacy_doc.document_element.tag_name == "HTML"
