"""Tests for URLSearchParams WHATWG conformance additions ( / ).

Covers: size, has(name, value), delete(name, value), entries().
"""
from __future__ import annotations

import pytest

from aspose_html.url._search_params import URLSearchParams


# ---------------------------------------------------------------------------
# size property
# ---------------------------------------------------------------------------

def test_size_empty() -> None:
    assert URLSearchParams("").size == 0


def test_size_multiple() -> None:
    p = URLSearchParams("a=1&b=2&a=3")
    assert p.size == 3


def test_size_single() -> None:
    assert URLSearchParams("a=1").size == 1


def test_size_duplicates_counted() -> None:
    p = URLSearchParams("a=1&a=2")
    assert p.size == 2


# ---------------------------------------------------------------------------
# has(name) — existing one-arg behaviour preserved
# ---------------------------------------------------------------------------

def test_has_name_only_exists() -> None:
    p = URLSearchParams("a=1&b=2")
    assert p.has("a") is True


def test_has_name_only_missing() -> None:
    p = URLSearchParams("a=1&b=2")
    assert p.has("c") is False


# ---------------------------------------------------------------------------
# has(name, value) — two-arg form
# ---------------------------------------------------------------------------

def test_has_name_and_value_match() -> None:
    p = URLSearchParams("a=1&a=2")
    assert p.has("a", "1") is True


def test_has_name_and_value_second_match() -> None:
    p = URLSearchParams("a=1&a=2")
    assert p.has("a", "2") is True


def test_has_name_and_value_no_match() -> None:
    p = URLSearchParams("a=1&a=2")
    assert p.has("a", "99") is False


def test_has_name_exists_but_value_wrong() -> None:
    p = URLSearchParams("a=1&b=2")
    assert p.has("a", "2") is False


# ---------------------------------------------------------------------------
# delete(name) — existing one-arg behaviour preserved
# ---------------------------------------------------------------------------

def test_delete_name_only() -> None:
    p = URLSearchParams("a=1&a=2&b=3")
    p.delete("a")
    assert str(p) == "b=3"


def test_delete_name_only_missing_is_noop() -> None:
    p = URLSearchParams("a=1&b=2")
    p.delete("z")
    assert str(p) == "a=1&b=2"


# ---------------------------------------------------------------------------
# delete(name, value) — two-arg form
# ---------------------------------------------------------------------------

def test_delete_name_and_value() -> None:
    p = URLSearchParams("a=1&a=2&b=3")
    p.delete("a", "1")
    assert str(p) == "a=2&b=3"


def test_delete_name_and_value_only_exact_removed() -> None:
    """Deleting a=1 must leave a=2 untouched."""
    p = URLSearchParams("a=1&a=2")
    p.delete("a", "1")
    assert str(p) == "a=2"


def test_delete_name_and_value_no_match_is_noop() -> None:
    p = URLSearchParams("a=1&b=2")
    p.delete("a", "99")
    assert str(p) == "a=1&b=2"


def test_delete_name_and_value_all_matching() -> None:
    """When every pair matches, result is empty."""
    p = URLSearchParams("a=1&a=1")
    p.delete("a", "1")
    assert str(p) == ""


# ---------------------------------------------------------------------------
# entries() iterator
# ---------------------------------------------------------------------------

def test_entries_order() -> None:
    p = URLSearchParams("a=1&b=2&a=3")
    assert list(p.entries()) == [("a", "1"), ("b", "2"), ("a", "3")]


def test_entries_empty() -> None:
    assert list(URLSearchParams("").entries()) == []


def test_entries_single() -> None:
    assert list(URLSearchParams("x=42").entries()) == [("x", "42")]


# ---------------------------------------------------------------------------
# Consistency checks
# ---------------------------------------------------------------------------

def test_has_two_arg_consistency_with_entries() -> None:
    """Every (name, value) from entries() must satisfy has(name, value)."""
    p = URLSearchParams("a=1&b=2&a=3&c=4")
    for name, value in p.entries():
        assert p.has(name, value) is True, f"has({name!r}, {value!r}) returned False"


def test_entries_same_as_items() -> None:
    """entries() and items() must produce identical sequences."""
    p = URLSearchParams("x=1&y=2&x=3")
    assert list(p.entries()) == list(p.items())


def test_entries_same_as_iter() -> None:
    """entries() must produce the same sequence as iterating the object."""
    p = URLSearchParams("a=1&b=2")
    assert list(p.entries()) == list(p)


def test_size_after_delete_two_arg() -> None:
    p = URLSearchParams("a=1&a=2&b=3")
    assert p.size == 3
    p.delete("a", "1")
    assert p.size == 2


def test_size_after_append() -> None:
    p = URLSearchParams("a=1")
    p.append("b", "2")
    assert p.size == 2
