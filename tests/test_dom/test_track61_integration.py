"""Track 61 Document adopted stylesheets — integration matrix (BACK-259).

Covers cross-behavior evidence for the Track 61 contract:

- ``Document.adopted_style_sheets`` assignment/getter behavior (ADR-238)
- ``attach_style_sheet`` / ``detach_style_sheet`` interoperability (ADR-239)
- ``Document.style_sheets`` deterministic ordering with element-derived sheets

ADR: ADR-240
SPEC: SPEC-115
Tasks: BACK-257, BACK-258, BACK-259
"""

from __future__ import annotations

from aspose_html.dom import Document
from aspose_html.cssom import CSSStyleSheet


def _sheet() -> CSSStyleSheet:
    sheet = CSSStyleSheet()
    sheet.replace_sync("body { color: red; }")
    return sheet


def test_adopted_assignment_replaces_list_atomically() -> None:
    doc = Document()
    a = _sheet()
    b = _sheet()
    doc.adopted_style_sheets = [a]
    doc.adopted_style_sheets = [b]
    assert doc.adopted_style_sheets == [b]


def test_attach_interoperates_with_adopted_storage_without_dup_identity() -> None:
    doc = Document()
    sheet = _sheet()
    doc.adopted_style_sheets = [sheet]
    doc.attach_style_sheet(sheet)
    assert doc.adopted_style_sheets == [sheet]


def test_detach_operates_on_assigned_adopted_sheet() -> None:
    doc = Document()
    sheet = _sheet()
    doc.adopted_style_sheets = [sheet]
    doc.detach_style_sheet(sheet)
    assert doc.adopted_style_sheets == []


def test_style_sheets_orders_adopted_before_style_and_link_nodes() -> None:
    doc = Document()
    adopted = _sheet()
    doc.adopted_style_sheets = [adopted]

    html = doc.create_element("html")
    body = doc.create_element("body")
    html.append_child(body)
    doc.append_child(html)

    style = doc.create_element("style")
    style.text_content = "p { margin: 0; }"
    body.append_child(style)

    link = doc.create_element("link")
    link.set_attribute("rel", "stylesheet")
    link.set_attribute("href", "https://example.com/x.css")
    body.append_child(link)

    sheets = doc.style_sheets
    assert sheets[0] is adopted
    assert len(sheets) == 3


def test_property_setter_rejects_non_stylesheet_members() -> None:
    doc = Document()
    try:
        doc.adopted_style_sheets = ["not-a-sheet"]  # type: ignore[list-item]
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_detach_unknown_sheet_is_noop() -> None:
    doc = Document()
    known = _sheet()
    unknown = _sheet()
    doc.adopted_style_sheets = [known]
    doc.detach_style_sheet(unknown)
    assert doc.adopted_style_sheets == [known]
