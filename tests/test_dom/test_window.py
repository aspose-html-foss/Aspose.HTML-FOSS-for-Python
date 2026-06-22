import pytest
import importlib
import sys

from aspose_html.dom import (
    BroadcastChannel,
    Crypto,
    DataCloneError,
    Event,
    EventTarget,
    IntersectionObserver,
    IntersectionObserverEntry,
    MessageChannel,
    MessagePort,
    Performance,
    PerformanceEntry,
    PerformanceTiming,
    ResizeObserver,
    ResizeObserverEntry,
    Screen,
    SecurityError,
    Selection,
    SubtleCrypto,
    set_default_user_agent,
)
from aspose_html.dom._document import Document
from aspose_html.dom._exceptions import NotSupportedError
from aspose_html.dom._window_event_loop import WindowEventLoop
from aspose_html.html_document import HTMLDocument
from aspose_html.url import URL


def test_default_view_lazy_and_cached():
    doc = HTMLDocument.parse("<p>x</p>")
    assert doc._get_cached_default_view() is None
    w1 = doc.default_view
    w2 = doc.default_view
    assert w1 is w2
    assert doc._get_cached_default_view() is w1
    assert w1.document is doc


def test_window_is_per_document():
    d1 = HTMLDocument.parse("<p>a</p>")
    d2 = HTMLDocument.parse("<p>b</p>")
    assert d1.default_view is not d2.default_view


def test_optional_js_dependency_absence_does_not_break_dom_import(monkeypatch):
    """aspose_html.js import failure must not affect aspose_html.dom usage."""
    from aspose_html.dom import Document as DomDocument

    doc = DomDocument()
    assert doc.default_view is not None

    saved = sys.modules.pop("quickjs", None)
    saved_js = sys.modules.pop("aspose_html.js", None)
    saved_bridge = sys.modules.pop("aspose_html.js._quickjs_bridge", None)
    monkeypatch.setitem(sys.modules, "quickjs", None)

    try:
        with pytest.raises(ImportError, match="requires the 'quickjs' package"):
            importlib.import_module("aspose_html.js")
        # DOM path remains healthy after js import failure.
        assert DomDocument().default_view is not None
    finally:
        if saved is not None:
            sys.modules["quickjs"] = saved
        else:
            sys.modules.pop("quickjs", None)
        if saved_js is not None:
            sys.modules["aspose_html.js"] = saved_js
        if saved_bridge is not None:
            sys.modules["aspose_html.js._quickjs_bridge"] = saved_bridge


def test_navigator_user_agent_default_override():
    set_default_user_agent("UnitTestUA/1")
    d = HTMLDocument.parse("<p>x</p>")
    assert "UnitTestUA/1" in d.default_view.navigator.user_agent


def test_window_is_event_target_and_dispatches_listeners():
    d = HTMLDocument.parse("<p>x</p>")
    w = d.default_view
    assert isinstance(w, EventTarget)
    calls = []
    w.add_event_listener("ping", lambda e: calls.append(e.type))
    assert w.dispatch_event(Event("ping")) is True
    assert calls == ["ping"]


def test_window_exposes_observer_constructors() -> None:
    win = Document().default_view

    assert win.IntersectionObserver is IntersectionObserver
    assert win.ResizeObserver is ResizeObserver


def test_intersection_observer_stub_methods_are_deterministic_noops() -> None:
    win = Document().default_view
    seen = []

    observer = win.IntersectionObserver(lambda entries, obs: seen.append((entries, obs)))
    target = win.document.create_element("div")

    observer.observe(target)
    observer.unobserve(target)
    observer.disconnect()

    records = observer.take_records()
    assert records == []
    assert isinstance(records, list)
    assert seen == []


def test_resize_observer_stub_methods_are_deterministic_noops() -> None:
    win = Document().default_view
    seen = []

    observer = win.ResizeObserver(lambda entries, obs: seen.append((entries, obs)))
    target = win.document.create_element("div")

    observer.observe(target)
    observer.unobserve(target)
    observer.disconnect()

    records = observer.take_records()
    assert records == []
    assert isinstance(records, list)
    assert seen == []


def test_observer_entry_types_are_publicly_instantiable() -> None:
    assert isinstance(IntersectionObserverEntry(), IntersectionObserverEntry)
    assert isinstance(ResizeObserverEntry(), ResizeObserverEntry)


def test_window_exposes_message_constructor_references() -> None:
    win = Document().default_view

    assert win.MessagePort is MessagePort
    assert win.MessageChannel is MessageChannel
    assert win.BroadcastChannel is BroadcastChannel


def test_message_channel_constructor_creates_two_ports() -> None:
    channel = MessageChannel()

    assert isinstance(channel.port1, MessagePort)
    assert isinstance(channel.port2, MessagePort)
    assert channel.port1 is not channel.port2


def test_message_port_lifecycle_is_idempotent() -> None:
    port = MessageChannel().port1

    assert port.closed is False
    port.start()
    port.start()
    assert port.closed is False

    port.close()
    port.close()
    assert port.closed is True


def test_message_channel_post_message_is_queued_until_event_loop_drain() -> None:
    channel = MessageChannel()
    seen = []
    channel.port2.onmessage = lambda evt: seen.append(evt)
    channel.port2.start()

    channel.port1.post_message({"payload": 1})
    channel.port1.post_message("text")

    assert seen == []
    channel.port1._event_loop.drain()
    assert seen == [{"payload": 1}, "text"]


def test_message_channel_post_message_snapshots_payload_at_enqueue_boundary() -> None:
    channel = MessageChannel()
    seen = []
    channel.port2.onmessage = lambda evt: seen.append(evt)
    channel.port2.start()

    payload = {"nested": [1]}
    channel.port1.post_message(payload)
    payload["nested"].append(2)

    channel.port1._event_loop.drain()
    assert seen == [{"nested": [1]}]


def test_message_channel_post_message_raises_data_clone_error_for_non_cloneable_payload() -> None:
    channel = MessageChannel()

    with pytest.raises(DataCloneError):
        channel.port1.post_message(lambda: None)


def test_message_channel_closed_port_invalid_state_error_precedes_clone_error() -> None:
    from aspose_html.dom import InvalidStateError

    channel = MessageChannel()
    channel.port1.close()

    with pytest.raises(InvalidStateError):
        channel.port1.post_message(lambda: None)


def test_message_channel_post_message_does_not_dispatch_when_target_not_started() -> None:
    channel = MessageChannel()
    seen = []
    channel.port2.onmessage = lambda evt: seen.append(evt)

    channel.port1.post_message("first")
    channel.port1._event_loop.drain()
    assert seen == []

    channel.port2.start()
    channel.port1.post_message("second")
    channel.port1._event_loop.drain()
    assert seen == ["first", "second"]


def test_message_port_close_gates_post_message_with_invalid_state_error() -> None:
    from aspose_html.dom import InvalidStateError

    channel = MessageChannel()
    channel.port1.close()

    with pytest.raises(InvalidStateError):
        channel.port1.post_message("x")


def test_broadcast_channel_constructor_and_name_are_stable() -> None:
    channel = BroadcastChannel("updates")

    assert channel.name == "updates"
    channel.close()


def test_broadcast_channel_post_message_fanout_is_queued_until_event_loop_drain() -> None:
    sender = BroadcastChannel("updates")
    receiver = BroadcastChannel("updates")
    seen = []
    receiver.onmessage = lambda evt: seen.append(evt)

    sender.post_message({"payload": 1})
    sender.post_message("text")

    assert seen == []
    sender._event_loop.drain()
    assert seen == [{"payload": 1}, "text"]

    sender.close()
    receiver.close()


def test_broadcast_channel_post_message_snapshots_payload_for_each_sibling() -> None:
    sender = BroadcastChannel("updates")
    receiver_a = BroadcastChannel("updates")
    receiver_b = BroadcastChannel("updates")
    seen_a = []
    seen_b = []
    receiver_a.onmessage = lambda evt: seen_a.append(evt)
    receiver_b.onmessage = lambda evt: seen_b.append(evt)

    payload = {"nested": [1]}
    sender.post_message(payload)
    payload["nested"].append(2)

    sender._event_loop.drain()

    assert seen_a == [{"nested": [1]}]
    assert seen_b == [{"nested": [1]}]
    # Each dispatch carries its own cloned snapshot object.
    assert seen_a[0] is not seen_b[0]

    sender.close()
    receiver_a.close()
    receiver_b.close()


def test_broadcast_channel_post_message_raises_data_clone_error_for_non_cloneable_payload() -> None:
    sender = BroadcastChannel("updates")
    receiver = BroadcastChannel("updates")

    with pytest.raises(DataCloneError):
        sender.post_message(lambda: None)

    sender.close()
    receiver.close()


def test_broadcast_channel_closed_invalid_state_error_precedes_clone_error() -> None:
    from aspose_html.dom import InvalidStateError

    channel = BroadcastChannel("updates")
    channel.close()

    with pytest.raises(InvalidStateError):
        channel.post_message(lambda: None)


def test_broadcast_channel_excludes_sender_self_delivery() -> None:
    sender = BroadcastChannel("updates")
    seen = []
    sender.onmessage = lambda evt: seen.append(evt)

    sender.post_message("no-self")
    sender._event_loop.drain()

    assert seen == []
    sender.close()


def test_broadcast_channel_delivery_targets_open_same_name_only() -> None:
    sender = BroadcastChannel("updates")
    receiver_open = BroadcastChannel("updates")
    receiver_other_name = BroadcastChannel("other")
    receiver_closed = BroadcastChannel("updates")
    seen_open = []
    seen_other = []
    seen_closed = []
    receiver_open.onmessage = lambda evt: seen_open.append(evt)
    receiver_other_name.onmessage = lambda evt: seen_other.append(evt)
    receiver_closed.onmessage = lambda evt: seen_closed.append(evt)
    receiver_closed.close()

    sender.post_message("payload")
    sender._event_loop.drain()

    assert seen_open == ["payload"]
    assert seen_other == []
    assert seen_closed == []

    sender.close()
    receiver_open.close()
    receiver_other_name.close()


def test_broadcast_channel_close_is_idempotent() -> None:
    channel = BroadcastChannel("updates")

    channel.close()
    channel.close()


def test_broadcast_channel_post_message_on_closed_channel_raises_invalid_state_error() -> None:
    from aspose_html.dom import InvalidStateError

    channel = BroadcastChannel("updates")
    channel.close()

    with pytest.raises(InvalidStateError):
        channel.post_message("closed")


def test_broadcast_channel_close_unregisters_from_future_fanout() -> None:
    sender = BroadcastChannel("updates")
    receiver = BroadcastChannel("updates")
    seen = []
    receiver.onmessage = lambda evt: seen.append(evt)

    receiver.close()
    sender.post_message("dropped")
    sender._event_loop.drain()

    assert seen == []

    sender.close()



def test_request_idle_callback_returns_int_and_does_not_auto_invoke_callback() -> None:
    win = Document().default_view
    seen = []

    callback_id = win.request_idle_callback(lambda deadline=None: seen.append(deadline))

    assert isinstance(callback_id, int)
    assert seen == []


def test_cancel_idle_callback_is_idempotent_and_safe_for_unknown_ids() -> None:
    win = Document().default_view
    callback_id = win.request_idle_callback(lambda *_: None)

    win.cancel_idle_callback(callback_id)
    win.cancel_idle_callback(callback_id)
    win.cancel_idle_callback(999_999)


def test_window_dispatch_stop_immediate_propagation():
    d = HTMLDocument.parse("<p>x</p>")
    w = d.default_view
    calls = []

    def first(evt):
        calls.append("first")
        evt.stop_immediate_propagation()

    def second(evt):
        calls.append("second")

    w.add_event_listener("stop", first)
    w.add_event_listener("stop", second)
    w.dispatch_event(Event("stop"))
    assert calls == ["first"]


def test_location_assign_replace_and_hash():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start?q=1"
    w = d.default_view
    h = w.history

    assert h.length == 1
    w.location.assign("/next")
    assert w.location.href == "https://example.com/next"
    assert h.length == 2

    w.location.replace("/replaced")
    assert w.location.href == "https://example.com/replaced"
    assert h.length == 2

    w.location.hash = "frag"
    assert w.location.href == "https://example.com/replaced#frag"
    assert h.length == 3

    w.location.hash = "#frag"
    assert h.length == 3


def test_location_href_setter_valid_same_document_uses_replace_semantics() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history
    before_length = h.length

    w.location.href = "/next?x=1#f"

    assert w.location.href == "https://example.com/next?x=1#f"
    assert d.url == "https://example.com/next?x=1#f"
    assert h.length == before_length


def test_location_hash_effective_change_dispatches_hashchange_once() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/p"
    w = d.default_view
    seen = []

    w.add_event_listener("hashchange", lambda evt: seen.append((evt.old_url, evt.new_url)))

    w.location.hash = "frag"

    assert seen == [("https://example.com/p", "https://example.com/p#frag")]


def test_location_hash_equivalent_write_does_not_dispatch_hashchange() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/p#frag"
    w = d.default_view
    seen = []

    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    w.location.hash = "#frag"

    assert seen == []


def test_location_href_hash_only_change_dispatches_hashchange_without_growing_history() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/p#one"
    w = d.default_view
    h = w.history
    before_length = h.length
    seen = []

    w.add_event_listener("hashchange", lambda evt: seen.append((evt.old_url, evt.new_url)))

    w.location.href = "https://example.com/p#two"

    assert seen == [("https://example.com/p#one", "https://example.com/p#two")]
    assert h.length == before_length


def test_location_href_non_hash_change_does_not_dispatch_hashchange() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/p#one"
    w = d.default_view
    seen = []

    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    w.location.href = "https://example.com/q#one"

    assert seen == []


def test_location_href_setter_cross_origin_failure_is_atomic() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history
    before_href = w.location.href
    before_doc_url = d.url
    before_length = h.length
    before_state = h.state
    seen = []
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    with pytest.raises(SecurityError):
        w.location.href = "https://other.example/next"

    assert w.location.href == before_href
    assert d.url == before_doc_url
    assert h.length == before_length
    assert h.state == before_state
    assert seen == []


def test_location_href_setter_invalid_text_failure_is_atomic() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history
    before_href = w.location.href
    before_doc_url = d.url
    before_length = h.length
    before_state = h.state
    seen = []
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    with pytest.raises(SecurityError, match="invalid URL"):
        w.location.href = "http://[::1"

    assert w.location.href == before_href
    assert d.url == before_doc_url
    assert h.length == before_length
    assert h.state == before_state
    assert seen == []


def test_location_href_setter_equivalent_write_is_strict_noop() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/a/b"
    w = d.default_view
    h = w.history
    before_href = w.location.href
    before_doc_url = d.url
    before_length = h.length
    before_state = h.state

    w.location.href = "https://example.com/a/b"

    assert w.location.href == before_href
    assert d.url == before_doc_url
    assert h.length == before_length
    assert h.state == before_state


def test_location_protocol_setter_cross_origin_is_atomic():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "http://example.com/start?q=1"
    w = d.default_view
    h = w.history
    before_href = w.location.href
    before_len = h.length
    before_state = h.state

    with pytest.raises(SecurityError):
        w.location.protocol = "https"

    assert w.location.href == before_href
    assert d._url == before_href
    assert h.length == before_len
    assert h.state == before_state


def test_location_protocol_setter_normalizes_and_noop():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history
    before_len = h.length

    w.location.protocol = "https:"

    assert w.location.href == "https://example.com/start"
    assert h.length == before_len


def test_location_host_setter_same_value_is_noop():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com:8080/start"
    w = d.default_view
    h = w.history
    before_len = h.length

    w.location.host = "example.com:8080"

    assert w.location.hostname == "example.com"
    assert w.location.port == "8080"
    assert w.location.href == "https://example.com:8080/start"
    assert d._url == "https://example.com:8080/start"
    assert h.length == before_len


def test_location_host_setter_cross_origin_change_is_atomic_failure():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com:8080/start?q=1#frag"
    w = d.default_view
    h = w.history
    before_href = w.location.href
    before_len = h.length
    before_state = h.state

    with pytest.raises(SecurityError):
        w.location.host = "other.example:8080"

    assert w.location.href == before_href
    assert d._url == before_href
    assert h.length == before_len
    assert h.state == before_state


def test_location_hostname_setter_cross_origin_is_atomic():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com:8080/p?q=1#frag"
    w = d.default_view
    h = w.history
    before_href = w.location.href
    before_len = h.length
    before_state = h.state

    with pytest.raises(SecurityError):
        w.location.hostname = "other.example"

    assert w.location.href == before_href
    assert d._url == before_href
    assert h.length == before_len
    assert h.state == before_state


def test_location_hostname_setter_same_value_is_noop():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com:8080/p?q=1#frag"
    w = d.default_view
    h = w.history
    before_len = h.length

    w.location.hostname = "example.com"

    assert w.location.href == "https://example.com:8080/p?q=1#frag"
    assert d._url == "https://example.com:8080/p?q=1#frag"
    assert h.length == before_len


def test_location_port_setter_cross_origin_is_atomic():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/p"
    w = d.default_view
    h = w.history
    before_href = w.location.href
    before_len = h.length
    before_state = h.state

    with pytest.raises(SecurityError):
        w.location.port = "8443"

    assert w.location.href == before_href
    assert w.location.port == ""
    assert d._url == before_href
    assert h.length == before_len
    assert h.state == before_state


def test_location_port_setter_same_value_is_noop():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com:8443/p"
    w = d.default_view
    h = w.history
    before_len = h.length

    w.location.port = "8443"

    assert w.location.href == "https://example.com:8443/p"
    assert w.location.port == "8443"
    assert d._url == "https://example.com:8443/p"
    assert h.length == before_len


def test_location_pathname_setter_prepends_slash_when_missing():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view

    w.location.pathname = "next"

    assert w.location.href == "https://example.com/next"
    assert d._url == "https://example.com/next"


def test_location_search_setter_prefixes_question_and_clears_query():
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/p?q=1"
    w = d.default_view

    w.location.search = "a=2"
    assert w.location.href == "https://example.com/p?a=2"
    assert w.location.search == "?a=2"

    w.location.search = ""
    assert w.location.href == "https://example.com/p"
    assert w.location.search == ""


def test_location_search_roundtrip_determinism_via_url_delegation() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/p"
    w = d.default_view
    h = w.history
    before_len = h.length

    w.location.search = "q=hello%20world&x=%2B"
    assert w.location.search == "?q=hello%20world&x=%2B"

    candidate = URL(w.location.href)
    candidate.search_params.append("q", "tail")
    w.location.replace(candidate.href)

    assert w.location.search == "?q=hello+world&x=%2B&q=tail"
    assert d._url == "https://example.com/p?q=hello+world&x=%2B&q=tail"
    assert h.length == before_len


def test_location_component_writes_canonicalize_and_repeat_noop() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/a/./b?q=1#frag"
    w = d.default_view
    h = w.history

    initial_len = h.length
    w.location.pathname = "/a/b"
    assert w.location.href == "https://example.com/a/b?q=1#frag"
    assert d._url == "https://example.com/a/b?q=1#frag"
    assert h.length == initial_len

    w.location.search = ""
    assert w.location.href == "https://example.com/a/b#frag"
    assert d._url == "https://example.com/a/b#frag"
    assert h.length == initial_len

    w.location.search = ""
    assert w.location.href == "https://example.com/a/b#frag"
    assert h.length == initial_len

    w.location.hash = ""
    assert w.location.href == "https://example.com/a/b"
    assert d._url == "https://example.com/a/b"
    assert h.length == initial_len + 1

    w.location.hash = ""
    assert w.location.href == "https://example.com/a/b"
    assert h.length == initial_len + 1


@pytest.mark.parametrize(
    "setter,value,expected_exc",
    [
        ("protocol", "   ", ValueError),
        ("host", "bad host", SecurityError),
        ("hostname", "bad host", SecurityError),
        ("port", "99999", ValueError),
        ("search", "%", ValueError),
    ],
)
def test_location_mutator_invalid_writes_are_atomic(setter, value, expected_exc):
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com:8080/p?q=1#f"
    w = d.default_view
    h = w.history
    before_href = w.location.href
    before_doc_url = d._url
    before_len = h.length
    before_state = h.state

    with pytest.raises(expected_exc):
        setattr(w.location, setter, value)

    assert w.location.href == before_href
    assert d._url == before_doc_url
    assert h.length == before_len
    assert h.state == before_state


def test_location_history_url_integration_assign_replace_component_matrix() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/base/index.html?q=1#frag"
    w = d.default_view
    h = w.history

    assert h.length == 1
    w.location.assign("../next/./page?x=1#n")
    assert w.location.href == "https://example.com/next/page?x=1#n"
    assert d.url == "https://example.com/next/page?x=1#n"
    assert h.length == 2

    w.location.replace("/final/./spot?x=1#n")
    assert w.location.href == "https://example.com/final/spot?x=1#n"
    assert d.url == "https://example.com/final/spot?x=1#n"
    assert h.length == 2

    w.location.protocol = "https:"
    w.location.host = "example.com"
    w.location.pathname = "workflow"
    w.location.search = "a=1&a=2&b=x%20y&c=%2B"
    assert w.location.href == "https://example.com/workflow?a=1&a=2&b=x%20y&c=%2B#n"
    assert d.url == "https://example.com/workflow?a=1&a=2&b=x%20y&c=%2B#n"
    assert h.length == 2

    w.location.search = "a=1&a=2&b=x+y&c=%2B"
    assert w.location.href == "https://example.com/workflow?a=1&a=2&b=x+y&c=%2B#n"
    assert d.url == "https://example.com/workflow?a=1&a=2&b=x+y&c=%2B#n"
    assert h.length == 2


def test_location_history_url_integration_atomic_cross_origin_component_failure() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history

    w.location.assign("/a")
    before_href = w.location.href
    before_doc_url = d.url
    before_length = h.length
    before_state = h.state

    with pytest.raises(SecurityError):
        w.location.hostname = "other.example"

    assert w.location.href == before_href
    assert d.url == before_doc_url
    assert h.length == before_length
    assert h.state == before_state


def test_location_history_url_integration_traversal_noop_contracts_preserved() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/"
    w = d.default_view
    h = w.history
    events = []

    w.add_event_listener("popstate", lambda _evt: events.append("pop"))
    w.location.assign("/a")
    before_href = w.location.href

    h.go(0)
    h.go(99)
    h.go(-99)

    assert w.location.href == before_href
    assert d.url == before_href
    assert events == []


def test_back104_location_href_integration_matrix_hash_non_hash_noop_and_atomic_failure() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start#one"
    w = d.default_view
    h = w.history

    hash_events = []
    pop_events = []
    w.add_event_listener("hashchange", lambda evt: hash_events.append((evt.old_url, evt.new_url)))
    w.add_event_listener("popstate", lambda _evt: pop_events.append("pop"))

    before_len = h.length
    w.location.href = "https://example.com/start#two"
    assert w.location.href == "https://example.com/start#two"
    assert d.url == "https://example.com/start#two"
    assert h.length == before_len
    assert hash_events == [("https://example.com/start#one", "https://example.com/start#two")]
    assert pop_events == []

    hash_events.clear()
    w.location.href = "https://example.com/next#two"
    assert w.location.href == "https://example.com/next#two"
    assert d.url == "https://example.com/next#two"
    assert h.length == before_len
    assert hash_events == []
    assert pop_events == []

    hash_events.clear()
    w.location.href = "https://example.com/next#two"
    assert w.location.href == "https://example.com/next#two"
    assert d.url == "https://example.com/next#two"
    assert h.length == before_len
    assert hash_events == []
    assert pop_events == []

    before_href = w.location.href
    before_doc_url = d.url
    before_state = h.state
    with pytest.raises(SecurityError):
        w.location.href = "https://other.example/blocked"

    assert w.location.href == before_href
    assert d.url == before_doc_url
    assert h.length == before_len
    assert h.state == before_state
    assert hash_events == []
    assert pop_events == []


def test_location_reload_public_available_and_returns_none() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view

    assert hasattr(w.location, "reload")
    assert w.location.reload() is None


def test_location_reload_is_atomic_noop_and_event_silent_and_idempotent() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history

    w.location.assign("/one")
    h.replace_state({"k": "v"}, "", None)

    before_index = h._index
    before_href = w.location.href
    before_state = h.state
    pop_events = []
    hash_events = []
    w.add_event_listener("popstate", lambda _evt: pop_events.append("pop"))
    w.add_event_listener("hashchange", lambda _evt: hash_events.append("hash"))

    w.location.reload()
    w.location.reload()
    w.location.reload()

    assert h._index == before_index
    assert w.location.href == before_href
    assert h.state == before_state
    assert pop_events == []
    assert hash_events == []


def test_location_reload_preserves_normal_traversal_behavior_after_noop() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history

    w.location.assign("/one")
    w.location.assign("/two")

    pop_states = []
    w.add_event_listener("popstate", lambda evt: pop_states.append(evt.state))

    w.location.reload()
    h.back()

    assert w.location.href == "https://example.com/one"
    assert pop_states == [None]


def test_track22_reload_and_traversal_event_matrix_composition() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history
    seen = []

    w.add_event_listener("popstate", lambda evt: seen.append(("popstate", evt.state, w.location.href)))
    w.add_event_listener("hashchange", lambda evt: seen.append(("hashchange", evt.old_url, evt.new_url)))

    h.push_state({"a": 1}, "", "/page#one")
    h.push_state({"b": 2}, "", "/page#two")
    seen.clear()

    before_index = h._index
    before_href = w.location.href
    before_state = h.state
    w.location.reload()

    assert h._index == before_index
    assert w.location.href == before_href
    assert h.state == before_state
    assert seen == []

    h.go(-1)
    assert seen == [
        ("popstate", {"a": 1}, "https://example.com/page#one"),
        ("hashchange", "https://example.com/page#two", "https://example.com/page#one"),
    ]


def test_track22_reload_does_not_mask_failure_atomicity_or_event_silence() -> None:
    d = HTMLDocument.parse("<p>x</p>")
    d._url = "https://example.com/start"
    w = d.default_view
    h = w.history
    seen = []

    w.add_event_listener("popstate", lambda _evt: seen.append("popstate"))
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    h.push_state({"ok": 1}, "", "/ok")
    before_href = w.location.href
    before_state = h.state
    before_len = h.length
    w.location.reload()

    with pytest.raises(SecurityError):
        w.location.href = "https://other.example/blocked"

    assert w.location.href == before_href
    assert h.state == before_state
    assert h.length == before_len
    assert seen == []


# ---------------------------------------------------------------------------
# BACK-147: Window timer stubs and screen/viewport stubs (SPEC-082 Group E)
# ---------------------------------------------------------------------------

def test_screen_exported_from_dom():
    """Screen is importable from aspose_html.dom (AC #1)."""
    assert Screen is not None


def test_screen_default_attribute_values():
    """Screen has documented default values (AC #1)."""
    s = Screen()
    assert s.width == 0
    assert s.height == 0
    assert s.avail_width == 0
    assert s.avail_height == 0
    assert s.color_depth == 24
    assert s.pixel_depth == 24


def test_window_screen_returns_screen_instance():
    """Window.screen returns a Screen instance (AC #2)."""
    w = Document().default_view
    assert isinstance(w.screen, Screen)


def test_window_screen_is_cached():
    """Window.screen returns the same instance on repeated access (AC #2)."""
    w = Document().default_view
    assert w.screen is w.screen


def test_window_screen_defaults():
    """Window.screen stub attributes (AC #2)."""
    w = Document().default_view
    s = w.screen
    assert s.width == 0
    assert s.height == 0
    assert s.color_depth == 24
    assert s.pixel_depth == 24


def test_window_set_timeout_returns_nonzero_int_handle():
    """set_timeout returns deterministic positive integer handles."""
    w = Document().default_view
    h1 = w.set_timeout(lambda: None, 1000)
    h2 = w.set_timeout(lambda: None, 1000)
    assert isinstance(h1, int)
    assert isinstance(h2, int)
    assert h1 > 0
    assert h2 == h1 + 1


def test_window_set_timeout_with_args_dispatches_callback_with_arguments():
    """set_timeout forwards *args when dispatched."""
    w = Document().default_view
    seen: list[tuple[object, ...]] = []
    w.set_timeout(lambda *a: seen.append(a), 100, "x", 42)
    assert w._dispatch_timer_macrotasks() == 1
    assert seen == [("x", 42)]


def test_window_set_interval_returns_nonzero_int_handle():
    """set_interval returns deterministic positive integer handles."""
    w = Document().default_view
    handle = w.set_interval(lambda: None, 500)
    assert isinstance(handle, int)
    assert handle > 0


def test_window_request_animation_frame_returns_zero():
    """request_animation_frame returns 0 (AC #3)."""
    w = Document().default_view
    assert w.request_animation_frame(lambda t: None) == 0


def test_window_clear_timeout_noop():
    """clear_timeout is idempotent for unknown/repeated handles."""
    w = Document().default_view
    h = w.set_timeout(lambda: None, 1)
    w.clear_timeout(h)
    w.clear_timeout(h)
    w.clear_timeout(None)
    w.clear_timeout(999)


def test_window_clear_interval_noop():
    """clear_interval is idempotent for unknown/repeated handles."""
    w = Document().default_view
    h = w.set_interval(lambda: None, 1)
    w.clear_interval(h)
    w.clear_interval(h)
    w.clear_interval(None)


def test_window_cancel_animation_frame_noop():
    """cancel_animation_frame does not raise (AC #4)."""
    w = Document().default_view
    w.cancel_animation_frame(0)
    w.cancel_animation_frame(None)


def test_timer_callbacks_run_only_when_dispatch_triggered():
    """set_timeout/set_interval are queued until macro-task dispatch runs."""
    w = Document().default_view
    calls: list[str] = []
    w.set_timeout(lambda: calls.append("timeout"), 0)
    w.set_interval(lambda: calls.append("interval"), 0)
    assert calls == []

    assert w._dispatch_timer_macrotasks(1) == 1
    assert calls == ["timeout"]

    assert w._dispatch_timer_macrotasks(2) == 2
    assert calls == ["timeout", "interval", "interval"]


def test_timer_dispatch_fifo_order_for_new_timers():
    """Timer macro-task dispatch preserves registration order (FIFO)."""
    w = Document().default_view
    calls: list[str] = []
    w.set_timeout(lambda: calls.append("first"), 0)
    w.set_timeout(lambda: calls.append("second"), 0)
    w.set_timeout(lambda: calls.append("third"), 0)

    assert w._dispatch_timer_macrotasks() == 3
    assert calls == ["first", "second", "third"]


def test_interval_reschedule_and_clear_inside_callback():
    """Intervals are rescheduled after callback unless canceled."""
    w = Document().default_view
    calls: list[str] = []
    handle = 0

    def on_interval() -> None:
        nonlocal handle
        calls.append("tick")
        if len(calls) == 2:
            w.clear_interval(handle)

    handle = w.set_interval(on_interval, 0)
    assert w._dispatch_timer_macrotasks(4) == 2
    assert calls == ["tick", "tick"]


def test_navigation_lifecycle_happy_path_and_ready_state_progression() -> None:
    doc = Document()
    win = doc.default_view

    assert win._navigation_lifecycle_state == "idle"
    assert doc.ready_state == "complete"

    assert win._navigation_begin() is True
    assert win._navigation_lifecycle_state == "navigating"

    win._navigation_accept_response()
    assert win._navigation_lifecycle_state == "replacing_document"
    assert doc.ready_state == "loading"

    win._navigation_mark_parsing()
    assert win._navigation_lifecycle_state == "parsing"
    assert doc.ready_state == "interactive"

    win._navigation_complete()
    assert win._navigation_lifecycle_state == "completed"
    assert doc.ready_state == "complete"


def test_navigation_lifecycle_cancellation_is_idempotent_and_clears_scheduled_work() -> None:
    doc = Document()
    win = doc.default_view

    timeout_id = win.set_timeout(lambda: None, 10)
    interval_id = win.set_interval(lambda: None, 10)
    idle_id = win.request_idle_callback(lambda *_: None)
    assert timeout_id in win._active_timers
    assert interval_id in win._active_timers
    assert idle_id in win._idle_callbacks
    assert len(win._timer_task_queue) >= 2

    assert win._navigation_begin() is True
    win._navigation_cancel()

    assert win._navigation_lifecycle_state == "idle"
    assert win._active_timers == {}
    assert list(win._timer_task_queue) == []
    assert win._idle_callbacks == {}
    assert doc.ready_state == "complete"

    # Non-active cancellation remains deterministic no-op.
    win._navigation_cancel()
    assert win._navigation_lifecycle_state == "idle"


def test_navigation_lifecycle_rejects_reentrant_begin_during_replacement() -> None:
    win = Document().default_view

    assert win._navigation_begin() is True
    win._navigation_accept_response()

    assert win._navigation_begin() is False


def test_navigation_lifecycle_illegal_transition_guards_raise_runtime_error() -> None:
    win = Document().default_view

    with pytest.raises(RuntimeError):
        win._navigation_accept_response()

    assert win._navigation_begin() is True
    with pytest.raises(RuntimeError):
        win._navigation_complete()


def test_navigation_pipeline_html_branch_replacement_order_and_ready_state() -> None:
    win = Document().default_view
    calls: list[str] = []

    def scheduler(job):
        calls.append("scheduler")
        # readyState must already be loading before parser is scheduled
        calls.append(f"ready_before_schedule:{win.document.ready_state}")
        job()

    result_doc = win._navigation_process_response(
        response_kind="html",
        html_source="<html><body><p>x</p></body></html>",
        scheduler_hook=scheduler,
    )

    assert result_doc is win.document
    assert win.document.ready_state == "complete"
    assert calls == ["scheduler", "ready_before_schedule:loading"]
    assert win._navigation_cleanup_marks[:4] == [
        "replace_started",
        "scheduled_work_cleared",
        "replace_ready",
        "document_attached",
    ]
    assert "parser_schedule_requested" in win._navigation_cleanup_marks
    assert "parser_started" in win._navigation_cleanup_marks
    assert win._navigation_cleanup_marks[-1] == "completed"


def test_navigation_pipeline_media_like_branch_skips_parser_scheduling() -> None:
    win = Document().default_view
    called = False

    def scheduler(_job):
        nonlocal called
        called = True

    doc = win._navigation_process_response(
        response_kind="image",
        scheduler_hook=scheduler,
    )

    assert doc is win.document
    assert called is False
    assert win.document.ready_state == "complete"
    assert "media_like_branch" in win._navigation_cleanup_marks
    assert "parser_schedule_requested" not in win._navigation_cleanup_marks
    assert win._navigation_cleanup_marks[-1] == "completed_non_html"


def test_navigation_pipeline_uses_parser_hook_via_scheduler_only() -> None:
    win = Document().default_view
    events: list[str] = []

    def scheduler(job):
        events.append("scheduler_called")
        job()

    def parser_hook(_html: str, _doc: Document) -> None:
        events.append("parser_called")

    win._navigation_process_response(
        response_kind="html",
        html_source="<html></html>",
        scheduler_hook=scheduler,
        parser_hook=parser_hook,
    )

    assert events == ["scheduler_called", "parser_called"]


def test_browsing_context_owns_lifecycle_state_and_document_pointer() -> None:
    win = Document().default_view

    assert win._browsing_context.current_document is win.document
    assert win._browsing_context.lifecycle_state == "idle"
    assert win._browsing_context.active_navigation_token is None

    win._navigation_process_response(
        response_kind="image",
    )

    assert win._browsing_context.current_document is win.document
    assert win._browsing_context.lifecycle_state == "completed"
    assert win._browsing_context.active_navigation_token is None


def test_browsing_context_navigation_token_lineage_is_issued_and_cleared() -> None:
    win = Document().default_view

    assert win._navigation_begin() is True
    token = win._browsing_context.active_navigation_token
    assert token == 1

    win._navigation_accept_response()
    win._navigation_mark_parsing()
    win._navigation_complete()

    assert win._browsing_context.active_navigation_token is None
    assert win._navigation_begin() is True
    assert win._browsing_context.active_navigation_token == 2


def test_window_event_loop_rejects_unregistered_task_source() -> None:
    loop = WindowEventLoop()

    with pytest.raises(ValueError, match="unregistered task source"):
        loop.schedule("navigation", "navigation-start", token=1, callback=lambda: None)


def test_window_event_loop_cancellation_and_cleanup_are_idempotent() -> None:
    loop = WindowEventLoop()
    loop.register_task_source("navigation")
    calls: list[str] = []

    loop.schedule("navigation", "navigation-start", token=7, callback=lambda: calls.append("run"))
    loop.cancel(7)
    loop.cancel(7)
    loop.drain()
    loop.cleanup(7)
    loop.cleanup(7)

    assert calls == []


def test_window_event_loop_rejects_unknown_microtask_phase_marker() -> None:
    loop = WindowEventLoop()

    with pytest.raises(ValueError, match="unsupported microtask phase"):
        loop.schedule("microtask", "promise-job", callback=lambda: None)


def test_window_microtask_checkpoint_intent_is_owned_by_event_loop(monkeypatch) -> None:
    win = Document().default_view
    seen: list[tuple[str, object | None]] = []
    original = WindowEventLoop.schedule_microtask_checkpoint

    def wrapped(self, callback, *, token=None):
        if self is win._event_loop:
            seen.append(("microtask-checkpoint", token))
        return original(self, callback, token=token)

    monkeypatch.setattr(WindowEventLoop, "schedule_microtask_checkpoint", wrapped)
    win._schedule_microtask_checkpoint(lambda: None, token=5)

    assert seen == [("microtask-checkpoint", 5)]


def test_window_has_no_local_microtask_queue_ownership_shortcuts() -> None:
    # Window must not own its own microtask queue storage — all scheduling
    # authority belongs to WindowEventLoop.  The public queue_microtask()
    # method is permitted (it routes through the seam); standalone queue
    # slots are not.
    win = Document().default_view

    assert not hasattr(win, "_microtask_queue")
    assert not hasattr(win, "_promise_jobs")


def test_window_navigation_uses_event_loop_task_source_boundary(monkeypatch) -> None:
    win = Document().default_view
    seen: list[tuple[str, str, object | None]] = []
    original_schedule = WindowEventLoop.schedule

    def wrapped(self, source_name: str, phase: str, token: object | None = None, callback=None):
        if self is win._event_loop:
            seen.append((source_name, phase, token))
        original_schedule(self, source_name, phase, token=token, callback=callback)

    monkeypatch.setattr(WindowEventLoop, "schedule", wrapped)
    win._navigation_process_response(response_kind="html", html_source="<html></html>")

    phases = [phase for _source, phase, _token in seen]
    assert "navigation-start" in phases
    assert "document-attach" in phases
    assert "navigation-complete" in phases


def test_window_navigation_cancel_uses_event_loop_cancel_phase(monkeypatch) -> None:
    win = Document().default_view
    seen: list[tuple[str, str, object | None]] = []
    original_schedule = WindowEventLoop.schedule

    def wrapped(self, source_name: str, phase: str, token: object | None = None, callback=None):
        if self is win._event_loop:
            seen.append((source_name, phase, token))
        original_schedule(self, source_name, phase, token=token, callback=callback)

    monkeypatch.setattr(WindowEventLoop, "schedule", wrapped)
    assert win._navigation_begin() is True
    token = win._browsing_context.active_navigation_token
    win._navigation_cancel()

    assert token is not None
    assert any(source == "navigation" and phase == "navigation-cancel" for source, phase, _ in seen)


def test_window_timer_api_delegates_to_window_event_loop(monkeypatch) -> None:
    win = Document().default_view
    seen: list[tuple[str, object]] = []

    original_schedule_timer = WindowEventLoop.schedule_timer
    original_cancel_timer = WindowEventLoop.cancel_timer
    original_dispatch_timer_tasks = WindowEventLoop.dispatch_timer_tasks

    def wrapped_schedule(self, callback, args, *, repeating: bool):
        if self is win._event_loop:
            seen.append(("schedule", repeating))
        return original_schedule_timer(self, callback, args, repeating=repeating)

    def wrapped_cancel(self, handle: int):
        if self is win._event_loop:
            seen.append(("cancel", handle))
        return original_cancel_timer(self, handle)

    def wrapped_dispatch(self, max_tasks=None):
        if self is win._event_loop:
            seen.append(("dispatch", max_tasks))
        return original_dispatch_timer_tasks(self, max_tasks)

    monkeypatch.setattr(WindowEventLoop, "schedule_timer", wrapped_schedule)
    monkeypatch.setattr(WindowEventLoop, "cancel_timer", wrapped_cancel)
    monkeypatch.setattr(WindowEventLoop, "dispatch_timer_tasks", wrapped_dispatch)

    timeout_id = win.set_timeout(lambda: None, 0)
    interval_id = win.set_interval(lambda: None, 0)
    assert timeout_id > 0 and interval_id > 0
    win.clear_timeout(timeout_id)
    win.clear_interval(interval_id)
    win._dispatch_timer_macrotasks(0)

    assert ("schedule", False) in seen
    assert ("schedule", True) in seen
    assert ("cancel", timeout_id) in seen
    assert ("cancel", interval_id) in seen
    assert ("dispatch", 0) in seen


def test_window_viewport_stubs():
    """All viewport stubs return documented values (AC #6)."""
    w = Document().default_view
    assert w.inner_width == 0
    assert w.inner_height == 0
    assert w.outer_width == 0
    assert w.outer_height == 0
    assert w.scroll_x == 0.0
    assert w.scroll_y == 0.0
    assert w.device_pixel_ratio == 1.0


def test_window_page_offsets_equal_scroll():
    """page_x_offset == scroll_x and page_y_offset == scroll_y (AC #7)."""
    w = Document().default_view
    assert w.page_x_offset == w.scroll_x
    assert w.page_y_offset == w.scroll_y


def test_window_viewport_return_types():
    """Viewport int/float return types are correct."""
    w = Document().default_view
    assert isinstance(w.inner_width, int)
    assert isinstance(w.inner_height, int)
    assert isinstance(w.outer_width, int)
    assert isinstance(w.outer_height, int)
    assert isinstance(w.scroll_x, float)
    assert isinstance(w.scroll_y, float)
    assert isinstance(w.page_x_offset, float)
    assert isinstance(w.page_y_offset, float)
    assert isinstance(w.device_pixel_ratio, float)


# ---------------------------------------------------------------------------
# BACK-151: Navigator extended stubs — platform, language, languages,
#           online, cookie_enabled, vendor (SPEC-083 Group C / ADR-134)
# ---------------------------------------------------------------------------

def test_navigator_platform_stub():
    """Navigator.platform returns 'Python' (AC #1)."""
    from aspose_html.dom._window import Navigator
    assert Navigator().platform == "Python"


def test_navigator_language_stub():
    """Navigator.language returns 'en' (AC #2)."""
    from aspose_html.dom._window import Navigator
    assert Navigator().language == "en"


def test_navigator_languages_stub():
    """Navigator.languages returns ('en',) (AC #3)."""
    from aspose_html.dom._window import Navigator
    nav = Navigator()
    assert nav.languages == ("en",)
    assert isinstance(nav.languages, tuple)


def test_navigator_online_stub():
    """Navigator.online is True (AC #4)."""
    from aspose_html.dom._window import Navigator
    assert Navigator().online is True


def test_navigator_cookie_enabled_stub():
    """Navigator.cookie_enabled is False (AC #5)."""
    from aspose_html.dom._window import Navigator
    assert Navigator().cookie_enabled is False


def test_navigator_vendor_stub():
    """Navigator.vendor returns '' (AC #6)."""
    from aspose_html.dom._window import Navigator
    assert Navigator().vendor == ""


def test_navigator_extended_stubs_return_types():
    """Navigator extended properties have correct types."""
    from aspose_html.dom._window import Navigator
    nav = Navigator()
    assert isinstance(nav.platform, str)
    assert isinstance(nav.language, str)
    assert isinstance(nav.languages, tuple)
    assert isinstance(nav.online, bool)
    assert isinstance(nav.cookie_enabled, bool)
    assert isinstance(nav.vendor, str)


def test_navigator_extended_stubs_are_read_only():
    """Navigator extended properties have no setters."""
    from aspose_html.dom._window import Navigator
    nav = Navigator()
    for attr in ("platform", "language", "languages", "online", "cookie_enabled", "vendor"):
        assert isinstance(getattr(Navigator, attr), property), f"{attr} must be a property"
        assert getattr(Navigator, attr).fset is None, f"{attr} must be read-only"


def test_navigator_platform_via_document_integration():
    """doc.default_view.navigator.platform works via Document (AC #8)."""
    doc = Document()
    assert doc.default_view.navigator.platform == "Python"


def test_navigator_extended_stubs_all_via_document_integration():
    """All six extended navigator properties accessible via doc.default_view.navigator."""
    doc = Document()
    nav = doc.default_view.navigator
    assert nav.platform == "Python"
    assert nav.language == "en"
    assert nav.languages == ("en",)
    assert nav.online is True
    assert nav.cookie_enabled is False
    assert nav.vendor == ""


# ---------------------------------------------------------------------------
# BACK-153: Window interaction stubs — alert, confirm, prompt,
#           get_computed_style, match_media + MediaQueryList (SPEC-083 Group E)
# ---------------------------------------------------------------------------

def test_window_alert_returns_none():
    """Window.alert() and Window.alert('msg') both return None (AC #1)."""
    win = Document().default_view
    assert win.alert() is None
    assert win.alert("test message") is None


def test_window_confirm_returns_false():
    """Window.confirm() returns False (AC #2)."""
    win = Document().default_view
    assert win.confirm("Are you sure?") is False
    assert win.confirm() is False


def test_window_prompt_returns_none():
    """Window.prompt() returns None (AC #3)."""
    win = Document().default_view
    assert win.prompt("Enter name") is None
    assert win.prompt() is None
    assert win.prompt("With default", "default") is None


def test_window_match_media_print_not_matches():
    """Window.match_media("print").matches is False in default screen env (AC #4)."""
    win = Document().default_view
    mql = win.match_media("print")
    assert mql.matches is False
    assert mql.media == "print"


def test_window_match_media_screen_matches():
    """Window.match_media("screen").matches is True in default screen env."""
    win = Document().default_view
    mql = win.match_media("screen")
    assert mql.matches is True
    assert mql.media == "screen"


def test_window_match_media_various_queries():
    """match_media preserves the query string verbatim; unsupported queries return False."""
    win = Document().default_view
    # unsupported feature queries should evaluate to False
    for q in ("(max-width: 768px)",):
        mql = win.match_media(q)
        assert mql.media == q
        assert mql.matches is False


def test_window_get_computed_style_delegates():
    """Window.get_computed_style(el) delegates to element cascade (AC #5)."""
    doc = HTMLDocument.parse(
        '<style>p { color: blue; }</style><p id="p1">text</p>'
    )
    el = doc.get_element_by_id("p1")
    cs = doc.default_view.get_computed_style(el)
    assert cs.get_property_value("color") == "blue"


def test_window_get_computed_style_accepts_pseudo_elt():
    """Window.get_computed_style accepts pseudo_elt argument without raising."""
    doc = HTMLDocument.parse(
        '<style>p { color: green; }</style><p id="p2">text</p>'
    )
    el = doc.get_element_by_id("p2")
    cs = doc.default_view.get_computed_style(el, "::before")
    assert cs.get_property_value("color") == "green"


def test_media_query_list_exported():
    """MediaQueryList is importable from aspose_html.dom (AC #6)."""
    from aspose_html.dom import MediaQueryList
    mql = MediaQueryList("(min-width: 1024px)")
    assert not mql.matches
    assert mql.media == "(min-width: 1024px)"


def test_media_query_list_add_remove_event_listener_noop():
    """MediaQueryList.add/remove_event_listener are no-ops (AC #7)."""
    from aspose_html.dom import MediaQueryList
    mql = MediaQueryList("screen")
    callback = lambda evt: None  # noqa: E731
    mql.add_event_listener("change", callback)
    mql.add_event_listener("change", callback, {"once": True})
    mql.remove_event_listener("change", callback)
    mql.remove_event_listener("change", callback, {"once": True})
    # No assertion needed — must not raise


def test_media_query_list_matches_real_evaluation():
    """MediaQueryList.matches evaluates against the default screen env."""
    from aspose_html.dom import MediaQueryList
    # These should match the default env (screen + prefers-color-scheme: light)
    assert MediaQueryList("screen").matches is True
    assert MediaQueryList("all").matches is True
    assert MediaQueryList("(prefers-color-scheme: light)").matches is True
    # These should not match
    assert MediaQueryList("print").matches is False
    assert MediaQueryList("(max-width: 0px)").matches is False
    assert MediaQueryList("(min-width: 99999px)").matches is False


def test_media_query_list_slots():
    """MediaQueryList uses __slots__ for memory efficiency."""
    from aspose_html.dom import MediaQueryList
    mql = MediaQueryList("screen")
    assert hasattr(MediaQueryList, "__slots__")
    assert "_media" in MediaQueryList.__slots__


def test_window_alert_confirm_prompt_return_types():
    """Return type contracts for dialog stubs."""
    win = Document().default_view
    result_alert = win.alert("x")
    result_confirm = win.confirm("x")
    result_prompt = win.prompt("x")
    assert result_alert is None
    assert result_confirm is False
    assert isinstance(result_confirm, bool)
    assert result_prompt is None


def test_window_open_returns_none_default_args() -> None:
    win = Document().default_view
    assert win.open() is None


def test_window_open_returns_none_with_explicit_args() -> None:
    win = Document().default_view
    assert win.open("https://example.com", "_self", "noopener") is None


def test_window_close_focus_blur_return_none() -> None:
    win = Document().default_view
    assert win.close() is None
    assert win.focus() is None
    assert win.blur() is None


def test_window_open_no_url_or_history_mutation() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    win = doc.default_view
    history = win.history

    before_href = win.location.href
    before_length = history.length
    before_state = history.state

    result = win.open("https://other.example/ignored", "_blank", "noopener")

    assert result is None
    assert win.location.href == before_href
    assert doc.url == before_href
    assert history.length == before_length
    assert history.state == before_state


def test_document_dynamic_markup_methods_route_intents_via_browsing_context() -> None:
    doc = Document()
    win = doc.default_view

    for method in (doc.open, doc.write, doc.writeln, doc.close):
        with pytest.raises(NotSupportedError):
            method()

    assert win._browsing_context.dynamic_markup_intents == (
        "open",
        "write",
        "writeln",
        "close",
    )


def test_document_dynamic_markup_methods_do_not_mutate_lifecycle_or_ready_state() -> None:
    doc = Document()
    win = doc.default_view

    lifecycle_before = win._navigation_lifecycle_state
    ready_state_before = doc.ready_state

    with pytest.raises(NotSupportedError):
        doc.open()
    with pytest.raises(NotSupportedError):
        doc.write("<p>x</p>")
    with pytest.raises(NotSupportedError):
        doc.close()

    assert win._navigation_lifecycle_state == lifecycle_before
    assert doc.ready_state == ready_state_before


# ------------------------------------------------------------------
# Track 60 — Window.queue_microtask (ADR-232 / BACK-251)
# ------------------------------------------------------------------


def test_queue_microtask_returns_none() -> None:
    """AC #1 — queue_microtask(lambda: None) returns None without error."""
    win = Document().default_view
    result = win.queue_microtask(lambda: None)
    assert result is None


def test_queue_microtask_callback_not_invoked_synchronously() -> None:
    """AC #2 — callback is NOT called synchronously after queue_microtask."""
    win = Document().default_view
    called: list[int] = []
    win.queue_microtask(lambda: called.append(1))
    # Immediately after the call the list must still be empty — the callback
    # must not have been dispatched synchronously.
    assert called == []


def test_queue_microtask_twice_does_not_raise() -> None:
    """AC #3 — calling twice does not raise."""
    win = Document().default_view
    win.queue_microtask(lambda: None)
    win.queue_microtask(lambda: None)  # second call must not raise


def test_queue_microtask_routes_through_event_loop_seam(monkeypatch) -> None:
    """AC #5 — routes through WindowEventLoop, not a direct execution bypass."""
    win = Document().default_view
    seam_calls: list[object] = []
    original = WindowEventLoop.schedule_microtask_checkpoint

    def intercepted(self, callback, *, token=None):
        if self is win._event_loop:
            seam_calls.append(callback)
        return original(self, callback, token=token)

    monkeypatch.setattr(WindowEventLoop, "schedule_microtask_checkpoint", intercepted)

    cb = lambda: None  # noqa: E731
    win.queue_microtask(cb)

    # The callback must have been forwarded to the WindowEventLoop seam.
    assert seam_calls == [cb]


def test_queue_microtask_callback_stored_in_event_loop_queue() -> None:
    """Supplementary — enqueued callback sits in the event-loop queue, not Window."""
    win = Document().default_view
    cb = lambda: None  # noqa: E731
    win.queue_microtask(cb)

    # Window must have no _microtask_queue of its own.
    assert not hasattr(win, "_microtask_queue")

    # The callback should be accessible in the WindowEventLoop internal queue
    # (drain-able in a future phase).  We verify by draining — cb must execute
    # at that point (demonstrating the loop, not Window, held it).
    executed: list[bool] = []
    flag_cb = lambda: executed.append(True)  # noqa: E731
    win.queue_microtask(flag_cb)
    # Before drain, flag is unset.
    assert executed == []
    # After drain via WindowEventLoop, flag is set.
    win._event_loop.drain()
    assert True in executed


def test_window_event_loop_mixed_microtask_and_timer_order_timer_then_microtask() -> None:
    """Track 62 ordering hardening: explicit timer dispatch then microtask drain."""
    win = Document().default_view
    observed: list[str] = []

    win.set_timeout(lambda: observed.append("timer"), 0)
    win.queue_microtask(lambda: observed.append("microtask"))

    # Registration is non-synchronous for both paths.
    assert observed == []

    # Timer and microtask queues are intentionally separate; callers choose
    # phase order explicitly.
    assert win._dispatch_timer_macrotasks() == 1
    win._event_loop.drain()

    assert observed == ["timer", "microtask"]


def test_window_event_loop_mixed_microtask_and_timer_order_microtask_then_timer() -> None:
    """Track 62 ordering hardening: explicit microtask drain then timer dispatch."""
    win = Document().default_view
    observed: list[str] = []

    win.set_timeout(lambda: observed.append("timer"), 0)
    win.queue_microtask(lambda: observed.append("microtask"))

    assert observed == []

    win._event_loop.drain()
    assert win._dispatch_timer_macrotasks() == 1

    assert observed == ["microtask", "timer"]


def test_window_event_loop_cancelled_microtask_token_cleanup_with_mixed_timer_work() -> None:
    """Track 62 cancellation hardening: cancelled microtask token is cleaned."""
    loop = WindowEventLoop()
    observed: list[str] = []
    token = object()

    loop.schedule_microtask_checkpoint(lambda: observed.append("microtask"), token=token)
    loop.cancel(token)

    timer_id = loop.schedule_timer(lambda: observed.append("timer"), (), repeating=False)
    assert timer_id > 0

    assert loop.dispatch_timer_tasks() == 1
    loop.drain()

    assert observed == ["timer"]
    assert token in loop._cleaned_tokens
    assert token not in loop._cancelled_tokens


def test_window_event_loop_queue_microtask_and_promise_job_checkpoint_order() -> None:
    """Track 66 ordering: Promise-job checkpoint uses the same event-loop seam."""
    win = Document().default_view
    observed: list[str] = []

    win.queue_microtask(lambda: observed.append("queueMicrotask"))
    win._schedule_microtask_checkpoint(lambda: observed.append("promiseJob"), token=None)

    assert observed == []
    win._event_loop.drain()
    assert observed == ["queueMicrotask", "promiseJob"]


def test_window_unhandled_rejection_is_scheduled_not_synchronous() -> None:
    win = Document().default_view
    seen: list[object] = []
    win.onunhandledrejection = lambda evt: seen.append(evt.reason)

    win._queue_unhandled_rejection("boom")
    assert seen == []

    win._event_loop.drain()
    assert seen == ["boom"]


def test_window_unhandled_rejection_payload_exposes_reason_and_type() -> None:
    win = Document().default_view
    payloads: list[object] = []
    win.onunhandledrejection = lambda evt: payloads.append(evt)

    reason = {"err": 1}
    win._queue_unhandled_rejection(reason)
    win._event_loop.drain()

    assert len(payloads) == 1
    payload = payloads[0]
    assert payload.reason is reason
    assert payload.type == "unhandledrejection"
    assert payload.phase == "unhandled-rejection"


def test_window_unhandled_rejection_without_handler_is_noop() -> None:
    win = Document().default_view

    win._queue_unhandled_rejection("drop")

    # Deterministic no-op: queue drains cleanly with no handler installed.
    win._event_loop.drain()


def test_window_unhandled_rejection_after_close_is_noop() -> None:
    win = Document().default_view
    seen: list[object] = []
    win.onunhandledrejection = lambda evt: seen.append(evt.reason)
    win.close()

    win._queue_unhandled_rejection("closed")
    win._event_loop.drain()

    assert seen == []


# ---------------------------------------------------------------------------
# Track 60 — Window.structured_clone and DataCloneError (ADR-233 / BACK-252)
# ---------------------------------------------------------------------------


def test_structured_clone_returns_equal_distinct_object() -> None:
    """AC #1 — structured_clone({'a': 1}) returns an equal but distinct object."""
    win = Document().default_view
    original = {"a": 1, "b": [2, 3]}
    cloned = win.structured_clone(original)
    assert cloned == original
    assert cloned is not original


def test_structured_clone_raises_data_clone_error_for_lambda() -> None:
    """AC #2 — cloning a lambda raises DataCloneError."""
    win = Document().default_view
    with pytest.raises(DataCloneError):
        win.structured_clone(lambda: None)


def test_data_clone_error_code_is_25() -> None:
    """AC #3 — DataCloneError.code == 25."""
    e = DataCloneError("test")
    assert e.code == 25


def test_data_clone_error_importable_from_dom() -> None:
    """AC #4 — DataCloneError is importable directly from aspose_html.dom."""
    from aspose_html.dom import DataCloneError as DCE  # noqa: PLC0415
    assert DCE is DataCloneError


def test_structured_clone_with_transfer_list_does_not_raise() -> None:
    """AC #5 — transfer=[] does not raise for a plain dict."""
    win = Document().default_view
    result = win.structured_clone({"x": 1}, transfer=[])
    assert result == {"x": 1}


def test_structured_clone_deep_copy_is_independent() -> None:
    """Supplementary — mutations to the clone do not affect the original."""
    win = Document().default_view
    original = {"nested": [1, 2, 3]}
    cloned = win.structured_clone(original)
    cloned["nested"].append(99)
    assert original["nested"] == [1, 2, 3]


def test_data_clone_error_inherits_dom_exception() -> None:
    """Supplementary — DataCloneError is a DOMException subclass."""
    from aspose_html.dom._exceptions import DOMException  # noqa: PLC0415
    e = DataCloneError("msg")
    assert isinstance(e, DOMException)


def test_structured_clone_default_message() -> None:
    """Supplementary — DataCloneError default message is the spec string."""
    e = DataCloneError()
    assert str(e) == "The object cannot be cloned."


def test_structured_clone_delegates_to_shared_clone_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    win = Document().default_view
    calls: list[object] = []

    def _fake_clone(value: object) -> object:
        calls.append(value)
        return {"delegated": True}

    monkeypatch.setattr("aspose_html.dom._window.clone_or_raise_data_clone_error", _fake_clone)

    assert win.structured_clone({"x": 1}) == {"delegated": True}
    assert calls == [{"x": 1}]


# ---------------------------------------------------------------------------
# Track 69 — Window.structured_clone transfer parameter (ADR-257 / BACK-279)
# ---------------------------------------------------------------------------


def test_structured_clone_transfer_none_behaves_as_before() -> None:
    """AC-2 — transfer=None is identical to calling without transfer."""
    win = Document().default_view
    result = win.structured_clone({"a": [1, 2]}, transfer=None)
    assert result == {"a": [1, 2]}


def test_structured_clone_transfer_empty_list_behaves_as_before() -> None:
    """AC-2 — transfer=[] is identical to calling without transfer."""
    win = Document().default_view
    result = win.structured_clone({"a": [1, 2]}, transfer=[])
    assert result == {"a": [1, 2]}


def test_structured_clone_transfer_plain_value_clones_normally() -> None:
    """AC-2 — a plain serializable value in the transfer list clones without error."""
    win = Document().default_view
    # A plain dict is not a WHATWG transferable type; it should clone normally.
    result = win.structured_clone({"v": 99}, transfer=[{"plain": True}])
    assert result == {"v": 99}


def test_structured_clone_transfer_mock_transferable_raises_data_clone_error() -> None:
    """AC-3 — a mock type whose name matches a WHATWG transferable raises DataCloneError."""
    win = Document().default_view

    class ArrayBuffer:
        """Stub whose name matches WHATWG ArrayBuffer."""

    ab = ArrayBuffer()
    with pytest.raises(DataCloneError):
        win.structured_clone({"v": 1}, transfer=[ab])


def test_structured_clone_transfer_error_message_contains_type_name() -> None:
    """AC-3 — DataCloneError message contains the type name and 'headless context'."""
    win = Document().default_view

    class MessagePort:
        """Stub whose name matches WHATWG MessagePort."""

    mp = MessagePort()
    with pytest.raises(DataCloneError, match="MessagePort"):
        win.structured_clone(42, transfer=[mp])


# Track 60 — Window.crypto / Crypto / SubtleCrypto (ADR-234 / BACK-253)
# -----------------------------------------------------------------------


def test_crypto_cached_singleton() -> None:
    """AC #1 — w.crypto is w.crypto (same instance on every access)."""
    win = Document().default_view
    assert win.crypto is win.crypto


def test_crypto_get_random_values_fills_zeros() -> None:
    """AC #2 — get_random_values returns zero-filled array."""
    win = Document().default_view
    arr = bytearray(4)
    result = win.crypto.get_random_values(arr)
    assert result is arr
    assert result == bytearray(4)


def test_crypto_random_uuid_format() -> None:
    """AC #3 — random_uuid() returns 36-char string with 4 dashes."""
    win = Document().default_view
    uuid = win.crypto.random_uuid()
    assert len(uuid) == 36
    assert uuid.count("-") == 4


def test_crypto_subtle_digest_raises_not_supported_error() -> None:
    """AC #4 — w.crypto.subtle.digest raises NotSupportedError."""
    win = Document().default_view
    with pytest.raises(NotSupportedError):
        win.crypto.subtle.digest("SHA-256", b"")


def test_window_crypto_constructor_property() -> None:
    """AC #5 — w.Crypto returns the Crypto class."""
    win = Document().default_view
    assert win.Crypto is Crypto


def test_crypto_importable_from_dom() -> None:
    """AC #6 — Crypto and SubtleCrypto importable from aspose_html.dom."""
    from aspose_html.dom import Crypto as C, SubtleCrypto as SC  # noqa: PLC0415
    assert C is Crypto
    assert SC is SubtleCrypto


def test_crypto_get_random_values_eight_bytes() -> None:
    """Supplementary — get_random_values works for 8-byte array."""
    c = Crypto()
    arr = bytearray(8)
    result = c.get_random_values(arr)
    assert result == bytearray(8)
    assert result is arr


def test_crypto_subtle_all_methods_raise() -> None:
    """Supplementary — all SubtleCrypto methods raise NotSupportedError."""
    sc = SubtleCrypto()
    methods = [
        sc.encrypt, sc.decrypt, sc.sign, sc.verify,
        sc.generate_key, sc.derive_key, sc.derive_bits,
        sc.import_key, sc.export_key, sc.wrap_key, sc.unwrap_key,
    ]
    for method in methods:
        with pytest.raises(NotSupportedError):
            method()


def test_crypto_subtle_property() -> None:
    """Supplementary — Crypto.subtle returns a SubtleCrypto instance."""
    c = Crypto()
    assert isinstance(c.subtle, SubtleCrypto)


def test_crypto_random_uuid_nil_value() -> None:
    """Supplementary — deterministic nil UUID value matches spec stub."""
    c = Crypto()
    assert c.random_uuid() == "00000000-0000-4000-8000-000000000000"


# ---------------------------------------------------------------------------
# Track 60 — Window.performance / Performance / PerformanceTiming (ADR-235 / BACK-254)
# ---------------------------------------------------------------------------


def _make_win() -> "object":
    from aspose_html.dom._window import Window  # noqa: PLC0415
    doc = Document()
    return Window(doc)


def test_performance_now_returns_float() -> None:
    """AC #2 — p.now() returns a float."""
    p = Performance()
    assert isinstance(p.now(), float)


def test_performance_now_non_negative() -> None:
    """AC #2 — p.now() returns a value >= 0.0."""
    p = Performance()
    assert p.now() >= 0.0


def test_performance_now_monotonic() -> None:
    """AC #3 — two successive now() calls return non-decreasing values."""
    p = Performance()
    t1 = p.now()
    t2 = p.now()
    assert t2 >= t1


def test_performance_mark_stores_entry() -> None:
    """AC #4 — mark('t1') stores entry with entry_type='mark' and name='t1'."""
    p = Performance()
    p.mark("t1")
    entries = p.get_entries_by_type("mark")
    assert len(entries) == 1
    assert entries[0].name == "t1"
    assert entries[0].entry_type == "mark"


def test_performance_measure_stores_entry() -> None:
    """AC #5 — measure('m') stores entry with entry_type='measure'."""
    p = Performance()
    p.measure("m")
    entries = p.get_entries_by_type("measure")
    assert len(entries) == 1
    assert entries[0].entry_type == "measure"
    assert entries[0].name == "m"


def test_performance_get_entries_by_type_filters() -> None:
    """AC #6 — get_entries_by_type('mark') returns only marks."""
    p = Performance()
    p.mark("a")
    p.measure("b")
    marks = p.get_entries_by_type("mark")
    assert len(marks) == 1
    assert marks[0].entry_type == "mark"
    measures = p.get_entries_by_type("measure")
    assert len(measures) == 1
    assert measures[0].entry_type == "measure"


def test_performance_clear_marks_removes_marks_leaves_measures() -> None:
    """AC #7 — clear_marks() removes all marks but not measures."""
    p = Performance()
    p.mark("m1")
    p.mark("m2")
    p.measure("dur")
    p.clear_marks()
    assert p.get_entries_by_type("mark") == []
    assert len(p.get_entries_by_type("measure")) == 1


def test_performance_timing_navigation_start_is_zero() -> None:
    """AC #8 — timing.navigation_start == 0."""
    p = Performance()
    assert p.timing.navigation_start == 0


def test_performance_timing_all_attributes_zero() -> None:
    """All PerformanceTiming attributes return 0."""
    t = PerformanceTiming()
    attrs = [
        "navigation_start", "fetch_start", "domain_lookup_start",
        "domain_lookup_end", "connect_start", "connect_end",
        "secure_connection_start", "request_start", "response_start",
        "response_end", "dom_loading", "dom_interactive",
        "dom_content_loaded_event_start", "dom_content_loaded_event_end",
        "dom_complete", "load_event_start", "load_event_end",
        "unload_event_start", "unload_event_end", "redirect_start",
        "redirect_end",
    ]
    for attr in attrs:
        assert getattr(t, attr) == 0, f"Expected 0 for {attr}"


def test_window_performance_cached_singleton() -> None:
    """AC #1 — w.performance is w.performance (cached singleton)."""
    win = _make_win()
    assert win.performance is win.performance


def test_window_performance_now_returns_float() -> None:
    """w.performance.now() returns a float >= 0.0."""
    win = _make_win()
    result = win.performance.now()
    assert isinstance(result, float)
    assert result >= 0.0


def test_performance_importable_from_dom() -> None:
    """AC #9 — Performance, PerformanceTiming, PerformanceEntry importable from aspose_html.dom."""
    from aspose_html.dom import Performance as Perf, PerformanceTiming as PT, PerformanceEntry as PE  # noqa: PLC0415
    assert Perf is Performance
    assert PT is PerformanceTiming
    assert PE is PerformanceEntry


def test_window_performance_constructor_property() -> None:
    """w.Performance returns the Performance class."""
    win = _make_win()
    assert win.Performance is Performance


def test_performance_entry_dataclass_fields() -> None:
    """PerformanceEntry is a dataclass with correct fields."""
    e = PerformanceEntry(name="x", entry_type="mark", start_time=1.5, duration=0.0)
    assert e.name == "x"
    assert e.entry_type == "mark"
    assert e.start_time == 1.5
    assert e.duration == 0.0


def test_performance_get_entries_by_name() -> None:
    """get_entries_by_name filters by name."""
    p = Performance()
    p.mark("a")
    p.mark("b")
    p.mark("a")
    result = p.get_entries_by_name("a")
    assert len(result) == 2
    assert all(e.name == "a" for e in result)


def test_performance_clear_marks_named() -> None:
    """clear_marks(name) removes only marks with that name."""
    p = Performance()
    p.mark("x")
    p.mark("y")
    p.clear_marks("x")
    remaining = p.get_entries_by_type("mark")
    assert len(remaining) == 1
    assert remaining[0].name == "y"


def test_performance_clear_measures_all() -> None:
    """clear_measures() removes all measures, leaves marks."""
    p = Performance()
    p.mark("a")
    p.measure("m1")
    p.measure("m2")
    p.clear_measures()
    assert p.get_entries_by_type("measure") == []
    assert len(p.get_entries_by_type("mark")) == 1


def test_performance_clear_measures_named() -> None:
    """clear_measures(name) removes only measures with that name."""
    p = Performance()
    p.measure("m1")
    p.measure("m2")
    p.clear_measures("m1")
    remaining = p.get_entries_by_type("measure")
    assert len(remaining) == 1
    assert remaining[0].name == "m2"


def test_performance_mark_duration_is_zero() -> None:
    """mark() entries always have duration 0.0."""
    p = Performance()
    p.mark("t")
    e = p.get_entries_by_type("mark")[0]
    assert e.duration == 0.0


def test_performance_measure_with_start_end_marks_does_not_raise() -> None:
    """measure() with start_mark/end_mark arguments does not raise."""
    p = Performance()
    p.mark("start")
    p.mark("end")
    p.measure("interval", start_mark="start", end_mark="end")
    assert len(p.get_entries_by_type("measure")) == 1


def test_performance_get_entries_by_name_no_match_returns_empty() -> None:
    """get_entries_by_name with no match returns []."""
    p = Performance()
    assert p.get_entries_by_name("nonexistent") == []


def test_performance_timing_is_singleton_per_instance() -> None:
    """timing property returns the same PerformanceTiming instance every call."""
    p = Performance()
    assert p.timing is p.timing


# ---------------------------------------------------------------------------
# Track 60 — Window.get_selection() (BACK-255)
# ---------------------------------------------------------------------------

def test_window_get_selection_delegates_to_document() -> None:
    """AC#1: w.get_selection() is w.document.get_selection() (same object)."""
    doc = Document()
    w = doc.default_view
    assert w.get_selection() is doc.get_selection()


def test_window_get_selection_same_instance_on_repeated_calls() -> None:
    """AC#2: calling get_selection() twice returns the same Selection instance."""
    doc = Document()
    w = doc.default_view
    sel1 = w.get_selection()
    sel2 = w.get_selection()
    assert sel1 is sel2


def test_window_get_selection_returns_selection_type() -> None:
    """AC#3: return value is a Selection instance."""
    doc = Document()
    w = doc.default_view
    assert isinstance(w.get_selection(), Selection)


# ---------------------------------------------------------------------------
# Track 100 — Window / Navigator IDL tail (BACK-321, ADR-299)
# AC-10 through AC-24
# ---------------------------------------------------------------------------

def test_window_screen_left_top() -> None:
    """AC-10: screen_left == 0 and screen_top == 0."""
    doc = Document()
    w = doc.default_view
    assert w.screen_left == 0
    assert w.screen_top == 0
    # Must be aliases for screen_x / screen_y
    assert w.screen_left == w.screen_x
    assert w.screen_top == w.screen_y


def test_window_print_stop() -> None:
    """AC-11/AC-12: print() and stop() execute without raising."""
    doc = Document()
    w = doc.default_view
    result_print = w.print()
    result_stop = w.stop()
    assert result_print is None
    assert result_stop is None


def test_window_name() -> None:
    """AC-13: name returns '' by default; get/set round-trip."""
    doc = Document()
    w = doc.default_view
    assert w.name == ""
    w.name = "myframe"
    assert w.name == "myframe"
    # Non-string values should be coerced to str
    w.name = 42  # type: ignore[assignment]
    assert w.name == "42"


def test_window_status() -> None:
    """AC-14: status returns '' by default; setter round-trips."""
    doc = Document()
    w = doc.default_view
    assert w.status == ""
    w.status = "Loading..."
    assert w.status == "Loading..."
    w.status = ""
    assert w.status == ""


def test_navigator_extended() -> None:
    """AC-15 through AC-24: all new Navigator properties/methods."""
    doc = Document()
    nav = doc.default_view.navigator
    # AC-15
    assert nav.hardware_concurrency == 1
    # AC-16
    assert nav.max_touch_points == 0
    # AC-17
    assert nav.pdf_viewer_enabled is False
    # AC-18
    assert nav.app_code_name == "Mozilla"
    # AC-19
    assert nav.app_name == "Netscape"
    # AC-20
    assert nav.app_version == ""
    # AC-21
    assert nav.product == "Gecko"
    # AC-22
    assert nav.vendor_sub == ""
    assert nav.product_sub == ""
    # AC-23
    assert nav.java_enabled() is False
    # AC-24
    assert nav.do_not_track is None


# ---------------------------------------------------------------------------
# Track 102 — Window / Navigator IDL tail (BACK-323 / ADR-301)
# ---------------------------------------------------------------------------

def test_window_frames_returns_self() -> None:
    """AC-1 (BACK-323): Window.frames returns the Window instance itself."""
    win = Document().default_view
    assert win.frames is win


def test_window_length_is_zero() -> None:
    """AC-2 (BACK-323): Window.length is always 0 in headless."""
    win = Document().default_view
    assert win.length == 0


def test_window_post_message_no_raise() -> None:
    """AC-3 (BACK-323): Window.post_message executes without raising."""
    win = Document().default_view
    win.post_message("hello", "*")


def test_window_find_returns_false() -> None:
    """AC-4 (BACK-323): Window.find always returns False."""
    win = Document().default_view
    assert win.find("text") is False


def test_window_move_resize_no_raise() -> None:
    """AC-5 (BACK-323): move_to/by/resize_to/by all execute without raising."""
    win = Document().default_view
    win.move_to(100, 200)
    win.move_by(10, 10)
    win.resize_to(800, 600)
    win.resize_by(50, 50)


def test_window_is_secure_context() -> None:
    """AC-6 (BACK-323): Window.is_secure_context is True."""
    win = Document().default_view
    assert win.is_secure_context is True


def test_window_crossorigin_isolated() -> None:
    """AC-7 (BACK-323): Window.crossorigin_isolated is False."""
    win = Document().default_view
    assert win.crossorigin_isolated is False


def test_window_origin_agent_cluster() -> None:
    """AC-8 (BACK-323): Window.origin_agent_cluster is False."""
    win = Document().default_view
    assert win.origin_agent_cluster is False


def test_navigator_stub_properties_none() -> None:
    """AC-9–14,18,19 (BACK-323): all None-returning Navigator stub properties."""
    nav = Document().default_view.navigator
    for attr in (
        "clipboard", "media_devices", "storage", "geolocation",
        "credentials", "xr", "locks", "bluetooth", "hid", "usb",
        "serial", "wake_lock",
    ):
        assert getattr(nav, attr) is None, f"Expected None: navigator.{attr}"


def test_navigator_vibrate_false() -> None:
    """AC-15 (BACK-323): Navigator.vibrate returns False."""
    nav = Document().default_view.navigator
    assert nav.vibrate(200) is False


def test_navigator_can_share_false() -> None:
    """AC-16 (BACK-323): Navigator.can_share returns False."""
    nav = Document().default_view.navigator
    assert nav.can_share({"url": "https://example.com"}) is False


def test_navigator_send_beacon_false() -> None:
    """AC-17 (BACK-323): Navigator.send_beacon returns False."""
    nav = Document().default_view.navigator
    assert nav.send_beacon("https://example.com/log") is False


def test_navigator_share_raises_not_supported() -> None:
    """AC (BACK-323): Navigator.share raises DOMException."""
    from aspose_html.dom._exceptions import NotSupportedError
    nav = Document().default_view.navigator
    with pytest.raises(NotSupportedError):
        nav.share({"url": "https://example.com"})


# ---------------------------------------------------------------------------
# Track 103 — Window / Navigator IDL tail (BACK-324 / ADR-302)
# ---------------------------------------------------------------------------

def test_bar_props_visible_false() -> None:
    """AC-8: All BarProp toolbar stubs return visible=False."""
    w = HTMLDocument.parse("<html></html>").default_view
    for name in ("location_bar", "menu_bar", "personal_bar",
                 "scroll_bars", "status_bar", "tool_bar"):
        bar = getattr(w, name)
        assert bar.visible is False, f"{name}.visible should be False"


def test_atob_hello() -> None:
    """AC-9: window.atob('aGVsbG8=') == 'hello'."""
    w = HTMLDocument.parse("<html></html>").default_view
    assert w.atob("aGVsbG8=") == "hello"


def test_btoa_hello() -> None:
    """AC-9: window.btoa('hello') == 'aGVsbG8='."""
    w = HTMLDocument.parse("<html></html>").default_view
    assert w.btoa("hello") == "aGVsbG8="


def test_atob_invalid_raises() -> None:
    """AC-10: window.atob with invalid base64 raises DOMException."""
    from aspose_html.dom._exceptions import InvalidCharacterError
    w = HTMLDocument.parse("<html></html>").default_view
    with pytest.raises(InvalidCharacterError):
        w.atob("not valid base64!!!")


def test_btoa_non_latin1_raises() -> None:
    """AC-10: window.btoa with non-Latin-1 character raises DOMException."""
    from aspose_html.dom._exceptions import InvalidCharacterError
    w = HTMLDocument.parse("<html></html>").default_view
    with pytest.raises(InvalidCharacterError):
        w.btoa("Ā")  # code point 256, outside Latin-1


def test_window_fetch_is_none() -> None:
    """AC-11: window.fetch is None."""
    w = HTMLDocument.parse("<html></html>").default_view
    assert w.fetch is None


def test_navigator_connection_is_none() -> None:
    """AC-12: navigator.connection is None."""
    w = HTMLDocument.parse("<html></html>").default_view
    assert w.navigator.connection is None


def test_navigator_device_memory() -> None:
    """AC-12: navigator.device_memory == 8.0."""
    w = HTMLDocument.parse("<html></html>").default_view
    assert w.navigator.device_memory == 8.0
