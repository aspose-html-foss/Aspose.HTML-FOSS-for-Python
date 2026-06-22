"""Per-document style cache lookup — M7.1 (SPEC-168 / ADR-315).

``computed_style(element)`` returns a cached :class:`ComputedStyle` for an
element, resolving it through the existing cascade engine on a miss. The
cache lives on the owning ``Document`` instance (keyed by ``id(element)``)
and is invalidated lazily whenever the document's ``_style_epoch`` is
bumped — never at module scope (INV-010). The lookup consults a flat
dict; it performs no tree traversal (INV-009).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ._computed_style import ComputedStyle

if TYPE_CHECKING:
    from aspose_html.dom._document import Document
    from aspose_html.dom._element import Element


def computed_style(element: "Element") -> ComputedStyle:
    """Return the cached :class:`ComputedStyle` for *element*.

    Resolution rules:

    - **No owner document (orphan element):** produce a fresh
      ``ComputedStyle`` directly from the cascade engine with ``epoch == 0``
      and do **not** cache it (there is no document to own the cache).
    - **With an owner document:** look the element up in the document's
      per-document cache by ``id(element)``. On a hit return the same
      ``ComputedStyle`` object (identity preserved); on a miss resolve via
      ``_cascade.get_computed_style``, wrap it at the document's current
      ``_style_epoch``, cache it, and return it.

    Because :meth:`Document._bump_style_epoch` clears the cache, a call
    after a bump misses and yields a fresh snapshot carrying the new
    epoch.

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> from aspose_html.dom import Document
    >>> from aspose_html.layout import computed_style
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> doc.append_child(el)
    <Element 'DIV'>
    >>> sheet = CSSStyleSheet()
    >>> sheet.replace_sync("div { color: red }")
    >>> doc.attach_style_sheet(sheet)
    >>> computed_style(el) is computed_style(el)   # cached identity
    True
    >>> first = computed_style(el)
    >>> doc._bump_style_epoch()
    >>> second = computed_style(el)
    >>> second is first                        # fresh after invalidation
    False
    >>> second.epoch > first.epoch
    True

    An orphan element resolves uncached at epoch 0:

    >>> orphan = Document().create_element("span")
    >>> computed_style(orphan).epoch
    0
    """
    from aspose_html.dom._cascade import get_computed_style  # noqa: PLC0415

    doc: "Document | None" = element.owner_document
    if doc is None:
        return ComputedStyle(get_computed_style(element), 0)

    cache = doc._style_cache
    key = id(element)
    cached = cache.get(key)
    if cached is not None:
        return cached

    style = ComputedStyle(get_computed_style(element), doc._style_epoch)
    cache[key] = style
    return style


def bump_style_epoch(document: "Document") -> None:
    """Invalidate *document*'s style cache by bumping its epoch.

    Thin internal-package re-export delegating to
    :meth:`Document._bump_style_epoch`, so DOM hook sites that already
    hold a ``Document`` can invalidate through the layout package surface
    without reaching into a private method name. Equivalent to calling
    ``document._bump_style_epoch()`` directly.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> from aspose_html.layout import bump_style_epoch
    >>> doc = Document()
    >>> doc._style_epoch
    0
    >>> bump_style_epoch(doc)
    >>> doc._style_epoch
    1
    """
    document._bump_style_epoch()
