"""Tests for AbortController and AbortSignal stubs (ADR-171 / BACK-188)."""
import pytest

from aspose_html.dom import AbortController, AbortSignal


# ---------------------------------------------------------------------------
# AC #1 — clean import (covered by the import above; test makes it explicit)
# ---------------------------------------------------------------------------


def test_import():
    """from aspose_html.dom import AbortController, AbortSignal succeeds."""
    from aspose_html.dom import AbortController as AC, AbortSignal as AS  # noqa: F401


# ---------------------------------------------------------------------------
# AC #2 — signal.aborted is False initially
# ---------------------------------------------------------------------------


def test_signal_aborted_initially_false():
    ctrl = AbortController()
    assert ctrl.signal.aborted is False


# ---------------------------------------------------------------------------
# AC #3 — signal.reason is None initially
# ---------------------------------------------------------------------------


def test_signal_reason_initially_none():
    ctrl = AbortController()
    assert ctrl.signal.reason is None


# ---------------------------------------------------------------------------
# AC #4 — abort() sets signal.aborted to True
# ---------------------------------------------------------------------------


def test_abort_sets_aborted_true():
    ctrl = AbortController()
    ctrl.abort()
    assert ctrl.signal.aborted is True


# ---------------------------------------------------------------------------
# AC #5 — abort("timeout") sets signal.reason == "timeout"
# ---------------------------------------------------------------------------


def test_abort_sets_reason():
    ctrl = AbortController()
    ctrl.abort("timeout")
    assert ctrl.signal.reason == "timeout"


# ---------------------------------------------------------------------------
# AC #6 — second abort("other") is a no-op; reason remains "timeout"
# ---------------------------------------------------------------------------


def test_abort_is_idempotent():
    ctrl = AbortController()
    ctrl.abort("timeout")
    ctrl.abort("other")
    assert ctrl.signal.reason == "timeout"
    assert ctrl.signal.aborted is True


# ---------------------------------------------------------------------------
# AC #7 — ctrl.signal is ctrl.signal (same instance on every access)
# ---------------------------------------------------------------------------


def test_signal_is_same_instance():
    ctrl = AbortController()
    assert ctrl.signal is ctrl.signal


# ---------------------------------------------------------------------------
# AC #8 — isinstance(ctrl.signal, AbortSignal) is True
# ---------------------------------------------------------------------------


def test_signal_is_abortsignal():
    ctrl = AbortController()
    assert isinstance(ctrl.signal, AbortSignal)


# ---------------------------------------------------------------------------
# AC #9 covered by pytest --doctest-modules; also a guard test here
# ---------------------------------------------------------------------------


def test_aborted_flag_monotonic():
    """Signal can never revert from aborted=True to aborted=False."""
    ctrl = AbortController()
    ctrl.abort()
    # Directly call _do_abort with a reset attempt — still stays aborted
    ctrl.signal._do_abort(None)  # idempotent, no revert
    assert ctrl.signal.aborted is True


# ---------------------------------------------------------------------------
# repr sanity
# ---------------------------------------------------------------------------


def test_repr():
    ctrl = AbortController()
    assert repr(ctrl) == "AbortController(aborted=False)"
    assert repr(ctrl.signal) == "AbortSignal(aborted=False)"
    ctrl.abort()
    assert repr(ctrl) == "AbortController(aborted=True)"
    assert repr(ctrl.signal) == "AbortSignal(aborted=True)"


# ---------------------------------------------------------------------------
# abort with no reason — reason stays None
# ---------------------------------------------------------------------------


def test_abort_no_reason_reason_stays_none():
    ctrl = AbortController()
    ctrl.abort()
    assert ctrl.signal.reason is None


# ---------------------------------------------------------------------------
# abort with non-string reason
# ---------------------------------------------------------------------------


def test_abort_with_object_reason():
    ctrl = AbortController()
    exc = ValueError("cancelled")
    ctrl.abort(exc)
    assert ctrl.signal.reason is exc
