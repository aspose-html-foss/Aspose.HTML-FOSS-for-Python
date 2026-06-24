"""StackOfOpenElements — §13.2.4.2 open elements stack.

The stack is a list[Element] where index 0 is the bottom (oldest) and
index -1 is the current (most recently opened) element.

Scope element sets are spec-defined, small, and stable — written as
frozensets here rather than generated (see  rationale for ).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom import Element

# §13.2.4.2 — standard scope boundary elements
_SCOPE_ELEMENTS: frozenset[str] = frozenset({
    "applet", "caption", "html", "table", "td", "th",
    "marquee", "object", "template",
    # MathML
    "mi", "mo", "mn", "ms", "mtext", "annotation-xml",
    # SVG
    "foreignobject", "desc", "title",
})

_BUTTON_SCOPE_ELEMENTS: frozenset[str] = _SCOPE_ELEMENTS | frozenset({"button"})

_LIST_ITEM_SCOPE_ELEMENTS: frozenset[str] = _SCOPE_ELEMENTS | frozenset({"ol", "ul"})

_TABLE_SCOPE_ELEMENTS: frozenset[str] = frozenset({"html", "table", "template"})

_SELECT_SCOPE_ELEMENTS: frozenset[str] = frozenset({"optgroup", "option"})


class StackOfOpenElements:
    """The stack of open elements as defined in §13.2.4.2.

    Provides all scope-checking operations required by the spec:
    has_in_scope, has_in_button_scope, has_in_list_item_scope,
    has_in_table_scope, has_in_select_scope.

    The stack is a list[Element] where index 0 is the bottom (oldest)
    and index -1 is the current (most recently opened) element.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> from aspose_html.tree._open_elements import StackOfOpenElements
    >>> doc = Document()
    >>> stack = StackOfOpenElements()
    >>> html_el = doc.create_element('html')
    >>> stack.push(html_el)
    >>> stack.current.tag_name
    'HTML'
    """

    __slots__ = ("_stack",)

    def __init__(self) -> None:
        self._stack: list[Element] = []

    def push(self, element: Element) -> None:
        """Push element onto the top of the stack."""
        self._stack.append(element)

    def pop(self) -> Element:
        """Pop and return the current (top) element."""
        return self._stack.pop()

    def pop_until(self, *tag_names: str) -> None:
        """Pop elements until an element with one of tag_names is popped."""
        tag_set = set(tag_names)
        while self._stack:
            el = self._stack.pop()
            if el._local_name in tag_set:
                return

    def pop_until_node(self, node: Element) -> None:
        """Pop elements until node is popped."""
        while self._stack:
            el = self._stack.pop()
            if el is node:
                return

    @property
    def current(self) -> Element | None:
        """The topmost element, or None if empty."""
        return self._stack[-1] if self._stack else None

    @property
    def bottom(self) -> Element | None:
        """The bottom-most element, or None if empty."""
        return self._stack[0] if self._stack else None

    def __len__(self) -> int:
        return len(self._stack)

    def __iter__(self):
        return iter(self._stack)

    def __contains__(self, tag_name: str) -> bool:  # type: ignore[override]
        """True if any element on the stack has the given tag_name (lowercase)."""
        return any(el._local_name == tag_name for el in self._stack)

    def contains_node(self, node: Element) -> bool:
        """True if the exact node object is on the stack."""
        return node in self._stack

    def has_in_scope(self, tag_name: str) -> bool:
        """§13.2.4.2 — has element in scope."""
        for el in reversed(self._stack):
            if el._local_name == tag_name:
                return True
            if el._local_name in _SCOPE_ELEMENTS:
                return False
        return False

    def has_in_button_scope(self, tag_name: str) -> bool:
        """§13.2.4.2 — has element in button scope."""
        for el in reversed(self._stack):
            if el._local_name == tag_name:
                return True
            if el._local_name in _BUTTON_SCOPE_ELEMENTS:
                return False
        return False

    def has_in_list_item_scope(self, tag_name: str) -> bool:
        """§13.2.4.2 — has element in list item scope."""
        for el in reversed(self._stack):
            if el._local_name == tag_name:
                return True
            if el._local_name in _LIST_ITEM_SCOPE_ELEMENTS:
                return False
        return False

    def has_in_table_scope(self, tag_name: str) -> bool:
        """§13.2.4.2 — has element in table scope."""
        for el in reversed(self._stack):
            if el._local_name == tag_name:
                return True
            if el._local_name in _TABLE_SCOPE_ELEMENTS:
                return False
        return False

    def has_in_select_scope(self, tag_name: str) -> bool:
        """§13.2.4.2 — has element in select scope.

        Note: select scope is inverted — any element NOT in the select
        scope set stops the search.
        """
        for el in reversed(self._stack):
            if el._local_name == tag_name:
                return True
            if el._local_name not in _SELECT_SCOPE_ELEMENTS:
                return False
        return False

    def index_of(self, element: Element) -> int:
        """Return 0-based index from bottom, or -1 if not found."""
        try:
            return self._stack.index(element)
        except ValueError:
            return -1

    def __repr__(self) -> str:
        names = [el._local_name for el in self._stack]
        return f"StackOfOpenElements({names!r})"
