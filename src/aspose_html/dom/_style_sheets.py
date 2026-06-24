"""Stylesheet list surface for DOM stylesheet discovery ()."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterator

if TYPE_CHECKING:
    from aspose_html.cssom import CSSStyleSheet


class StyleSheetList:
    """Live ordered stylesheet collection.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> doc.style_sheets.length
    0
    """

    __slots__ = ("_provider",)

    def __init__(self, provider: Callable[[], list["CSSStyleSheet"]]) -> None:
        self._provider = provider

    @property
    def length(self) -> int:
        """Number of stylesheets currently exposed by this list."""
        return len(self._provider())

    def item(self, index: int) -> "CSSStyleSheet | None":
        """Return stylesheet at *index*, or ``None`` when out of range."""
        sheets = self._provider()
        if index < 0 or index >= len(sheets):
            return None
        return sheets[index]

    def __len__(self) -> int:
        return self.length

    def __iter__(self) -> Iterator["CSSStyleSheet"]:
        return iter(self._provider())

    def __getitem__(self, index: int) -> "CSSStyleSheet":
        return self._provider()[index]
