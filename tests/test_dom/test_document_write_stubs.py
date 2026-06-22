"""Tests for Document.open/close/write/writeln stubs (SPEC-093 / ADR-155)."""
import inspect

import pytest

from aspose_html.dom import Document
from aspose_html.dom._exceptions import NotSupportedError


def test_open_no_args_raises():
    with pytest.raises(NotSupportedError) as exc_info:
        Document().open()
    assert str(exc_info.value) == (
        "Document.open() is not supported in static document processing mode"
    )


def test_open_with_args_raises():
    with pytest.raises(NotSupportedError) as exc_info:
        Document().open("text/html", "replace")
    assert str(exc_info.value) == (
        "Document.open() is not supported in static document processing mode"
    )


def test_close_raises():
    with pytest.raises(NotSupportedError) as exc_info:
        Document().close()
    assert str(exc_info.value) == (
        "Document.close() is not supported in static document processing mode"
    )


def test_write_no_args_raises():
    with pytest.raises(NotSupportedError) as exc_info:
        Document().write()
    assert str(exc_info.value) == (
        "Document.write() is not supported; use HTMLDocument.parse() to create documents"
    )


def test_write_single_arg_raises():
    with pytest.raises(NotSupportedError) as exc_info:
        Document().write("<p>hello</p>")
    assert str(exc_info.value) == (
        "Document.write() is not supported; use HTMLDocument.parse() to create documents"
    )


def test_write_multiple_args_raises():
    with pytest.raises(NotSupportedError) as exc_info:
        Document().write("<p>", "hello", "</p>")
    assert str(exc_info.value) == (
        "Document.write() is not supported; use HTMLDocument.parse() to create documents"
    )


def test_writeln_no_args_raises():
    with pytest.raises(NotSupportedError) as exc_info:
        Document().writeln()
    assert str(exc_info.value) == (
        "Document.write() is not supported; use HTMLDocument.parse() to create documents"
    )


def test_writeln_single_arg_raises():
    with pytest.raises(NotSupportedError) as exc_info:
        Document().writeln("<p>hello</p>")
    assert str(exc_info.value) == (
        "Document.write() is not supported; use HTMLDocument.parse() to create documents"
    )


def test_signatures():
    """AC-8: All four methods have the correct parameter signatures."""
    open_sig = inspect.signature(Document.open)
    params = list(open_sig.parameters)
    assert params == ["self", "type", "replace"]
    assert open_sig.parameters["type"].default == "text/html"
    assert open_sig.parameters["replace"].default == ""

    close_sig = inspect.signature(Document.close)
    assert list(close_sig.parameters) == ["self"]

    write_sig = inspect.signature(Document.write)
    assert list(write_sig.parameters) == ["self", "text"]
    assert write_sig.parameters["text"].kind == inspect.Parameter.VAR_POSITIONAL

    writeln_sig = inspect.signature(Document.writeln)
    assert list(writeln_sig.parameters) == ["self", "text"]
    assert writeln_sig.parameters["text"].kind == inspect.Parameter.VAR_POSITIONAL


def test_slots_unchanged():
    """AC-11: Document.__slots__ does not contain new entries for these methods."""
    slots = set(Document.__slots__)
    for name in ("open", "close", "write", "writeln"):
        assert name not in slots
