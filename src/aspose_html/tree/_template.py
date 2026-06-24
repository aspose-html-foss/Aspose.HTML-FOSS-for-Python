"""TemplateInsertionModeStack — §13.2.4.1 template insertion mode stack.

The <template> element maintains a separate stack of insertion modes in
addition to the main insertion mode.  When inside a template the topmost
template mode governs token processing.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.tree._insertion_modes import InsertionMode


class TemplateInsertionModeStack:
    """The template insertion mode stack per §13.2.4.1.

    Examples
    --------
    >>> from aspose_html.tree._template import TemplateInsertionModeStack
    >>> from aspose_html.tree._insertion_modes import InsertionMode
    >>> stack = TemplateInsertionModeStack()
    >>> stack.push(InsertionMode.IN_TEMPLATE)
    >>> stack.current
    <InsertionMode.IN_TEMPLATE: 'in_template'>
    """

    __slots__ = ("_stack",)

    def __init__(self) -> None:
        self._stack: list[InsertionMode] = []

    def push(self, mode: InsertionMode) -> None:
        """Push a new template insertion mode."""
        self._stack.append(mode)

    def pop(self) -> InsertionMode:
        """Pop and return the current template insertion mode."""
        return self._stack.pop()

    @property
    def current(self) -> InsertionMode | None:
        """The topmost template insertion mode, or None if empty."""
        return self._stack[-1] if self._stack else None

    def __len__(self) -> int:
        return len(self._stack)

    def __repr__(self) -> str:
        return f"TemplateInsertionModeStack({self._stack!r})"
