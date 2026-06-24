"""Inline formatting context layout + text shaping (M7.4)."""
from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from aspose_html.dom import NodeType

from ._box_tree import classify_display
from ._fragment_tree import BlockFragment, FragmentRoot, InlineTextFragment, LineFragment, ShapedRun
from ._style_cache import computed_style

if TYPE_CHECKING:
    from aspose_html.dom import Node
    from ._computed_style import ComputedStyle


def _normalize_whitespace(text: str, white_space: str) -> tuple[str, ...]:
    if not text:
        return ()
    ws = (white_space or "normal").strip().lower()
    if ws in ("pre", "pre-wrap"):
        return tuple(text.split("\n"))

    collapsed: list[str] = []
    pending_space = False
    for ch in text:
        if ch.isspace():
            pending_space = True
            continue
        if pending_space and collapsed:
            collapsed.append(" ")
        pending_space = False
        collapsed.append(ch)
    normalized = "".join(collapsed).strip()
    return (normalized,) if normalized else ()


def _shape_run(text: str, style: ComputedStyle) -> ShapedRun:
    del style
    if not text:
        return ShapedRun(text="", advance=0.0, ascent=0.0, descent=0.0)
    try:
        import skia  # type: ignore

        font = skia.Font(None, 12)
        width = float(font.measureText(text))
        metrics = font.getMetrics()
        ascent = float(abs(getattr(metrics, "fAscent", 0.0)))
        descent = float(getattr(metrics, "fDescent", 0.0))
        return ShapedRun(text=text, advance=width, ascent=ascent, descent=descent)
    except Exception:
        # Deterministic fallback when Skia shaping is unavailable: keep payload
        # but avoid custom glyph-width heuristics.
        return ShapedRun(text=text, advance=0.0, ascent=0.0, descent=0.0)


def _break_lines(runs: tuple[ShapedRun, ...], width: float) -> tuple[LineFragment, ...]:
    lines: list[LineFragment] = []
    current: list[InlineTextFragment] = []
    cursor_x = 0.0
    cursor_y = 0.0
    line_height = 0.0
    line_baseline = 0.0

    for run in runs:
        forced_break = run.text == "\n"
        if forced_break:
            lines.append(
                LineFragment(
                    runs=tuple(current),
                    x=0.0,
                    y=cursor_y,
                    width=cursor_x,
                    height=line_height,
                    baseline=line_baseline,
                )
            )
            cursor_y += line_height
            current = []
            cursor_x = 0.0
            line_height = 0.0
            line_baseline = 0.0
            continue

        if current and cursor_x + run.advance > width:
            lines.append(
                LineFragment(
                    runs=tuple(current),
                    x=0.0,
                    y=cursor_y,
                    width=cursor_x,
                    height=line_height,
                    baseline=line_baseline,
                )
            )
            cursor_y += line_height
            current = []
            cursor_x = 0.0
            line_height = 0.0
            line_baseline = 0.0

        frag = InlineTextFragment(
            run=run,
            x=cursor_x,
            y=cursor_y,
            width=run.advance,
            height=run.ascent + run.descent,
            baseline=run.ascent,
        )
        current.append(frag)
        cursor_x += run.advance
        line_height = max(line_height, frag.height)
        line_baseline = max(line_baseline, frag.baseline)

    if current or not lines:
        lines.append(
            LineFragment(
                runs=tuple(current),
                x=0.0,
                y=cursor_y,
                width=cursor_x,
                height=line_height,
                baseline=line_baseline,
            )
        )
    return tuple(lines)


def _collect_inline_text(node: Node | None) -> str:
    if node is None:
        return ""
    chunks: list[str] = []
    stack: list[Node] = list(reversed(node.child_nodes))
    while stack:
        cur = stack.pop()
        if cur.node_type == NodeType.TEXT_NODE:
            if cur.node_value:
                chunks.append(cur.node_value)
            continue
        if cur.node_type != NodeType.ELEMENT_NODE:
            children = cur.child_nodes
            for i in range(len(children) - 1, -1, -1):
                stack.append(children[i])
            continue
        style = computed_style(cur)
        display = classify_display(style.get("display"))
        if display.generates == "none" or display.outer in ("block", "run-in"):
            continue
        children = cur.child_nodes
        for i in range(len(children) - 1, -1, -1):
            stack.append(children[i])
    return "".join(chunks)


def _layout_block_inline(fragment: BlockFragment, available_width: float) -> BlockFragment:
    children: list[BlockFragment] = []
    for child in fragment.children:
        children.append(_layout_block_inline(child, child.width if child.width > 0 else available_width))

    white_space = "normal"
    if fragment.source_node is not None and fragment.source_node.node_type == NodeType.ELEMENT_NODE:
        white_space = computed_style(fragment.source_node).get("white-space") or "normal"
    text = _collect_inline_text(fragment.source_node)
    normalized_parts = _normalize_whitespace(text, white_space)

    runs: list[ShapedRun] = []
    source_style = computed_style(fragment.source_node) if fragment.source_node is not None and fragment.source_node.node_type == NodeType.ELEMENT_NODE else None
    for idx, part in enumerate(normalized_parts):
        if source_style is not None and part:
            runs.append(_shape_run(part, source_style))
        if white_space in ("pre", "pre-wrap") and idx != len(normalized_parts) - 1:
            runs.append(ShapedRun(text="\n", advance=0.0, ascent=0.0, descent=0.0))

    line_fragments = _break_lines(tuple(runs), fragment.width if fragment.width > 0 else available_width)
    return replace(fragment, children=tuple(children), line_fragments=line_fragments)


def layout_inline_fragments(root: FragmentRoot, available_width: float) -> FragmentRoot:
    """Augment block fragments with line/text fragments.

    Returns a new fragment tree; input records remain unchanged.
    """
    return FragmentRoot(
        children=tuple(_layout_block_inline(child, child.width if child.width > 0 else available_width) for child in root.children)
    )
