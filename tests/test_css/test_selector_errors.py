"""Regression tests for selector error contracts in query-selector APIs."""

from __future__ import annotations

import pytest

from aspose_html.dom import Document, Element


def _build_tree() -> tuple[Document, Element]:
    doc = Document()
    html = doc.create_element("html")
    body = doc.create_element("body")
    div = doc.create_element("div")
    div.set_attribute("id", "target")
    doc.append_child(html)
    html.append_child(body)
    body.append_child(div)
    return doc, body


@pytest.mark.parametrize("selector", ["div::before", ":before"])
def test_query_selector_pseudo_element_raises_syntax_error(selector: str) -> None:
    """Document query_selector/query_selector_all normalize pseudo-elements to SyntaxError."""
    doc, _ = _build_tree()

    with pytest.raises(SyntaxError):
        doc.query_selector(selector)
    with pytest.raises(SyntaxError):
        doc.query_selector_all(selector)


@pytest.mark.parametrize("selector", ["div::before", ":before"])
def test_element_query_selector_pseudo_element_raises_syntax_error(selector: str) -> None:
    """Element query_selector/query_selector_all normalize pseudo-elements to SyntaxError."""
    _, body = _build_tree()

    with pytest.raises(SyntaxError):
        body.query_selector(selector)
    with pytest.raises(SyntaxError):
        body.query_selector_all(selector)


def test_valid_selector_still_matches() -> None:
    """Valid selectors remain unaffected by pseudo-element error normalization."""
    doc, body = _build_tree()

    assert doc.query_selector("div") is not None
    assert len(doc.query_selector_all("div")) == 1
    assert body.query_selector("#target") is not None
    assert len(body.query_selector_all("div")) == 1
