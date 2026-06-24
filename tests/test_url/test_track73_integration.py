""" integration matrix — WHATWG URL Standard surface completeness.

Covers all  FRs across  (URL.parse),  (URLSearchParams
tail), and  (Document.document_uri).
"""
import doctest

import pytest

from aspose_html.dom import Document
from aspose_html.url import URL, URLSearchParams


# ---------------------------------------------------------------------------
# Group A: URL.parse() success paths
# ---------------------------------------------------------------------------

def test_url_parse_absolute_returns_url_object():
    result = URL.parse("https://example.com/path")
    assert result is not None
    assert isinstance(result, URL)


def test_url_parse_href_matches_input():
    result = URL.parse("https://example.com/")
    assert result is not None
    assert result.href == "https://example.com/"


def test_url_parse_with_base_resolves():
    result = URL.parse("page", base="https://example.com/root/")
    assert result is not None
    assert result.href == "https://example.com/root/page"


def test_url_parse_with_url_base_resolves():
    base = URL("https://example.com/dir/")
    result = URL.parse("sub", base=base)
    assert result is not None
    assert result.href == "https://example.com/dir/sub"


def test_url_parse_absolute_ignores_base():
    result = URL.parse("https://other.com/", base="https://example.com/")
    assert result is not None
    assert result.hostname == "other.com"


# ---------------------------------------------------------------------------
# Group B: URL.parse() failure paths
# ---------------------------------------------------------------------------

def test_url_parse_invalid_returns_none():
    result = URL.parse("http://%")
    assert result is None


def test_url_parse_malformed_host_returns_none():
    # Malformed percent-encoding in host always fails
    result = URL.parse("http://exa%mple.com/")
    assert result is None


def test_url_parse_empty_string_returns_none():
    result = URL.parse("")
    assert result is None


def test_url_parse_never_raises():
    # URL.parse must never raise URLParseError regardless of input
    from aspose_html.url._url import URLParseError
    try:
        result = URL.parse("\x00\x01\x02bad")
        # result may be None or a URL — both are acceptable
        assert result is None or isinstance(result, URL)
    except URLParseError:
        pytest.fail("URL.parse() raised URLParseError — it must return None instead")


# ---------------------------------------------------------------------------
# Group C: URL.parse() vs can_parse() consistency
# ---------------------------------------------------------------------------

def test_url_parse_consistent_with_can_parse_valid():
    inputs = [
        "https://example.com",
        "http://user:pass@host/path?q=1#frag",
        ("page", "https://example.com/root/"),
    ]
    for item in inputs:
        if isinstance(item, tuple):
            url_str, base = item
            parsed = URL.parse(url_str, base=base)
            can = URL.can_parse(url_str, base=base)
        else:
            parsed = URL.parse(item)
            can = URL.can_parse(item)
        assert (parsed is not None) == can, f"Mismatch for {item!r}: parse={parsed}, can_parse={can}"


def test_url_parse_consistent_with_can_parse_invalid():
    invalids = ["http://%", "", "http://exa%mple.com/"]
    for bad in invalids:
        parsed = URL.parse(bad)
        can = URL.can_parse(bad)
        assert (parsed is not None) == can, (
            f"Mismatch for {bad!r}: parse={'ok' if parsed else 'None'}, can_parse={can}"
        )


# ---------------------------------------------------------------------------
# Group D: URLSearchParams.size
# ---------------------------------------------------------------------------

def test_size_empty_params():
    p = URLSearchParams()
    assert p.size == 0


def test_size_single_pair():
    p = URLSearchParams("a=1")
    assert p.size == 1


def test_size_multiple_pairs():
    p = URLSearchParams("a=1&b=2&c=3")
    assert p.size == 3


def test_size_duplicate_names():
    p = URLSearchParams("a=1&a=2")
    assert p.size == 2


def test_size_after_append():
    p = URLSearchParams("a=1")
    p.append("b", "2")
    assert p.size == 2


def test_size_after_delete_one_arg():
    p = URLSearchParams("a=1&a=2&b=3")
    p.delete("a")
    assert p.size == 1


# ---------------------------------------------------------------------------
# Group E: URLSearchParams.has(name, value) — two-argument form
# ---------------------------------------------------------------------------

def test_has_two_arg_exact_match():
    p = URLSearchParams("a=1&a=2&b=3")
    assert p.has("a", "1") is True


def test_has_two_arg_value_mismatch():
    p = URLSearchParams("a=1&b=2")
    assert p.has("a", "9") is False


def test_has_two_arg_name_mismatch():
    p = URLSearchParams("a=1")
    assert p.has("z", "1") is False


def test_has_one_arg_compatibility():
    p = URLSearchParams("a=1&b=2")
    assert p.has("a") is True
    assert p.has("missing") is False


def test_has_two_arg_second_occurrence():
    p = URLSearchParams("a=1&a=2")
    assert p.has("a", "2") is True


# ---------------------------------------------------------------------------
# Group F: URLSearchParams.delete(name, value) — two-argument form
# ---------------------------------------------------------------------------

def test_delete_two_arg_removes_only_matched_pair():
    p = URLSearchParams("a=1&a=2&b=3")
    p.delete("a", "1")
    assert str(p) == "a=2&b=3"


def test_delete_two_arg_leaves_other_values():
    p = URLSearchParams("x=foo&x=bar&x=baz")
    p.delete("x", "bar")
    result = list(p.entries())
    assert result == [("x", "foo"), ("x", "baz")]


def test_delete_one_arg_removes_all_with_name():
    p = URLSearchParams("a=1&a=2&b=3")
    p.delete("a")
    assert str(p) == "b=3"


def test_delete_two_arg_noop_on_value_mismatch():
    p = URLSearchParams("a=1&b=2")
    p.delete("a", "9")
    assert p.size == 2


def test_delete_two_arg_size_decrements():
    p = URLSearchParams("a=1&a=2")
    p.delete("a", "1")
    assert p.size == 1


# ---------------------------------------------------------------------------
# Group G: URLSearchParams.entries()
# ---------------------------------------------------------------------------

def test_entries_empty():
    p = URLSearchParams()
    assert list(p.entries()) == []


def test_entries_returns_all_pairs():
    p = URLSearchParams("a=1&b=2&c=3")
    assert list(p.entries()) == [("a", "1"), ("b", "2"), ("c", "3")]


def test_entries_order_preserved():
    p = URLSearchParams("z=last&a=first")
    pairs = list(p.entries())
    assert pairs[0] == ("z", "last")
    assert pairs[1] == ("a", "first")


def test_entries_after_mutation():
    p = URLSearchParams("a=1")
    p.append("b", "2")
    assert list(p.entries()) == [("a", "1"), ("b", "2")]


# ---------------------------------------------------------------------------
# Group H: Document.document_uri
# ---------------------------------------------------------------------------

def test_document_uri_exists():
    doc = Document()
    assert hasattr(doc, "document_uri")


def test_document_uri_matches_url():
    doc = Document()
    assert doc.document_uri == doc.url


def test_document_uri_returns_string():
    doc = Document()
    assert isinstance(doc.document_uri, str)


def test_document_uri_default_value():
    doc = Document()
    assert doc.document_uri == "about:blank"


def test_document_uri_reflects_url_mutation():
    doc = Document()
    doc._url = "https://example.com/"
    assert doc.document_uri == "https://example.com/"
    assert doc.document_uri == doc.url


# ---------------------------------------------------------------------------
# Group I: Doctest sweep
# ---------------------------------------------------------------------------

def test_url_module_doctests_pass():
    import aspose_html.url._url as mod
    results = doctest.testmod(mod, verbose=False)
    assert results.failed == 0, f"{results.failed} doctest(s) failed in url/_url.py"


def test_search_params_doctests_pass():
    import aspose_html.url._search_params as mod
    results = doctest.testmod(mod, verbose=False)
    assert results.failed == 0, f"{results.failed} doctest(s) failed in url/_search_params.py"


def test_document_uri_doctest_passes():
    import aspose_html.dom._document as mod
    doc = Document()
    # Direct inline verification matching the docstring example
    assert doc.document_uri == doc.url
    assert doc.document_uri == "about:blank"
    # Sweep the module doctests as a safety net
    results = doctest.testmod(mod, verbose=False)
    assert results.failed == 0, f"{results.failed} doctest(s) failed in dom/_document.py"
