"""Tests for BACK-41 — DOM Events (EventTarget, Event, CustomEvent).

Acceptance criteria AC-1 through AC-12 are covered by named test functions.
Additional tests cover dispatch-algorithm correctness required by INV-005.
"""
from __future__ import annotations

import inspect

import pytest

from aspose_html.dom import Document, Event, CustomEvent, EventTarget, Node
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_doc_with_div() -> tuple[Document, object]:
    """Return (doc, div_element) with div appended to doc."""
    doc = Document()
    div = doc.create_element("div")
    doc.append_child(div)
    return doc, div


# ---------------------------------------------------------------------------
# AC-1, AC-2 — add_event_listener + dispatch_event invokes fn
# ---------------------------------------------------------------------------

def test_add_listener_and_dispatch():
    """AC-1, AC-2: add_event_listener + dispatch_event invokes fn."""
    doc, div = _make_doc_with_div()
    results = []
    div.add_event_listener("click", lambda e: results.append(e.type))
    returned = div.dispatch_event(Event("click"))
    assert results == ["click"]
    assert returned is True


# ---------------------------------------------------------------------------
# AC-3 — remove_event_listener
# ---------------------------------------------------------------------------

def test_remove_listener():
    """AC-3: remove_event_listener deregisters; subsequent dispatch doesn't call fn."""
    doc, div = _make_doc_with_div()
    results = []
    fn = lambda e: results.append(1)
    div.add_event_listener("click", fn)
    div.remove_event_listener("click", fn)
    div.dispatch_event(Event("click"))
    assert results == []


# ---------------------------------------------------------------------------
# AC-4 — idempotent registration
# ---------------------------------------------------------------------------

def test_idempotent_registration():
    """AC-4: same (type, listener, capture) triple registered twice stores only once."""
    doc, div = _make_doc_with_div()
    results = []
    fn = lambda e: results.append(1)
    div.add_event_listener("click", fn)
    div.add_event_listener("click", fn)  # duplicate
    div.dispatch_event(Event("click"))
    assert results == [1]  # only one invocation


# ---------------------------------------------------------------------------
# AC-5 — bubbling propagation
# ---------------------------------------------------------------------------

def test_bubbling_propagation():
    """AC-5: bubbling event on child propagates to parent."""
    doc, div = _make_doc_with_div()
    span = doc.create_element("span")
    div.append_child(span)

    parent_calls = []
    div.add_event_listener("click", lambda e: parent_calls.append(1))
    span.dispatch_event(Event("click", bubbles=True))
    assert parent_calls == [1]


# ---------------------------------------------------------------------------
# AC-6 — stop_propagation
# ---------------------------------------------------------------------------

def test_stop_propagation():
    """AC-6: stop_propagation() prevents parent from receiving event."""
    doc, div = _make_doc_with_div()
    span = doc.create_element("span")
    div.append_child(span)

    parent_calls = []
    span.add_event_listener("click", lambda e: e.stop_propagation())
    div.add_event_listener("click", lambda e: parent_calls.append(1))
    span.dispatch_event(Event("click", bubbles=True))
    assert parent_calls == []


# ---------------------------------------------------------------------------
# AC-7 — prevent_default
# ---------------------------------------------------------------------------

def test_prevent_default():
    """AC-7: prevent_default() causes dispatch_event to return False."""
    doc, div = _make_doc_with_div()
    div.add_event_listener("submit", lambda e: e.prevent_default())
    result = div.dispatch_event(Event("submit", cancelable=True))
    assert result is False


# ---------------------------------------------------------------------------
# AC-8 — CustomEvent detail
# ---------------------------------------------------------------------------

def test_custom_event_detail():
    """AC-8: CustomEvent detail payload preserved."""
    payload = {"key": "val", "num": 42}
    ev = CustomEvent("change", detail=payload)
    assert ev.detail is payload
    assert ev.type == "change"
    assert isinstance(ev, Event)


# ---------------------------------------------------------------------------
# AC-9 — Event importable from aspose_html.dom
# ---------------------------------------------------------------------------

def test_event_importable():
    """AC-9: Event and CustomEvent importable from aspose_html.dom."""
    from aspose_html.dom import Event as E, CustomEvent as CE
    e = E("test")
    assert isinstance(e, E)
    ce = CE("test2", detail=None)
    assert isinstance(ce, CE)
    assert isinstance(ce, E)


# ---------------------------------------------------------------------------
# AC-10 — EventTarget importable from aspose_html.dom
# ---------------------------------------------------------------------------

def test_event_target_importable():
    """AC-10: EventTarget importable from aspose_html.dom; Node instances are EventTargets."""
    from aspose_html.dom import EventTarget as ET
    doc = Document()
    el = doc.create_element("p")
    assert isinstance(el, ET)
    assert isinstance(doc, ET)


# ---------------------------------------------------------------------------
# AC-11 — type hints and docstrings
# ---------------------------------------------------------------------------

def test_type_hints():
    """AC-11: methods have type hints (spot check via inspect)."""
    # Event
    sig = inspect.signature(Event.__init__)
    params = sig.parameters
    assert "type" in params
    assert params["type"].annotation == str
    assert params["bubbles"].annotation == bool
    assert params["cancelable"].annotation == bool

    # CustomEvent
    sig_ce = inspect.signature(CustomEvent.__init__)
    assert "detail" in sig_ce.parameters

    # EventTarget public methods
    for method_name in ("add_event_listener", "remove_event_listener", "dispatch_event"):
        method = getattr(EventTarget, method_name)
        hints = inspect.get_annotations(method, eval_str=False)
        # Every method should have at least a 'return' annotation
        assert "return" in hints or len(hints) > 0, (
            f"EventTarget.{method_name} missing type hints"
        )

    # All public methods on Event have docstrings
    for name in ("prevent_default", "stop_propagation", "stop_immediate_propagation"):
        method = getattr(Event, name)
        assert method.__doc__, f"Event.{name} missing docstring"

    # All public methods on EventTarget have docstrings
    for name in ("add_event_listener", "remove_event_listener", "dispatch_event"):
        method = getattr(EventTarget, name)
        assert method.__doc__, f"EventTarget.{name} missing docstring"


# ---------------------------------------------------------------------------
# AC-12 — non-regression: existing Node operations unaffected
# ---------------------------------------------------------------------------

def test_all_existing_tests_unaffected():
    """AC-12: Node subclass instances still work as DOM nodes (non-regression)."""
    # Create a full document tree and verify basic DOM operations are intact.
    doc = Document()
    html = doc.create_element("html")
    body = doc.create_element("body")
    p = doc.create_element("p")
    t = doc.create_text_node("Hello world")

    doc.append_child(html)
    html.append_child(body)
    body.append_child(p)
    p.append_child(t)

    assert p.parent_node is body
    assert p.first_child is t
    assert body.first_child is p
    assert t.node_value == "Hello world"
    assert doc.get_root_node() is doc
    assert doc.contains(t)

    # Serialisation via HTMLDocument is also unaffected.
    html_doc = HTMLDocument.parse("<div class='box'>text</div>")
    divs = html_doc.query_selector_all("div")
    assert len(divs) == 1
    assert divs[0].get_attribute("class") == "box"


# ---------------------------------------------------------------------------
# Bonus: capture-phase fires before at-target
# ---------------------------------------------------------------------------

def test_capture_phase():
    """Bonus: capture=True listener fires in capture phase, not bubble."""
    doc, div = _make_doc_with_div()
    span = doc.create_element("span")
    div.append_child(span)

    order = []
    div.add_event_listener("click", lambda e: order.append("capture"), capture=True)
    span.add_event_listener("click", lambda e: order.append("at-target"))
    span.dispatch_event(Event("click"))
    assert order == ["capture", "at-target"]


# ---------------------------------------------------------------------------
# Bonus: stop_immediate_propagation prevents second listener on same target
# ---------------------------------------------------------------------------

def test_stop_immediate_propagation():
    """Two listeners on same element; first calls stop_immediate_propagation(); second not fired."""
    doc, div = _make_doc_with_div()
    results = []

    def first(e):
        results.append("first")
        e.stop_immediate_propagation()

    def second(e):
        results.append("second")

    div.add_event_listener("click", first)
    div.add_event_listener("click", second)
    div.dispatch_event(Event("click"))
    assert results == ["first"]


# ---------------------------------------------------------------------------
# Bonus: snapshot semantics — listener added during dispatch not invoked
# ---------------------------------------------------------------------------

def test_snapshot_semantics():
    """Listener added inside dispatch is NOT invoked for the current event."""
    doc, div = _make_doc_with_div()
    added_during: list[int] = []

    def outer(e):
        div.add_event_listener("click", lambda e2: added_during.append(1))

    div.add_event_listener("click", outer)
    div.dispatch_event(Event("click"))
    assert added_during == []  # not called this dispatch

    div.dispatch_event(Event("click"))
    assert added_during == [1]  # called on second dispatch


# ---------------------------------------------------------------------------
# Bonus: re-dispatch guard raises ValueError
# ---------------------------------------------------------------------------

def test_redispatch_guard():
    """dispatch_event raises ValueError if the event is already in dispatch."""
    doc, div = _make_doc_with_div()
    span = doc.create_element("span")
    div.append_child(span)

    event = Event("click", bubbles=True)
    errors: list[Exception] = []

    def try_redispatch(e):
        try:
            div.dispatch_event(e)
        except ValueError as exc:
            errors.append(exc)

    div.add_event_listener("click", try_redispatch)
    div.dispatch_event(event)
    assert len(errors) == 1
    assert "already being dispatched" in str(errors[0])


# ---------------------------------------------------------------------------
# Bonus: prevent_default is no-op when cancelable=False
# ---------------------------------------------------------------------------

def test_prevent_default_non_cancelable():
    """prevent_default() is a no-op when cancelable=False."""
    e = Event("click", cancelable=False)
    e.prevent_default()
    assert e.default_prevented is False


def test_init_event_updates_state_pre_dispatch():
    """BACK-121: init_event updates mutable state before dispatch."""
    e = Event("click", bubbles=False, cancelable=False)
    e.prevent_default()

    e.init_event("submit", True, True)

    assert e.type == "submit"
    assert e.bubbles is True
    assert e.cancelable is True
    assert e.target is None
    assert e.current_target is None
    assert e.event_phase == Event.NONE
    assert e.default_prevented is False


def test_init_event_refuses_mutation_during_dispatch():
    """BACK-121: init_event is a no-op while the event is in dispatch."""
    doc, div = _make_doc_with_div()
    e = Event("click", bubbles=False, cancelable=False)
    seen: list[tuple[str, bool, bool]] = []

    def listener(ev: Event) -> None:
        ev.init_event("submit", True, True)
        seen.append((ev.type, ev.bubbles, ev.cancelable))

    div.add_event_listener("click", listener)
    div.dispatch_event(e)

    assert seen == [("click", False, False)]
    assert e.type == "click"
    assert e.bubbles is False
    assert e.cancelable is False


def test_init_custom_event_updates_state_pre_dispatch():
    """BACK-122: init_custom_event updates core fields and detail."""
    ev = CustomEvent("change", bubbles=False, cancelable=False, detail={"v": 1})
    ev.prevent_default()

    payload = {"v": 2}
    ev.init_custom_event("update", True, True, payload)

    assert ev.type == "update"
    assert ev.bubbles is True
    assert ev.cancelable is True
    assert ev.detail is payload
    assert ev.target is None
    assert ev.current_target is None
    assert ev.event_phase == Event.NONE
    assert ev.default_prevented is False


def test_init_custom_event_refuses_mutation_during_dispatch():
    """BACK-122: init_custom_event is a no-op during dispatch."""
    doc, div = _make_doc_with_div()
    ev = CustomEvent("change", bubbles=False, cancelable=False, detail={"v": 1})
    seen: list[tuple[str, bool, bool, object]] = []

    def listener(event: Event) -> None:
        assert isinstance(event, CustomEvent)
        custom = event
        custom.init_custom_event("update", True, True, {"v": 2})
        seen.append((custom.type, custom.bubbles, custom.cancelable, custom.detail))

    div.add_event_listener("change", listener)
    div.dispatch_event(ev)

    assert seen == [("change", False, False, {"v": 1})]
    assert ev.type == "change"
    assert ev.bubbles is False
    assert ev.cancelable is False
    assert ev.detail == {"v": 1}


# ---------------------------------------------------------------------------
# Bonus: standalone EventTarget (not a Node) works correctly
# ---------------------------------------------------------------------------

def test_standalone_event_target():
    """EventTarget used standalone (no _parent) dispatches events correctly."""
    et = EventTarget()
    results = []
    et.add_event_listener("ping", lambda e: results.append(e.type))
    returned = et.dispatch_event(Event("ping"))
    assert results == ["ping"]
    assert returned is True


# ---------------------------------------------------------------------------
# Bonus: remove_event_listener is no-op when listener not registered
# ---------------------------------------------------------------------------

def test_remove_listener_noop():
    """remove_event_listener is a no-op when listener was never registered."""
    doc, div = _make_doc_with_div()
    fn = lambda e: None
    # Should not raise
    div.remove_event_listener("click", fn)


# ---------------------------------------------------------------------------
# Bonus: add_event_listener raises TypeError for non-callable
# ---------------------------------------------------------------------------

def test_add_listener_type_error():
    """add_event_listener raises TypeError for non-callable listener."""
    doc, div = _make_doc_with_div()
    with pytest.raises(TypeError):
        div.add_event_listener("click", "not_callable")


# ---------------------------------------------------------------------------
# Regression: WHATWG §2.9.6 — stop_propagation must not skip at-target phase
# ---------------------------------------------------------------------------

def test_stop_propagation_does_not_skip_at_target():
    """stop_propagation() on ancestor must not prevent the target from firing.

    WHATWG DOM §2.9.6: stop_propagation halts traversal *between* nodes in
    the ancestor chain. The dispatch target always executes unconditionally.
    """
    doc, div = _make_doc_with_div()
    span = doc.create_element("span")
    div.append_child(span)
    results: list[str] = []
    div.add_event_listener("click", lambda e: e.stop_propagation(), capture=True)
    span.add_event_listener("click", lambda e: results.append("at-target"))
    span.dispatch_event(Event("click", bubbles=True))
    assert results == ["at-target"]
