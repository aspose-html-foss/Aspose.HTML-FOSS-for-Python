"""In-memory History API stubs.

State values are snapshotted through the shared Track 67 structured-clone
helper seam. Unsupported values preserve the legacy ``TypeError`` contract.
"""
from __future__ import annotations

import dataclasses
from urllib.parse import urlparse
from typing import TYPE_CHECKING

from aspose_html.dom._exceptions import SecurityError
from aspose_html.dom._structured_clone import clone_or_raise_data_clone_error
from aspose_html.dom._event import HashChangeEvent, PopStateEvent

if TYPE_CHECKING:
    from aspose_html.dom._window import Window


@dataclasses.dataclass
class _HistoryEntry:
    state: object | None
    title: str
    url: str


def _extract_fragment(url: str) -> str:
    return urlparse(url).fragment


class History:
    """In-memory session history for a Window.

    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> doc._url = "https://example.com/"
    >>> h = doc.default_view.history
    >>> h.length
    1
    """
    __slots__ = ("_window", "_entries", "_index", "_scroll_restoration")

    def __init__(self, window: "Window") -> None:
        self._window = window
        self._entries: list[_HistoryEntry] = [_HistoryEntry(None, "", window._document._url)]
        self._index = 0
        self._scroll_restoration = "auto"

    @property
    def length(self) -> int:
        return len(self._entries)

    @property
    def state(self) -> object | None:
        return self._clone_state_for_read(self._entries[self._index].state)

    @property
    def scroll_restoration(self) -> str:
        return self._scroll_restoration

    @scroll_restoration.setter
    def scroll_restoration(self, value: str) -> None:
        self._scroll_restoration = value if value in ("auto", "manual") else "auto"

    def push_state(self, state: object, title: str = "", url: str | None = None) -> None:
        """Push a new session-history entry."""
        old_url = self._entries[self._index].url
        resolved_url = self._resolve_and_check_origin(url)
        state_copy = self._clone_state_for_storage(state)
        self._entries = self._entries[: self._index + 1]
        self._entries.append(_HistoryEntry(state=state_copy, title=title, url=resolved_url))
        self._index = len(self._entries) - 1
        self._apply_navigation_url(resolved_url)
        self._dispatch_hashchange_if_needed(old_url, resolved_url)

    def replace_state(self, state: object, title: str = "", url: str | None = None) -> None:
        """Replace the current session-history entry."""
        old_url = self._entries[self._index].url
        resolved_url = self._resolve_and_check_origin(url)
        state_copy = self._clone_state_for_storage(state)
        entry = self._entries[self._index]
        entry.state = state_copy
        entry.title = title
        entry.url = resolved_url
        self._apply_navigation_url(resolved_url)
        self._dispatch_hashchange_if_needed(old_url, resolved_url)

    def go(self, delta: int = 0) -> None:
        """Move by ``delta`` in session history and dispatch ``popstate`` on traversal.

        Dispatch semantics:
        - ``go(0)`` is a no-op (no event)
        - out-of-range traversal is a no-op (no event)
        - index-changing traversal dispatches exactly one ``PopStateEvent``
          after updating ``window.location``

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc._url = "https://example.com/"
        >>> win = doc.default_view
        >>> h = win.history
        >>> seen = []
        >>> win.add_event_listener("popstate", lambda evt: seen.append((evt.state, win.location.pathname)))
        >>> h.push_state({"a": 1}, "", "/a")
        >>> h.push_state({"b": 2}, "", "/b")
        >>> h.back()
        >>> seen
        [({'a': 1}, '/a')]
        """
        normalized_delta = self._normalize_traversal_delta(delta)
        if normalized_delta == 0:
            return
        target_index = self._index + normalized_delta
        if target_index < 0 or target_index >= len(self._entries):
            return
        old_url = self._entries[self._index].url
        self._index = target_index
        entry = self._entries[target_index]
        self._apply_navigation_url(entry.url)
        self._dispatch_popstate_for_entry(entry)
        self._dispatch_hashchange_if_needed(old_url, entry.url)

    def back(self) -> None:
        """Equivalent to ``go(-1)``."""
        self.go(-1)

    def forward(self) -> None:
        """Equivalent to ``go(1)``."""
        self.go(1)

    def _apply_navigation_url(self, url: str) -> None:
        self._window._document._url = url

    def _resolve_and_check_origin(self, url: str | None) -> str:
        current_url = self._entries[self._index].url
        if url is None:
            return current_url
        from aspose_html.url import URL, URLParseError  # noqa: PLC0415
        try:
            target = URL(url, base=current_url)
        except (URLParseError, ValueError) as exc:
            raise SecurityError(f"invalid URL: {url!r}") from exc
        try:
            current = URL(current_url)
        except (URLParseError, ValueError):
            if target.href != current_url:
                raise SecurityError(f"cross-origin pushState blocked: {url!r}")
            return target.href
        if (
            target.protocol != current.protocol
            or target.hostname != current.hostname
            or target.port != current.port
        ):
            raise SecurityError(f"cross-origin pushState blocked: {url!r}")
        return target.href

    def _is_effective_url_change(self, target_url: str, current_url: str) -> bool:
        return target_url != current_url

    def _dispatch_hashchange_if_needed(self, old_url: str, new_url: str) -> None:
        if old_url == new_url:
            return
        old_parts = urlparse(old_url)
        new_parts = urlparse(new_url)
        old_non_fragment = (
            old_parts.scheme,
            old_parts.netloc,
            old_parts.path,
            old_parts.params,
            old_parts.query,
        )
        new_non_fragment = (
            new_parts.scheme,
            new_parts.netloc,
            new_parts.path,
            new_parts.params,
            new_parts.query,
        )
        if old_non_fragment != new_non_fragment:
            return
        if _extract_fragment(old_url) == _extract_fragment(new_url):
            return
        self._window.dispatch_event(HashChangeEvent(old_url=old_url, new_url=new_url))

    def _dispatch_popstate_for_entry(self, entry: _HistoryEntry) -> None:
        self._window.dispatch_event(PopStateEvent(state=self._clone_state_for_read(entry.state)))

    def _normalize_traversal_delta(self, delta: object) -> int:
        if isinstance(delta, int):
            return delta
        raise TypeError("History.go delta must be an int")

    def _clone_state_for_storage(self, state: object) -> object:
        if state is None:
            return None
        return self._clone_state_or_raise(state)

    def _clone_state_for_read(self, state: object) -> object:
        if state is None:
            return None
        return self._clone_state_or_raise(state)

    def _clone_state_or_raise(self, state: object) -> object:
        try:
            return clone_or_raise_data_clone_error(state)
        except Exception as exc:  # noqa: BLE001
            raise TypeError(
                "History state is not supported by structured-clone-compatible deepcopy"
            ) from exc
