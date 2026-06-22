"""CSS selector parse error utilities.

The DOM Standard §4.2.2 specifies that invalid selector strings raise
"SyntaxError". We use the Python builtin SyntaxError directly — no custom
subclass — so that users do not need to import a custom exception class.
See ADR-007 §7 for rationale.

This module is internal. It provides helpers for formatting error messages.
"""
from __future__ import annotations


def syntax_error(message: str, position: int | None = None) -> SyntaxError:
    """Create a SyntaxError with a descriptive message and optional position."""
    if position is not None:
        return SyntaxError(f"Invalid CSS selector at position {position}: {message}")
    return SyntaxError(f"Invalid CSS selector: {message}")
