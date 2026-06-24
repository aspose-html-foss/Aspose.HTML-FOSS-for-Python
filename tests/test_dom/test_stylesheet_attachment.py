from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document


def test_document_style_sheets_includes_programmatic_attachments_in_order():
    doc = Document()
    a = CSSStyleSheet()
    b = CSSStyleSheet()
    doc.attach_style_sheet(a)
    doc.attach_style_sheet(b)

    assert list(doc.style_sheets) == [a, b]


def test_document_style_sheets_includes_style_element_sheet():
    doc = Document()
    root = doc.create_element("html")
    head = doc.create_element("head")
    style = doc.create_element("style")
    style.text_content = "p { color: red }"
    head.append_child(style)
    root.append_child(head)
    doc.append_child(root)

    assert doc.style_sheets.length == 1
    assert doc.style_sheets[0].owner_node is style
    assert doc.style_sheets[0].css_rules[0].css_text == "p { color: red }"


def test_style_element_sheet_reparses_after_text_change():
    doc = Document()
    style = doc.create_element("style")
    style.text_content = "p { color: red }"
    first = style.sheet

    style.text_content = "p { color: blue }"
    second = style.sheet

    assert first is not None
    assert second is not None
    assert first is not second
    assert second.css_rules[0].css_text == "p { color: blue }"


def test_link_sheet_requires_stylesheet_rel_token_case_insensitive():
    doc = Document()
    link = doc.create_element("link")
    link.rel = "preload"
    assert link.sheet is None

    link.rel = "Alternate StyleSheet"
    assert link.sheet is not None


def test_link_sheet_sets_owner_and_href_without_fetching():
    doc = Document()
    link = doc.create_element("link")
    link.rel = "stylesheet"
    link.href = "style.css"

    sheet = link.sheet
    assert sheet is not None
    assert sheet.owner_node is link
    assert sheet.href == "style.css"
    assert sheet.css_rules.length == 0


def test_element_style_sheets_matches_document_order_baseline():
    doc = Document()
    root = doc.create_element("html")
    head = doc.create_element("head")
    style = doc.create_element("style")
    style.text_content = "p { color: red }"
    head.append_child(style)
    root.append_child(head)
    doc.append_child(root)

    programmatic = CSSStyleSheet()
    doc.attach_style_sheet(programmatic)
    el = doc.create_element("div")
    root.append_child(el)

    assert list(el.style_sheets) == list(doc.style_sheets)
    assert el.style_sheets[0] is programmatic


def test_attach_style_sheet_is_idempotent():
    doc = Document()
    sheet = CSSStyleSheet()
    doc.attach_style_sheet(sheet)
    doc.attach_style_sheet(sheet)
    assert doc.style_sheets.length == 1


def test_detach_style_sheet_is_noop_when_missing():
    doc = Document()
    sheet = CSSStyleSheet()
    doc.detach_style_sheet(sheet)
    assert doc.style_sheets.length == 0


def test_style_sheet_list_item_out_of_range_returns_none():
    doc = Document()
    assert doc.style_sheets.item(0) is None


def test_style_sheet_list_is_live_after_dom_mutation():
    doc = Document()
    root = doc.create_element("html")
    head = doc.create_element("head")
    root.append_child(head)
    doc.append_child(root)
    sheets = doc.style_sheets
    assert sheets.length == 0

    style = doc.create_element("style")
    style.text_content = "p { color: red }"
    head.append_child(style)

    assert sheets.length == 1
