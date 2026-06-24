"""Tests for ComputedStyle + computed_style — M7.1 ( / ).

Covers AC-1 (package surface), AC-2 (slots / immutability), AC-3 (read
accessor parity with ComputedStyleDeclaration), AC-4 (read-only epoch),
and AC-7 (cache identity / invalidation), plus the orphan-element path.
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document
from aspose_html.dom._cascade import ComputedStyleDeclaration
import aspose_html.layout as layout_pkg
from aspose_html.layout import ComputedStyle, bump_style_epoch, computed_style


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _styled_element():
    """Return (doc, element) with a single 'div { color: red }' sheet attached."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: red; margin: 0 }")
    doc.attach_style_sheet(sheet)
    return doc, el


# ---------------------------------------------------------------------------
# AC-1 — package surface
# ---------------------------------------------------------------------------


def test_ac1_package_exports() -> None:
    # M7.4 exports add inline-layout entrypoint + inline fragment records.
    assert set(layout_pkg.__all__) == {
        "ComputedStyle",
        "computed_style",
        "bump_style_epoch",
        "BoxNode",
        "BoxRoot",
        "Display",
        "build_box_tree",
        "classify_display",
        "EdgeSizes",
        "BlockFragment",
        "FragmentRoot",
        "layout_block_tree",
        "ShapedRun",
        "InlineTextFragment",
        "LineFragment",
        "layout_inline_fragments",
        "PageMarginBoxes",
        "PageFragment",
        "paginate_fragments",
    }
    assert layout_pkg.ComputedStyle is ComputedStyle
    assert layout_pkg.computed_style is computed_style
    assert layout_pkg.bump_style_epoch is bump_style_epoch
    # Module docstring present and explains the package.
    assert layout_pkg.__doc__ is not None
    assert "layout" in layout_pkg.__doc__.lower()


def test_ac1_package_submodules_exist() -> None:
    from aspose_html.layout import _computed_style, _style_cache

    assert hasattr(_computed_style, "ComputedStyle")
    assert hasattr(_style_cache, "computed_style")
    assert hasattr(_style_cache, "bump_style_epoch")


# ---------------------------------------------------------------------------
# AC-2 — slots / immutability
# ---------------------------------------------------------------------------


def test_ac2_slots_exact() -> None:
    assert ComputedStyle.__slots__ == ("_decl", "_epoch")


def test_ac2_no_extra_attributes() -> None:
    rs = ComputedStyle(ComputedStyleDeclaration({"color": "red"}), 0)
    with pytest.raises(AttributeError):
        rs.extra = "nope"  # type: ignore[attr-defined]
    # No __dict__ either.
    assert not hasattr(rs, "__dict__")


# ---------------------------------------------------------------------------
# AC-3 — read-accessor parity with ComputedStyleDeclaration
# ---------------------------------------------------------------------------


def test_ac3_accessors_byte_identical() -> None:
    decl = ComputedStyleDeclaration({"color": "red", "margin": "0"})
    rs = ComputedStyle(decl, 0)

    # get mirrors get_property_value (returns '' for absent, never raises).
    assert rs.get("color") == decl.get_property_value("color") == "red"
    assert rs.get("not-present") == decl.get_property_value("not-present") == ""

    # __getitem__ mirrors ComputedStyleDeclaration.__getitem__ (raises KeyError).
    assert rs["color"] == decl["color"]
    with pytest.raises(KeyError):
        _ = rs["not-present"]

    # __contains__ / __iter__ / __len__ delegate.
    assert ("color" in rs) == ("color" in decl) is True
    assert ("not-present" in rs) == ("not-present" in decl) is False
    assert list(rs) == list(decl)
    assert len(rs) == len(decl) == 2


# ---------------------------------------------------------------------------
# AC-4 — read-only epoch
# ---------------------------------------------------------------------------


def test_ac4_epoch_returns_construction_value() -> None:
    rs = ComputedStyle(ComputedStyleDeclaration({}), 42)
    assert rs.epoch == 42


def test_ac4_epoch_is_read_only() -> None:
    rs = ComputedStyle(ComputedStyleDeclaration({}), 1)
    with pytest.raises(AttributeError):
        rs.epoch = 2  # type: ignore[misc]


# ---------------------------------------------------------------------------
# AC-7 — cache identity and invalidation
# ---------------------------------------------------------------------------


def test_ac7_same_object_without_bump() -> None:
    _doc, el = _styled_element()
    first = computed_style(el)
    second = computed_style(el)
    assert first is second


def test_ac7_fresh_object_after_bump() -> None:
    doc, el = _styled_element()
    first = computed_style(el)
    epoch_before = first.epoch
    doc._bump_style_epoch()
    second = computed_style(el)
    assert second is not first
    assert second.epoch == epoch_before + 1


def test_ac7_computed_style_reflects_cascade_value() -> None:
    _doc, el = _styled_element()
    rs = computed_style(el)
    assert rs.get("color") == "red"
    assert rs.get("color") == el.get_computed_style().get_property_value("color")


# ---------------------------------------------------------------------------
# Orphan-element path ( — uncached, epoch 0)
# ---------------------------------------------------------------------------


def test_orphan_element_uncached_epoch_zero() -> None:
    # A truly document-less element (constructed without an owner document)
    # resolves uncached at epoch 0 — there is no Document to own the cache.
    from aspose_html.dom._element import Element

    orphan = Element("span", "http://www.w3.org/1999/xhtml")
    assert orphan.owner_document is None
    rs = computed_style(orphan)
    assert isinstance(rs, ComputedStyle)
    assert rs.epoch == 0
    # Each call produces a fresh object (no cache for orphans).
    assert computed_style(orphan) is not rs


def test_bump_style_epoch_helper_matches_method() -> None:
    doc = Document()
    assert doc._style_epoch == 0
    bump_style_epoch(doc)
    assert doc._style_epoch == 1
    doc._bump_style_epoch()
    assert doc._style_epoch == 2
