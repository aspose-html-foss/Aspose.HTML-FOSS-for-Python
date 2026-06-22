import pytest
import threading

from aspose_html.dom import Document, HashChangeEvent, History, PopStateEvent, SecurityError


def test_history_basic_navigation_and_singleton() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    assert isinstance(h, History)
    assert h is doc.default_view.history
    assert h.length == 1
    assert h.state is None

    h.push_state({"x": 1}, "", "/p")
    assert h.length == 2
    assert h.state == {"x": 1}
    assert doc.default_view.location.pathname == "/p"

    h.replace_state({"y": 2}, "", "/q")
    assert h.length == 2
    assert h.state == {"y": 2}
    assert doc.default_view.location.pathname == "/q"

    h.back()
    assert h.state is None
    h.forward()
    assert h.state == {"y": 2}


def test_history_origin_checks_and_no_dom_mutation() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    root = doc.create_element("html")
    doc.append_child(root)
    before = len(doc.child_nodes)

    h = doc.default_view.history
    h.push_state({"a": 1}, "", "/ok")
    assert len(doc.child_nodes) == before

    try:
        h.push_state({}, "", "https://other.example/")
    except SecurityError:
        pass
    else:
        raise AssertionError("Expected SecurityError")


def test_history_push_drops_forward_and_state_is_isolated_from_input() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    state = {"k": [1]}
    h.push_state(state, "", "/a")
    h.push_state({"b": 2}, "", "/b")
    h.back()
    h.push_state({"c": 3}, "", "/c")
    assert h.length == 3
    h.forward()  # no-op at end
    assert h.state == {"c": 3}

    h.back()
    state["k"].append(2)
    assert h.state == {"k": [1]}


def test_history_replace_state_is_isolated_from_input() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    h.push_state({"k": 1}, "", "/a")

    state = {"k": [1]}
    h.replace_state(state, "", "/a")
    state["k"].append(2)

    assert h.state == {"k": [1]}


def test_history_back_forward_preserves_entry_snapshots() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history

    first = {"arr": [1]}
    second = {"arr": [2]}
    h.push_state(first, "", "/a")
    h.push_state(second, "", "/b")
    first["arr"].append(9)
    second["arr"].append(8)

    h.back()
    assert h.state == {"arr": [1]}
    h.forward()
    assert h.state == {"arr": [2]}


def test_history_traversal_dispatches_popstate_once_per_index_change() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    events = []

    def on_pop(evt: PopStateEvent) -> None:
        events.append((evt.state, w.location.href))

    w.add_event_listener("popstate", on_pop)
    h.push_state({"a": 1}, "", "/a")
    h.push_state({"b": 2}, "", "/b")
    assert events == []

    h.back()
    h.forward()
    h.go(-1)
    assert events == [
        ({"a": 1}, "https://example.com/a"),
        ({"b": 2}, "https://example.com/b"),
        ({"a": 1}, "https://example.com/a"),
    ]


def test_history_go_multistep_dispatches_single_target_snapshot_per_call() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda evt: seen.append((evt.state, w.location.href)))

    h.push_state({"a": 1}, "", "/a")
    h.push_state({"b": 2}, "", "/b")
    h.push_state({"c": 3}, "", "/c")
    h.push_state({"d": 4}, "", "/d")

    h.go(-2)
    h.go(2)

    assert seen == [
        ({"b": 2}, "https://example.com/b"),
        ({"d": 4}, "https://example.com/d"),
    ]


def test_popstate_event_state_isolated_from_internal_entry() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []

    def on_pop(evt: PopStateEvent) -> None:
        seen.append(evt.state)

    w.add_event_listener("popstate", on_pop)
    h.push_state({"k": [1]}, "", "/a")
    h.push_state({"k": [2]}, "", "/b")

    h.back()
    assert seen == [{"k": [1]}]
    seen[0]["k"].append(9)

    assert h.state == {"k": [1]}


def test_history_popstate_payload_is_recloned_per_dispatch_for_same_entry() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda evt: seen.append(evt.state))

    h.push_state({"k": [1]}, "", "/a")
    h.push_state({"k": [2]}, "", "/b")

    h.back()
    seen[0]["k"].append(9)
    h.forward()
    h.back()

    assert seen[2] == {"k": [1]}
    assert seen[2] is not seen[0]


def test_history_traversal_noops_do_not_dispatch_popstate() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    count = 0

    def on_pop(_evt: PopStateEvent) -> None:
        nonlocal count
        count += 1

    w.add_event_listener("popstate", on_pop)
    h.go(0)
    h.back()
    h.forward()
    h.go(10)
    h.go(-10)
    assert count == 0


def test_history_push_and_replace_do_not_dispatch_popstate() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda _evt: seen.append("pop"))

    h.push_state({"a": 1}, "", "/a")
    h.replace_state({"b": 2}, "", "/b")

    assert seen == []


@pytest.mark.parametrize("delta", ["1", 1.0, object()])
def test_history_go_rejects_non_int_delta(delta: object) -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    before_href = doc.default_view.location.href

    with pytest.raises(TypeError, match="History.go delta must be an int"):
        h.go(delta)  # type: ignore[arg-type]

    assert doc.default_view.location.href == before_href


def test_history_go_accepts_bool_delta_python_int_compatibility() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []

    w.add_event_listener("popstate", lambda evt: seen.append((evt.state, w.location.href)))
    h.push_state({"a": 1}, "", "/a")

    h.go(False)
    assert w.location.href == "https://example.com/a"
    assert seen == []

    h.go(True)
    assert w.location.href == "https://example.com/a"
    assert seen == []


def test_history_go_zero_is_strict_noop_for_url_and_event() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda _evt: seen.append("pop"))
    h.push_state({"a": 1}, "", "/a")
    before_index = h._index
    before_href = w.location.href

    h.go(0)

    assert h._index == before_index
    assert w.location.href == before_href
    assert seen == []


def test_history_go_zero_is_atomic_noop_for_index_href_and_state() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda _evt: seen.append("popstate"))
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    h.push_state({"k": [1]}, "", "/a#one")
    before_index = h._index
    before_href = w.location.href
    before_state = h.state

    h.go(0)

    assert h._index == before_index
    assert w.location.href == before_href
    assert h.state == before_state
    assert seen == []


def test_history_go_out_of_range_is_strict_noop_for_url_and_event() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda _evt: seen.append("pop"))
    h.push_state({"a": 1}, "", "/a")
    before_index = h._index
    before_href = w.location.href

    h.go(10)
    h.go(-10)

    assert h._index == before_index
    assert w.location.href == before_href
    assert seen == []


def test_history_go_out_of_range_is_atomic_noop_for_index_href_and_state() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda _evt: seen.append("popstate"))
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    h.push_state({"a": 1}, "", "/a#one")
    h.push_state({"b": 2}, "", "/b#two")

    before_end_index = h._index
    before_end_href = w.location.href
    before_end_state = h.state
    h.go(10)
    assert h._index == before_end_index
    assert w.location.href == before_end_href
    assert h.state == before_end_state

    h.go(-1)
    start_index = h._index
    start_href = w.location.href
    start_state = h.state
    h.go(-10)
    assert h._index == start_index
    assert w.location.href == start_href
    assert h.state == start_state
    assert seen == [
        "popstate",
    ]


def test_history_single_entry_back_forward_are_atomic_noops() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda _evt: seen.append("popstate"))
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    before_index = h._index
    before_href = w.location.href
    before_state = h.state

    h.back()
    h.forward()

    assert h._index == before_index
    assert w.location.href == before_href
    assert h.state == before_state
    assert seen == []


def test_history_boundary_wrappers_on_multi_entry_stack_are_atomic_noops() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda _evt: seen.append("popstate"))
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    h.push_state({"a": 1}, "", "/a")
    h.push_state({"b": 2}, "", "/b")

    h.go(-2)
    seen.clear()

    start_index = h._index
    start_href = w.location.href
    start_state = h.state
    h.back()
    assert h._index == start_index
    assert w.location.href == start_href
    assert h.state == start_state
    assert seen == []

    h.go(2)
    seen.clear()

    end_index = h._index
    end_href = w.location.href
    end_state = h.state
    h.forward()
    assert h._index == end_index
    assert w.location.href == end_href
    assert h.state == end_state
    assert seen == []


def test_history_go_in_range_positive_and_negative_traverse_correctly() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda evt: seen.append((evt.state, w.location.href)))

    h.push_state({"a": 1}, "", "/a")
    h.push_state({"b": 2}, "", "/b")

    h.go(-1)
    assert h._index == 1
    assert w.location.href == "https://example.com/a"

    h.go(1)
    assert h._index == 2
    assert w.location.href == "https://example.com/b"
    assert seen == [
        ({"a": 1}, "https://example.com/a"),
        ({"b": 2}, "https://example.com/b"),
    ]


def test_history_in_range_traversal_still_mutates_index_href_and_state() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda evt: seen.append((evt.state, w.location.href)))
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    h.push_state({"a": 1}, "", "/a#one")
    h.push_state({"b": 2}, "", "/a#two")
    seen.clear()

    before_index = h._index
    before_href = w.location.href
    before_state = h.state

    h.back()

    assert h._index != before_index
    assert w.location.href != before_href
    assert h.state != before_state
    assert h._index == 1
    assert w.location.href == "https://example.com/a#one"
    assert h.state == {"a": 1}
    assert seen == [
        ({"a": 1}, "https://example.com/a#one"),
        "hashchange",
    ]


def test_history_push_state_url_none_preserves_current_url_string() -> None:
    doc = Document()
    doc._url = "https://example.com/a"
    h = doc.default_view.history
    h.push_state({"x": 1}, "", None)

    assert doc.default_view.location.href == "https://example.com/a"


def test_history_push_state_invalid_url_is_atomic() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    h.push_state({"ok": 1}, "", "/a")
    before_length = h.length
    before_state = h.state
    before_href = doc.default_view.location.href

    with pytest.raises(SecurityError, match="invalid URL"):
        h.push_state({"bad": 1}, "", "http://[::1")

    assert h.length == before_length
    assert h.state == before_state
    assert doc.default_view.location.href == before_href


def test_history_replace_state_cross_origin_is_atomic() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    h.push_state({"ok": 1}, "", "/a")
    before_length = h.length
    before_state = h.state
    before_href = doc.default_view.location.href

    with pytest.raises(SecurityError, match="cross-origin pushState blocked"):
        h.replace_state({"bad": 1}, "", "https://other.example/")

    assert h.length == before_length
    assert h.state == before_state
    assert doc.default_view.location.href == before_href


def test_history_push_and_replace_store_canonical_href() -> None:
    doc = Document()
    doc._url = "https://example.com/base/index.html"
    h = doc.default_view.history

    h.push_state({"x": 1}, "", "../a/./b?x=1#frag")
    assert doc.default_view.location.href == "https://example.com/a/b?x=1#frag"

    h.replace_state({"y": 2}, "", "https://example.com/a/b?x=1#frag")
    assert doc.default_view.location.href == "https://example.com/a/b?x=1#frag"


def test_history_push_same_effective_url_still_creates_new_entry() -> None:
    doc = Document()
    doc._url = "https://example.com/a/b"
    h = doc.default_view.history

    h.push_state({"x": 1}, "", "./")

    assert h.length == 2
    assert doc.default_view.location.href == "https://example.com/a/"


def test_popstate_event_shape() -> None:
    evt = PopStateEvent(state={"k": 1})
    assert evt.type == "popstate"
    assert evt.bubbles is False
    assert evt.cancelable is False
    assert evt.state == {"k": 1}


def test_hashchange_event_shape() -> None:
    evt = HashChangeEvent(
        old_url="https://example.com/a#one",
        new_url="https://example.com/a#two",
    )
    assert evt.type == "hashchange"
    assert evt.bubbles is False
    assert evt.cancelable is False
    assert evt.old_url == "https://example.com/a#one"
    assert evt.new_url == "https://example.com/a#two"


def test_history_traversal_hash_transition_dispatches_popstate_then_hashchange() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    w = doc.default_view
    h = w.history
    seen = []

    w.add_event_listener("popstate", lambda evt: seen.append(("popstate", evt.state, w.location.href)))
    w.add_event_listener(
        "hashchange",
        lambda evt: seen.append(("hashchange", evt.old_url, evt.new_url)),
    )

    h.push_state({"a": 1}, "", "/page#one")
    h.push_state({"b": 2}, "", "/page#two")
    seen.clear()

    h.back()

    assert seen == [
        ("popstate", {"a": 1}, "https://example.com/page#one"),
        ("hashchange", "https://example.com/page#two", "https://example.com/page#one"),
    ]


def test_history_traversal_non_hash_transition_does_not_dispatch_hashchange() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    w = doc.default_view
    h = w.history
    seen = []

    w.add_event_listener("popstate", lambda _evt: seen.append("popstate"))
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    h.push_state({"a": 1}, "", "/a#frag")
    h.push_state({"b": 2}, "", "/b#frag")
    seen.clear()

    h.back()

    assert seen == ["popstate"]


def test_history_push_and_replace_hash_only_url_update_dispatch_hashchange_once() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener(
        "hashchange",
        lambda evt: seen.append((evt.old_url, evt.new_url)),
    )

    h.push_state({"base": 0}, "", "/a")
    assert seen == []

    seen.clear()
    h.push_state({"a": 1}, "", "/a#one")
    assert seen == [("https://example.com/a", "https://example.com/a#one")]

    seen.clear()
    h.replace_state({"b": 2}, "", "/a#two")
    assert seen == [("https://example.com/a#one", "https://example.com/a#two")]


def test_history_hashchange_not_dispatched_on_push_replace_failures() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("hashchange", lambda _evt: seen.append("hashchange"))

    with pytest.raises(SecurityError, match="invalid URL"):
        h.push_state({"bad": 1}, "", "http://[::1")

    with pytest.raises(SecurityError, match="cross-origin pushState blocked"):
        h.replace_state({"bad": 1}, "", "https://other.example/path#x")

    assert seen == []


def test_history_unsupported_state_raises_type_error() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history

    with pytest.raises(
        TypeError,
        match="History state is not supported by structured-clone-compatible deepcopy",
    ):
        h.push_state({"bad": threading.Lock()}, "", "/a")


def test_history_state_read_isolation_and_per_read_independence() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    h.push_state({"k": [1]}, "", "/a")

    first = h.state
    second = h.state
    assert first == {"k": [1]}
    assert second == {"k": [1]}
    assert first is not second
    assert isinstance(first, dict)
    assert isinstance(second, dict)
    assert first["k"] is not second["k"]

    first["k"].append(9)
    assert h.state == {"k": [1]}


def test_history_push_state_clone_failure_is_atomic() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    before_length = h.length
    before_state = h.state
    before_href = doc.default_view.location.href

    with pytest.raises(
        TypeError,
        match="History state is not supported by structured-clone-compatible deepcopy",
    ):
        h.push_state({"bad": threading.Lock()}, "", "/a")

    assert h.length == before_length
    assert h.state == before_state
    assert doc.default_view.location.href == before_href


def test_history_replace_state_clone_failure_is_atomic() -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    h.push_state({"ok": 1}, "", "/a")
    before_length = h.length
    before_state = h.state
    before_href = doc.default_view.location.href

    with pytest.raises(
        TypeError,
        match="History state is not supported by structured-clone-compatible deepcopy",
    ):
        h.replace_state({"bad": threading.Lock()}, "", "/b")

    assert h.length == before_length
    assert h.state == before_state
    assert doc.default_view.location.href == before_href


def test_history_state_cloning_delegates_to_shared_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    doc = Document()
    doc._url = "https://example.com/"
    h = doc.default_view.history
    calls: list[object] = []

    def _fake_clone(value: object) -> object:
        calls.append(value)
        return {"delegated": True}

    monkeypatch.setattr("aspose_html.dom._history.clone_or_raise_data_clone_error", _fake_clone)

    h.push_state({"a": 1}, "", "/a")
    assert h.state == {"delegated": True}
    assert calls == [{"a": 1}, {"delegated": True}]


def test_location_history_url_integration_atomic_invalid_location_write_keeps_history_entry() -> None:
    doc = Document()
    doc._url = "https://example.com/base"
    w = doc.default_view
    h = w.history

    h.push_state({"s": 1}, "", "/a")
    before_href = w.location.href
    before_doc_url = doc.url
    before_length = h.length
    before_state = h.state

    with pytest.raises(ValueError):
        w.location.port = "99999"

    assert w.location.href == before_href
    assert doc.url == before_doc_url
    assert h.length == before_length
    assert h.state == before_state


def test_history_origin_resolution_fallback_when_current_unparseable() -> None:
    doc = Document()
    doc._url = "about:blank"
    h = doc.default_view.history
    h.push_state({"ok": 1}, "", "about:blank")
    assert h.state == {"ok": 1}

    try:
        h.push_state({"bad": 1}, "", "https://example.com/")
    except SecurityError:
        pass
    else:
        raise AssertionError("Expected SecurityError when current URL is unparseable and target differs")


def test_location_href_setter_hardening_preserves_assign_replace_and_go_contracts() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    w = doc.default_view
    h = w.history
    seen = []
    w.add_event_listener("popstate", lambda evt: seen.append((evt.state, w.location.href)))

    w.location.href = "/seed"
    assert h.length == 1
    assert w.location.href == "https://example.com/seed"

    w.location.assign("/a")
    assert h.length == 2
    assert w.location.href == "https://example.com/a"

    w.location.replace("/b")
    assert h.length == 2
    assert w.location.href == "https://example.com/b"

    h.go(0)
    assert seen == []

    h.go(-1)
    assert w.location.href == "https://example.com/seed"
    assert seen == [(None, "https://example.com/seed")]


def test_back104_history_go_integration_matrix_noop_and_event_ordering() -> None:
    doc = Document()
    doc._url = "https://example.com/start"
    w = doc.default_view
    h = w.history
    seen = []

    w.add_event_listener("popstate", lambda evt: seen.append(("popstate", evt.state, w.location.href)))
    w.add_event_listener("hashchange", lambda evt: seen.append(("hashchange", evt.old_url, evt.new_url)))

    h.push_state({"a": 1}, "", "/page#one")
    h.push_state({"b": 2}, "", "/page#two")
    h.push_state({"c": 3}, "", "/other#two")
    seen.clear()

    before_index = h._index
    before_href = w.location.href

    h.go(0)
    h.go(99)
    h.go(-99)

    assert h._index == before_index
    assert w.location.href == before_href
    assert seen == []

    h.go(-1)
    assert seen == [
        ("popstate", {"b": 2}, "https://example.com/page#two"),
    ]

    seen.clear()
    h.go(-1)
    assert seen == [
        ("popstate", {"a": 1}, "https://example.com/page#one"),
        ("hashchange", "https://example.com/page#two", "https://example.com/page#one"),
    ]

    seen.clear()
    h.go(2)
    assert seen == [
        ("popstate", {"c": 3}, "https://example.com/other#two"),
    ]
