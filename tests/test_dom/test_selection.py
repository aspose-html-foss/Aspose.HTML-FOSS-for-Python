"""Tests for Selection API baseline + phase 2 (/)."""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    IndexSizeError,
    InvalidStateError,
    MutationObserver,
    Selection,
    WrongDocumentError,
)


def _doc_with_parent_and_text() -> tuple[Document, object, object]:
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    text = doc.create_text_node("hello")
    parent.append_child(text)
    return doc, parent, text


def test_document_get_selection_returns_singleton_selection() -> None:
    doc = Document()
    s1 = doc.get_selection()
    s2 = doc.get_selection()

    assert isinstance(s1, Selection)
    assert s1 is s2


def test_empty_selection_shape_and_get_range_at_error() -> None:
    sel = Document().get_selection()

    assert sel.range_count == 0
    assert sel.is_collapsed is True
    assert sel.anchor_node is None
    assert sel.focus_node is None
    assert sel.anchor_offset == 0
    assert sel.focus_offset == 0
    with pytest.raises(IndexSizeError):
        sel.get_range_at(0)


def test_add_range_lifecycle_and_replacement() -> None:
    doc = Document()
    sel = doc.get_selection()
    r1 = doc.create_range()
    r2 = doc.create_range()

    sel.add_range(r1)
    assert sel.range_count == 1
    assert sel.get_range_at(0) is r1

    sel.add_range(r2)
    assert sel.range_count == 1
    assert sel.get_range_at(0) is r2

    sel.remove_all_ranges()
    assert sel.range_count == 0
    assert sel.anchor_node is None
    assert sel.focus_node is None
    with pytest.raises(IndexSizeError):
        sel.get_range_at(1)


def test_add_range_rejects_cross_document_and_detached() -> None:
    doc1 = Document()
    doc2 = Document()
    sel = doc1.get_selection()

    with pytest.raises(WrongDocumentError):
        sel.add_range(doc2.create_range())

    r = doc1.create_range()
    r.detach()
    with pytest.raises(InvalidStateError):
        sel.add_range(r)


def test_collapse_node_offset_and_none_clear() -> None:
    doc, parent, _ = _doc_with_parent_and_text()
    sel = doc.get_selection()

    sel.collapse(parent, 1)
    r = sel.get_range_at(0)
    assert r.start_container is parent
    assert r.end_container is parent
    assert r.start_offset == 1
    assert r.end_offset == 1
    assert sel.is_collapsed is True

    sel.collapse(None)
    assert sel.range_count == 0


def test_collapse_rejects_cross_document_node() -> None:
    doc1 = Document()
    doc2 = Document()

    with pytest.raises(WrongDocumentError):
        doc1.get_selection().collapse(doc2.create_element("x"), 0)


def test_set_position_alias_equivalence_and_none_clear() -> None:
    doc = Document()
    host = doc.create_element("div")
    doc.append_child(host)
    sel = doc.get_selection()

    sel.set_position(host, 0)
    assert sel.range_count == 1
    assert sel.anchor_node is host
    assert sel.focus_node is host
    assert sel.anchor_offset == 0
    assert sel.focus_offset == 0
    assert sel.is_collapsed is True

    sel.set_position(None)
    assert sel.range_count == 0
    assert sel.anchor_node is None
    assert sel.focus_node is None


def test_set_position_error_paths_match_collapse() -> None:
    doc1 = Document()
    doc2 = Document()
    host = doc1.create_element("div")
    doc1.append_child(host)

    with pytest.raises(WrongDocumentError):
        doc1.get_selection().set_position(doc2.create_element("x"), 0)

    with pytest.raises(IndexSizeError):
        doc1.get_selection().set_position(host, 2)


def test_select_all_children_and_cross_document_validation() -> None:
    doc = Document()
    host = doc.create_element("div")
    host.append_child(doc.create_element("a"))
    host.append_child(doc.create_element("b"))
    doc.append_child(host)
    sel = doc.get_selection()

    sel.select_all_children(host)
    r = sel.get_range_at(0)
    assert r.start_container is host
    assert r.end_container is host
    assert r.start_offset == 0
    assert r.end_offset == 2

    with pytest.raises(WrongDocumentError):
        sel.select_all_children(Document().create_element("other"))


def test_directional_anchor_focus_mapping_forwards_and_backwards() -> None:
    doc = Document()
    host = doc.create_element("div")
    host.append_child(doc.create_element("a"))
    host.append_child(doc.create_element("b"))
    doc.append_child(host)
    sel = doc.get_selection()

    sel.select_all_children(host)
    assert sel.anchor_node is host
    assert sel.anchor_offset == 0
    assert sel.focus_node is host
    assert sel.focus_offset == 2

    # Internal seam for  directional mapping tests.
    sel._direction = "backwards"
    assert sel.anchor_node is host
    assert sel.anchor_offset == 2
    assert sel.focus_node is host
    assert sel.focus_offset == 0


def test_collapsed_selection_is_directionless_anchor_equals_focus() -> None:
    doc = Document()
    host = doc.create_element("div")
    doc.append_child(host)
    sel = doc.get_selection()

    sel.collapse(host, 0)
    assert sel.anchor_node is sel.focus_node is host
    assert sel.anchor_offset == sel.focus_offset == 0
    assert sel.is_collapsed is True


def test_collapse_to_start_replaces_with_fresh_collapsed_range() -> None:
    doc = Document()
    host = doc.create_element("div")
    host.append_child(doc.create_element("a"))
    host.append_child(doc.create_element("b"))
    doc.append_child(host)
    sel = doc.get_selection()

    sel.select_all_children(host)
    prior = sel.get_range_at(0)
    sel.collapse_to_start()

    current = sel.get_range_at(0)
    assert current is not prior
    assert current.start_container is host
    assert current.end_container is host
    assert current.start_offset == 0
    assert current.end_offset == 0
    assert sel.anchor_offset == sel.focus_offset == 0


def test_collapse_to_end_replaces_with_fresh_collapsed_range() -> None:
    doc = Document()
    host = doc.create_element("div")
    host.append_child(doc.create_element("a"))
    host.append_child(doc.create_element("b"))
    doc.append_child(host)
    sel = doc.get_selection()

    sel.select_all_children(host)
    prior = sel.get_range_at(0)
    sel.collapse_to_end()

    current = sel.get_range_at(0)
    assert current is not prior
    assert current.start_container is host
    assert current.end_container is host
    assert current.start_offset == 2
    assert current.end_offset == 2
    assert sel.anchor_offset == sel.focus_offset == 2


def test_collapse_to_start_and_end_raise_on_empty_selection() -> None:
    sel = Document().get_selection()

    with pytest.raises(InvalidStateError):
        sel.collapse_to_start()
    with pytest.raises(InvalidStateError):
        sel.collapse_to_end()


def test_selection_reuses_live_range_updates_for_child_list_mutations() -> None:
    doc = Document()
    parent = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    parent.append_child(a)
    parent.append_child(b)
    doc.append_child(parent)

    sel = doc.get_selection()
    r = doc.create_range()
    r.set_start(parent, 1)
    r.set_end(parent, 2)
    sel.add_range(r)

    parent.insert_before(doc.create_element("x"), b)

    selected = sel.get_range_at(0)
    assert selected.start_offset == 2
    assert selected.end_offset == 3


def test_selection_reuses_live_range_clamp_on_character_data_shorten() -> None:
    doc, _parent, text = _doc_with_parent_and_text()
    sel = doc.get_selection()
    r = doc.create_range()
    r.set_start(text, 5)
    r.set_end(text, 5)
    sel.add_range(r)

    text.data = "hi"

    selected = sel.get_range_at(0)
    assert selected.start_offset == 2
    assert selected.end_offset == 2


def test_detached_range_can_remain_selected_until_explicit_change() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("a")
    parent.append_child(child)
    doc.append_child(parent)

    sel = doc.get_selection()
    r = doc.create_range()
    r.select_node_contents(parent)
    sel.add_range(r)
    r.detach()

    parent.append_child(doc.create_element("b"))

    selected = sel.get_range_at(0)
    assert selected is r
    assert selected.end_offset == 1


def test_selection_non_mutating_calls_do_not_emit_mutation_records() -> None:
    doc = Document()
    root = doc.create_element("div")
    doc.append_child(root)
    records = []
    observer = MutationObserver(lambda recs, _obs: records.extend(recs))
    observer.observe(root, child_list=True)

    sel = doc.get_selection()
    sel.add_range(doc.create_range())
    _ = sel.get_range_at(0)
    sel.remove_all_ranges()

    assert records == []


# ---------------------------------------------------------------------------
# Phase 3 —  /  / : extend(), to_string(), contains_node()
# ---------------------------------------------------------------------------


def _doc_with_two_children() -> tuple:
    """Return (doc, host, a, b) where host has children [a, b] in document."""
    doc = Document()
    host = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    host.append_child(a)
    host.append_child(b)
    doc.append_child(host)
    return doc, host, a, b


def test_extend_empty_selection_is_noop() -> None:
    """AC-1: extend() on empty selection is a no-op; range_count stays 0."""
    doc, host, _a, _b = _doc_with_two_children()
    sel = doc.get_selection()

    # Must not raise; range_count must remain 0.
    sel.extend(host, 0)
    assert sel.range_count == 0


def test_extend_focus_after_anchor_forwards() -> None:
    """AC-2: extend() with focus after anchor sets direction='forwards', anchor
    unchanged, focus moves."""
    doc, host, _a, _b = _doc_with_two_children()
    sel = doc.get_selection()
    sel.select_all_children(host)  # start=(host,0), end=(host,2), forwards

    # Anchor is (host, 0); extend focus to (host, 1) — still after anchor.
    sel.extend(host, 1)

    assert sel._direction == "forwards"
    # Anchor must be unchanged at (host, 0).
    assert sel.anchor_node is host
    assert sel.anchor_offset == 0
    # Focus must have moved to (host, 1).
    assert sel.focus_node is host
    assert sel.focus_offset == 1


def test_extend_focus_before_anchor_backwards() -> None:
    """AC-3: extend() with focus before anchor sets direction='backwards',
    anchor unchanged, focus moves."""
    doc, host, _a, _b = _doc_with_two_children()
    sel = doc.get_selection()
    sel.select_all_children(host)  # forwards: anchor=(host,0), focus=(host,2)

    # Move focus to (host, 0) — before anchor at (host, 2) would be needed.
    # After select_all_children, anchor=(host,0), focus=(host,2).
    # Extend to (host, 0) = same as anchor → collapses.  Use a fresh setup:
    # We need anchor AFTER focus.  Manually set _direction to make backwards.
    # Better: use collapse then extend to a position before the current range.
    # Set up a selection anchored at offset 2, focus at 0.
    doc2, host2, _a2, _b2 = _doc_with_two_children()
    sel2 = doc2.get_selection()
    sel2.select_all_children(host2)  # anchor=(host2,0), focus=(host2,2)
    # Now extend focus to (host2, 0): focus <= anchor → backwards.
    sel2.extend(host2, 0)

    assert sel2._direction == "none"  # collapsed (focus == anchor == 0)

    # To get a proper backwards test: start with a forwards selection anchored
    # at offset 1, then extend focus to offset 0.
    doc3 = Document()
    host3 = doc3.create_element("div")
    doc3.create_element("a")
    doc3.create_element("b")
    doc3.create_element("c")
    for tag in ("a", "b", "c"):
        host3.append_child(doc3.create_element(tag))
    doc3.append_child(host3)
    sel3 = doc3.get_selection()
    r3 = doc3.create_range()
    r3.set_start(host3, 1)
    r3.set_end(host3, 2)
    sel3.add_range(r3)
    # sel3 is forwards: anchor=(host3,1), focus=(host3,2)
    assert sel3.anchor_offset == 1
    assert sel3.focus_offset == 2

    # Extend focus to (host3, 0) — before anchor at offset 1.
    sel3.extend(host3, 0)

    assert sel3._direction == "backwards"
    # Anchor must remain at (host3, 1).
    assert sel3.anchor_node is host3
    assert sel3.anchor_offset == 1
    # Focus must be at (host3, 0).
    assert sel3.focus_node is host3
    assert sel3.focus_offset == 0


def test_extend_to_anchor_collapses() -> None:
    """AC-4: extend() to the exact anchor boundary collapses selection;
    is_collapsed is True and direction is 'none'."""
    doc, host, _a, _b = _doc_with_two_children()
    sel = doc.get_selection()
    r = doc.create_range()
    r.set_start(host, 1)
    r.set_end(host, 2)
    sel.add_range(r)
    # anchor=(host,1), focus=(host,2)

    sel.extend(host, 1)  # move focus to exact anchor position

    assert sel.is_collapsed is True
    assert sel._direction == "none"


def test_extend_preserves_range_identity() -> None:
    """AC-5: Range object identity is preserved after extend()."""
    doc, host, _a, _b = _doc_with_two_children()
    sel = doc.get_selection()
    sel.select_all_children(host)
    r_before = sel.get_range_at(0)

    sel.extend(host, 1)

    r_after = sel.get_range_at(0)
    assert r_after is r_before


def test_to_string_non_collapsed() -> None:
    """AC-6: str(selection) returns text content of non-collapsed range."""
    doc = Document()
    p = doc.create_element("p")
    doc.append_child(p)
    t = doc.create_text_node("hello world")
    p.append_child(t)
    sel = doc.get_selection()
    r = doc.create_range()
    r.set_start(t, 0)
    r.set_end(t, 5)
    sel.add_range(r)

    assert sel.to_string() == "hello"
    assert str(sel) == "hello"


def test_to_string_collapsed_returns_empty() -> None:
    """AC-6: str(selection) returns '' when range is collapsed."""
    doc, host, _a, _b = _doc_with_two_children()
    sel = doc.get_selection()
    sel.collapse(host, 0)

    assert sel.to_string() == ""
    assert str(sel) == ""


def test_to_string_empty_selection_returns_empty() -> None:
    """AC-6: str(selection) returns '' when selection has no range."""
    sel = Document().get_selection()

    assert sel.to_string() == ""
    assert str(sel) == ""


def test_to_string_equals_str() -> None:
    """AC-7: to_string() and str(selection) return identical results."""
    doc = Document()
    p = doc.create_element("p")
    doc.append_child(p)
    t = doc.create_text_node("abc")
    p.append_child(t)
    sel = doc.get_selection()
    r = doc.create_range()
    r.set_start(t, 0)
    r.set_end(t, 3)
    sel.add_range(r)

    assert sel.to_string() == str(sel)


def test_contains_node_fully_inside() -> None:
    """AC-8: contains_node(node) returns True when node is fully within the
    selected range."""
    doc = Document()
    host = doc.create_element("div")
    inner = doc.create_element("span")
    host.append_child(inner)
    doc.append_child(host)
    sel = doc.get_selection()
    sel.select_all_children(host)  # range covers (host,0)..(host,1) → inner inside

    assert sel.contains_node(inner) is True


def test_contains_node_fully_outside() -> None:
    """AC-9: contains_node(node) returns False when node is fully outside the
    selected range."""
    doc = Document()
    host = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    host.append_child(a)
    host.append_child(b)
    doc.append_child(host)
    sel = doc.get_selection()
    # Select only the first child slot: (host,0)..(host,1) covers 'a' only.
    r = doc.create_range()
    r.set_start(host, 0)
    r.set_end(host, 1)
    sel.add_range(r)

    # 'b' is at index 1 in host, so it is outside the range (host,0)..(host,1).
    assert sel.contains_node(b) is False


def test_contains_node_partial_overlap_true() -> None:
    """AC-10: contains_node(node, allow_partial_containment=True) returns True
    when node partially overlaps the selected range.

    Demonstrates the difference between partial and strict mode by using a
    text node whose start boundary is partially covered by the range while
    relying on intersects_node for the partial path.
    """
    doc = Document()
    host = doc.create_element("div")
    a = doc.create_element("a")
    b = doc.create_element("b")
    host.append_child(a)
    host.append_child(b)
    doc.append_child(host)
    sel = doc.get_selection()
    # Range covers only slot 1 of host: (host,1)..(host,2) — contains 'b' only.
    r = doc.create_range()
    r.set_start(host, 1)
    r.set_end(host, 2)
    sel.add_range(r)

    # 'a' is at index 0 in host — entirely BEFORE the range (host,1)..(host,2).
    # Strict: compare_point(a, 0) compares boundary (a,0) against range.
    # a precedes host's slot 1, so compare_point(a,0) = -1 (before range start).
    # -1 <= 0 is True, but compare_point(a, _max_offset(a)) where a has no
    # children so max_offset=0 → compare_point(a,0) = -1, and -1 >= 0 is False.
    # → strict returns False for 'a'. Partial: intersects_node(a) returns False
    # since 'a' is entirely before the range.
    assert sel.contains_node(a, allow_partial_containment=False) is False
    assert sel.contains_node(a, allow_partial_containment=True) is False

    # 'b' is within the range (host,1)..(host,2).
    # Strict: compare_point(b,0)=0 (≤0), compare_point(b,0)=0 (≥0) → True.
    # Partial: intersects_node(b) = True.
    assert sel.contains_node(b, allow_partial_containment=False) is True
    assert sel.contains_node(b, allow_partial_containment=True) is True

    # 'host' straddles the range — range is a sub-range of host.
    # intersects_node(host) → True (partial).
    assert sel.contains_node(host, allow_partial_containment=True) is True


def test_contains_node_empty_selection() -> None:
    """AC-11: contains_node(node) returns False when selection is empty."""
    doc = Document()
    host = doc.create_element("div")
    doc.append_child(host)
    sel = doc.get_selection()

    assert sel.contains_node(host) is False
