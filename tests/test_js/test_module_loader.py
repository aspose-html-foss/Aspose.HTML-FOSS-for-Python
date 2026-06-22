"""Tests for aspose_html.js._module_loader.

Covers ModuleLoadPolicy, ModuleNotFoundError, and ModuleRegistry.
No ``quickjs`` dependency required.

The module is loaded directly via ``importlib`` to avoid triggering the
``aspose_html.js`` package ``__init__.py``, which hard-requires ``quickjs``.
This is intentional: ``_module_loader.py`` must be importable without
``quickjs`` (SPEC-124 NFR-2); the package-level guard should not prevent
testing the pure-Python policy layer.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Direct module load — bypasses aspose_html.js.__init__ quickjs guard
# ---------------------------------------------------------------------------

_MOD_PATH = (
    Path(__file__).parent.parent.parent
    / "src" / "aspose_html" / "js" / "_module_loader.py"
)
_spec = importlib.util.spec_from_file_location(
    "aspose_html.js._module_loader", _MOD_PATH
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
sys.modules.setdefault("aspose_html.js._module_loader", _mod)

ModuleLoadPolicy = _mod.ModuleLoadPolicy
ModuleNotFoundError = _mod.ModuleNotFoundError
ModuleRegistry = _mod.ModuleRegistry


# ---------------------------------------------------------------------------
# ModuleLoadPolicy
# ---------------------------------------------------------------------------

class TestModuleLoadPolicyConstants:
    def test_module_load_policy_constants_are_distinct_ints(self) -> None:
        """SCRIPT_ONLY and REGISTERED_MODULES are distinct integer constants."""
        assert isinstance(ModuleLoadPolicy.SCRIPT_ONLY, int)
        assert isinstance(ModuleLoadPolicy.REGISTERED_MODULES, int)
        assert ModuleLoadPolicy.SCRIPT_ONLY != ModuleLoadPolicy.REGISTERED_MODULES

    def test_module_load_policy_script_only_is_zero(self) -> None:
        """SCRIPT_ONLY is 0 (the default/off value)."""
        assert ModuleLoadPolicy.SCRIPT_ONLY == 0

    def test_module_load_policy_registered_modules_is_one(self) -> None:
        """REGISTERED_MODULES is 1 (the opt-in value)."""
        assert ModuleLoadPolicy.REGISTERED_MODULES == 1


# ---------------------------------------------------------------------------
# ModuleNotFoundError
# ---------------------------------------------------------------------------

class TestModuleNotFoundError:
    def test_module_not_found_error_is_lookup_error(self) -> None:
        """ModuleNotFoundError must subclass LookupError (INV-001)."""
        err = ModuleNotFoundError("./missing.js")
        assert isinstance(err, LookupError)

    def test_module_not_found_error_stores_specifier(self) -> None:
        """The .specifier attribute stores the exact specifier string passed."""
        err = ModuleNotFoundError("./some/module.js")
        assert err.specifier == "./some/module.js"

    def test_module_not_found_error_is_catchable_as_lookup_error(self) -> None:
        """ModuleNotFoundError can be caught with except LookupError."""
        with pytest.raises(LookupError):
            raise ModuleNotFoundError("./catchme.js")

    def test_module_not_found_error_str_is_specifier(self) -> None:
        """str(error) contains the specifier."""
        err = ModuleNotFoundError("./foo.js")
        assert "./foo.js" in str(err)

    def test_module_not_found_error_empty_specifier(self) -> None:
        """An empty string is a valid specifier."""
        err = ModuleNotFoundError("")
        assert err.specifier == ""


# ---------------------------------------------------------------------------
# ModuleRegistry
# ---------------------------------------------------------------------------

class TestModuleRegistry:
    def test_module_registry_register_and_resolve_roundtrip(self) -> None:
        """register() then resolve() returns the registered source."""
        reg = ModuleRegistry()
        reg.register("./math.js", "export const add = (a, b) => a + b;")
        assert reg.resolve("./math.js") == "export const add = (a, b) => a + b;"

    def test_module_registry_resolve_missing_returns_none(self) -> None:
        """resolve() returns None for an unregistered specifier."""
        reg = ModuleRegistry()
        assert reg.resolve("./not-registered.js") is None

    def test_module_registry_overwrite_registration(self) -> None:
        """Re-registering the same specifier replaces the previous source."""
        reg = ModuleRegistry()
        reg.register("./a.js", "export const x = 1;")
        reg.register("./a.js", "export const x = 99;")
        assert reg.resolve("./a.js") == "export const x = 99;"

    def test_module_registry_len(self) -> None:
        """__len__ reflects the number of distinct registered specifiers."""
        reg = ModuleRegistry()
        assert len(reg) == 0
        reg.register("a", "export const a = 1;")
        assert len(reg) == 1
        reg.register("b", "export const b = 2;")
        assert len(reg) == 2
        # Overwriting does not increase length
        reg.register("a", "export const a = 42;")
        assert len(reg) == 2

    def test_module_registry_contains(self) -> None:
        """__contains__ returns True for registered specifiers only."""
        reg = ModuleRegistry()
        reg.register("present", "export default 1;")
        assert "present" in reg
        assert "absent" not in reg

    def test_module_registry_empty_string_specifier_accepted(self) -> None:
        """An empty string is a valid specifier key."""
        reg = ModuleRegistry()
        reg.register("", "export const empty = true;")
        assert reg.resolve("") == "export const empty = true;"
        assert "" in reg
        assert len(reg) == 1

    def test_module_registry_multiple_specifiers_independent(self) -> None:
        """Multiple specifiers are independently stored and retrieved."""
        reg = ModuleRegistry()
        specifiers = {
            "./a.js": "export const a = 1;",
            "./b.js": "export const b = 2;",
            "lodash": "export default {};",
        }
        for spec, src in specifiers.items():
            reg.register(spec, src)
        for spec, src in specifiers.items():
            assert reg.resolve(spec) == src
        assert len(reg) == len(specifiers)

    def test_module_registry_non_string_key_not_in_registry(self) -> None:
        """Non-string values are not contained in the registry."""
        reg = ModuleRegistry()
        reg.register("42", "export default 42;")
        assert 42 not in reg  # integer 42 != string "42"

    def test_module_registry_starts_empty(self) -> None:
        """A freshly constructed registry has length 0 and no entries."""
        reg = ModuleRegistry()
        assert len(reg) == 0
        assert reg.resolve("anything") is None
        assert "anything" not in reg


# ---------------------------------------------------------------------------
# Module-level __all__
# ---------------------------------------------------------------------------

class TestModuleAll:
    def test_all_exports_present(self) -> None:
        """_module_loader.__all__ exports all three public symbols."""
        assert set(_mod.__all__) == {
            "ModuleLoadPolicy",
            "ModuleRegistry",
            "ModuleNotFoundError",
        }
