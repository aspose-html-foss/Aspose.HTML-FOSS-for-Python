"""test_active_formatting.py — unit tests for ActiveFormattingList."""
import pytest
from aspose_html.dom import Document
from aspose_html.tree._active_formatting import ActiveFormattingList, MARKER


@pytest.fixture
def doc():
    return Document()


@pytest.fixture
def lst():
    return ActiveFormattingList()


def test_push_element(doc, lst):
    """Pushing an element adds it to the list."""
    el = doc.create_element("b")
    lst.push(el)
    assert len(lst) == 1
    assert lst[0] is el


def test_push_marker(lst):
    """Pushing a marker adds the MARKER sentinel."""
    lst.push_marker()
    assert len(lst) == 1
    assert lst.is_marker(lst[0])


def test_clear_to_last_marker(doc, lst):
    """clear_to_last_marker removes entries up to and including the last marker."""
    el1 = doc.create_element("b")
    el2 = doc.create_element("i")
    lst.push(el1)
    lst.push_marker()
    lst.push(el2)
    assert len(lst) == 3
    lst.clear_to_last_marker()
    # Only el1 should remain
    assert len(lst) == 1
    assert lst[0] is el1


def test_clear_to_last_marker_no_marker(doc, lst):
    """clear_to_last_marker with no marker clears everything."""
    el = doc.create_element("b")
    lst.push(el)
    lst.clear_to_last_marker()
    assert len(lst) == 0


def test_reconstruct_empty_list(lst):
    """reconstruct does nothing on an empty list."""

    class FakeBuilder:
        class _open_elements:
            @staticmethod
            def contains_node(node):
                return False

        def _clone_element(self, el):
            raise AssertionError("Should not clone anything")

        def _insert_element(self, el):
            raise AssertionError("Should not insert anything")

    lst.reconstruct(FakeBuilder())
    assert len(lst) == 0


def test_reconstruct_all_on_stack(doc, lst):
    """reconstruct does nothing when all entries are on the open elements stack."""
    el = doc.create_element("b")
    lst.push(el)

    class FakeBuilder:
        class _open_elements:
            @staticmethod
            def contains_node(node):
                return node is el  # el is "on stack"

        def _clone_element(self, e):
            raise AssertionError("Should not clone")

        def _insert_element(self, e):
            raise AssertionError("Should not insert")

    lst.reconstruct(FakeBuilder())
    # Nothing should be cloned or inserted
    assert len(lst) == 1


def test_duplicate_element_replacement(doc, lst):
    """Noah's Ark: third duplicate since last marker replaces the oldest."""
    # Create three <b> elements with the same attributes
    el1 = doc.create_element("b")
    el2 = doc.create_element("b")
    el3 = doc.create_element("b")
    el4 = doc.create_element("b")

    lst.push(el1)
    lst.push(el2)
    lst.push(el3)
    # At this point we have 3 <b> elements. Pushing a 4th should replace el1.
    lst.push(el4)
    # The oldest duplicate (el1) should have been replaced by el4
    assert el1 not in list(lst)
    assert el4 in list(lst)


def test_remove(doc, lst):
    """remove() removes a specific element."""
    el = doc.create_element("b")
    lst.push(el)
    lst.remove(el)
    assert len(lst) == 0


def test_remove_not_present(doc, lst):
    """remove() is a no-op if element is not in list."""
    el = doc.create_element("b")
    lst.remove(el)  # Should not raise


def test_replace(doc, lst):
    """replace() replaces an element at the same position."""
    el_old = doc.create_element("b")
    el_new = doc.create_element("b")
    lst.push(el_old)
    lst.replace(el_old, el_new)
    assert lst[0] is el_new


def test_contains(doc, lst):
    """contains() returns True if element is in the list."""
    el = doc.create_element("b")
    assert not lst.contains(el)
    lst.push(el)
    assert lst.contains(el)


def test_is_marker_returns_false_for_element(doc, lst):
    """is_marker returns False for a real element."""
    el = doc.create_element("b")
    assert not lst.is_marker(el)
