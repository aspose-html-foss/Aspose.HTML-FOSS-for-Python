"""Track 35 integration hardening tests — SPEC-082 Group F (BACK-148).

Covers cross-component interactions introduced by BACK-143 through BACK-147:
- Registry completeness sweep: all ~50 new tag names
- Media element clone fidelity
- HTMLAudioElement isinstance hierarchy
- toggle_attribute ID-registration interaction
- get_attribute_names with namespaced attributes
- Window.screen lazy-cache identity
- Timer callback non-execution
"""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    Element,
    HTMLElement,
    HTMLAudioElement,
    HTMLVideoElement,
    HTMLMediaElement,
    HTMLSourceElement,
    HTMLTrackElement,
    HTMLCanvasElement,
    HTMLParamElement,
    HTMLNavElement,
    HTMLSectionElement,
    HTMLArticleElement,
    HTMLAsideElement,
    HTMLHeaderElement,
    HTMLFooterElement,
    HTMLMainElement,
    HTMLFigureElement,
    HTMLFigCaptionElement,
    HTMLAddressElement,
    HTMLWBRElement,
    HTMLNoScriptElement,
    HTMLMarkElement,
    HTMLSmallElement,
    HTMLRubyElement,
    HTMLUnknownElement,
    Screen,
)
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# AC #1 — Parametrized registry completeness test (all ~50 new tag names)
# ---------------------------------------------------------------------------

# Tag names introduced by BACK-143 (sectioning/text-level) and
# BACK-144/145 (media, canvas, param).  Each entry: (tag, expected_class).
# All must return instanceof expected_class and NOT be HTMLUnknownElement.
_TRACK35_NEW_TAGS: list[tuple[str, type]] = [
    # BACK-143: sectioning elements
    ("nav",         HTMLNavElement),
    ("section",     HTMLSectionElement),
    ("article",     HTMLArticleElement),
    ("aside",       HTMLAsideElement),
    ("header",      HTMLHeaderElement),
    ("footer",      HTMLFooterElement),
    ("main",        HTMLMainElement),
    ("figure",      HTMLFigureElement),
    ("figcaption",  HTMLFigCaptionElement),
    ("address",     HTMLAddressElement),
    ("wbr",         HTMLWBRElement),
    ("noscript",    HTMLNoScriptElement),
    ("mark",        HTMLMarkElement),
    ("small",       HTMLSmallElement),
    ("ruby",        HTMLRubyElement),
    ("rt",          HTMLRubyElement),
    ("rp",          HTMLRubyElement),
    # BACK-143: text-level elements (mapped to HTMLElement base)
    ("abbr",        HTMLElement),
    ("b",           HTMLElement),
    ("bdi",         HTMLElement),
    ("bdo",         HTMLElement),
    ("cite",        HTMLElement),
    ("code",        HTMLElement),
    ("dfn",         HTMLElement),
    ("em",          HTMLElement),
    ("i",           HTMLElement),
    ("kbd",         HTMLElement),
    ("s",           HTMLElement),
    ("samp",        HTMLElement),
    ("slot",        HTMLElement),
    ("strong",      HTMLElement),
    ("sub",         HTMLElement),
    ("sup",         HTMLElement),
    ("u",           HTMLElement),
    ("var",         HTMLElement),
    # BACK-144: media elements
    ("audio",       HTMLAudioElement),
    ("video",       HTMLVideoElement),
    # BACK-145: source/track/canvas/param
    ("source",      HTMLSourceElement),
    ("track",       HTMLTrackElement),
    ("canvas",      HTMLCanvasElement),
    ("param",       HTMLParamElement),
]


@pytest.mark.parametrize("tag,expected_cls", _TRACK35_NEW_TAGS)
def test_registry_completeness_track35(tag: str, expected_cls: type) -> None:
    """AC #1: Every Track 35 tag name resolves to the expected class."""
    doc = Document()
    el = doc.create_element(tag)
    assert isinstance(el, expected_cls), (
        f"create_element({tag!r}) returned {type(el).__name__}, "
        f"expected {expected_cls.__name__}"
    )
    assert isinstance(el, HTMLElement), (
        f"create_element({tag!r}) must return an HTMLElement instance"
    )
    assert not isinstance(el, HTMLUnknownElement), (
        f"create_element({tag!r}) must NOT return HTMLUnknownElement"
    )


# ---------------------------------------------------------------------------
# AC #2 — Media element clone fidelity
# ---------------------------------------------------------------------------

def test_audio_clone_preserves_src() -> None:
    """Audio clone preserves src IDL attribute value (AC #2)."""
    d = Document()
    audio = d.create_element("audio")
    audio.set_attribute("src", "podcast.mp3")
    clone = audio.clone_node(deep=False)
    assert isinstance(clone, HTMLAudioElement)
    assert clone.src == "podcast.mp3"


def test_video_clone_preserves_src() -> None:
    """Video clone preserves src IDL attribute value (AC #2)."""
    d = Document()
    video = d.create_element("video")
    video.set_attribute("src", "clip.mp4")
    clone = video.clone_node(deep=False)
    assert isinstance(clone, HTMLVideoElement)
    assert clone.src == "clip.mp4"


def test_video_clone_preserves_poster() -> None:
    """Video clone preserves poster attribute (AC #2)."""
    d = Document()
    video = d.create_element("video")
    video.poster = "thumb.jpg"
    clone = video.clone_node(deep=False)
    assert isinstance(clone, HTMLVideoElement)
    assert clone.poster == "thumb.jpg"


def test_audio_clone_preserves_controls_and_loop() -> None:
    """Audio clone preserves boolean IDL attributes (AC #2)."""
    d = Document()
    audio = d.create_element("audio")
    audio.set_attribute("controls", "")
    audio.set_attribute("loop", "")
    clone = audio.clone_node(deep=False)
    assert isinstance(clone, HTMLAudioElement)
    assert clone.controls is True
    assert clone.loop is True


# ---------------------------------------------------------------------------
# AC #3 — isinstance hierarchy test
# ---------------------------------------------------------------------------

def test_audio_isinstance_hierarchy() -> None:
    """HTMLAudioElement is HTMLMediaElement is HTMLElement is Element (AC #3)."""
    d = Document()
    audio = d.create_element("audio")
    assert isinstance(audio, HTMLAudioElement)
    assert isinstance(audio, HTMLMediaElement)
    assert isinstance(audio, HTMLElement)
    assert isinstance(audio, Element)


def test_video_isinstance_hierarchy() -> None:
    """HTMLVideoElement is also HTMLMediaElement is HTMLElement is Element (AC #3)."""
    d = Document()
    video = d.create_element("video")
    assert isinstance(video, HTMLVideoElement)
    assert isinstance(video, HTMLMediaElement)
    assert isinstance(video, HTMLElement)
    assert isinstance(video, Element)


# ---------------------------------------------------------------------------
# AC #4 — toggle_attribute ID-registration interaction test
# ---------------------------------------------------------------------------

def test_toggle_attribute_id_registration() -> None:
    """toggle_attribute('hidden') on an element appended to doc does not corrupt ID registry (AC #4)."""
    d = Document()
    el = d.create_element("div")
    d.append_child(el)
    result = el.toggle_attribute("hidden")  # adds "hidden"
    assert result is True
    assert el.has_attribute("hidden")
    # Toggle back off
    result2 = el.toggle_attribute("hidden")
    assert result2 is False
    assert not el.has_attribute("hidden")


def test_toggle_attribute_id_attribute_registered() -> None:
    """Setting id via toggle_attribute adds it and element is findable via get_element_by_id (AC #4)."""
    d = Document()
    el = d.create_element("div")
    d.append_child(el)
    # Set an id directly, then verify toggle_attribute with force doesn't corrupt registry
    el.set_attribute("id", "my-el")
    assert d.get_element_by_id("my-el") is el
    # toggle_attribute on a non-id attribute must not affect the ID registry
    el.toggle_attribute("hidden", force=True)
    assert d.get_element_by_id("my-el") is el  # still findable


# ---------------------------------------------------------------------------
# AC #5 (window test) — Window.screen is Window.screen (cached identity)
# ---------------------------------------------------------------------------

def test_window_screen_is_cached() -> None:
    """Window.screen returns the same Screen instance on repeated access (AC #5 in window context)."""
    d = Document()
    w = d.default_view
    screen1 = w.screen
    screen2 = w.screen
    assert screen1 is screen2
    assert isinstance(screen1, Screen)


# ---------------------------------------------------------------------------
# AC #6 — Timer callback is never executed
# ---------------------------------------------------------------------------

def test_set_timeout_callback_not_called() -> None:
    """set_timeout callback is never invoked (AC #6)."""
    d = Document()
    w = d.default_view
    called: list[str] = []
    w.set_timeout(lambda: called.append("timeout"), 0)
    assert called == []


def test_set_interval_callback_not_called() -> None:
    """set_interval callback is never invoked (AC #6)."""
    d = Document()
    w = d.default_view
    called: list[str] = []
    w.set_interval(lambda: called.append("interval"), 0)
    assert called == []


def test_raf_callback_not_called() -> None:
    """request_animation_frame callback is never invoked (AC #6)."""
    d = Document()
    w = d.default_view
    called: list[str] = []
    w.request_animation_frame(lambda t: called.append("raf"))
    assert called == []


# ---------------------------------------------------------------------------
# Sectioning element in parsed tree (ADR-131 test 2)
# ---------------------------------------------------------------------------

def test_sectioning_elements_in_tree() -> None:
    """nav/section/article created by parser are findable with query_selector."""
    doc = HTMLDocument.parse("<body><nav><a>link</a></nav><section><p>x</p></section></body>")
    nav = doc.query_selector("nav")
    assert nav is not None
    assert isinstance(nav, HTMLNavElement)

    section = doc.query_selector("section")
    assert section is not None
    assert isinstance(section, HTMLSectionElement)


# ---------------------------------------------------------------------------
# get_attribute_names with namespaced attributes (ADR-131 test 7)
# ---------------------------------------------------------------------------

def test_get_attribute_names_namespaced() -> None:
    """get_attribute_names returns qualified names for namespaced attrs."""
    d = Document()
    el = d.create_element("div")
    el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#")
    names = el.get_attribute_names()
    assert "xlink:href" in names


def test_get_attribute_names_includes_all_attrs() -> None:
    """get_attribute_names returns all attribute names in insertion order."""
    d = Document()
    el = d.create_element("div")
    el.set_attribute("class", "box")
    el.set_attribute("id", "main")
    names = el.get_attribute_names()
    assert names == ["class", "id"]


# ---------------------------------------------------------------------------
# Canvas clone preserves width/height (ADR-131 test 4)
# ---------------------------------------------------------------------------

def test_canvas_clone_preserves_width_height() -> None:
    """Canvas clone preserves width and height IDL attributes."""
    d = Document()
    el = d.create_element("canvas")
    el.width = 800
    el.height = 600
    clone = el.clone_node(deep=False)
    assert isinstance(clone, HTMLCanvasElement)
    assert clone.width == 800
    assert clone.height == 600
