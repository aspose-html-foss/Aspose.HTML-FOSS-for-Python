"""FormData — snapshot name/value collection."""
from __future__ import annotations

import logging
from collections.abc import Iterator

_LOGGER = logging.getLogger("aspose_html.formdata")
_SKIP_INPUT_TYPES = frozenset({"submit", "reset", "button", "image"})


class FormData:
    """Snapshot collection of form control name/value pairs.

    >>> fd = FormData()
    >>> len(fd)
    0
    """
    __slots__ = ("_entries",)

    def __init__(self, form: object | None = None) -> None:
        self._entries: list[tuple[str, str]] = []
        if form is not None:
            self._snapshot_form(form)

    def _snapshot_form(self, form) -> None:
        from aspose_html.dom.html._form_elements import (
            HTMLButtonElement,
            HTMLInputElement,
            HTMLOptionElement,
            HTMLOutputElement,
            HTMLSelectElement,
            HTMLTextAreaElement,
        )

        for el in form.elements:
            name = getattr(el, "name", "") or ""
            if name == "" or getattr(el, "disabled", False):
                continue
            if isinstance(el, HTMLInputElement):
                t = el.type
                if t == "file":
                    _LOGGER.debug("FormData: skipping file input %r", name)
                    continue
                if t in _SKIP_INPUT_TYPES:
                    continue
                if t in ("checkbox", "radio") and not el.checked:
                    continue
                v = "on" if t in ("checkbox", "radio") and el.value == "" else el.value
                self._entries.append((name, v))
            elif isinstance(el, HTMLSelectElement):
                if el.multiple:
                    for opt in el.options:
                        if isinstance(opt, HTMLOptionElement) and opt.selected:
                            self._entries.append((name, opt.value))
                else:
                    chosen = None
                    for opt in el.options:
                        if isinstance(opt, HTMLOptionElement):
                            if chosen is None:
                                chosen = opt
                            if opt.selected:
                                chosen = opt
                                break
                    if chosen is not None:
                        self._entries.append((name, chosen.value))
            elif isinstance(el, HTMLTextAreaElement):
                self._entries.append((name, el.value))
            elif isinstance(el, HTMLOutputElement):
                self._entries.append((name, el.value))
            elif isinstance(el, HTMLButtonElement):
                continue

    def append(self, name: str, value: str) -> None:
        self._entries.append((str(name), str(value)))

    def delete(self, name: str) -> None:
        name = str(name)
        self._entries = [(n, v) for (n, v) in self._entries if n != name]

    def get(self, name: str) -> str | None:
        name = str(name)
        for n, v in self._entries:
            if n == name:
                return v
        return None

    def get_all(self, name: str) -> list[str]:
        name = str(name)
        return [v for n, v in self._entries if n == name]

    def has(self, name: str) -> bool:
        name = str(name)
        return any(n == name for n, _ in self._entries)

    def set(self, name: str, value: str) -> None:
        name, value = str(name), str(value)
        first = next((i for i, (n, _) in enumerate(self._entries) if n == name), None)
        if first is None:
            self._entries.append((name, value))
            return
        kept = [(n, v) for (n, v) in self._entries if n != name]
        kept.insert(first, (name, value))
        self._entries = kept

    def entries(self) -> Iterator[tuple[str, str]]:
        return iter(self._entries)

    def keys(self) -> Iterator[str]:
        for n, _ in self._entries:
            yield n

    def values(self) -> Iterator[str]:
        for _, v in self._entries:
            yield v

    def __iter__(self) -> Iterator[tuple[str, str]]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)
