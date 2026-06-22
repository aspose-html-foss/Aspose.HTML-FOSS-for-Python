from aspose_html import URLSearchParams, URL


def test_search_params_get_all_and_len():
    p = URLSearchParams("a=1&b=2&a=3")
    assert p.get_all("a") == ["1", "3"]
    assert len(p) == 3


def test_search_params_set_and_sort():
    p = URLSearchParams([("b", "2"), ("a", "1"), ("b", "3")])
    p.set("b", "9")
    assert p.get_all("b") == ["9"]
    p.sort()
    assert list(p.keys()) == ["a", "b"]


def test_live_binding_to_url_search():
    u = URL("https://example.com/?a=1")
    u.search_params.append("b", "2")
    assert "b=2" in u.search


def test_duplicate_ordering_roundtrip_across_mutations() -> None:
    p = URLSearchParams("a=1&b=2&a=3")
    assert list(p.items()) == [("a", "1"), ("b", "2"), ("a", "3")]

    p.append("a", "4")
    assert list(p.items()) == [("a", "1"), ("b", "2"), ("a", "3"), ("a", "4")]

    p.set("a", "9")
    assert list(p.items()) == [("a", "9"), ("b", "2")]

    p.delete("b")
    assert list(p.items()) == [("a", "9")]
    assert str(p) == "a=9"


def test_leading_question_mark_constructor_equivalence() -> None:
    with_prefix = URLSearchParams("?a=1&b=2")
    without_prefix = URLSearchParams("a=1&b=2")
    assert str(with_prefix) == str(without_prefix) == "a=1&b=2"


def test_space_canonicalization_is_stable() -> None:
    p = URLSearchParams("q=hello%20world&t=a+b")
    assert p.get("q") == "hello world"
    assert p.get("t") == "a b"
    assert str(p) == "q=hello+world&t=a+b"


def test_literal_plus_roundtrip_fidelity() -> None:
    p = URLSearchParams("x=%2B&y=++")
    assert p.get("x") == "+"
    assert p.get("y") == "  "
    assert str(p) == "x=%2B&y=++"


def test_blank_key_value_behavior_is_deterministic() -> None:
    p = URLSearchParams("=blank-name&empty=&k=v")
    assert list(p.items()) == [("", "blank-name"), ("empty", ""), ("k", "v")]
    assert str(p) == "=blank-name&empty=&k=v"


def test_location_history_url_integration_search_params_carry_through() -> None:
    u = URL("https://example.com/p?a=1&a=2&b=x%20y&c=%2B")
    params = u.search_params

    assert list(params.items()) == [("a", "1"), ("a", "2"), ("b", "x y"), ("c", "+")]
    assert str(params) == "a=1&a=2&b=x+y&c=%2B"

    params.set("a", "9")
    assert list(params.items()) == [("a", "9"), ("b", "x y"), ("c", "+")]
    assert u.search == "?a=9&b=x+y&c=%2B"
    assert u.href == "https://example.com/p?a=9&b=x+y&c=%2B"
