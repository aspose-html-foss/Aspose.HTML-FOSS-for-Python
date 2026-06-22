"""Live Range tracking tests (BACK-55, ADR-049, WHATWG DOM §5.1)."""
from __future__ import annotations

import gc
import weakref

from aspose_html.dom import Document


def _parent_with_children(count: int = 3):
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    children = []
    for idx in range(count):
        child = doc.create_element(f"c{idx}")
        parent.append_child(child)
        children.append(child)
    return doc, parent, children


def test_insert_before_boundary_start_increments_offset() -> None:
    doc, parent, children = _parent_with_children(2)
    r = doc.create_range()
    r.set_start(parent, 1)
    r.set_end(parent, 2)

    parent.insert_before(doc.create_element("x"), children[1])

    assert r.start_offset == 2
    assert r.end_offset == 3


def test_append_before_end_boundary_increments_end_offset() -> None:
    doc, parent, _ = _parent_with_children(1)
    r = doc.create_range()
    r.select_node_contents(parent)

    parent.append_child(doc.create_element("x"))

    assert r.end_offset == 2


def test_insert_after_boundary_does_not_increment_offset() -> None:
    doc, parent, children = _parent_with_children(2)
    r = doc.create_range()
    r.set_start(parent, 0)
    r.set_end(parent, 0)

    parent.insert_before(doc.create_element("x"), children[1])

    assert r.start_offset == 0
    assert r.end_offset == 0


def test_insert_document_fragment_increments_by_child_count() -> None:
    doc, parent, children = _parent_with_children(2)
    frag = doc.create_document_fragment()
    frag.append_child(doc.create_element("x"))
    frag.append_child(doc.create_element("y"))
    r = doc.create_range()
    r.set_start(parent, 1)
    r.set_end(parent, 2)

    parent.insert_before(frag, children[1])

    assert r.start_offset == 3
    assert r.end_offset == 4


def test_remove_start_container_relocates_to_old_parent_and_index() -> None:
    doc, parent, children = _parent_with_children(2)
    text = doc.create_text_node("hello")
    children[0].append_child(text)
    r = doc.create_range()
    r.set_start(text, 2)
    r.set_end(parent, 2)

    parent.remove_child(children[0])

    assert r.start_container is parent
    assert r.start_offset == 0


def test_remove_end_container_relocates_to_old_parent_and_index() -> None:
    doc, parent, children = _parent_with_children(2)
    text = doc.create_text_node("hello")
    children[1].append_child(text)
    r = doc.create_range()
    r.set_start(parent, 0)
    r.set_end(text, 3)

    parent.remove_child(children[1])

    assert r.end_container is parent
    assert r.end_offset == 1


def test_remove_descendant_boundary_relocates_to_removed_child_index() -> None:
    doc, parent, children = _parent_with_children(1)
    inner = doc.create_element("inner")
    text = doc.create_text_node("hello")
    children[0].append_child(inner)
    inner.append_child(text)
    r = doc.create_range()
    r.set_start(text, 1)
    r.set_end(text, 4)

    parent.remove_child(children[0])

    assert r.start_container is parent
    assert r.start_offset == 0
    assert r.end_container is parent
    assert r.end_offset == 0


def test_remove_before_boundary_decrements_parent_offset() -> None:
    doc, parent, children = _parent_with_children(3)
    r = doc.create_range()
    r.set_start(parent, 2)
    r.set_end(parent, 3)

    parent.remove_child(children[0])

    assert r.start_offset == 1
    assert r.end_offset == 2


def test_remove_at_boundary_does_not_decrement_boundary_before_node() -> None:
    doc, parent, children = _parent_with_children(3)
    r = doc.create_range()
    r.set_start(parent, 1)
    r.set_end(parent, 1)

    parent.remove_child(children[1])

    assert r.start_offset == 1
    assert r.end_offset == 1


def test_replace_child_updates_removal_and_insertion_boundaries() -> None:
    doc, parent, children = _parent_with_children(2)
    r = doc.create_range()
    r.set_start(parent, 1)
    r.set_end(children[0], 0)

    parent.replace_child(doc.create_element("x"), children[0])

    assert r.start_container is parent
    assert r.start_offset == 1
    assert r.end_container is parent
    assert r.end_offset == 1


def test_text_data_shortening_clamps_start_offset() -> None:
    doc = Document()
    parent = doc.create_element("div")
    text = doc.create_text_node("hello")
    doc.append_child(parent)
    parent.append_child(text)
    r = doc.create_range()
    r.set_start(text, 5)
    r.set_end(text, 5)

    text.data = "hi"

    assert r.start_offset == 2
    assert r.end_offset == 2


def test_text_data_shortening_clamps_end_offset_only_when_needed() -> None:
    doc = Document()
    parent = doc.create_element("div")
    text = doc.create_text_node("hello")
    doc.append_child(parent)
    parent.append_child(text)
    r = doc.create_range()
    r.set_start(text, 1)
    r.set_end(text, 4)

    text.data = "hey"

    assert r.start_offset == 1
    assert r.end_offset == 3


def test_text_data_extension_preserves_offsets() -> None:
    doc = Document()
    parent = doc.create_element("div")
    text = doc.create_text_node("hi")
    doc.append_child(parent)
    parent.append_child(text)
    r = doc.create_range()
    r.set_start(text, 1)
    r.set_end(text, 2)

    text.data = "hello"

    assert r.start_offset == 1
    assert r.end_offset == 2


def test_detach_unregisters_range_from_future_updates() -> None:
    doc, parent, children = _parent_with_children(2)
    r = doc.create_range()
    r.set_start(parent, 1)
    r.set_end(parent, 2)
    r.detach()

    parent.insert_before(doc.create_element("x"), children[1])

    assert r.start_offset == 1
    assert r.end_offset == 2


def test_ranges_are_weakly_tracked() -> None:
    doc = Document()
    r = doc.create_range()
    ref = weakref.ref(r)

    del r
    gc.collect()

    assert ref() is None
    assert len(doc._ranges) == 0
