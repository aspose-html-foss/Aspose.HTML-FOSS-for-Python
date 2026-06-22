"""Tests for EventTarget.add_event_listener once=True option (ADR-173, BACK-190).

Covers all eight test cases specified in ADR-173 §Testing.
"""
import pytest

from aspose_html.dom import EventTarget, Event, Document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_et() -> EventTarget:
    """Return a fresh standalone EventTarget."""
    return EventTarget()


def _fire(et: EventTarget, type_: str) -> None:
    """Dispatch a non-bubbling event of *type_* on *et*."""
    et.dispatch_event(Event(type_))


# ---------------------------------------------------------------------------
# Test 1: once fires once
# ---------------------------------------------------------------------------

def test_once_fires_exactly_once():
    """A once=True listener fires on first dispatch and is silent on subsequent ones."""
    et = _make_et()
    log: list[int] = []
    et.add_event_listener("ping", lambda e: log.append(1), once=True)
    _fire(et, "ping")
    _fire(et, "ping")
    assert log == [1], f"expected [1], got {log!r}"


# ---------------------------------------------------------------------------
# Test 2: once auto-remove — bucket empty after first fire
# ---------------------------------------------------------------------------

def test_once_auto_removed_after_dispatch():
    """After the first dispatch, the once listener is absent from the bucket."""
    et = _make_et()
    fn = lambda e: None  # noqa: E731
    et.add_event_listener("ping", fn, once=True)
    _fire(et, "ping")
    # Internal bucket must be empty (or key absent)
    bucket = (et._event_listeners or {}).get(("ping", False), [])
    assert bucket == [], f"bucket should be empty after once-dispatch, got {bucket!r}"


# ---------------------------------------------------------------------------
# Test 3: cancel before fire via remove_event_listener
# ---------------------------------------------------------------------------

def test_once_cancel_before_fire():
    """Cancelling a once=True listener before dispatch means it never fires."""
    et = _make_et()
    log: list[int] = []
    fn = lambda e: log.append(1)  # noqa: E731
    et.add_event_listener("ping", fn, once=True)
    et.remove_event_listener("ping", fn)
    _fire(et, "ping")
    assert log == [], f"expected [], got {log!r}"


# ---------------------------------------------------------------------------
# Test 4: non-once listeners unaffected
# ---------------------------------------------------------------------------

def test_non_once_fires_multiple_times():
    """A listener registered without once=True continues to fire on every dispatch."""
    et = _make_et()
    log: list[int] = []
    et.add_event_listener("ping", lambda e: log.append(1))
    _fire(et, "ping")
    _fire(et, "ping")
    assert log == [1, 1], f"expected [1, 1], got {log!r}"


# ---------------------------------------------------------------------------
# Test 5: idempotency — once flag excluded from identity key
# ---------------------------------------------------------------------------

def test_idempotency_once_flag_not_identity():
    """Registering the same (type, listener, capture) triple twice is a no-op.

    The once flag does NOT change the identity key — the first registration wins.
    """
    et = _make_et()
    log: list[int] = []
    fn = lambda e: log.append(1)  # noqa: E731
    # Register once=True first, then try to override with once=False
    et.add_event_listener("ping", fn, once=True)
    et.add_event_listener("ping", fn, once=False)  # no-op — same triple
    _fire(et, "ping")
    _fire(et, "ping")
    # First registration was once=True → fires only once
    assert log == [1], f"first-registration-wins; expected [1], got {log!r}"


# ---------------------------------------------------------------------------
# Test 6: capture + once combination
# ---------------------------------------------------------------------------

def test_capture_once_auto_removes_capture_listener():
    """once=True with capture=True auto-removes the capture-phase listener."""
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)

    log: list[str] = []
    parent.add_event_listener(
        "click",
        lambda e: log.append("capture"),
        capture=True,
        once=True,
    )
    child.dispatch_event(Event("click", bubbles=True))
    child.dispatch_event(Event("click", bubbles=True))
    assert log == ["capture"], f"capture-once should fire once; got {log!r}"


# ---------------------------------------------------------------------------
# Test 7: multiple once listeners on same event type
# ---------------------------------------------------------------------------

def test_multiple_once_listeners_each_fire_once():
    """Two different once=True listeners on the same event type both fire on
    the first dispatch and neither fires on the second."""
    et = _make_et()
    log_a: list[int] = []
    log_b: list[int] = []
    et.add_event_listener("ping", lambda e: log_a.append(1), once=True)
    et.add_event_listener("ping", lambda e: log_b.append(2), once=True)
    _fire(et, "ping")
    _fire(et, "ping")
    assert log_a == [1], f"listener A: expected [1], got {log_a!r}"
    assert log_b == [2], f"listener B: expected [2], got {log_b!r}"


# ---------------------------------------------------------------------------
# Test 8: existing event dispatch tests pass (regression guard)
# ---------------------------------------------------------------------------

def test_non_once_bubbling_regression():
    """Existing bubbling dispatch works correctly after the internal storage change."""
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)

    parent_log: list[int] = []
    child_log: list[int] = []
    parent.add_event_listener("click", lambda e: parent_log.append(1))
    child.add_event_listener("click", lambda e: child_log.append(1))
    result = child.dispatch_event(Event("click", bubbles=True))
    assert result is True
    assert child_log == [1]
    assert parent_log == [1]


def test_stop_propagation_regression():
    """stop_propagation() halts ancestor traversal — unaffected by storage change."""
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)

    parent_log: list[int] = []

    def stop_it(e: Event) -> None:
        e.stop_propagation()

    child.add_event_listener("click", stop_it)
    parent.add_event_listener("click", lambda e: parent_log.append(1))
    child.dispatch_event(Event("click", bubbles=True))
    assert parent_log == [], "stop_propagation should prevent parent from receiving event"


def test_remove_event_listener_regression():
    """remove_event_listener still works correctly after storage format change."""
    et = _make_et()
    log: list[int] = []
    fn = lambda e: log.append(1)  # noqa: E731
    et.add_event_listener("ping", fn)
    et.remove_event_listener("ping", fn)
    _fire(et, "ping")
    assert log == [], f"removed listener must not fire; got {log!r}"


def test_type_error_non_callable():
    """TypeError is raised when listener is not callable (unchanged behaviour)."""
    et = _make_et()
    with pytest.raises(TypeError):
        et.add_event_listener("ping", "not-a-callable")  # type: ignore[arg-type]
