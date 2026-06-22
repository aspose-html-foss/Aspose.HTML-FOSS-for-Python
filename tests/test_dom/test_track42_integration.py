"""Track 42 integration hardening tests (BACK-184 / SPEC-097 / ADR-167).

Cross-component integration checks for BACK-180 through BACK-183:
  Group A — HTMLTableElement mutation round-trip
  Group B — Element geometry gap (offset_parent, client_top, client_left)
  Group C — CSS @layer cascade ordering
  Group D — HTMLScriptElement.text + HTMLStyleElement.sheet + HTMLLinkElement.sheet
  Group E — Doctest sweep for touched public modules
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.dom.html._elements import (
    HTMLDivElement,
    HTMLLinkElement,
    HTMLScriptElement,
    HTMLStyleElement,
    HTMLTableCaptionElement,
    HTMLTableCellElement,
    HTMLTableElement,
    HTMLTableRowElement,
    HTMLTableSectionElement,
)


# ---------------------------------------------------------------------------
# Group A — HTMLTableElement mutation round-trip
# ---------------------------------------------------------------------------


def test_group_a_insert_row_appends_and_live_collection_reflects() -> None:
    """insert_row appended rows are reflected in the live rows collection."""
    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    assert len(list(table.rows)) == 0

    tr0 = table.insert_row()
    assert isinstance(tr0, HTMLTableRowElement)
    assert len(list(table.rows)) == 1

    tr1 = table.insert_row()
    tr2 = table.insert_row()
    assert len(list(table.rows)) == 3


def test_group_a_delete_row_removes_correct_row() -> None:
    """delete_row at index 1 removes the second row; remaining rows shift."""
    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    tr0 = table.insert_row()
    tr1 = table.insert_row()
    tr2 = table.insert_row()
    rows_before = list(table.rows)
    assert rows_before[0] is tr0
    assert rows_before[1] is tr1
    assert rows_before[2] is tr2

    table.delete_row(1)

    rows_after = list(table.rows)
    assert len(rows_after) == 2
    assert rows_after[0] is tr0
    assert rows_after[1] is tr2


def test_group_a_insert_row_at_zero_prepends() -> None:
    """insert_row(0) prepends; new row is first in live collection."""
    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    tr_existing = table.insert_row()
    tr_new = table.insert_row(0)

    rows = list(table.rows)
    assert rows[0] is tr_new
    assert rows[1] is tr_existing


def test_group_a_create_t_head_idempotent() -> None:
    """create_t_head returns the same element on second call."""
    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    thead_a = table.create_t_head()
    thead_b = table.create_t_head()
    assert thead_a is thead_b
    assert isinstance(thead_a, HTMLTableSectionElement)


def test_group_a_create_caption_idempotent() -> None:
    """create_caption returns the same element on second call."""
    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    cap_a = table.create_caption()
    cap_b = table.create_caption()
    assert cap_a is cap_b
    assert isinstance(cap_a, HTMLTableCaptionElement)


def test_group_a_section_insert_delete_row() -> None:
    """insert_row/delete_row on HTMLTableSectionElement is reflected in section.rows."""
    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    tbody = table.create_t_foot()
    assert len(list(tbody.rows)) == 0

    tr = tbody.insert_row()
    assert isinstance(tr, HTMLTableRowElement)
    assert len(list(tbody.rows)) == 1

    tbody.delete_row(0)
    assert len(list(tbody.rows)) == 0


def test_group_a_insert_cell_and_delete_cell_on_row() -> None:
    """insert_cell/delete_cell on HTMLTableRowElement updates cells collection."""
    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    tr = table.insert_row()
    assert len(list(tr.cells)) == 0

    cell = tr.insert_cell()
    assert isinstance(cell, HTMLTableCellElement)
    assert len(list(tr.cells)) == 1

    tr.delete_cell(0)
    assert len(list(tr.cells)) == 0


def test_group_a_cell_scope_attribute_reflection() -> None:
    """HTMLTableCellElement.scope reflects the 'scope' attribute."""
    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    tr = table.insert_row()
    cell = tr.insert_cell()
    assert cell.scope == ""

    cell.scope = "col"
    assert cell.scope == "col"
    assert cell.get_attribute("scope") == "col"


def test_group_a_out_of_range_raises_index_size_error() -> None:
    """insert_row and delete_row raise IndexSizeError for out-of-range indices."""
    from aspose_html.dom._exceptions import IndexSizeError

    doc = Document()
    table = doc.create_element("table")
    doc.append_child(table)

    with pytest.raises(IndexSizeError):
        table.insert_row(-2)

    with pytest.raises(IndexSizeError):
        table.insert_row(1)  # 0 rows; index 1 is beyond end

    table.insert_row()  # now 1 row

    with pytest.raises(IndexSizeError):
        table.delete_row(-1)

    with pytest.raises(IndexSizeError):
        table.delete_row(1)


# ---------------------------------------------------------------------------
# Group B — Element geometry gap (offset_parent, client_top, client_left)
# ---------------------------------------------------------------------------


def test_group_b_offset_parent_is_none_on_element() -> None:
    """Element.offset_parent always returns None in headless mode."""
    doc = Document()
    el = doc.create_element("div")
    assert el.offset_parent is None


def test_group_b_client_top_is_zero_on_element() -> None:
    """Element.client_top always returns 0 in headless mode."""
    doc = Document()
    el = doc.create_element("div")
    assert el.client_top == 0


def test_group_b_client_left_is_zero_on_element() -> None:
    """Element.client_left always returns 0 in headless mode."""
    doc = Document()
    el = doc.create_element("div")
    assert el.client_left == 0


def test_group_b_geometry_gap_accessible_on_html_subclass() -> None:
    """offset_parent, client_top, client_left are inherited by HTMLElement subclasses."""
    doc = Document()
    div = doc.create_element("div")
    assert isinstance(div, HTMLDivElement)
    assert div.offset_parent is None
    assert div.client_top == 0
    assert div.client_left == 0


def test_group_b_offset_width_height_also_zero() -> None:
    """offset_width and offset_height (from Track 34) remain 0 alongside new stubs."""
    doc = Document()
    el = doc.create_element("div")
    assert el.offset_width == 0
    assert el.offset_height == 0
    # All four offset/client stubs consistent
    assert el.offset_parent is None
    assert el.client_top == 0
    assert el.client_left == 0


# ---------------------------------------------------------------------------
# Group C — CSS @layer cascade ordering
# ---------------------------------------------------------------------------


def test_group_c_first_layer_wins_over_second_at_equal_specificity() -> None:
    """First @layer block wins over second when specificity is equal."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)

    sheet = CSSStyleSheet.from_text(
        "@layer base { div { color: red } }"
        "@layer theme { div { color: blue } }"
    )
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_group_c_unlayered_beats_all_layers() -> None:
    """Unlayered rule beats both @layer blocks at equal specificity."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)

    sheet = CSSStyleSheet.from_text(
        "@layer base { div { color: red } }"
        "@layer theme { div { color: blue } }"
        "div { color: green }"
    )
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_group_c_higher_specificity_in_later_layer_still_wins() -> None:
    """Higher specificity in a later layer wins over lower specificity in an earlier layer."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("id", "main")
    doc.append_child(el)

    sheet = CSSStyleSheet.from_text(
        "@layer base { div { color: red } }"
        "@layer theme { #main { color: blue } }"
    )
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    # #main has specificity (1,0,0) vs div (0,0,1); specificity wins over layer order
    assert style.get_property_value("color") == "blue"


def test_group_c_within_same_layer_source_order_applies() -> None:
    """Within a single @layer block, later declaration wins (source order)."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)

    sheet = CSSStyleSheet.from_text(
        "@layer base { div { color: red } div { color: purple } }"
    )
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("color") == "purple"


def test_group_c_no_layer_no_regression() -> None:
    """Stylesheet with no @layer works without regression."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)

    sheet = CSSStyleSheet.from_text("div { color: orange }")
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("color") == "orange"


def test_group_c_mixed_media_and_layer_combination() -> None:
    """@media rules in a sheet with @layer blocks do not interfere."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)

    # @media (screen-only rule won't match in headless, so margin stays unset)
    # @layer provides background-color
    sheet = CSSStyleSheet.from_text(
        "@layer base { div { background-color: yellow } }"
        "@media print { div { background-color: white } }"
    )
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("background-color") == "yellow"


# ---------------------------------------------------------------------------
# Group D — HTMLScriptElement.text + HTMLStyleElement.sheet + HTMLLinkElement.sheet
# ---------------------------------------------------------------------------


def test_group_d_script_text_empty_when_no_children() -> None:
    """HTMLScriptElement.text returns '' when element has no text children."""
    doc = Document()
    script = doc.create_element("script")
    assert isinstance(script, HTMLScriptElement)
    assert script.text == ""


def test_group_d_script_text_setter_creates_text_child() -> None:
    """HTMLScriptElement.text setter creates a single Text child node."""
    doc = Document()
    script = doc.create_element("script")
    script.text = "var x = 1;"
    assert script.text == "var x = 1;"


def test_group_d_script_text_setter_replaces_on_second_assignment() -> None:
    """HTMLScriptElement.text setter replaces content on second assignment."""
    doc = Document()
    script = doc.create_element("script")
    script.text = "var x = 1;"
    script.text = "var y = 2;"
    assert script.text == "var y = 2;"


def test_group_d_style_sheet_returns_sheet_with_owner_node() -> None:
    """HTMLStyleElement.sheet returns a CSSStyleSheet with owner_node set."""
    doc = Document()
    style = doc.create_element("style")
    assert isinstance(style, HTMLStyleElement)
    style.text_content = "p { color: red }"
    sheet = style.sheet
    assert sheet is not None
    assert sheet.owner_node is style


def test_group_d_style_sheet_parses_text_content() -> None:
    """HTMLStyleElement.sheet parses text_content and exposes css_rules."""
    doc = Document()
    style = doc.create_element("style")
    style.text_content = "div { color: blue }"
    sheet = style.sheet
    assert sheet is not None
    assert len(sheet.css_rules) == 1
    assert "color: blue" in sheet.css_rules[0].css_text


def test_group_d_link_sheet_returns_none_with_no_stylesheet_rel() -> None:
    """HTMLLinkElement.sheet returns None when rel is not 'stylesheet'."""
    doc = Document()
    link = doc.create_element("link")
    assert isinstance(link, HTMLLinkElement)
    link.href = "style.css"
    # rel not set → not stylesheet
    assert link.sheet is None


def test_group_d_link_sheet_returns_none_for_preload_rel() -> None:
    """HTMLLinkElement.sheet returns None for rel='preload' (not stylesheet)."""
    doc = Document()
    link = doc.create_element("link")
    link.rel = "preload"
    link.href = "data.css"
    assert link.sheet is None


def test_group_d_link_sheet_returns_sheet_for_stylesheet_rel() -> None:
    """HTMLLinkElement.sheet returns a CSSStyleSheet when rel='stylesheet'."""
    doc = Document()
    link = doc.create_element("link")
    link.rel = "stylesheet"
    link.href = "theme.css"
    sheet = link.sheet
    assert sheet is not None
    assert sheet.owner_node is link


# ---------------------------------------------------------------------------
# Group E — Doctest sweep for touched public modules
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    [
        "src/aspose_html/dom/html/_elements.py",
        "src/aspose_html/dom/_element.py",
        "src/aspose_html/dom/_cascade.py",
    ],
)
def test_group_e_doctest_sweep(module_path: str) -> None:
    """All >>> examples in the touched public modules execute cleanly."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--doctest-modules",
            module_path,
            "-q",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"doctest failed for {module_path}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
