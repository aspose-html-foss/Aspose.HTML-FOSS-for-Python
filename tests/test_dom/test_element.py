"""Tests for Element properties and attribute methods."""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, NodeType


@pytest.fixture
def doc() -> Document:
    return Document()


def test_get_attribute_returns_value(doc: Document) -> None:
    """AC-5: get_attribute returns the correct attribute value."""
    el = doc.create_element("div")
    el.set_attribute("id", "main")
    assert el.get_attribute("id") == "main"


def test_get_attribute_absent_returns_none(doc: Document) -> None:
    el = doc.create_element("div")
    assert el.get_attribute("missing") is None


def test_set_attribute_creates(doc: Document) -> None:
    el = doc.create_element("span")
    el.set_attribute("data-x", "1")
    assert el.get_attribute("data-x") == "1"


def test_set_attribute_updates(doc: Document) -> None:
    el = doc.create_element("span")
    el.set_attribute("data-x", "1")
    el.set_attribute("data-x", "2")
    assert el.get_attribute("data-x") == "2"
    assert len(el.attributes) == 1  # no duplicate


def test_remove_attribute(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("class", "box")
    el.remove_attribute("class")
    assert el.get_attribute("class") is None
    assert not el.has_attribute("class")


def test_has_attribute(doc: Document) -> None:
    el = doc.create_element("div")
    assert not el.has_attribute("id")
    el.set_attribute("id", "x")
    assert el.has_attribute("id")


def test_children_vs_child_nodes(doc: Document) -> None:
    """AC-4: child_nodes and children are distinct objects."""
    el = doc.create_element("div")
    assert el.child_nodes is not el.children


def test_children_element_only(doc: Document) -> None:
    """AC-4: children contains only Element children."""
    parent = doc.create_element("div")
    child_el = doc.create_element("span")
    child_text = doc.create_text_node("hi")
    doc.append_child(parent)
    parent.append_child(child_el)
    parent.append_child(child_text)

    assert len(parent.child_nodes) == 2
    assert len(parent.children) == 1
    assert parent.children[0] is child_el


def test_class_list_split(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("class", "foo bar baz")
    assert list(el.class_list) == ["foo", "bar", "baz"]


def test_class_list_empty(doc: Document) -> None:
    el = doc.create_element("div")
    assert len(el.class_list) == 0


def test_first_element_child_last_element_child(doc: Document) -> None:
    parent = doc.create_element("div")
    doc.append_child(parent)
    a = doc.create_element("a")
    b = doc.create_element("b")
    parent.append_child(a)
    parent.append_child(b)

    assert parent.first_element_child is a
    assert parent.last_element_child is b


def test_next_element_sibling_previous_element_sibling(doc: Document) -> None:
    parent = doc.create_element("div")
    doc.append_child(parent)
    a = doc.create_element("a")
    b = doc.create_element("b")
    parent.append_child(a)
    parent.append_child(b)

    assert a.next_element_sibling is b
    assert b.previous_element_sibling is a
    assert a.previous_element_sibling is None
    assert b.next_element_sibling is None


def test_child_element_count(doc: Document) -> None:
    parent = doc.create_element("ul")
    doc.append_child(parent)
    assert parent.child_element_count == 0
    li1 = doc.create_element("li")
    li2 = doc.create_element("li")
    parent.append_child(li1)
    parent.append_child(li2)
    assert parent.child_element_count == 2


# ===========================================================================
# : get_attribute_node / set_attribute_node / remove_attribute_node
# ===========================================================================

def test_get_attribute_node_returns_attr(doc: Document) -> None:
    """AC-1: get_attribute_node returns Attr with correct name/value."""
    from aspose_html.dom import Attr
    el = doc.create_element("div")
    el.set_attribute("id", "main")
    attr = el.get_attribute_node("id")
    assert attr is not None
    assert isinstance(attr, Attr)
    assert attr.name == "id"
    assert attr.value == "main"


def test_get_attribute_node_absent_returns_none(doc: Document) -> None:
    """AC-1: get_attribute_node returns None when attribute absent."""
    el = doc.create_element("div")
    assert el.get_attribute_node("missing") is None


def test_set_attribute_node_insert_returns_none(doc: Document) -> None:
    """AC-2: set_attribute_node inserts new attr and returns None."""
    from aspose_html.dom import Attr
    el = doc.create_element("div")
    attr = Attr("class", "box", owner_element=None)
    result = el.set_attribute_node(attr)
    assert result is None
    assert el.get_attribute("class") == "box"


def test_set_attribute_node_replace_returns_old(doc: Document) -> None:
    """AC-2: set_attribute_node replaces existing and returns the old Attr."""
    from aspose_html.dom import Attr
    el = doc.create_element("div")
    old_attr = Attr("class", "box", owner_element=None)
    el.set_attribute_node(old_attr)
    new_attr = Attr("class", "flex", owner_element=None)
    displaced = el.set_attribute_node(new_attr)
    assert displaced is old_attr
    assert el.get_attribute("class") == "flex"


def test_remove_attribute_node_removes_and_returns(doc: Document) -> None:
    """AC-3: remove_attribute_node removes attr and returns it."""
    el = doc.create_element("div")
    el.set_attribute("data-x", "1")
    attr = el.get_attribute_node("data-x")
    removed = el.remove_attribute_node(attr)
    assert removed is attr
    assert not el.has_attribute("data-x")


def test_remove_attribute_node_not_present_raises(doc: Document) -> None:
    """AC-3: remove_attribute_node raises NotFoundError when attr absent."""
    from aspose_html.dom import Attr, NotFoundError
    el = doc.create_element("div")
    attr = Attr("data-x", "1", owner_element=None)
    with pytest.raises(NotFoundError):
        el.remove_attribute_node(attr)


def test_set_attribute_node_in_use_raises(doc: Document) -> None:
    """AC-4: set_attribute_node raises InUseAttributeError for attr owned by another element."""
    from aspose_html.dom import InUseAttributeError
    el1 = doc.create_element("div")
    el2 = doc.create_element("span")
    el1.set_attribute("id", "x")
    attr = el1.get_attribute_node("id")
    with pytest.raises(InUseAttributeError):
        el2.set_attribute_node(attr)


def test_toggle_attribute_no_force(doc: Document) -> None:
    el = doc.create_element("div")
    assert el.toggle_attribute("hidden") is True
    assert el.has_attribute("hidden") is True
    assert el.toggle_attribute("hidden") is False
    assert el.has_attribute("hidden") is False


def test_toggle_attribute_force_true(doc: Document) -> None:
    el = doc.create_element("div")
    assert el.toggle_attribute("disabled", force=True) is True
    assert el.has_attribute("disabled") is True
    assert el.toggle_attribute("disabled", force=True) is True


def test_toggle_attribute_force_false(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("disabled", "")
    assert el.toggle_attribute("disabled", force=False) is False
    assert el.has_attribute("disabled") is False


def test_toggle_attribute_invalid_name_raises(doc: Document) -> None:
    from aspose_html.dom import InvalidCharacterError

    el = doc.create_element("div")
    with pytest.raises(InvalidCharacterError):
        el.toggle_attribute("bad name")


def test_get_attribute_names(doc: Document) -> None:
    el = doc.create_element("span")
    assert el.get_attribute_names() == []
    el.set_attribute("class", "foo")
    el.set_attribute("id", "bar")
    assert el.get_attribute_names() == ["class", "id"]


def test_has_attributes(doc: Document) -> None:
    el = doc.create_element("div")
    assert el.has_attributes() is False
    el.set_attribute("x", "1")
    assert el.has_attributes() is True
    el.remove_attribute("x")
    assert el.has_attributes() is False


def test_scroll_into_view_noop(doc: Document) -> None:
    el = doc.create_element("div")
    el.scroll_into_view()
    el.scroll_into_view(True)
    el.scroll_into_view(False)
    el.scroll_into_view({"behavior": "smooth"})


def test_scroll_noop(doc: Document) -> None:
    el = doc.create_element("div")
    el.scroll(0, 0)
    el.scroll({"top": 100, "left": 0})


def test_get_animations_returns_empty_list(doc: Document) -> None:
    el = doc.create_element("div")

    animations = el.get_animations()
    assert animations == []
    assert isinstance(animations, list)


def test_query_selector_all_scope_child_matches_direct_children(doc: Document) -> None:
    """ AC-1: :scope > span is rooted at the element receiver."""
    root = doc.create_element("div")
    span_direct = doc.create_element("span")
    nested_holder = doc.create_element("p")
    span_nested = doc.create_element("span")
    nested_holder.append_child(span_nested)
    root.append_child(span_direct)
    root.append_child(nested_holder)

    result = list(root.query_selector_all(":scope > span"))
    assert result == [span_direct]


def test_document_query_selector_all_scope_child_html_is_deterministic(doc: Document) -> None:
    """ AC-2: document-root :scope semantics are deterministic."""
    html = doc.create_element("html")
    body = doc.create_element("body")
    html.append_child(body)
    doc.append_child(html)

    # Current bounded semantics: root candidate itself is not enumerated,
    # so :scope > html does not match.
    assert list(doc.query_selector_all(":scope > html")) == []


def test_scope_inside_compound_selector_matches_child_filtering(doc: Document) -> None:
    """ AC-3: :scope composes with supported compound selectors."""
    root = doc.create_element("section")
    keep = doc.create_element("span")
    skip = doc.create_element("span")
    skip.set_attribute("class", "skip")
    root.append_child(keep)
    root.append_child(skip)

    result = list(root.query_selector_all(":scope > span:not(.skip)"))
    assert result == [keep]


# ---------------------------------------------------------------------------
#  — CSSOM View / Pointer Events / Fullscreen IDL stubs ()
# ---------------------------------------------------------------------------


def test_element_scroll_into_view_if_needed(doc: Document) -> None:
    """AC-1: scroll_into_view_if_needed executes without error."""
    el = doc.create_element("div")
    el.scroll_into_view_if_needed()
    el.scroll_into_view_if_needed(True)
    el.scroll_into_view_if_needed(False)


def test_element_pointer_capture_stubs(doc: Document) -> None:
    """AC-2 + AC-3: set/release_pointer_capture no-op; has_pointer_capture returns False."""
    el = doc.create_element("div")
    el.set_pointer_capture(1)
    el.release_pointer_capture(1)
    assert el.has_pointer_capture(1) is False
    assert el.has_pointer_capture(0) is False


def test_element_request_pointer_lock(doc: Document) -> None:
    """AC-4: request_pointer_lock executes without error."""
    el = doc.create_element("canvas")
    el.request_pointer_lock()


def test_element_request_fullscreen(doc: Document) -> None:
    """AC-5: request_fullscreen executes without error with and without options."""
    el = doc.create_element("div")
    el.request_fullscreen()
    el.request_fullscreen({"navigationUI": "hide"})
    el.request_fullscreen(None)


def test_element_check_visibility(doc: Document) -> None:
    """AC-6: check_visibility always returns True."""
    el = doc.create_element("div")
    assert el.check_visibility() is True
    assert el.check_visibility({"visibilityProperty": True}) is True
    assert el.check_visibility(None) is True
