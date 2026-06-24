""" messaging delivery integration matrix ().

Covers the bounded runtime contracts finalized by /:

- deterministic queue/schedule behavior for ``MessagePort`` and
  ``BroadcastChannel``;
- explicit start/close gating for ``MessagePort`` delivery;
- bounded API surface (no transfer-list/origin overload semantics in this track).
"""

from __future__ import annotations

import pytest

from aspose_html.dom import BroadcastChannel, InvalidStateError, MessageChannel


def test_message_port_gating_matrix_start_then_close() -> None:
    channel = MessageChannel()
    seen: list[object] = []
    channel.port2.onmessage = lambda evt: seen.append(evt)

    # Not started yet: queued but undispatched.
    channel.port1.post_message("before-start")
    channel.port1._event_loop.drain()
    assert seen == []

    # Start gate opens dispatch for already queued + future messages.
    channel.port2.start()
    channel.port1.post_message("after-start")
    channel.port1._event_loop.drain()
    assert seen == ["before-start", "after-start"]

    # Closed target stops all future receives.
    channel.port2.close()
    channel.port1.post_message("after-close")
    channel.port1._event_loop.drain()
    assert seen == ["before-start", "after-start"]


def test_message_port_and_broadcast_channel_share_non_synchronous_delivery_boundary() -> None:
    msg_channel = MessageChannel()
    msg_seen: list[object] = []
    msg_channel.port2.onmessage = lambda evt: msg_seen.append(("port", evt))
    msg_channel.port2.start()

    bc_sender = BroadcastChannel("track65-sync-boundary")
    bc_receiver = BroadcastChannel("track65-sync-boundary")
    bc_seen: list[object] = []
    bc_receiver.onmessage = lambda evt: bc_seen.append(("broadcast", evt))

    msg_channel.port1.post_message("m1")
    bc_sender.post_message("b1")

    # Explicit boundary: producer call stack never synchronously fires handlers.
    assert msg_seen == []
    assert bc_seen == []

    msg_channel.port1._event_loop.drain()
    bc_sender._event_loop.drain()

    assert msg_seen == [("port", "m1")]
    assert bc_seen == [("broadcast", "b1")]

    bc_sender.close()
    bc_receiver.close()


def test_broadcast_channel_ordering_and_open_receiver_matrix() -> None:
    sender = BroadcastChannel("track65-matrix")
    receiver_open = BroadcastChannel("track65-matrix")
    receiver_other = BroadcastChannel("track65-matrix-other")
    receiver_closed = BroadcastChannel("track65-matrix")

    seen_open: list[object] = []
    seen_other: list[object] = []
    seen_closed: list[object] = []

    receiver_open.onmessage = lambda evt: seen_open.append(evt)
    receiver_other.onmessage = lambda evt: seen_other.append(evt)
    receiver_closed.onmessage = lambda evt: seen_closed.append(evt)
    receiver_closed.close()

    sender.post_message("first")
    sender.post_message("second")
    sender._event_loop.drain()

    assert seen_open == ["first", "second"]
    assert seen_other == []
    assert seen_closed == []

    sender.close()
    receiver_open.close()
    receiver_other.close()


def test_track65_bounded_api_rejects_unimplemented_overloads() -> None:
    channel = MessageChannel()
    channel.port2.start()

    with pytest.raises(TypeError):
        channel.port1.post_message("payload", [channel.port2])

    bc = BroadcastChannel("track65-bounds")
    with pytest.raises(TypeError):
        bc.post_message("payload", "https://example.com")

    bc.close()


def test_closed_state_errors_remain_explicit_for_producers() -> None:
    channel = MessageChannel()
    channel.port1.close()
    with pytest.raises(InvalidStateError):
        channel.port1.post_message("x")

    bc = BroadcastChannel("track65-invalid-state")
    bc.close()
    with pytest.raises(InvalidStateError):
        bc.post_message("x")
