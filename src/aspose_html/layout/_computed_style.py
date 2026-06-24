"""Layout-facing immutable style snapshot — M7.1 ( / ).

``ComputedStyle`` is a read-only, frozen wrapper around the
:class:`~aspose_html.dom._cascade.ComputedStyleDeclaration` that the
existing cascade engine already produces, tagged with the
``Document._style_epoch`` at which it was produced.

The cascade engine (``aspose_html.dom._cascade``) remains the single
**producer** of resolved style; ``ComputedStyle`` adds a stable, cacheable
*view*, never a second cascade (). It introduces no new cascade
rule, selector-matching path, or property-resolution logic — it merely
caches the §6.1.2 *computed value* (CSS 2.2 §6) so layout passes can read
an element's style many times without re-resolving it on every access.

See  (M7 architecture baseline) and  (M7.1 implementation).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from aspose_html.dom._cascade import ComputedStyleDeclaration


class ComputedStyle:
    """Immutable layout-facing snapshot of an element's resolved style.

    A ``ComputedStyle`` wraps the ``ComputedStyleDeclaration`` produced by
    the cascade engine plus the ``Document._style_epoch`` at which it was
    produced. It is frozen after construction (``__slots__`` omits a
    ``__dict__``), so it carries no shared mutable state — the precondition
    for the M7.6 process-parallel rendering model ().

    The read accessors (``get``, ``__getitem__``, ``__contains__``,
    ``__iter__``, ``__len__``) delegate directly to the wrapped
    declaration and return byte-identical values.

    Parameters
    ----------
    decl:
        The ``ComputedStyleDeclaration`` snapshot to wrap.
    epoch:
        The ``Document._style_epoch`` value at production time.

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> from aspose_html.dom import Document
    >>> from aspose_html.layout import ComputedStyle, computed_style
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> doc.append_child(el)
    <Element 'DIV'>
    >>> sheet = CSSStyleSheet()
    >>> sheet.replace_sync("div { color: red }")
    >>> doc.attach_style_sheet(sheet)
    >>> rs = computed_style(el)
    >>> isinstance(rs, ComputedStyle)
    True
    >>> rs.get("color")
    'red'
    >>> rs.get("not-set")
    ''
    >>> "color" in rs
    True
    >>> rs.epoch == doc._style_epoch
    True
    """

    __slots__ = ("_decl", "_epoch")

    def __init__(self, decl: "ComputedStyleDeclaration", epoch: int) -> None:
        self._decl = decl
        self._epoch = epoch

    @property
    def epoch(self) -> int:
        """The ``Document._style_epoch`` this snapshot was produced at.

        Read-only — there is no setter.

        Examples
        --------
        >>> from aspose_html.dom._cascade import ComputedStyleDeclaration
        >>> from aspose_html.layout import ComputedStyle
        >>> rs = ComputedStyle(ComputedStyleDeclaration({"color": "red"}), 7)
        >>> rs.epoch
        7
        """
        return self._epoch

    def get(self, name: str) -> str:
        """Return the resolved value of *name*, or ``''`` when absent.

        Mirrors ``ComputedStyleDeclaration.get_property_value`` — never
        raises, returning the empty string for an unknown property.

        Examples
        --------
        >>> from aspose_html.dom._cascade import ComputedStyleDeclaration
        >>> from aspose_html.layout import ComputedStyle
        >>> rs = ComputedStyle(ComputedStyleDeclaration({"color": "red"}), 0)
        >>> rs.get("color")
        'red'
        >>> rs.get("margin")
        ''
        """
        return self._decl.get_property_value(name)

    def __getitem__(self, name: str) -> str:
        """Return the resolved value of *name*; raise ``KeyError`` if absent.

        Byte-identical to ``ComputedStyleDeclaration.__getitem__``.

        Examples
        --------
        >>> from aspose_html.dom._cascade import ComputedStyleDeclaration
        >>> from aspose_html.layout import ComputedStyle
        >>> rs = ComputedStyle(ComputedStyleDeclaration({"color": "red"}), 0)
        >>> rs["color"]
        'red'
        """
        return self._decl[name]

    def __contains__(self, name: object) -> bool:
        """Return ``True`` when *name* is a resolved property.

        Examples
        --------
        >>> from aspose_html.dom._cascade import ComputedStyleDeclaration
        >>> from aspose_html.layout import ComputedStyle
        >>> rs = ComputedStyle(ComputedStyleDeclaration({"color": "red"}), 0)
        >>> "color" in rs
        True
        >>> "margin" in rs
        False
        """
        return name in self._decl

    def __iter__(self) -> "Iterator[str]":
        """Iterate over resolved property names.

        Examples
        --------
        >>> from aspose_html.dom._cascade import ComputedStyleDeclaration
        >>> from aspose_html.layout import ComputedStyle
        >>> rs = ComputedStyle(ComputedStyleDeclaration({"color": "red"}), 0)
        >>> list(rs)
        ['color']
        """
        return iter(self._decl)

    def __len__(self) -> int:
        """Return the number of resolved properties.

        Examples
        --------
        >>> from aspose_html.dom._cascade import ComputedStyleDeclaration
        >>> from aspose_html.layout import ComputedStyle
        >>> rs = ComputedStyle(ComputedStyleDeclaration({"color": "red"}), 0)
        >>> len(rs)
        1
        """
        return len(self._decl)
