"""Tests for Element.matches() and Element.closest() — BACK-19 / ADR-014."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# Shared fixture helper
# ---------------------------------------------------------------------------

def _make_doc():
    """Return (doc, outer_div, inner_span, p) for a tree:

    Document
      div.container
        span.active
        p#para
    """
    doc = Document()
    outer = doc.create_element("div")
    outer.set_attribute("class", "container")
    inner = doc.create_element("span")
    inner.set_attribute("class", "active")
    para = doc.create_element("p")
    para.set_attribute("id", "para")
    doc.append_child(outer)
    outer.append_child(inner)
    outer.append_child(para)
    return doc, outer, inner, para


# ---------------------------------------------------------------------------
# matches() tests
# ---------------------------------------------------------------------------

def test_matches_simple_tag():
    """AC-1: div.matches('div') returns True; wrong tag returns False."""
    doc, outer, inner, para = _make_doc()
    assert outer.matches("div") is True


def test_matches_wrong_tag():
    """span.matches('div') returns False."""
    doc, outer, inner, para = _make_doc()
    assert inner.matches("div") is False


def test_matches_class_selector():
    """AC-2: element with class 'active' matches '.active'."""
    doc, outer, inner, para = _make_doc()
    assert inner.matches(".active") is True
    assert outer.matches(".active") is False


def test_matches_id_selector():
    """Element with id='para' matches '#para'; other elements do not."""
    doc, outer, inner, para = _make_doc()
    assert para.matches("#para") is True
    assert outer.matches("#para") is False


def test_matches_attribute_selector():
    """Element with an href attribute matches '[href]'."""
    doc = Document()
    a = doc.create_element("a")
    a.set_attribute("href", "https://example.com")
    doc.append_child(a)
    assert a.matches("[href]") is True
    assert a.matches("[data-x]") is False


def test_matches_descendant_selector():
    """span inside div matches 'div span'."""
    doc, outer, inner, para = _make_doc()
    # inner span is a descendant of the outer div
    assert inner.matches("div span") is True
    # the outer div itself is not a descendant of a div (at this level)
    assert outer.matches("div span") is False


def test_matches_compound_selector():
    """AC-3: div.container matches 'div.container'; span does not."""
    doc, outer, inner, para = _make_doc()
    assert outer.matches("div.container") is True
    assert inner.matches("span.container") is False


def test_matches_returns_false_for_different_class():
    """Element with class 'container' does not match '.active'."""
    doc, outer, inner, para = _make_doc()
    assert outer.matches(".active") is False


def test_matches_detached_element():
    """matches() on a detached element uses self as root."""
    doc = Document()
    div = doc.create_element("div")
    div.set_attribute("class", "box")
    # detached — never appended to doc
    assert div.matches("div") is True
    assert div.matches(".box") is True
    assert div.matches("span") is False


def test_matches_invalid_selector_raises_syntax_error():
    """AC-8: completely invalid selector raises SyntaxError."""
    doc, outer, inner, para = _make_doc()
    with pytest.raises(SyntaxError):
        outer.matches("!!!invalid")


# ---------------------------------------------------------------------------
# closest() tests
# ---------------------------------------------------------------------------

def test_closest_self_match():
    """AC-4: closest('div') returns self when self is a div."""
    doc, outer, inner, para = _make_doc()
    assert outer.closest("div") is outer


def test_closest_ancestor():
    """AC-5: span inside div — closest('div') returns the ancestor div."""
    doc, outer, inner, para = _make_doc()
    assert inner.closest("div") is outer


def test_closest_returns_none():
    """AC-6: no ancestor matches the selector — returns None."""
    doc, outer, inner, para = _make_doc()
    assert outer.closest("article") is None
    assert inner.closest("article") is None


def test_closest_not_self():
    """closest('p') on span checks parents; p is a sibling, not ancestor."""
    doc, outer, inner, para = _make_doc()
    # inner span has no 'p' ancestor — para is sibling of span
    assert inner.closest("p") is None


def test_closest_self_inclusive_with_class():
    """closest is truly self-inclusive even with class selector."""
    doc, outer, inner, para = _make_doc()
    assert inner.closest(".active") is inner


def test_closest_detached_element():
    """AC-7: detached element — closest returns self if matches, else None."""
    doc = Document()
    div = doc.create_element("div")
    # detached: not appended to doc
    assert div.closest("div") is div
    span = doc.create_element("span")
    assert span.closest("div") is None


def test_closest_multiple_levels():
    """AC-12: deeply nested — closest returns correct ancestor at any depth."""
    doc = Document()
    level1 = doc.create_element("div")
    level1.set_attribute("class", "root")
    level2 = doc.create_element("section")
    level3 = doc.create_element("article")
    level4 = doc.create_element("span")
    doc.append_child(level1)
    level1.append_child(level2)
    level2.append_child(level3)
    level3.append_child(level4)

    # deepest node: find each ancestor
    assert level4.closest("article") is level3
    assert level4.closest("section") is level2
    assert level4.closest("div") is level1
    assert level4.closest("div.root") is level1
    assert level4.closest("body") is None


def test_closest_does_not_reach_document():
    """AC-10: closest() stops at parent_element=None, never returning Document."""
    doc, outer, inner, para = _make_doc()
    # outer.parent_element is None (parent is Document, not Element)
    result = outer.closest("html")
    assert result is None
    # Confirm the Document node is not returned
    assert not isinstance(result, Document)


def test_closest_invalid_selector_raises_syntax_error():
    """AC-8 (closest): invalid selector propagates SyntaxError."""
    doc, outer, inner, para = _make_doc()
    with pytest.raises(SyntaxError):
        outer.closest("!!!invalid")
