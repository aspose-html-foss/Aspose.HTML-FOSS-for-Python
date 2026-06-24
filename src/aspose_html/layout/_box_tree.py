"""DOM → layout box-tree projection (M7.2 /  /  amended).

This module builds a deterministic, layout-facing box tree from a DOM
document. Scope is structural only: the orthogonal display triple
``(outer_display, inner_display, replaced)`` per CSS Display Level 3 §2,
``display: none`` pruning, ``display: contents`` hoist, anonymous block-in-
inline wrapping (CSS 2.2 §9.2.1.1), and source-node back-references.
Geometry/line-breaking/pagination/paint are out of scope.

The display classifier (:func:`classify_display`) transcribes the verbatim
rules from CSS Display L3 §2.1 / §2.2 / §2.5 / §2.6 — no substring
heuristics, no silent block-coercion (). All classifier tables are
module-level immutable constants (); the tree walk uses an explicit
stack ().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Literal, Mapping

from aspose_html.dom import NodeType

from ._style_cache import computed_style

if TYPE_CHECKING:
    from aspose_html.dom import Document, Element, Node
    from ._computed_style import ComputedStyle

# --- display value types (CSS Display L3 §2) -----------------------------

Outer = Literal["block", "inline", "run-in"]
Inner = Literal["flow", "flow-root", "table", "flex", "grid", "ruby"]
Generation = Literal["box", "none", "contents"]


@dataclass(frozen=True, slots=True)
class Display:
    """Resolved display triple per CSS Display L3 §2.

    Attributes
    ----------
    outer:
        The outer display role per §2.1: ``block``, ``inline``, or
        ``run-in``. ``None`` when the element generates no box
        (``generates != "box"``).
    inner:
        The inner formatting context per §2.2: ``flow``, ``flow-root``,
        ``table``, ``flex``, ``grid``, ``ruby``. ``None`` when the
        element generates no box, when it is a replaced element (§2.2:
        "The inner display of a replaced element is outside the scope
        of CSS"), or when it carries a layout-internal display value
        (``<display-internal>``, §2.4).
    generates:
        Whether the element generates a principal box (§2.5): ``box``,
        ``none``, or ``contents``.
    list_item:
        ``True`` when the resolved value carried the ``list-item`` flag
        per §2.3. Recorded only — the ``::marker`` pseudo-box is a
        follow-up slice.
    layout_internal:
        Raw ``<display-internal>`` token (``table-row``, ``table-cell``,
        ``ruby-base``, …) when the resolved value is layout-internal
        per §2.4; ``None`` otherwise. Recorded only — the per-FC
        modules (M7.4+) apply the §2.4 / §2.7 fixups.
    """

    outer: Outer | None
    inner: Inner | None
    generates: Generation
    list_item: bool
    layout_internal: str | None


# --- classifier tables (module-level constants — ) ----------------

#: §2.6 — Precomposed Inline-level Display Values (legacy). Each maps to
#: ``(outer, inner)`` verbatim per the spec.
_DISPLAY_LEGACY: Mapping[str, tuple[Outer, Inner]] = MappingProxyType(
    {
        "inline-block": ("inline", "flow-root"),
        "inline-table": ("inline", "table"),
        "inline-flex": ("inline", "flex"),
        "inline-grid": ("inline", "grid"),
    }
)

#: §2.4 — Layout-Internal Display Types. The classifier passes these
#: through on the ``layout_internal`` channel; M7.4+ FC modules apply the
#: §2.4 automatic-table / ruby wrapper insertion when assembling each
#: formatting context.
_DISPLAY_INTERNAL: frozenset[str] = frozenset(
    {
        "table-row-group",
        "table-header-group",
        "table-footer-group",
        "table-row",
        "table-cell",
        "table-column-group",
        "table-column",
        "table-caption",
        "ruby-base",
        "ruby-text",
        "ruby-base-container",
        "ruby-text-container",
    }
)

#: §2.1 — ``<display-outside>`` keywords.
_OUTER_KEYWORDS: frozenset[str] = frozenset({"block", "inline", "run-in"})

#: §2.2 — ``<display-inside>`` keywords.
_INNER_KEYWORDS: frozenset[str] = frozenset(
    {"flow", "flow-root", "table", "flex", "grid", "ruby"}
)

#: HTML replaced elements producing a replaced box (FR-5 / HI-5). Outer
#: display comes from the cascade; inner display is N/A per §2.2.
_REPLACED_TAGS: frozenset[str] = frozenset(
    {"img", "canvas", "video", "iframe", "object", "embed"}
)

#: §2 propdef Initial: ``inline``. Returned for unknown values — never
#: silently coerced to ``block`` (the substring-heuristic bug).
_INITIAL_DISPLAY: Display = Display(
    outer="inline",
    inner="flow",
    generates="box",
    list_item=False,
    layout_internal=None,
)


# --- classifier (CSS Display L3 §2 — verbatim mapping) -------------------


def classify_display(value: str) -> Display:
    """Classify a resolved-display string per CSS Display L3 §2.

    Pure function. Maps the cascade-engine output to the orthogonal
    triple ``(outer, inner, generates)`` per §2.1 / §2.2 / §2.5 / §2.6,
    plus the optional ``list-item`` flag (§2.3) and layout-internal
    token passthrough (§2.4). Unknown values resolve to the §2 initial
    value (``inline flow``) — NEVER silently coerced to ``block``.

    Examples
    --------
    >>> classify_display("block")
    Display(outer='block', inner='flow', generates='box', list_item=False, layout_internal=None)
    >>> classify_display("inline-block")
    Display(outer='inline', inner='flow-root', generates='box', list_item=False, layout_internal=None)
    >>> classify_display("none")
    Display(outer=None, inner=None, generates='none', list_item=False, layout_internal=None)
    >>> classify_display("contents")
    Display(outer=None, inner=None, generates='contents', list_item=False, layout_internal=None)
    >>> classify_display("table-cell")
    Display(outer=None, inner=None, generates='box', list_item=False, layout_internal='table-cell')
    >>> classify_display("ruby")  # outer defaults to inline per §2.2
    Display(outer='inline', inner='ruby', generates='box', list_item=False, layout_internal=None)
    >>> classify_display("weird-value")  # unknown → §2 initial value
    Display(outer='inline', inner='flow', generates='box', list_item=False, layout_internal=None)
    """
    s = value.strip().lower()

    # §2.5 — Box Generation. Both `none` and `contents` elements have no
    # outer/inner display type (§2.5 last paragraph).
    if s == "none":
        return Display(
            outer=None, inner=None, generates="none", list_item=False, layout_internal=None
        )
    if s == "contents":
        return Display(
            outer=None, inner=None, generates="contents", list_item=False, layout_internal=None
        )

    # §2.6 — Precomposed Inline-level Display Values (legacy). Verbatim
    # "Computes to" mappings — see _DISPLAY_LEGACY.
    if s in _DISPLAY_LEGACY:
        outer_legacy, inner_legacy = _DISPLAY_LEGACY[s]
        return Display(
            outer=outer_legacy,
            inner=inner_legacy,
            generates="box",
            list_item=False,
            layout_internal=None,
        )

    # §2.4 — Layout-Internal Display Types. Classifier records the value;
    # the per-FC layout modules in M7.4+ apply the automatic-table /
    # ruby fixups.
    if s in _DISPLAY_INTERNAL:
        return Display(
            outer=None,
            inner=None,
            generates="box",
            list_item=False,
            layout_internal=s,
        )

    # §2.3 — list-item flag. Grammar:
    #     <display-outside>? && [ flow | flow-root ]? && list-item
    tokens = s.split()
    has_list_item = "list-item" in tokens
    if has_list_item:
        tokens = [t for t in tokens if t != "list-item"]

    # Empty input (or pure whitespace) is not a valid <display> value;
    # fall back to the §2 propdef "Initial: inline". Pure `list-item`
    # falls through to the (None, None) default path below per §2.3.
    if not tokens and not has_list_item:
        return _INITIAL_DISPLAY

    # Resolve outer / inner per §2.1 / §2.2 grammar over the remaining
    # tokens.
    outer_token: Outer | None = None
    inner_token: Inner | None = None
    for t in tokens:
        if t in _OUTER_KEYWORDS:
            outer_token = t  # type: ignore[assignment]
        elif t in _INNER_KEYWORDS:
            inner_token = t  # type: ignore[assignment]
        else:
            # Unknown keyword → §2 initial value. NEVER silently coerce
            # to block — that was the substring-heuristic bug (
            # Phase 2).
            return _INITIAL_DISPLAY

    if outer_token is None and inner_token is None:
        # Only list-item was present. Per §2.3 the principal box's
        # outer defaults to block and inner defaults to flow.
        outer_token, inner_token = "block", "flow"
    elif outer_token is not None and inner_token is None:
        # §2.1 — "If a <display-outside> value is specified but
        # <display-inside> is omitted, the element's inner display
        # type defaults to flow."
        inner_token = "flow"
    elif outer_token is None and inner_token is not None:
        # §2.2 — "If a <display-inside> value is specified but
        # <display-outside> is omitted, the element's outer display
        # type defaults to block — except for ruby, which defaults to
        # inline."
        outer_token = "inline" if inner_token == "ruby" else "block"

    return Display(
        outer=outer_token,
        inner=inner_token,
        generates="box",
        list_item=has_list_item,
        layout_internal=None,
    )


# --- box-tree records (FR-1 — orthogonal triple, no `kind` literal) ------


@dataclass(slots=True)
class BoxNode:
    """Single box-tree node produced by :func:`build_box_tree`.

    Carries the orthogonal display triple per CSS Display L3 §2
    (FR-1):

    - ``outer_display`` — ``block``/``inline``/``run-in`` per §2.1. The
      anonymous wrappers from CSS 2.2 §9.2.1.1 are created with
      ``outer_display="block"``. Text sequences carry ``"inline"``.
    - ``inner_display`` — formatting context per §2.2. ``None`` for
      replaced boxes (§2.2 "The inner display of a replaced element is
      outside the scope of CSS"), for anonymous wrappers (synthesised
      flow blocks; ``inner_display="flow"``), and for text sequences.
    - ``replaced`` — orthogonal flag from the element tag (HI-5).
    - ``source_node`` — back-reference to the DOM node; ``None`` for
      anonymous wrappers. The ``display: contents`` hoist preserves
      descendant ``source_node`` identity (HI-3).
    - ``is_anonymous`` — ``True`` iff this box has no source node.
    """

    outer_display: Outer | None
    inner_display: Inner | None
    replaced: bool
    source_node: "Node | None"
    children: list["BoxNode"] = field(default_factory=list)
    style: "ComputedStyle | None" = None
    text: str = ""
    is_anonymous: bool = False


@dataclass(slots=True)
class BoxRoot:
    """Root wrapper returned by :func:`build_box_tree`."""

    source_node: "Document"
    children: list[BoxNode] = field(default_factory=list)


def _make_text_box(node: "Node", data: str) -> BoxNode:
    """Build an inline text-sequence box.

    Text sequences carry ``outer_display="inline"`` so the block-in-
    inline anonymous-wrapper rule treats them as inline-level (FR-6).
    """
    return BoxNode(
        outer_display="inline",
        inner_display=None,
        replaced=False,
        source_node=node,
        children=[],
        style=None,
        text=data,
        is_anonymous=False,
    )


def _is_block_level(child: BoxNode) -> bool:
    """True when *child* is block-level for §9.2.1.1 wrapper insertion.

    FR-6: trigger on ``outer_display``, not on the deleted ``kind``
    literal. Anonymous wrappers built by this module are themselves
    block-level by construction.
    """
    if child.is_anonymous:
        return child.outer_display == "block"
    return child.outer_display in ("block", "run-in")


def _is_inline_level(child: BoxNode) -> bool:
    """True when *child* is inline-level for §9.2.1.1 wrapper insertion."""
    return child.outer_display == "inline" and not _is_block_level(child)


def _normalize_anonymous_wrappers(box: BoxNode) -> None:
    """Apply CSS 2.2 §9.2.1.1 block-in-inline wrapping to *box*'s children.

    When the box has at least one block-level and at least one inline-
    level child, consecutive runs of inline-level children are wrapped
    in an anonymous block box. The trigger is ``outer_display``, not
    the deleted ``kind`` literal (FR-6).
    """
    # Only block-level containers may host anonymous block wrappers.
    # Inline parents never own anonymous block siblings — their
    # block-level children trigger block-in-inline splitting in the
    # IFC, which is M7.4's job.
    if box.outer_display != "block" and not box.is_anonymous:
        return
    if len(box.children) < 2:
        return

    has_block = any(_is_block_level(c) for c in box.children)
    has_inline = any(_is_inline_level(c) for c in box.children)
    if not (has_block and has_inline):
        return

    normalized: list[BoxNode] = []
    inline_run: list[BoxNode] = []

    def flush_inline_run() -> None:
        if not inline_run:
            return
        anon = BoxNode(
            outer_display="block",
            inner_display="flow",
            replaced=False,
            source_node=None,
            children=list(inline_run),
            style=None,
            text="",
            is_anonymous=True,
        )
        normalized.append(anon)
        inline_run.clear()

    for child in box.children:
        if _is_inline_level(child):
            inline_run.append(child)
        else:
            flush_inline_run()
            normalized.append(child)
    flush_inline_run()
    box.children = normalized


def build_box_tree(document: "Document") -> BoxRoot:
    """Build and return the M7.2 structural box tree for *document*.

    Uses explicit-stack traversal only (). Applies the CSS
    Display L3 §2 classifier (FR-2), the ``display: none`` prune
    (FR-3, §2.5 "none"), the ``display: contents`` hoist (FR-4, §2.5
    "contents" with HI-3 source-node preservation + HI-4 replaced
    elision), and post-order CSS 2.2 §9.2.1.1 anonymous-wrapper
    normalisation (FR-6).
    """
    root = BoxRoot(source_node=document)
    # Stack frames are (node, parent_box, exiting).
    # `exiting` sentinel frames trigger _normalize_anonymous_wrappers
    # on the parent box after all its children are processed.
    stack: list[tuple["Node", BoxRoot | BoxNode, bool]] = [(document, root, False)]

    while stack:
        node, parent_box, exiting = stack.pop()

        if exiting:
            # Post-order normalisation on the parent box. The sentinel
            # is also used by `display: contents` frames where there
            # is no box of our own — in that case parent_box is the
            # hoist target and normalisation is already its
            # responsibility (it gets its own exit frame).
            if isinstance(parent_box, BoxNode):
                _normalize_anonymous_wrappers(parent_box)
            continue

        node_type = node.node_type
        if node_type == NodeType.TEXT_NODE:
            # Text sequences inherit display:none from the ancestor
            # chain: the parent element with display:none never pushes
            # its children onto the stack (FR-3).
            data = node.node_value or ""
            if data:
                parent_box.children.append(_make_text_box(node, data))
            continue

        if node_type == NodeType.ELEMENT_NODE:
            element = node  # type: ignore[assignment]
            style = computed_style(element)
            display = classify_display(style.get("display"))
            replaced = element.local_name.lower() in _REPLACED_TAGS

            # §2.5 "contents" on a replaced element computes to
            # `display: none` (HI-4). Elide the subtree.
            if display.generates == "contents" and replaced:
                continue

            # §2.5 "none": elide element and entire subtree (FR-3).
            if display.generates == "none":
                continue

            # §2.5 "contents": elide the element's own box; hoist
            # children into parent in document order. source_node
            # identity preserved by HI-3.
            if display.generates == "contents":
                children = element.child_nodes
                # Push the children in reverse so document order is
                # restored on pop. No exit frame here — we are not
                # creating a new box, so there is nothing to
                # normalise. The parent's exit frame (already pushed
                # by the caller's loop) handles wrapper normalisation
                # over the full child set after the hoist.
                for i in range(len(children) - 1, -1, -1):
                    stack.append((children[i], parent_box, False))
                continue

            # Build the principal box. For replaced elements §2.2
            # makes inner display N/A.
            inner = None if replaced else display.inner
            box = BoxNode(
                outer_display=display.outer,
                inner_display=inner,
                replaced=replaced,
                source_node=element,
                children=[],
                style=style,
                text="",
                is_anonymous=False,
            )
            parent_box.children.append(box)

            # Replaced subtrees are opaque to box generation — do not
            # descend (replaced elements have no rendered children;
            # they consume the element's intrinsic image / media).
            if not replaced:
                stack.append((element, box, True))
                children = element.child_nodes
                for i in range(len(children) - 1, -1, -1):
                    stack.append((children[i], box, False))
            continue

        # Other node types (Document, DocumentFragment, comment, …):
        # walk children without producing a box of our own.
        children = node.child_nodes
        for i in range(len(children) - 1, -1, -1):
            stack.append((children[i], parent_box, False))

    return root
