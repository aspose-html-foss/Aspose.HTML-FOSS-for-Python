from __future__ import annotations

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.layout import (
    BlockFragment,
    EdgeSizes,
    FragmentRoot,
    InlineTextFragment,
    LineFragment,
    ShapedRun,
    paginate_fragments,
)


def _line(height: float) -> LineFragment:
    run = ShapedRun(text="x", advance=0.0, ascent=height, descent=0.0)
    return LineFragment(
        runs=(InlineTextFragment(run=run, x=0.0, y=0.0, width=0.0, height=height, baseline=height),),
        x=0.0,
        y=0.0,
        width=0.0,
        height=height,
        baseline=height,
    )


def _block(node, *, height: float, lines: tuple[LineFragment, ...] = ()) -> BlockFragment:
    return BlockFragment(
        source_node=node,
        children=(),
        x=0.0,
        y=0.0,
        width=100.0,
        height=height,
        margin=EdgeSizes(),
        padding=EdgeSizes(),
        border=EdgeSizes(),
        line_fragments=lines,
        is_anonymous=False,
    )


def _attach_root_with_children(doc: Document, count: int):
    root = doc.create_element("div")
    doc.append_child(root)
    children = []
    for _ in range(count):
        el = doc.create_element("div")
        root.append_child(el)
        children.append(el)
    return tuple(children)


def test_paginate_fragments_honors_forced_breaks() -> None:
    doc = Document()
    a, b, c = _attach_root_with_children(doc, 3)
    sheet = CSSStyleSheet()
    sheet.replace_sync("div:nth-of-type(1){break-after:page} div:nth-of-type(3){break-before:page}")
    doc.attach_style_sheet(sheet)

    root = FragmentRoot(children=(_block(a, height=10.0), _block(b, height=10.0), _block(c, height=10.0)))
    pages = paginate_fragments(root, page_width=200.0, page_height=100.0)

    assert len(pages) == 3
    assert pages[0].children == (root.children[0],)
    assert pages[1].children == (root.children[1],)
    assert pages[2].children == (root.children[2],)


def test_paginate_fragments_honors_break_inside_avoid_when_feasible() -> None:
    doc = Document()
    a, b = _attach_root_with_children(doc, 2)
    sheet = CSSStyleSheet()
    sheet.replace_sync("div:nth-of-type(2){break-inside:avoid}")
    doc.attach_style_sheet(sheet)

    root = FragmentRoot(children=(_block(a, height=60.0), _block(b, height=50.0)))
    pages = paginate_fragments(root, page_width=200.0, page_height=100.0)

    assert len(pages) == 2
    assert len(pages[0].children) == 1
    assert len(pages[1].children) == 1


def test_paginate_fragments_falls_back_for_unfit_avoid_content() -> None:
    doc = Document()
    a, b = _attach_root_with_children(doc, 2)
    sheet = CSSStyleSheet()
    sheet.replace_sync("div:nth-of-type(2){break-inside:avoid}")
    doc.attach_style_sheet(sheet)

    root = FragmentRoot(children=(_block(a, height=20.0), _block(b, height=150.0)))
    pages = paginate_fragments(root, page_width=200.0, page_height=100.0)

    assert len(pages) == 1
    assert pages[0].children == root.children


def test_paginate_fragments_applies_widows_orphans_deterministically() -> None:
    doc = Document()
    a, b = _attach_root_with_children(doc, 2)
    sheet = CSSStyleSheet()
    sheet.replace_sync("div:nth-of-type(2){widows:2;orphans:2}")
    doc.attach_style_sheet(sheet)

    lines = (_line(10.0), _line(10.0), _line(10.0), _line(10.0))
    root = FragmentRoot(children=(_block(a, height=10.0), _block(b, height=40.0, lines=lines)))

    pages = paginate_fragments(root, page_width=200.0, page_height=30.0)

    assert len(pages) == 2
    assert len(pages[0].children) == 2
    assert len(pages[0].children[1].line_fragments) == 2
    assert len(pages[1].children) == 1
    assert len(pages[1].children[0].line_fragments) == 2
    assert [p.page_index for p in pages] == [0, 1]
