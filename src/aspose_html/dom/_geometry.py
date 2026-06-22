"""CSSOM View geometry types — DOMRect and DOMRectList.

This is a leaf module: it has no imports from ``aspose_html`` at module level.
All types here are pure Python and carry no DOM-tree state.

References
----------
- CSSOM View Module Level 1 §7.1 — The DOMRect interface
- CSSOM View Module Level 1 §7.2 — The DOMRectList interface
"""
from __future__ import annotations

from typing import Iterator


class DOMRect:
    """An axis-aligned bounding rectangle (CSSOM View §7.1).

    The four stored attributes ``x``, ``y``, ``width``, and ``height`` are
    mutable.  The four computed properties ``top``, ``right``, ``bottom``, and
    ``left`` handle negative dimensions as specified in CSSOM View §7.1:

    - ``top    = min(y, y + height)``
    - ``right  = max(x, x + width)``
    - ``bottom = max(y, y + height)``
    - ``left   = min(x, x + width)``

    In a server-side (headless) context all values default to ``0.0``.

    Examples
    --------
    >>> r = DOMRect(x=10.0, y=20.0, width=100.0, height=50.0)
    >>> r.left
    10.0
    >>> r.right
    110.0
    >>> r.top
    20.0
    >>> r.bottom
    70.0
    >>> r2 = DOMRect()
    >>> r2.x == r2.y == r2.width == r2.height == 0.0
    True
    """

    __slots__ = ("x", "y", "width", "height")

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 0.0,
        height: float = 0.0,
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height

    # ------------------------------------------------------------------
    # Computed read-only properties (CSSOM View §7.1)
    # ------------------------------------------------------------------

    @property
    def top(self) -> float:
        """Minimum of ``y`` and ``y + height`` per CSSOM View §7.1.

        Examples
        --------
        >>> DOMRect(y=20.0, height=50.0).top
        20.0
        >>> DOMRect(y=20.0, height=-50.0).top
        -30.0
        """
        return min(self.y, self.y + self.height)

    @property
    def right(self) -> float:
        """Maximum of ``x`` and ``x + width`` per CSSOM View §7.1.

        Examples
        --------
        >>> DOMRect(x=10.0, width=100.0).right
        110.0
        >>> DOMRect(x=10.0, width=-5.0).right
        10.0
        """
        return max(self.x, self.x + self.width)

    @property
    def bottom(self) -> float:
        """Maximum of ``y`` and ``y + height`` per CSSOM View §7.1.

        Examples
        --------
        >>> DOMRect(y=20.0, height=50.0).bottom
        70.0
        >>> DOMRect(y=20.0, height=-50.0).bottom
        20.0
        """
        return max(self.y, self.y + self.height)

    @property
    def left(self) -> float:
        """Minimum of ``x`` and ``x + width`` per CSSOM View §7.1.

        Examples
        --------
        >>> DOMRect(x=10.0, width=100.0).left
        10.0
        >>> DOMRect(x=10.0, width=-5.0).left
        5.0
        """
        return min(self.x, self.x + self.width)

    def __repr__(self) -> str:
        return (
            f"DOMRect(x={self.x!r}, y={self.y!r}, "
            f"width={self.width!r}, height={self.height!r})"
        )


class DOMRectList:
    """An immutable sequence of :class:`DOMRect` objects (CSSOM View §7.2).

    Iteration and index access follow standard Python sequence protocol.
    ``item()`` returns ``None`` for out-of-range indices, matching the WHATWG
    WebIDL spec's nullable return type.  ``__getitem__`` raises ``IndexError``
    for out-of-range indices, following the Python protocol.

    Examples
    --------
    >>> rl = DOMRectList([])
    >>> len(rl)
    0
    >>> rl.item(0) is None
    True
    >>> r1, r2 = DOMRect(1.0), DOMRect(2.0)
    >>> rl2 = DOMRectList([r1, r2])
    >>> len(rl2)
    2
    >>> rl2.item(0) is r1
    True
    >>> rl2.item(99) is None
    True
    >>> list(rl2) == [r1, r2]
    True
    """

    __slots__ = ("_rects",)

    def __init__(self, rects: list[DOMRect]) -> None:
        self._rects: list[DOMRect] = list(rects)

    def item(self, index: int) -> DOMRect | None:
        """Return the rect at *index*, or ``None`` if out of range.

        Examples
        --------
        >>> rl = DOMRectList([DOMRect()])
        >>> rl.item(0) is not None
        True
        >>> rl.item(5) is None
        True
        """
        if 0 <= index < len(self._rects):
            return self._rects[index]
        return None

    def __len__(self) -> int:
        return len(self._rects)

    def __iter__(self) -> Iterator[DOMRect]:
        return iter(self._rects)

    def __getitem__(self, index: int) -> DOMRect:
        return self._rects[index]

    def __repr__(self) -> str:
        return f"DOMRectList([{', '.join(repr(r) for r in self._rects)}])"
