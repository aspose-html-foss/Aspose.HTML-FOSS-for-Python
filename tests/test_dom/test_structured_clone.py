"""Unit tests for _structured_clone.py — transferable-type registry and helpers.

Covers BACK-278 / ADR-256 / SPEC-123 §FR-1, FR-2 acceptance criteria.
"""
from __future__ import annotations

import types
import pytest

from aspose_html.dom._structured_clone import (
    TRANSFERABLE_EXCLUDED_TYPES,
    _TRANSFERABLE_TYPE_NAMES,
    clone_or_raise_data_clone_error,
    clone_value,
    transfer_or_raise_data_clone_error,
)
from aspose_html.dom._window import DataCloneError


# ---------------------------------------------------------------------------
# Helpers — stub classes whose *names* match WHATWG transferable types
# ---------------------------------------------------------------------------

class ArrayBuffer:  # noqa: D101
    pass


class MessagePort:  # noqa: D101
    pass


class ReadableStream:  # noqa: D101
    pass


# ---------------------------------------------------------------------------
# clone_value — basic coverage (Track 67 seam; must remain unchanged)
# ---------------------------------------------------------------------------

def test_clone_value_plain_dict() -> None:
    """clone_value returns a deep copy of a plain dict."""
    original = {"key": [1, 2, 3]}
    result = clone_value(original)
    assert result == original
    assert result is not original
    assert result["key"] is not original["key"]


def test_clone_value_nested_list() -> None:
    """clone_value produces a deep copy of a nested list."""
    original = [[1, 2], [3, 4]]
    result = clone_value(original)
    assert result == original
    assert result[0] is not original[0]


def test_clone_value_function_raises() -> None:
    """clone_value raises TypeError for functions."""
    with pytest.raises(TypeError, match="is not structured-cloneable"):
        clone_value(lambda: None)


def test_clone_value_generator_raises() -> None:
    """clone_value raises TypeError for generators."""
    def gen():
        yield 1  # noqa: PERF203

    with pytest.raises(TypeError, match="is not structured-cloneable"):
        clone_value(gen())


# ---------------------------------------------------------------------------
# TRANSFERABLE_EXCLUDED_TYPES constant
# ---------------------------------------------------------------------------

def test_transferable_excluded_types_is_tuple_of_strings() -> None:
    """TRANSFERABLE_EXCLUDED_TYPES is a tuple and every element is a str."""
    assert isinstance(TRANSFERABLE_EXCLUDED_TYPES, tuple)
    assert all(isinstance(name, str) for name in TRANSFERABLE_EXCLUDED_TYPES)


def test_transferable_excluded_types_has_ten_entries() -> None:
    """TRANSFERABLE_EXCLUDED_TYPES lists exactly the 10 WHATWG §2.7.4 names."""
    expected = {
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
    assert set(TRANSFERABLE_EXCLUDED_TYPES) == expected
    assert len(TRANSFERABLE_EXCLUDED_TYPES) == 10


# ---------------------------------------------------------------------------
# _TRANSFERABLE_TYPE_NAMES frozenset
# ---------------------------------------------------------------------------

def test_transferable_type_names_frozenset() -> None:
    """_TRANSFERABLE_TYPE_NAMES is a frozenset derived from the tuple."""
    assert isinstance(_TRANSFERABLE_TYPE_NAMES, frozenset)
    assert _TRANSFERABLE_TYPE_NAMES == frozenset(TRANSFERABLE_EXCLUDED_TYPES)


def test_transferable_type_names_o1_lookup() -> None:
    """Known names are present; unknown names are absent — O(1) membership."""
    assert "ArrayBuffer" in _TRANSFERABLE_TYPE_NAMES
    assert "RTCDataChannel" in _TRANSFERABLE_TYPE_NAMES
    assert "dict" not in _TRANSFERABLE_TYPE_NAMES
    assert "int" not in _TRANSFERABLE_TYPE_NAMES


# ---------------------------------------------------------------------------
# transfer_or_raise_data_clone_error — is_in_transfer_list=False path
# ---------------------------------------------------------------------------

def test_transfer_or_raise_not_in_list_plain_dict() -> None:
    """When is_in_transfer_list=False, delegates to clone_or_raise for dicts."""
    original = {"a": 1, "b": [2, 3]}
    result = transfer_or_raise_data_clone_error(original, is_in_transfer_list=False)
    assert result == original
    assert result is not original


def test_transfer_or_raise_not_in_list_function_raises_data_clone_error() -> None:
    """When is_in_transfer_list=False, non-cloneable types still raise DataCloneError."""
    with pytest.raises(DataCloneError):
        transfer_or_raise_data_clone_error(lambda: None, is_in_transfer_list=False)


def test_transfer_or_raise_not_in_list_module_raises_data_clone_error() -> None:
    """When is_in_transfer_list=False, modules still raise DataCloneError."""
    with pytest.raises(DataCloneError):
        transfer_or_raise_data_clone_error(types, is_in_transfer_list=False)


# ---------------------------------------------------------------------------
# transfer_or_raise_data_clone_error — is_in_transfer_list=True path
# ---------------------------------------------------------------------------

def test_transfer_or_raise_in_list_plain_dict_clones_normally() -> None:
    """When is_in_transfer_list=True, plain dicts are cloned (no-op transfer)."""
    original = {"x": 42}
    result = transfer_or_raise_data_clone_error(original, is_in_transfer_list=True)
    assert result == original
    assert result is not original


def test_transfer_or_raise_in_list_known_type_raises() -> None:
    """When is_in_transfer_list=True, a WHATWG-named transferable type raises DataCloneError."""
    ab = ArrayBuffer()
    with pytest.raises(DataCloneError, match="ArrayBuffer") as exc_info:
        transfer_or_raise_data_clone_error(ab, is_in_transfer_list=True)
    assert "not supported in headless context" in str(exc_info.value)


def test_transfer_or_raise_in_list_message_port_raises() -> None:
    """MessagePort (another WHATWG transferable name) also raises DataCloneError."""
    mp = MessagePort()
    with pytest.raises(DataCloneError, match="MessagePort"):
        transfer_or_raise_data_clone_error(mp, is_in_transfer_list=True)


def test_transfer_or_raise_in_list_readable_stream_raises() -> None:
    """ReadableStream raises DataCloneError when in the transfer list."""
    rs = ReadableStream()
    with pytest.raises(DataCloneError, match="ReadableStream"):
        transfer_or_raise_data_clone_error(rs, is_in_transfer_list=True)


def test_transfer_or_raise_in_list_unknown_type_clones_normally() -> None:
    """When is_in_transfer_list=True, types NOT in the registry are cloned normally."""
    # A class named something that is not in _TRANSFERABLE_TYPE_NAMES
    class MyCustomObject:
        pass

    obj = MyCustomObject()
    result = transfer_or_raise_data_clone_error(obj, is_in_transfer_list=True)
    # deepcopy of a plain object succeeds
    assert result is not obj


def test_transfer_or_raise_in_list_not_in_list_symmetry() -> None:
    """Serializable value clones identically regardless of is_in_transfer_list."""
    value = [1, 2, {"nested": True}]
    result_false = transfer_or_raise_data_clone_error(value, is_in_transfer_list=False)
    result_true = transfer_or_raise_data_clone_error(value, is_in_transfer_list=True)
    assert result_false == result_true


def test_transfer_or_raise_in_list_error_message_format() -> None:
    """DataCloneError message matches the WHATWG-aligned format exactly."""
    ab = ArrayBuffer()
    with pytest.raises(DataCloneError) as exc_info:
        transfer_or_raise_data_clone_error(ab, is_in_transfer_list=True)
    assert str(exc_info.value) == "Transfer of ArrayBuffer is not supported in headless context"


# ---------------------------------------------------------------------------
# Regression guard: clone_or_raise_data_clone_error signature unchanged
# ---------------------------------------------------------------------------

def test_clone_or_raise_not_modified() -> None:
    """clone_or_raise_data_clone_error signature accepts exactly one positional arg."""
    import inspect
    sig = inspect.signature(clone_or_raise_data_clone_error)
    params = list(sig.parameters.values())
    assert len(params) == 1
    assert params[0].name == "value"


def test_clone_or_raise_basic() -> None:
    """clone_or_raise_data_clone_error still works — Track 67 seam preserved."""
    result = clone_or_raise_data_clone_error({"a": 1})
    assert result == {"a": 1}
