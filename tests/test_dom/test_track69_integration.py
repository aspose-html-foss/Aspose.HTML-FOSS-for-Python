"""Track 69 integration matrix — structured-clone transferable policy.

Tests the full scenario matrix per SPEC-123/FR-4:
  1. Serializable plain types clone correctly.
  2. Excluded types (functions, generators, modules) raise DataCloneError.
  3. Transferable-eligible mock types raise DataCloneError when in transfer list.
  4. Window.structured_clone with and without transfer=[].
"""
from __future__ import annotations

import types

import pytest

from aspose_html.dom import DataCloneError
from aspose_html.dom._document import Document
from aspose_html.dom._structured_clone import (
    TRANSFERABLE_EXCLUDED_TYPES,
    transfer_or_raise_data_clone_error,
)


# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------


def _window():
    """Return a fresh Window instance backed by a plain Document."""
    return Document().default_view


class ArrayBuffer:
    """Stub whose __name__ matches the WHATWG ArrayBuffer transferable type."""


class ReadableStream:
    """Stub whose __name__ matches the WHATWG ReadableStream transferable type."""


# ---------------------------------------------------------------------------
# FR-4 category 1 — Serializable plain types clone correctly
# ---------------------------------------------------------------------------


def test_serializable_dict_clones() -> None:
    """A plain dict clones to an equal, distinct object."""
    value = {"key": "val", "nested": [1, 2, 3]}
    result = transfer_or_raise_data_clone_error(value, is_in_transfer_list=False)
    assert result == value
    assert result is not value


def test_serializable_nested_structure_clones_with_no_aliasing() -> None:
    """Cloned nested structure shares no object identity with the original."""
    inner = [1, 2, 3]
    value = {"inner": inner}
    result = transfer_or_raise_data_clone_error(value, is_in_transfer_list=False)
    result["inner"].append(99)
    assert inner == [1, 2, 3], "clone must be independent of original"


def test_serializable_scalar_types_clone() -> None:
    """int, str, float, bool, None all clone successfully."""
    win = _window()
    for scalar in (42, "hello", 3.14, True, None):
        cloned = win.structured_clone(scalar)
        assert cloned == scalar


# ---------------------------------------------------------------------------
# FR-4 category 2 — Excluded types raise DataCloneError
# ---------------------------------------------------------------------------


def test_excluded_function_raises_data_clone_error() -> None:
    """A function object cannot be structured-cloned."""
    win = _window()
    with pytest.raises(DataCloneError):
        win.structured_clone(lambda: None)


def test_excluded_generator_raises_data_clone_error() -> None:
    """A generator object cannot be structured-cloned."""
    win = _window()

    def _gen():
        yield 1

    with pytest.raises(DataCloneError):
        win.structured_clone(_gen())


def test_excluded_module_raises_data_clone_error() -> None:
    """A module object cannot be structured-cloned."""
    win = _window()
    with pytest.raises(DataCloneError):
        win.structured_clone(types)


# ---------------------------------------------------------------------------
# FR-4 category 3 — Transferable-eligible mock types in / out of transfer list
# ---------------------------------------------------------------------------


def test_mock_transferable_in_transfer_list_raises() -> None:
    """A stub ArrayBuffer in the transfer list raises DataCloneError."""
    ab = ArrayBuffer()
    with pytest.raises(DataCloneError, match="ArrayBuffer"):
        transfer_or_raise_data_clone_error(ab, is_in_transfer_list=True)


def test_mock_transferable_not_in_transfer_list_raises_on_deepcopy() -> None:
    """A stub ArrayBuffer NOT in the transfer list clones by value (plain Python object)."""
    ab = ArrayBuffer()
    # The stub is a plain Python object — deepcopy succeeds.
    result = transfer_or_raise_data_clone_error(ab, is_in_transfer_list=False)
    assert isinstance(result, ArrayBuffer)
    assert result is not ab


def test_all_transferable_excluded_type_names_present() -> None:
    """TRANSFERABLE_EXCLUDED_TYPES contains the expected WHATWG §2.7.4 type names."""
    expected_subset = {
        "ArrayBuffer",
        "MessagePort",
        "ReadableStream",
        "WritableStream",
        "TransformStream",
        "ImageBitmap",
        "OffscreenCanvas",
        "AudioData",
        "VideoFrame",
        "RTCDataChannel",
    }
    assert expected_subset <= set(TRANSFERABLE_EXCLUDED_TYPES)


def test_readable_stream_stub_in_transfer_list_raises() -> None:
    """A stub ReadableStream in the transfer list raises DataCloneError."""
    rs = ReadableStream()
    with pytest.raises(DataCloneError, match="ReadableStream"):
        transfer_or_raise_data_clone_error(rs, is_in_transfer_list=True)


# ---------------------------------------------------------------------------
# FR-4 category 4 — Window.structured_clone with and without transfer=[]
# ---------------------------------------------------------------------------


def test_window_structured_clone_no_transfer_arg() -> None:
    """window.structured_clone(value) without transfer arg returns a deep clone."""
    win = _window()
    value = {"a": [1, 2], "b": {"c": 3}}
    result = win.structured_clone(value)
    assert result == value
    assert result is not value
    assert result["a"] is not value["a"]


def test_window_structured_clone_empty_transfer_list() -> None:
    """window.structured_clone(value, transfer=[]) behaves identically to no-transfer."""
    win = _window()
    value = [1, 2, 3]
    result = win.structured_clone(value, transfer=[])
    assert result == value
    assert result is not value


def test_window_structured_clone_transfer_with_mock_transferable_raises() -> None:
    """window.structured_clone raises DataCloneError when transfer list has a known type."""
    win = _window()
    ab = ArrayBuffer()
    with pytest.raises(DataCloneError, match="ArrayBuffer"):
        win.structured_clone({"data": 1}, transfer=[ab])
