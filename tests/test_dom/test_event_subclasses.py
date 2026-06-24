"""Tests for  — DOM event subclasses.

Covers UIEvent, MouseEvent, KeyboardEvent, FocusEvent, InputEvent, ErrorEvent
and the Document.create_event() extension ( / ).

Acceptance criteria AC-1 through AC-12 are covered by named test functions.
"""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    Event,
    ErrorEvent,
    FocusEvent,
    InputEvent,
    KeyboardEvent,
    MouseEvent,
    UIEvent,
)
from aspose_html.dom._exceptions import NotSupportedError


# ---------------------------------------------------------------------------
# AC-1 — all six classes importable from aspose_html.dom
# ---------------------------------------------------------------------------


def test_ac1_importable() -> None:
    """AC-1: All six new event classes importable from aspose_html.dom."""
    # already imported at module level; just assert they're not None
    assert UIEvent is not None
    assert MouseEvent is not None
    assert KeyboardEvent is not None
    assert FocusEvent is not None
    assert InputEvent is not None
    assert ErrorEvent is not None


# ---------------------------------------------------------------------------
# AC-2 — UIEvent properties
# ---------------------------------------------------------------------------


def test_ac2_uievent_properties() -> None:
    """AC-2: UIEvent('scroll', detail=3).detail == 3 and .view is None."""
    e = UIEvent("scroll", detail=3)
    assert e.type == "scroll"
    assert e.detail == 3
    assert e.view is None


def test_uievent_defaults() -> None:
    """UIEvent defaults: detail=0, bubbles=False, cancelable=False."""
    e = UIEvent("resize")
    assert e.detail == 0
    assert e.bubbles is False
    assert e.cancelable is False


# ---------------------------------------------------------------------------
# AC-3 — MouseEvent properties
# ---------------------------------------------------------------------------


def test_ac3_mouseevent_properties() -> None:
    """AC-3: MouseEvent('click', button=0, client_x=10, client_y=20) properties."""
    e = MouseEvent("click", button=0, client_x=10, client_y=20)
    assert e.type == "click"
    assert e.button == 0
    assert e.client_x == 10
    assert e.client_y == 20


def test_mouseevent_all_properties() -> None:
    """MouseEvent: check all properties including modifier keys and stubs."""
    e = MouseEvent(
        "mousedown",
        bubbles=True,
        cancelable=True,
        detail=1,
        button=2,
        buttons=3,
        client_x=5,
        client_y=6,
        screen_x=100,
        screen_y=200,
        alt_key=True,
        ctrl_key=True,
        meta_key=True,
        shift_key=True,
        related_target=None,
    )
    assert e.button == 2
    assert e.buttons == 3
    assert e.client_x == 5
    assert e.client_y == 6
    assert e.screen_x == 100
    assert e.screen_y == 200
    assert e.alt_key is True
    assert e.ctrl_key is True
    assert e.meta_key is True
    assert e.shift_key is True
    assert e.related_target is None
    # Stub-zero properties
    assert e.offset_x == 0
    assert e.offset_y == 0
    assert e.page_x == 0
    assert e.page_y == 0
    # Inherited UIEvent
    assert e.detail == 1
    assert e.view is None


# ---------------------------------------------------------------------------
# AC-4 — KeyboardEvent properties
# ---------------------------------------------------------------------------


def test_ac4_keyboardevent_properties() -> None:
    """AC-4: KeyboardEvent('keydown', key='Enter', code='Enter', shift_key=True)."""
    e = KeyboardEvent("keydown", key="Enter", code="Enter", shift_key=True)
    assert e.key == "Enter"
    assert e.code == "Enter"
    assert e.shift_key is True


def test_keyboardevent_all_properties() -> None:
    """KeyboardEvent: check all properties including location, repeat, is_composing."""
    e = KeyboardEvent(
        "keypress",
        bubbles=True,
        cancelable=True,
        key="a",
        code="KeyA",
        location=KeyboardEvent.DOM_KEY_LOCATION_LEFT,
        repeat=True,
        is_composing=True,
        alt_key=True,
        ctrl_key=False,
        meta_key=False,
        shift_key=False,
    )
    assert e.key == "a"
    assert e.code == "KeyA"
    assert e.location == KeyboardEvent.DOM_KEY_LOCATION_LEFT
    assert e.repeat is True
    assert e.is_composing is True
    assert e.alt_key is True
    assert e.ctrl_key is False
    assert e.meta_key is False
    assert e.shift_key is False


def test_keyboardevent_location_constants() -> None:
    """DOM_KEY_LOCATION_* class constants have expected values."""
    assert KeyboardEvent.DOM_KEY_LOCATION_STANDARD == 0
    assert KeyboardEvent.DOM_KEY_LOCATION_LEFT == 1
    assert KeyboardEvent.DOM_KEY_LOCATION_RIGHT == 2
    assert KeyboardEvent.DOM_KEY_LOCATION_NUMPAD == 3


# ---------------------------------------------------------------------------
# AC-5 — FocusEvent properties
# ---------------------------------------------------------------------------


def test_ac5_focusevent_properties() -> None:
    """AC-5: FocusEvent('focus').related_target is None."""
    e = FocusEvent("focus")
    assert e.type == "focus"
    assert e.related_target is None


# ---------------------------------------------------------------------------
# AC-6 — InputEvent properties
# ---------------------------------------------------------------------------


def test_ac6_inputevent_properties() -> None:
    """AC-6: InputEvent('input', data='a', input_type='insertText')."""
    e = InputEvent("input", data="a", input_type="insertText")
    assert e.data == "a"
    assert e.input_type == "insertText"


def test_inputevent_defaults() -> None:
    """InputEvent defaults: data=None, input_type='', is_composing=False."""
    e = InputEvent("beforeinput")
    assert e.data is None
    assert e.input_type == ""
    assert e.is_composing is False


# ---------------------------------------------------------------------------
# AC-7 — ErrorEvent properties
# ---------------------------------------------------------------------------


def test_ac7_errorevent_properties() -> None:
    """AC-7: ErrorEvent('error', message='oops', lineno=42, error=None)."""
    e = ErrorEvent("error", message="oops", lineno=42, error=None)
    assert e.message == "oops"
    assert e.lineno == 42
    assert e.error is None


def test_errorevent_all_properties() -> None:
    """ErrorEvent: check all properties."""
    e = ErrorEvent(
        "error",
        message="ReferenceError: x is not defined",
        filename="app.js",
        lineno=5,
        colno=12,
        error=None,
    )
    assert e.message == "ReferenceError: x is not defined"
    assert e.filename == "app.js"
    assert e.lineno == 5
    assert e.colno == 12
    assert e.error is None


# ---------------------------------------------------------------------------
# AC-8 — inheritance chain
# ---------------------------------------------------------------------------


def test_ac8_inheritance_chain() -> None:
    """AC-8: MouseEvent is UIEvent is Event; UIEvent is Event."""
    assert isinstance(UIEvent("x"), Event)
    assert isinstance(MouseEvent("x"), UIEvent)
    assert isinstance(MouseEvent("x"), Event)
    assert isinstance(KeyboardEvent("x"), UIEvent)
    assert isinstance(FocusEvent("x"), UIEvent)
    assert isinstance(InputEvent("x"), UIEvent)
    # ErrorEvent inherits from Event, NOT UIEvent
    assert isinstance(ErrorEvent("x"), Event)
    assert not isinstance(ErrorEvent("x"), UIEvent)


# ---------------------------------------------------------------------------
# AC-9 — doc.create_event("MouseEvent") returns MouseEvent
# ---------------------------------------------------------------------------


def test_ac9_create_event_mouseevent() -> None:
    """AC-9: doc.create_event('MouseEvent') returns a MouseEvent instance."""
    doc = Document()
    ev = doc.create_event("MouseEvent")
    assert isinstance(ev, MouseEvent)
    assert isinstance(ev, UIEvent)
    assert isinstance(ev, Event)


# ---------------------------------------------------------------------------
# AC-10 — doc.create_event("UIEvent") case-insensitive
# ---------------------------------------------------------------------------


def test_ac10_create_event_uievent_case_insensitive() -> None:
    """AC-10: doc.create_event('UIEvent') and 'uievent' both return UIEvent."""
    doc = Document()
    assert isinstance(doc.create_event("UIEvent"), UIEvent)
    assert isinstance(doc.create_event("uievent"), UIEvent)
    assert isinstance(doc.create_event("UIEVENT"), UIEvent)


def test_create_event_all_new_types() -> None:
    """create_event dispatch covers all six new type strings."""
    doc = Document()
    assert isinstance(doc.create_event("UIEvent"), UIEvent)
    assert isinstance(doc.create_event("MouseEvent"), MouseEvent)
    assert isinstance(doc.create_event("MouseEvents"), MouseEvent)  # legacy alias
    assert isinstance(doc.create_event("KeyboardEvent"), KeyboardEvent)
    assert isinstance(doc.create_event("FocusEvent"), FocusEvent)
    assert isinstance(doc.create_event("InputEvent"), InputEvent)
    assert isinstance(doc.create_event("ErrorEvent"), ErrorEvent)


def test_create_event_existing_types_still_work() -> None:
    """Non-regression: existing Event/CustomEvent dispatch unaffected."""
    from aspose_html.dom import CustomEvent
    doc = Document()
    assert isinstance(doc.create_event("Event"), Event)
    assert isinstance(doc.create_event("Events"), Event)
    assert isinstance(doc.create_event("HTMLEvents"), Event)
    assert isinstance(doc.create_event("CustomEvent"), CustomEvent)


# ---------------------------------------------------------------------------
# AC-11 — unsupported interface raises NotSupportedError
# ---------------------------------------------------------------------------


def test_ac11_unsupported_event_raises() -> None:
    """AC-11: doc.create_event('UnsupportedEvent') raises NotSupportedError."""
    doc = Document()
    with pytest.raises(NotSupportedError):
        doc.create_event("UnsupportedEvent")


# ---------------------------------------------------------------------------
# AC-12 — docstring examples pass (verified via pytest --doctest-modules
#          invoked separately; this test is the structural check)
# ---------------------------------------------------------------------------


def test_ac12_docstring_examples_exist() -> None:
    """AC-12: All six classes have docstrings with >>> examples."""
    for cls in (UIEvent, MouseEvent, KeyboardEvent, FocusEvent, InputEvent, ErrorEvent):
        assert cls.__doc__ is not None, f"{cls.__name__} missing docstring"
        assert ">>>" in cls.__doc__, f"{cls.__name__} docstring missing >>> example"


# ---------------------------------------------------------------------------
# init_event compatibility — inherited from Event
# ---------------------------------------------------------------------------


def test_init_event_works_on_subclasses() -> None:
    """init_event() inherited from Event resets type/bubbles/cancelable on subclass instances."""
    e = MouseEvent("click", bubbles=True, cancelable=True)
    e.init_event("dblclick", False, False)
    assert e.type == "dblclick"
    assert e.bubbles is False
    assert e.cancelable is False

    k = KeyboardEvent("keydown", bubbles=True)
    k.init_event("keyup", False, False)
    assert k.type == "keyup"

    f = FocusEvent("focus")
    f.init_event("blur", False, False)
    assert f.type == "blur"
