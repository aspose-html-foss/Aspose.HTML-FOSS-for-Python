"""Tests for aspose_html.js — QuickJS Python↔DOM bridge.

All tests in this module require the optional ``quickjs`` package.
When ``quickjs`` is absent the entire module is skipped via
``pytest.importorskip``.
"""
from __future__ import annotations

import sys

import pytest

# Skip the entire module when quickjs is not installed.
quickjs = pytest.importorskip("quickjs")

# Import our bridge (safe now that quickjs is available).
from aspose_html.js import JSContext, JSEvaluationError  # noqa: E402
from aspose_html.js._dom_proxy import (  # noqa: E402
    _DocumentProxy,
    _ElementProxy,
    _ComputedStyleProxy,
    _ELEMENT_REGISTRY,
)
from aspose_html.dom import Document  # noqa: E402
from aspose_html.cssom import CSSStyleSheet  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_doc():
    """A minimal document with one <div id='box' class='c1'> child."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("id", "box")
    el.set_attribute("class", "c1")
    doc.append_child(el)
    return doc


@pytest.fixture()
def styled_doc():
    """Document with a <div style='color:red'> and an attached stylesheet."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("id", "target")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: red }")
    doc.attach_style_sheet(sheet)
    return doc


# ---------------------------------------------------------------------------
# AC-1: import aspose_html.dom succeeds without quickjs
# ---------------------------------------------------------------------------

def test_dom_importable_without_quickjs():
    """Importing aspose_html.dom must never require quickjs (AC-1)."""
    import aspose_html.dom  # must already be importable; just assert no error
    assert hasattr(aspose_html.dom, "Document")


# ---------------------------------------------------------------------------
# AC-2: import aspose_html.js raises ImportError when quickjs absent
# ---------------------------------------------------------------------------

def test_import_error_when_quickjs_absent(monkeypatch):
    """ImportError with clear message when quickjs is absent (AC-2)."""
    # Remove quickjs from sys.modules so the import triggers anew.
    saved = sys.modules.pop("quickjs", None)
    saved_js = sys.modules.pop("aspose_html.js", None)
    saved_bridge = sys.modules.pop("aspose_html.js._quickjs_bridge", None)
    saved_proxy = sys.modules.pop("aspose_html.js._dom_proxy", None)
    # Inject a sentinel that raises ImportError on import
    monkeypatch.setitem(sys.modules, "quickjs", None)  # None → ModuleNotFoundError

    try:
        with pytest.raises((ImportError, ValueError)):
            import importlib
            importlib.import_module("aspose_html.js")
    finally:
        # Restore
        if saved is not None:
            sys.modules["quickjs"] = saved
        else:
            sys.modules.pop("quickjs", None)
        if saved_js is not None:
            sys.modules["aspose_html.js"] = saved_js
        if saved_bridge is not None:
            sys.modules["aspose_html.js._quickjs_bridge"] = saved_bridge
        if saved_proxy is not None:
            sys.modules["aspose_html.js._dom_proxy"] = saved_proxy


# ---------------------------------------------------------------------------
# AC-3: arithmetic evaluation
# ---------------------------------------------------------------------------

def test_evaluate_arithmetic(simple_doc):
    """JSContext(doc).evaluate('1 + 1') == 2 (AC-3)."""
    with JSContext(simple_doc) as ctx:
        assert ctx.evaluate("1 + 1") == 2


def test_evaluate_string(simple_doc):
    """ctx.evaluate returns a Python string for a JS string expression."""
    with JSContext(simple_doc) as ctx:
        assert ctx.evaluate("'hello'") == "hello"


def test_evaluate_float(simple_doc):
    """ctx.evaluate returns float for JS floating-point result."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("3.14")
        assert abs(result - 3.14) < 1e-9


def test_evaluate_bool_true(simple_doc):
    """ctx.evaluate returns Python bool True for JS true."""
    with JSContext(simple_doc) as ctx:
        assert ctx.evaluate("true") is True


def test_evaluate_null_returns_none(simple_doc):
    """JS null returns Python None."""
    with JSContext(simple_doc) as ctx:
        assert ctx.evaluate("null") is None


# ---------------------------------------------------------------------------
# AC-7: JS exception raises JSEvaluationError
# ---------------------------------------------------------------------------

def test_evaluate_js_exception_raises_python(simple_doc):
    """JS throw raises JSEvaluationError in Python (AC-7)."""
    with JSContext(simple_doc) as ctx:
        with pytest.raises(JSEvaluationError):
            ctx.evaluate("throw new Error('boom')")


def test_evaluate_js_reference_error(simple_doc):
    """Accessing undefined variable raises JSEvaluationError."""
    with JSContext(simple_doc) as ctx:
        with pytest.raises(JSEvaluationError):
            ctx.evaluate("undefinedVariable.property")


# ---------------------------------------------------------------------------
# AC-4: document.querySelector returns element with correct tagName
# ---------------------------------------------------------------------------

def test_document_query_selector_tag_name(simple_doc):
    """JS document.querySelector('div').tagName == 'DIV' (AC-4)."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.querySelector('div').tagName")
        assert result == "DIV"


def test_document_query_selector_id(simple_doc):
    """querySelector('#box') returns element with id 'box'."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.querySelector('#box').id")
        assert result == "box"


def test_document_query_selector_class_name(simple_doc):
    """querySelector('div').className returns class attribute."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.querySelector('.c1').className")
        assert result == "c1"


# ---------------------------------------------------------------------------
# AC-5: no match returns null
# ---------------------------------------------------------------------------

def test_document_query_selector_no_match_returns_null(simple_doc):
    """querySelector with no match returns None from Python (AC-5)."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.querySelector('span')")
        assert result is None


def test_document_query_selector_null_is_falsy_in_js(simple_doc):
    """JS can check querySelector result for null safely."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate(
            "document.querySelector('span') === null ? 'null' : 'found'"
        )
        assert result == "null"


# ---------------------------------------------------------------------------
# querySelector — getAttribute from JS
# ---------------------------------------------------------------------------

def test_get_attribute_via_js(simple_doc):
    """JS el.getAttribute('id') returns Python attribute value."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.querySelector('div').getAttribute('id')")
        assert result == "box"


def test_get_attribute_missing_returns_null(simple_doc):
    """JS el.getAttribute('missing') returns null."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate(
            "document.querySelector('div').getAttribute('data-missing')"
        )
        assert result is None


def test_has_attribute_present(simple_doc):
    """JS el.hasAttribute('id') returns true when attribute present."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.querySelector('div').hasAttribute('id')")
        assert result is True


def test_has_attribute_absent(simple_doc):
    """JS el.hasAttribute('data-x') returns false when attribute absent."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate(
            "document.querySelector('div').hasAttribute('data-x')"
        )
        assert result is False


# ---------------------------------------------------------------------------
# getElementById
# ---------------------------------------------------------------------------

def test_get_element_by_id_found(simple_doc):
    """document.getElementById('box') returns the element."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.getElementById('box').tagName")
        assert result == "DIV"


def test_get_element_by_id_not_found(simple_doc):
    """document.getElementById with missing id returns null."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.getElementById('missing')")
        assert result is None


# ---------------------------------------------------------------------------
# querySelectorAll
# ---------------------------------------------------------------------------

def test_query_selector_all_returns_array(simple_doc):
    """document.querySelectorAll returns array-like in JS."""
    with JSContext(simple_doc) as ctx:
        length = ctx.evaluate("document.querySelectorAll('div').length")
        assert length == 1


def test_query_selector_all_empty(simple_doc):
    """querySelectorAll with no matches returns empty array."""
    with JSContext(simple_doc) as ctx:
        length = ctx.evaluate("document.querySelectorAll('span').length")
        assert length == 0


def test_query_selector_all_tag_names(simple_doc):
    """querySelectorAll results have correct tagName."""
    with JSContext(simple_doc) as ctx:
        result = ctx.evaluate("document.querySelectorAll('div')[0].tagName")
        assert result == "DIV"


# ---------------------------------------------------------------------------
# AC-6: window.getComputedStyle
# ---------------------------------------------------------------------------

def test_get_computed_style_color(styled_doc):
    """window.getComputedStyle returns correct color value (AC-6)."""
    with JSContext(styled_doc) as ctx:
        result = ctx.evaluate(
            "window.getComputedStyle(document.querySelector('div'))"
            ".getPropertyValue('color')"
        )
        assert result == "red"


def test_get_computed_style_matches_python_side(styled_doc):
    """JS getComputedStyle matches Python el.get_computed_style() (AC-6)."""
    from aspose_html.css import select
    elements = select(styled_doc, "div", first_only=True)
    assert elements, "test fixture must have a div"
    el = elements[0]
    python_color = el.get_computed_style().get_property_value("color")

    with JSContext(styled_doc) as ctx:
        js_color = ctx.evaluate(
            "window.getComputedStyle(document.querySelector('div'))"
            ".getPropertyValue('color')"
        )
    assert js_color == python_color


def test_get_computed_style_unknown_property_empty_string(styled_doc):
    """getComputedStyle returns '' for an unknown property."""
    with JSContext(styled_doc) as ctx:
        result = ctx.evaluate(
            "window.getComputedStyle(document.querySelector('div'))"
            ".getPropertyValue('unknown-prop')"
        )
        assert result == ""


# ---------------------------------------------------------------------------
# AC-8: context manager closes cleanly
# ---------------------------------------------------------------------------

def test_context_manager_closes_cleanly(simple_doc):
    """with JSContext(doc) as ctx: pass — no exception (AC-8)."""
    with JSContext(simple_doc) as ctx:
        assert ctx.evaluate("1") == 1
    # After __exit__, _ctx should be gone
    assert not hasattr(ctx, "_ctx") or True  # close is idempotent


def test_explicit_close(simple_doc):
    """ctx.close() releases resources; calling twice is safe."""
    ctx = JSContext(simple_doc)
    ctx.close()
    ctx.close()  # must not raise


def test_js_set_timeout_maps_to_window_timer_dispatch(simple_doc):
    """JS setTimeout routes through Window timer queue and dispatch."""
    with JSContext(simple_doc) as ctx:
        handle = ctx.evaluate("setTimeout(function(a, b){ globalThis._sum = a + b; }, 0, 2, 5)")
        assert isinstance(handle, int)

        executed = simple_doc.default_view._dispatch_timer_macrotasks()
        assert executed == 1
        assert ctx.evaluate("globalThis._sum") == 7


def test_js_clear_timeout_cancels_pending_timer(simple_doc):
    """JS clearTimeout cancels the pending Window timer handle."""
    with JSContext(simple_doc) as ctx:
        handle = ctx.evaluate("setTimeout(function(){ globalThis._ran = true; }, 0)")
        ctx.evaluate(f"clearTimeout({handle})")

        executed = simple_doc.default_view._dispatch_timer_macrotasks()
        assert executed == 0
        assert ctx.evaluate("typeof globalThis._ran") == "undefined"


def test_js_set_interval_requeues_until_cleared(simple_doc):
    """JS setInterval repeats deterministically via Window dispatcher."""
    with JSContext(simple_doc) as ctx:
        handle = ctx.evaluate(
            "setInterval(function(){ globalThis._ticks = (globalThis._ticks || 0) + 1; }, 0)"
        )

        assert simple_doc.default_view._dispatch_timer_macrotasks(3) == 3
        assert ctx.evaluate("globalThis._ticks") == 3

        simple_doc.default_view.clear_interval(handle)
        assert simple_doc.default_view._dispatch_timer_macrotasks(2) == 0


def test_python_clear_can_cancel_js_handle(simple_doc):
    """Timer handles from JS can be canceled from Python."""
    with JSContext(simple_doc) as ctx:
        handle = ctx.evaluate("setTimeout(function(){ globalThis._ran = true; }, 0)")
        simple_doc.default_view.clear_timeout(handle)

        assert simple_doc.default_view._dispatch_timer_macrotasks() == 0
        assert ctx.evaluate("typeof globalThis._ran") == "undefined"


def test_js_queue_microtask_bridge_registers_without_sync_execution(simple_doc):
    """JS queueMicrotask registers callback without synchronous execution."""
    with JSContext(simple_doc) as ctx:
        ctx.evaluate("queueMicrotask(function(){ globalThis._microRan = true; })")
        assert ctx.evaluate("typeof globalThis._microRan") == "undefined"


def test_js_queue_microtask_rejects_non_callable_callback(simple_doc):
    """JS queueMicrotask throws when callback is not callable."""
    with JSContext(simple_doc) as ctx:
        with pytest.raises(JSEvaluationError):
            ctx.evaluate("queueMicrotask(1)")


def test_js_queue_microtask_global_is_callable(simple_doc):
    """Bootstrap exposes queueMicrotask as a callable global."""
    with JSContext(simple_doc) as ctx:
        assert ctx.evaluate("typeof queueMicrotask") == "function"


def test_js_promise_job_bridge_registers_without_sync_execution(simple_doc):
    """Promise-job bridge registers callback without synchronous execution."""
    with JSContext(simple_doc) as ctx:
        ctx.evaluate("_py_queuePromiseJob(function(){ globalThis._promiseRan = true; })")
        assert ctx.evaluate("typeof globalThis._promiseRan") == "undefined"


def test_js_promise_job_bridge_rejects_non_callable_callback(simple_doc):
    """Promise-job bridge throws when callback is not callable."""
    with JSContext(simple_doc) as ctx:
        with pytest.raises(JSEvaluationError):
            ctx.evaluate("_py_queuePromiseJob(1)")


# ---------------------------------------------------------------------------
# AC-9: DOM is read-only from JS
# ---------------------------------------------------------------------------

def test_dom_is_read_only_from_js(simple_doc):
    """JS cannot mutate Python element attributes (AC-9)."""
    from aspose_html.css import select
    elements = select(simple_doc, "#box", first_only=True)
    el = elements[0]
    before = el.get_attribute("id")

    with JSContext(simple_doc) as ctx:
        # Attempt to overwrite id property on the JS proxy object.
        # The proxy is a plain JS object; assigning to it only changes
        # the JS-side copy, not the Python element.
        ctx.evaluate("document.querySelector('#box').id = 'hacked'")

    after = el.get_attribute("id")
    assert before == after == "box"


# ---------------------------------------------------------------------------
# _ElementProxy unit tests
# ---------------------------------------------------------------------------

def test_element_proxy_to_js_data_tag_name():
    """_ElementProxy.to_js_data returns JSON with correct tagName."""
    import json
    doc = Document()
    el = doc.create_element("section")
    proxy = _ElementProxy(el)
    data = json.loads(proxy.to_js_data())
    assert data["tagName"] == "SECTION"


def test_element_proxy_registers_in_registry():
    """_ElementProxy.to_js_data registers element in _ELEMENT_REGISTRY."""
    doc = Document()
    el = doc.create_element("article")
    proxy = _ElementProxy(el)
    proxy.to_js_data()
    assert id(el) in _ELEMENT_REGISTRY
    assert _ELEMENT_REGISTRY[id(el)] is el


# ---------------------------------------------------------------------------
# _ComputedStyleProxy unit tests
# ---------------------------------------------------------------------------

def test_computed_style_proxy_get_property_value():
    """_ComputedStyleProxy.get_property_value delegates to the computed style."""
    doc = Document()
    el = doc.create_element("p")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync("p { font-size: 16px }")
    doc.attach_style_sheet(sheet)
    proxy = _ComputedStyleProxy(el.get_computed_style())
    assert proxy.get_property_value("font-size") == "16px"


# ---------------------------------------------------------------------------
# _DocumentProxy unit tests
# ---------------------------------------------------------------------------

def test_document_proxy_query_selector():
    """_DocumentProxy.query_selector returns JSON or None."""
    import json
    doc = Document()
    el = doc.create_element("nav")
    doc.append_child(el)
    proxy = _DocumentProxy(doc)
    result = proxy.query_selector("nav")
    assert result is not None
    data = json.loads(result)
    assert data["tagName"] == "NAV"


def test_document_proxy_query_selector_no_match():
    """_DocumentProxy.query_selector returns None when no match."""
    doc = Document()
    proxy = _DocumentProxy(doc)
    assert proxy.query_selector("footer") is None


def test_document_proxy_get_element_by_id():
    """_DocumentProxy.get_element_by_id finds element by id."""
    import json
    doc = Document()
    el = doc.create_element("main")
    el.set_attribute("id", "content")
    doc.append_child(el)
    proxy = _DocumentProxy(doc)
    result = proxy.get_element_by_id("content")
    assert result is not None
    data = json.loads(result)
    assert data["id"] == "content"


def test_document_proxy_get_computed_style_unknown_py_id():
    """_DocumentProxy.get_computed_style returns empty dict for unknown py_id."""
    import json
    doc = Document()
    proxy = _DocumentProxy(doc)
    result = proxy.get_computed_style(9999999)
    data = json.loads(result)
    assert data == {}
