"""URLSearchParams implementation."""
from __future__ import annotations

from collections.abc import Iterator
from urllib.parse import parse_qsl, urlencode


class URLSearchParams:
    """Ordered query-string pairs with duplicate-key support.

    >>> p = URLSearchParams("a=1&a=2")
    >>> p.get_all("a")
    ['1', '2']
    """
    __slots__ = ("_entries", "_url_ref")

    def __init__(self, init: str | dict[object, object] | list[tuple[object, object]] | None = None) -> None:
        self._entries: list[tuple[str, str]] = []
        self._url_ref = None
        if init is None:
            return
        if isinstance(init, str):
            raw = init[1:] if init.startswith("?") else init
            self._entries = [(k, v) for k, v in parse_qsl(raw, keep_blank_values=True)]
            return
        if isinstance(init, dict):
            self._entries = [(str(k), str(v)) for k, v in init.items()]
            return
        self._entries = [(str(k), str(v)) for k, v in init]

    def _sync(self) -> None:
        if self._url_ref is not None:
            self._url_ref._set_search_from_params(self)

    def _refresh_from_string(self, value: str) -> None:
        raw = value[1:] if value.startswith("?") else value
        self._entries = [(k, v) for k, v in parse_qsl(raw, keep_blank_values=True)]

    @property
    def size(self) -> int:
        """Return the total number of name-value pairs, including duplicates.

        WHATWG URL Standard §6.2 (added to the living standard in 2022).

        >>> URLSearchParams("a=1&b=2").size
        2
        >>> URLSearchParams("a=1&a=2").size
        2
        >>> URLSearchParams("").size
        0
        """
        return len(self._entries)

    def append(self, name: str, value: str) -> None:
        """Append a name/value pair.

        >>> p = URLSearchParams()
        >>> p.append("a", "1")
        >>> str(p)
        'a=1'
        """
        self._entries.append((str(name), str(value)))
        self._sync()

    def delete(self, name: str, value: str | None = None) -> None:
        """Remove matching name-value pairs.

        With one argument removes all pairs with the given name (existing
        behaviour, unchanged). With two arguments removes only pairs where
        both name and value match exactly (WHATWG URL Standard §6.2).

        >>> p = URLSearchParams("a=1&a=2&b=3")
        >>> p.delete("b")
        >>> str(p)
        'a=1&a=2'
        >>> p2 = URLSearchParams("a=1&a=2&b=3")
        >>> p2.delete("a", "1")
        >>> str(p2)
        'a=2&b=3'
        """
        name = str(name)
        if value is None:
            self._entries = [(k, v) for k, v in self._entries if k != name]
        else:
            value = str(value)
            self._entries = [
                (k, v) for k, v in self._entries
                if not (k == name and v == value)
            ]
        self._sync()

    def get(self, name: str) -> str | None:
        """Return first value for *name*, else None."""
        name = str(name)
        for k, v in self._entries:
            if k == name:
                return v
        return None

    def get_all(self, name: str) -> list[str]:
        """Return all values for *name*."""
        name = str(name)
        return [v for k, v in self._entries if k == name]

    def has(self, name: str, value: str | None = None) -> bool:
        """Return ``True`` if a matching pair exists.

        With one argument returns ``True`` if any pair has the given name
        (existing behaviour, unchanged). With two arguments returns ``True``
        only if a pair exists with both the given name and value
        (WHATWG URL Standard §6.2 two-argument form).

        >>> p = URLSearchParams("a=1&a=2&b=3")
        >>> p.has("a")
        True
        >>> p.has("c")
        False
        >>> p.has("a", "1")
        True
        >>> p.has("a", "9")
        False
        """
        name = str(name)
        if value is None:
            return any(k == name for k, _ in self._entries)
        value = str(value)
        return any(k == name and v == value for k, v in self._entries)

    def set(self, name: str, value: str) -> None:
        """Replace all values for *name* with one value."""
        name = str(name)
        value = str(value)
        first = next((i for i, (k, _) in enumerate(self._entries) if k == name), None)
        if first is None:
            self._entries.append((name, value))
        else:
            kept = [(k, v) for (k, v) in self._entries if k != name]
            kept.insert(first, (name, value))
            self._entries = kept
        self._sync()

    def sort(self) -> None:
        """Sort entries by name, stable for equal names."""
        self._entries.sort(key=lambda kv: kv[0])
        self._sync()

    def keys(self) -> Iterator[str]:
        for k, _ in self._entries:
            yield k

    def values(self) -> Iterator[str]:
        for _, v in self._entries:
            yield v

    def items(self) -> Iterator[tuple[str, str]]:
        return iter(self._entries)

    def entries(self) -> Iterator[tuple[str, str]]:
        """Return an iterator of ``(name, value)`` pairs.

        WHATWG URL Standard §6.2. Identical to :meth:`items`; both coexist:
        ``entries()`` for WHATWG/JavaScript-standard code, ``items()`` for
        Python-natural usage.

        >>> list(URLSearchParams("a=1&b=2").entries())
        [('a', '1'), ('b', '2')]
        >>> list(URLSearchParams("").entries())
        []
        """
        return iter(self._entries)

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __str__(self) -> str:
        return urlencode(self._entries, doseq=True)
