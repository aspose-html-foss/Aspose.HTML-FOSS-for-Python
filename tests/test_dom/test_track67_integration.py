""" structured-clone fidelity integration matrix ().

Covers cross-surface snapshot coherence for messaging and history payload
boundaries finalized by /.
"""

from __future__ import annotations

from aspose_html.dom import BroadcastChannel, MessageChannel
from aspose_html.dom._document import Document


def test_track67_snapshot_boundary_is_coherent_across_message_port_and_history() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    history = doc.default_view.history

    channel = MessageChannel()
    seen_port: list[object] = []
    channel.port2.onmessage = lambda evt: seen_port.append(evt)
    channel.port2.start()

    payload = {"nested": [1]}
    channel.port1.post_message(payload)
    history.push_state(payload, "", "/a")
    payload["nested"].append(2)

    channel.port1._event_loop.drain()

    assert seen_port == [{"nested": [1]}]
    assert history.state == {"nested": [1]}
    assert seen_port[0] is not history.state


def test_track67_snapshot_boundary_is_coherent_across_broadcast_and_history() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    history = doc.default_view.history

    sender = BroadcastChannel("track67")
    receiver = BroadcastChannel("track67")
    seen_broadcast: list[object] = []
    receiver.onmessage = lambda evt: seen_broadcast.append(evt)

    payload = {"nested": [1]}
    sender.post_message(payload)
    history.replace_state(payload, "", "/b")
    payload["nested"].append(2)

    sender._event_loop.drain()

    assert seen_broadcast == [{"nested": [1]}]
    assert history.state == {"nested": [1]}

    sender.close()
    receiver.close()


def test_track67_history_traversal_events_unchanged_by_clone_policy_alignment() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    window = doc.default_view
    history = window.history
    seen: list[tuple[object, str]] = []
    window.add_event_listener("popstate", lambda evt: seen.append((evt.state, window.location.href)))

    history.push_state({"a": 1}, "", "/a")
    history.push_state({"b": 2}, "", "/b")

    history.back()
    history.forward()

    assert seen == [
        ({"a": 1}, "https://example.com/a"),
        ({"b": 2}, "https://example.com/b"),
    ]
