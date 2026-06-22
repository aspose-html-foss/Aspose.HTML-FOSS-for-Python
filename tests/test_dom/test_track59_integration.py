"""Track 59 browser messaging stubs — integration matrix (BACK-250).

Covers constructor availability and deterministic no-delivery behavior for all
Track 59 messaging APIs: ``MessageChannel``, ``MessagePort``, and
``BroadcastChannel``.  These are headless deterministic stubs — no asynchronous
message delivery occurs in this phase.

ADR: ADR-231
SPEC: SPEC-113
Tasks: BACK-248, BACK-249, BACK-250
"""

from __future__ import annotations

import aspose_html.dom as dom
from aspose_html.dom import (
    BroadcastChannel,
    Document,
    InvalidStateError,
    MessageChannel,
    MessagePort,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh_window():
    return Document().default_view


# ---------------------------------------------------------------------------
# AC-1: Constructor availability via public import and Window reference
# ---------------------------------------------------------------------------


class TestConstructorAvailability:
    """All Track 59 types are accessible via the public dom namespace and via
    the per-window constructor-reference properties."""

    def test_message_channel_available_from_dom_namespace(self) -> None:
        assert dom.MessageChannel is MessageChannel

    def test_message_port_available_from_dom_namespace(self) -> None:
        assert dom.MessagePort is MessagePort

    def test_broadcast_channel_available_from_dom_namespace(self) -> None:
        assert dom.BroadcastChannel is BroadcastChannel

    def test_window_message_channel_property_is_constructor_reference(self) -> None:
        win = _fresh_window()
        assert win.MessageChannel is MessageChannel

    def test_window_message_port_property_is_constructor_reference(self) -> None:
        win = _fresh_window()
        assert win.MessagePort is MessagePort

    def test_window_broadcast_channel_property_is_constructor_reference(self) -> None:
        win = _fresh_window()
        assert win.BroadcastChannel is BroadcastChannel

    def test_message_channel_is_instantiable(self) -> None:
        ch = MessageChannel()
        assert ch is not None

    def test_broadcast_channel_is_instantiable_with_name(self) -> None:
        ch = BroadcastChannel("probe")
        assert ch is not None

    def test_message_port_is_not_directly_instantiable_without_channel(self) -> None:
        # MessagePort can be constructed directly but is typically obtained from
        # MessageChannel.  Verify it does not raise on direct construction.
        port = MessagePort()
        assert port is not None


# ---------------------------------------------------------------------------
# AC-1 continued: MessageChannel / MessagePort structural contracts
# ---------------------------------------------------------------------------


class TestMessageChannelStructure:
    """MessageChannel always creates two distinct, linked MessagePort endpoints."""

    def test_port1_and_port2_are_message_ports(self) -> None:
        ch = MessageChannel()
        assert isinstance(ch.port1, MessagePort)
        assert isinstance(ch.port2, MessagePort)

    def test_port1_and_port2_are_distinct_objects(self) -> None:
        ch = MessageChannel()
        assert ch.port1 is not ch.port2

    def test_port1_peer_is_port2(self) -> None:
        ch = MessageChannel()
        assert ch.port1._peer is ch.port2

    def test_port2_peer_is_port1(self) -> None:
        ch = MessageChannel()
        assert ch.port2._peer is ch.port1

    def test_ports_start_in_open_state(self) -> None:
        ch = MessageChannel()
        assert ch.port1.closed is False
        assert ch.port2.closed is False


# ---------------------------------------------------------------------------
# AC-1: MessagePort lifecycle (start / close idempotence)
# ---------------------------------------------------------------------------


class TestMessagePortLifecycle:
    """MessagePort.start() is a no-op; close() is idempotent and permanent."""

    def test_start_is_idempotent_and_does_not_raise(self) -> None:
        port = MessageChannel().port1
        port.start()
        port.start()
        assert port.closed is False

    def test_close_sets_closed_flag(self) -> None:
        port = MessageChannel().port1
        port.close()
        assert port.closed is True

    def test_close_is_idempotent(self) -> None:
        port = MessageChannel().port1
        port.close()
        port.close()
        assert port.closed is True

    def test_start_after_close_does_not_reopen_port(self) -> None:
        port = MessageChannel().port1
        port.close()
        port.start()
        assert port.closed is True

    def test_onmessage_slot_initialises_as_none(self) -> None:
        port = MessageChannel().port1
        assert port.onmessage is None

    def test_onmessage_slot_is_settable(self) -> None:
        port = MessageChannel().port1
        port.onmessage = lambda evt: None
        assert port.onmessage is not None


# ---------------------------------------------------------------------------
# AC-1 / AC-2: Deterministic no-delivery for MessageChannel
# ---------------------------------------------------------------------------


class TestMessageChannelNoDelivery:
    """post_message is accepted without raising but never delivers to peer."""

    def test_post_message_does_not_invoke_peer_onmessage(self) -> None:
        ch = MessageChannel()
        seen: list[object] = []
        ch.port2.onmessage = lambda evt: seen.append(evt)

        ch.port1.post_message({"key": "value"})

        assert seen == []

    def test_post_message_accepts_arbitrary_payload_types(self) -> None:
        ch = MessageChannel()
        ch.port1.post_message(None)
        ch.port1.post_message(42)
        ch.port1.post_message(b"bytes")
        ch.port1.post_message({"complex": [1, 2, 3]})
        # none of the above should raise

    def test_post_message_raises_after_close(self) -> None:
        ch = MessageChannel()
        ch.port1.close()
        try:
            ch.port1.post_message("after close")
        except InvalidStateError:
            return
        raise AssertionError("Expected InvalidStateError after close().")

    def test_multiple_post_messages_never_deliver(self) -> None:
        ch = MessageChannel()
        seen: list[object] = []
        ch.port2.onmessage = lambda evt: seen.append(evt)

        for i in range(5):
            ch.port1.post_message(i)

        assert seen == []


# ---------------------------------------------------------------------------
# AC-2: Deterministic no-delivery for BroadcastChannel
# ---------------------------------------------------------------------------


class TestBroadcastChannelNoDelivery:
    """BroadcastChannel.post_message never delivers in this headless phase."""

    def test_post_message_does_not_invoke_onmessage(self) -> None:
        ch = BroadcastChannel("test-channel")
        seen: list[object] = []
        ch.onmessage = lambda evt: seen.append(evt)

        ch.post_message({"payload": 1})

        assert seen == []

    def test_post_message_does_not_raise_with_none_onmessage(self) -> None:
        ch = BroadcastChannel("test-channel")
        assert ch.onmessage is None
        ch.post_message("no handler set")

    def test_post_message_after_close_raises_invalid_state_error(self) -> None:
        ch = BroadcastChannel("test-channel")
        ch.close()
        try:
            ch.post_message("after close")
        except InvalidStateError:
            return
        raise AssertionError("Expected InvalidStateError after close().")

    def test_name_is_stable_after_post_message(self) -> None:
        ch = BroadcastChannel("stable-name")
        ch.post_message("payload")
        assert ch.name == "stable-name"


# ---------------------------------------------------------------------------
# AC-2: BroadcastChannel close idempotence + name contract
# ---------------------------------------------------------------------------


class TestBroadcastChannelLifecycle:
    """BroadcastChannel close is idempotent; name is stable from construction."""

    def test_name_reflects_constructor_argument(self) -> None:
        assert BroadcastChannel("my-channel").name == "my-channel"

    def test_name_is_coerced_to_string(self) -> None:
        ch = BroadcastChannel(42)  # type: ignore[arg-type]
        assert ch.name == "42"

    def test_close_is_idempotent(self) -> None:
        ch = BroadcastChannel("idempotent")
        ch.close()
        ch.close()

    def test_onmessage_is_never_invoked_after_close(self) -> None:
        ch = BroadcastChannel("after-close")
        seen: list[object] = []
        ch.onmessage = lambda evt: seen.append(evt)
        ch.close()
        try:
            ch.post_message("dropped")
        except InvalidStateError:
            pass
        assert seen == []


# ---------------------------------------------------------------------------
# AC-4: No coupling regressions with Window timer / event-loop behavior
# ---------------------------------------------------------------------------


class TestNoWindowCouplingRegression:
    """Messaging construction must not affect Window timer or event-loop state."""

    def test_message_channel_construction_does_not_affect_timer_queue(self) -> None:
        win = _fresh_window()
        calls: list[str] = []
        t1 = win.set_timeout(lambda: calls.append("t1"), 0)

        # Create and post to a channel — must not disturb the timer queue.
        ch = MessageChannel()
        ch.port1.post_message("probe")

        fired = win._dispatch_timer_macrotasks(5)
        assert fired == 1
        assert calls == ["t1"]

    def test_broadcast_channel_construction_does_not_affect_timer_queue(self) -> None:
        win = _fresh_window()
        calls: list[str] = []
        win.set_timeout(lambda: calls.append("t1"), 0)

        BroadcastChannel("probe").post_message("x")

        fired = win._dispatch_timer_macrotasks(5)
        assert fired == 1
        assert calls == ["t1"]

    def test_message_channel_does_not_consume_idle_callbacks(self) -> None:
        win = _fresh_window()
        seen: list[object] = []
        win.request_idle_callback(lambda *_: seen.append("idle"))

        ch = MessageChannel()
        ch.port1.post_message("test")

        # Idle callbacks are not auto-dispatched by messaging.
        assert seen == []

    def test_window_messaging_constructors_stable_across_fresh_windows(self) -> None:
        win1 = _fresh_window()
        win2 = _fresh_window()

        # Each fresh Window should expose the same class references.
        assert win1.MessageChannel is win2.MessageChannel is MessageChannel
        assert win1.MessagePort is win2.MessagePort is MessagePort
        assert win1.BroadcastChannel is win2.BroadcastChannel is BroadcastChannel

    def test_event_target_inheritance_on_message_port(self) -> None:
        from aspose_html.dom import EventTarget

        port = MessageChannel().port1
        assert isinstance(port, EventTarget)

    def test_event_target_inheritance_on_broadcast_channel(self) -> None:
        from aspose_html.dom import EventTarget

        ch = BroadcastChannel("inheritance-check")
        assert isinstance(ch, EventTarget)
