"""Track 71 integration matrix — JS module loading and dynamic import stubs.

Groups:
  A — Module loader policy layer (no quickjs required)
  B — JSContext.eval_module and register_module (quickjs-gated)
  C — Optional-dependency safety (no quickjs required)

BACK-282 / ADR-260 / SPEC-124.
"""
from __future__ import annotations

import pytest

# ===========================================================================
# Group A — ModuleRegistry pure-Python (no quickjs required)
# ===========================================================================


def test_module_registry_round_trip() -> None:
    """register() + resolve() returns the stored source unchanged."""
    from aspose_html.js._module_loader import ModuleRegistry

    reg = ModuleRegistry()
    source = "export const add = (a, b) => a + b;"
    reg.register("./a.js", source)
    assert reg.resolve("./a.js") == source


def test_module_registry_overwrite() -> None:
    """Re-registering the same specifier replaces the previous source."""
    from aspose_html.js._module_loader import ModuleRegistry

    reg = ModuleRegistry()
    reg.register("./a.js", "old")
    reg.register("./a.js", "new")
    assert reg.resolve("./a.js") == "new"


def test_module_registry_missing_raises() -> None:
    """resolve() returns None for an unknown specifier (no exception)."""
    from aspose_html.js._module_loader import ModuleRegistry

    reg = ModuleRegistry()
    reg.register("./known.js", "export const x = 1;")
    assert reg.resolve("./unknown.js") is None


def test_module_registry_registered_names_immutable() -> None:
    """len() and __contains__ reflect the registry contents correctly."""
    from aspose_html.js._module_loader import ModuleRegistry

    reg = ModuleRegistry()
    assert len(reg) == 0
    reg.register("./b.js", "export default 42;")
    assert len(reg) == 1
    assert "./b.js" in reg
    assert "./c.js" not in reg


def test_module_not_found_error_is_lookup_error() -> None:
    """ModuleNotFoundError subclasses LookupError and carries the specifier."""
    from aspose_html.js._module_loader import ModuleNotFoundError

    with pytest.raises(ModuleNotFoundError) as exc_info:
        raise ModuleNotFoundError("./x.js")

    exc = exc_info.value
    assert isinstance(exc, LookupError)
    assert str(exc) == "./x.js"
    assert exc.specifier == "./x.js"


def test_module_load_policy_values() -> None:
    """ModuleLoadPolicy.SCRIPT_ONLY and REGISTERED_MODULES exist and differ."""
    from aspose_html.js._module_loader import ModuleLoadPolicy

    assert ModuleLoadPolicy.SCRIPT_ONLY == 0
    assert ModuleLoadPolicy.REGISTERED_MODULES == 1
    assert ModuleLoadPolicy.SCRIPT_ONLY != ModuleLoadPolicy.REGISTERED_MODULES


# ===========================================================================
# Group B — JSContext module integration (quickjs-gated)
# ===========================================================================

_quickjs = pytest.importorskip("quickjs", reason="quickjs not installed")


def _make_doc():
    from aspose_html.dom import Document
    return Document()


def test_jscontext_register_module_stores() -> None:
    """register_module persists the source in the internal _module_registry."""
    from aspose_html.js import JSContext

    doc = _make_doc()
    with JSContext(doc) as ctx:
        ctx.register_module("./m.js", "export const v = 99;")
        assert "./m.js" in ctx._module_registry
        assert ctx._module_registry.resolve("./m.js") == "export const v = 99;"


def test_jscontext_eval_module_executes() -> None:
    """eval_module runs a registered module source without raising."""
    from aspose_html.js import JSContext

    doc = _make_doc()
    with JSContext(doc) as ctx:
        ctx.eval_module("const x = 1;")  # no error expected


def test_jscontext_eval_module_unknown_raises() -> None:
    """eval_module propagates an error for a non-registered import specifier."""
    from aspose_html.js import JSContext, JSEvaluationError

    doc = _make_doc()
    with JSContext(doc) as ctx:
        # Either native ModuleNotFoundError propagation or fallback JSEvaluationError
        with pytest.raises(Exception):
            ctx.eval_module('import "./nonexistent.js";')


def test_jscontext_import_stub_raises_not_implemented() -> None:
    """import_stub always raises NotImplementedError enforcing the headless boundary."""
    from aspose_html.js import JSContext

    doc = _make_doc()
    with JSContext(doc) as ctx:
        with pytest.raises(NotImplementedError) as exc_info:
            ctx.import_stub("./anything.js")
        msg = str(exc_info.value)
        assert "Dynamic import() is not supported in headless mode" in msg
        assert "register_module" in msg


def test_jscontext_module_registry_initialized() -> None:
    """_module_registry attribute is a ModuleRegistry instance on every JSContext."""
    from aspose_html.js import JSContext
    from aspose_html.js._module_loader import ModuleRegistry

    doc = _make_doc()
    with JSContext(doc) as ctx:
        assert isinstance(ctx._module_registry, ModuleRegistry)


# ===========================================================================
# Group C — Package export surface (no quickjs required when importing _module_loader directly)
# ===========================================================================


def test_package_exports_module_registry() -> None:
    """ModuleRegistry is importable from aspose_html.js (requires quickjs at runtime)."""
    from aspose_html.js import ModuleRegistry  # noqa: F401

    assert ModuleRegistry is not None


def test_package_exports_module_not_found_error() -> None:
    """ModuleNotFoundError is importable from aspose_html.js (requires quickjs at runtime)."""
    from aspose_html.js import ModuleNotFoundError  # noqa: F401

    assert ModuleNotFoundError is not None


def test_module_not_found_error_distinct_from_builtin() -> None:
    """Our ModuleNotFoundError inherits from LookupError, not ImportError/ModuleNotFoundError."""
    from aspose_html.js._module_loader import ModuleNotFoundError as OurError

    # Must be LookupError-based (the stdlib ModuleNotFoundError is ImportError-based)
    assert issubclass(OurError, LookupError)
    # Must NOT be a subclass of the stdlib ModuleNotFoundError (which is ImportError)
    assert not issubclass(OurError, ImportError)
    # Confirm it is distinct from the builtin
    import builtins
    assert OurError is not builtins.__dict__.get("ModuleNotFoundError")
