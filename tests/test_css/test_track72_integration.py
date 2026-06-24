""" integration matrix — CSS computed-style property completeness.

Exercises the full cascade pipeline (HTMLDocument -> stylesheet attachment ->
get_computed_style -> get_property_value) for the expanded CSS property surface
added in  (property table) and  (shorthand expansion).

Groups:
  A: Layout properties (position, overflow-x, box-sizing, z-index, object-fit,
     visibility)
  B: Flexbox properties (flex-direction, flex-wrap, justify-content, align-items,
     flex-grow, align-self)
  C: Grid properties (grid-template-columns, grid-auto-flow, grid-column-start,
     grid-area)
  D: Transform and visual properties (transform, opacity, filter, mix-blend-mode)
  E: Transition and animation properties (transition-duration,
     transition-timing-function, animation-name, animation-iteration-count)
  F: Shorthand broadcast end-to-end (flex, gap, border-radius, transition,
     animation, flex-flow)
  G: CSS.supports for new property names
  H: Doctest sweep of _cascade.py

"""
from __future__ import annotations

import doctest

import pytest

from aspose_html.cssom import CSS, CSSStyleSheet
from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_doc(selector: str, css: str) -> object:
    """Return an element styled by a single rule.

    Creates a ``Document``, appends one element matching *selector*, attaches
    a stylesheet with the given *css* rule, and returns the element.
    """
    tag = selector.split(":")[0].split("[")[0].strip()
    doc = Document()
    el = doc.create_element(tag)
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(f"{selector} {{ {css} }}")
    doc.attach_style_sheet(sheet)
    return el


# ---------------------------------------------------------------------------
# Group A — Layout properties via computed style
# ---------------------------------------------------------------------------


class TestGroupALayoutProperties:
    """Group A: common layout properties resolve from a stylesheet rule."""

    def test_position_absolute(self) -> None:
        """position: absolute resolves to 'absolute'."""
        el = _make_doc("div", "position: absolute")
        assert el.get_computed_style().get_property_value("position") == "absolute"

    def test_overflow_x_hidden(self) -> None:
        """overflow-x: hidden resolves to 'hidden'."""
        el = _make_doc("div", "overflow-x: hidden")
        assert el.get_computed_style().get_property_value("overflow-x") == "hidden"

    def test_box_sizing_border_box(self) -> None:
        """box-sizing: border-box resolves to 'border-box'."""
        el = _make_doc("div", "box-sizing: border-box")
        assert el.get_computed_style().get_property_value("box-sizing") == "border-box"

    def test_z_index(self) -> None:
        """z-index: 10 resolves to '10'."""
        el = _make_doc("div", "z-index: 10")
        assert el.get_computed_style().get_property_value("z-index") == "10"

    def test_object_fit_contain(self) -> None:
        """object-fit: contain resolves to 'contain'."""
        el = _make_doc("div", "object-fit: contain")
        assert el.get_computed_style().get_property_value("object-fit") == "contain"

    def test_visibility_hidden(self) -> None:
        """visibility: hidden resolves to 'hidden'."""
        el = _make_doc("div", "visibility: hidden")
        assert el.get_computed_style().get_property_value("visibility") == "hidden"


# ---------------------------------------------------------------------------
# Group B — Flexbox properties end-to-end
# ---------------------------------------------------------------------------


class TestGroupBFlexboxProperties:
    """Group B: flex sub-properties resolve from a stylesheet rule."""

    def test_flex_direction_column(self) -> None:
        """flex-direction: column resolves to 'column'."""
        el = _make_doc("div", "flex-direction: column")
        assert el.get_computed_style().get_property_value("flex-direction") == "column"

    def test_flex_wrap(self) -> None:
        """flex-wrap: wrap resolves to 'wrap'."""
        el = _make_doc("div", "flex-wrap: wrap")
        assert el.get_computed_style().get_property_value("flex-wrap") == "wrap"

    def test_justify_content_center(self) -> None:
        """justify-content: center resolves to 'center'."""
        el = _make_doc("div", "justify-content: center")
        assert el.get_computed_style().get_property_value("justify-content") == "center"

    def test_align_items_flex_start(self) -> None:
        """align-items: flex-start resolves to 'flex-start'."""
        el = _make_doc("div", "align-items: flex-start")
        assert el.get_computed_style().get_property_value("align-items") == "flex-start"

    def test_flex_grow(self) -> None:
        """flex-grow: 2 resolves to '2'."""
        el = _make_doc("div", "flex-grow: 2")
        assert el.get_computed_style().get_property_value("flex-grow") == "2"

    def test_align_self_stretch(self) -> None:
        """align-self: stretch resolves to 'stretch'."""
        el = _make_doc("div", "align-self: stretch")
        assert el.get_computed_style().get_property_value("align-self") == "stretch"


# ---------------------------------------------------------------------------
# Group C — Grid properties end-to-end
# ---------------------------------------------------------------------------


class TestGroupCGridProperties:
    """Group C: grid properties resolve from a stylesheet rule."""

    def test_grid_template_columns(self) -> None:
        """grid-template-columns: 1fr 1fr resolves to '1fr 1fr'."""
        el = _make_doc("div", "grid-template-columns: 1fr 1fr")
        assert (
            el.get_computed_style().get_property_value("grid-template-columns")
            == "1fr 1fr"
        )

    def test_grid_auto_flow_column(self) -> None:
        """grid-auto-flow: column resolves to 'column'."""
        el = _make_doc("div", "grid-auto-flow: column")
        assert el.get_computed_style().get_property_value("grid-auto-flow") == "column"

    def test_grid_column_start(self) -> None:
        """grid-column-start: 2 resolves to '2'."""
        el = _make_doc("div", "grid-column-start: 2")
        assert el.get_computed_style().get_property_value("grid-column-start") == "2"

    def test_grid_area(self) -> None:
        """grid-area: header expands all four grid placement longhands to 'header'.

        Updated by  / : grid-area is now a recognised shorthand
        that expands to grid-row-start, grid-column-start, grid-row-end,
        grid-column-end.  The shorthand itself returns '' from get_computed_style
        because the cascade stores only the resolved longhands.
        """
        el = _make_doc("div", "grid-area: header")
        style = el.get_computed_style()
        assert style.get_property_value("grid-row-start") == "header"
        assert style.get_property_value("grid-column-start") == "header"
        assert style.get_property_value("grid-row-end") == "header"
        assert style.get_property_value("grid-column-end") == "header"


# ---------------------------------------------------------------------------
# Group D — Transform and visual properties
# ---------------------------------------------------------------------------


class TestGroupDTransformAndVisual:
    """Group D: transform and visual effect properties resolve end-to-end."""

    def test_transform(self) -> None:
        """transform: translateX(10px) resolves correctly."""
        el = _make_doc("div", "transform: translateX(10px)")
        assert (
            el.get_computed_style().get_property_value("transform")
            == "translateX(10px)"
        )

    def test_opacity(self) -> None:
        """opacity: 0.5 resolves to '0.5'."""
        el = _make_doc("div", "opacity: 0.5")
        assert el.get_computed_style().get_property_value("opacity") == "0.5"

    def test_filter(self) -> None:
        """filter: blur(4px) resolves to 'blur(4px)'."""
        el = _make_doc("div", "filter: blur(4px)")
        assert el.get_computed_style().get_property_value("filter") == "blur(4px)"

    def test_mix_blend_mode(self) -> None:
        """mix-blend-mode: multiply resolves to 'multiply'."""
        el = _make_doc("div", "mix-blend-mode: multiply")
        assert (
            el.get_computed_style().get_property_value("mix-blend-mode") == "multiply"
        )


# ---------------------------------------------------------------------------
# Group E — Transition and animation properties
# ---------------------------------------------------------------------------


class TestGroupETransitionAnimation:
    """Group E: transition and animation sub-properties resolve end-to-end."""

    def test_transition_duration(self) -> None:
        """transition-duration: 0.3s resolves to '0.3s'."""
        el = _make_doc("div", "transition-duration: 0.3s")
        assert (
            el.get_computed_style().get_property_value("transition-duration") == "0.3s"
        )

    def test_transition_timing_function(self) -> None:
        """transition-timing-function: ease-in resolves to 'ease-in'."""
        el = _make_doc("div", "transition-timing-function: ease-in")
        assert (
            el.get_computed_style().get_property_value("transition-timing-function")
            == "ease-in"
        )

    def test_animation_name(self) -> None:
        """animation-name: slide resolves to 'slide'."""
        el = _make_doc("div", "animation-name: slide")
        assert el.get_computed_style().get_property_value("animation-name") == "slide"

    def test_animation_iteration_count(self) -> None:
        """animation-iteration-count: infinite resolves to 'infinite'."""
        el = _make_doc("div", "animation-iteration-count: infinite")
        assert (
            el.get_computed_style().get_property_value("animation-iteration-count")
            == "infinite"
        )


# ---------------------------------------------------------------------------
# Group F — Shorthand broadcast end-to-end
# ---------------------------------------------------------------------------


class TestGroupFShorthandBroadcast:
    """Group F: shorthand rules broadcast value to all longhands via the cascade."""

    def test_flex_broadcasts_to_longhands(self) -> None:
        """flex: 1 causes flex-grow, flex-shrink, flex-basis to all be non-empty."""
        el = _make_doc("div", "flex: 1")
        style = el.get_computed_style()
        assert style.get_property_value("flex-grow") != ""
        assert style.get_property_value("flex-shrink") != ""
        assert style.get_property_value("flex-basis") != ""

    def test_gap_broadcasts_to_row_and_column_gap(self) -> None:
        """gap: 16px causes row-gap and column-gap to both be non-empty."""
        el = _make_doc("div", "gap: 16px")
        style = el.get_computed_style()
        assert style.get_property_value("row-gap") != ""
        assert style.get_property_value("column-gap") != ""

    def test_border_radius_broadcasts_to_four_corners(self) -> None:
        """border-radius: 8px broadcasts to all four corner sub-properties."""
        el = _make_doc("div", "border-radius: 8px")
        style = el.get_computed_style()
        assert style.get_property_value("border-top-left-radius") != ""
        assert style.get_property_value("border-top-right-radius") != ""
        assert style.get_property_value("border-bottom-right-radius") != ""
        assert style.get_property_value("border-bottom-left-radius") != ""

    def test_transition_shorthand_broadcasts_to_longhands(self) -> None:
        """transition: all 0.2s broadcasts to transition-property, duration, timing, delay."""
        el = _make_doc("div", "transition: all")
        style = el.get_computed_style()
        assert style.get_property_value("transition-property") != ""
        assert style.get_property_value("transition-duration") != ""
        assert style.get_property_value("transition-timing-function") != ""
        assert style.get_property_value("transition-delay") != ""

    def test_animation_shorthand_broadcasts_to_longhands(self) -> None:
        """animation: spin 1s linear infinite broadcasts to animation-name, duration."""
        el = _make_doc("div", "animation: spin")
        style = el.get_computed_style()
        assert style.get_property_value("animation-name") != ""
        assert style.get_property_value("animation-duration") != ""

    def test_flex_flow_broadcasts_to_direction_and_wrap(self) -> None:
        """flex-flow: row-reverse nowrap broadcasts to flex-direction and flex-wrap."""
        el = _make_doc("div", "flex-flow: row")
        style = el.get_computed_style()
        assert style.get_property_value("flex-direction") != ""
        assert style.get_property_value("flex-wrap") != ""


# ---------------------------------------------------------------------------
# Group G — CSS.supports for new properties
# ---------------------------------------------------------------------------


class TestGroupGCSSSupports:
    """Group G: CSS.supports() returns correct results for new and unknown properties."""

    def test_flex_direction_supported(self) -> None:
        """CSS.supports('flex-direction', 'row') is truthy."""
        assert CSS.supports("flex-direction", "row") is True

    def test_transform_none_supported(self) -> None:
        """CSS.supports('transform', 'none') is truthy."""
        assert CSS.supports("transform", "none") is True

    def test_unknown_property_not_supported(self) -> None:
        """CSS.supports('unknown-prop', 'foo') is falsy."""
        assert CSS.supports("unknown-prop", "foo") is False

    def test_animation_name_supported(self) -> None:
        """CSS.supports('animation-name', 'none') is truthy."""
        assert CSS.supports("animation-name", "none") is True


# ---------------------------------------------------------------------------
# Group H — Doctest sweep
# ---------------------------------------------------------------------------


def test_doctest_cascade_module_clean() -> None:
    """All >>> blocks in _cascade.py pass under doctest ().

    Runs the module's doctests in isolation and asserts zero failures.
    """
    import aspose_html.dom._cascade as _mod

    results = doctest.testmod(_mod, verbose=False)
    assert results.failed == 0, (
        f"{results.failed} doctest failure(s) in _cascade.py "
        f"(attempted {results.attempted})"
    )
