"""QuickJS bridge — JSContext implementation.

Wraps a ``quickjs.Context`` with a Python DOM-aware global environment.
Python callbacks are injected as JS global functions via
``quickjs.Context.add_callable``; the ``document``, ``window``, and
``console`` objects are constructed in JS via a bootstrap ``eval`` call
that wires those callbacks into WHATWG-shaped objects.

DOM access through the bridge is primarily **read-only**; the sole
write-through is ``el.setAttribute(name, value)``, which routes to
``_py_setAttribute`` and mutates the Python DOM.  All other writes
are silently discarded.

Note: the DOM node classes use ``__slots__`` without ``__weakref__``, so
strong references to the document are held for the lifetime of the
JSContext.  Callers should close the context promptly to release the
reference.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import quickjs

from ._dom_proxy import _DocumentProxy

if TYPE_CHECKING:
    from aspose_html.dom._document import Document


# ---------------------------------------------------------------------------
# Public exception
# ---------------------------------------------------------------------------

class JSEvaluationError(Exception):
    """Raised when a JavaScript expression throws an exception.

    Wraps :class:`quickjs.JSException` so that callers do not need to
    import ``quickjs`` to handle JS errors.

    Examples
    --------
    >>> from aspose_html.dom import Document  # doctest: +SKIP
    >>> from aspose_html.js import JSContext, JSEvaluationError  # doctest: +SKIP
    >>> doc = Document()  # doctest: +SKIP
    >>> with JSContext(doc) as ctx:  # doctest: +SKIP
    ...     ctx.evaluate("throw new Error('boom')")  # doctest: +SKIP
    Traceback (most recent call last):
        ...
    JSEvaluationError: Error: boom
    """


# ---------------------------------------------------------------------------
# JS bootstrap template
# ---------------------------------------------------------------------------

# This JS snippet is eval'd once to construct the document / window objects
# from the Python callbacks registered via add_callable.  Every Python
# callback is named with a ``_py_`` prefix and handles one operation.
# The JS side does JSON.parse / JSON.stringify as needed for complex values.
_BOOTSTRAP_JS = """
// Check whether Proxy is available (QuickJS >=2020.01).
// If the Proxy constructor is available we use it; otherwise fall back to a
// frozen empty object so that property access returns undefined (never throws).
var _makeStyleStub = (function() {
    try {
        var _p = new Proxy({}, {
            get: function(t, p) { return typeof p === 'string' ? '' : undefined; },
            set: function(t, p, v) { return true; }
        });
        return function() { return _p; };
    } catch (e) {
        var _frozen = Object.freeze({});
        return function() { return _frozen; };
    }
})();

function _makeElement(jsonStr) {
    if (jsonStr === null || jsonStr === undefined) return null;
    var d = JSON.parse(jsonStr);
    var pyId = d.__py_id__;
    return {
        tagName:     d.tagName,
        id:          d.id,
        className:   d.className,
        textContent: d.textContent,
        __py_id__:   pyId,
        getAttribute: function(name) {
            return _py_getAttribute(pyId, name);
        },
        hasAttribute: function(name) {
            return _py_hasAttribute(pyId, name);
        },
        setAttribute: function(name, value) {
            _py_setAttribute(pyId, name, value);
        },
        // Event API stubs — no-ops; bridge is headless (no event loop)
        addEventListener:    function(type, listener, options) {},
        removeEventListener: function(type, listener, options) {},
        dispatchEvent:       function(event) { return false; },
        // Minimal style stub — prevents TypeError on el.style.prop access
        style: _makeStyleStub()
    };
}

function _makeElementList(jsonStr) {
    var arr = JSON.parse(jsonStr);
    return arr.map(function(d) {
        return _makeElement(JSON.stringify(d));
    });
}

function _makeComputedStyle(jsonStr) {
    var d = JSON.parse(jsonStr);
    return {
        getPropertyValue: function(name) {
            return d[name] || "";
        }
    };
}

var document = {
    querySelector: function(sel) {
        return _makeElement(_py_querySelector(sel));
    },
    querySelectorAll: function(sel) {
        return _makeElementList(_py_querySelectorAll(sel));
    },
    getElementById: function(id) {
        return _makeElement(_py_getElementById(id));
    },
    getElementsByTagName: function(tag) {
        return _makeElementList(_py_getElementsByTagName(tag));
    },
    // Event API stubs
    addEventListener:    function(type, listener, options) {},
    removeEventListener: function(type, listener, options) {},
    dispatchEvent:       function(event) { return false; }
};

var window = {
    getComputedStyle: function(el, pseudo) {
        var pyId = el ? el.__py_id__ : null;
        return _makeComputedStyle(_py_getComputedStyle(pyId, pseudo || null));
    },
    setTimeout: function(callback, delay) {
        var args = Array.prototype.slice.call(arguments, 2);
        return _py_setTimeout(callback, delay || 0, JSON.stringify(args));
    },
    setInterval: function(callback, delay) {
        var args = Array.prototype.slice.call(arguments, 2);
        return _py_setInterval(callback, delay || 0, JSON.stringify(args));
    },
    clearTimeout: function(handle) {
        _py_clearTimeout(handle);
    },
    clearInterval: function(handle) {
        _py_clearInterval(handle);
    },
    // Event API stubs
    addEventListener:    function(type, listener, options) {},
    removeEventListener: function(type, listener, options) {},
    dispatchEvent:       function(event) { return false; }
};

// Expose browser-style timer globals that route to Window timer semantics.
var setTimeout = window.setTimeout;
var setInterval = window.setInterval;
var clearTimeout = window.clearTimeout;
var clearInterval = window.clearInterval;
var queueMicrotask = function(callback) {
    return _py_queueMicrotask(callback);
};

var console = {
    log: function() {}
};

// Dynamic import() stub — raises in headless script context.
// Note: QuickJS may handle import() as syntax (not a callable), so this
// defineProperty override may not intercept all dynamic import calls.
// Module-mode evaluation (eval_module) uses QuickJS's own module resolution.
// Callers should use JSContext.register_module + eval_module instead of import().
try {
    Object.defineProperty(globalThis, 'import', {
        value: function(specifier) {
            throw new TypeError(
                "Dynamic import() is not supported in headless context: " + specifier
            );
        },
        writable: false,
        configurable: false
    });
} catch (_importStubErr) {
    // Silently ignore: QuickJS may not allow redefining import on globalThis
}
"""


# ---------------------------------------------------------------------------
# JSContext
# ---------------------------------------------------------------------------

class JSContext:
    """A JavaScript execution context backed by QuickJS, pre-wired to a DOM.

    Creates a ``quickjs.Context`` and injects read-only DOM proxy callbacks
    so that JS code can call ``document.querySelector``,
    ``window.getComputedStyle``, and read element properties.

    The context is a Python *context manager* — use ``with JSContext(doc) as
    ctx:`` to guarantee cleanup of QuickJS runtime resources on exit.

    Parameters
    ----------
    document : Document
        The Python DOM document this context is wired to.

    Examples
    --------
    All examples require the optional ``quickjs`` package:

    >>> from aspose_html.dom import Document  # doctest: +SKIP
    >>> from aspose_html.js import JSContext   # doctest: +SKIP
    >>> doc = Document()  # doctest: +SKIP
    >>> el = doc.create_element("div")  # doctest: +SKIP
    >>> doc.append_child(el)  # doctest: +SKIP
    <Element 'DIV'>
    >>> with JSContext(doc) as ctx:  # doctest: +SKIP
    ...     ctx.evaluate("1 + 1")
    2
    """

    __slots__ = ("_ctx", "_doc", "_proxy", "_module_registry")

    def __init__(self, document: "Document") -> None:
        # Strong reference — DOM classes use __slots__ without __weakref__
        self._doc: "Document" = document
        self._proxy: _DocumentProxy = _DocumentProxy(document)
        from ._module_loader import ModuleRegistry
        self._module_registry: "ModuleRegistry" = ModuleRegistry()
        self._ctx: quickjs.Context = quickjs.Context()
        self._install_globals()

    # ------------------------------------------------------------------
    # Internal setup
    # ------------------------------------------------------------------

    def _install_globals(self) -> None:
        """Register Python callbacks and bootstrap JS globals."""
        ctx = self._ctx
        proxy = self._proxy

        # Register Python-backed callbacks as JS globals
        ctx.add_callable("_py_querySelector", proxy.query_selector)
        ctx.add_callable("_py_querySelectorAll", proxy.query_selector_all)
        ctx.add_callable("_py_getElementById", proxy.get_element_by_id)
        ctx.add_callable("_py_getElementsByTagName", proxy.get_elements_by_tag_name)
        ctx.add_callable("_py_getAttribute", proxy.get_attribute)
        ctx.add_callable("_py_hasAttribute", proxy.has_attribute)
        ctx.add_callable("_py_getComputedStyle", proxy.get_computed_style)
        ctx.add_callable("_py_setAttribute", proxy.set_attribute)
        ctx.add_callable("_py_setTimeout", self._py_set_timeout)
        ctx.add_callable("_py_setInterval", self._py_set_interval)
        ctx.add_callable("_py_clearTimeout", self._py_clear_timeout)
        ctx.add_callable("_py_clearInterval", self._py_clear_interval)
        ctx.add_callable("_py_queueMicrotask", self._py_queue_microtask)
        ctx.add_callable("_py_queuePromiseJob", self._py_queue_promise_job)

        # Register optional module-loader hook when the QuickJS binding supports it
        if hasattr(ctx, "set_module_loader"):
            ctx.set_module_loader(self._resolve_module)

        # Bootstrap JS objects from the registered callbacks
        try:
            ctx.eval(_BOOTSTRAP_JS)
        except quickjs.JSException as exc:  # pragma: no cover
            raise RuntimeError(f"JSContext bootstrap failed: {exc}") from exc

    def _coerce_timer_callback(self, callback: object) -> "Callable[..., object]":
        if not callable(callback):
            raise TypeError("setTimeout/setInterval callback must be callable")
        return callback

    def _decode_timer_args(self, args_json: str | None) -> tuple[object, ...]:
        import json

        if not args_json:
            return ()
        decoded = json.loads(args_json)
        if not isinstance(decoded, list):
            return ()
        return tuple(decoded)

    def _coerce_microtask_callback(self, callback: object) -> "Callable[[], None]":
        if not callable(callback):
            raise TypeError("queueMicrotask callback must be callable")
        return callback

    def _py_set_timeout(self, callback: object, delay: object = 0, args_json: str | None = None) -> int:
        cb = self._coerce_timer_callback(callback)
        args = self._decode_timer_args(args_json)
        delay_ms = int(delay) if delay is not None else 0
        return self._doc.default_view.set_timeout(cb, delay_ms, *args)

    def _py_set_interval(self, callback: object, delay: object = 0, args_json: str | None = None) -> int:
        cb = self._coerce_timer_callback(callback)
        args = self._decode_timer_args(args_json)
        delay_ms = int(delay) if delay is not None else 0
        return self._doc.default_view.set_interval(cb, delay_ms, *args)

    def _py_clear_timeout(self, handle: object | None = None) -> None:
        self._doc.default_view.clear_timeout(int(handle) if handle is not None else None)

    def _py_clear_interval(self, handle: object | None = None) -> None:
        self._doc.default_view.clear_interval(int(handle) if handle is not None else None)

    def _py_queue_microtask(self, callback: object) -> None:
        cb = self._coerce_microtask_callback(callback)
        self._doc.default_view.queue_microtask(cb)

    def _py_queue_promise_job(self, callback: object) -> None:
        """Queue a QuickJS Promise-job callback on the Window checkpoint seam."""
        cb = self._coerce_microtask_callback(callback)
        self._doc.default_view._schedule_microtask_checkpoint(cb, token=None)

    def _resolve_module(self, specifier: str) -> str:
        """Called by QuickJS when it needs to load a module by specifier.

        Returns the registered source string or raises
        :class:`~aspose_html.js._module_loader.ModuleNotFoundError` when the
        specifier is not found in the registry.  QuickJS converts the Python
        exception to a JS module-load error visible to JS code.
        """
        source = self._module_registry.resolve(specifier)
        if source is None:
            from ._module_loader import ModuleNotFoundError
            raise ModuleNotFoundError(specifier)
        return source

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def register_module(self, specifier: str, source: str) -> None:
        """Register an ES module source string under *specifier*.

        After registration, JS code evaluated via :meth:`eval_module` can
        import this module using an ``import`` statement that matches the
        registered specifier string.

        Parameters
        ----------
        specifier : str
            The module specifier string as it appears in JS ``import``
            statements (e.g. ``"./utils.js"`` or ``"lodash"``).
        source : str
            The ES module source code.

        Returns
        -------
        None

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> from aspose_html.js import JSContext  # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> with JSContext(doc) as ctx:  # doctest: +SKIP
        ...     ctx.register_module("./math.js", "export const add = (a, b) => a + b;")
        """
        self._module_registry.register(specifier, source)

    def eval_module(self, source: str, *, module_name: str = "<inline>") -> Any:
        """Evaluate *source* as an ES module in the QuickJS context.

        Attempts to use the QuickJS native module-evaluation path
        (``context.eval_module``) when available.  Falls back to script
        evaluation with a runtime warning when the native path is absent —
        in fallback mode, top-level ``export`` and static ``import``
        statements are not supported and the return value is always ``None``.

        Parameters
        ----------
        source : str
            An ES module source string.  In native mode this may contain
            ``import``/``export`` statements.  In fallback mode, module
            syntax raises :class:`JSEvaluationError`.
        module_name : str, optional
            A name for the module used in error messages.  Defaults to
            ``"<inline>"``.

        Returns
        -------
        Any
            The module's default export when the native QuickJS module API
            returns a value; ``None`` in fallback mode or when there is no
            default export.

        Raises
        ------
        JSEvaluationError
            If the JavaScript source throws an exception or contains
            syntax errors.

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> from aspose_html.js import JSContext  # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> with JSContext(doc) as ctx:  # doctest: +SKIP
        ...     ctx.eval_module("const x = 1;")
        """
        try:
            if hasattr(self._ctx, "eval_module"):
                return self._ctx.eval_module(source, module_name)
            else:
                import warnings
                warnings.warn(
                    "quickjs does not expose eval_module(); falling back to"
                    " script evaluation. Module syntax (import/export) is not"
                    " supported in fallback mode.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                return self._ctx.eval(source)
        except quickjs.JSException as exc:
            raise JSEvaluationError(str(exc)) from exc

    def import_stub(self, specifier: str) -> None:
        """Unconditionally raise ``NotImplementedError`` for dynamic ``import()``.

        Dynamic ``import()`` is a JS syntax construct that cannot be safely
        dispatched to Python handlers in the headless QuickJS context.  Use
        :meth:`register_module` to register a module source string and
        :meth:`eval_module` to evaluate it.

        Parameters
        ----------
        specifier : str
            The module specifier string that was requested.

        Raises
        ------
        NotImplementedError
            Always.

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> from aspose_html.js import JSContext  # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> with JSContext(doc) as ctx:  # doctest: +SKIP
        ...     ctx.import_stub("./math.js")
        Traceback (most recent call last):
            ...
        NotImplementedError: Dynamic import() is not supported in headless mode; use JSContext.register_module + eval_module
        """
        raise NotImplementedError(
            "Dynamic import() is not supported in headless mode; "
            "use JSContext.register_module + eval_module"
        )

    def evaluate(self, js_source: str) -> Any:
        """Evaluate *js_source* in the QuickJS context.

        Parameters
        ----------
        js_source : str
            A JavaScript expression or statement string.

        Returns
        -------
        Any
            The Python equivalent of the JS return value.  Primitive
            types (``str``, ``int``, ``float``, ``bool``, ``None``) are
            returned directly.  JS ``null`` / ``undefined`` return
            ``None``.

        Raises
        ------
        JSEvaluationError
            If the JavaScript expression throws an exception.

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> from aspose_html.js import JSContext   # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> with JSContext(doc) as ctx:  # doctest: +SKIP
        ...     ctx.evaluate("1 + 1")
        2
        """
        try:
            return self._ctx.eval(js_source)
        except quickjs.JSException as exc:
            raise JSEvaluationError(str(exc)) from exc

    def close(self) -> None:
        """Release the QuickJS runtime resources.

        Safe to call multiple times.

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> from aspose_html.js import JSContext   # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> ctx = JSContext(doc)  # doctest: +SKIP
        >>> ctx.close()  # doctest: +SKIP
        """
        if hasattr(self, "_ctx"):
            del self._ctx

    def __enter__(self) -> "JSContext":
        """Return *self* for use as a context manager.

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> from aspose_html.js import JSContext   # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> with JSContext(doc) as ctx:  # doctest: +SKIP
        ...     ctx.evaluate("'hello'")
        'hello'
        """
        return self

    def __exit__(self, *args: object) -> None:
        """Close the context when exiting the ``with`` block."""
        self.close()
