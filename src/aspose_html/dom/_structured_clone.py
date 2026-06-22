"""Shared structured-clone helpers for DOM runtime payload boundaries.

Implements three layers of the WHATWG HTML §2.7 structured-clone policy:

1. **Excluded types** (``_NON_CLONEABLE_TYPES``): Python intrinsics that can
   never be cloned — functions, generators, coroutines, modules.  These are
   rejected by ``clone_value`` before deepcopy is attempted.

2. **Serializable types**: standard Python containers and scalars (dict, list,
   str, int, float, bool, None, bytes, bytearray, set, frozenset, etc.).
   These pass through ``clone_value`` / ``clone_or_raise_data_clone_error``
   unchanged.

3. **Transferable types** (``TRANSFERABLE_EXCLUDED_TYPES``): the ten WHATWG
   §2.7.4 transferable object type names for which no Python implementation
   exists in this codebase.  In a browser, transfer neutersthe original
   object and moves ownership across a context boundary.  In a headless
   single-runtime Python environment neither neutering nor cross-context
   routing is available, so *any* value whose ``type().__name__`` matches
   one of these names raises ``DataCloneError`` when passed with
   ``is_in_transfer_list=True``.
"""
from __future__ import annotations

import copy
import types as _types


_NON_CLONEABLE_TYPES: tuple[type[object], ...] = (
    _types.FunctionType,
    _types.MethodType,
    _types.GeneratorType,
    _types.CoroutineType,
    _types.AsyncGeneratorType,
    _types.ModuleType,
)

# ---------------------------------------------------------------------------
# Transferable-type registry (WHATWG HTML §2.7.4)
# ---------------------------------------------------------------------------
# These are the *string names* of the ten types listed in the WHATWG §2.7.4
# normative transferable-object table as of the HTML Living Standard 2026.
# No Python class with any of these names exists in this codebase; the names
# are kept as strings so that the registry is queryable and documentable
# without requiring stub class definitions.
#
# The names match the WebIDL / JavaScript constructor names used in the spec.
# When a future task adds a Python implementation of one of these types (e.g.
# an ArrayBuffer proxy), that implementation must *also* update
# ``_TRANSFERABLE_TYPE_NAMES`` to use ``isinstance`` for the concrete type
# rather than a string-name comparison.
TRANSFERABLE_EXCLUDED_TYPES: tuple[str, ...] = (
    "ArrayBuffer",      # §2.7.4 — transferable only; detach semantics not available
    "MessagePort",      # §2.7.4 — transferable only; no cross-thread routing
    "ReadableStream",   # §2.7.4 — transferable only; no stream engine
    "WritableStream",   # §2.7.4 — transferable only; no stream engine
    "TransformStream",  # §2.7.4 — transferable only; no stream engine
    "ImageBitmap",      # §2.7.4 — transferable only; no bitmap engine
    "OffscreenCanvas",  # §2.7.4 — transferable only; no rendering surface
    "AudioData",        # §2.7.4 — transferable only; no audio pipeline
    "VideoFrame",       # §2.7.4 — transferable only; no video pipeline
    "RTCDataChannel",   # §2.7.4 — transferable only; no WebRTC stack
)

# Internal frozenset for O(1) membership tests — built from the authoritative
# tuple above so the two structures are always in sync.
_TRANSFERABLE_TYPE_NAMES: frozenset[str] = frozenset(TRANSFERABLE_EXCLUDED_TYPES)


def clone_value(value: object) -> object:
    """Return a deepcopy-based structured-clone-compatible copy of ``value``.

    Raises the underlying deepcopy exception (or ``TypeError`` from explicit
    pre-guards) when the value is not cloneable.
    """
    if isinstance(value, _NON_CLONEABLE_TYPES):
        raise TypeError(
            f"{type(value).__name__} is not structured-cloneable."
        )
    return copy.deepcopy(value)


def clone_or_raise_data_clone_error(value: object) -> object:
    """Clone ``value`` or raise ``DataCloneError`` on failure.

    Import is intentionally local to avoid import cycles with
    :mod:`aspose_html.dom._window` during module initialization.
    """
    from aspose_html.dom._window import DataCloneError  # noqa: PLC0415

    try:
        return clone_value(value)
    except Exception as exc:  # noqa: BLE001
        raise DataCloneError(str(exc)) from exc


def transfer_or_raise_data_clone_error(
    value: object,
    *,
    is_in_transfer_list: bool,
) -> object:
    """Clone ``value`` applying the WHATWG §2.7.4 transferable-type policy.

    Parameters
    ----------
    value:
        The value to clone.
    is_in_transfer_list:
        When ``False`` (the normal clone path): delegates directly to
        :func:`clone_or_raise_data_clone_error` — semantics are identical to
        the Track 67 seam.

        When ``True``: checks ``type(value).__name__`` against
        ``_TRANSFERABLE_TYPE_NAMES``.  If the type is a known WHATWG
        transferable type, raises :class:`DataCloneError` with the message::

            "Transfer of <TypeName> is not supported in headless context"

        If the type is *not* a known transferable type, falls through to
        ``clone_or_raise_data_clone_error`` (plain serializable values in a
        transfer list are cloned by value — the transfer list is a no-op for
        non-transferable types in a headless environment).

    Returns
    -------
    object
        A deep-copy clone of ``value`` when cloning succeeds.

    Raises
    ------
    DataCloneError
        When the value is a known WHATWG transferable type and
        ``is_in_transfer_list`` is ``True``, or when
        :func:`clone_or_raise_data_clone_error` raises on the value.

    Examples
    --------
    Serializable values pass through regardless of the flag:

    >>> transfer_or_raise_data_clone_error({"x": 1}, is_in_transfer_list=False)
    {'x': 1}
    >>> transfer_or_raise_data_clone_error({"x": 1}, is_in_transfer_list=True)
    {'x': 1}

    A stub class whose name matches a WHATWG transferable type raises when
    placed in the transfer list:

    >>> class ArrayBuffer: pass
    >>> ab = ArrayBuffer()
    >>> import contextlib
    >>> from aspose_html.dom._window import DataCloneError
    >>> with contextlib.suppress(DataCloneError):
    ...     transfer_or_raise_data_clone_error(ab, is_in_transfer_list=True)
    ...     assert False, "should have raised"
    """
    from aspose_html.dom._window import DataCloneError  # noqa: PLC0415

    if is_in_transfer_list and type(value).__name__ in _TRANSFERABLE_TYPE_NAMES:
        raise DataCloneError(
            f"Transfer of {type(value).__name__} is not supported in headless context"
        )
    return clone_or_raise_data_clone_error(value)
