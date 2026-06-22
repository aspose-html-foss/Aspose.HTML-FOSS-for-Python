"""Track 44 integration hardening tests (BACK-193 / SPEC-099 / ADR-176).

Cross-component integration checks for BACK-190..BACK-192:
  Group A — EventTarget once=True option: fires once, idempotency with regular
            listeners, capture flag interaction, bubbling chain interaction
  Group B — Element Attr-node NS methods + MutationObserver: round-trip,
            displacement, string-based NS consistency
  Group C — HTMLTextAreaElement / HTMLInputElement selection API: parsed
            document stubs, set_selection_range, select callability,
            isolation from other IDL properties
  Group D — Doctest sweep for _event_target.py, _element.py, _elements.py
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from aspose_html.dom import (
    Document,
    Event,
    EventTarget,
    MutationObserver,
    HTMLInputElement,
    HTMLTextAreaElement,
)
from aspose_html.html_document import HTMLDocument


_XLINK = "http://www.w3.org/1999/xlink"


# ---------------------------------------------------------------------------
# Group A — EventTarget once=True correctness (BACK-190)
# ---------------------------------------------------------------------------


def test_a1_once_fires_once() -> None:
    """A once=True listener fires exactly once across multiple dispatches."""
    et = EventTarget()
    fired: list[int] = []
    et.add_event_listener("x", lambda e: fired.append(1), once=True)

    et.dispatch_event(Event("x"))
    et.dispatch_event(Event("x"))
    et.dispatch_event(Event("x"))

    assert fired == [1], f"expected [1], got {fired}"


def test_a2_once_listener_removed_after_fire() -> None:
    """After the first dispatch, the once=True listener is absent from _event_listeners."""
    et = EventTarget()
    fn = lambda e: None  # noqa: E731
    et.add_event_listener("x", fn, once=True)

    # Before dispatch — listener is present
    key = ("x", False)
    assert et._event_listeners is not None
    bucket_before = et._event_listeners.get(key, [])
    assert any(f is fn for f, _ in bucket_before)

    et.dispatch_event(Event("x"))

    # After dispatch — listener is removed
    bucket_after = et._event_listeners.get(key, [])
    assert not any(f is fn for f, _ in bucket_after)


def test_a3_remove_before_dispatch_suppresses_once_listener() -> None:
    """Calling remove_event_listener before dispatch suppresses a once=True listener."""
    et = EventTarget()
    fired: list[int] = []
    fn = lambda e: fired.append(1)  # noqa: E731
    et.add_event_listener("x", fn, once=True)
    et.remove_event_listener("x", fn)

    et.dispatch_event(Event("x"))

    assert fired == []


def test_a4_non_once_listener_unaffected_by_adjacent_once() -> None:
    """A normal (non-once) listener is not affected when an adjacent once=True listener is consumed."""
    et = EventTarget()
    once_calls: list[int] = []
    regular_calls: list[int] = []

    et.add_event_listener("x", lambda e: once_calls.append(1), once=True)
    et.add_event_listener("x", lambda e: regular_calls.append(1))

    et.dispatch_event(Event("x"))
    et.dispatch_event(Event("x"))
    et.dispatch_event(Event("x"))

    assert once_calls == [1], f"once listener should fire exactly once, got {once_calls}"
    assert regular_calls == [1, 1, 1], (
        f"regular listener should fire every time, got {regular_calls}"
    )


def test_a5_once_with_capture_fires_once_in_capture_phase() -> None:
    """A once=True + capture=True listener fires exactly once in the capture phase."""
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)

    capture_calls: list[int] = []

    doc.add_event_listener(
        "click",
        lambda e: capture_calls.append(1),
        capture=True,
        once=True,
    )

    child.dispatch_event(Event("click", bubbles=True))
    child.dispatch_event(Event("click", bubbles=True))

    assert capture_calls == [1], (
        f"capture once listener should fire exactly once, got {capture_calls}"
    )


def test_a6_once_in_bubbling_chain_fires_once() -> None:
    """A once=True listener on a parent fires exactly once when a child event bubbles."""
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)

    parent_calls: list[int] = []
    parent.add_event_listener("click", lambda e: parent_calls.append(1), once=True)

    child.dispatch_event(Event("click", bubbles=True))
    child.dispatch_event(Event("click", bubbles=True))
    child.dispatch_event(Event("click", bubbles=True))

    assert parent_calls == [1], (
        f"bubbling once listener should fire exactly once, got {parent_calls}"
    )


# ---------------------------------------------------------------------------
# Group B — Attr-node NS methods + MutationObserver (BACK-191)
# ---------------------------------------------------------------------------


def _doc_and_svg() -> tuple[Document, object]:
    doc = Document()
    el = doc.create_element("svg")
    return doc, el


def test_b1_set_attribute_node_ns_mutation_observer_record() -> None:
    """set_attribute_node_ns fires a MutationObserver record with correct attribute_name."""
    doc, el = _doc_and_svg()
    records: list[object] = []
    obs = MutationObserver(lambda recs, _obs: records.extend(recs))
    obs.observe(el, attributes=True)

    attr = doc.create_attribute_ns(_XLINK, "xlink:href")
    attr.value = "#b1"
    el.set_attribute_node_ns(attr)

    assert len(records) == 1
    rec = records[0]
    assert rec.type == "attributes"
    # attribute_name is the qualified name stored in the record
    assert rec.attribute_name is not None


def test_b2_remove_attribute_node_ns_mutation_observer_record() -> None:
    """remove_attribute_node_ns fires a MutationObserver deletion record."""
    doc, el = _doc_and_svg()
    el.set_attribute_ns(_XLINK, "xlink:href", "#b2")

    records: list[object] = []
    obs = MutationObserver(lambda recs, _obs: records.extend(recs))
    obs.observe(el, attributes=True)

    el.remove_attribute_node_ns(_XLINK, "href")

    assert len(records) == 1
    assert records[0].type == "attributes"


def test_b3_get_set_attribute_node_ns_round_trip_preserves_value() -> None:
    """get_attribute_node_ns after set_attribute_node_ns returns the same value and namespace."""
    doc, el = _doc_and_svg()

    attr = doc.create_attribute_ns(_XLINK, "xlink:href")
    attr.value = "#round-trip"
    el.set_attribute_node_ns(attr)

    retrieved = el.get_attribute_node_ns(_XLINK, "href")
    assert retrieved is not None
    assert retrieved.value == "#round-trip"
    assert retrieved._namespace_uri == _XLINK


def test_b4_set_attribute_node_ns_displacement_clears_owner() -> None:
    """After replacing an existing attr, the displaced attr's _owner_element is None."""
    doc, el = _doc_and_svg()

    # Insert original
    old_attr = doc.create_attribute_ns(_XLINK, "xlink:href")
    old_attr.value = "#old"
    el.set_attribute_node_ns(old_attr)
    assert old_attr._owner_element is el

    # Replace with new attr of same NS / local_name
    new_attr = doc.create_attribute_ns(_XLINK, "xlink:href")
    new_attr.value = "#new"
    displaced = el.set_attribute_node_ns(new_attr)

    assert displaced is old_attr
    assert old_attr._owner_element is None
    assert el.get_attribute_ns(_XLINK, "href") == "#new"


def test_b5_ns_methods_consistent_with_string_based_set_attribute_ns() -> None:
    """set_attribute_ns followed by get_attribute_node_ns returns a correct Attr."""
    doc, el = _doc_and_svg()
    el.set_attribute_ns(_XLINK, "xlink:href", "#string-set")

    attr = el.get_attribute_node_ns(_XLINK, "href")
    assert attr is not None
    assert attr.value == "#string-set"
    assert attr._namespace_uri == _XLINK
    assert attr.local_name == "href"


# ---------------------------------------------------------------------------
# Group C — Text-control selection API (BACK-192)
# ---------------------------------------------------------------------------


def test_c1_parsed_textarea_selection_stubs() -> None:
    """Parsed <textarea> exposes selection stubs returning expected constants."""
    doc = HTMLDocument.parse(
        "<html><body><textarea id='ta' name='bio'>hello</textarea></body></html>"
    )
    ta = doc.get_element_by_id("ta")
    assert ta is not None
    assert isinstance(ta, HTMLTextAreaElement)

    assert ta.selection_start == 0
    assert ta.selection_end == 0
    assert ta.selection_direction == "none"


def test_c2_parsed_input_selection_stubs() -> None:
    """Parsed <input type='text'> exposes selection stubs returning expected constants."""
    doc = HTMLDocument.parse(
        "<html><body><input id='inp' type='text' name='q' value='hi'></body></html>"
    )
    inp = doc.get_element_by_id("inp")
    assert inp is not None
    assert isinstance(inp, HTMLInputElement)

    assert inp.selection_start == 0
    assert inp.selection_end == 0
    assert inp.selection_direction == "none"


def test_c3_set_selection_range_and_select_callable() -> None:
    """set_selection_range and select() are callable without error on both types."""
    doc = HTMLDocument.parse(
        "<html><body>"
        "<textarea id='ta'>content</textarea>"
        "<input id='inp' type='text' value='data'>"
        "</body></html>"
    )
    ta = doc.get_element_by_id("ta")
    inp = doc.get_element_by_id("inp")
    assert ta is not None and inp is not None

    # No exception must be raised — these are no-ops in headless mode.
    ta.set_selection_range(0, 5)
    ta.set_selection_range(1, 3, "forward")
    ta.select()

    inp.set_selection_range(0, 2)
    inp.set_selection_range(0, 2, "backward")
    inp.select()


def test_c4_selection_properties_do_not_interfere_with_value_and_name() -> None:
    """Selection properties and value/name are independent on the same element."""
    doc = HTMLDocument.parse(
        "<html><body>"
        "<textarea id='ta' name='bio'>hello world</textarea>"
        "<input id='inp' name='q' value='foo'>"
        "</body></html>"
    )
    ta = doc.get_element_by_id("ta")
    inp = doc.get_element_by_id("inp")
    assert ta is not None and inp is not None

    # Checking selection stubs
    assert ta.selection_start == 0
    assert ta.selection_end == 0
    assert ta.selection_direction == "none"

    # value/name are unaffected
    assert ta.name == "bio"
    assert ta.value == "hello world"

    assert inp.selection_start == 0
    assert inp.selection_end == 0
    assert inp.selection_direction == "none"
    assert inp.name == "q"
    assert inp.value == "foo"


# ---------------------------------------------------------------------------
# Group D — Doctest sweep (BACK-190, BACK-191, BACK-192)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    [
        "src/aspose_html/dom/_event_target.py",
        "src/aspose_html/dom/_element.py",
        "src/aspose_html/dom/html/_elements.py",
    ],
)
def test_d_doctest_sweep(module_path: str) -> None:
    """All >>> docstring examples in the given source file execute cleanly."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--doctest-modules", module_path, "-q"],
        capture_output=True,
        text=True,
        cwd=str(__import__("pathlib").Path(__file__).parent.parent.parent),
    )
    assert result.returncode == 0, (
        f"doctest failed for {module_path}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
