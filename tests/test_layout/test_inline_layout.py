from __future__ import annotations

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.layout import build_box_tree, layout_block_tree, layout_inline_fragments


def _attach_styles(doc: Document, css: str) -> None:
    sheet = CSSStyleSheet()
    sheet.replace_sync(css)
    doc.attach_style_sheet(sheet)


def _layout(doc: Document, width: float = 120.0):
    block_root = layout_block_tree(build_box_tree(doc), width)
    return layout_inline_fragments(block_root, width)


def test_normal_whitespace_collapses_sequences() -> None:
    doc = Document()
    div = doc.create_element("div")
    div.append_child(doc.create_text_node("a   b\n\tc"))
    doc.append_child(div)
    _attach_styles(doc, "div { display:block; white-space: normal; margin:0; padding:0; border:0; }")

    root = _layout(doc)
    run_texts = [run.run.text for run in root.children[0].line_fragments[0].runs]
    assert run_texts == ["a b c"]


def test_pre_preserves_newline_forced_breaks() -> None:
    doc = Document()
    div = doc.create_element("div")
    div.append_child(doc.create_text_node("alpha\nbeta"))
    doc.append_child(div)
    _attach_styles(doc, "div { display:block; white-space: pre; margin:0; padding:0; border:0; }")

    root = _layout(doc)
    line_texts = ["".join(r.run.text for r in ln.runs) for ln in root.children[0].line_fragments]
    assert line_texts == ["alpha", "beta"]


def test_nowrap_single_line_even_when_wide_text() -> None:
    doc = Document()
    div = doc.create_element("div")
    div.append_child(doc.create_text_node("averyveryverylongtoken"))
    doc.append_child(div)
    _attach_styles(doc, "div { display:block; white-space: nowrap; width: 8px; margin:0; padding:0; border:0; }")

    root = _layout(doc, width=8.0)
    assert len(root.children[0].line_fragments) == 1


def test_mixed_inline_nodes_preserve_source_order() -> None:
    doc = Document()
    div = doc.create_element("div")
    span = doc.create_element("span")
    div.append_child(doc.create_text_node("start "))
    span.append_child(doc.create_text_node("middle"))
    div.append_child(span)
    div.append_child(doc.create_text_node(" end"))
    doc.append_child(div)
    _attach_styles(
        doc,
        "div { display:block; margin:0; padding:0; border:0; } span { display:inline; }",
    )

    root = _layout(doc)
    text = "".join(run.run.text for run in root.children[0].line_fragments[0].runs)
    assert text == "start middle end"


def test_line_break_is_deterministic() -> None:
    doc = Document()
    div = doc.create_element("div")
    div.append_child(doc.create_text_node("one two three four"))
    doc.append_child(div)
    _attach_styles(doc, "div { display:block; white-space: normal; width: 7px; margin:0; padding:0; border:0; }")

    root_a = _layout(doc, width=7.0)
    root_b = _layout(doc, width=7.0)
    a = [line.width for line in root_a.children[0].line_fragments]
    b = [line.width for line in root_b.children[0].line_fragments]
    assert a == b
