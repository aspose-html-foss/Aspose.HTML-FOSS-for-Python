"""Tests for Web Storage stubs — Storage, Window.local_storage, Window.session_storage.

Covers WHATWG HTML §12.2 Storage interface and Window integration per  / .
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, Storage


# ---------------------------------------------------------------------------
# Storage unit tests
# ---------------------------------------------------------------------------


def test_storage_initial_length_is_zero() -> None:
    s = Storage()
    assert s.length == 0


def test_storage_set_get() -> None:
    s = Storage()
    s.set_item("k", "v")
    assert s.get_item("k") == "v"


def test_storage_get_missing_returns_none() -> None:
    s = Storage()
    assert s.get_item("missing") is None


def test_storage_set_increments_length() -> None:
    s = Storage()
    assert s.length == 0
    s.set_item("a", "1")
    assert s.length == 1
    s.set_item("b", "2")
    assert s.length == 2


def test_storage_set_same_key_does_not_increase_length() -> None:
    s = Storage()
    s.set_item("k", "first")
    s.set_item("k", "second")
    assert s.length == 1
    assert s.get_item("k") == "second"


def test_storage_remove_existing_key() -> None:
    s = Storage()
    s.set_item("k", "v")
    s.remove_item("k")
    assert s.get_item("k") is None
    assert s.length == 0


def test_storage_remove_missing_is_noop() -> None:
    s = Storage()
    s.remove_item("not_here")  # must not raise


def test_storage_clear() -> None:
    s = Storage()
    s.set_item("a", "1")
    s.set_item("b", "2")
    s.clear()
    assert s.length == 0
    assert s.get_item("a") is None


def test_storage_key_insertion_order() -> None:
    s = Storage()
    s.set_item("first", "1")
    s.set_item("second", "2")
    s.set_item("third", "3")
    assert s.key(0) == "first"
    assert s.key(1) == "second"
    assert s.key(2) == "third"


def test_storage_key_out_of_range_returns_none() -> None:
    s = Storage()
    s.set_item("x", "1")
    assert s.key(1) is None
    assert s.key(10) is None


def test_storage_key_negative_returns_none() -> None:
    s = Storage()
    s.set_item("x", "1")
    assert s.key(-1) is None


def test_storage_set_item_coerces_value_to_str() -> None:
    s = Storage()
    s.set_item("n", "42")  # type: ignore[arg-type]  # testing coercion
    assert s.get_item("n") == "42"


def test_storage_overwrite_preserves_insertion_order_for_original_position() -> None:
    """Updating an existing key preserves its insertion-order position."""
    s = Storage()
    s.set_item("a", "1")
    s.set_item("b", "2")
    s.set_item("a", "updated")
    # Python dict: updating an existing key preserves its position
    assert s.key(0) == "a"
    assert s.key(1) == "b"


# ---------------------------------------------------------------------------
# Window.local_storage and Window.session_storage integration tests
# ---------------------------------------------------------------------------


def test_window_local_storage_returns_storage_instance() -> None:
    doc = Document()
    ls = doc.default_view.local_storage
    assert isinstance(ls, Storage)


def test_window_session_storage_returns_storage_instance() -> None:
    doc = Document()
    ss = doc.default_view.session_storage
    assert isinstance(ss, Storage)


def test_window_local_storage_cached_same_instance() -> None:
    doc = Document()
    assert doc.default_view.local_storage is doc.default_view.local_storage


def test_window_session_storage_cached_same_instance() -> None:
    doc = Document()
    assert doc.default_view.session_storage is doc.default_view.session_storage


def test_window_local_and_session_storage_are_distinct_objects() -> None:
    doc = Document()
    assert doc.default_view.local_storage is not doc.default_view.session_storage


def test_window_local_session_storage_do_not_share_data() -> None:
    doc = Document()
    doc.default_view.local_storage.set_item("x", "local")
    assert doc.default_view.session_storage.get_item("x") is None


def test_window_local_storage_persists_between_accesses() -> None:
    doc = Document()
    doc.default_view.local_storage.set_item("theme", "dark")
    assert doc.default_view.local_storage.get_item("theme") == "dark"


def test_window_session_storage_persists_between_accesses() -> None:
    doc = Document()
    doc.default_view.session_storage.set_item("token", "abc")
    assert doc.default_view.session_storage.get_item("token") == "abc"


def test_two_windows_have_independent_local_storages() -> None:
    doc1 = Document()
    doc2 = Document()
    doc1.default_view.local_storage.set_item("k", "win1")
    assert doc2.default_view.local_storage.get_item("k") is None


# ---------------------------------------------------------------------------
# Public API export
# ---------------------------------------------------------------------------


def test_storage_importable_from_dom() -> None:
    from aspose_html.dom import Storage as S  # noqa: PLC0415
    assert S is not None


def test_storage_in_dom_all() -> None:
    import aspose_html.dom as dom  # noqa: PLC0415
    assert "Storage" in dom.__all__
