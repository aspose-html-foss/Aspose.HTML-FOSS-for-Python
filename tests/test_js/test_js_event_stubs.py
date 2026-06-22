"""Tests for JS bridge event stubs and setAttribute write-through.

ADR-145, BACK-162: verifies that addEventListener / removeEventListener /
dispatchEvent are callable no-ops on elements, document, and window; that
el.setAttribute writes through to the Python DOM; and that el.style does not
throw on property access or assignment.

All tests in this module require the optional ``quickjs`` package.
When ``quickjs`` is absent the entire module is skipped via
``pytest.importorskip``.
"""
from __future__ import annotations

import pytest

# Skip the entire module when quickjs is not installed.
quickjs = pytest.importorskip("quickjs")

from aspose_html.js import JSContext, JSEvaluationError  # noqa: E402
from aspose_html.dom import Document  # noqa: E402
from aspose_html.cssom import CSSStyleSheet  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def doc_with_div():
    """Minimal document with one <div id='box'> child."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("id", "box")
    doc.append_child(el)
    return doc


@pytest.fixture()
def doc_with_style():
    """Document with a <div> and an attached stylesheet."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("id", "target")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: blue }")
    doc.attach_style_sheet(sheet)
    return doc


# ---------------------------------------------------------------------------
# AC-1: el.addEventListener does not throw
# ---------------------------------------------------------------------------

def test_element_add_event_listener_no_throw(doc_with_div):
    """JS el.addEventListener('click', fn) does not throw (AC-1)."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "document.querySelector('div').addEventListener('click', function(){})"
        )
    # addEventListener returns undefined → Python None
    assert result is None


# ---------------------------------------------------------------------------
# el.removeEventListener does not throw
# ---------------------------------------------------------------------------

def test_element_remove_event_listener_no_throw(doc_with_div):
    """JS el.removeEventListener('click', fn) does not throw."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "document.querySelector('div').removeEventListener('click', function(){})"
        )
    assert result is None


# ---------------------------------------------------------------------------
# AC-2: el.dispatchEvent returns false without throwing
# ---------------------------------------------------------------------------

def test_element_dispatch_event_returns_false(doc_with_div):
    """JS el.dispatchEvent({type:'click'}) returns false without throwing (AC-2)."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "document.querySelector('div').dispatchEvent({type: 'click'})"
        )
    assert result is False


# ---------------------------------------------------------------------------
# AC-3: document.addEventListener does not throw
# ---------------------------------------------------------------------------

def test_document_add_event_listener_no_throw(doc_with_div):
    """JS document.addEventListener('DOMContentLoaded', fn) does not throw (AC-3)."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "document.addEventListener('DOMContentLoaded', function(){})"
        )
    assert result is None


def test_document_remove_event_listener_no_throw(doc_with_div):
    """JS document.removeEventListener does not throw."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "document.removeEventListener('DOMContentLoaded', function(){})"
        )
    assert result is None


def test_document_dispatch_event_returns_false(doc_with_div):
    """JS document.dispatchEvent returns false without throwing."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate("document.dispatchEvent({type: 'load'})")
    assert result is False


# ---------------------------------------------------------------------------
# AC-4: window.addEventListener does not throw
# ---------------------------------------------------------------------------

def test_window_add_event_listener_no_throw(doc_with_div):
    """JS window.addEventListener('load', fn) does not throw (AC-4)."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "window.addEventListener('load', function(){})"
        )
    assert result is None


def test_window_dispatch_event_returns_false(doc_with_div):
    """JS window.dispatchEvent returns false without throwing."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate("window.dispatchEvent({type: 'load'})")
    assert result is False


# ---------------------------------------------------------------------------
# AC-5: el.setAttribute mutates Python DOM
# ---------------------------------------------------------------------------

def test_set_attribute_mutates_python_dom(doc_with_div):
    """JS el.setAttribute('class', 'active') is visible via Python get_attribute (AC-5)."""
    from aspose_html.css import select
    elements = select(doc_with_div, "div", first_only=True)
    assert elements, "fixture must have a div"
    el = elements[0]

    with JSContext(doc_with_div) as ctx:
        ctx.evaluate("document.querySelector('div').setAttribute('class', 'active')")

    assert el.get_attribute("class") == "active"


# ---------------------------------------------------------------------------
# AC-6: el.setAttribute('style', ...) is visible to Python cascade
# ---------------------------------------------------------------------------

def test_set_attribute_style_mutates_style_attribute(doc_with_div):
    """JS setAttribute('style', 'color: green') is visible via Python get_attribute (AC-6)."""
    from aspose_html.css import select
    elements = select(doc_with_div, "div", first_only=True)
    assert elements, "fixture must have a div"
    el = elements[0]

    with JSContext(doc_with_div) as ctx:
        ctx.evaluate(
            "document.querySelector('div').setAttribute('style', 'color: green')"
        )

    assert el.get_attribute("style") == "color: green"


# ---------------------------------------------------------------------------
# getAttribute reflects setAttribute within the same JS session
# ---------------------------------------------------------------------------

def test_get_attribute_reflects_set_attribute(doc_with_div):
    """JS getAttribute reflects a prior setAttribute call in the same evaluate."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "(function(){"
            "  var el = document.querySelector('div');"
            "  el.setAttribute('data-x', '1');"
            "  return el.getAttribute('data-x');"
            "})()"
        )
    assert result == "1"


# ---------------------------------------------------------------------------
# AC-7: el.style.color access does not throw
# ---------------------------------------------------------------------------

def test_style_access_no_throw(doc_with_div):
    """JS el.style.color access does not throw; returns '' or None (AC-7)."""
    with JSContext(doc_with_div) as ctx:
        # Must not raise JSEvaluationError
        result = ctx.evaluate("document.querySelector('div').style.color")
    # Result is '' (Proxy) or None (undefined from frozen object)
    assert result in ("", None)


# ---------------------------------------------------------------------------
# AC-8: el.style.color = 'red' does not throw and does NOT mutate Python DOM
# ---------------------------------------------------------------------------

def test_style_assignment_no_throw_no_mutation(doc_with_div):
    """JS el.style.color = 'red' does not throw and does not mutate Python DOM (AC-8)."""
    from aspose_html.css import select
    elements = select(doc_with_div, "div", first_only=True)
    assert elements, "fixture must have a div"
    el = elements[0]
    before = el.get_attribute("style")

    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "document.querySelector('div').style.color = 'red'"
        )

    # style attribute on Python element must be unchanged
    assert el.get_attribute("style") == before
    # The assignment itself should not raise; result is 'red' (JS assignment expression)
    assert result == "red"


# ---------------------------------------------------------------------------
# AC-5: setAttribute with invalid (empty) name does not crash
# ---------------------------------------------------------------------------

def test_set_attribute_invalid_name_no_crash(doc_with_div):
    """JS el.setAttribute('', 'x') does not crash (empty name is silently ignored)."""
    with JSContext(doc_with_div) as ctx:
        # Must not raise JSEvaluationError
        result = ctx.evaluate(
            "document.querySelector('div').setAttribute('', 'x')"
        )
    assert result is None


# ---------------------------------------------------------------------------
# Chained: query + addEventListener + getAttribute in one evaluate call
# ---------------------------------------------------------------------------

def test_chained_event_and_query(doc_with_div):
    """Chained JS: querySelector + addEventListener + getAttribute — no error."""
    with JSContext(doc_with_div) as ctx:
        result = ctx.evaluate(
            "(function(){"
            "  var el = document.querySelector('div');"
            "  el.addEventListener('click', function(){});"
            "  return el.getAttribute('id');"
            "})()"
        )
    assert result == "box"
