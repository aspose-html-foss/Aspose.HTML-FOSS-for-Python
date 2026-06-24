"""Tests for : _INITIAL_VALUE_BASELINE expansion (, ).

Verifies that the ~130 new non-inherited CSS properties added in  are
present in _KNOWN_PROPERTIES (and therefore in _INITIAL_VALUE_BASELINE), have
the correct initial values, and that get_computed_style() resolves declared
values for newly registered properties.
"""
from __future__ import annotations

import pytest

from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE, _KNOWN_PROPERTIES
from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# Layout / positioning properties
# ---------------------------------------------------------------------------


class TestLayoutPropertiesInKnownProperties:
    """Spot-check layout/positioning properties added by ."""

    def test_overflow_x_present(self) -> None:
        assert "overflow-x" in _KNOWN_PROPERTIES

    def test_overflow_y_present(self) -> None:
        assert "overflow-y" in _KNOWN_PROPERTIES

    def test_overflow_present(self) -> None:
        assert "overflow" in _KNOWN_PROPERTIES

    def test_position_present(self) -> None:
        assert "position" in _KNOWN_PROPERTIES

    def test_box_sizing_present(self) -> None:
        assert "box-sizing" in _KNOWN_PROPERTIES

    def test_z_index_present(self) -> None:
        assert "z-index" in _KNOWN_PROPERTIES

    def test_float_present(self) -> None:
        assert "float" in _KNOWN_PROPERTIES

    def test_clear_present(self) -> None:
        assert "clear" in _KNOWN_PROPERTIES

    def test_top_present(self) -> None:
        assert "top" in _KNOWN_PROPERTIES

    def test_right_present(self) -> None:
        assert "right" in _KNOWN_PROPERTIES

    def test_bottom_present(self) -> None:
        assert "bottom" in _KNOWN_PROPERTIES

    def test_left_present(self) -> None:
        assert "left" in _KNOWN_PROPERTIES

    def test_clip_present(self) -> None:
        assert "clip" in _KNOWN_PROPERTIES

    def test_object_fit_present(self) -> None:
        assert "object-fit" in _KNOWN_PROPERTIES

    def test_object_position_present(self) -> None:
        assert "object-position" in _KNOWN_PROPERTIES

    def test_resize_present(self) -> None:
        assert "resize" in _KNOWN_PROPERTIES

    def test_aspect_ratio_present(self) -> None:
        assert "aspect-ratio" in _KNOWN_PROPERTIES


# ---------------------------------------------------------------------------
# Flexbox properties
# ---------------------------------------------------------------------------


class TestFlexboxPropertiesInKnownProperties:
    """Spot-check flexbox properties added by ."""

    def test_flex_direction_present(self) -> None:
        assert "flex-direction" in _KNOWN_PROPERTIES

    def test_flex_wrap_present(self) -> None:
        assert "flex-wrap" in _KNOWN_PROPERTIES

    def test_flex_grow_present(self) -> None:
        assert "flex-grow" in _KNOWN_PROPERTIES

    def test_flex_shrink_present(self) -> None:
        assert "flex-shrink" in _KNOWN_PROPERTIES

    def test_flex_basis_present(self) -> None:
        assert "flex-basis" in _KNOWN_PROPERTIES

    def test_flex_present(self) -> None:
        assert "flex" in _KNOWN_PROPERTIES

    def test_flex_flow_present(self) -> None:
        assert "flex-flow" in _KNOWN_PROPERTIES

    def test_justify_content_present(self) -> None:
        assert "justify-content" in _KNOWN_PROPERTIES

    def test_align_items_present(self) -> None:
        assert "align-items" in _KNOWN_PROPERTIES

    def test_align_self_present(self) -> None:
        assert "align-self" in _KNOWN_PROPERTIES

    def test_align_content_present(self) -> None:
        assert "align-content" in _KNOWN_PROPERTIES

    def test_order_present(self) -> None:
        assert "order" in _KNOWN_PROPERTIES

    def test_gap_present(self) -> None:
        assert "gap" in _KNOWN_PROPERTIES

    def test_row_gap_present(self) -> None:
        assert "row-gap" in _KNOWN_PROPERTIES

    def test_column_gap_present(self) -> None:
        assert "column-gap" in _KNOWN_PROPERTIES


# ---------------------------------------------------------------------------
# Grid properties
# ---------------------------------------------------------------------------


class TestGridPropertiesInKnownProperties:
    """Spot-check grid properties added by ."""

    def test_grid_template_columns_present(self) -> None:
        assert "grid-template-columns" in _KNOWN_PROPERTIES

    def test_grid_template_rows_present(self) -> None:
        assert "grid-template-rows" in _KNOWN_PROPERTIES

    def test_grid_template_areas_present(self) -> None:
        assert "grid-template-areas" in _KNOWN_PROPERTIES

    def test_grid_auto_flow_present(self) -> None:
        assert "grid-auto-flow" in _KNOWN_PROPERTIES

    def test_grid_auto_columns_present(self) -> None:
        assert "grid-auto-columns" in _KNOWN_PROPERTIES

    def test_grid_auto_rows_present(self) -> None:
        assert "grid-auto-rows" in _KNOWN_PROPERTIES

    def test_grid_column_start_present(self) -> None:
        assert "grid-column-start" in _KNOWN_PROPERTIES

    def test_grid_column_end_present(self) -> None:
        assert "grid-column-end" in _KNOWN_PROPERTIES

    def test_grid_row_start_present(self) -> None:
        assert "grid-row-start" in _KNOWN_PROPERTIES

    def test_grid_row_end_present(self) -> None:
        assert "grid-row-end" in _KNOWN_PROPERTIES

    def test_grid_area_present(self) -> None:
        assert "grid-area" in _KNOWN_PROPERTIES

    def test_grid_column_present(self) -> None:
        assert "grid-column" in _KNOWN_PROPERTIES

    def test_grid_row_present(self) -> None:
        assert "grid-row" in _KNOWN_PROPERTIES

    def test_grid_template_present(self) -> None:
        assert "grid-template" in _KNOWN_PROPERTIES

    def test_grid_present(self) -> None:
        assert "grid" in _KNOWN_PROPERTIES


# ---------------------------------------------------------------------------
# Transform / filter properties
# ---------------------------------------------------------------------------


class TestTransformPropertiesInKnownProperties:
    """Spot-check transform/filter properties added by ."""

    def test_transform_present(self) -> None:
        assert "transform" in _KNOWN_PROPERTIES

    def test_transform_origin_present(self) -> None:
        assert "transform-origin" in _KNOWN_PROPERTIES

    def test_transform_style_present(self) -> None:
        assert "transform-style" in _KNOWN_PROPERTIES

    def test_transform_box_present(self) -> None:
        assert "transform-box" in _KNOWN_PROPERTIES

    def test_perspective_present(self) -> None:
        assert "perspective" in _KNOWN_PROPERTIES

    def test_perspective_origin_present(self) -> None:
        assert "perspective-origin" in _KNOWN_PROPERTIES

    def test_backface_visibility_present(self) -> None:
        assert "backface-visibility" in _KNOWN_PROPERTIES

    def test_opacity_present(self) -> None:
        assert "opacity" in _KNOWN_PROPERTIES

    def test_filter_present(self) -> None:
        assert "filter" in _KNOWN_PROPERTIES

    def test_backdrop_filter_present(self) -> None:
        assert "backdrop-filter" in _KNOWN_PROPERTIES

    def test_mix_blend_mode_present(self) -> None:
        assert "mix-blend-mode" in _KNOWN_PROPERTIES

    def test_isolation_present(self) -> None:
        assert "isolation" in _KNOWN_PROPERTIES


# ---------------------------------------------------------------------------
# Transition / animation properties
# ---------------------------------------------------------------------------


class TestTransitionAnimationPropertiesInKnownProperties:
    """Spot-check transition/animation properties added by ."""

    def test_transition_property_present(self) -> None:
        assert "transition-property" in _KNOWN_PROPERTIES

    def test_transition_duration_present(self) -> None:
        assert "transition-duration" in _KNOWN_PROPERTIES

    def test_transition_timing_function_present(self) -> None:
        assert "transition-timing-function" in _KNOWN_PROPERTIES

    def test_transition_delay_present(self) -> None:
        assert "transition-delay" in _KNOWN_PROPERTIES

    def test_transition_present(self) -> None:
        assert "transition" in _KNOWN_PROPERTIES

    def test_animation_name_present(self) -> None:
        assert "animation-name" in _KNOWN_PROPERTIES

    def test_animation_duration_present(self) -> None:
        assert "animation-duration" in _KNOWN_PROPERTIES

    def test_animation_timing_function_present(self) -> None:
        assert "animation-timing-function" in _KNOWN_PROPERTIES

    def test_animation_delay_present(self) -> None:
        assert "animation-delay" in _KNOWN_PROPERTIES

    def test_animation_iteration_count_present(self) -> None:
        assert "animation-iteration-count" in _KNOWN_PROPERTIES

    def test_animation_direction_present(self) -> None:
        assert "animation-direction" in _KNOWN_PROPERTIES

    def test_animation_fill_mode_present(self) -> None:
        assert "animation-fill-mode" in _KNOWN_PROPERTIES

    def test_animation_play_state_present(self) -> None:
        assert "animation-play-state" in _KNOWN_PROPERTIES

    def test_animation_present(self) -> None:
        assert "animation" in _KNOWN_PROPERTIES


# ---------------------------------------------------------------------------
# Initial values
# ---------------------------------------------------------------------------


class TestInitialValueBaselineInitialValues:
    """Verify that specific initial values are set correctly per /."""

    def test_position_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["position"] == "static"

    def test_opacity_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["opacity"] == "1"

    def test_flex_grow_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["flex-grow"] == "0"

    def test_flex_shrink_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["flex-shrink"] == "1"

    def test_flex_direction_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["flex-direction"] == "row"

    def test_flex_wrap_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["flex-wrap"] == "nowrap"

    def test_z_index_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["z-index"] == "auto"

    def test_box_sizing_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["box-sizing"] == "content-box"

    def test_transform_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["transform"] == "none"

    def test_filter_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["filter"] == "none"

    def test_animation_name_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["animation-name"] == "none"

    def test_transition_duration_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["transition-duration"] == "0s"

    def test_transition_property_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["transition-property"] == "all"

    def test_grid_template_columns_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["grid-template-columns"] == "none"

    def test_grid_auto_flow_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["grid-auto-flow"] == "row"

    def test_grid_column_start_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["grid-column-start"] == "auto"

    def test_background_image_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["background-image"] == "none"

    def test_background_position_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["background-position"] == "0% 0%"

    def test_box_shadow_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["box-shadow"] == "none"

    def test_object_fit_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["object-fit"] == "fill"

    def test_mix_blend_mode_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["mix-blend-mode"] == "normal"

    def test_float_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["float"] == "none"

    def test_clear_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["clear"] == "none"

    def test_top_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["top"] == "auto"

    def test_column_count_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["column-count"] == "auto"

    def test_column_span_initial_value(self) -> None:
        assert _INITIAL_VALUE_BASELINE["column-span"] == "none"


# ---------------------------------------------------------------------------
# get_computed_style round-trip
# ---------------------------------------------------------------------------


class TestGetComputedStyleReturnsNewProperties:
    """Verify get_computed_style() resolves declared values for newly registered properties."""

    def test_flex_direction_column_resolved(self) -> None:
        """Stylesheet declaring flex-direction:column must be returned by get_computed_style."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { display: flex; flex-direction: column }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("flex-direction") == "column"

    def test_display_flex_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { display: flex }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("display") == "flex"

    def test_position_absolute_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { position: absolute; top: 10px }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("position") == "absolute"
        assert style.get_property_value("top") == "10px"

    def test_opacity_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { opacity: 0.5 }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("opacity") == "0.5"

    def test_transform_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { transform: rotate(45deg) }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("transform") == "rotate(45deg)"

    def test_grid_template_columns_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { display: grid; grid-template-columns: 1fr 1fr }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("grid-template-columns") == "1fr 1fr"

    def test_transition_duration_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { transition-duration: 300ms }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("transition-duration") == "300ms"

    def test_animation_name_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { animation-name: slide-in }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("animation-name") == "slide-in"

    def test_z_index_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { z-index: 100 }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("z-index") == "100"

    def test_box_sizing_resolved(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { box-sizing: border-box }")
        doc.attach_style_sheet(sheet)

        style = el.get_computed_style()
        assert style.get_property_value("box-sizing") == "border-box"
