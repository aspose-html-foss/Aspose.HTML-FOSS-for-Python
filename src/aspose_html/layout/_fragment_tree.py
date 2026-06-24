"""Fragment-tree records for layout pipeline output (M7.3).

The fragment tree is the geometry-bearing output of layout stages. Records are
frozen dataclasses with slots so they remain immutable and process-picklable for
later page-parallel rendering work.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom import Node


@dataclass(frozen=True, slots=True)
class EdgeSizes:
    """Logical edge sizes in CSS px units."""

    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    left: float = 0.0


@dataclass(frozen=True, slots=True)
class BlockFragment:
    """Geometry fragment for a block-level box."""

    source_node: Node | None
    children: tuple["BlockFragment", ...]
    x: float
    y: float
    width: float
    height: float
    margin: EdgeSizes
    padding: EdgeSizes
    border: EdgeSizes
    line_fragments: tuple["LineFragment", ...] = ()
    is_anonymous: bool = False


@dataclass(frozen=True, slots=True)
class FragmentRoot:
    """Root wrapper for block-layout fragment output."""

    children: tuple[BlockFragment, ...]


@dataclass(frozen=True, slots=True)
class ShapedRun:
    """Shaped text-run payload with deterministic metrics."""

    text: str
    advance: float
    ascent: float
    descent: float


@dataclass(frozen=True, slots=True)
class InlineTextFragment:
    """Positioned inline text fragment for a single shaped run."""

    run: ShapedRun
    x: float
    y: float
    width: float
    height: float
    baseline: float


@dataclass(frozen=True, slots=True)
class LineFragment:
    """Single inline formatting context line box."""

    runs: tuple[InlineTextFragment, ...]
    x: float
    y: float
    width: float
    height: float
    baseline: float


@dataclass(frozen=True, slots=True)
class PageMarginBoxes:
    """Placeholder page-margin-box container for later paint stages."""

    top: tuple[BlockFragment, ...] = ()
    right: tuple[BlockFragment, ...] = ()
    bottom: tuple[BlockFragment, ...] = ()
    left: tuple[BlockFragment, ...] = ()


@dataclass(frozen=True, slots=True)
class PageFragment:
    """Single paginated fragmentainer (page box) with ordered content."""

    page_index: int
    x: float
    y: float
    width: float
    height: float
    children: tuple[BlockFragment, ...]
    margin_boxes: PageMarginBoxes = PageMarginBoxes()
