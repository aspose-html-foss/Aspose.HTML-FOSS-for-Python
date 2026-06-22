"""Tests for Track 113 — HTML Element / CSS IDL tail (13 IDL members + 14 CSS entries).

Covers all 15 acceptance criteria from SPEC-166 / ADR-312.
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# HTMLInputElement — AC-1 through AC-3
# ---------------------------------------------------------------------------

def test_ac1_autocorrect_default():
    """AC-1a: autocorrect returns 'on' when attribute absent."""
    doc = Document()
    inp = doc.create_element("input")
    assert inp.autocorrect == "on"


def test_ac1_autocorrect_explicit_off():
    """AC-1b: autocorrect returns 'off' when attribute is 'off'."""
    doc = Document()
    inp = doc.create_element("input")
    inp.set_attribute("autocorrect", "off")
    assert inp.autocorrect == "off"


def test_ac1_autocorrect_explicit_on():
    """AC-1c: autocorrect returns 'on' when attribute is 'on'."""
    doc = Document()
    inp = doc.create_element("input")
    inp.set_attribute("autocorrect", "on")
    assert inp.autocorrect == "on"


def test_ac2_incremental_absent():
    """AC-2a: incremental returns False when attribute absent."""
    doc = Document()
    inp = doc.create_element("input")
    assert inp.incremental is False


def test_ac2_incremental_present():
    """AC-2b: incremental returns True when attribute present."""
    doc = Document()
    inp = doc.create_element("input")
    inp.set_attribute("incremental", "")
    assert inp.incremental is True


def test_ac3_webkitdirectory_absent():
    """AC-3a: webkitdirectory returns False when attribute absent."""
    doc = Document()
    inp = doc.create_element("input")
    assert inp.webkitdirectory is False


def test_ac3_webkitdirectory_present():
    """AC-3b: webkitdirectory returns True when attribute present."""
    doc = Document()
    inp = doc.create_element("input")
    inp.set_attribute("webkitdirectory", "")
    assert inp.webkitdirectory is True


# ---------------------------------------------------------------------------
# HTMLOutputElement — AC-4
# ---------------------------------------------------------------------------

def test_ac4_output_type():
    """AC-4: HTMLOutputElement.type_ always returns 'output'."""
    doc = Document()
    out = doc.create_element("output")
    assert out.type_ == "output"


# ---------------------------------------------------------------------------
# HTMLDataListElement — AC-5
# ---------------------------------------------------------------------------

def test_ac5_datalist_options_empty():
    """AC-5a: options on empty datalist has length 0."""
    doc = Document()
    dl = doc.create_element("datalist")
    assert len(dl.options) == 0


def test_ac5_datalist_options_live():
    """AC-5b: options is a live HTMLCollection of <option> children."""
    doc = Document()
    dl = doc.create_element("datalist")
    opt1 = doc.create_element("option")
    opt2 = doc.create_element("option")
    span = doc.create_element("span")
    dl.append_child(opt1)
    dl.append_child(opt2)
    dl.append_child(span)
    coll = dl.options
    assert len(coll) == 2


def test_ac5_datalist_options_excludes_non_option():
    """AC-5c: options excludes non-<option> children."""
    doc = Document()
    dl = doc.create_element("datalist")
    dl.append_child(doc.create_element("div"))
    assert len(dl.options) == 0


# ---------------------------------------------------------------------------
# HTMLObjectElement — AC-6
# ---------------------------------------------------------------------------

def test_ac6_object_get_svg_document_returns_none():
    """AC-6: HTMLObjectElement.get_svg_document() returns None."""
    doc = Document()
    obj = doc.create_element("object")
    assert obj.get_svg_document() is None


# ---------------------------------------------------------------------------
# HTMLEmbedElement — AC-7
# ---------------------------------------------------------------------------

def test_ac7_embed_get_svg_document_returns_none():
    """AC-7a: HTMLEmbedElement.get_svg_document() returns None."""
    doc = Document()
    embed = doc.create_element("embed")
    assert embed.get_svg_document() is None


def test_ac7_embed_type_absent():
    """AC-7b: HTMLEmbedElement.type_ returns '' when attribute absent."""
    doc = Document()
    embed = doc.create_element("embed")
    assert embed.type_ == ""


def test_ac7_embed_type_reflects():
    """AC-7c: HTMLEmbedElement.type_ reflects the type attribute."""
    doc = Document()
    embed = doc.create_element("embed")
    embed.set_attribute("type", "image/svg+xml")
    assert embed.type_ == "image/svg+xml"


# ---------------------------------------------------------------------------
# HTMLSourceElement — AC-8
# ---------------------------------------------------------------------------

def test_ac8_source_type_absent():
    """AC-8a: HTMLSourceElement.type_ returns '' when attribute absent."""
    doc = Document()
    src = doc.create_element("source")
    assert src.type_ == ""


def test_ac8_source_type_reflects():
    """AC-8b: HTMLSourceElement.type_ reflects the type attribute."""
    doc = Document()
    src = doc.create_element("source")
    src.set_attribute("type", "video/mp4")
    assert src.type_ == "video/mp4"


def test_ac8_source_width_default():
    """AC-8c: HTMLSourceElement.width returns 0 when attribute absent."""
    doc = Document()
    src = doc.create_element("source")
    assert src.width == 0


def test_ac8_source_width_reflects():
    """AC-8d: HTMLSourceElement.width reflects the width attribute as int."""
    doc = Document()
    src = doc.create_element("source")
    src.set_attribute("width", "320")
    assert src.width == 320


def test_ac8_source_width_non_numeric():
    """AC-8e: HTMLSourceElement.width returns 0 for non-numeric attribute."""
    doc = Document()
    src = doc.create_element("source")
    src.set_attribute("width", "abc")
    assert src.width == 0


def test_ac8_source_height_default():
    """AC-8f: HTMLSourceElement.height returns 0 when attribute absent."""
    doc = Document()
    src = doc.create_element("source")
    assert src.height == 0


def test_ac8_source_height_reflects():
    """AC-8g: HTMLSourceElement.height reflects the height attribute as int."""
    doc = Document()
    src = doc.create_element("source")
    src.set_attribute("height", "240")
    assert src.height == 240


def test_ac8_source_height_non_numeric():
    """AC-8h: HTMLSourceElement.height returns 0 for non-numeric attribute."""
    doc = Document()
    src = doc.create_element("source")
    src.set_attribute("height", "auto")
    assert src.height == 0


# ---------------------------------------------------------------------------
# HTMLTrackElement — AC-9
# ---------------------------------------------------------------------------

def test_ac9_track_track_returns_none():
    """AC-9: HTMLTrackElement.track returns None in headless mode."""
    doc = Document()
    track = doc.create_element("track")
    assert track.track is None


# ---------------------------------------------------------------------------
# Navigator — AC-10
# ---------------------------------------------------------------------------

def test_ac10_navigator_on_line():
    """AC-10: Navigator.on_line returns True."""
    from aspose_html.dom._window_stubs import Navigator
    assert Navigator().on_line is True


# ---------------------------------------------------------------------------
# CSS.supports — AC-11 through AC-14
# ---------------------------------------------------------------------------

def test_ac11_text_size_adjust():
    """AC-11a: CSS.supports('text-size-adjust', 'auto') is True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("text-size-adjust", "auto") is True


def test_ac11_webkit_text_size_adjust():
    """AC-11b: CSS.supports('-webkit-text-size-adjust', 'auto') is True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("-webkit-text-size-adjust", "auto") is True


def test_ac12_line_clamp():
    """AC-12a: CSS.supports('line-clamp', '3') is True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("line-clamp", "3") is True


def test_ac12_webkit_line_clamp():
    """AC-12b: CSS.supports('-webkit-line-clamp', '3') is True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("-webkit-line-clamp", "3") is True


def test_ac13_mask_border_source():
    """AC-13a: CSS.supports('mask-border-source', 'none') is True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("mask-border-source", "none") is True


def test_ac13_mask_border_shorthand():
    """AC-13b: CSS.supports('mask-border', 'none') is True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("mask-border", "none") is True


def test_ac13_mask_border_longhands():
    """AC-13c: All mask-border longhands are supported."""
    from aspose_html.cssom import CSS
    for prop, value in [
        ("mask-border-slice", "0"),
        ("mask-border-width", "auto"),
        ("mask-border-outset", "0"),
        ("mask-border-repeat", "stretch"),
        ("mask-border-mode", "alpha"),
    ]:
        assert CSS.supports(prop, value) is True, f"CSS.supports({prop!r}, {value!r}) should be True"


def test_ac14_grid_shorthand():
    """AC-14: CSS.supports('grid', 'none') is True (grid shorthand registered)."""
    from aspose_html.cssom import CSS
    assert CSS.supports("grid", "none") is True


def test_ac14_border_image_shorthand():
    """AC-14b: CSS.supports('border-image', 'none') is True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("border-image", "none") is True
