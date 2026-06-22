"""Tests for Document._style_epoch + invalidation hooks — M7.1 (SPEC-168/ADR-315).

Covers AC-5 (slots), AC-6 (bump + clear), and AC-8..AC-16 (the full
invalidation hook table). AC-17 (CSSOM byte-identical output) is covered
by the existing tests/test_dom/test_cascade*.py suite.
"""
from __future__ import annotations

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.dom._element import _STYLE_AFFECTING_ATTRS
from aspose_html.layout import computed_style


def _doc_with_element():
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    return doc, el


# ---------------------------------------------------------------------------
# AC-5 — slots
# ---------------------------------------------------------------------------


def test_ac5_document_slots_contains_style_epoch() -> None:
    assert "_style_epoch" in Document.__slots__


def test_ac5_init_sets_epoch_zero() -> None:
    assert Document()._style_epoch == 0


def test_ac5_element_slots_unchanged() -> None:
    # The frozen Element.__slots__ contract (INV-008): per-element cache state
    # lives on the Document, never on the element. M7.1 must not grow it.
    from aspose_html.dom._element import Element

    assert Element.__slots__ == (
        "_tag_name",
        "_namespace_uri",
        "_prefix",
        "_local_name",
        "_attributes",
        "_children_cache",
        "_template_content",
        "_style_declaration",
        "_class_list",
        "_dataset",
    )


# ---------------------------------------------------------------------------
# AC-6 — bump + cache clear
# ---------------------------------------------------------------------------


def test_ac6_bump_increments_and_clears_cache() -> None:
    # Fresh document: two bumps from 0 yield epoch 2 + empty cache (AC-6).
    doc = Document()
    el = doc.create_element("div")
    # create_element does not connect, so no tree-mutation bump yet.
    assert doc._style_epoch == 0
    computed_style(el)  # populate the cache (el is owned even if detached)
    assert doc._style_cache  # non-empty
    doc._bump_style_epoch()
    doc._bump_style_epoch()
    assert doc._style_epoch == 2
    assert doc._style_cache == {}


# ---------------------------------------------------------------------------
# AC-8 / AC-9 — attach / detach style sheet
# ---------------------------------------------------------------------------


def test_ac8_attach_style_sheet_bumps_once() -> None:
    doc = Document()
    before = doc._style_epoch
    doc.attach_style_sheet(CSSStyleSheet())
    assert doc._style_epoch == before + 1


def test_ac9_detach_style_sheet_bumps_once() -> None:
    doc = Document()
    sheet = CSSStyleSheet()
    doc.attach_style_sheet(sheet)
    before = doc._style_epoch
    doc.detach_style_sheet(sheet)
    assert doc._style_epoch == before + 1


# ---------------------------------------------------------------------------
# AC-10 — adopted_style_sheets setter bumps once per assignment
# ---------------------------------------------------------------------------


def test_ac10_adopted_setter_one_bump_regardless_of_count() -> None:
    doc = Document()
    before = doc._style_epoch
    doc.adopted_style_sheets = [CSSStyleSheet(), CSSStyleSheet(), CSSStyleSheet()]
    assert doc._style_epoch == before + 1


def test_ac10_adopted_setter_empty_still_one_bump() -> None:
    doc = Document()
    before = doc._style_epoch
    doc.adopted_style_sheets = []
    assert doc._style_epoch == before + 1


# ---------------------------------------------------------------------------
# AC-11 — replace_sync (attached vs detached)
# ---------------------------------------------------------------------------


def test_ac11_replace_sync_on_attached_bumps() -> None:
    doc = Document()
    sheet = CSSStyleSheet()
    doc.attach_style_sheet(sheet)
    before = doc._style_epoch
    sheet.replace_sync("div { color: red }")
    assert doc._style_epoch == before + 1


def test_ac11_replace_sync_on_detached_no_bump() -> None:
    doc = Document()
    sheet = CSSStyleSheet()
    doc.attach_style_sheet(sheet)
    doc.detach_style_sheet(sheet)
    before = doc._style_epoch
    sheet.replace_sync("div { color: blue }")
    assert doc._style_epoch == before  # unchanged


def test_ac11_replace_sync_on_never_attached_no_bump() -> None:
    # A standalone sheet has no owning document — replace_sync must not raise.
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: red }")  # no document, no error


# ---------------------------------------------------------------------------
# AC-12 — insert_rule / delete_rule (attached)
# ---------------------------------------------------------------------------


def test_ac12_insert_rule_on_attached_bumps() -> None:
    doc = Document()
    sheet = CSSStyleSheet.from_text("div { color: red }")
    doc.attach_style_sheet(sheet)
    before = doc._style_epoch
    sheet.insert_rule("span { color: blue }")
    assert doc._style_epoch == before + 1


def test_ac12_delete_rule_on_attached_bumps() -> None:
    doc = Document()
    sheet = CSSStyleSheet.from_text("div { color: red } span { color: blue }")
    doc.attach_style_sheet(sheet)
    before = doc._style_epoch
    sheet.delete_rule(0)
    assert doc._style_epoch == before + 1


def test_ac12_insert_rule_on_detached_no_bump() -> None:
    doc = Document()
    sheet = CSSStyleSheet.from_text("div { color: red }")
    doc.attach_style_sheet(sheet)
    doc.detach_style_sheet(sheet)
    before = doc._style_epoch
    sheet.insert_rule("span { color: blue }")
    assert doc._style_epoch == before


# ---------------------------------------------------------------------------
# AC-13 / AC-14 — inline style set_property / remove_property
# ---------------------------------------------------------------------------


def test_ac13_set_property_with_owner_bumps_once() -> None:
    doc, el = _doc_with_element()
    before = doc._style_epoch
    el.style.set_property("color", "red")
    assert doc._style_epoch == before + 1


def test_ac13_set_property_on_detached_but_owned_bumps_once() -> None:
    # An element created via create_element has an owner_document even when not
    # connected to the tree; set_property bumps exactly once (never twice via
    # the set_attribute funnel) and never raises.
    owned = Document().create_element("div")  # not attached to its document tree
    owned_doc = owned.owner_document
    before = owned_doc._style_epoch
    owned.style.set_property("color", "red")  # must not raise
    assert owned_doc._style_epoch == before + 1


def test_ac13_set_property_truly_detached_no_owner_document() -> None:
    # A detached element with no owner document at all (Element constructed
    # without a document): set_property must be a silent no-op for the cache.
    from aspose_html.dom._element import Element

    el = Element("div", "http://www.w3.org/1999/xhtml")
    assert el.owner_document is None
    el.style.set_property("color", "red")  # must not raise, no document to bump


def test_ac14_remove_property_with_owner_bumps_once() -> None:
    doc, el = _doc_with_element()
    el.style.set_property("color", "red")
    before = doc._style_epoch
    el.style.remove_property("color")
    assert doc._style_epoch == before + 1


# ---------------------------------------------------------------------------
# AC-15 — set_attribute for class/id/style vs other names
# ---------------------------------------------------------------------------


def test_ac15_style_affecting_attrs_bump_once_each() -> None:
    for name, value in (("class", "foo"), ("id", "bar"), ("style", "color: red")):
        doc, el = _doc_with_element()
        before = doc._style_epoch
        el.set_attribute(name, value)
        assert doc._style_epoch == before + 1, name
    assert _STYLE_AFFECTING_ATTRS == frozenset({"class", "id", "style"})


def test_ac15_other_attribute_no_bump() -> None:
    doc, el = _doc_with_element()
    before = doc._style_epoch
    el.set_attribute("data-x", "1")
    el.set_attribute("title", "hi")
    assert doc._style_epoch == before


def test_ac15_remove_style_affecting_attr_bumps() -> None:
    doc, el = _doc_with_element()
    el.set_attribute("class", "foo")
    before = doc._style_epoch
    el.remove_attribute("class")
    assert doc._style_epoch == before + 1


def test_ac15_remove_other_attribute_no_bump() -> None:
    doc, el = _doc_with_element()
    el.set_attribute("data-x", "1")
    before = doc._style_epoch
    el.remove_attribute("data-x")
    assert doc._style_epoch == before


# ---------------------------------------------------------------------------
# AC-16 — tree mutations bump once per call
# ---------------------------------------------------------------------------


def test_ac16_append_child_bumps_once() -> None:
    doc, parent = _doc_with_element()
    child = doc.create_element("span")
    before = doc._style_epoch
    parent.append_child(child)
    assert doc._style_epoch == before + 1


def test_ac16_remove_child_bumps_once() -> None:
    doc, parent = _doc_with_element()
    child = doc.create_element("span")
    parent.append_child(child)
    before = doc._style_epoch
    parent.remove_child(child)
    assert doc._style_epoch == before + 1


def test_ac16_insert_before_bumps_once() -> None:
    doc, parent = _doc_with_element()
    ref = doc.create_element("a")
    parent.append_child(ref)
    new = doc.create_element("b")
    before = doc._style_epoch
    parent.insert_before(new, ref)
    assert doc._style_epoch == before + 1


def test_ac16_replace_child_bumps_once() -> None:
    doc, parent = _doc_with_element()
    old = doc.create_element("a")
    parent.append_child(old)
    new = doc.create_element("b")
    before = doc._style_epoch
    parent.replace_child(new, old)
    assert doc._style_epoch == before + 1


def test_ac16_orphan_subtree_mutation_no_bump() -> None:
    # A subtree with no owning document never bumps (orphan safety).
    from aspose_html.dom._element import Element

    parent = Element("div", "http://www.w3.org/1999/xhtml")
    child = Element("span", "http://www.w3.org/1999/xhtml")
    assert parent.owner_document is None
    parent.append_child(child)  # must not raise; no document to bump
