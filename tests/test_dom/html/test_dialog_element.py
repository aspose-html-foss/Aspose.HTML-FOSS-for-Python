"""Tests for HTMLDialogElement.show / show_modal / close / return_value.

 /  /  Group D.
"""

import pytest
from aspose_html.dom import Document
from aspose_html.dom.html import HTMLDialogElement


def _make_dialog() -> HTMLDialogElement:
    doc = Document()
    dlg = doc.create_element("dialog")
    assert isinstance(dlg, HTMLDialogElement)
    return dlg


# ---------------------------------------------------------------------------
# AC-8: dlg.show() sets dlg.open == True
# ---------------------------------------------------------------------------

def test_dialog_show_sets_open_true():
    dlg = _make_dialog()
    assert dlg.open is False
    dlg.show()
    assert dlg.open is True


def test_dialog_show_idempotent():
    """show() on an already-open dialog is a no-op — does not raise."""
    dlg = _make_dialog()
    dlg.show()
    dlg.show()  # second call must not raise
    assert dlg.open is True


# ---------------------------------------------------------------------------
# AC-9: dlg.show_modal() sets dlg.open == True
# ---------------------------------------------------------------------------

def test_dialog_show_modal_sets_open_true():
    dlg = _make_dialog()
    assert dlg.open is False
    dlg.show_modal()
    assert dlg.open is True


def test_dialog_show_modal_idempotent():
    dlg = _make_dialog()
    dlg.show_modal()
    dlg.show_modal()
    assert dlg.open is True


# ---------------------------------------------------------------------------
# AC-10: dlg.close() → open == False, return_value == ""
# ---------------------------------------------------------------------------

def test_dialog_close_no_return_value():
    dlg = _make_dialog()
    dlg.show()
    dlg.close()
    assert dlg.open is False
    assert dlg.return_value == ""


def test_dialog_close_idempotent():
    """close() on an already-closed dialog must not raise."""
    dlg = _make_dialog()
    dlg.close()  # called without ever opening
    assert dlg.open is False


# ---------------------------------------------------------------------------
# AC-11: dlg.close("ok") → open == False, return_value == "ok"
# ---------------------------------------------------------------------------

def test_dialog_close_with_return_value():
    dlg = _make_dialog()
    dlg.show_modal()
    dlg.close("ok")
    assert dlg.open is False
    assert dlg.return_value == "ok"


def test_dialog_close_empty_string_explicit():
    dlg = _make_dialog()
    dlg.show()
    dlg.close("")
    assert dlg.open is False
    assert dlg.return_value == ""


def test_dialog_close_arbitrary_string():
    dlg = _make_dialog()
    dlg.show()
    dlg.close("submitted")
    assert dlg.return_value == "submitted"


# ---------------------------------------------------------------------------
# AC-12: return_value property is readable and writable
# ---------------------------------------------------------------------------

def test_dialog_return_value_default_empty():
    dlg = _make_dialog()
    assert dlg.return_value == ""


def test_dialog_return_value_setter():
    dlg = _make_dialog()
    dlg.return_value = "cancel"
    assert dlg.return_value == "cancel"


def test_dialog_return_value_reflects_returnvalue_attribute():
    """return_value mirrors the 'returnvalue' content attribute."""
    dlg = _make_dialog()
    dlg.set_attribute("returnvalue", "attr-set")
    assert dlg.return_value == "attr-set"


def test_dialog_return_value_setter_updates_attribute():
    dlg = _make_dialog()
    dlg.return_value = "via-property"
    assert dlg.get_attribute("returnvalue") == "via-property"


# ---------------------------------------------------------------------------
# Interaction: show → close sequence updates both open and return_value
# ---------------------------------------------------------------------------

def test_dialog_show_close_sequence():
    dlg = _make_dialog()
    dlg.show()
    assert dlg.open is True
    dlg.close("done")
    assert dlg.open is False
    assert dlg.return_value == "done"


def test_dialog_show_modal_then_close():
    dlg = _make_dialog()
    dlg.show_modal()
    assert dlg.open is True
    dlg.close("modal-result")
    assert dlg.open is False
    assert dlg.return_value == "modal-result"


def test_dialog_reopen_after_close():
    """Can re-open a closed dialog."""
    dlg = _make_dialog()
    dlg.show()
    dlg.close("first")
    assert dlg.open is False
    dlg.show()
    assert dlg.open is True
