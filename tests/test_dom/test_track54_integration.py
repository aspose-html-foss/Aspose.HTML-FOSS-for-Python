"""Track 54 integration hardening tests (BACK-237)."""

from __future__ import annotations

from aspose_html.dom import Document


class TestTrack54Integration:
    """Cross-scenario timer/task behavior matrix for headless Window timers."""

    def test_timeout_ordering_interval_repetition_and_cancellation_matrix(self) -> None:
        win = Document().default_view
        calls: list[str] = []

        t1 = win.set_timeout(lambda: calls.append("t1"), 0)
        i1 = win.set_interval(lambda: calls.append("i1"), 0)
        t2 = win.set_timeout(lambda: calls.append("t2"), 0)

        # FIFO order among newly registered timer handles.
        assert win._dispatch_timer_macrotasks(3) == 3
        assert calls == ["t1", "i1", "t2"]

        # Interval re-queues after execution.
        assert win._dispatch_timer_macrotasks(1) == 1
        assert calls == ["t1", "i1", "t2", "i1"]

        # Canceled timeouts are skipped when their queued handle is popped.
        t3 = win.set_timeout(lambda: calls.append("t3"), 0)
        win.clear_timeout(t3)
        # First turn executes the already re-queued interval.
        assert win._dispatch_timer_macrotasks(1) == 1
        assert calls == ["t1", "i1", "t2", "i1", "i1"]
        # Canceled handle is skipped without consuming execution budget,
        # so dispatcher continues and executes the next active interval task.
        assert win._dispatch_timer_macrotasks(1) == 1
        assert calls == ["t1", "i1", "t2", "i1", "i1", "i1"]

        # Canceling interval before its next turn suppresses future execution.
        win.clear_interval(i1)
        assert win._dispatch_timer_macrotasks(10) == 0
        assert calls == ["t1", "i1", "t2", "i1", "i1", "i1"]

    def test_zero_and_negative_dispatch_limits_are_noops(self) -> None:
        win = Document().default_view
        calls: list[str] = []

        win.set_timeout(lambda: calls.append("ran"), 0)

        assert win._dispatch_timer_macrotasks(0) == 0
        assert win._dispatch_timer_macrotasks(-5) == 0
        assert calls == []

        assert win._dispatch_timer_macrotasks(1) == 1
        assert calls == ["ran"]
