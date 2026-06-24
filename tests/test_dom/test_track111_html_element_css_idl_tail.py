"""Tests for  — HTML element / CSS IDL tail (20 missing members).

Covers all 24 acceptance criteria from  / .
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# HTMLInputElement — AC-1 through AC-4
# ---------------------------------------------------------------------------

def test_ac1_set_range_text_raises():
    """AC-1: inp.set_range_text('x') raises NotSupportedError."""
    from aspose_html.dom._exceptions import NotSupportedError
    doc = Document()
    inp = doc.create_element("input")
    with pytest.raises(NotSupportedError):
        inp.set_range_text("x")


def test_ac2_list_returns_none():
    """AC-2: inp.list_ returns None."""
    doc = Document()
    inp = doc.create_element("input")
    assert inp.list_ is None


def test_ac3_value_as_date_returns_none():
    """AC-3: inp.value_as_date returns None."""
    doc = Document()
    inp = doc.create_element("input")
    assert inp.value_as_date is None


def test_ac4_value_as_date_setter_no_raise():
    """AC-4: inp.value_as_date = object() does not raise."""
    doc = Document()
    inp = doc.create_element("input")
    inp.value_as_date = object()  # must not raise


# ---------------------------------------------------------------------------
# HTMLFieldSetElement — AC-5 through AC-6
# ---------------------------------------------------------------------------

def test_ac5_set_custom_validity_succeeds():
    """AC-5: fs.set_custom_validity('error') succeeds (no exception)."""
    doc = Document()
    fs = doc.create_element("fieldset")
    fs.set_custom_validity("error")  # must not raise


def test_ac6_check_validity_returns_true():
    """AC-6: fs.check_validity() returns True on a fresh HTMLFieldSetElement."""
    doc = Document()
    fs = doc.create_element("fieldset")
    assert fs.check_validity() is True


# ---------------------------------------------------------------------------
# HTMLImageElement — AC-7 through AC-8
# ---------------------------------------------------------------------------

def test_ac7_img_x_returns_zero():
    """AC-7: img.x returns 0."""
    doc = Document()
    img = doc.create_element("img")
    assert img.x == 0


def test_ac8_img_y_returns_zero():
    """AC-8: img.y returns 0."""
    doc = Document()
    img = doc.create_element("img")
    assert img.y == 0


# ---------------------------------------------------------------------------
# HTMLVideoElement — AC-9 through AC-11
# ---------------------------------------------------------------------------

def test_ac9_request_picture_in_picture_raises():
    """AC-9: vid.request_picture_in_picture() raises NotSupportedError."""
    from aspose_html.dom._exceptions import NotSupportedError
    doc = Document()
    vid = doc.create_element("video")
    with pytest.raises(NotSupportedError):
        vid.request_picture_in_picture()


def test_ac10_disable_pip_false_when_absent():
    """AC-10: vid.disable_picture_in_picture returns False when attribute absent."""
    doc = Document()
    vid = doc.create_element("video")
    assert vid.disable_picture_in_picture is False


def test_ac11_disable_pip_true_after_set_attribute():
    """AC-11: vid.disable_picture_in_picture returns True after set_attribute."""
    doc = Document()
    vid = doc.create_element("video")
    vid.set_attribute("disablepictureinpicture", "")
    assert vid.disable_picture_in_picture is True


# ---------------------------------------------------------------------------
# HTMLTableElement — AC-12 through AC-13
# ---------------------------------------------------------------------------

def test_ac12_tbodies_empty_on_empty_table():
    """AC-12: table.tbodies has length 0 on empty table."""
    doc = Document()
    table = doc.create_element("table")
    assert len(table.tbodies) == 0


def test_ac13_tbodies_length_one_after_parse():
    """AC-13: table.tbodies has length 1 after parsing <table><tbody></tbody></table>."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<table><tbody></tbody></table>")
    tables = doc.get_elements_by_tag_name("table")
    assert len(tables) == 1
    table = tables[0]
    assert len(table.tbodies) == 1


# ---------------------------------------------------------------------------
# Document — AC-14 through AC-15
# ---------------------------------------------------------------------------

def test_ac14_strict_error_checking_returns_true():
    """AC-14: doc.strict_error_checking returns True."""
    doc = Document()
    assert doc.strict_error_checking is True


def test_ac15_strict_error_checking_setter_no_raise():
    """AC-15: doc.strict_error_checking = False does not raise."""
    doc = Document()
    doc.strict_error_checking = False  # must not raise


# ---------------------------------------------------------------------------
# CSS.supports — AC-16 through AC-24
# ---------------------------------------------------------------------------

def test_ac16_font_variation_settings():
    """AC-16: CSS.supports('font-variation-settings', 'normal') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("font-variation-settings", "normal") is True


def test_ac17_font_palette():
    """AC-17: CSS.supports('font-palette', 'normal') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("font-palette", "normal") is True


def test_ac18_zoom():
    """AC-18: CSS.supports('zoom', '1') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("zoom", "1") is True


def test_ac19_animation_composition():
    """AC-19: CSS.supports('animation-composition', 'replace') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("animation-composition", "replace") is True


def test_ac20_animation_range():
    """AC-20: CSS.supports('animation-range', 'normal') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("animation-range", "normal") is True


def test_ac21_animation_range_start():
    """AC-21: CSS.supports('animation-range-start', 'normal') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("animation-range-start", "normal") is True


def test_ac22_animation_range_end():
    """AC-22: CSS.supports('animation-range-end', 'normal') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("animation-range-end", "normal") is True


def test_ac23_math_depth():
    """AC-23: CSS.supports('math-depth', '0') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("math-depth", "0") is True


def test_ac24_math_style():
    """AC-24: CSS.supports('math-style', 'normal') returns True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("math-style", "normal") is True
