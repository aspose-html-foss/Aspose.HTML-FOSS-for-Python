"""Unit tests for the M7.2 box-tree builder ( /  amended).

The tests are split into three groups:

1. ``classify_display`` direct unit tests — every keyword from CSS
   Display L3 §2.1 / §2.2 / §2.5 / §2.6 plus the resolved two-keyword
   pairs (§2 grammar) and the §2.4 layout-internal passthrough.
2. Tree-shape regression tests on the new ``outer_display`` /
   ``inner_display`` / ``replaced`` fields. Intent is unchanged from
   the previous test suite — only the field names move.
3. Phase-2 amendment regressions — the bugs the substring heuristic
   shipped (``inline-block`` bucketed as block, ``display: contents``
   producing a box) get direct, fixture-level coverage.
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.layout import Display, build_box_tree, classify_display


def _attach_styles(doc: Document, css: str) -> None:
    sheet = CSSStyleSheet()
    sheet.replace_sync(css)
    doc.attach_style_sheet(sheet)


# -------------------------------------------------------------------------
# 1. classify_display — direct unit tests over every §2.1 / §2.2 / §2.5
#    / §2.6 keyword. (AC-2)
# -------------------------------------------------------------------------

# (input, expected (outer, inner, generates, list_item, layout_internal))
_CLASSIFIER_CASES: list[tuple[str, tuple]] = [
    # §2.1 — single <display-outside> (inner defaults to flow).
    ("block", ("block", "flow", "box", False, None)),
    ("inline", ("inline", "flow", "box", False, None)),
    ("run-in", ("run-in", "flow", "box", False, None)),
    # §2.2 — single <display-inside> (outer defaults to block, except
    # ruby → inline).
    ("flow", ("block", "flow", "box", False, None)),
    ("flow-root", ("block", "flow-root", "box", False, None)),
    ("table", ("block", "table", "box", False, None)),
    ("flex", ("block", "flex", "box", False, None)),
    ("grid", ("block", "grid", "box", False, None)),
    ("ruby", ("inline", "ruby", "box", False, None)),
    # §2 grammar — resolved two-keyword pairs.
    ("block flow", ("block", "flow", "box", False, None)),
    ("inline flow-root", ("inline", "flow-root", "box", False, None)),
    ("block flex", ("block", "flex", "box", False, None)),
    ("inline flex", ("inline", "flex", "box", False, None)),
    ("block grid", ("block", "grid", "box", False, None)),
    ("inline grid", ("inline", "grid", "box", False, None)),
    ("block table", ("block", "table", "box", False, None)),
    ("inline table", ("inline", "table", "box", False, None)),
    ("inline ruby", ("inline", "ruby", "box", False, None)),
    ("block ruby", ("block", "ruby", "box", False, None)),
    # §2.6 — legacy precomposed inline-level.
    ("inline-block", ("inline", "flow-root", "box", False, None)),
    ("inline-table", ("inline", "table", "box", False, None)),
    ("inline-flex", ("inline", "flex", "box", False, None)),
    ("inline-grid", ("inline", "grid", "box", False, None)),
    # §2.5 — box generation.
    ("none", (None, None, "none", False, None)),
    ("contents", (None, None, "contents", False, None)),
    # §2.3 — list-item flag (recorded, not yet acted on).
    ("list-item", ("block", "flow", "box", True, None)),
    ("inline list-item", ("inline", "flow", "box", True, None)),
    # §2.4 — layout-internal pass-through.
    ("table-cell", (None, None, "box", False, "table-cell")),
    ("table-row", (None, None, "box", False, "table-row")),
    ("ruby-base", (None, None, "box", False, "ruby-base")),
    # Unknown / initial — §2 propdef "Initial: inline" (NEVER coerced
    # to block).
    ("", ("inline", "flow", "box", False, None)),
    ("weird-value", ("inline", "flow", "box", False, None)),
]


@pytest.mark.parametrize("value,expected", _CLASSIFIER_CASES)
def test_classify_display_covers_css_display_l3_section_2(
    value: str, expected: tuple
) -> None:
    """AC-2: every §2.1/§2.2/§2.5/§2.6 keyword maps per the cited spec."""
    d = classify_display(value)
    assert isinstance(d, Display)
    assert (d.outer, d.inner, d.generates, d.list_item, d.layout_internal) == expected


def test_classify_display_case_insensitive_and_whitespace_trimmed() -> None:
    """Resolved values come from the cascade — lowercase/trimmed input still
    classifies."""
    assert classify_display("  Inline-Block  ").outer == "inline"
    assert classify_display("  Inline-Block  ").inner == "flow-root"
    assert classify_display("NONE").generates == "none"


def test_classify_display_unknown_value_yields_initial_not_block() -> None:
    """Phase-2 amendment: the substring heuristic silently coerced unknowns
    to block. The cited classifier returns the §2 initial value (inline flow)."""
    d = classify_display("totally-made-up")
    assert d.outer == "inline"
    assert d.inner == "flow"
    assert d.generates == "box"


# -------------------------------------------------------------------------
# 2. Tree-shape regression — the existing intent on outer_display/
#    inner_display/replaced. (AC-1, AC-3, AC-7, AC-8)
# -------------------------------------------------------------------------


def test_display_none_prunes_entire_subtree() -> None:
    """AC-3 — §2.5 'none' elides element and entire subtree."""
    doc = Document()
    host = doc.create_element("div")
    hidden = doc.create_element("span")
    hidden.append_child(doc.create_text_node("secret"))
    host.append_child(hidden)
    host.append_child(doc.create_text_node("visible"))
    doc.append_child(host)
    _attach_styles(doc, "div { display:block } span { display:none }")

    tree = build_box_tree(doc)
    children = tree.children[0].children
    # Only one child survives — the visible text. The hidden span and
    # its 'secret' text descendant are pruned entirely.
    assert len(children) == 1
    assert children[0].outer_display == "inline"
    assert children[0].inner_display is None
    assert children[0].text == "visible"


def test_block_hierarchy_deterministic() -> None:
    """AC-1 — block-block-text shape with the new triple fields."""
    doc = Document()
    div = doc.create_element("div")
    p = doc.create_element("p")
    text = doc.create_text_node("hello")
    p.append_child(text)
    div.append_child(p)
    doc.append_child(div)
    _attach_styles(doc, "div, p { display:block }")

    tree = build_box_tree(doc)
    outer = tree.children[0]
    inner = outer.children[0]
    assert (outer.outer_display, outer.inner_display, outer.replaced) == ("block", "flow", False)
    assert (inner.outer_display, inner.inner_display, inner.replaced) == ("block", "flow", False)
    assert inner.children[0].outer_display == "inline"
    assert inner.children[0].text == "hello"


def test_inline_text_order_preserved() -> None:
    """AC-1 — inline run with nested inline child, text order preserved."""
    doc = Document()
    span = doc.create_element("span")
    span.append_child(doc.create_text_node("a"))
    b = doc.create_element("b")
    b.append_child(doc.create_text_node("b"))
    span.append_child(b)
    span.append_child(doc.create_text_node("c"))
    doc.append_child(span)
    _attach_styles(doc, "span,b { display:inline }")

    tree = build_box_tree(doc)
    box = tree.children[0]
    assert box.outer_display == "inline"
    assert box.inner_display == "flow"
    outers = [c.outer_display for c in box.children]
    assert outers == ["inline", "inline", "inline"]
    # All inline-level — no anonymous wrapping (AC-7 inverse).
    assert all(not c.is_anonymous for c in box.children)
    assert box.children[0].text == "a"
    assert box.children[1].children[0].text == "b"
    assert box.children[2].text == "c"


def test_mixed_inline_and_block_children_get_anonymous_wrapper() -> None:
    """AC-7 — block-in-inline anonymous wrapping keys on outer_display.

    The fixture is the canonical [inline-text, block-elt, inline-text]
    case. Output shape `[anonymous, block, anonymous]` is preserved
    from the legacy implementation; only the trigger moved from
    `kind` to `outer_display`.
    """
    doc = Document()
    parent = doc.create_element("div")
    parent.append_child(doc.create_text_node("before"))
    child_block = doc.create_element("section")
    child_block.append_child(doc.create_text_node("middle"))
    parent.append_child(child_block)
    parent.append_child(doc.create_text_node("after"))
    doc.append_child(parent)
    _attach_styles(doc, "div,section { display:block }")

    tree = build_box_tree(doc)
    parent_box = tree.children[0]
    assert len(parent_box.children) == 3
    a, mid, c = parent_box.children
    # Anonymous wrappers carry outer_display='block', inner_display='flow',
    # source_node is None.
    assert a.is_anonymous is True
    assert (a.outer_display, a.inner_display, a.replaced) == ("block", "flow", False)
    assert a.source_node is None
    assert mid.is_anonymous is False
    assert (mid.outer_display, mid.inner_display) == ("block", "flow")
    assert c.is_anonymous is True
    assert (c.outer_display, c.inner_display) == ("block", "flow")
    # The wrapped inline-text payloads survive intact.
    assert a.children[0].text == "before"
    assert mid.children[0].text == "middle"
    assert c.children[0].text == "after"


def test_every_box_maps_back_to_source_node() -> None:
    """AC-8 — every non-anonymous box exposes its source DOM node."""
    doc = Document()
    div = doc.create_element("div")
    span = doc.create_element("span")
    text = doc.create_text_node("x")
    span.append_child(text)
    div.append_child(span)
    doc.append_child(div)
    _attach_styles(doc, "div { display:block } span { display:inline }")

    tree = build_box_tree(doc)
    assert tree.source_node is doc
    assert tree.children[0].source_node is div
    assert tree.children[0].children[0].source_node is span
    assert tree.children[0].children[0].children[0].source_node is text


# -------------------------------------------------------------------------
# 3. Phase-2 amendment regressions — the bugs the substring heuristic
#    shipped. (AC-5)
# -------------------------------------------------------------------------


def test_inline_block_is_inline_level_not_block() -> None:
    """AC-5 / direct regression: inline-block previously bucketed as block."""
    doc = Document()
    span = doc.create_element("span")
    span.append_child(doc.create_text_node("x"))
    doc.append_child(span)
    _attach_styles(doc, "span { display: inline-block }")

    tree = build_box_tree(doc)
    box = tree.children[0]
    assert box.outer_display == "inline"
    assert box.inner_display == "flow-root"
    assert box.replaced is False


def test_inline_flex_is_inline_level_not_block() -> None:
    """AC-5 — `inline-flex` per §2.6 → outer=inline, inner=flex."""
    doc = Document()
    span = doc.create_element("span")
    doc.append_child(span)
    _attach_styles(doc, "span { display: inline-flex }")

    box = build_box_tree(doc).children[0]
    assert (box.outer_display, box.inner_display) == ("inline", "flex")


def test_inline_grid_is_inline_level_not_block() -> None:
    """AC-5 — `inline-grid` per §2.6 → outer=inline, inner=grid."""
    doc = Document()
    span = doc.create_element("span")
    doc.append_child(span)
    _attach_styles(doc, "span { display: inline-grid }")

    box = build_box_tree(doc).children[0]
    assert (box.outer_display, box.inner_display) == ("inline", "grid")


def test_inline_table_is_inline_level_not_block() -> None:
    """AC-5 — `inline-table` per §2.6 → outer=inline, inner=table."""
    doc = Document()
    span = doc.create_element("span")
    doc.append_child(span)
    _attach_styles(doc, "span { display: inline-table }")

    box = build_box_tree(doc).children[0]
    assert (box.outer_display, box.inner_display) == ("inline", "table")


def test_two_keyword_inline_flow_root_is_inline_level() -> None:
    """AC-2 + AC-5 — the §2 two-keyword form `inline flow-root` matches the
    §2.6 legacy form."""
    doc = Document()
    span = doc.create_element("span")
    doc.append_child(span)
    _attach_styles(doc, "span { display: inline flow-root }")

    box = build_box_tree(doc).children[0]
    assert (box.outer_display, box.inner_display) == ("inline", "flow-root")


# -------------------------------------------------------------------------
# 4. display:contents hoist semantics (§2.5, HI-3, HI-4) — AC-4.
# -------------------------------------------------------------------------


def test_display_contents_hoists_children_into_parent_in_order() -> None:
    """AC-4 / HI-3: `display: contents` elides only the element's own box;
    children appear in the parent's children in document order with
    `source_node` references intact."""
    doc = Document()
    parent = doc.create_element("div")
    host = doc.create_element("span")  # display: contents
    b = doc.create_element("b")
    i = doc.create_element("i")
    host.append_child(b)
    host.append_child(i)
    parent.append_child(host)
    doc.append_child(parent)
    _attach_styles(
        doc,
        "div { display: block } span { display: contents } b, i { display: inline }",
    )

    tree = build_box_tree(doc)
    parent_box = tree.children[0]
    # The <span> produced no box; <b> and <i> are now direct children
    # of the <div> in document order.
    assert len(parent_box.children) == 2
    assert parent_box.children[0].source_node is b
    assert parent_box.children[1].source_node is i
    # source_node identity preserved (HI-3): no anonymous wrappers
    # interposed.
    assert all(not c.is_anonymous for c in parent_box.children)


def test_display_contents_on_replaced_elides_subtree() -> None:
    """AC-4 / HI-4: `display: contents` on a replaced element computes to
    `display: none` per §2.5 last paragraph."""
    doc = Document()
    parent = doc.create_element("div")
    img = doc.create_element("img")
    parent.append_child(img)
    doc.append_child(parent)
    _attach_styles(doc, "div { display:block } img { display: contents }")

    tree = build_box_tree(doc)
    parent_box = tree.children[0]
    # Replaced + contents → elided.
    assert parent_box.children == []


def test_display_contents_does_not_mutate_dom() -> None:
    """ — the hoist is a box-tree projection, not DOM reparenting."""
    doc = Document()
    parent = doc.create_element("div")
    host = doc.create_element("span")
    b = doc.create_element("b")
    host.append_child(b)
    parent.append_child(host)
    doc.append_child(parent)
    _attach_styles(doc, "span { display: contents }")

    build_box_tree(doc)
    # DOM structure is untouched: the <span> still owns <b>.
    assert b.parent_node is host
    assert host.parent_node is parent


def test_display_contents_nested_chain_hoists_through() -> None:
    """§2.5 NOTE — anonymous box-generation rules ignore display:contents
    elements entirely. Two nested contents collapse into the grandparent."""
    doc = Document()
    grand = doc.create_element("div")
    mid = doc.create_element("span")
    inner = doc.create_element("span")
    leaf = doc.create_element("b")
    inner.append_child(leaf)
    mid.append_child(inner)
    grand.append_child(mid)
    doc.append_child(grand)
    _attach_styles(
        doc,
        "div { display: block } span { display: contents } b { display: inline }",
    )

    tree = build_box_tree(doc)
    grand_box = tree.children[0]
    # Two contents-elided spans collapse; <b> is now a direct child of
    # the <div> box, with its source_node still pointing to the
    # original DOM <b>.
    assert len(grand_box.children) == 1
    assert grand_box.children[0].source_node is leaf


# -------------------------------------------------------------------------
# 5. Replaced elements (§2.2, FR-5, AC-6).
# -------------------------------------------------------------------------


def test_replaced_inline_default() -> None:
    """AC-6 — <img> with default `inline` cascade is inline-level replaced."""
    doc = Document()
    host = doc.create_element("div")
    img = doc.create_element("img")
    host.append_child(img)
    doc.append_child(host)
    _attach_styles(doc, "div { display:block }")

    tree = build_box_tree(doc)
    img_box = tree.children[0].children[0]
    assert img_box.replaced is True
    assert img_box.outer_display == "inline"
    assert img_box.inner_display is None  # §2.2: N/A on replaced.
    assert img_box.source_node is img


def test_replaced_block_with_display_block() -> None:
    """AC-6 — <img style='display:block'> is block-level replaced."""
    doc = Document()
    host = doc.create_element("div")
    img = doc.create_element("img")
    host.append_child(img)
    doc.append_child(host)
    _attach_styles(doc, "div { display:block } img { display: block }")

    tree = build_box_tree(doc)
    img_box = tree.children[0].children[0]
    assert img_box.replaced is True
    assert img_box.outer_display == "block"
    assert img_box.inner_display is None


def test_replaced_subtree_is_opaque() -> None:
    """§2.2 NOTE on replaced contents — replaced subtrees are not descended."""
    doc = Document()
    host = doc.create_element("div")
    obj = doc.create_element("object")
    obj.append_child(doc.create_text_node("fallback"))
    host.append_child(obj)
    doc.append_child(host)
    _attach_styles(doc, "div { display:block }")

    tree = build_box_tree(doc)
    obj_box = tree.children[0].children[0]
    assert obj_box.replaced is True
    # Replaced children are not produced as box-tree boxes.
    assert obj_box.children == []


# -------------------------------------------------------------------------
# 4. UA default stylesheet downstream effects ( / ,
#    ). Before this slice every element resolved to the §2 initial
#    `inline`; now the box tree matches real HTML *without* author CSS.
#    (FR-5 / FR-6, AC-5)
# -------------------------------------------------------------------------


def _iter_boxes(box):
    yield box
    for child in box.children:
        yield from _iter_boxes(child)


def _box_for_tag(tree, tag: str):
    for box in _iter_boxes(tree):
        node = box.source_node
        if node is not None and getattr(node, "local_name", None) == tag:
            return box
    return None


def test_ua_default_box_levels_without_author_css() -> None:
    """FR-5 / AC-5: a UA-styled document yields correct box levels."""
    from aspose_html.html_document import HTMLDocument

    doc = HTMLDocument.parse(
        "<!doctype html><html><body>"
        "<div id=d></div>"
        "<span id=s></span>"
        "<ul><li id=li></li></ul>"
        "<table><tr><td id=td></td></tr></table>"
        "</body></html>"
    )
    tree = build_box_tree(doc)

    div_box = _box_for_tag(tree, "div")
    assert div_box is not None and div_box.outer_display == "block"

    span_box = _box_for_tag(tree, "span")
    assert span_box is not None and span_box.outer_display == "inline"


def test_ua_default_display_classification() -> None:
    """FR-5 / AC-5: classify_display over the UA-resolved display values."""
    from aspose_html.html_document import HTMLDocument
    from aspose_html.layout import computed_style

    doc = HTMLDocument.parse(
        "<!doctype html><html><body>"
        "<li id=li></li>"
        "<table id=t><tr><td id=td></td></tr></table>"
        "</body></html>"
    )

    li = doc.get_element_by_id("li")
    assert classify_display(computed_style(li).get("display")).list_item is True

    table = doc.get_element_by_id("t")
    assert classify_display(computed_style(table).get("display")).inner == "table"

    td = doc.get_element_by_id("td")
    assert classify_display(computed_style(td).get("display")).layout_internal == "table-cell"


def test_ua_default_head_generates_no_box() -> None:
    """FR-5 / AC-5: <head>/<script> resolve to display:none → no box."""
    from aspose_html.html_document import HTMLDocument
    from aspose_html.layout import computed_style

    doc = HTMLDocument.parse(
        "<!doctype html><html><head><script>var x=1;</script></head>"
        "<body><div></div></body></html>"
    )
    head = doc.get_elements_by_tag_name("head")[0]
    assert classify_display(computed_style(head).get("display")).generates == "none"
    # The <head> subtree produces no box in the tree.
    assert _box_for_tag(build_box_tree(doc), "head") is None


def test_ua_defaults_trigger_block_in_inline_anonymous_wrapper() -> None:
    """FR-6 / AC-5: anonymous wrapping triggers on realistic UA-styled HTML.

    Before this slice every element was inline, so a block container with
    mixed inline/block children never arose from default markup. With the
    UA defaults, ``<body>`` (block) hosting an inline ``<span>`` next to a
    block ``<div>`` produces the CSS 2.2 §9.2.1.1 anonymous-block split.
    """
    from aspose_html.html_document import HTMLDocument

    doc = HTMLDocument.parse(
        "<!doctype html><html><body><span>a</span><div></div></body></html>"
    )
    tree = build_box_tree(doc)
    body_box = _box_for_tag(tree, "body")
    assert body_box is not None
    # The inline <span> run is wrapped in an anonymous block; the <div>
    # stays a separate block sibling.
    anon = [c for c in body_box.children if c.is_anonymous]
    assert anon, "expected an anonymous block wrapper for the inline run"
    assert anon[0].outer_display == "block"
    assert any(
        not c.is_anonymous
        and getattr(c.source_node, "local_name", None) == "div"
        for c in body_box.children
    )
