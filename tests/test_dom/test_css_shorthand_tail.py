""" shorthand-tail tests for background, border-radius, animation.

/, /, 
(FR-1, FR-2, FR-3, FR-4; AC-1, AC-2, AC-3, AC-4, AC-5, AC-6).
"""
from __future__ import annotations

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document


def _styled_div(declaration: str):
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    sheet = CSSStyleSheet()
    sheet.replace_sync(f"div {{ {declaration} }}")
    doc.attach_style_sheet(sheet)
    return el


def test_background_position_size_repeat_slash_split() -> None:
    """AC-1: background position/size split does not misroute repeat."""
    el = _styled_div('background: url("a b.png") center/cover no-repeat')
    style = el.get_computed_style()

    assert style.get_property_value("background-position") == "center"
    assert style.get_property_value("background-size") == "cover"
    assert style.get_property_value("background-repeat") == "no-repeat"


def test_background_multi_layer_unsupported_returns_no_expansion() -> None:
    """Unsupported multi-layer background stays deterministic and non-crashing."""
    el = _styled_div("background: red, blue")
    style = el.get_computed_style()

    # Deterministic no-expansion: shorthand does not mis-populate longhands.
    assert style.get_property_value("background-position") == ""
    assert style.get_property_value("background-size") == ""
    assert style.get_property_value("background-repeat") == ""


def test_border_radius_single_axis_slash_expands_to_pair_values() -> None:
    """AC-2: border-radius: 10px / 20px -> all corners '10px 20px'."""
    el = _styled_div("border-radius: 10px / 20px")
    style = el.get_computed_style()

    for corner in (
        "border-top-left-radius",
        "border-top-right-radius",
        "border-bottom-right-radius",
        "border-bottom-left-radius",
    ):
        assert style.get_property_value(corner) == "10px 20px"


def test_border_radius_two_axis_slash_maps_corners_deterministically() -> None:
    """AC-3: 10 20 / 30 40 maps corners per axis shorthand expansion."""
    el = _styled_div("border-radius: 10px 20px / 30px 40px")
    style = el.get_computed_style()

    assert style.get_property_value("border-top-left-radius") == "10px 30px"
    assert style.get_property_value("border-top-right-radius") == "20px 40px"
    assert style.get_property_value("border-bottom-right-radius") == "10px 30px"
    assert style.get_property_value("border-bottom-left-radius") == "20px 40px"


def test_transition_shorthand_regression_unaffected() -> None:
    """AC-6: existing transition shorthand behaviour remains unchanged."""
    el = _styled_div("transition: opacity 0.2s linear 1s")
    style = el.get_computed_style()

    assert style.get_property_value("transition-property") == "opacity"
    assert style.get_property_value("transition-duration") == "0.2s"
    assert style.get_property_value("transition-timing-function") == "linear"
    assert style.get_property_value("transition-delay") == "1s"


def test_animation_shorthand_single_entry_deterministic_parse() -> None:
    """AC-4: canonical single animation expands to non-empty longhands."""
    el = _styled_div("animation: slidein 3s ease-in 1s infinite alternate")
    style = el.get_computed_style()

    assert style.get_property_value("animation-name") == "slidein"
    assert style.get_property_value("animation-duration") == "3s"
    assert style.get_property_value("animation-timing-function") == "ease-in"
    assert style.get_property_value("animation-delay") == "1s"
    assert style.get_property_value("animation-iteration-count") == "infinite"
    assert style.get_property_value("animation-direction") == "alternate"
    assert style.get_property_value("animation-fill-mode") == "none"
    assert style.get_property_value("animation-play-state") == "running"


def test_animation_shorthand_explicit_defaults_round_trip() -> None:
    """AC-5: explicit defaults map to all eight animation longhands."""
    el = _styled_div("animation: none 0s ease 0s 1 normal none running")
    style = el.get_computed_style()

    assert style.get_property_value("animation-name") == "none"
    assert style.get_property_value("animation-duration") == "0s"
    assert style.get_property_value("animation-timing-function") == "ease"
    assert style.get_property_value("animation-delay") == "0s"
    assert style.get_property_value("animation-iteration-count") == "1"
    assert style.get_property_value("animation-direction") == "normal"
    assert style.get_property_value("animation-fill-mode") == "none"
    assert style.get_property_value("animation-play-state") == "running"


def test_animation_multi_entry_unsupported_returns_no_expansion() -> None:
    """FR-4: comma-list animations stay deterministic no-expansion."""
    el = _styled_div("animation: fade 1s linear, spin 2s ease")
    style = el.get_computed_style()

    assert style.get_property_value("animation-name") == ""
    assert style.get_property_value("animation-duration") == ""
    assert style.get_property_value("animation-timing-function") == ""
    assert style.get_property_value("animation-delay") == ""
    assert style.get_property_value("animation-iteration-count") == ""
    assert style.get_property_value("animation-direction") == ""
    assert style.get_property_value("animation-fill-mode") == ""
    assert style.get_property_value("animation-play-state") == ""
