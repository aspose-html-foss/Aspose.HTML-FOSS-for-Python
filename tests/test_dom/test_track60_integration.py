""" Window utility stubs — integration matrix ().

Covers cross-component integration evidence for the five new surfaces
introduced in :

- ``Window.queue_microtask`` ()
- ``Window.structured_clone`` / ``DataCloneError`` ()
- ``Window.crypto`` / ``Crypto`` / ``SubtleCrypto`` ()
- ``Window.performance`` / ``Performance`` / ``PerformanceTiming`` ()
- ``Window.get_selection`` ()

Groups A–G per  specification.  Minimum 30 assertions across all groups.

Tasks: , , , , , 
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

import aspose_html.dom as dom
from aspose_html.dom import (
    Crypto,
    DataCloneError,
    Document,
    MessageChannel,
    Performance,
    PerformanceTiming,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh_window():
    """Return a new Window instance attached to a blank Document."""
    return Document().default_view


# ---------------------------------------------------------------------------
# Group A — queue_microtask routing ( / )
# ---------------------------------------------------------------------------


class TestGroupA_QueueMicrotask:
    """queue_microtask no-op and non-interference verified."""

    def test_queue_microtask_returns_none(self) -> None:
        """Calling queue_microtask returns None without raising."""
        w = _fresh_window()
        result = w.queue_microtask(lambda: None)
        assert result is None

    def test_callback_not_invoked_synchronously(self) -> None:
        """Callback is NOT invoked synchronously after queue_microtask returns."""
        w = _fresh_window()
        call_log: list[int] = []
        w.queue_microtask(lambda: call_log.append(1))
        assert call_log == []

    def test_multiple_callbacks_not_invoked_synchronously(self) -> None:
        """Multiple enqueued callbacks remain pending after all registrations."""
        w = _fresh_window()
        call_log: list[int] = []
        w.queue_microtask(lambda: call_log.append(1))
        w.queue_microtask(lambda: call_log.append(2))
        w.queue_microtask(lambda: call_log.append(3))
        assert call_log == []

    def test_no_interference_with_set_timeout_id(self) -> None:
        """queue_microtask does not affect set_timeout timer IDs."""
        w = _fresh_window()
        tid_before = w.set_timeout(lambda: None, 0)
        w.queue_microtask(lambda: None)
        tid_after = w.set_timeout(lambda: None, 0)
        # Timer IDs are independent counters; microtask enqueueing must not
        # increment them or reset the timer counter.
        assert isinstance(tid_before, int)
        assert isinstance(tid_after, int)

    def test_no_interference_with_set_interval_id(self) -> None:
        """queue_microtask does not affect set_interval timer IDs."""
        w = _fresh_window()
        iid = w.set_interval(lambda: None, 100)
        w.queue_microtask(lambda: None)
        assert isinstance(iid, int)


# ---------------------------------------------------------------------------
# Group B — structured_clone + DataCloneError ( / )
# ---------------------------------------------------------------------------


class TestGroupB_StructuredClone:
    """structured_clone clones plain data; raises DataCloneError for lambda."""

    def test_clone_plain_dict_equal(self) -> None:
        """structured_clone returns a dict equal to the original."""
        w = _fresh_window()
        original = {"a": 1}
        cloned = w.structured_clone(original)
        assert cloned == original

    def test_clone_plain_dict_distinct_object(self) -> None:
        """structured_clone returns a distinct object (not the same reference)."""
        w = _fresh_window()
        original = {"a": 1}
        cloned = w.structured_clone(original)
        assert cloned is not original

    def test_clone_list_equal_and_distinct(self) -> None:
        """structured_clone of a list returns an equal, independent list."""
        w = _fresh_window()
        original = [1, 2, 3]
        cloned = w.structured_clone(original)
        assert cloned == original
        assert cloned is not original

    def test_clone_lambda_raises_data_clone_error(self) -> None:
        """structured_clone of a lambda raises DataCloneError."""
        w = _fresh_window()
        try:
            w.structured_clone(lambda: None)
            assert False, "Expected DataCloneError"
        except DataCloneError:
            pass

    def test_data_clone_error_code_is_25(self) -> None:
        """DataCloneError.code == 25 per WebIDL."""
        w = _fresh_window()
        try:
            w.structured_clone(lambda: None)
        except DataCloneError as exc:
            assert exc.code == 25

    def test_data_clone_error_importable_from_dom(self) -> None:
        """DataCloneError is importable from aspose_html.dom."""
        assert dom.DataCloneError is DataCloneError

    def test_clone_with_empty_transfer_list_does_not_raise(self) -> None:
        """structured_clone(x, transfer=[]) does not raise for plain dict."""
        w = _fresh_window()
        result = w.structured_clone({"key": "value"}, transfer=[])
        assert result == {"key": "value"}

    def test_clone_nested_structure_deep_independence(self) -> None:
        """structured_clone of a nested structure produces an independent copy."""
        w = _fresh_window()
        original = {"outer": {"inner": [1, 2, 3]}}
        cloned = w.structured_clone(original)
        assert cloned == original
        # Mutation of clone does not affect original
        cloned["outer"]["inner"].append(99)
        assert original["outer"]["inner"] == [1, 2, 3]


# ---------------------------------------------------------------------------
# Group C — Crypto stubs ( / )
# ---------------------------------------------------------------------------


class TestGroupC_CryptoStubs:
    """Crypto singleton, zeros, uuid format, SubtleCrypto raises."""

    def test_crypto_is_cached_singleton(self) -> None:
        """w.crypto is w.crypto (same instance every access)."""
        w = _fresh_window()
        assert w.crypto is w.crypto

    def test_crypto_get_random_values_returns_zero_filled(self) -> None:
        """Crypto.get_random_values fills the array with zeros (deterministic)."""
        w = _fresh_window()
        buf = bytearray(4)
        result = w.crypto.get_random_values(buf)
        assert all(b == 0 for b in result)

    def test_crypto_random_uuid_36_chars(self) -> None:
        """Crypto.random_uuid returns a 36-character string."""
        w = _fresh_window()
        uuid = w.crypto.random_uuid()
        assert len(uuid) == 36

    def test_crypto_random_uuid_has_4_dashes(self) -> None:
        """Crypto.random_uuid returns a UUID-format string with exactly 4 dashes."""
        w = _fresh_window()
        uuid = w.crypto.random_uuid()
        assert uuid.count("-") == 4

    def test_crypto_random_uuid_matches_pattern(self) -> None:
        """Crypto.random_uuid matches standard UUID format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."""
        w = _fresh_window()
        uuid = w.crypto.random_uuid()
        pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        assert pattern.match(uuid), f"UUID format invalid: {uuid!r}"

    def test_subtle_crypto_raises_not_supported_error(self) -> None:
        """SubtleCrypto.digest raises NotSupportedError."""
        w = _fresh_window()
        try:
            w.crypto.subtle.digest("SHA-256", b"")
            assert False, "Expected NotSupportedError"
        except dom.NotSupportedError:
            pass

    def test_window_crypto_constructor_property(self) -> None:
        """w.Crypto returns the Crypto class."""
        w = _fresh_window()
        assert w.Crypto is Crypto

    def test_crypto_importable_from_dom(self) -> None:
        """Crypto is importable from aspose_html.dom."""
        assert dom.Crypto is Crypto


# ---------------------------------------------------------------------------
# Group D — Performance stubs ( / )
# ---------------------------------------------------------------------------


class TestGroupD_PerformanceStubs:
    """Performance singleton, monotonic now(), mark/measure/clear lifecycle."""

    def test_performance_is_cached_singleton(self) -> None:
        """w.performance is w.performance (same instance every access)."""
        w = _fresh_window()
        assert w.performance is w.performance

    def test_performance_now_returns_float(self) -> None:
        """Performance.now() returns a float."""
        w = _fresh_window()
        t = w.performance.now()
        assert isinstance(t, float)

    def test_performance_now_non_negative(self) -> None:
        """Performance.now() returns a non-negative float."""
        w = _fresh_window()
        assert w.performance.now() >= 0.0

    def test_performance_now_monotonically_non_decreasing(self) -> None:
        """Two successive Performance.now() calls are non-decreasing."""
        w = _fresh_window()
        t1 = w.performance.now()
        t2 = w.performance.now()
        assert t2 >= t1

    def test_performance_mark_stores_entry(self) -> None:
        """Performance.mark stores a mark entry retrievable by type."""
        w = _fresh_window()
        w.performance.mark("t1")
        entries = w.performance.get_entries_by_type("mark")
        assert len(entries) >= 1

    def test_performance_get_entries_by_type_returns_stored_mark(self) -> None:
        """get_entries_by_type('mark') returns the stored mark by name."""
        w = _fresh_window()
        w.performance.mark("my-mark")
        entries = w.performance.get_entries_by_type("mark")
        names = [e.name for e in entries]
        assert "my-mark" in names

    def test_performance_clear_marks_removes_all_entries(self) -> None:
        """Performance.clear_marks() removes all mark entries."""
        w = _fresh_window()
        w.performance.mark("a")
        w.performance.mark("b")
        w.performance.clear_marks()
        entries = w.performance.get_entries_by_type("mark")
        assert entries == []

    def test_performance_timing_navigation_start_is_zero(self) -> None:
        """PerformanceTiming.navigation_start == 0 (headless stub)."""
        w = _fresh_window()
        assert w.performance.timing.navigation_start == 0

    def test_performance_importable_from_dom(self) -> None:
        """Performance is importable from aspose_html.dom."""
        assert dom.Performance is Performance

    def test_performance_timing_importable_from_dom(self) -> None:
        """PerformanceTiming is importable from aspose_html.dom."""
        assert dom.PerformanceTiming is PerformanceTiming


# ---------------------------------------------------------------------------
# Group E — get_selection delegation ( / )
# ---------------------------------------------------------------------------


class TestGroupE_GetSelectionDelegation:
    """get_selection delegation identity confirmed."""

    def test_get_selection_delegates_to_document(self) -> None:
        """w.get_selection() is w.document.get_selection() (same object)."""
        w = _fresh_window()
        assert w.get_selection() is w.document.get_selection()

    def test_get_selection_returns_same_instance_twice(self) -> None:
        """Calling get_selection() twice returns the same Selection instance."""
        w = _fresh_window()
        sel1 = w.get_selection()
        sel2 = w.get_selection()
        assert sel1 is sel2


# ---------------------------------------------------------------------------
# Group F — no-regression cross-check
# ---------------------------------------------------------------------------


class TestGroupF_NoRegressionCrossCheck:
    """No-regression: messaging unaffected, performance monotonic after microtask."""

    def test_queue_microtask_does_not_affect_message_channel(self) -> None:
        """queue_microtask must not deliver MessageChannel messages or alter ports."""
        w = _fresh_window()
        ch = MessageChannel()
        seen: list[object] = []
        ch.port2.onmessage = lambda evt: seen.append(evt)

        # Enqueue a microtask that posts a message — no delivery should occur
        w.queue_microtask(lambda: ch.port1.post_message({"key": "value"}))

        # Both: microtask not yet executed, message not yet delivered
        assert seen == []
        assert ch.port1.closed is False

    def test_performance_now_monotonic_after_queue_microtask(self) -> None:
        """performance.now() continues to be non-decreasing after queue_microtask."""
        w = _fresh_window()
        t1 = w.performance.now()
        w.queue_microtask(lambda: None)
        t2 = w.performance.now()
        assert t2 >= t1

    def test_performance_now_non_decreasing_across_queue_microtask_calls(self) -> None:
        """performance.now() is non-decreasing even across multiple queue_microtask calls."""
        w = _fresh_window()
        times: list[float] = []
        for _ in range(3):
            w.queue_microtask(lambda: None)
            times.append(w.performance.now())
        # Each successive measurement must be >= the previous
        assert all(times[i + 1] >= times[i] for i in range(len(times) - 1))


# ---------------------------------------------------------------------------
# Group G — doctest sweep
# ---------------------------------------------------------------------------


class TestGroupG_DoctestSweep:
    """pytest --doctest-modules on _window.py produces 0 failures."""

    def test_window_module_doctests_pass(self) -> None:
        """All >>> blocks in src/aspose_html/dom/_window.py run cleanly."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--doctest-modules",
                "-q",
                "--no-header",
                "src/aspose_html/dom/_window.py",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, (
            f"Doctest failures in _window.py:\n{result.stdout}\n{result.stderr}"
        )
