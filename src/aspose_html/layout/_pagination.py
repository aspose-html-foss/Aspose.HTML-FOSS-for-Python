"""Pagination of block/inline fragments into page fragments (M7.5)."""
from __future__ import annotations

from dataclasses import dataclass, replace

from aspose_html.dom import NodeType

from ._fragment_tree import BlockFragment, FragmentRoot, LineFragment, PageFragment, PageMarginBoxes
from ._style_cache import computed_style


@dataclass(frozen=True, slots=True)
class BreakHints:
    break_before: str
    break_after: str
    break_inside: str
    widows: int
    orphans: int


def _parse_int(raw: str, default: int) -> int:
    try:
        value = int((raw or "").strip())
    except ValueError:
        return default
    return value if value > 0 else default


def _collect_break_hints(fragment: BlockFragment) -> BreakHints:
    node = fragment.source_node
    if node is None or node.node_type != NodeType.ELEMENT_NODE:
        return BreakHints("auto", "auto", "auto", 2, 2)
    style = computed_style(node)
    before = (style.get("break-before") or "auto").strip().lower()
    after = (style.get("break-after") or "auto").strip().lower()
    inside = (style.get("break-inside") or "auto").strip().lower()
    widows = _parse_int(style.get("widows") or "", 2)
    orphans = _parse_int(style.get("orphans") or "", 2)
    return BreakHints(before, after, inside, widows, orphans)


def _is_forced_break(value: str) -> bool:
    return value in {"page", "left", "right", "recto", "verso", "always"}


def _line_total_height(lines: tuple[LineFragment, ...]) -> float:
    return sum(line.height for line in lines)


def _with_lines(fragment: BlockFragment, lines: tuple[LineFragment, ...]) -> BlockFragment:
    return replace(fragment, line_fragments=lines, height=_line_total_height(lines))


def _apply_widows_orphans(
    lines: tuple[LineFragment, ...],
    remaining_height: float,
    widows: int,
    orphans: int,
) -> tuple[tuple[LineFragment, ...], tuple[LineFragment, ...]]:
    if len(lines) < 2:
        return (), lines
    used = 0.0
    fit = 0
    for line in lines:
        if fit > 0 and used + line.height > remaining_height:
            break
        if fit == 0 and line.height > remaining_height:
            break
        used += line.height
        fit += 1
    if fit == 0:
        return (), lines
    if fit < orphans:
        return (), lines
    tail = len(lines) - fit
    if tail < widows:
        fit = len(lines) - widows
    if fit < orphans or fit <= 0:
        return (), lines
    return lines[:fit], lines[fit:]


def paginate_fragments(root: FragmentRoot, page_width: float, page_height: float) -> tuple[PageFragment, ...]:
    """Paginate block fragments into ordered immutable page fragments."""
    if page_width <= 0 or page_height <= 0:
        raise ValueError("page_width and page_height must be positive")

    pages: list[PageFragment] = []
    current_children: list[BlockFragment] = []
    current_height = 0.0

    def flush_page() -> None:
        nonlocal current_children, current_height
        if not current_children and pages:
            return
        pages.append(
            PageFragment(
                page_index=len(pages),
                x=0.0,
                y=0.0,
                width=page_width,
                height=page_height,
                children=tuple(current_children),
                margin_boxes=PageMarginBoxes(),
            )
        )
        current_children = []
        current_height = 0.0

    queue: list[BlockFragment] = list(root.children)
    idx = 0
    while idx < len(queue):
        fragment = queue[idx]
        idx += 1
        hints = _collect_break_hints(fragment)

        if _is_forced_break(hints.break_before) and current_children:
            flush_page()

        remaining = page_height - current_height
        frag_height = fragment.height
        avoid_inside = hints.break_inside in {"avoid", "avoid-page"}

        if frag_height > remaining and current_children and avoid_inside and frag_height <= page_height:
            flush_page()
            remaining = page_height

        if fragment.line_fragments and frag_height > remaining and remaining > 0:
            head, tail = _apply_widows_orphans(fragment.line_fragments, remaining, hints.widows, hints.orphans)
            if head:
                top = _with_lines(fragment, head)
                bottom = _with_lines(fragment, tail)
                current_children.append(top)
                current_height += top.height
                flush_page()
                queue.insert(idx, bottom)
                continue
            if current_children:
                flush_page()
                remaining = page_height

        current_children.append(fragment)
        current_height += fragment.height

        if _is_forced_break(hints.break_after):
            flush_page()

    flush_page()
    return tuple(pages)
