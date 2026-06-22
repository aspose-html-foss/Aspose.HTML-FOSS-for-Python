"""Tests for Node base behaviour — tree mutation, traversal, ownership."""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    HierarchyRequestError,
    NotFoundError,
)


@pytest.fixture
def doc() -> Document:
    return Document()


def test_append_child_sets_parent(doc: Document) -> None:
    """AC-2: parent_node is set after append_child."""
    el = doc.create_element("div")
    doc.append_child(el)
    assert el.parent_node is doc


def test_append_child_self_raises(doc: Document) -> None:
    """AC-3: inserting a node into itself raises HierarchyRequestError."""
    el = doc.create_element("div")
    doc.append_child(el)
    with pytest.raises(HierarchyRequestError):
        el.append_child(el)


def test_append_child_ancestor_raises(doc: Document) -> None:
    """Inserting an ancestor raises HierarchyRequestError."""
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)
    with pytest.raises(HierarchyRequestError):
        child.append_child(parent)


def test_remove_child_not_found_raises(doc: Document) -> None:
    """remove_child raises NotFoundError if node is not a child."""
    el = doc.create_element("div")
    with pytest.raises(NotFoundError):
        doc.remove_child(el)


def test_insert_before_none_appends(doc: Document) -> None:
    """insert_before(node, None) is equivalent to append_child."""
    el = doc.create_element("p")
    doc.insert_before(el, None)
    assert doc.first_child is el


def test_insert_before_reference_not_found_raises(doc: Document) -> None:
    """insert_before raises NotFoundError if reference is not a child."""
    a = doc.create_element("a")
    b = doc.create_element("b")
    doc.append_child(a)
    with pytest.raises(NotFoundError):
        doc.insert_before(a, b)  # b is not a child of doc


def test_replace_child_swaps_position(doc: Document) -> None:
    """replace_child swaps old_child for new_child at the same index."""
    a = doc.create_element("a")
    b = doc.create_element("b")
    doc.append_child(a)
    old = doc.replace_child(b, a)
    assert old is a
    assert doc.first_child is b
    assert a.parent_node is None
    assert b.parent_node is doc


def test_replace_child_old_not_found_raises(doc: Document) -> None:
    """replace_child raises NotFoundError if old_child is not a child."""
    a = doc.create_element("a")
    b = doc.create_element("b")
    with pytest.raises(NotFoundError):
        doc.replace_child(b, a)


def test_previous_sibling_next_sibling_navigation(doc: Document) -> None:
    """previous_sibling and next_sibling navigate correctly."""
    root = doc.create_element("div")
    doc.append_child(root)
    a = doc.create_element("a")
    b = doc.create_element("b")
    c = doc.create_element("c")
    root.append_child(a)
    root.append_child(b)
    root.append_child(c)

    assert a.previous_sibling is None
    assert a.next_sibling is b
    assert b.previous_sibling is a
    assert b.next_sibling is c
    assert c.next_sibling is None


def test_first_child_last_child(doc: Document) -> None:
    """first_child and last_child return correct nodes."""
    root = doc.create_element("div")
    doc.append_child(root)
    a = doc.create_element("a")
    b = doc.create_element("b")
    root.append_child(a)
    root.append_child(b)

    assert root.first_child is a
    assert root.last_child is b


def test_has_child_nodes_false_for_empty_container(doc: Document) -> None:
    """has_child_nodes returns False when a container has no children."""
    root = doc.create_element("div")
    assert root.has_child_nodes() is False


def test_has_child_nodes_true_after_adding_child(doc: Document) -> None:
    """has_child_nodes returns True after adding a direct child."""
    root = doc.create_element("div")
    root.append_child(doc.create_element("span"))
    assert root.has_child_nodes() is True


def test_has_child_nodes_false_for_leaf_node(doc: Document) -> None:
    """has_child_nodes returns False for leaf character-data nodes."""
    leaf = doc.create_text_node("leaf")
    assert leaf.has_child_nodes() is False


def test_owner_document_propagated(doc: Document) -> None:
    """Nodes created by factory methods have the correct owner_document."""
    el = doc.create_element("section")
    t = doc.create_text_node("hello")
    assert el.owner_document is doc
    assert t.owner_document is doc


def test_is_same_node_returns_true_for_same_instance(doc: Document) -> None:
    """is_same_node returns True when the object is identical."""
    node = doc.create_element("div")
    assert node.is_same_node(node) is True


def test_is_same_node_returns_false_for_different_instance(doc: Document) -> None:
    """is_same_node returns False for a different node instance."""
    left = doc.create_element("div")
    right = doc.create_element("div")
    assert left.is_same_node(right) is False


def test_is_same_node_returns_false_for_none(doc: Document) -> None:
    """is_same_node returns False for None input."""
    node = doc.create_element("div")
    assert node.is_same_node(None) is False


def test_lookup_namespace_uri_default_namespace(doc: Document) -> None:
    """lookup_namespace_uri(None) resolves the nearest default namespace."""
    root = doc.create_element("root")
    root.set_attribute("xmlns", "urn:root")
    child = doc.create_element("child")
    root.append_child(child)
    doc.append_child(root)

    assert child.lookup_namespace_uri(None) == "urn:root"


def test_lookup_namespace_uri_prefixed_namespace(doc: Document) -> None:
    """lookup_namespace_uri(prefix) resolves the nearest prefixed mapping."""
    root = doc.create_element("root")
    root.set_attribute("xmlns:svg", "http://www.w3.org/2000/svg")
    child = doc.create_element("child")
    root.append_child(child)
    doc.append_child(root)

    assert child.lookup_namespace_uri("svg") == "http://www.w3.org/2000/svg"


def test_lookup_namespace_uri_missing_prefix_returns_none(doc: Document) -> None:
    """lookup_namespace_uri returns None when no mapping exists."""
    root = doc.create_element("root")
    doc.append_child(root)

    assert root.lookup_namespace_uri("missing") is None


def test_lookup_prefix_prefixed_namespace(doc: Document) -> None:
    """lookup_prefix(namespace) resolves the nearest declared prefix."""
    root = doc.create_element("root")
    root.set_attribute("xmlns:svg", "http://www.w3.org/2000/svg")
    child = doc.create_element("child")
    root.append_child(child)
    doc.append_child(root)

    assert child.lookup_prefix("http://www.w3.org/2000/svg") == "svg"


def test_lookup_prefix_missing_namespace_returns_none(doc: Document) -> None:
    """lookup_prefix returns None when no mapping exists."""
    root = doc.create_element("root")
    doc.append_child(root)

    assert root.lookup_prefix("urn:missing") is None


def test_lookup_prefix_none_namespace_returns_none(doc: Document) -> None:
    """lookup_prefix(None) returns None."""
    root = doc.create_element("root")
    doc.append_child(root)

    assert root.lookup_prefix(None) is None


def test_is_default_namespace_matching_default_namespace(doc: Document) -> None:
    """is_default_namespace returns True for matching default namespace."""
    root = doc.create_element("root")
    root.set_attribute("xmlns", "urn:root")
    child = doc.create_element("child")
    root.append_child(child)
    doc.append_child(root)

    assert child.is_default_namespace("urn:root") is True


def test_is_default_namespace_non_matching_namespace(doc: Document) -> None:
    """is_default_namespace returns False for non-matching namespace."""
    root = doc.create_element("root")
    root.set_attribute("xmlns", "urn:root")
    child = doc.create_element("child")
    root.append_child(child)
    doc.append_child(root)

    assert child.is_default_namespace("urn:other") is False


def test_is_default_namespace_no_default_namespace_context(doc: Document) -> None:
    """is_default_namespace returns False when no default namespace is in scope."""
    root = doc.create_element("root")
    child = doc.create_element("child")
    root.append_child(child)
    doc.append_child(root)

    assert child.is_default_namespace("urn:any") is False


def test_is_supported_returns_stable_false_for_nominal_probe_names(doc: Document) -> None:
    """is_supported conservatively returns False for legacy probe names."""
    assert doc.is_supported("Core") is False
    assert doc.is_supported("XML", "3.0") is False
    assert doc.is_supported("html", "1.0") is False


def test_is_supported_unknown_feature_and_versions_are_deterministic(doc: Document) -> None:
    """is_supported stays deterministic for unknown names and versions."""
    assert doc.is_supported("missing") is False
    assert doc.is_supported("missing", None) is False
    assert doc.is_supported("missing", "9.9") is False


def test_get_feature_returns_none_for_nominal_and_unknown_probes(doc: Document) -> None:
    """get_feature returns None for both nominal and unknown probe names."""
    assert doc.get_feature("Core") is None
    assert doc.get_feature("XML", "3.0") is None
    assert doc.get_feature("missing", "9.9") is None


def test_set_user_data_then_get_user_data_returns_stored_value(doc: Document) -> None:
    """set_user_data stores node-local metadata retrievable by key."""
    previous = doc.set_user_data("token", {"id": 7})

    assert previous is None
    assert doc.get_user_data("token") == {"id": 7}


def test_set_user_data_replace_returns_previous_value(doc: Document) -> None:
    """Replacing an existing key returns the previous stored value."""
    doc.set_user_data("token", "v1")
    previous = doc.set_user_data("token", "v2")

    assert previous == "v1"
    assert doc.get_user_data("token") == "v2"


def test_set_user_data_none_clears_key_and_missing_key_returns_none(doc: Document) -> None:
    """Storing None clears key mapping and missing keys return None."""
    doc.set_user_data("token", "v1")
    previous = doc.set_user_data("token", None)

    assert previous == "v1"
    assert doc.get_user_data("token") is None
    assert doc.get_user_data("missing") is None


def test_set_user_data_handler_argument_is_accepted_deterministically(doc: Document) -> None:
    """Optional handler argument is accepted without changing storage semantics."""
    handler = object()
    previous = doc.set_user_data("token", "v1", handler=handler)

    assert previous is None
    assert doc.get_user_data("token") == "v1"


def test_document_normalize_document_matches_node_normalize_semantics(doc: Document) -> None:
    """Document.normalize_document preserves existing Node.normalize behavior."""
    parent = doc.create_element("div")
    doc.append_child(parent)
    parent.append_child(doc.create_text_node("a"))
    parent.append_child(doc.create_text_node(""))
    parent.append_child(doc.create_text_node("b"))

    doc.normalize_document()

    assert len(parent.child_nodes) == 1
    assert parent.first_child is not None
    assert parent.first_child.data == "ab"
