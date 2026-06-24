"""Normal-flow block layout (M7.3 / CSS 2.2 §10.3.3 subset)."""
from __future__ import annotations

from dataclasses import dataclass

from ._box_tree import BoxNode, BoxRoot
from ._fragment_tree import BlockFragment, EdgeSizes, FragmentRoot


@dataclass(slots=True)
class _Frame:
    box: BoxNode
    parent: list[BlockFragment]
    x: float
    y: float
    containing_width: float
    entered: bool = False
    used_width: float = 0.0
    margin: EdgeSizes = EdgeSizes()
    padding: EdgeSizes = EdgeSizes()
    border: EdgeSizes = EdgeSizes()
    content_x: float = 0.0
    content_y: float = 0.0
    cursor_y: float = 0.0
    child_idx: int = 0
    block_children: tuple[BoxNode, ...] = ()
    child_frags: list[BlockFragment] | None = None


def _parse_px(raw: str) -> float | None:
    s = (raw or "").strip().lower()
    if not s:
        return 0.0
    if s == "auto":
        return None
    if s.endswith("px"):
        try:
            return float(s[:-2])
        except ValueError:
            return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _edge(style: object, prefix: str) -> EdgeSizes:
    get = getattr(style, "get", None)
    if get is None:
        return EdgeSizes()
    return EdgeSizes(
        top=float(_parse_px(get(f"{prefix}-top")) or 0.0),
        right=float(_parse_px(get(f"{prefix}-right")) or 0.0),
        bottom=float(_parse_px(get(f"{prefix}-bottom")) or 0.0),
        left=float(_parse_px(get(f"{prefix}-left")) or 0.0),
    )


def _resolve_used_width(box: BoxNode, containing_width: float) -> tuple[float, EdgeSizes, EdgeSizes, EdgeSizes]:
    style = box.style
    margin = _edge(style, "margin")
    padding = _edge(style, "padding")
    border = _edge(style, "border")

    if style is None:
        return containing_width, margin, padding, border

    width_raw = style.get("width")
    width = _parse_px(width_raw)
    ml = _parse_px(style.get("margin-left"))
    mr = _parse_px(style.get("margin-right"))
    pl = padding.left
    pr = padding.right
    bl = border.left
    br = border.right

    if ml is None:
        ml = 0.0
    if mr is None:
        mr = 0.0

    horizontal_non_content = ml + mr + pl + pr + bl + br
    available_for_content = max(0.0, containing_width - horizontal_non_content)

    if width is None:
        used_width = available_for_content
    else:
        used_width = max(0.0, width)

    # §10.3.3 centering case: both margins auto and width specified.
    if _parse_px(style.get("margin-left")) is None and _parse_px(style.get("margin-right")) is None and width is not None:
        remaining = containing_width - (used_width + pl + pr + bl + br)
        if remaining >= 0:
            ml = mr = remaining / 2.0
        else:
            ml = 0.0
            mr = remaining

    margin = EdgeSizes(top=margin.top, right=float(mr), bottom=margin.bottom, left=float(ml))
    return used_width, margin, padding, border


def layout_block_tree(box_root: BoxRoot, containing_block_width: float) -> FragmentRoot:
    """Lay out block-level normal-flow boxes into immutable fragments."""
    root_children: list[BlockFragment] = []
    stack: list[_Frame] = []

    cursor_y = 0.0
    for box in box_root.children:
        if box.outer_display != "block":
            continue
        stack.append(_Frame(box=box, parent=root_children, x=0.0, y=cursor_y, containing_width=containing_block_width))

        while stack:
            st = stack[-1]
            if not st.entered:
                used_width, margin, padding, border = _resolve_used_width(st.box, st.containing_width)
                st.entered = True
                st.used_width = used_width
                st.margin = margin
                st.padding = padding
                st.border = border
                st.content_x = st.x + margin.left + border.left + padding.left
                st.content_y = st.y + margin.top + border.top + padding.top
                st.cursor_y = st.content_y
                st.block_children = tuple(c for c in st.box.children if c.outer_display == "block")
                st.child_frags = []

            if st.child_idx < len(st.block_children):
                child = st.block_children[st.child_idx]
                st.child_idx += 1
                stack.append(
                    _Frame(
                        box=child,
                        parent=st.child_frags if st.child_frags is not None else [],
                        x=st.content_x,
                        y=st.cursor_y,
                        containing_width=st.used_width,
                    )
                )
                continue

            stack.pop()
            children = tuple(st.child_frags or [])
            if children:
                content_height = sum(c.height for c in children)
            else:
                h = _parse_px(st.box.style.get("height") if st.box.style else "")
                content_height = float(h or 0.0)

            total_height = (
                content_height
                + st.padding.top
                + st.padding.bottom
                + st.border.top
                + st.border.bottom
                + st.margin.top
                + st.margin.bottom
            )
            frag = BlockFragment(
                source_node=st.box.source_node,
                children=children,
                x=st.content_x,
                y=st.content_y,
                width=st.used_width,
                height=total_height,
                margin=st.margin,
                padding=st.padding,
                border=st.border,
                is_anonymous=st.box.is_anonymous,
            )
            st.parent.append(frag)
            if stack:
                parent = stack[-1]
                parent.cursor_y += frag.height

        if root_children:
            last = root_children[-1]
            cursor_y = last.y + last.height

    return FragmentRoot(children=tuple(root_children))
