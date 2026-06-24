"""Tests for Document convenience properties: head, body, title.

Covers  ().
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, Element, NodeType
from aspose_html.html_document import HTMLDocument


@pytest.fixture
def doc() -> Document:
    return Document()


@pytest.fixture
def doc_with_html(doc: Document):
    """Document with a bare <html> root element, no children yet."""
    html = doc.create_element("html")
    doc.append_child(html)
    return doc, html


# ------------------------------------------------------------------
# Document.head
# ------------------------------------------------------------------


def test_head_returns_none_when_no_document_element(doc: Document) -> None:
    """AC-1: fresh document with no children returns None for head."""
    assert doc.head is None


def test_head_returns_none_when_no_head_child(doc_with_html) -> None:
    """AC-1: document element exists but has no <head> child."""
    doc, html = doc_with_html
    # append a body but no head
    body = doc.create_element("body")
    html.append_child(body)
    assert doc.head is None


def test_head_returns_head_element(doc_with_html) -> None:
    """AC-1: returns the <head> element child of document_element."""
    doc, html = doc_with_html
    head = doc.create_element("head")
    html.append_child(head)
    assert doc.head is head


def test_head_returns_first_head_element(doc_with_html) -> None:
    """head returns the first matching child when multiple head-like nodes exist."""
    doc, html = doc_with_html
    head1 = doc.create_element("head")
    head2 = doc.create_element("head")
    html.append_child(head1)
    html.append_child(head2)
    assert doc.head is head1


# ------------------------------------------------------------------
# Document.body
# ------------------------------------------------------------------


def test_body_returns_none_when_no_document_element(doc: Document) -> None:
    """AC-2: fresh document with no children returns None for body."""
    assert doc.body is None


def test_body_returns_none_when_no_body_child(doc_with_html) -> None:
    """AC-2: document element exists but has no <body> child."""
    doc, html = doc_with_html
    head = doc.create_element("head")
    html.append_child(head)
    assert doc.body is None


def test_body_returns_body_element(doc_with_html) -> None:
    """AC-2: returns the <body> element child of document_element."""
    doc, html = doc_with_html
    body = doc.create_element("body")
    html.append_child(body)
    assert doc.body is body


def test_body_returns_first_body_element(doc_with_html) -> None:
    """body returns the first matching child when multiple body elements exist."""
    doc, html = doc_with_html
    body1 = doc.create_element("body")
    body2 = doc.create_element("body")
    html.append_child(body1)
    html.append_child(body2)
    assert doc.body is body1


# ------------------------------------------------------------------
# Document.title — getter
# ------------------------------------------------------------------


def test_title_getter_returns_empty_when_no_head(doc: Document) -> None:
    """AC-3: no head element — title getter returns empty string."""
    assert doc.title == ""


def test_title_getter_returns_empty_when_no_title_element(doc_with_html) -> None:
    """AC-3: head exists but has no <title> child — returns empty string."""
    doc, html = doc_with_html
    head = doc.create_element("head")
    html.append_child(head)
    assert doc.title == ""


def test_title_getter_returns_text_content_of_title(doc_with_html) -> None:
    """AC-3: returns the text_content of the first <title> in <head>."""
    doc, html = doc_with_html
    head = doc.create_element("head")
    title_el = doc.create_element("title")
    title_el.text_content = "My Page"
    html.append_child(head)
    head.append_child(title_el)
    assert doc.title == "My Page"


def test_title_getter_returns_first_title_content(doc_with_html) -> None:
    """title getter uses the first <title> child even when multiple exist."""
    doc, html = doc_with_html
    head = doc.create_element("head")
    t1 = doc.create_element("title")
    t1.text_content = "First"
    t2 = doc.create_element("title")
    t2.text_content = "Second"
    html.append_child(head)
    head.append_child(t1)
    head.append_child(t2)
    assert doc.title == "First"


def test_title_getter_returns_empty_string_for_empty_title(doc_with_html) -> None:
    """title getter returns '' (not None) when <title> element has no text."""
    doc, html = doc_with_html
    head = doc.create_element("head")
    title_el = doc.create_element("title")
    html.append_child(head)
    head.append_child(title_el)
    result = doc.title
    assert result == ""
    assert isinstance(result, str)


# ------------------------------------------------------------------
# Document.title — setter
# ------------------------------------------------------------------


def test_title_setter_noop_when_no_head(doc: Document) -> None:
    """AC-4: setter is a no-op when head is absent — no exception raised."""
    doc.title = "ignored"
    assert doc.head is None


def test_title_setter_creates_title_when_absent(doc_with_html) -> None:
    """AC-4: creates a new <title> element when none exists."""
    doc, html = doc_with_html
    head = doc.create_element("head")
    html.append_child(head)

    doc.title = "New"

    assert doc.title == "New"
    # Verify the <title> child was physically appended to head
    title_children = [
        c for c in head._children
        if c._node_type == NodeType.ELEMENT_NODE and c._local_name == "title"
    ]
    assert len(title_children) == 1
    assert title_children[0].text_content == "New"


def test_title_setter_updates_existing_title(doc_with_html) -> None:
    """AC-4: updates text_content of the existing <title> in place."""
    doc, html = doc_with_html
    head = doc.create_element("head")
    title_el = doc.create_element("title")
    title_el.text_content = "Old"
    html.append_child(head)
    head.append_child(title_el)

    doc.title = "New"

    assert doc.title == "New"
    # Must not have created a second <title> element
    title_children = [
        c for c in head._children
        if c._node_type == NodeType.ELEMENT_NODE and c._local_name == "title"
    ]
    assert len(title_children) == 1


def test_title_setter_does_not_modify_slots() -> None:
    """AC-6: Document.__slots__ must not contain new entries for these properties."""
    assert set(Document.__slots__) == {
        "_compat_mode",
        "_parse_errors",
        "_id_map",
        "_url",
        "_mutation_signal",
        "_selection",
        "_character_set",   # added by  ()
        "_style_epoch",     # added by  (, M7.1 style cache)
        "_style_cache",     # added by  (, M7.1 style cache)
    }


def test_document_url_defaults_to_about_blank() -> None:
    assert Document().url == "about:blank"


def test_document_base_uri_defaults_to_about_blank() -> None:
    assert Document().base_uri == "about:blank"


def test_parse_sets_document_url_from_base_url() -> None:
    doc = HTMLDocument.parse("<html></html>", base_url="https://example.com/a/")
    assert doc.url == "https://example.com/a/"


def test_document_base_uri_matches_url_after_parse() -> None:
    doc = HTMLDocument.parse("<html></html>", base_url="https://example.com/a/")
    assert doc.base_uri == doc.url
