from __future__ import annotations

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.layout import build_box_tree, layout_block_tree


def _attach_styles(doc: Document, css: str) -> None:
    sheet = CSSStyleSheet()
    sheet.replace_sync(css)
    doc.attach_style_sheet(sheet)


def test_explicit_width_and_nested_block_stacking() -> None:
    doc = Document()
    outer = doc.create_element("div")
    child1 = doc.create_element("div")
    child2 = doc.create_element("div")
    outer.append_child(child1)
    outer.append_child(child2)
    doc.append_child(outer)
    _attach_styles(
        doc,
        "div { display:block; margin:0; padding:0; border:0; }"
        "div { width: 200px; height: 10px; }",
    )

    tree = build_box_tree(doc)
    fr = layout_block_tree(tree, 500.0)
    assert len(fr.children) == 1
    root = fr.children[0]
    assert root.width == 200.0
    assert len(root.children) == 2
    assert root.children[0].y <= root.children[1].y


def test_auto_width_fills_containing_block() -> None:
    doc = Document()
    div = doc.create_element("div")
    doc.append_child(div)
    _attach_styles(doc, "div { display:block; margin:0; padding:0; border:0; width:auto; }")

    fr = layout_block_tree(build_box_tree(doc), 320.0)
    assert fr.children[0].width == 320.0


def test_auto_margins_center_specified_width() -> None:
    doc = Document()
    div = doc.create_element("div")
    doc.append_child(div)
    _attach_styles(
        doc,
        "div { display:block; width:200px; margin-left:auto; margin-right:auto; padding:0; border:0; }",
    )

    fr = layout_block_tree(build_box_tree(doc), 500.0)
    box = fr.children[0]
    assert box.margin.left == 150.0
    assert box.margin.right == 150.0


def test_anonymous_wrappers_survive_into_fragments() -> None:
    doc = Document()
    parent = doc.create_element("div")
    parent.append_child(doc.create_text_node("before"))
    section = doc.create_element("section")
    section.append_child(doc.create_text_node("middle"))
    parent.append_child(section)
    parent.append_child(doc.create_text_node("after"))
    doc.append_child(parent)
    _attach_styles(doc, "div, section { display:block; margin:0; padding:0; border:0; }")

    fr = layout_block_tree(build_box_tree(doc), 600.0)
    parent_frag = fr.children[0]
    assert len(parent_frag.children) == 3
    assert parent_frag.children[0].is_anonymous is True
    assert parent_frag.children[2].is_anonymous is True


def test_ua_default_driven_div_block_flow() -> None:
    doc = Document()
    root = doc.create_element("main")
    a = doc.create_element("div")
    b = doc.create_element("div")
    root.append_child(a)
    root.append_child(b)
    doc.append_child(root)
    _attach_styles(doc, "div { margin:0; padding:0; border:0; height:12px; }")

    fr = layout_block_tree(build_box_tree(doc), 400.0)
    root_frag = fr.children[0]
    assert len(root_frag.children) == 2
    assert root_frag.children[0].y <= root_frag.children[1].y
