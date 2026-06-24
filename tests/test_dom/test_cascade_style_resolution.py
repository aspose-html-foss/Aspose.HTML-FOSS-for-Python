"""Tests for Element.get_computed_style() cascade resolution (/84/85/86)."""

import pytest

from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import ComputedStyleDeclaration, Document


def _attached_div() -> tuple[Document, object]:
    doc = Document()
    element = doc.create_element("div")
    doc.append_child(element)
    return doc, element


def test_get_computed_style_returns_read_only_snapshot_surface() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { margin: 0; color: red }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()

    assert isinstance(style, ComputedStyleDeclaration)
    #  (Phase 7): only properties with explicit rule or inherited
    # parent values appear in computed style.  Root element with no parent
    # only surfaces the explicitly-declared properties:
    # color + 4 margin longhands = 5.
    #  (, HI-1): the UA default stylesheet now supplies
    # `display: block` for <div> (§15.3.3), so a styled <div> carries one
    # additional property. Recomputed deliberately: 5 -> 6. The sort order
    # places `display` between `color` and `margin-*`.
    assert style.length == 6
    assert len(style) == 6
    assert list(style) == [
        "color",
        "display",
        "margin-bottom",
        "margin-left",
        "margin-right",
        "margin-top",
    ]
    assert style.item(0) == "color"
    assert style.item(1) == "display"
    assert style.item(5) == "margin-top"
    assert style["color"] == "red"
    assert style["display"] == "block"
    assert "margin-top" in style
    # Unset inherited properties return "" without appearing in the snapshot.
    assert style.get_property_value("font-family") == ""
    assert style.get_property_value("font-size") == ""

    # Snapshot behavior: modifying the stylesheet after resolution does not mutate
    # already-returned ComputedStyleDeclaration.
    sheet.replace_sync("div { margin: 5px; color: blue }")
    assert style.get_property_value("color") == "red"
    assert style.get_property_value("margin-top") == "0"


def test_margin_shorthand_expands_one_value_to_four_sides() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { margin: 8px }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("margin-top") == "8px"
    assert style.get_property_value("margin-right") == "8px"
    assert style.get_property_value("margin-bottom") == "8px"
    assert style.get_property_value("margin-left") == "8px"


def test_margin_shorthand_expands_two_values_with_tb_rl_mapping() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin", "4px 10px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-top") == "4px"
    assert style.get_property_value("margin-right") == "10px"
    assert style.get_property_value("margin-bottom") == "4px"
    assert style.get_property_value("margin-left") == "10px"


def test_padding_shorthand_expands_three_values_with_middle_reuse() -> None:
    doc, element = _attached_div()
    element.style.set_property("padding", "1px 2px 3px")

    style = element.get_computed_style()
    assert style.get_property_value("padding-top") == "1px"
    assert style.get_property_value("padding-right") == "2px"
    assert style.get_property_value("padding-bottom") == "3px"
    assert style.get_property_value("padding-left") == "2px"


def test_shorthand_and_longhand_same_origin_longhand_wins_by_later_order() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin", "1px")
    element.style.set_property("margin-left", "9px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-top") == "1px"
    assert style.get_property_value("margin-left") == "9px"


def test_longhand_beats_earlier_shorthand_but_loses_to_later_shorthand() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin-left", "2px")
    element.style.set_property("margin", "5px 7px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-left") == "7px"


def test_important_longhand_beats_non_important_shorthand() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { margin: 3px } div { margin-left: 11px !important }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("margin-left") == "11px"
    assert style.get_property_value("margin-top") == "3px"


def test_unsupported_shorthand_token_count_is_ignored_deterministically() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin", "")
    element.style.set_property("padding", "1px 2px 3px 4px 5px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-top") == ""
    assert style.get_property_value("padding-top") == ""


def test_keyword_on_expanded_longhand_still_uses_adr074_semantics() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin", "initial")
    element.style.set_property("padding", "unset")

    style = element.get_computed_style()
    assert style.get_property_value("margin-top") == ""
    assert style.get_property_value("margin-right") == ""
    assert style.get_property_value("padding-bottom") == ""


def test_border_shorthand_expands_width_style_color_for_all_sides() -> None:
    doc, element = _attached_div()
    element.style.set_property("border", "1px solid red")

    style = element.get_computed_style()
    for side in ("top", "right", "bottom", "left"):
        assert style.get_property_value(f"border-{side}-width") == "1px"
        assert style.get_property_value(f"border-{side}-style") == "solid"
        assert style.get_property_value(f"border-{side}-color") == "red"


def test_border_shorthand_defaults_missing_color_to_currentcolor() -> None:
    doc, element = _attached_div()
    element.style.set_property("border", "2px dashed")

    style = element.get_computed_style()
    assert style.get_property_value("border-top-width") == "2px"
    assert style.get_property_value("border-top-style") == "dashed"
    assert style.get_property_value("border-top-color") == "currentcolor"


def test_border_shorthand_defaults_missing_style_and_width() -> None:
    doc, element = _attached_div()
    element.style.set_property("border", "blue")

    style = element.get_computed_style()
    assert style.get_property_value("border-left-width") == "medium"
    assert style.get_property_value("border-left-style") == "none"
    assert style.get_property_value("border-left-color") == "blue"


def test_border_side_shorthand_only_updates_targeted_side() -> None:
    doc, element = _attached_div()
    element.style.set_property("border-right", "4px dotted green")

    style = element.get_computed_style()
    assert style.get_property_value("border-right-width") == "4px"
    assert style.get_property_value("border-right-style") == "dotted"
    assert style.get_property_value("border-right-color") == "green"
    assert style.get_property_value("border-left-width") == ""
    assert style.get_property_value("border-left-style") == ""
    assert style.get_property_value("border-left-color") == ""


def test_border_longhand_later_overrides_expanded_shorthand_component() -> None:
    doc, element = _attached_div()
    element.style.set_property("border", "1px solid red")
    element.style.set_property("border-left-color", "purple")

    style = element.get_computed_style()
    assert style.get_property_value("border-left-width") == "1px"
    assert style.get_property_value("border-left-style") == "solid"
    assert style.get_property_value("border-left-color") == "purple"


def test_later_border_shorthand_overrides_earlier_border_left_longhand() -> None:
    doc, element = _attached_div()
    element.style.set_property("border-left-color", "orange")
    element.style.set_property("border", "3px double navy")

    style = element.get_computed_style()
    assert style.get_property_value("border-left-color") == "navy"


def test_important_border_longhand_beats_non_important_border_shorthand() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "div { border: 1px solid red } div { border-right-style: dotted !important }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("border-right-style") == "dotted"
    assert style.get_property_value("border-right-width") == "1px"


def test_unsupported_border_shorthand_shape_is_ignored_deterministically() -> None:
    doc, element = _attached_div()
    element.style.set_property("border", "solid dotted")
    element.style.set_property("border-top", "1px solid red blue")

    style = element.get_computed_style()
    assert style.get_property_value("border-left-style") == ""
    assert style.get_property_value("border-top-width") == ""


def test_border_shorthand_with_var_substitution_preserves_deterministic_winners() -> None:
    doc, element = _attached_div()
    element.style.set_property("--tone", "teal")
    element.style.set_property("border", "5px solid var(--tone)")

    style = element.get_computed_style()
    assert style.get_property_value("border-bottom-width") == "5px"
    assert style.get_property_value("border-bottom-style") == "solid"
    assert style.get_property_value("border-bottom-color") == "teal"


def test_css_wide_keyword_on_expanded_border_longhand_keeps_adr074_semantics() -> None:
    doc, element = _attached_div()
    element.style.set_property("border", "initial")

    style = element.get_computed_style()
    assert style.get_property_value("border-top-width") == ""
    assert style.get_property_value("border-right-style") == ""
    assert style.get_property_value("border-left-color") == ""


def test_logical_margin_inline_start_stores_independently() -> None:
    #  (): logical properties are independent of physical ones.
    # margin-inline-start stores in its own cascade slot; margin-left is unaffected.
    doc, element = _attached_div()
    element.style.set_property("margin-inline-start", "12px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-inline-start") == "12px"
    assert style.get_property_value("margin-left") == ""


def test_logical_margin_block_end_stores_independently() -> None:
    #  (): margin-block-end is an independent property.
    doc, element = _attached_div()
    element.style.set_property("margin-block-end", "6px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-block-end") == "6px"
    assert style.get_property_value("margin-bottom") == ""


def test_logical_padding_inline_end_stores_independently() -> None:
    #  (): padding-inline-end is an independent property.
    doc, element = _attached_div()
    element.style.set_property("padding-inline-end", "4px")

    style = element.get_computed_style()
    assert style.get_property_value("padding-inline-end") == "4px"
    assert style.get_property_value("padding-right") == ""


def test_physical_and_logical_are_independent_slots() -> None:
    #  (): logical and physical properties occupy separate
    # cascade slots — setting both stores both independently.
    doc, element = _attached_div()
    element.style.set_property("margin-left", "2px")
    element.style.set_property("margin-inline-start", "9px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-left") == "2px"
    assert style.get_property_value("margin-inline-start") == "9px"


def test_important_physical_beats_non_important_logical_same_target() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "div { margin-inline-start: 3px } div { margin-left: 10px !important }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("margin-left") == "10px"


def test_logical_margin_inline_and_physical_margin_are_independent() -> None:
    #  (): margin-inline-start stores independently of
    # margin-left.  The physical margin shorthand expands to physical longhands;
    # margin-inline-start populates only its own slot.
    doc, element = _attached_div()
    element.style.set_property("margin", "1px")
    element.style.set_property("margin-inline-start", "7px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-top") == "1px"
    assert style.get_property_value("margin-left") == "1px"
    assert style.get_property_value("margin-inline-start") == "7px"


def test_logical_margin_inline_does_not_affect_physical_margin_left() -> None:
    #  (): margin-inline is now a supported shorthand that expands
    # to margin-inline-start / margin-inline-end.  It must NOT affect margin-left.
    doc, element = _attached_div()
    element.style.set_property("margin-inline", "5px")

    style = element.get_computed_style()
    assert style.get_property_value("margin-inline-start") == "5px"
    assert style.get_property_value("margin-inline-end") == "5px"
    assert style.get_property_value("margin-left") == ""


def test_cascade_precedence_important_overrides_non_important() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: red !important } div { color: blue }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_cascade_precedence_specificity_overrides_lower_specificity() -> None:
    doc, element = _attached_div()
    element.set_attribute("id", "hero")
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: blue } #hero { color: green }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_cascade_precedence_source_order_breaks_specificity_ties() -> None:
    doc, element = _attached_div()
    element.set_attribute("class", "box")
    sheet = CSSStyleSheet()
    sheet.replace_sync(".box { color: red } .box { color: blue }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_source_order_uses_stylesheet_then_rule_then_declaration_order() -> None:
    doc, element = _attached_div()
    element.set_attribute("class", "box")

    first = CSSStyleSheet()
    first.replace_sync(".box { color: red; color: green }")
    second = CSSStyleSheet()
    second.replace_sync(".box { color: blue }")

    doc.attach_style_sheet(first)
    doc.attach_style_sheet(second)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_media_all_rule_participates_in_cascade() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media all { div { color: red } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_media_screen_rule_participates_with_baseline_screen() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media screen { div { color: green } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_media_print_rule_is_filtered_out() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media print { div { color: red } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_media_prefers_color_scheme_light_participates() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media (prefers-color-scheme: light) { div { color: red } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_media_prefers_color_scheme_dark_is_filtered_out() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media (prefers-color-scheme: dark) { div { color: red } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_media_not_prefix_inverts_supported_query() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media not print { div { color: red } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_media_and_requires_both_supported_operands() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "@media screen and (prefers-color-scheme: light) { div { color: red } }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_media_query_list_matches_when_any_member_matches() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media print, screen { div { color: red } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_unsupported_media_query_is_ignored_deterministically() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media (min-width: 1px) { div { color: red } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_invalid_media_query_is_ignored_deterministically() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@media not { div { color: red } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_media_nested_rule_source_order_is_deterministic() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "@media all { div { color: red } div { color: blue } }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_unsupported_declarations_are_ignored_deterministically() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "div { "
        "--theme: dark; "
        "9bad: nope; "
        "good: ; "
        " color:  red  ; "
        " }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    # : only properties with explicit values appear in computed style.
    # Invalid/empty declarations are ignored; no inherited-property pre-fill for
    # elements without a parent.
    #  (, HI-1): <div> now carries the UA default
    # `display: block` (§15.3.3); recomputed deliberately. The invalid/empty
    # declarations are still ignored — only the valid UA `display` is added.
    assert list(style) == [
        "--theme",
        "color",
        "display",
    ]
    assert style.get_property_value("--theme") == "dark"
    assert style.get_property_value("color") == "red"
    assert style.get_property_value("display") == "block"


def test_get_property_value_returns_empty_string_for_missing_property() -> None:
    doc, element = _attached_div()
    style = element.get_computed_style()
    assert style.get_property_value("padding") == ""


def test_item_returns_none_out_of_range() -> None:
    doc, element = _attached_div()
    style = element.get_computed_style()
    assert style.item(-1) is None
    assert style.item(6) is None


def test_element_get_computed_style_delegates_to_cascade_entrypoint() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { border: 1px solid black }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert isinstance(style, ComputedStyleDeclaration)
    assert style.get_property_value("border-top-width") == "1px"
    assert style.get_property_value("border-top-style") == "solid"
    assert style.get_property_value("border-top-color") == "black"


def test_getitem_raises_keyerror_for_missing_property() -> None:
    doc, element = _attached_div()
    style = element.get_computed_style()

    try:
        _ = style["opacity"]
        assert False, "Expected KeyError"
    except KeyError:
        pass


def test_inline_declaration_participates_in_computed_style() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "green")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_inline_non_important_beats_stylesheet_non_important() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: red }")
    doc.attach_style_sheet(sheet)
    element.style.set_property("color", "green")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_stylesheet_important_beats_inline_non_important() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: blue !important }")
    doc.attach_style_sheet(sheet)
    element.style.set_property("color", "green")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_inline_important_beats_stylesheet_non_important() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: red }")
    doc.attach_style_sheet(sheet)
    element.set_attribute("style", "color: green !important")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_inline_important_beats_stylesheet_important() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: blue !important }")
    doc.attach_style_sheet(sheet)
    element.set_attribute("style", "color: green !important")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_inline_duplicate_property_uses_last_declaration() -> None:
    doc, element = _attached_div()
    element.set_attribute("style", "color: red; color: green")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_inline_unsupported_declarations_ignored_deterministically() -> None:
    doc, element = _attached_div()
    element.set_attribute(
        "style",
        "--theme: dark; 9bad: nope; bad: ; color: red; color: blue",
    )

    style = element.get_computed_style()
    # : only properties with explicit values appear in computed style.
    #  (, HI-1): <div> now carries the UA default
    # `display: block` (§15.3.3); recomputed deliberately.
    assert list(style) == [
        "--theme",
        "color",
        "display",
    ]
    assert style.get_property_value("--theme") == "dark"
    assert style.get_property_value("color") == "blue"
    assert style.get_property_value("display") == "block"


def test_custom_property_stylesheet_declaration_is_resolved() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { --brand-color: teal }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("--brand-color") == "teal"


def test_custom_property_important_beats_non_important() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { --theme: red !important } div { --theme: blue }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("--theme") == "red"


def test_custom_property_specificity_and_source_order_apply() -> None:
    doc, element = _attached_div()
    element.set_attribute("class", "hero")
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "div { --tone: red } .hero { --tone: green } .hero { --tone: blue }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("--tone") == "blue"


def test_custom_property_inline_participates_in_same_comparator() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { --accent: blue !important }")
    doc.attach_style_sheet(sheet)
    element.set_attribute("style", "--accent: green")

    style = element.get_computed_style()
    assert style.get_property_value("--accent") == "blue"


def test_custom_property_inherits_from_parent_when_missing_locally() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("div")
    parent.append_child(child)
    doc.append_child(parent)
    parent.style.set_property("--tone", "orchid")

    style = child.get_computed_style()
    assert style.get_property_value("--tone") == "orchid"


def test_local_custom_property_overrides_inherited_custom_property() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("div")
    parent.append_child(child)
    doc.append_child(parent)
    parent.style.set_property("--tone", "orchid")
    child.style.set_property("--tone", "gold")

    style = child.get_computed_style()
    assert style.get_property_value("--tone") == "gold"


def test_custom_property_multi_level_inheritance_uses_nearest_ancestor() -> None:
    doc = Document()
    grandparent = doc.create_element("div")
    parent = doc.create_element("div")
    child = doc.create_element("div")
    grandparent.append_child(parent)
    parent.append_child(child)
    doc.append_child(grandparent)

    grandparent.style.set_property("--tone", "blue")
    parent.style.set_property("--tone", "red")

    style = child.get_computed_style()
    assert style.get_property_value("--tone") == "red"


def test_malformed_custom_property_name_is_ignored_deterministically() -> None:
    doc, element = _attached_div()
    element.set_attribute("style", "--bad_name: nope; --ok-name: yes")

    style = element.get_computed_style()
    assert style.get_property_value("--bad_name") == ""
    assert style.get_property_value("--ok-name") == "yes"


def test_non_custom_property_behavior_unchanged_with_custom_properties_present() -> None:
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "div { --token: x; color: red } div { --token: y !important; color: blue }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_inherited_subset_documented_scope_is_applied() -> None:
    doc = Document()
    parent = doc.create_element("section")
    child = doc.create_element("span")
    parent.append_child(child)
    doc.append_child(parent)

    parent.style.set_property("color", "purple")
    parent.style.set_property("font-family", "serif")
    parent.style.set_property("font-size", "16px")
    parent.style.set_property("font-style", "italic")
    parent.style.set_property("font-weight", "600")
    parent.style.set_property("line-height", "1.4")
    parent.style.set_property("margin", "11px")

    style = child.get_computed_style()
    assert style.get_property_value("color") == "purple"
    assert style.get_property_value("font-family") == "serif"
    assert style.get_property_value("font-size") == "16px"
    assert style.get_property_value("font-style") == "italic"
    assert style.get_property_value("font-weight") == "600"
    assert style.get_property_value("line-height") == "1.4"
    assert style.get_property_value("margin") == ""


def test_inherited_property_falls_back_to_parent_when_local_missing() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("div")
    parent.append_child(child)
    doc.append_child(parent)
    parent.style.set_property("color", "red")

    style = child.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_local_winner_overrides_parent_inherited_value() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("div")
    parent.append_child(child)
    doc.append_child(parent)
    parent.style.set_property("color", "red")
    child.style.set_property("color", "green")

    style = child.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_root_uses_initial_fallback_for_missing_inherited_subset() -> None:
    doc, element = _attached_div()
    style = element.get_computed_style()

    assert style.get_property_value("color") == ""
    assert style.get_property_value("font-family") == ""
    assert style.get_property_value("font-size") == ""
    assert style.get_property_value("font-style") == ""
    assert style.get_property_value("font-weight") == ""
    assert style.get_property_value("line-height") == ""


def test_non_subset_property_does_not_inherit() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("div")
    parent.append_child(child)
    doc.append_child(parent)
    parent.style.set_property("margin", "13px")

    style = child.get_computed_style()
    assert style.get_property_value("margin") == ""


def test_multi_level_inheritance_uses_nearest_ancestor_value() -> None:
    doc = Document()
    grandparent = doc.create_element("div")
    parent = doc.create_element("div")
    child = doc.create_element("div")
    grandparent.append_child(parent)
    parent.append_child(child)
    doc.append_child(grandparent)

    grandparent.style.set_property("color", "blue")
    parent.style.set_property("color", "red")

    style = child.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_inheritance_with_inline_parent_value_and_stylesheet_child_gap() -> None:
    doc = Document()
    parent = doc.create_element("section")
    child = doc.create_element("span")
    parent.append_child(child)
    doc.append_child(parent)

    sheet = CSSStyleSheet()
    sheet.replace_sync("span { margin: 4px }")
    doc.attach_style_sheet(sheet)
    parent.style.set_property("font-size", "18px")

    style = child.get_computed_style()
    assert style.get_property_value("font-size") == "18px"
    assert style.get_property_value("margin-top") == "4px"


def test_var_substitutes_from_effective_custom_property_map() -> None:
    doc, element = _attached_div()
    element.set_attribute("style", "--brand: teal; color: var(--brand)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "teal"


def test_var_uses_fallback_when_custom_property_missing() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "var(--brand, blue)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_var_uses_fallback_when_referenced_custom_property_is_empty_or_invalid() -> None:
    doc, element = _attached_div()
    element.style.set_property("--ok-name", "green")
    element.style.set_property("color", "var(--bad_name, blue)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_var_uses_fallback_when_reference_name_is_malformed() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "var(name, blue)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_var_without_fallback_unresolved_omits_property() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "var(--missing)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_var_with_malformed_reference_and_no_fallback_omits_property() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "var(name)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_var_uses_inherited_custom_property_value() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("div")
    parent.append_child(child)
    doc.append_child(parent)
    parent.style.set_property("--tone", "orchid")
    child.style.set_property("color", "var(--tone)")

    style = child.get_computed_style()
    assert style.get_property_value("color") == "orchid"


def test_custom_property_cycle_without_fallback_is_omitted() -> None:
    doc, element = _attached_div()
    element.style.set_property("--brand", "var(--brand)")

    style = element.get_computed_style()
    assert style.get_property_value("--brand") == ""


def test_custom_property_cycle_with_fallback_resolves_to_fallback() -> None:
    doc, element = _attached_div()
    element.style.set_property("--brand", "var(--brand, red)")

    style = element.get_computed_style()
    assert style.get_property_value("--brand") == "red"


def test_indirect_custom_property_cycle_is_detected_deterministically() -> None:
    doc, element = _attached_div()
    element.style.set_property("--a", "var(--b)")
    element.style.set_property("--b", "var(--a)")

    style = element.get_computed_style()
    assert style.get_property_value("--a") == ""
    assert style.get_property_value("--b") == ""


def test_regular_property_var_cycle_without_fallback_is_omitted() -> None:
    doc, element = _attached_div()
    element.style.set_property("--brand", "var(--brand)")
    element.style.set_property("color", "var(--brand)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_regular_property_var_cycle_with_fallback_uses_fallback() -> None:
    doc, element = _attached_div()
    element.style.set_property("--brand", "var(--brand)")
    element.style.set_property("color", "var(--brand, purple)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "purple"


def test_invalid_var_reference_name_without_fallback_is_omitted() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "var(name)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_invalid_var_reference_name_with_fallback_uses_fallback() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "var(name, blue)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "blue"


def test_malformed_var_empty_args_is_omitted() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "var()")

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_non_full_value_var_shape_remains_raw_and_does_not_raise() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "calc(1px + var(--tone, red))")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "calc(1px + var(--tone, red))"


def test_non_var_regular_values_remain_unchanged() -> None:
    doc, element = _attached_div()
    element.style.set_property("color", "rgb(1, 2, 3)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "rgb(1, 2, 3)"


def test_css_wide_inherit_uses_parent_value_for_inherited_property() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    parent.append_child(child)
    doc.append_child(parent)
    parent.style.set_property("color", "red")
    child.style.set_property("color", "inherit")

    style = child.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_css_wide_initial_uses_baseline_default() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin", "initial")

    style = element.get_computed_style()
    assert style.get_property_value("margin") == ""


def test_css_wide_unset_inherited_property_behaves_as_inherit() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    parent.append_child(child)
    doc.append_child(parent)
    parent.style.set_property("color", "green")
    child.style.set_property("color", "unset")

    style = child.get_computed_style()
    assert style.get_property_value("color") == "green"


def test_css_wide_unset_non_inherited_property_behaves_as_initial() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin", "5px")
    element.style.set_property("margin", "unset")

    style = element.get_computed_style()
    assert style.get_property_value("margin") == ""


def test_css_wide_inherit_without_parent_uses_baseline_when_defined() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin", "inherit")

    style = element.get_computed_style()
    assert style.get_property_value("margin") == ""


def test_css_wide_keyword_for_unsupported_property_is_omitted_deterministically() -> None:
    doc, element = _attached_div()
    element.style.set_property("border", "initial")

    style = element.get_computed_style()
    assert style.get_property_value("border") == ""


def test_keyword_winner_still_obeys_important_specificity_source_order() -> None:
    doc, element = _attached_div()
    element.set_attribute("id", "hero")
    sheet = CSSStyleSheet()
    sheet.replace_sync("div { color: red !important } #hero { color: inherit }")
    doc.attach_style_sheet(sheet)
    element.style.set_property("color", "green")

    style = element.get_computed_style()
    assert style.get_property_value("color") == "red"


def test_keyword_resolution_coexists_with_var_resolution_without_regressing_back89() -> None:
    doc, element = _attached_div()
    element.style.set_property("--brand", "teal")
    element.style.set_property("color", "inherit")
    element.style.set_property("margin", "var(--brand)")

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""
    assert style.get_property_value("margin-top") == "teal"
    assert style.get_property_value("margin-left") == "teal"


@pytest.mark.parametrize(
    ("declarations", "target_property", "expected"),
    [
        (
            [
                ("margin", "4px 8px"),
                ("margin-left", "unset"),
            ],
            "margin-left",
            "",
        ),
        (
            [
                ("padding", "var(--missing, 9px)"),
            ],
            "padding-right",
            "9px",
        ),
        (
            [
                ("padding", "1px 2px"),
                ("padding-right", "11px !important"),
            ],
            "padding-right",
            "11px",
        ),
        (
            [
                ("--bad", "teal"),
                ("padding", "1px 2px 3px 4px 5px"),
            ],
            "padding-top",
            "",
        ),
    ],
)
def test_mixed_interaction_matrix_inline_cases(
    declarations: list[tuple[str, str]],
    target_property: str,
    expected: str,
) -> None:
    """ matrix: mixed keyword/shorthand/var() deterministic outcomes."""
    doc, element = _attached_div()
    for name, value in declarations:
        element.style.set_property(name, value)

    style = element.get_computed_style()
    assert style.get_property_value(target_property) == expected


def test_mixed_interaction_matrix_keyword_on_expanded_shorthand_longhand() -> None:
    doc, element = _attached_div()
    element.style.set_property("margin", "5px 7px")
    element.style.set_property("margin-right", "initial")

    style = element.get_computed_style()
    assert style.get_property_value("margin-top") == "5px"
    assert style.get_property_value("margin-right") == ""


def test_mixed_interaction_matrix_inheritance_boundary_with_shorthand_keyword_and_var() -> None:
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    parent.append_child(child)
    doc.append_child(parent)

    parent.style.set_property("color", "purple")
    child.style.set_property("color", "unset")
    child.style.set_property("--gap", "6px")
    child.style.set_property("margin", "var(--gap)")

    style = child.get_computed_style()
    assert style.get_property_value("color") == "purple"
    assert style.get_property_value("margin-left") == "6px"


# ---------------------------------------------------------------------------
# Group S — @supports cascade participation (, , )
# ---------------------------------------------------------------------------


def test_supports_known_property_condition_participates_in_cascade() -> None:
    """AC-1: @supports with a known property yields its child rules."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@supports (color: red) { div { color: purple } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "purple"


def test_supports_unknown_property_condition_is_excluded() -> None:
    """AC-2: @supports with an unknown/custom property is excluded."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@supports (--experimental-feature: yes) { div { color: green } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    # Custom property name fails _SUPPORTED_NAME_RE — not applied.
    assert style.get_property_value("color") == ""


def test_supports_not_condition_inverts_match() -> None:
    """AC-3: @supports not (known) — inner True → negated → False → not applied."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    # color is a known property → inner evaluates True → not True = False
    sheet.replace_sync("@supports not (color: red) { div { color: teal } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_supports_and_condition_requires_all_clauses() -> None:
    """AC-4: @supports (known) and (known) — both known → applied."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@supports (color: red) and (font-size: 1em) { div { background-color: yellow } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("background-color") == "yellow"


def test_supports_and_condition_fails_when_any_clause_unknown() -> None:
    """AC-4 negative: @supports (known) and (--unknown) — second clause fails."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@supports (color: red) and (--unknown: x) { div { color: orange } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_supports_or_condition_matches_when_any_clause_known() -> None:
    """AC-5: @supports (known) or (--unknown) — first clause matches → applied."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@supports (color: red) or (--unknown: x) { div { color: pink } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "pink"


def test_supports_selector_condition_is_false() -> None:
    """AC-6: @supports selector(...) always evaluates to False."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync("@supports selector(div > p) { div { color: cyan } }")
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == ""


def test_supports_empty_condition_is_false() -> None:
    """AC-7: empty condition_text evaluates to False without raising."""
    from aspose_html.dom._cascade import _supports_condition_matches

    assert _supports_condition_matches("") is False
    assert _supports_condition_matches("   ") is False


def test_supports_child_source_order_deterministic() -> None:
    """AC-9: Two @supports blocks — later one wins source-order precedence."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "@supports (color: red) { div { color: navy } }"
        " @supports (color: red) { div { color: olive } }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    # Second @supports block wins by source order (higher rule_index)
    assert style.get_property_value("color") == "olive"


def test_supports_does_not_regress_media_rule_participation() -> None:
    """AC-8: @media and @supports coexist; both values appear in computed style."""
    doc, element = _attached_div()
    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "@media all { div { color: navy } }"
        " @supports (font-size: 1em) { div { font-size: 12px } }"
    )
    doc.attach_style_sheet(sheet)

    style = element.get_computed_style()
    assert style.get_property_value("color") == "navy"
    assert style.get_property_value("font-size") == "12px"
