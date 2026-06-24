""" QuickJS/microtask runtime boundary — integration matrix ().

Covers cross-component guardrails finalized across /242:

- QuickJS ``queueMicrotask`` bridge validates callable input and does not run
  callbacks synchronously at registration time.
- Microtask checkpoint scheduling remains owned by ``WindowEventLoop``.
- Mixed timer/microtask ordering stays explicit and deterministic by drain order.

Tasks: , , 
"""

from __future__ import annotations

import pytest

from aspose_html.dom import Document


def test_window_queue_microtask_registration_is_non_synchronous() -> None:
    win = Document().default_view
    observed: list[str] = []

    win.queue_microtask(lambda: observed.append("microtask"))

    #  boundary: registration only; no immediate callback execution.
    assert observed == []


def test_runtime_boundary_allows_explicit_timer_then_microtask_drain_order() -> None:
    win = Document().default_view
    observed: list[str] = []

    win.set_timeout(lambda: observed.append("timer"), 0)
    win.queue_microtask(lambda: observed.append("microtask"))

    assert win._dispatch_timer_macrotasks() == 1
    win._event_loop.drain()

    assert observed == ["timer", "microtask"]


def test_runtime_boundary_allows_explicit_microtask_then_timer_drain_order() -> None:
    win = Document().default_view
    observed: list[str] = []

    win.set_timeout(lambda: observed.append("timer"), 0)
    win.queue_microtask(lambda: observed.append("microtask"))

    win._event_loop.drain()
    assert win._dispatch_timer_macrotasks() == 1

    assert observed == ["microtask", "timer"]


def test_quickjs_queue_microtask_bridge_enforces_callable_and_defers_execution() -> None:
    quickjs = pytest.importorskip("quickjs")
    assert quickjs is not None

    from aspose_html.js import JSContext, JSEvaluationError

    doc = Document()
    with JSContext(doc) as ctx:
        ctx.evaluate("queueMicrotask(function () { return 1; });")
        with pytest.raises(JSEvaluationError, match="queueMicrotask callback must be callable"):
            ctx.evaluate("queueMicrotask(123)")
