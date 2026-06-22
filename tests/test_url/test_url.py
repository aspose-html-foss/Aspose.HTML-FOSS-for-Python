import pytest

from aspose_html import URL, URLParseError


def test_url_roundtrip_and_components():
    u = URL("https://example.com:8443/p?q=1#h")
    assert u.href == "https://example.com:8443/p?q=1#h"
    assert u.protocol == "https:"
    assert u.hostname == "example.com"
    assert u.port == "8443"
    assert u.pathname == "/p"
    assert u.search == "?q=1"
    assert u.hash == "#h"


def test_url_with_base_and_path_setter():
    u = URL("page", base="https://example.com/root/")
    assert u.href == "https://example.com/root/page"
    u.pathname = "/new"
    assert u.href == "https://example.com/new"


def test_url_invalid_percent_raises():
    with pytest.raises(URLParseError):
        URL("http://%")


def test_url_userinfo_and_host_component_setters() -> None:
    u = URL("https://example.com/path")
    u.username = "alice"
    u.password = "secret"
    assert u.href.startswith("https://alice:secret@example.com")

    u.host = "example.org:8443"
    assert u.hostname == "example.org"
    assert u.port == "8443"

    u.hostname = "www.example.net"
    assert u.hostname == "www.example.net"
    u.port = "9443"
    assert u.port == "9443"


def test_url_protocol_and_hash_setters_and_identity_dunders() -> None:
    u = URL("https://example.com/p?q=1")
    u.protocol = "HTTP:"
    u.hash = "frag"
    assert u.protocol == "http:"
    assert u.hash == "#frag"

    v = URL(str(u))
    assert repr(u).startswith("URL(")
    assert u == v
    assert hash(u) == hash(v)


def test_url_dot_segment_path_canonicalization() -> None:
    u = URL("https://example.com/a/./b/../c")
    assert u.href == "https://example.com/a/c"

    u.pathname = "/x/./y/../z"
    assert u.href == "https://example.com/x/z"


def test_url_empty_query_and_fragment_elision() -> None:
    u = URL("https://example.com/p?")
    assert u.href == "https://example.com/p"

    u.search = ""
    assert u.href == "https://example.com/p"

    u.href = "https://example.com/p#"
    assert u.href == "https://example.com/p"

    u.hash = ""
    assert u.href == "https://example.com/p"


def test_url_repeated_assignment_idempotence() -> None:
    u = URL("https://example.com/a/./b?q=1#frag")
    first = u.href

    u.pathname = "/a/b"
    second = u.href
    u.pathname = "/a/b"
    assert u.href == second

    u.search = ""
    after_search_clear = u.href
    u.search = ""
    assert u.href == after_search_clear

    u.hash = ""
    after_hash_clear = u.href
    u.hash = ""
    assert u.href == after_hash_clear

    u.href = u.href
    assert u.href == after_hash_clear
    assert first == "https://example.com/a/b?q=1#frag"


def test_url_search_params_live_binding_deterministic_roundtrip() -> None:
    u = URL("https://example.com/p?q=hello%20world&x=%2B")
    params = u.search_params

    assert str(params) == "q=hello+world&x=%2B"
    params.append("q", "tail")
    assert u.search == "?q=hello+world&x=%2B&q=tail"
    assert u.href == "https://example.com/p?q=hello+world&x=%2B&q=tail"

    u.search = "?x=%2B&q=hello+world"
    assert str(params) == "x=%2B&q=hello+world"

    params.set("q", "hello world")
    assert u.search == "?x=%2B&q=hello+world"
    assert u.href == "https://example.com/p?x=%2B&q=hello+world"


def test_location_history_url_integration_canonical_href_stability_cycle() -> None:
    u = URL("https://example.com/a/./b/../c?q=1#")
    assert u.href == "https://example.com/a/c?q=1"

    u.pathname = "/a/./c"
    assert u.href == "https://example.com/a/c?q=1"

    u.search = ""
    assert u.href == "https://example.com/a/c"

    stable = u.href
    u.href = stable
    u.pathname = "/a/c"
    u.hash = ""
    assert u.href == stable


def test_url_can_parse_valid_absolute_url() -> None:
    assert URL.can_parse("https://example.com") is True


def test_url_can_parse_invalid_input_returns_false() -> None:
    assert URL.can_parse("http://%") is False


def test_url_can_parse_relative_with_valid_base_returns_true() -> None:
    assert URL.can_parse("page", base="https://example.com/root/") is True


def test_url_can_parse_relative_without_base_follows_current_policy() -> None:
    assert URL.can_parse("page") is True


def test_url_can_parse_accepts_base_url_instance() -> None:
    base = URL("https://example.com/root/")
    assert URL.can_parse("child", base=base) is True
