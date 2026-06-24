"""Layout engine package — M7 ( architecture baseline).

This package hosts the box-tree, style cache, block/inline layout, and
fragmentation machinery that turn a styled DOM into paginated output.
M7.1 ( / ) lands the first piece: the cached-style
substrate every subsequent M7 track consumes.

The M7 cache contract
---------------------

The existing ``aspose_html.dom._cascade`` engine remains the single
**producer** of resolved style. This package adds a layout-facing
**cache**, not a second cascade:

- :class:`ComputedStyle` is an immutable, read-only snapshot wrapping the
  ``ComputedStyleDeclaration`` the cascade engine already produces, plus
  the ``Document._style_epoch`` at which it was produced.
- :func:`computed_style` returns a cached ``ComputedStyle`` for an element,
  resolving on a miss through the cascade engine and caching the result
  on the owning ``Document`` instance keyed by ``id(element)``.
- :func:`bump_style_epoch` invalidates a document's cache by bumping its
  epoch; the cache is cleared lazily and rebuilt on the next read.

Two milestone-wide disciplines bind every module under this package:

- **** — DOM/box-tree traversals use explicit-stack iteration,
  never recursion. (M7.1 itself performs no tree walk; the cache lookup
  consults a flat ``id``-keyed dict.)
- **** — no module-level mutable state. All per-render state
  lives on the ``Document`` instance or on an explicit per-render-job
  object, so the M7.6 ``ProcessPoolExecutor`` page-parallel model stays
  reachable.

All three symbols below are internal-package surface; they are **not**
re-exported from ``aspose_html.dom`` and do not change the public CSSOM
surface ().
"""
from __future__ import annotations

from ._box_tree import (
    BoxNode,
    BoxRoot,
    Display,
    build_box_tree,
    classify_display,
)
from ._block import layout_block_tree
from ._computed_style import ComputedStyle
from ._fragment_tree import (
    BlockFragment,
    EdgeSizes,
    FragmentRoot,
    InlineTextFragment,
    LineFragment,
    PageFragment,
    PageMarginBoxes,
    ShapedRun,
)
from ._inline import layout_inline_fragments
from ._pagination import paginate_fragments
from ._style_cache import bump_style_epoch, computed_style

__all__ = [
    "ComputedStyle",
    "computed_style",
    "bump_style_epoch",
    "BoxNode",
    "BoxRoot",
    "Display",
    "build_box_tree",
    "classify_display",
    "EdgeSizes",
    "BlockFragment",
    "FragmentRoot",
    "layout_block_tree",
    "ShapedRun",
    "InlineTextFragment",
    "LineFragment",
    "layout_inline_fragments",
    "PageMarginBoxes",
    "PageFragment",
    "paginate_fragments",
]
