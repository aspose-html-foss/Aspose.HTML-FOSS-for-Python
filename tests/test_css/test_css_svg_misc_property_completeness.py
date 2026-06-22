"""CSS SVG presentational + misc property table completeness — BACK-317 / ADR-295.

Covers SPEC-149 AC-1 through AC-51:

  Group A (AC-1..31)  — SVG presentational properties (CSS.supports + shorthand)
  Group B (AC-32..36) — CSS Motion Path (offset-* longhands + offset shorthand)
  Group C (AC-37..39) — CSS Paged Media legacy (page-break-*)
  Group D (AC-40)     — Scroll-snap tail (scroll-snap-stop)
  Group E (AC-41..45) — Misc modern CSS properties
  Group F (AC-46..48) — Legacy grid-gap aliases + text-combine-upright
  Suite   (AC-49..51) — _INITIAL_VALUE_BASELINE count + full-suite + css-module
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSS, CSSStyleSheet
from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_element(css: str) -> object:
    """Return a div element with *css* applied via an attached stylesheet."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(f"div {{ {css} }}")
    doc.attach_style_sheet(sheet)
    return el


def _make_element_inline(prop: str, value: str) -> object:
    """Return a div element with *prop: value* set as inline style."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    el.style[prop] = value
    return el


# ---------------------------------------------------------------------------
# Group A — SVG paint properties (AC-1..12)
# ---------------------------------------------------------------------------


def test_svg_paint_properties_supported() -> None:
    """AC-1 through AC-12: CSS.supports returns True for SVG paint longhands."""
    props = [
        ("fill", "black"),
        ("stroke", "none"),
        ("stroke-width", "1px"),
        ("stroke-dasharray", "none"),
        ("stroke-dashoffset", "0"),
        ("stroke-linecap", "butt"),
        ("stroke-linejoin", "miter"),
        ("stroke-miterlimit", "4"),
        ("stroke-opacity", "1"),
        ("fill-opacity", "1"),
        ("fill-rule", "nonzero"),
        ("clip-rule", "nonzero"),
    ]
    for prop, val in props:
        assert CSS.supports(prop, val), (
            f"CSS.supports({prop!r}, {val!r}) should be True"
        )


# ---------------------------------------------------------------------------
# Group A — SVG color/rendering + filter environment (AC-13..18)
# ---------------------------------------------------------------------------


def test_svg_color_and_rendering_properties_supported() -> None:
    """AC-13 through AC-18: CSS.supports returns True for color/rendering/filter props."""
    props = [
        ("color-interpolation", "sRGB"),
        ("color-interpolation-filters", "linearRGB"),
        ("color-rendering", "auto"),
        ("flood-color", "black"),
        ("flood-opacity", "1"),
        ("lighting-color", "white"),
    ]
    for prop, val in props:
        assert CSS.supports(prop, val), (
            f"CSS.supports({prop!r}, {val!r}) should be True"
        )


# ---------------------------------------------------------------------------
# Group A — SVG marker longhands (AC-19..21)
# ---------------------------------------------------------------------------


def test_svg_marker_longhands_supported() -> None:
    """AC-19 through AC-21: CSS.supports returns True for marker-start/mid/end."""
    for prop in ("marker-start", "marker-mid", "marker-end"):
        assert CSS.supports(prop, "none"), (
            f"CSS.supports({prop!r}, 'none') should be True"
        )


# ---------------------------------------------------------------------------
# Group A — marker shorthand expansion (AC-22)
# ---------------------------------------------------------------------------


def test_svg_marker_shorthand_expands() -> None:
    """AC-22: marker shorthand broadcasts to marker-start, marker-mid, marker-end."""
    el = _make_element("marker: url(#m)")
    style = el.get_computed_style()
    for longhand in ("marker-start", "marker-mid", "marker-end"):
        assert style.get_property_value(longhand) == "url(#m)", (
            f"Expected {longhand!r} to be 'url(#m)' after marker: url(#m), "
            f"got {style.get_property_value(longhand)!r}"
        )


def test_svg_marker_shorthand_inline_expands() -> None:
    """AC-22 (inline variant): el.style['marker'] = 'url(#m)' populates longhands."""
    el = _make_element_inline("marker", "url(#m)")
    style = el.get_computed_style()
    for longhand in ("marker-start", "marker-mid", "marker-end"):
        assert style.get_property_value(longhand) == "url(#m)", (
            f"Expected {longhand!r} to be 'url(#m)' after inline marker: url(#m), "
            f"got {style.get_property_value(longhand)!r}"
        )


# ---------------------------------------------------------------------------
# Group A — SVG rendering, gradient, text, effects (AC-23..31)
# ---------------------------------------------------------------------------


def test_svg_rendering_and_paint_tail_supported() -> None:
    """AC-23 through AC-28: CSS.supports returns True for rendering/paint/text-anchor."""
    props = [
        ("shape-rendering", "auto"),
        ("stop-color", "black"),
        ("stop-opacity", "1"),
        ("text-anchor", "start"),
        ("vector-effect", "none"),
        ("paint-order", "normal"),
    ]
    for prop, val in props:
        assert CSS.supports(prop, val), (
            f"CSS.supports({prop!r}, {val!r}) should be True"
        )


def test_svg_baseline_properties_supported() -> None:
    """AC-29 through AC-31: CSS.supports returns True for baseline properties."""
    props = [
        ("dominant-baseline", "auto"),
        ("alignment-baseline", "auto"),
        ("baseline-shift", "0"),
    ]
    for prop, val in props:
        assert CSS.supports(prop, val), (
            f"CSS.supports({prop!r}, {val!r}) should be True"
        )


# ---------------------------------------------------------------------------
# Group B — CSS Motion Path longhands (AC-32..35)
# ---------------------------------------------------------------------------


def test_offset_longhands_supported() -> None:
    """AC-32 through AC-35: CSS.supports returns True for offset-path/distance/rotate/anchor."""
    props = [
        ("offset-path", "none"),
        ("offset-distance", "0"),
        ("offset-rotate", "auto"),
        ("offset-anchor", "auto"),
    ]
    for prop, val in props:
        assert CSS.supports(prop, val), (
            f"CSS.supports({prop!r}, {val!r}) should be True"
        )


# ---------------------------------------------------------------------------
# Group B — offset shorthand expansion (AC-36)
# ---------------------------------------------------------------------------


def test_offset_shorthand_expands() -> None:
    """AC-36: offset shorthand distributes positionally to offset longhands."""
    el = _make_element("offset: none 0 auto")
    style = el.get_computed_style()
    assert style.get_property_value("offset-path") == "none", (
        f"Expected offset-path='none', got {style.get_property_value('offset-path')!r}"
    )
    assert style.get_property_value("offset-distance") == "0", (
        f"Expected offset-distance='0', got {style.get_property_value('offset-distance')!r}"
    )
    assert style.get_property_value("offset-rotate") == "auto", (
        f"Expected offset-rotate='auto', got {style.get_property_value('offset-rotate')!r}"
    )


def test_offset_shorthand_inline_expands() -> None:
    """AC-36 (inline variant): el.style['offset'] = 'none 0 auto' populates longhands."""
    el = _make_element_inline("offset", "none 0 auto")
    style = el.get_computed_style()
    assert style.get_property_value("offset-path") == "none", (
        f"Expected offset-path='none', got {style.get_property_value('offset-path')!r}"
    )
    assert style.get_property_value("offset-distance") == "0", (
        f"Expected offset-distance='0', got {style.get_property_value('offset-distance')!r}"
    )
    assert style.get_property_value("offset-rotate") == "auto", (
        f"Expected offset-rotate='auto', got {style.get_property_value('offset-rotate')!r}"
    )


# ---------------------------------------------------------------------------
# Group C — CSS Paged Media legacy (AC-37..39)
# ---------------------------------------------------------------------------


def test_page_break_properties_supported() -> None:
    """AC-37 through AC-39: CSS.supports returns True for page-break-* longhands."""
    props = [
        ("page-break-before", "auto"),
        ("page-break-after", "auto"),
        ("page-break-inside", "auto"),
    ]
    for prop, val in props:
        assert CSS.supports(prop, val), (
            f"CSS.supports({prop!r}, {val!r}) should be True"
        )


# ---------------------------------------------------------------------------
# Group D — Scroll-snap tail (AC-40)
# ---------------------------------------------------------------------------


def test_scroll_snap_stop_supported() -> None:
    """AC-40: CSS.supports('scroll-snap-stop', 'normal') returns True."""
    assert CSS.supports("scroll-snap-stop", "normal")


# ---------------------------------------------------------------------------
# Group E — Misc modern CSS (AC-41..45)
# ---------------------------------------------------------------------------


def test_misc_modern_properties_supported() -> None:
    """AC-41 through AC-45: CSS.supports returns True for misc modern CSS properties."""
    props = [
        ("color-scheme", "normal"),
        ("animation-timeline", "auto"),
        ("content-visibility", "visible"),
        ("forced-color-adjust", "auto"),
        ("print-color-adjust", "economy"),
    ]
    for prop, val in props:
        assert CSS.supports(prop, val), (
            f"CSS.supports({prop!r}, {val!r}) should be True"
        )


# ---------------------------------------------------------------------------
# Group F — Legacy grid-gap aliases + writing modes (AC-46..48)
# ---------------------------------------------------------------------------


def test_legacy_grid_gap_and_writing_mode_supported() -> None:
    """AC-46 through AC-48: CSS.supports returns True for grid gap aliases and text-combine-upright."""
    props = [
        ("grid-row-gap", "0px"),
        ("grid-column-gap", "0px"),
        ("text-combine-upright", "none"),
    ]
    for prop, val in props:
        assert CSS.supports(prop, val), (
            f"CSS.supports({prop!r}, {val!r}) should be True"
        )


# ---------------------------------------------------------------------------
# Suite — _INITIAL_VALUE_BASELINE count (AC-49)
# ---------------------------------------------------------------------------


def test_initial_value_baseline_count() -> None:
    """AC-49: _INITIAL_VALUE_BASELINE has exactly 416 entries after Track 114.

    Track 94 established 286; Track 96 (ADR-295) added 48 (334);
    Track 98 (ADR-297, BACK-319) added 19 shorthand registrations (353);
    Track 108 (ADR-307, BACK-328) added 14 longhands + 1 shorthand sentinel (368);
    Track 109 (ADR-308, BACK-329) added 2 inherited longhands (370);
    Track 110 (ADR-309, BACK-330) added 10 CSS property longhands (380);
    Track 111 (ADR-310, BACK-331) added 8 longhands + 1 shorthand sentinel (389);
    Track 112 (ADR-311, BACK-333) added 9 longhands (398);
    Track 113 (ADR-312, BACK-334) added 11 entries (409);
    Track 114 (ADR-313, BACK-335) added 7 entries (416).
    """
    from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE
    assert len(_INITIAL_VALUE_BASELINE) == 416, (
        f"Expected 416 entries, got {len(_INITIAL_VALUE_BASELINE)}"
    )


# ---------------------------------------------------------------------------
# AC-50: Stylesheet resolution for SVG properties
# ---------------------------------------------------------------------------


def test_stylesheet_svg_property_resolution() -> None:
    """AC-50 (representative): stylesheet with SVG properties resolves correctly."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "div { fill: red; stroke: blue; dominant-baseline: middle; "
        "flood-color: white; paint-order: stroke; }"
    )
    doc.attach_style_sheet(sheet)
    style = el.get_computed_style()
    assert style.get_property_value("fill") == "red"
    assert style.get_property_value("stroke") == "blue"
    assert style.get_property_value("dominant-baseline") == "middle"
    assert style.get_property_value("flood-color") == "white"
    assert style.get_property_value("paint-order") == "stroke"


# ---------------------------------------------------------------------------
# AC-51: CSS module regression guard (run via pytest test_css/ -x)
# ---------------------------------------------------------------------------


def test_no_regression_on_known_css_supports() -> None:
    """AC-51 (guard): pre-existing CSS.supports() calls continue to return True."""
    # Sample of properties from previous tracks — must not regress
    known_properties = [
        ("color", "red"),
        ("background-color", "blue"),
        ("margin", "0"),
        ("padding", "10px"),
        ("font-size", "16px"),
        ("display", "block"),
        ("position", "relative"),
        ("flex", "1"),
        ("grid-template-columns", "1fr"),
        ("scroll-snap-type", "x mandatory"),
        ("scroll-snap-align", "start"),
        ("mask-image", "none"),
        ("overscroll-behavior", "auto"),
        ("text-decoration", "none"),
    ]
    for prop, val in known_properties:
        assert CSS.supports(prop, val), (
            f"Regression: CSS.supports({prop!r}, {val!r}) should be True"
        )
