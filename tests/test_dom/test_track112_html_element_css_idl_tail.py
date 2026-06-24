"""Tests for  — HTML element / Window / Document / CSS IDL tail (67 members).

Covers all acceptance criteria from  /  ().
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# HTMLInputElement — AC-1, AC-2
# ---------------------------------------------------------------------------

def test_ac1_input_src_reflects_attribute() -> None:
    """AC-1: HTMLInputElement.src reflects the src content attribute."""
    doc = Document()
    inp = doc.create_element("input")
    assert inp.src == ""
    inp.set_attribute("src", "image.png")
    assert inp.src == "image.png"


def test_ac2_input_alt_reflects_attribute() -> None:
    """AC-2: HTMLInputElement.alt reflects the alt content attribute."""
    doc = Document()
    inp = doc.create_element("input")
    assert inp.alt == ""
    inp.set_attribute("alt", "Submit")
    assert inp.alt == "Submit"


# ---------------------------------------------------------------------------
# HTMLSelectElement — AC-3
# ---------------------------------------------------------------------------

def test_ac3_select_labels_returns_empty_static_node_list() -> None:
    """AC-3: HTMLSelectElement.labels returns _StaticNodeList([])."""
    doc = Document()
    sel = doc.create_element("select")
    labels = sel.labels
    assert len(labels) == 0
    assert list(labels) == []


# ---------------------------------------------------------------------------
# HTMLTextAreaElement — AC-4, AC-5
# ---------------------------------------------------------------------------

def test_ac4_textarea_type_returns_textarea() -> None:
    """AC-4: HTMLTextAreaElement.type returns 'textarea' (read-only)."""
    doc = Document()
    ta = doc.create_element("textarea")
    assert ta.type == "textarea"


def test_ac5_textarea_set_range_text_raises() -> None:
    """AC-5: HTMLTextAreaElement.set_range_text('x') raises NotSupportedError."""
    from aspose_html.dom._exceptions import NotSupportedError
    doc = Document()
    ta = doc.create_element("textarea")
    with pytest.raises(NotSupportedError):
        ta.set_range_text("x")


# ---------------------------------------------------------------------------
# HTMLButtonElement — AC-6
# ---------------------------------------------------------------------------

def test_ac6_button_form_enc_type_reflects_attribute() -> None:
    """AC-6: HTMLButtonElement.form_enc_type reflects the formenctype attribute."""
    doc = Document()
    btn = doc.create_element("button")
    assert btn.form_enc_type == ""
    btn.set_attribute("formenctype", "multipart/form-data")
    assert btn.form_enc_type == "multipart/form-data"


# ---------------------------------------------------------------------------
# HTMLLinkElement — AC-7 through AC-12
# ---------------------------------------------------------------------------

def test_ac7_link_image_srcset_reflects_attribute() -> None:
    """AC-7: HTMLLinkElement.image_srcset reflects the imagesrcset attribute."""
    doc = Document()
    link = doc.create_element("link")
    assert link.image_srcset == ""
    link.set_attribute("imagesrcset", "img-2x.png 2x")
    assert link.image_srcset == "img-2x.png 2x"


def test_ac8_link_image_sizes_reflects_attribute() -> None:
    """AC-8: HTMLLinkElement.image_sizes reflects the imagesizes attribute."""
    doc = Document()
    link = doc.create_element("link")
    assert link.image_sizes == ""
    link.set_attribute("imagesizes", "(max-width: 600px) 100vw")
    assert link.image_sizes == "(max-width: 600px) 100vw"


def test_ac9_link_blocking_returns_empty_string() -> None:
    """AC-9: HTMLLinkElement.blocking returns '' when attribute is absent."""
    doc = Document()
    link = doc.create_element("link")
    assert link.blocking == ""


def test_ac10_link_fetch_priority_default_auto() -> None:
    """AC-10: HTMLLinkElement.fetch_priority returns 'auto' when absent."""
    doc = Document()
    link = doc.create_element("link")
    assert link.fetch_priority == "auto"
    link.set_attribute("fetchpriority", "high")
    assert link.fetch_priority == "high"


def test_ac11_link_rev_reflects_attribute() -> None:
    """AC-11: HTMLLinkElement.rev reflects the rev content attribute."""
    doc = Document()
    link = doc.create_element("link")
    assert link.rev == ""
    link.set_attribute("rev", "made")
    assert link.rev == "made"


def test_ac12_link_target_reflects_attribute() -> None:
    """AC-12: HTMLLinkElement.target reflects the target content attribute."""
    doc = Document()
    link = doc.create_element("link")
    assert link.target == ""
    link.set_attribute("target", "_blank")
    assert link.target == "_blank"


# ---------------------------------------------------------------------------
# HTMLScriptElement — AC-13 through AC-15
# ---------------------------------------------------------------------------

def test_ac13_script_charset_reflects_attribute() -> None:
    """AC-13: HTMLScriptElement.charset reflects the charset attribute."""
    doc = Document()
    script = doc.create_element("script")
    assert script.charset == ""
    script.set_attribute("charset", "utf-8")
    assert script.charset == "utf-8"


def test_ac14_script_event_reflects_attribute() -> None:
    """AC-14: HTMLScriptElement.event reflects the event attribute."""
    doc = Document()
    script = doc.create_element("script")
    assert script.event == ""
    script.set_attribute("event", "onclick")
    assert script.event == "onclick"


def test_ac15_script_html_for_reflects_for_attribute() -> None:
    """AC-15: HTMLScriptElement.html_for reflects the 'for' content attribute."""
    doc = Document()
    script = doc.create_element("script")
    assert script.html_for == ""
    script.set_attribute("for", "myElement")
    assert script.html_for == "myElement"


# ---------------------------------------------------------------------------
# HTMLStyleElement — AC-16
# ---------------------------------------------------------------------------

def test_ac16_style_blocking_returns_empty_string() -> None:
    """AC-16: HTMLStyleElement.blocking returns '' when attribute is absent."""
    doc = Document()
    style = doc.create_element("style")
    assert style.blocking == ""


# ---------------------------------------------------------------------------
# HTMLMetaElement — AC-17, AC-18
# ---------------------------------------------------------------------------

def test_ac17_meta_scheme_reflects_attribute() -> None:
    """AC-17: HTMLMetaElement.scheme reflects the scheme attribute."""
    doc = Document()
    meta = doc.create_element("meta")
    assert meta.scheme == ""
    meta.set_attribute("scheme", "ISBN")
    assert meta.scheme == "ISBN"


def test_ac18_meta_media_reflects_attribute() -> None:
    """AC-18: HTMLMetaElement.media reflects the media attribute."""
    doc = Document()
    meta = doc.create_element("meta")
    assert meta.media == ""
    meta.set_attribute("media", "screen")
    assert meta.media == "screen"


# ---------------------------------------------------------------------------
# HTMLIFrameElement — AC-19 through AC-25
# ---------------------------------------------------------------------------

def test_ac19_iframe_get_svg_document_returns_none() -> None:
    """AC-19: HTMLIFrameElement.get_svg_document() returns None."""
    doc = Document()
    iframe = doc.create_element("iframe")
    assert iframe.get_svg_document() is None


def test_ac20_iframe_align_reflects_attribute() -> None:
    """AC-20: HTMLIFrameElement.align reflects the align attribute."""
    doc = Document()
    iframe = doc.create_element("iframe")
    assert iframe.align == ""
    iframe.set_attribute("align", "center")
    assert iframe.align == "center"


def test_ac21_iframe_scrolling_reflects_attribute() -> None:
    """AC-21: HTMLIFrameElement.scrolling reflects the scrolling attribute."""
    doc = Document()
    iframe = doc.create_element("iframe")
    assert iframe.scrolling == ""
    iframe.set_attribute("scrolling", "no")
    assert iframe.scrolling == "no"


def test_ac22_iframe_frame_border_reflects_frameborder() -> None:
    """AC-22: HTMLIFrameElement.frame_border reflects the frameborder attribute."""
    doc = Document()
    iframe = doc.create_element("iframe")
    assert iframe.frame_border == ""
    iframe.set_attribute("frameborder", "0")
    assert iframe.frame_border == "0"


def test_ac23_iframe_long_desc_reflects_longdesc() -> None:
    """AC-23: HTMLIFrameElement.long_desc reflects the longdesc attribute."""
    doc = Document()
    iframe = doc.create_element("iframe")
    assert iframe.long_desc == ""
    iframe.set_attribute("longdesc", "desc.html")
    assert iframe.long_desc == "desc.html"


def test_ac24_iframe_margin_height_reflects_marginheight() -> None:
    """AC-24: HTMLIFrameElement.margin_height reflects the marginheight attribute."""
    doc = Document()
    iframe = doc.create_element("iframe")
    assert iframe.margin_height == ""
    iframe.set_attribute("marginheight", "10")
    assert iframe.margin_height == "10"


def test_ac25_iframe_margin_width_reflects_marginwidth() -> None:
    """AC-25: HTMLIFrameElement.margin_width reflects the marginwidth attribute."""
    doc = Document()
    iframe = doc.create_element("iframe")
    assert iframe.margin_width == ""
    iframe.set_attribute("marginwidth", "5")
    assert iframe.margin_width == "5"


# ---------------------------------------------------------------------------
# HTMLTableElement — AC-26 through AC-28
# ---------------------------------------------------------------------------

def test_ac26_table_thead_alias_for_t_head() -> None:
    """AC-26: HTMLTableElement.thead returns first <thead> child or None."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<table><thead><tr></tr></thead></table>")
    table = doc.query_selector("table")
    assert table.thead is not None
    assert table.thead.tag_name == "THEAD"
    assert table.thead is table.t_head


def test_ac26_table_thead_none_when_absent() -> None:
    """AC-26: HTMLTableElement.thead returns None when no thead child."""
    doc = Document()
    table = doc.create_element("table")
    assert table.thead is None


def test_ac27_table_tfoot_alias_for_t_foot() -> None:
    """AC-27: HTMLTableElement.tfoot returns first <tfoot> child or None."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<table><tfoot><tr></tr></tfoot></table>")
    table = doc.query_selector("table")
    assert table.tfoot is not None
    assert table.tfoot.tag_name == "TFOOT"
    assert table.tfoot is table.t_foot


def test_ac28_table_align_reflects_attribute() -> None:
    """AC-28: HTMLTableElement.align reflects the align attribute."""
    doc = Document()
    table = doc.create_element("table")
    assert table.align == ""
    table.set_attribute("align", "center")
    assert table.align == "center"


# ---------------------------------------------------------------------------
# HTMLTableRowElement — AC-29 through AC-33
# ---------------------------------------------------------------------------

def test_ac29_tr_align_reflects_attribute() -> None:
    """AC-29: HTMLTableRowElement.align reflects the align attribute."""
    doc = Document()
    tr = doc.create_element("tr")
    assert tr.align == ""
    tr.set_attribute("align", "center")
    assert tr.align == "center"


def test_ac30_tr_bg_color_reflects_bgcolor() -> None:
    """AC-30: HTMLTableRowElement.bg_color reflects the bgcolor attribute."""
    doc = Document()
    tr = doc.create_element("tr")
    assert tr.bg_color == ""
    tr.set_attribute("bgcolor", "#ffffff")
    assert tr.bg_color == "#ffffff"


def test_ac31_tr_ch_reflects_char() -> None:
    """AC-31: HTMLTableRowElement.ch reflects the char attribute."""
    doc = Document()
    tr = doc.create_element("tr")
    assert tr.ch == ""
    tr.set_attribute("char", ".")
    assert tr.ch == "."


def test_ac32_tr_ch_off_reflects_charoff() -> None:
    """AC-32: HTMLTableRowElement.ch_off reflects the charoff attribute."""
    doc = Document()
    tr = doc.create_element("tr")
    assert tr.ch_off == ""
    tr.set_attribute("charoff", "2")
    assert tr.ch_off == "2"


def test_ac33_tr_v_align_reflects_valign() -> None:
    """AC-33: HTMLTableRowElement.v_align reflects the valign attribute."""
    doc = Document()
    tr = doc.create_element("tr")
    assert tr.v_align == ""
    tr.set_attribute("valign", "top")
    assert tr.v_align == "top"


# ---------------------------------------------------------------------------
# HTMLTableSectionElement — AC-34 through AC-37
# ---------------------------------------------------------------------------

def test_ac34_tbody_align_reflects_attribute() -> None:
    """AC-34: HTMLTableSectionElement.align reflects the align attribute."""
    doc = Document()
    tbody = doc.create_element("tbody")
    assert tbody.align == ""
    tbody.set_attribute("align", "right")
    assert tbody.align == "right"


def test_ac35_tbody_ch_reflects_char() -> None:
    """AC-35: HTMLTableSectionElement.ch reflects the char attribute."""
    doc = Document()
    tbody = doc.create_element("tbody")
    assert tbody.ch == ""
    tbody.set_attribute("char", ",")
    assert tbody.ch == ","


def test_ac36_tbody_ch_off_reflects_charoff() -> None:
    """AC-36: HTMLTableSectionElement.ch_off reflects the charoff attribute."""
    doc = Document()
    tbody = doc.create_element("tbody")
    assert tbody.ch_off == ""
    tbody.set_attribute("charoff", "3")
    assert tbody.ch_off == "3"


def test_ac37_tbody_v_align_reflects_valign() -> None:
    """AC-37: HTMLTableSectionElement.v_align reflects the valign attribute."""
    doc = Document()
    tbody = doc.create_element("tbody")
    assert tbody.v_align == ""
    tbody.set_attribute("valign", "bottom")
    assert tbody.v_align == "bottom"


# ---------------------------------------------------------------------------
# HTMLTableColElement — AC-38, AC-39
# ---------------------------------------------------------------------------

def test_ac38_col_ch_reflects_char() -> None:
    """AC-38: HTMLTableColElement.ch reflects the char attribute."""
    doc = Document()
    col = doc.create_element("col")
    assert col.ch == ""
    col.set_attribute("char", ".")
    assert col.ch == "."


def test_ac39_col_ch_off_reflects_charoff() -> None:
    """AC-39: HTMLTableColElement.ch_off reflects the charoff attribute."""
    doc = Document()
    col = doc.create_element("col")
    assert col.ch_off == ""
    col.set_attribute("charoff", "1")
    assert col.ch_off == "1"


# ---------------------------------------------------------------------------
# HTMLTableCellElement — AC-40 through AC-43
# ---------------------------------------------------------------------------

def test_ac40_td_axis_reflects_attribute() -> None:
    """AC-40: HTMLTableCellElement.axis reflects the axis attribute."""
    doc = Document()
    td = doc.create_element("td")
    assert td.axis == ""
    td.set_attribute("axis", "category")
    assert td.axis == "category"


def test_ac41_td_v_align_reflects_valign() -> None:
    """AC-41: HTMLTableCellElement.v_align reflects the valign attribute."""
    doc = Document()
    td = doc.create_element("td")
    assert td.v_align == ""
    td.set_attribute("valign", "middle")
    assert td.v_align == "middle"


def test_ac42_td_ch_reflects_char() -> None:
    """AC-42: HTMLTableCellElement.ch reflects the char attribute."""
    doc = Document()
    td = doc.create_element("td")
    assert td.ch == ""
    td.set_attribute("char", ".")
    assert td.ch == "."


def test_ac43_td_ch_off_reflects_charoff() -> None:
    """AC-43: HTMLTableCellElement.ch_off reflects the charoff attribute."""
    doc = Document()
    td = doc.create_element("td")
    assert td.ch_off == ""
    td.set_attribute("charoff", "2")
    assert td.ch_off == "2"


# ---------------------------------------------------------------------------
# HTMLVideoElement — AC-44
# ---------------------------------------------------------------------------

def test_ac44_video_webkit_dropped_frame_count_returns_zero() -> None:
    """AC-44: HTMLVideoElement.webkit_dropped_frame_count returns 0."""
    doc = Document()
    video = doc.create_element("video")
    assert video.webkit_dropped_frame_count == 0


# ---------------------------------------------------------------------------
# Document — AC-45 through AC-50
# ---------------------------------------------------------------------------

def test_ac45_document_origin_returns_null_string() -> None:
    """AC-45: Document.origin returns 'null' (opaque origin in headless)."""
    doc = Document()
    assert doc.origin == "null"


def test_ac46_document_fg_color_empty_when_no_body() -> None:
    """AC-46: Document.fg_color returns '' when no <body> element."""
    doc = Document()
    assert doc.fg_color == ""


def test_ac47_document_bg_color_reflects_body_bgcolor() -> None:
    """AC-47: Document.bg_color reflects <body> bgcolor attribute."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body bgcolor='#fff'></body></html>")
    assert doc.bg_color == "#fff"


def test_ac48_document_link_color_reflects_body_link() -> None:
    """AC-48: Document.link_color reflects <body> link attribute."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body link='blue'></body></html>")
    assert doc.link_color == "blue"


def test_ac49_document_v_link_color_reflects_body_vlink() -> None:
    """AC-49: Document.v_link_color reflects <body> vlink attribute."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body vlink='purple'></body></html>")
    assert doc.v_link_color == "purple"


def test_ac50_document_a_link_color_reflects_body_alink() -> None:
    """AC-50: Document.a_link_color reflects <body> alink attribute."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body alink='red'></body></html>")
    assert doc.a_link_color == "red"


# ---------------------------------------------------------------------------
# Window — AC-51 through AC-58
# ---------------------------------------------------------------------------

def test_ac51_window_navigation_returns_none() -> None:
    """AC-51: Window.navigation returns None (headless stub)."""
    doc = Document()
    assert doc.default_view.navigation is None


def test_ac52_window_custom_elements_exists() -> None:
    """AC-52: Window.custom_elements exists (already a full stub in prior tracks)."""
    doc = Document()
    # custom_elements already exists from prior tracks; it is not None
    assert hasattr(doc.default_view, "custom_elements")


def test_ac53_window_locationbar_returns_barprop() -> None:
    """AC-53: Window.locationbar returns BarProp(visible=False)."""
    doc = Document()
    w = doc.default_view
    assert w.locationbar.visible is False
    assert w.locationbar is w.location_bar or not w.locationbar.visible


def test_ac54_window_menubar_returns_barprop() -> None:
    """AC-54: Window.menubar returns BarProp(visible=False)."""
    doc = Document()
    assert doc.default_view.menubar.visible is False


def test_ac55_window_personalbar_returns_barprop() -> None:
    """AC-55: Window.personalbar returns BarProp(visible=False)."""
    doc = Document()
    assert doc.default_view.personalbar.visible is False


def test_ac56_window_scrollbars_returns_barprop() -> None:
    """AC-56: Window.scrollbars returns BarProp(visible=False)."""
    doc = Document()
    assert doc.default_view.scrollbars.visible is False


def test_ac57_window_statusbar_returns_barprop() -> None:
    """AC-57: Window.statusbar returns BarProp(visible=False)."""
    doc = Document()
    assert doc.default_view.statusbar.visible is False


def test_ac58_window_toolbar_returns_barprop() -> None:
    """AC-58: Window.toolbar returns BarProp(visible=False)."""
    doc = Document()
    assert doc.default_view.toolbar.visible is False


# ---------------------------------------------------------------------------
# CSS.supports — AC-59 through AC-67
# ---------------------------------------------------------------------------

def test_ac59_css_supports_shape_margin() -> None:
    """AC-59: CSS.supports('shape-margin', '10px') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "shape-margin" in _KNOWN_PROPERTIES


def test_ac60_css_supports_shape_image_threshold() -> None:
    """AC-60: CSS.supports('shape-image-threshold', '0') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "shape-image-threshold" in _KNOWN_PROPERTIES


def test_ac61_css_supports_scrollbar_gutter() -> None:
    """AC-61: CSS.supports('scrollbar-gutter', 'auto') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "scrollbar-gutter" in _KNOWN_PROPERTIES


def test_ac62_css_supports_contain_intrinsic_size() -> None:
    """AC-62: CSS.supports('contain-intrinsic-size', 'none') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "contain-intrinsic-size" in _KNOWN_PROPERTIES


def test_ac63_css_supports_contain_intrinsic_width() -> None:
    """AC-63: CSS.supports('contain-intrinsic-width', 'none') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "contain-intrinsic-width" in _KNOWN_PROPERTIES


def test_ac64_css_supports_contain_intrinsic_height() -> None:
    """AC-64: CSS.supports('contain-intrinsic-height', 'none') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "contain-intrinsic-height" in _KNOWN_PROPERTIES


def test_ac65_css_supports_contain_intrinsic_block_size() -> None:
    """AC-65: CSS.supports('contain-intrinsic-block-size', 'none') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "contain-intrinsic-block-size" in _KNOWN_PROPERTIES


def test_ac66_css_supports_contain_intrinsic_inline_size() -> None:
    """AC-66: CSS.supports('contain-intrinsic-inline-size', 'none') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "contain-intrinsic-inline-size" in _KNOWN_PROPERTIES


def test_ac67_css_supports_webkit_user_select() -> None:
    """AC-67: CSS.supports('-webkit-user-select', 'auto') returns True."""
    from aspose_html.dom._cascade_data import _KNOWN_PROPERTIES
    assert "-webkit-user-select" in _KNOWN_PROPERTIES


# ---------------------------------------------------------------------------
# CSS.supports integration via public API
# ---------------------------------------------------------------------------

def test_css_supports_new_properties_via_public_api() -> None:
    """AC-59..67: CSS.supports() returns True for all 9 new CSS properties."""
    from aspose_html.cssom import CSS
    checks = [
        ("shape-margin", "10px"),
        ("shape-image-threshold", "0"),
        ("scrollbar-gutter", "auto"),
        ("contain-intrinsic-size", "none"),
        ("contain-intrinsic-width", "none"),
        ("contain-intrinsic-height", "none"),
        ("contain-intrinsic-block-size", "none"),
        ("contain-intrinsic-inline-size", "none"),
        ("-webkit-user-select", "auto"),
    ]
    for prop, val in checks:
        assert CSS.supports(prop, val), f"CSS.supports({prop!r}, {val!r}) returned False"
