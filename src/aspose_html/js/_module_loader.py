"""Module loader policy and registry for the headless QuickJS bridge.

This module defines the policy layer for JS module loading in a headless,
network-free context.  It has no third-party dependencies and is importable
without ``quickjs`` installed.

Public symbols:

:class:`ModuleLoadPolicy`
    Constants governing how a :class:`~aspose_html.js.JSContext` resolves
    module specifiers.

:class:`ModuleRegistry`
    Maps module specifier strings to ES module source strings.

:class:`ModuleNotFoundError`
    Raised when a module specifier has no registered source.

Examples
--------
>>> reg = ModuleRegistry()
>>> reg.register("./math.js", "export const add = (a, b) => a + b;")
>>> reg.resolve("./math.js")
'export const add = (a, b) => a + b;'
>>> "./math.js" in reg
True
>>> len(reg)
1
"""
from __future__ import annotations

__all__ = ["ModuleLoadPolicy", "ModuleRegistry", "ModuleNotFoundError"]


# ---------------------------------------------------------------------------
# Policy constants
# ---------------------------------------------------------------------------

class ModuleLoadPolicy:
    """Constants governing how a JSContext resolves module specifiers.

    Attributes
    ----------
    SCRIPT_ONLY : int
        Disable module loading; all specifiers raise
        :class:`ModuleNotFoundError`.  This is the default policy for
        a new ``JSContext``.
    REGISTERED_MODULES : int
        Enable resolution of specifiers that have been registered via
        :meth:`ModuleRegistry.register`.

    Examples
    --------
    >>> ModuleLoadPolicy.SCRIPT_ONLY
    0
    >>> ModuleLoadPolicy.REGISTERED_MODULES
    1
    >>> ModuleLoadPolicy.SCRIPT_ONLY != ModuleLoadPolicy.REGISTERED_MODULES
    True
    """

    SCRIPT_ONLY: int = 0
    REGISTERED_MODULES: int = 1


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class ModuleNotFoundError(LookupError):
    """Raised when a module specifier has no registered source.

    Subclasses :class:`LookupError` to match stdlib semantics for
    "name not found in registry" errors.

    Parameters
    ----------
    specifier : str
        The module specifier that could not be resolved.

    Attributes
    ----------
    specifier : str
        The specifier string passed to the constructor.

    Examples
    --------
    >>> err = ModuleNotFoundError("./missing.js")
    >>> err.specifier
    './missing.js'
    >>> isinstance(err, LookupError)
    True
    >>> raise ModuleNotFoundError("./missing.js")
    Traceback (most recent call last):
        ...
    aspose_html.js._module_loader.ModuleNotFoundError: ./missing.js
    """

    def __init__(self, specifier: str) -> None:
        super().__init__(specifier)
        self.specifier: str = specifier


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class ModuleRegistry:
    """Maps module specifiers to ES module source strings.

    A ``ModuleRegistry`` holds an explicit mapping from module specifier
    strings (such as ``"./utils.js"`` or ``"lodash"``) to their ES module
    source code.  It provides no network or filesystem resolution — all
    sources must be supplied by the caller via :meth:`register`.

    This registry is the sole module resolution mechanism in the headless
    QuickJS context.  Specifiers not present in the registry resolve to
    ``None`` from :meth:`resolve`, indicating "not found".

    Examples
    --------
    >>> reg = ModuleRegistry()
    >>> reg.register("./math.js", "export const add = (a, b) => a + b;")
    >>> reg.resolve("./math.js")
    'export const add = (a, b) => a + b;'
    >>> reg.resolve("./missing.js") is None
    True
    >>> len(reg)
    1
    """

    def __init__(self) -> None:
        self._sources: dict[str, str] = {}

    def register(self, specifier: str, source: str) -> None:
        """Register *source* under *specifier*.

        Overwrites any previously registered source for the same specifier.

        Parameters
        ----------
        specifier : str
            The module specifier string (e.g. ``"./utils.js"``).
        source : str
            The ES module source code string.

        Examples
        --------
        >>> reg = ModuleRegistry()
        >>> reg.register("./a.js", "export const x = 1;")
        >>> reg.resolve("./a.js")
        'export const x = 1;'
        >>> reg.register("./a.js", "export const x = 2;")
        >>> reg.resolve("./a.js")
        'export const x = 2;'
        """
        self._sources[specifier] = source

    def resolve(self, specifier: str) -> str | None:
        """Return the registered source for *specifier*, or ``None``.

        Never raises; returns ``None`` for specifiers with no registration.

        Parameters
        ----------
        specifier : str
            The module specifier to look up.

        Returns
        -------
        str or None
            The registered ES module source, or ``None`` when *specifier*
            has no registration.

        Examples
        --------
        >>> reg = ModuleRegistry()
        >>> reg.resolve("not-registered") is None
        True
        >>> reg.register("./b.js", "export default 99;")
        >>> reg.resolve("./b.js")
        'export default 99;'
        """
        return self._sources.get(specifier)

    def __len__(self) -> int:
        """Return the number of registered modules.

        Examples
        --------
        >>> reg = ModuleRegistry()
        >>> len(reg)
        0
        >>> reg.register("a", "export const x = 1;")
        >>> len(reg)
        1
        >>> reg.register("b", "export const y = 2;")
        >>> len(reg)
        2
        """
        return len(self._sources)

    def __contains__(self, specifier: object) -> bool:
        """Return ``True`` if *specifier* is registered.

        Parameters
        ----------
        specifier : object
            The value to test.  Returns ``False`` for any non-string value.

        Examples
        --------
        >>> reg = ModuleRegistry()
        >>> reg.register("b", "export default 42;")
        >>> "b" in reg
        True
        >>> "c" in reg
        False
        >>> 42 in reg
        False
        """
        return specifier in self._sources
