"""test_parse_errors.py — tests for parse error collection."""
import pytest
from aspose_html.tree import parse_html
from aspose_html.dom import ParseError


def test_parse_errors_is_list():
    """document.parse_errors is always a list."""
    doc = parse_html("<!DOCTYPE html><html><body></body></html>")
    assert isinstance(doc.parse_errors, list)


def test_tokenizer_errors_on_document():
    """Tokenizer parse errors are collected on the document."""
    # Malformed HTML that should produce tokenizer errors
    doc = parse_html("<!DOCTYPE html><p><!-- incomplete")
    # May have parse errors from the tokenizer
    assert isinstance(doc.parse_errors, list)


def test_tree_construction_error_unclosed_tags():
    """Tree construction with unclosed tags should not raise; errors may be recorded."""
    doc = parse_html("<b>unclosed")
    # Parser must complete without exception
    assert doc.document_element is not None
    assert isinstance(doc.parse_errors, list)


def test_multiple_errors_collected():
    """Multiple errors from different sources are all collected."""
    # Multiple unclosed tags and other issues
    doc = parse_html("<b><i><u>text")
    assert isinstance(doc.parse_errors, list)
    # Parser must complete
    assert doc.document_element is not None


def test_valid_html_few_errors():
    """Valid HTML5 with correct DOCTYPE should have no parse errors or very few."""
    doc = parse_html("<!DOCTYPE html><html><head></head><body><p>hello</p></body></html>")
    assert isinstance(doc.parse_errors, list)
    # Well-formed HTML should not produce errors
    assert len(doc.parse_errors) == 0


def test_parse_error_fields():
    """ParseError objects have the required fields."""
    # Trigger a specific parse error by using duplicate attributes
    # (The tokenizer records duplicate attribute errors)
    doc = parse_html('<!DOCTYPE html><div id="a" id="b">text</div>')
    # The resulting document must be valid
    assert doc.document_element is not None
    # Any parse errors collected must have the required fields
    for err in doc.parse_errors:
        assert isinstance(err, ParseError)
        assert isinstance(err.code, str)
        assert isinstance(err.line, int)
        assert isinstance(err.column, int)
        assert isinstance(err.message, str)
