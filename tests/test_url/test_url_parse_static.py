"""Tests for URL.parse() static method (WHATWG URL Standard §5.1)."""

import pytest

from aspose_html.url import URL


def test_parse_valid_absolute_url():
    result = URL.parse("https://example.com")
    assert result is not None
    assert result.href == "https://example.com"


def test_parse_invalid_url_returns_none():
    result = URL.parse("http://%")
    assert result is None


def test_parse_with_base():
    result = URL.parse("page", base="https://example.com/root/")
    assert result is not None
    assert result.href == "https://example.com/root/page"


def test_parse_none_base_with_relative_returns_none():
    # A bare percent-encoded-invalid string with no base raises URLParseError
    result = URL.parse("http://%25invalid%GG")
    assert result is None


def test_parse_returns_url_instance():
    result = URL.parse("https://example.com/path?q=1#frag")
    assert isinstance(result, URL)
    assert result.pathname == "/path"
    assert result.search == "?q=1"
    assert result.hash == "#frag"


def test_parse_vs_can_parse_consistency():
    inputs = [
        "https://example.com",
        "http://%",
        "ftp://files.example.org/resource",
        "mailto:user@example.com",
        "http://%invalid",
        "https://user:pass@host:8080/p?q=1#f",
    ]
    for s in inputs:
        assert (URL.parse(s) is not None) == URL.can_parse(s), (
            f"URL.parse and URL.can_parse disagree on {s!r}"
        )
