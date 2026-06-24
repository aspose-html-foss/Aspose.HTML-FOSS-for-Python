"""Tests for JSContext module-loading methods ( / ).

All tests that require a live QuickJS context are gated with
``pytest.importorskip("quickjs")``.

The package-export test (``test_module_registry_exported_from_package``)
validates that ModuleRegistry and ModuleNotFoundError appear in __all__ and
can be imported; since aspose_html.js.__init__ itself requires quickjs, this
test is also gated.
"""
from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Module-level gate — skip entire file when quickjs is absent.
# ---------------------------------------------------------------------------
quickjs = pytest.importorskip("quickjs")

from aspose_html.dom import Document  # noqa: E402
from aspose_html.js import JSContext, JSEvaluationError  # noqa: E402
from aspose_html.js._module_loader import ModuleNotFoundError  # noqa: E402


# ---------------------------------------------------------------------------
# Package-export test
# ---------------------------------------------------------------------------

def test_module_registry_exported_from_package() -> None:
    """ModuleRegistry and ModuleNotFoundError are importable from aspose_html.js."""
    from aspose_html.js import ModuleRegistry, ModuleNotFoundError as MNFError  # noqa: F401

    assert ModuleRegistry is not None
    assert MNFError is not None
    # Both names must appear in __all__
    import aspose_html.js as js_pkg
    assert "ModuleRegistry" in js_pkg.__all__
    assert "ModuleNotFoundError" in js_pkg.__all__


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def doc() -> Document:
    return Document()


@pytest.fixture()
def ctx(doc: Document):
    with JSContext(doc) as c:
        yield c


# ---------------------------------------------------------------------------
# register_module
# ---------------------------------------------------------------------------

def test_register_module_stores_in_registry(ctx: JSContext) -> None:
    """register_module stores the source in the internal ModuleRegistry."""
    ctx.register_module("./math.js", "export const add = (a, b) => a + b;")
    # The module should be resolvable from the internal registry
    assert "./math.js" in ctx._module_registry
    assert ctx._module_registry.resolve("./math.js") == "export const add = (a, b) => a + b;"


# ---------------------------------------------------------------------------
# eval_module — unknown specifier raises
# ---------------------------------------------------------------------------

def test_eval_module_unknown_raises_module_load_error(ctx: JSContext) -> None:
    """eval_module raises when an import refers to a non-registered specifier.

    When the native eval_module + set_module_loader path is available,
    the ModuleNotFoundError from the registry propagates.  When the fallback
    script-eval path is used, any import syntax raises JSEvaluationError.
    Either way, a non-registered import must not silently succeed.
    """
    if hasattr(quickjs.Context(), "eval_module"):
        # Native path present — any exception is acceptable
        with pytest.raises(Exception):
            ctx.eval_module('import "./nonexistent.js";')
    else:
        # Fallback path: import syntax is a JS syntax error
        with pytest.raises(JSEvaluationError):
            ctx.eval_module('import "./nonexistent.js";')


# ---------------------------------------------------------------------------
# import_stub
# ---------------------------------------------------------------------------

def test_import_stub_raises_not_implemented(ctx: JSContext) -> None:
    """import_stub always raises NotImplementedError with the headless message."""
    with pytest.raises(NotImplementedError) as exc_info:
        ctx.import_stub("./anything.js")

    msg = str(exc_info.value)
    assert "Dynamic import() is not supported in headless mode" in msg
    assert "register_module" in msg
    assert "eval_module" in msg
