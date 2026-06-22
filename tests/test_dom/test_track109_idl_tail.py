"""Tests for BACK-329: Track 109 — Media/Embedded/Form IDL tail + CSS inherited property tail.

Covers SPEC-162 / ADR-308 acceptance criteria AC-1 through AC-33.
"""

import pytest

from aspose_html.dom._document import Document
from aspose_html.dom.html._media_elements import HTMLMediaElement, HTMLVideoElement
from aspose_html.dom.html._embedded_elements import HTMLImageElement, HTMLCanvasElement
from aspose_html.dom.html._form_elements import HTMLSelectElement, HTMLFormElement


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _audio():
    return Document().create_element("audio")

def _video():
    return Document().create_element("video")

def _img():
    return Document().create_element("img")

def _canvas():
    return Document().create_element("canvas")

def _select():
    return Document().create_element("select")

def _form():
    return Document().create_element("form")


# ---------------------------------------------------------------------------
# HTMLMediaElement — TimeRanges stubs (AC-1, AC-6, AC-7)
# ---------------------------------------------------------------------------

def test_ac_01_buffered_length():
    """AC-1: HTMLMediaElement().buffered.length == 0 (no AttributeError)."""
    assert _audio().buffered.length == 0


def test_ac_06_played_length():
    """AC-6: HTMLMediaElement().played.length == 0."""
    assert _audio().played.length == 0


def test_ac_07_seekable_length():
    """AC-7: HTMLMediaElement().seekable.length == 0."""
    assert _audio().seekable.length == 0


@pytest.mark.parametrize("attr", ["buffered", "played", "seekable"])
def test_time_ranges_stubs_have_length(attr):
    """All three TimeRanges stubs carry a length attribute equal to 0."""
    media = _audio()
    tr = getattr(media, attr)
    assert tr.length == 0


# ---------------------------------------------------------------------------
# HTMLMediaElement — can_play_type (AC-2)
# ---------------------------------------------------------------------------

def test_ac_02_can_play_type_empty():
    """AC-2: HTMLMediaElement().can_play_type('video/mp4') == ''."""
    assert _audio().can_play_type("video/mp4") == ""


# ---------------------------------------------------------------------------
# HTMLMediaElement — seeking (AC-3)
# ---------------------------------------------------------------------------

def test_ac_03_seeking_false():
    """AC-3: HTMLMediaElement().seeking == False."""
    assert _audio().seeking is False


# ---------------------------------------------------------------------------
# HTMLMediaElement — default_playback_rate (AC-4)
# ---------------------------------------------------------------------------

def test_ac_04_default_playback_rate_default():
    """AC-4: HTMLMediaElement().default_playback_rate == 1.0."""
    assert _audio().default_playback_rate == 1.0


def test_ac_04_default_playback_rate_settable():
    """AC-4: setting default_playback_rate does not raise."""
    media = _audio()
    media.default_playback_rate = 2.0
    assert media.default_playback_rate == 2.0


# ---------------------------------------------------------------------------
# HTMLMediaElement — playback_rate (AC-5)
# ---------------------------------------------------------------------------

def test_ac_05_playback_rate_default():
    """AC-5: HTMLMediaElement().playback_rate == 1.0."""
    assert _audio().playback_rate == 1.0


def test_ac_05_playback_rate_settable():
    """AC-5: setting playback_rate does not raise."""
    media = _audio()
    media.playback_rate = 0.5
    assert media.playback_rate == 0.5


# ---------------------------------------------------------------------------
# HTMLMediaElement — media_keys, src_object, error (AC-8, AC-9, AC-10)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prop", ["media_keys", "src_object", "error"])
def test_media_none_properties(prop):
    """AC-8/9/10: media_keys, src_object, error each return None."""
    assert getattr(_audio(), prop) is None


# ---------------------------------------------------------------------------
# HTMLMediaElement — track lists (AC-11, AC-12, AC-13)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prop", ["text_tracks", "audio_tracks", "video_tracks"])
def test_track_list_stubs_length(prop):
    """AC-11/12/13: text_tracks, audio_tracks, video_tracks each have length 0."""
    assert getattr(_audio(), prop).length == 0


# ---------------------------------------------------------------------------
# HTMLMediaElement — add_text_track (AC-14)
# ---------------------------------------------------------------------------

def test_ac_14_add_text_track_returns_none():
    """AC-14: HTMLMediaElement().add_text_track('subtitles') is None."""
    assert _audio().add_text_track("subtitles") is None


# ---------------------------------------------------------------------------
# HTMLVideoElement — plays_inline (AC-15)
# ---------------------------------------------------------------------------

def test_ac_15_plays_inline_default_false():
    """AC-15: HTMLVideoElement().plays_inline == False."""
    assert _video().plays_inline is False


def test_ac_15_plays_inline_setter_sets_attribute():
    """AC-15: setting plays_inline=True sets the playsinline attribute."""
    video = _video()
    video.plays_inline = True
    assert video.plays_inline is True
    assert video.has_attribute("playsinline")


def test_ac_15_plays_inline_setter_removes_attribute():
    """AC-15: setting plays_inline=False removes the playsinline attribute."""
    video = _video()
    video.plays_inline = True
    video.plays_inline = False
    assert video.plays_inline is False
    assert not video.has_attribute("playsinline")


# ---------------------------------------------------------------------------
# HTMLVideoElement — webkit_decoded_frame_count (AC-16)
# ---------------------------------------------------------------------------

def test_ac_16_webkit_decoded_frame_count():
    """AC-16: HTMLVideoElement().webkit_decoded_frame_count == 0."""
    assert _video().webkit_decoded_frame_count == 0


# ---------------------------------------------------------------------------
# HTMLImageElement — current_src (AC-17)
# ---------------------------------------------------------------------------

def test_ac_17_current_src_empty():
    """AC-17: HTMLImageElement().current_src == '' when no src set."""
    assert _img().current_src == ""


def test_ac_17_current_src_reflects_src():
    """AC-17: current_src reflects the src attribute."""
    img = _img()
    img.src = "photo.jpg"
    assert img.current_src == "photo.jpg"


# ---------------------------------------------------------------------------
# HTMLImageElement — referrer_policy (AC-18)
# ---------------------------------------------------------------------------

def test_ac_18_referrer_policy_default():
    """AC-18: HTMLImageElement().referrer_policy == ''."""
    assert _img().referrer_policy == ""


def test_ac_18_referrer_policy_settable():
    """AC-18: referrer_policy reflects referrerpolicy attribute."""
    img = _img()
    img.referrer_policy = "no-referrer"
    assert img.referrer_policy == "no-referrer"
    assert img.get_attribute("referrerpolicy") == "no-referrer"


# ---------------------------------------------------------------------------
# HTMLImageElement — fetch_priority (AC-19)
# ---------------------------------------------------------------------------

def test_ac_19_fetch_priority_default():
    """AC-19: HTMLImageElement().fetch_priority == ''."""
    assert _img().fetch_priority == ""


def test_ac_19_fetch_priority_settable():
    """AC-19: fetch_priority reflects fetchpriority attribute."""
    img = _img()
    img.fetch_priority = "high"
    assert img.fetch_priority == "high"
    assert img.get_attribute("fetchpriority") == "high"


# ---------------------------------------------------------------------------
# HTMLImageElement — decode (AC-20)
# ---------------------------------------------------------------------------

def test_ac_20_decode_raises_not_implemented():
    """AC-20: HTMLImageElement().decode() raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        _img().decode()


# ---------------------------------------------------------------------------
# HTMLCanvasElement — to_data_url (AC-21)
# ---------------------------------------------------------------------------

def test_ac_21_to_data_url_returns_stub():
    """AC-21: HTMLCanvasElement().to_data_url() == 'data:,'."""
    assert _canvas().to_data_url() == "data:,"


def test_ac_21_to_data_url_with_type_arg():
    """AC-21: to_data_url accepts optional type argument."""
    assert _canvas().to_data_url("image/jpeg") == "data:,"


# ---------------------------------------------------------------------------
# HTMLCanvasElement — to_blob (AC-22)
# ---------------------------------------------------------------------------

def test_ac_22_to_blob_calls_callback_with_none():
    """AC-22: to_blob calls callback with None."""
    received = []
    _canvas().to_blob(received.append)
    assert received == [None]


# ---------------------------------------------------------------------------
# HTMLCanvasElement — transfer_control_to_offscreen (AC-23)
# ---------------------------------------------------------------------------

def test_ac_23_transfer_control_raises_not_supported():
    """AC-23: HTMLCanvasElement().transfer_control_to_offscreen() raises NotSupportedError."""
    from aspose_html.dom._exceptions import NotSupportedError
    with pytest.raises(NotSupportedError):
        _canvas().transfer_control_to_offscreen()


# ---------------------------------------------------------------------------
# HTMLSelectElement — autocomplete (AC-24)
# ---------------------------------------------------------------------------

def test_ac_24_select_autocomplete_default():
    """AC-24: HTMLSelectElement().autocomplete == ''."""
    assert _select().autocomplete == ""


def test_ac_24_select_autocomplete_settable():
    """AC-24: select.autocomplete reflects autocomplete attribute."""
    sel = _select()
    sel.autocomplete = "on"
    assert sel.autocomplete == "on"


# ---------------------------------------------------------------------------
# HTMLSelectElement — type (AC-25)
# ---------------------------------------------------------------------------

def test_ac_25_select_type_single():
    """AC-25: HTMLSelectElement().type == 'select-one' without multiple attr."""
    assert _select().type == "select-one"


def test_ac_25_select_type_multiple():
    """AC-25: HTMLSelectElement().type == 'select-multiple' when multiple attr set."""
    sel = _select()
    sel.multiple = True
    assert sel.type == "select-multiple"


# ---------------------------------------------------------------------------
# HTMLFormElement — item (AC-26)
# ---------------------------------------------------------------------------

def test_ac_26_form_item_empty():
    """AC-26: HTMLFormElement().item(0) is None for empty form."""
    assert _form().item(0) is None


def test_ac_26_form_item_returns_element():
    """AC-26: form.item(0) returns first listed control when present."""
    doc = Document()
    form = doc.create_element("form")
    inp = doc.create_element("input")
    form.append_child(inp)
    assert form.item(0) is inp
    assert form.item(1) is None


# ---------------------------------------------------------------------------
# HTMLFormElement — named_item (AC-27)
# ---------------------------------------------------------------------------

def test_ac_27_form_named_item_empty():
    """AC-27: HTMLFormElement().named_item('x') is None for empty form."""
    assert _form().named_item("x") is None


def test_ac_27_form_named_item_by_id():
    """AC-27: named_item returns element matching id attribute."""
    doc = Document()
    form = doc.create_element("form")
    inp = doc.create_element("input")
    inp.set_attribute("id", "username")
    form.append_child(inp)
    assert form.named_item("username") is inp


def test_ac_27_form_named_item_by_name():
    """AC-27: named_item returns element matching name attribute."""
    doc = Document()
    form = doc.create_element("form")
    inp = doc.create_element("input")
    inp.set_attribute("name", "email")
    form.append_child(inp)
    assert form.named_item("email") is inp


# ---------------------------------------------------------------------------
# Document.location (AC-28)
# ---------------------------------------------------------------------------

def test_ac_28_document_location_none():
    """AC-28: Document().location is None (detached document)."""
    assert Document().location is None


# ---------------------------------------------------------------------------
# CSS.supports — hyphenate-character and ruby-position (AC-29, AC-30)
# ---------------------------------------------------------------------------

def test_ac_29_css_supports_hyphenate_character():
    """AC-29: CSS.supports('hyphenate-character', 'auto') == True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("hyphenate-character", "auto") is True


def test_ac_30_css_supports_ruby_position():
    """AC-30: CSS.supports('ruby-position', 'over') == True."""
    from aspose_html.cssom import CSS
    assert CSS.supports("ruby-position", "over") is True


# ---------------------------------------------------------------------------
# _is_inherited — hyphenate-character and ruby-position (AC-31, AC-32)
# ---------------------------------------------------------------------------

def test_ac_31_hyphenate_character_inherited():
    """AC-31: _is_inherited('hyphenate-character') == True."""
    from aspose_html.dom._cascade_data import _is_inherited
    assert _is_inherited("hyphenate-character") is True


def test_ac_32_ruby_position_inherited():
    """AC-32: _is_inherited('ruby-position') == True."""
    from aspose_html.dom._cascade_data import _is_inherited
    assert _is_inherited("ruby-position") is True
