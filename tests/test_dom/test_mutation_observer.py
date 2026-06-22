"""Tests for BACK-53 — MutationObserver (ADR-045)."""
from __future__ import annotations

from aspose_html.dom import (
    Document,
    Element,
    InvalidStateError,
    MutationObserver,
    MutationRecord,
)


def _setup_parent() -> tuple[Document, object]:
    doc = Document()
    parent = doc.create_element("div")
    doc.append_child(parent)
    return doc, parent


def test_importable_from_dom():
    assert MutationObserver is not None
    assert MutationRecord is not None


def test_observe_append_child_notifies():
    doc, parent = _setup_parent()
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    child = doc.create_element("span")
    parent.append_child(child)
    assert len(got) == 1


def test_observe_remove_child_notifies():
    doc, parent = _setup_parent()
    child = doc.create_element("span")
    parent.append_child(child)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    parent.remove_child(child)
    assert got[0].removed_nodes == (child,)


def test_observe_insert_before_notifies():
    doc, parent = _setup_parent()
    ref = doc.create_element("a")
    parent.append_child(ref)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    node = doc.create_element("b")
    parent.insert_before(node, ref)
    assert got[0].added_nodes == (node,)


def test_append_empty_fragment_does_not_notify_child_list():
    doc, parent = _setup_parent()
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    empty_fragment = doc.create_document_fragment()
    parent.append_child(empty_fragment)
    assert got == []


def test_insert_before_empty_fragment_does_not_notify_child_list():
    doc, parent = _setup_parent()
    ref = doc.create_element("a")
    parent.append_child(ref)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    empty_fragment = doc.create_document_fragment()
    parent.insert_before(empty_fragment, ref)
    assert got == []


def test_observe_replace_child_notifies_two_records():
    doc, parent = _setup_parent()
    old = doc.create_element("a")
    new = doc.create_element("b")
    parent.append_child(old)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    parent.replace_child(new, old)
    assert len(got) == 2
    assert got[0].removed_nodes == (old,)
    assert got[1].added_nodes == (new,)


def test_attributes_set_attribute_notifies():
    _, parent = _setup_parent()
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, attributes=True)
    parent.set_attribute("class", "x")
    assert got[0].type == "attributes"


def test_attributes_remove_attribute_notifies():
    _, parent = _setup_parent()
    parent.set_attribute("class", "x")
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, attributes=True)
    parent.remove_attribute("class")
    assert got[0].attribute_name == "class"


def test_character_data_setter_notifies():
    doc, parent = _setup_parent()
    text = doc.create_text_node("old")
    parent.append_child(text)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(text, character_data=True)
    text.data = "new"
    assert got[0].type == "characterData"


def test_disconnect_stops_notifications():
    doc, parent = _setup_parent()
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    obs.disconnect()
    parent.append_child(doc.create_element("p"))
    assert got == []


def test_take_records_returns_and_clears_queue():
    doc, parent = _setup_parent()
    obs = MutationObserver(lambda records, observer: None)
    obs._pending_records.append(
        MutationRecord("childList", parent, (), (), None, None, None, None, None)
    )
    first = obs.take_records()
    second = obs.take_records()
    assert len(first) == 1
    assert second == []


def test_subtree_true_propagates_from_descendant():
    doc, parent = _setup_parent()
    child = doc.create_element("div")
    parent.append_child(child)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True, subtree=True)
    child.append_child(doc.create_element("span"))
    assert len(got) == 1


def test_subtree_false_does_not_propagate_from_descendant():
    doc, parent = _setup_parent()
    child = doc.create_element("div")
    parent.append_child(child)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True, subtree=False)
    child.append_child(doc.create_element("span"))
    assert got == []


def test_attribute_filter_applies():
    _, parent = _setup_parent()
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, attributes=True, attribute_filter=["href"])
    parent.set_attribute("class", "x")
    parent.set_attribute("href", "#id")
    assert len(got) == 1
    assert got[0].attribute_name == "href"


def test_record_type_child_list():
    doc, parent = _setup_parent()
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    parent.append_child(doc.create_element("i"))
    assert got[0].type == "childList"


def test_record_type_attributes():
    _, parent = _setup_parent()
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, attributes=True)
    parent.set_attribute("x", "1")
    assert got[0].type == "attributes"


def test_record_type_character_data():
    doc, parent = _setup_parent()
    text = doc.create_text_node("a")
    parent.append_child(text)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(text, character_data=True)
    text.data = "b"
    assert got[0].type == "characterData"


def test_record_added_nodes_contains_appended_node():
    doc, parent = _setup_parent()
    node = doc.create_element("x")
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    parent.append_child(node)
    assert got[0].added_nodes == (node,)


def test_record_previous_sibling_is_correct():
    doc, parent = _setup_parent()
    first = doc.create_element("a")
    second = doc.create_element("b")
    parent.append_child(first)
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, child_list=True)
    parent.append_child(second)
    assert got[0].previous_sibling is first


def test_multiple_observers_both_notified():
    doc, parent = _setup_parent()
    got1 = []
    got2 = []
    obs1 = MutationObserver(lambda records, observer: got1.extend(records))
    obs2 = MutationObserver(lambda records, observer: got2.extend(records))
    obs1.observe(parent, child_list=True)
    obs2.observe(parent, child_list=True)
    parent.append_child(doc.create_element("p"))
    assert len(got1) == 1
    assert len(got2) == 1


def test_observe_detached_node_raises_invalid_state_error():
    detached = Element("div", None, None, None)
    obs = MutationObserver(lambda records, observer: None)
    try:
        obs.observe(detached, child_list=True)
        assert False, "Expected InvalidStateError"
    except InvalidStateError:
        pass


def test_observe_replaces_existing_registration_for_target():
    _, parent = _setup_parent()
    obs = MutationObserver(lambda records, observer: None)
    obs.observe(parent, child_list=True)
    obs.observe(parent, attributes=True)
    assert len(obs._registrations) == 1
    assert obs._registrations[0].attributes is True


def test_attribute_old_value_requested_is_reported():
    _, parent = _setup_parent()
    parent.set_attribute("class", "old")
    got = []
    obs = MutationObserver(lambda records, observer: got.extend(records))
    obs.observe(parent, attributes=True, attribute_old_value=True)
    parent.set_attribute("class", "new")
    assert got[0].old_value == "old"
