"""aspose_html.js — QuickJS JavaScript execution layer.

Optional dependency: requires the ``quickjs`` PyPI package (~1.19.x).
Install it with::

    pip install quickjs

This subpackage is **not** imported by any other ``aspose_html`` module.
Import it explicitly when you need JS execution::

    from aspose_html.js import JSContext, JSEvaluationError

Public API:

:class:`JSContext`
    Context manager wrapping a QuickJS runtime pre-wired to a Python DOM.

:class:`JSEvaluationError`
    Raised when JS evaluation throws an exception; wraps
    ``quickjs.JSException`` so callers do not need ``quickjs`` to handle
    errors.

Examples
--------
All examples require the optional ``quickjs`` package:

>>> from aspose_html import HTMLDocument  # doctest: +SKIP
>>> from aspose_html.js import JSContext  # doctest: +SKIP
>>> doc = HTMLDocument.parse('<div id="x" style="color:red">hi</div>')  # doctest: +SKIP
>>> with JSContext(doc) as ctx:  # doctest: +SKIP
...     result = ctx.evaluate("document.querySelector('#x').tagName")
...     print(result)
DIV
"""
try:
    import quickjs as _quickjs  # noqa: F401
except ImportError as exc:
    raise ImportError(
        "aspose_html.js requires the 'quickjs' package. "
        "Install it with: pip install quickjs"
    ) from exc

from ._quickjs_bridge import JSContext, JSEvaluationError  # noqa: E402
from ._module_loader import ModuleRegistry, ModuleNotFoundError  # noqa: E402

__all__ = ["JSContext", "JSEvaluationError", "ModuleRegistry", "ModuleNotFoundError"]
