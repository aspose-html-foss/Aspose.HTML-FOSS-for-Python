"""Track 43 integration hardening tests (BACK-189 / SPEC-098 / ADR-172).

Cross-component integration checks for BACK-185..BACK-188:
  Group A — DOM event subclasses: hierarchy, create_event dispatch, properties,
            listener round-trip
  Group B — insert_adjacent_element and webkit_matches_selector
  Group C — HTMLSummaryElement / HTMLMenuElement: create_element, parse, serialise,
            get_elements_by_tag_name live collection
  Group D — AbortController / AbortSignal: state, abort, idempotency, import
  Group E — Doctest sweep for four touched public source files
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from aspose_html.dom import (
    AbortController,
    AbortSignal,
    Document,
    ErrorEvent,
    Event,
    FocusEvent,
    HTMLMenuElement,
    HTMLSummaryElement,
    InputEvent,
    KeyboardEvent,
    MouseEvent,
    UIEvent,
)
from aspose_html.dom._exceptions import NoModificationAllowedError
from aspose_html.dom._exceptions import SyntaxError as _SyntaxError
from aspose_html.dom.html._elements import HTMLElement
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Group A — DOM event subclasses
# ---------------------------------------------------------------------------


def test_event_hierarchy() -> None:
    """MouseEvent is a UIEvent is an Event; MRO is correct."""
    me = MouseEvent("click")
    assert isinstance(me, UIEvent)
    assert isinstance(me, Event)

    ue = UIEvent("scroll")
    assert isinstance(ue, Event)
    assert not isinstance(ue, MouseEvent)


def test_create_event_dispatch() -> None:
    """Document.create_event returns the correct class for all six types."""
    doc = Document()
    assert type(doc.create_event("MouseEvent")) is MouseEvent
    assert type(doc.create_event("KeyboardEvent")) is KeyboardEvent
    assert type(doc.create_event("UIEvent")) is UIEvent
    assert type(doc.create_event("FocusEvent")) is FocusEvent
    assert type(doc.create_event("InputEvent")) is InputEvent
    assert type(doc.create_event("ErrorEvent")) is ErrorEvent


def test_create_event_case_insensitive() -> None:
    """create_event is case-insensitive: 'mouseevent' returns MouseEvent."""
    doc = Document()
    assert type(doc.create_event("mouseevent")) is MouseEvent
    assert type(doc.create_event("KEYBOARDEVENT")) is KeyboardEvent


def test_mouse_event_properties() -> None:
    """MouseEvent carries correct button and coordinate fields."""
    e = MouseEvent("click", button=2, client_x=5, client_y=10)
    assert e.type == "click"
    assert e.button == 2
    assert e.client_x == 5
    assert e.client_y == 10


def test_keyboard_event_properties() -> None:
    """KeyboardEvent carries correct key, code, and modifier fields."""
    e = KeyboardEvent("keydown", key="A", code="KeyA", shift_key=True)
    assert e.key == "A"
    assert e.code == "KeyA"
    assert e.shift_key is True


def test_error_event_properties() -> None:
    """ErrorEvent carries message, lineno, and error fields."""
    e = ErrorEvent("error", message="boom", lineno=7, error=None)
    assert e.message == "boom"
    assert e.lineno == 7
    assert e.error is None


def test_event_dispatch_via_listener() -> None:
    """UIEvent dispatched on a Document reaches a registered listener."""
    doc = Document()
    received: list[Event] = []
    doc.add_event_listener("scroll", lambda ev: received.append(ev))
    doc.dispatch_event(UIEvent("scroll"))
    assert len(received) == 1
    assert isinstance(received[0], UIEvent)
    assert received[0].type == "scroll"


# ---------------------------------------------------------------------------
# Group B — insert_adjacent_element and webkit_matches_selector
# ---------------------------------------------------------------------------


def test_insert_adjacent_element_beforeend() -> None:
    """insert_adjacent_element('beforeend', child) appends; returns child."""
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    result = parent.insert_adjacent_element("beforeend", child)
    assert result is child
    assert parent.first_child is child


def test_insert_adjacent_element_afterbegin() -> None:
    """insert_adjacent_element('afterbegin', el) inserts as first child."""
    doc = Document()
    parent = doc.create_element("div")
    first = doc.create_element("span")
    second = doc.create_element("p")
    parent.append_child(first)
    parent.append_child(second)

    new = doc.create_element("b")
    parent.insert_adjacent_element("afterbegin", new)
    assert parent.first_child is new


def test_insert_adjacent_element_beforebegin() -> None:
    """insert_adjacent_element('beforebegin', sibling) inserts before self."""
    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)
    parent = doc.create_element("div")
    body.append_child(parent)

    sibling = doc.create_element("section")
    parent.insert_adjacent_element("beforebegin", sibling)

    children = list(body.child_nodes)
    assert children[0] is sibling
    assert children[1] is parent


def test_insert_adjacent_element_none() -> None:
    """insert_adjacent_element('beforeend', None) returns None; tree unchanged."""
    doc = Document()
    el = doc.create_element("div")
    result = el.insert_adjacent_element("beforeend", None)
    assert result is None
    assert el.first_child is None


def test_insert_adjacent_element_bad_position() -> None:
    """insert_adjacent_element raises SyntaxError for invalid position."""
    doc = Document()
    el = doc.create_element("div")
    child = doc.create_element("span")
    with pytest.raises(_SyntaxError):
        el.insert_adjacent_element("invalid", child)


def test_insert_adjacent_element_detached_beforebegin() -> None:
    """insert_adjacent_element('beforebegin', el) on detached element raises."""
    doc = Document()
    detached = doc.create_element("div")
    sibling = doc.create_element("span")
    with pytest.raises(NoModificationAllowedError):
        detached.insert_adjacent_element("beforebegin", sibling)


def test_webkit_matches_selector_matches() -> None:
    """webkit_matches_selector('div') == matches('div') for a <div>."""
    doc = Document()
    el = doc.create_element("div")
    assert el.webkit_matches_selector("div") == el.matches("div")
    assert el.webkit_matches_selector("div") is True


def test_webkit_matches_selector_no_match() -> None:
    """webkit_matches_selector('span') is False for a <div> element."""
    doc = Document()
    el = doc.create_element("div")
    assert el.webkit_matches_selector("span") is False


# ---------------------------------------------------------------------------
# Group C — HTMLSummaryElement and HTMLMenuElement
# ---------------------------------------------------------------------------


def test_create_element_summary() -> None:
    """create_element('summary') returns HTMLSummaryElement, an HTMLElement."""
    doc = Document()
    el = doc.create_element("summary")
    assert type(el) is HTMLSummaryElement
    assert isinstance(el, HTMLElement)


def test_create_element_menu() -> None:
    """create_element('menu') returns HTMLMenuElement, an HTMLElement."""
    doc = Document()
    el = doc.create_element("menu")
    assert type(el) is HTMLMenuElement
    assert isinstance(el, HTMLElement)


def test_parse_summary_in_details() -> None:
    """<summary> child of <details> parses as HTMLSummaryElement."""
    doc = HTMLDocument.parse(
        "<html><body><details><summary>Open</summary><p>content</p></details></body></html>"
    )
    details = doc.query_selector("details")
    assert details is not None
    summary = details.first_element_child
    assert summary is not None
    assert isinstance(summary, HTMLSummaryElement)


def test_parse_menu_element() -> None:
    """<menu> element parses as HTMLMenuElement."""
    doc = HTMLDocument.parse(
        "<html><body><menu><li>item</li></menu></body></html>"
    )
    menu = doc.query_selector("menu")
    assert menu is not None
    assert isinstance(menu, HTMLMenuElement)


def test_summary_serialise() -> None:
    """HTMLSummaryElement serialises as <summary>...</summary>, not self-closing."""
    doc = Document()
    el = doc.create_element("summary")
    el.text_content = "Open"
    html = el.outer_html
    assert "<summary>" in html
    assert "</summary>" in html


def test_menu_serialise() -> None:
    """HTMLMenuElement serialises as <menu>...</menu>, not self-closing."""
    doc = Document()
    el = doc.create_element("menu")
    el.text_content = "items"
    html = el.outer_html
    assert "<menu>" in html
    assert "</menu>" in html


def test_get_elements_by_tag_name_summary() -> None:
    """get_elements_by_tag_name('summary') returns 3 HTMLSummaryElements."""
    doc = HTMLDocument.parse(
        "<html><body>"
        "<details><summary>A</summary></details>"
        "<details><summary>B</summary></details>"
        "<details><summary>C</summary></details>"
        "</body></html>"
    )
    summaries = doc.get_elements_by_tag_name("summary")
    items = list(summaries)
    assert len(items) == 3
    for item in items:
        assert isinstance(item, HTMLSummaryElement)


# ---------------------------------------------------------------------------
# Group D — AbortController / AbortSignal
# ---------------------------------------------------------------------------


def test_abort_initial_state() -> None:
    """New AbortController: signal.aborted is False, signal.reason is None."""
    ctrl = AbortController()
    assert ctrl.signal.aborted is False
    assert ctrl.signal.reason is None


def test_abort_sets_flag() -> None:
    """abort() makes signal.aborted True."""
    ctrl = AbortController()
    ctrl.abort()
    assert ctrl.signal.aborted is True


def test_abort_with_reason() -> None:
    """abort('timeout') stores 'timeout' in signal.reason."""
    ctrl = AbortController()
    ctrl.abort("timeout")
    assert ctrl.signal.reason == "timeout"


def test_abort_idempotent() -> None:
    """Second abort() call leaves reason unchanged (idempotency)."""
    ctrl = AbortController()
    ctrl.abort("first")
    ctrl.abort("second")
    assert ctrl.signal.reason == "first"
    assert ctrl.signal.aborted is True


def test_abort_signal_same_instance() -> None:
    """ctrl.signal returns the same AbortSignal instance each time."""
    ctrl = AbortController()
    assert ctrl.signal is ctrl.signal


def test_abort_signal_repr() -> None:
    """repr(ctrl.signal) contains 'aborted=False' before abort."""
    ctrl = AbortController()
    r = repr(ctrl.signal)
    assert "aborted=False" in r


def test_abort_import() -> None:
    """from aspose_html.dom import AbortController, AbortSignal succeeds."""
    from aspose_html.dom import AbortController as AC, AbortSignal as AS  # noqa: F401
    assert AC is not None
    assert AS is not None


# ---------------------------------------------------------------------------
# Group E — Doctest sweep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "src/aspose_html/dom/_event.py",
        "src/aspose_html/dom/_element.py",
        "src/aspose_html/dom/html/_elements.py",
        "src/aspose_html/dom/_abort_controller.py",
    ],
)
def test_doctest_sweep(path: str) -> None:
    """All >>> docstring examples in the given source file execute cleanly."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--doctest-modules", path, "-q"],
        capture_output=True,
        text=True,
        cwd=str(
            __import__("pathlib").Path(__file__).parent.parent.parent
        ),
    )
    assert result.returncode == 0, result.stdout + result.stderr
