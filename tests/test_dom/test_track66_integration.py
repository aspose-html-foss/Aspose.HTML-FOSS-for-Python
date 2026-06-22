"""Track 66 Promise-job/rejection runtime boundary — integration matrix (BACK-271).

Covers finalized cross-module contracts from ADR-247/248/249 and SPEC-120:

- timer/macrotask dispatch remains explicit and deterministic relative to
  queueMicrotask and Promise-job checkpoint callbacks;
- Promise-job and unhandled-rejection callbacks are scheduled (never synchronous);
- bounded optional-runtime expectations remain explicit when QuickJS is absent.
"""

from __future__ import annotations

import pytest

from aspose_html.dom import Document


def test_track66_ordering_matrix_timer_then_microtask_then_promise_job() -> None:
    win = Document().default_view
    observed: list[str] = []

    win.set_timeout(lambda: observed.append("timer"), 0)
    win.queue_microtask(lambda: observed.append("queueMicrotask"))
    win._schedule_microtask_checkpoint(lambda: observed.append("promiseJob"), token=None)

    assert observed == []
    assert win._dispatch_timer_macrotasks() == 1
    win._event_loop.drain()

    assert observed == ["timer", "queueMicrotask", "promiseJob"]


def test_track66_ordering_matrix_microtask_then_promise_job_then_timer() -> None:
    win = Document().default_view
    observed: list[str] = []

    win.set_timeout(lambda: observed.append("timer"), 0)
    win.queue_microtask(lambda: observed.append("queueMicrotask"))
    win._schedule_microtask_checkpoint(lambda: observed.append("promiseJob"), token=None)

    assert observed == []
    win._event_loop.drain()
    assert win._dispatch_timer_macrotasks() == 1

    assert observed == ["queueMicrotask", "promiseJob", "timer"]


def test_track66_unhandled_rejection_delivery_is_non_synchronous_and_after_microtasks() -> None:
    win = Document().default_view
    observed: list[str] = []

    win.onunhandledrejection = lambda evt: observed.append(f"rejection:{evt.reason}")
    win.queue_microtask(lambda: observed.append("queueMicrotask"))
    win._queue_unhandled_rejection("boom")

    assert observed == []
    win._event_loop.drain()

    assert observed == ["queueMicrotask", "rejection:boom"]


def test_track66_quickjs_boundary_is_optional_and_explicit() -> None:
    quickjs = pytest.importorskip("quickjs")
    assert quickjs is not None

    from aspose_html.js import JSContext, JSEvaluationError

    doc = Document()
    with JSContext(doc) as ctx:
        with pytest.raises(JSEvaluationError, match="queueMicrotask callback must be callable"):
            ctx.evaluate("queueMicrotask(1)")
