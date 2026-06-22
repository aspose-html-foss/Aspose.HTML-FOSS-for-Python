"""Tests for HTML table element subclasses — BACK-35 / ADR-031."""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    Element,
    HTMLElement,
    HTMLTableElement,
    HTMLTableSectionElement,
    HTMLTableRowElement,
    HTMLTableCellElement,
    HTMLTableCaptionElement,
    HTMLTableColElement,
)


@pytest.fixture()
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# Dispatch: create_element returns correct subclass
# ---------------------------------------------------------------------------

def test_table_dispatch(doc: Document) -> None:
    el = doc.create_element("table")
    assert isinstance(el, HTMLTableElement)
    assert type(el) is HTMLTableElement


@pytest.mark.parametrize("tag", ["thead", "tbody", "tfoot"])
def test_section_dispatch(doc: Document, tag: str) -> None:
    el = doc.create_element(tag)
    assert isinstance(el, HTMLTableSectionElement)
    assert type(el) is HTMLTableSectionElement


def test_tr_dispatch(doc: Document) -> None:
    el = doc.create_element("tr")
    assert isinstance(el, HTMLTableRowElement)


@pytest.mark.parametrize("tag", ["td", "th"])
def test_cell_dispatch(doc: Document, tag: str) -> None:
    el = doc.create_element(tag)
    assert isinstance(el, HTMLTableCellElement)


def test_caption_dispatch(doc: Document) -> None:
    el = doc.create_element("caption")
    assert isinstance(el, HTMLTableCaptionElement)


@pytest.mark.parametrize("tag", ["col", "colgroup"])
def test_col_dispatch(doc: Document, tag: str) -> None:
    el = doc.create_element(tag)
    assert isinstance(el, HTMLTableColElement)


# ---------------------------------------------------------------------------
# isinstance hierarchy
# ---------------------------------------------------------------------------

def test_table_isinstance_chain(doc: Document) -> None:
    table = doc.create_element("table")
    assert isinstance(table, HTMLElement)
    assert isinstance(table, Element)


# ---------------------------------------------------------------------------
# __slots__ = ()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cls", [
    HTMLTableElement, HTMLTableSectionElement, HTMLTableRowElement,
    HTMLTableCellElement, HTMLTableCaptionElement, HTMLTableColElement,
])
def test_slots_empty(cls: type) -> None:
    assert cls.__slots__ == ()


# ---------------------------------------------------------------------------
# IDL properties: HTMLTableCellElement
# ---------------------------------------------------------------------------

def test_cell_col_span_default(doc: Document) -> None:
    td = doc.create_element("td")
    assert td.col_span == 1  # type: ignore[attr-defined]


def test_cell_col_span_setter(doc: Document) -> None:
    td = doc.create_element("td")
    td.col_span = 3  # type: ignore[attr-defined]
    assert td.get_attribute("colspan") == "3"
    assert td.col_span == 3  # type: ignore[attr-defined]


def test_cell_row_span_default(doc: Document) -> None:
    td = doc.create_element("td")
    assert td.row_span == 1  # type: ignore[attr-defined]


def test_cell_row_span_setter(doc: Document) -> None:
    th = doc.create_element("th")
    th.row_span = 2  # type: ignore[attr-defined]
    assert th.get_attribute("rowspan") == "2"


def test_cell_headers_default(doc: Document) -> None:
    td = doc.create_element("td")
    assert td.headers == ""  # type: ignore[attr-defined]


def test_cell_headers_setter(doc: Document) -> None:
    td = doc.create_element("td")
    td.headers = "col1 col2"  # type: ignore[attr-defined]
    assert td.get_attribute("headers") == "col1 col2"


# ---------------------------------------------------------------------------
# IDL properties: HTMLTableColElement
# ---------------------------------------------------------------------------

def test_col_span_default(doc: Document) -> None:
    col = doc.create_element("col")
    assert col.span == 1  # type: ignore[attr-defined]


def test_col_span_setter(doc: Document) -> None:
    col = doc.create_element("col")
    col.span = 5  # type: ignore[attr-defined]
    assert col.get_attribute("span") == "5"


# ---------------------------------------------------------------------------
# IDL properties: HTMLTableElement
# ---------------------------------------------------------------------------

def test_table_border(doc: Document) -> None:
    table = doc.create_element("table")
    assert table.border == ""  # type: ignore[attr-defined]
    table.border = "1"  # type: ignore[attr-defined]
    assert table.get_attribute("border") == "1"


# ---------------------------------------------------------------------------
# Live collection: rows / cells / t_bodies
# ---------------------------------------------------------------------------

def test_table_rows_includes_tr_in_tbody(doc: Document) -> None:
    table = doc.create_element("table")
    tbody = doc.create_element("tbody")
    tr = doc.create_element("tr")
    doc.append_child(table)
    table.append_child(tbody)
    tbody.append_child(tr)
    rows = list(table.rows)  # type: ignore[attr-defined]
    assert tr in rows


def test_table_t_bodies_live(doc: Document) -> None:
    table = doc.create_element("table")
    tbody = doc.create_element("tbody")
    doc.append_child(table)
    table.append_child(tbody)
    t_bodies = list(table.t_bodies)  # type: ignore[attr-defined]
    assert tbody in t_bodies


def test_section_rows(doc: Document) -> None:
    tbody = doc.create_element("tbody")
    tr = doc.create_element("tr")
    doc.append_child(tbody)
    tbody.append_child(tr)
    rows = list(tbody.rows)  # type: ignore[attr-defined]
    assert tr in rows


def test_row_cells(doc: Document) -> None:
    tr = doc.create_element("tr")
    td = doc.create_element("td")
    th = doc.create_element("th")
    doc.append_child(tr)
    tr.append_child(td)
    tr.append_child(th)
    cells = list(tr.cells)  # type: ignore[attr-defined]
    assert td in cells
    assert th in cells


# ---------------------------------------------------------------------------
# Exported from aspose_html.dom
# ---------------------------------------------------------------------------

def test_exports_from_dom() -> None:
    import aspose_html.dom as dom
    for name in [
        "HTMLTableElement", "HTMLTableSectionElement", "HTMLTableRowElement",
        "HTMLTableCellElement", "HTMLTableCaptionElement", "HTMLTableColElement",
    ]:
        assert name in dom.__all__
        assert hasattr(dom, name)
