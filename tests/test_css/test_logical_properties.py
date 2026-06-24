"""Tests for CSS Logical Properties Level 1 — , .

Covers all five property groups (logical margin, padding, border, sizing,
inset) and verifies that:

- Every longhand is registered in ``_KNOWN_PROPERTIES`` (CSS.supports returns
  True, get_computed_style returns the declared value).
- Axis shorthands (margin-block, padding-inline, inset-block, etc.) expand
  via the CSS two-value box-model rule.
- Per-side border shorthands expand to three longhands (width/style/color)
  using the same classifier as border-top/right/bottom/left.
- Axis border shorthands (border-block, border-inline) expand to six longhands.
- Logical properties are independent of their physical counterparts (FR-11).
- Existing physical shorthands still work correctly (regression, AC-13).
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSS, CSSStyleSheet
from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_el(css: str) -> object:
    """Create a document with one ``div`` styled via an attached stylesheet."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(f"div {{ {css} }}")
    doc.attach_style_sheet(sheet)
    return el


def _computed(css: str, prop: str) -> str:
    return _make_el(css).get_computed_style().get_property_value(prop)


def _inline_computed(prop: str, value: str) -> str:
    """Set *value* on element inline style and return computed value."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    el.style[prop] = value
    return el.get_computed_style().get_property_value(prop)


def _inline_computed_pair(shorthand: str, value: str, start_prop: str, end_prop: str) -> tuple[str, str]:
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    el.style[shorthand] = value
    style = el.get_computed_style()
    return style.get_property_value(start_prop), style.get_property_value(end_prop)


# ---------------------------------------------------------------------------
# AC-1 / FR-1: Logical margin longhands
# ---------------------------------------------------------------------------

class TestLogicalMarginLonghands:
    """Logical margin longhands register and store values independently."""

    def test_margin_block_start_longhand_direct(self) -> None:
        """AC-1: margin-block-start set directly returns the stored value."""
        assert _inline_computed("margin-block-start", "10px") == "10px"

    def test_margin_block_end_longhand_direct(self) -> None:
        assert _inline_computed("margin-block-end", "15px") == "15px"

    def test_margin_inline_start_longhand_direct(self) -> None:
        assert _inline_computed("margin-inline-start", "5px") == "5px"

    def test_margin_inline_end_longhand_direct(self) -> None:
        assert _inline_computed("margin-inline-end", "20px") == "20px"

    def test_margin_block_start_via_stylesheet(self) -> None:
        assert _computed("margin-block-start: 10px", "margin-block-start") == "10px"

    def test_logical_margin_independent_of_physical(self) -> None:
        """FR-11: setting margin-inline-start does not alter margin-left."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["margin-inline-start"] = "99px"
        style = el.get_computed_style()
        assert style.get_property_value("margin-inline-start") == "99px"
        # margin-left must remain at its initial empty value
        assert style.get_property_value("margin-left") == ""


# ---------------------------------------------------------------------------
# AC-2 / AC-3 / FR-2: margin-block and margin-inline two-value axis
# ---------------------------------------------------------------------------

class TestMarginAxisShorthands:
    """margin-block / margin-inline expand via the two-value box-model rule."""

    def test_margin_block_two_value_split(self) -> None:
        """AC-2: margin-block: 10px 20px → start=10px, end=20px."""
        start, end = _inline_computed_pair(
            "margin-block", "10px 20px", "margin-block-start", "margin-block-end"
        )
        assert start == "10px"
        assert end == "20px"

    def test_margin_block_one_value_broadcasts(self) -> None:
        """AC-2 (one-value form): margin-block: 5px → both sides 5px."""
        start, end = _inline_computed_pair(
            "margin-block", "5px", "margin-block-start", "margin-block-end"
        )
        assert start == "5px"
        assert end == "5px"

    def test_margin_inline_two_value_split(self) -> None:
        start, end = _inline_computed_pair(
            "margin-inline", "8px 12px", "margin-inline-start", "margin-inline-end"
        )
        assert start == "8px"
        assert end == "12px"

    def test_margin_inline_one_value_broadcasts(self) -> None:
        """AC-3: margin-inline: 5px → both margin-inline-start and margin-inline-end are 5px."""
        start, end = _inline_computed_pair(
            "margin-inline", "5px", "margin-inline-start", "margin-inline-end"
        )
        assert start == "5px"
        assert end == "5px"

    def test_margin_block_via_stylesheet(self) -> None:
        """margin-block shorthand works via an attached stylesheet too."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { margin-block: 3px 7px }")
        doc.attach_style_sheet(sheet)
        style = el.get_computed_style()
        assert style.get_property_value("margin-block-start") == "3px"
        assert style.get_property_value("margin-block-end") == "7px"


# ---------------------------------------------------------------------------
# AC-4 / FR-3 / FR-4: Logical padding
# ---------------------------------------------------------------------------

class TestLogicalPadding:
    """Logical padding longhands and axis shorthands."""

    def test_padding_block_start_longhand(self) -> None:
        assert _inline_computed("padding-block-start", "8px") == "8px"

    def test_padding_block_end_longhand(self) -> None:
        assert _inline_computed("padding-block-end", "12px") == "12px"

    def test_padding_inline_start_longhand(self) -> None:
        assert _inline_computed("padding-inline-start", "4px") == "4px"

    def test_padding_inline_end_longhand(self) -> None:
        assert _inline_computed("padding-inline-end", "6px") == "6px"

    def test_padding_block_two_value_split(self) -> None:
        """AC-4: padding-block: 8px 12px → start=8px, end=12px."""
        start, end = _inline_computed_pair(
            "padding-block", "8px 12px", "padding-block-start", "padding-block-end"
        )
        assert start == "8px"
        assert end == "12px"

    def test_padding_inline_one_value_broadcasts(self) -> None:
        start, end = _inline_computed_pair(
            "padding-inline", "5px", "padding-inline-start", "padding-inline-end"
        )
        assert start == "5px"
        assert end == "5px"

    def test_padding_inline_two_value_split(self) -> None:
        start, end = _inline_computed_pair(
            "padding-inline", "3px 9px", "padding-inline-start", "padding-inline-end"
        )
        assert start == "3px"
        assert end == "9px"


# ---------------------------------------------------------------------------
# AC-5 / FR-5 / FR-6: Logical border per-side shorthands
# ---------------------------------------------------------------------------

class TestLogicalBorderPerSideShorthands:
    """Per-side logical border shorthands expand to width/style/color."""

    def _set_border(self, shorthand: str, value: str) -> tuple[str, str, str]:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style[shorthand] = value
        style = el.get_computed_style()
        prefix = shorthand  # e.g. "border-block-start"
        return (
            style.get_property_value(f"{prefix}-width"),
            style.get_property_value(f"{prefix}-style"),
            style.get_property_value(f"{prefix}-color"),
        )

    def test_border_block_start_expands(self) -> None:
        """AC-5: border-block-start: 2px solid blue → width/style/color."""
        width, style, color = self._set_border("border-block-start", "2px solid blue")
        assert width == "2px"
        assert style == "solid"
        assert color == "blue"

    def test_border_block_end_expands(self) -> None:
        width, style, color = self._set_border("border-block-end", "1px dashed red")
        assert width == "1px"
        assert style == "dashed"
        assert color == "red"

    def test_border_inline_start_expands(self) -> None:
        """FR-6: border-inline-start: 3px dotted green → three longhands."""
        width, style, color = self._set_border("border-inline-start", "3px dotted green")
        assert width == "3px"
        assert style == "dotted"
        assert color == "green"

    def test_border_inline_end_expands(self) -> None:
        width, style, color = self._set_border("border-inline-end", "4px double navy")
        assert width == "4px"
        assert style == "double"
        assert color == "navy"

    def test_border_block_start_via_stylesheet(self) -> None:
        """Stylesheet-applied border-block-start shorthand."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { border-block-start: 2px solid blue }")
        doc.attach_style_sheet(sheet)
        style = el.get_computed_style()
        assert style.get_property_value("border-block-start-width") == "2px"
        assert style.get_property_value("border-block-start-style") == "solid"
        assert style.get_property_value("border-block-start-color") == "blue"


# ---------------------------------------------------------------------------
# AC-6 / FR-7: Axis border shorthands (6 longhands)
# ---------------------------------------------------------------------------

class TestLogicalBorderAxisShorthands:
    """border-block and border-inline expand to 6 longhands uniformly."""

    def test_border_block_expands_to_six_longhands(self) -> None:
        """AC-6: border-block: 1px dashed red → all six block border longhands."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["border-block"] = "1px dashed red"
        style = el.get_computed_style()
        for side in ("start", "end"):
            assert style.get_property_value(f"border-block-{side}-width") == "1px", side
            assert style.get_property_value(f"border-block-{side}-style") == "dashed", side
            assert style.get_property_value(f"border-block-{side}-color") == "red", side

    def test_border_inline_expands_to_six_longhands(self) -> None:
        """FR-7: border-inline: 2px solid black → all six inline border longhands."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["border-inline"] = "2px solid black"
        style = el.get_computed_style()
        for side in ("start", "end"):
            assert style.get_property_value(f"border-inline-{side}-width") == "2px", side
            assert style.get_property_value(f"border-inline-{side}-style") == "solid", side
            assert style.get_property_value(f"border-inline-{side}-color") == "black", side

    def test_border_block_via_stylesheet(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { border-block: 1px dashed red }")
        doc.attach_style_sheet(sheet)
        style = el.get_computed_style()
        assert style.get_property_value("border-block-start-width") == "1px"
        assert style.get_property_value("border-block-end-style") == "dashed"
        assert style.get_property_value("border-block-start-color") == "red"
        assert style.get_property_value("border-block-end-color") == "red"


# ---------------------------------------------------------------------------
# AC-7 / AC-8 / FR-8: Logical sizing
# ---------------------------------------------------------------------------

class TestLogicalSizing:
    """Logical sizing longhands register with correct initial values."""

    def test_block_size_longhand(self) -> None:
        """AC-7: block-size: 100px → stored and returned."""
        assert _inline_computed("block-size", "100px") == "100px"

    def test_inline_size_longhand(self) -> None:
        assert _inline_computed("inline-size", "50%") == "50%"

    def test_min_inline_size_longhand(self) -> None:
        """AC-8: min-inline-size: 50px → stored and returned."""
        assert _inline_computed("min-inline-size", "50px") == "50px"

    def test_max_block_size_longhand(self) -> None:
        assert _inline_computed("max-block-size", "200px") == "200px"

    def test_min_block_size_longhand(self) -> None:
        assert _inline_computed("min-block-size", "30px") == "30px"

    def test_max_inline_size_longhand(self) -> None:
        assert _inline_computed("max-inline-size", "none") == "none"

    def test_block_size_initial_value_is_auto(self) -> None:
        """block-size initial value must be 'auto' (matching physical height)."""
        from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE
        assert _INITIAL_VALUE_BASELINE["block-size"] == "auto"

    def test_max_block_size_initial_value_is_none(self) -> None:
        """max-block-size initial value must be 'none' (matching max-height)."""
        from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE
        assert _INITIAL_VALUE_BASELINE["max-block-size"] == "none"

    def test_min_block_size_initial_value_is_auto(self) -> None:
        from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE
        assert _INITIAL_VALUE_BASELINE["min-block-size"] == "auto"

    def test_max_inline_size_initial_value_is_none(self) -> None:
        from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE
        assert _INITIAL_VALUE_BASELINE["max-inline-size"] == "none"


# ---------------------------------------------------------------------------
# AC-9 / AC-10 / FR-9 / FR-10: Logical inset
# ---------------------------------------------------------------------------

class TestLogicalInset:
    """Logical inset longhands and axis shorthands."""

    def test_inset_block_start_longhand(self) -> None:
        assert _inline_computed("inset-block-start", "5px") == "5px"

    def test_inset_block_end_longhand(self) -> None:
        assert _inline_computed("inset-block-end", "10px") == "10px"

    def test_inset_inline_start_longhand(self) -> None:
        assert _inline_computed("inset-inline-start", "15px") == "15px"

    def test_inset_inline_end_longhand(self) -> None:
        assert _inline_computed("inset-inline-end", "20px") == "20px"

    def test_inset_block_two_value_split(self) -> None:
        """AC-9: inset-block: 10px 20px → start=10px, end=20px."""
        start, end = _inline_computed_pair(
            "inset-block", "10px 20px", "inset-block-start", "inset-block-end"
        )
        assert start == "10px"
        assert end == "20px"

    def test_inset_inline_one_value_broadcasts(self) -> None:
        """AC-10: inset-inline: 5px → both inset-inline-start and inset-inline-end are 5px."""
        start, end = _inline_computed_pair(
            "inset-inline", "5px", "inset-inline-start", "inset-inline-end"
        )
        assert start == "5px"
        assert end == "5px"

    def test_inset_block_one_value_broadcasts(self) -> None:
        start, end = _inline_computed_pair(
            "inset-block", "8px", "inset-block-start", "inset-block-end"
        )
        assert start == "8px"
        assert end == "8px"

    def test_inset_inline_two_value_split(self) -> None:
        start, end = _inline_computed_pair(
            "inset-inline", "3px 7px", "inset-inline-start", "inset-inline-end"
        )
        assert start == "3px"
        assert end == "7px"

    def test_inset_block_initial_values_are_auto(self) -> None:
        from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE
        assert _INITIAL_VALUE_BASELINE["inset-block-start"] == "auto"
        assert _INITIAL_VALUE_BASELINE["inset-block-end"] == "auto"
        assert _INITIAL_VALUE_BASELINE["inset-inline-start"] == "auto"
        assert _INITIAL_VALUE_BASELINE["inset-inline-end"] == "auto"


# ---------------------------------------------------------------------------
# AC-11 / AC-12: CSS.supports
# ---------------------------------------------------------------------------

class TestCSSSupports:
    """CSS.supports returns True for all new logical property longhands."""

    def test_margin_inline_start_supported(self) -> None:
        """AC-11: CSS.supports('margin-inline-start', '10px') is True."""
        assert CSS.supports("margin-inline-start", "10px") is True

    def test_block_size_supported(self) -> None:
        """AC-12: CSS.supports('block-size', 'auto') is True."""
        assert CSS.supports("block-size", "auto") is True

    def test_all_margin_longhands_supported(self) -> None:
        for prop in (
            "margin-block-start", "margin-block-end",
            "margin-inline-start", "margin-inline-end",
        ):
            assert CSS.supports(prop, "10px") is True, f"Expected CSS.supports({prop!r}) True"

    def test_all_padding_longhands_supported(self) -> None:
        for prop in (
            "padding-block-start", "padding-block-end",
            "padding-inline-start", "padding-inline-end",
        ):
            assert CSS.supports(prop, "5px") is True, f"Expected CSS.supports({prop!r}) True"

    def test_all_border_longhands_supported(self) -> None:
        for prop in (
            "border-block-start-width", "border-block-start-style", "border-block-start-color",
            "border-block-end-width", "border-block-end-style", "border-block-end-color",
            "border-inline-start-width", "border-inline-start-style", "border-inline-start-color",
            "border-inline-end-width", "border-inline-end-style", "border-inline-end-color",
        ):
            assert CSS.supports(prop, "1px") is True, f"Expected CSS.supports({prop!r}) True"

    def test_all_sizing_longhands_supported(self) -> None:
        for prop in ("block-size", "inline-size", "min-block-size",
                     "max-block-size", "min-inline-size", "max-inline-size"):
            assert CSS.supports(prop, "auto") is True, f"Expected CSS.supports({prop!r}) True"

    def test_all_inset_longhands_supported(self) -> None:
        for prop in (
            "inset-block-start", "inset-block-end",
            "inset-inline-start", "inset-inline-end",
        ):
            assert CSS.supports(prop, "5px") is True, f"Expected CSS.supports({prop!r}) True"


# ---------------------------------------------------------------------------
# AC-13: Regression — existing physical properties unchanged
# ---------------------------------------------------------------------------

class TestRegressionPhysicalProperties:
    """Existing physical shorthand expansions are unaffected (AC-13)."""

    def test_margin_four_value_still_works(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["margin"] = "10px 20px 30px 40px"
        style = el.get_computed_style()
        assert style.get_property_value("margin-top") == "10px"
        assert style.get_property_value("margin-right") == "20px"
        assert style.get_property_value("margin-bottom") == "30px"
        assert style.get_property_value("margin-left") == "40px"

    def test_padding_two_value_still_works(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["padding"] = "5px 15px"
        style = el.get_computed_style()
        assert style.get_property_value("padding-top") == "5px"
        assert style.get_property_value("padding-right") == "15px"
        assert style.get_property_value("padding-bottom") == "5px"
        assert style.get_property_value("padding-left") == "15px"

    def test_border_top_still_works(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["border-top"] = "2px solid red"
        style = el.get_computed_style()
        assert style.get_property_value("border-top-width") == "2px"
        assert style.get_property_value("border-top-style") == "solid"
        assert style.get_property_value("border-top-color") == "red"

    def test_border_shorthand_still_works(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["border"] = "1px dashed blue"
        style = el.get_computed_style()
        for side in ("top", "right", "bottom", "left"):
            assert style.get_property_value(f"border-{side}-width") == "1px"
            assert style.get_property_value(f"border-{side}-style") == "dashed"
            assert style.get_property_value(f"border-{side}-color") == "blue"

    def test_inset_physical_still_works(self) -> None:
        """Physical inset shorthand (top/right/bottom/left) is unaffected."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["inset"] = "10px 20px"
        style = el.get_computed_style()
        assert style.get_property_value("top") == "10px"
        assert style.get_property_value("right") == "20px"
        assert style.get_property_value("bottom") == "10px"
        assert style.get_property_value("left") == "20px"

    def test_logical_does_not_bleed_into_physical(self) -> None:
        """FR-11: setting margin-block-start must not alter margin-top."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        el.style["margin-block-start"] = "42px"
        style = el.get_computed_style()
        assert style.get_property_value("margin-block-start") == "42px"
        assert style.get_property_value("margin-top") == ""
