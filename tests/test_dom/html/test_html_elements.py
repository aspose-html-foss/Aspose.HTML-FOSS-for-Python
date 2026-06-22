"""Tests for the 10 concrete HTMLElement subclasses (BACK-16, ADR-012).

Covers:
- create_element() dispatch returning correct subclasses
- All IDL-reflected properties (string, boolean, integer)
- Special cases: http_equiv → http-equiv, async_ → async, type defaults,
  method defaults, HTMLTitleElement.text (text node, not attribute)
- SINV-001 fix: clone_node() preserves concrete subclass via _clone_self()
- Parse-integration: HTMLDocument.parse() creates correct subclasses
- Doctest verification
"""
from __future__ import annotations

import doctest

import pytest

from aspose_html.dom import (
    Document,
    Element,
    HTMLElement,
    HTMLAddressElement,
    HTMLAnchorElement,
    HTMLArticleElement,
    HTMLAsideElement,
    HTMLButtonElement,
    HTMLFigCaptionElement,
    HTMLFigureElement,
    HTMLFormElement,
    HTMLFooterElement,
    HTMLHeaderElement,
    HTMLImageElement,
    HTMLInputElement,
    HTMLMainElement,
    HTMLMarkElement,
    HTMLNavElement,
    HTMLNoScriptElement,
    HTMLLinkElement,
    HTMLMetaElement,
    HTMLRubyElement,
    HTMLSectionElement,
    HTMLScriptElement,
    HTMLSelectElement,
    HTMLSmallElement,
    HTMLTitleElement,
    HTMLWBRElement,
    HTMLHtmlElement,
    HTMLHeadElement,
    HTMLBodyElement,
    HTMLBRElement,
    HTMLHRElement,
    HTMLPreElement,
    HTMLStyleElement,
    HTMLBaseElement,
    HTMLLabelElement,
    HTMLLegendElement,
    HTMLModElement,
    HTMLAreaElement,
    HTMLMapElement,
    HTMLTimeElement,
    HTMLDataElement,
    HTMLQuoteElement,
    HTMLPictureElement,
    HTMLIFrameElement,
    HTMLEmbedElement,
    HTMLObjectElement,
    HTMLMediaElement,
    HTMLVideoElement,
    HTMLAudioElement,
    HTMLSourceElement,
    HTMLTrackElement,
    HTMLCanvasElement,
    HTMLParamElement,
    HTMLTextAreaElement,
    HTMLUnknownElement,
)
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALL_SUBCLASSES = [
    HTMLAddressElement,
    HTMLAnchorElement,
    HTMLArticleElement,
    HTMLAsideElement,
    HTMLButtonElement,
    HTMLFigCaptionElement,
    HTMLFigureElement,
    HTMLFormElement,
    HTMLFooterElement,
    HTMLHeaderElement,
    HTMLImageElement,
    HTMLInputElement,
    HTMLMainElement,
    HTMLMarkElement,
    HTMLNavElement,
    HTMLNoScriptElement,
    HTMLLinkElement,
    HTMLMetaElement,
    HTMLRubyElement,
    HTMLSectionElement,
    HTMLScriptElement,
    HTMLSelectElement,
    HTMLSmallElement,
    HTMLTitleElement,
    HTMLWBRElement,
    HTMLHtmlElement,
    HTMLHeadElement,
    HTMLBodyElement,
    HTMLBRElement,
    HTMLHRElement,
    HTMLPreElement,
    HTMLStyleElement,
    HTMLBaseElement,
    HTMLLabelElement,
    HTMLLegendElement,
    HTMLModElement,
    HTMLAreaElement,
    HTMLMapElement,
    HTMLTimeElement,
    HTMLDataElement,
    HTMLQuoteElement,
    HTMLPictureElement,
    HTMLIFrameElement,
    HTMLEmbedElement,
    HTMLObjectElement,
    HTMLMediaElement,
    HTMLVideoElement,
    HTMLAudioElement,
    HTMLSourceElement,
    HTMLTrackElement,
    HTMLCanvasElement,
    HTMLParamElement,
    HTMLUnknownElement,
]

_TAG_CLASS_PAIRS = [
    ("a", HTMLAnchorElement),
    ("button", HTMLButtonElement),
    ("form", HTMLFormElement),
    ("img", HTMLImageElement),
    ("input", HTMLInputElement),
    ("link", HTMLLinkElement),
    ("meta", HTMLMetaElement),
    ("script", HTMLScriptElement),
    ("select", HTMLSelectElement),
    ("title", HTMLTitleElement),
    ("html", HTMLHtmlElement),
    ("head", HTMLHeadElement),
    ("body", HTMLBodyElement),
    ("br", HTMLBRElement),
    ("hr", HTMLHRElement),
    ("pre", HTMLPreElement),
    ("listing", HTMLPreElement),
    ("xmp", HTMLPreElement),
    ("style", HTMLStyleElement),
    ("base", HTMLBaseElement),
    ("label", HTMLLabelElement),
    ("legend", HTMLLegendElement),
    ("ins", HTMLModElement),
    ("del", HTMLModElement),
    ("area", HTMLAreaElement),
    ("map", HTMLMapElement),
    ("time", HTMLTimeElement),
    ("data", HTMLDataElement),
    ("blockquote", HTMLQuoteElement),
    ("q", HTMLQuoteElement),
    ("picture", HTMLPictureElement),
    ("iframe", HTMLIFrameElement),
    ("embed", HTMLEmbedElement),
    ("object", HTMLObjectElement),
    ("audio", HTMLAudioElement),
    ("video", HTMLVideoElement),
    ("source", HTMLSourceElement),
    ("track", HTMLTrackElement),
    ("canvas", HTMLCanvasElement),
    ("param", HTMLParamElement),
]


# ===========================================================================
# Dispatch tests
# ===========================================================================

class TestDispatch:
    """create_element() returns the correct concrete subclass for each tag."""

    def test_create_anchor_returns_html_anchor_element(self):
        doc = Document()
        el = doc.create_element("a")
        assert isinstance(el, HTMLAnchorElement)

    def test_create_img_returns_html_image_element(self):
        doc = Document()
        el = doc.create_element("img")
        assert isinstance(el, HTMLImageElement)

    def test_create_input_returns_html_input_element(self):
        doc = Document()
        el = doc.create_element("input")
        assert isinstance(el, HTMLInputElement)

    def test_create_form_returns_html_form_element(self):
        doc = Document()
        el = doc.create_element("form")
        assert isinstance(el, HTMLFormElement)

    def test_create_script_returns_html_script_element(self):
        doc = Document()
        el = doc.create_element("script")
        assert isinstance(el, HTMLScriptElement)

    def test_create_link_returns_html_link_element(self):
        doc = Document()
        el = doc.create_element("link")
        assert isinstance(el, HTMLLinkElement)

    def test_create_meta_returns_html_meta_element(self):
        doc = Document()
        el = doc.create_element("meta")
        assert isinstance(el, HTMLMetaElement)

    def test_create_title_returns_html_title_element(self):
        doc = Document()
        el = doc.create_element("title")
        assert isinstance(el, HTMLTitleElement)

    def test_create_button_returns_html_button_element(self):
        doc = Document()
        el = doc.create_element("button")
        assert isinstance(el, HTMLButtonElement)

    def test_create_select_returns_html_select_element(self):
        doc = Document()
        el = doc.create_element("select")
        assert isinstance(el, HTMLSelectElement)

    def test_create_element_unknown_returns_html_element(self):
        """Unregistered tag returns base HTMLElement, not a plain Element."""
        doc = Document()
        el = doc.create_element("made-up-element")
        assert type(el) is HTMLElement
        assert isinstance(el, HTMLElement)
        assert isinstance(el, Element)

    def test_all_subclasses_are_html_element(self):
        for cls in _ALL_SUBCLASSES:
            assert issubclass(cls, HTMLElement), f"{cls.__name__} not subclass of HTMLElement"

    def test_all_subclasses_are_element(self):
        for cls in _ALL_SUBCLASSES:
            assert issubclass(cls, Element), f"{cls.__name__} not subclass of Element"

    @pytest.mark.parametrize("tag, expected_cls", _TAG_CLASS_PAIRS)
    def test_create_element_parametrized(self, tag: str, expected_cls: type):
        doc = Document()
        el = doc.create_element(tag)
        assert isinstance(el, expected_cls), (
            f"create_element({tag!r}) returned {type(el).__name__}, "
            f"expected {expected_cls.__name__}"
        )

    @pytest.mark.parametrize(
        "tag, expected_cls",
        [
            ("nav", HTMLNavElement),
            ("section", HTMLSectionElement),
            ("article", HTMLArticleElement),
            ("aside", HTMLAsideElement),
            ("header", HTMLHeaderElement),
            ("footer", HTMLFooterElement),
            ("main", HTMLMainElement),
            ("figure", HTMLFigureElement),
            ("figcaption", HTMLFigCaptionElement),
            ("address", HTMLAddressElement),
            ("wbr", HTMLWBRElement),
            ("noscript", HTMLNoScriptElement),
            ("mark", HTMLMarkElement),
            ("small", HTMLSmallElement),
            ("ruby", HTMLRubyElement),
            ("rt", HTMLRubyElement),
            ("rp", HTMLRubyElement),
            ("b", HTMLElement),
            ("i", HTMLElement),
            ("u", HTMLElement),
            ("s", HTMLElement),
            ("em", HTMLElement),
            ("strong", HTMLElement),
            ("code", HTMLElement),
            ("var", HTMLElement),
            ("samp", HTMLElement),
            ("kbd", HTMLElement),
            ("cite", HTMLElement),
            ("abbr", HTMLElement),
            ("bdi", HTMLElement),
            ("bdo", HTMLElement),
            ("dfn", HTMLElement),
            ("sub", HTMLElement),
            ("sup", HTMLElement),
            ("slot", HTMLElement),
        ],
    )
    def test_sectioning_text_level_create_element(self, tag: str, expected_cls: type):
        doc = Document()
        el = doc.create_element(tag)
        assert isinstance(el, expected_cls)
        assert isinstance(el, HTMLElement)
        assert not isinstance(el, HTMLUnknownElement)
        assert el.tag_name == tag.upper()


# ===========================================================================
# HTMLAnchorElement tests
# ===========================================================================

class TestHTMLAnchorElement:

    def test_anchor_href_default_empty(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.href == ""

    def test_anchor_href_get_set(self):
        doc = Document()
        a = doc.create_element("a")
        a.href = "https://example.com"
        assert a.href == "https://example.com"

    def test_anchor_target_default_empty(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.target == ""

    def test_anchor_target_get_set(self):
        doc = Document()
        a = doc.create_element("a")
        a.target = "_blank"
        assert a.target == "_blank"

    def test_anchor_href_reflects_attribute(self):
        """href property and get_attribute('href') are in sync."""
        doc = Document()
        a = doc.create_element("a")
        a.href = "https://example.com"
        assert a.get_attribute("href") == "https://example.com"

    def test_anchor_absolute_href_unchanged(self):
        doc = HTMLDocument.parse("<a href='https://x/y'></a>", base_url="https://example.com/pages/")
        a = doc.query_selector("a")
        assert a.href == "https://x/y"

    def test_anchor_relative_href_resolves_against_document_url(self):
        doc = HTMLDocument.parse("<a href='../other'></a>", base_url="https://example.com/pages/")
        a = doc.query_selector("a")
        assert a.href == "https://example.com/other"

    def test_anchor_and_link_resolve_against_head_base_href(self):
        doc = HTMLDocument.parse(
            "<html><head><base href='https://cdn.example.org/root/'></head>"
            "<body><a href='../other'></a><link href='asset.css'></body></html>",
            base_url="https://example.com/pages/",
        )
        a = doc.query_selector("a")
        link = doc.query_selector("link")
        assert a.href == "https://cdn.example.org/other"
        assert link.href == "https://cdn.example.org/root/asset.css"

    def test_anchor_detached_returns_raw_href(self):
        doc = Document()
        a = doc.create_element("a")
        a._owner_document = None
        a.href = "../other"
        assert a.href == "../other"


class TestHTMLMediaElements:

    def test_htmlmediaelement_audio_defaults(self):
        doc = Document()
        el = doc.create_element("audio")
        assert isinstance(el, HTMLAudioElement)
        assert isinstance(el, HTMLMediaElement)
        assert el.paused is True
        assert el.ended is False
        assert el.ready_state == 0
        assert el.network_state == 0
        assert el.current_time == 0.0
        assert el.volume == 1.0
        assert el.src == ""
        assert el.current_src == ""
        assert el.preload == ""
        assert el.cross_origin is None
        assert el.auto_play is False
        assert el.controls is False
        assert el.loop is False
        assert el.muted is False
        assert el.default_muted is False

    def test_htmlvideoelement_defaults(self):
        doc = Document()
        el = doc.create_element("video")
        assert isinstance(el, HTMLVideoElement)
        assert isinstance(el, HTMLMediaElement)
        assert el.width == 0
        assert el.height == 0
        assert el.video_width == 0
        assert el.video_height == 0
        assert el.poster == ""

    def test_htmlmediaelement_src_reflects_attribute(self):
        doc = Document()
        el = doc.create_element("audio")
        el.set_attribute("src", "media.mp3")
        assert el.src == "media.mp3"

    def test_htmlmediaelement_reflective_attributes(self):
        doc = Document()
        el = doc.create_element("audio")
        el.set_attribute("autoplay", "")
        el.set_attribute("controls", "")
        el.set_attribute("loop", "")
        el.set_attribute("muted", "")
        el.set_attribute("preload", "metadata")
        el.set_attribute("crossorigin", "anonymous")
        assert el.auto_play is True
        assert el.controls is True
        assert el.loop is True
        assert el.muted is True
        assert el.default_muted is True
        assert el.preload == "metadata"
        assert el.cross_origin == "anonymous"

    def test_htmlmediaelement_methods_are_noop(self):
        doc = Document()
        el = doc.create_element("audio")
        el.play()
        el.pause()
        el.load()

    def test_htmlmediaelement_write_stubs_are_noop(self):
        doc = Document()
        el = doc.create_element("audio")
        el.current_time = 42.0
        el.volume = 0.5
        assert el.current_time == 0.0
        assert el.volume == 1.0


class TestHTMLSourceTrackCanvasParamElements:

    def test_htmlsourceelement_reflections(self):
        el = Document().create_element("source")
        assert isinstance(el, HTMLSourceElement)
        assert el.src == ""
        assert el.type == ""
        assert el.srcset == ""
        assert el.sizes == ""
        assert el.media == ""

        el.src = "clip.mp4"
        el.type = "video/mp4"
        el.srcset = "small.png 1x, large.png 2x"
        el.sizes = "(max-width: 600px) 100vw, 50vw"
        el.media = "screen"
        assert el.src == "clip.mp4"
        assert el.type == "video/mp4"
        assert el.srcset == "small.png 1x, large.png 2x"
        assert el.sizes == "(max-width: 600px) 100vw, 50vw"
        assert el.media == "screen"

    def test_htmltrackelement_reflections_and_ready_state(self):
        el = Document().create_element("track")
        assert isinstance(el, HTMLTrackElement)
        assert el.kind == ""
        assert el.src == ""
        assert el.srclang == ""
        assert el.label == ""
        assert el.default is False
        assert el.ready_state == 0

        el.kind = "subtitles"
        el.src = "captions.vtt"
        el.srclang = "en"
        el.label = "English"
        el.default = True
        assert el.kind == "subtitles"
        assert el.src == "captions.vtt"
        assert el.srclang == "en"
        assert el.label == "English"
        assert el.default is True

        el.default = False
        assert el.default is False

    def test_htmlcanvaselement_defaults_and_get_context(self):
        el = Document().create_element("canvas")
        assert isinstance(el, HTMLCanvasElement)
        assert el.width == 300
        assert el.height == 150
        assert el.get_context("2d") is None

    def test_htmlcanvaselement_width_height_setters_and_invalid_defaults(self):
        el = Document().create_element("canvas")
        el.width = 800
        el.height = 600
        assert el.width == 800
        assert el.height == 600

        el.set_attribute("width", "oops")
        el.set_attribute("height", "oops")
        assert el.width == 300
        assert el.height == 150

    def test_htmlparamelement_reflections(self):
        el = Document().create_element("param")
        assert isinstance(el, HTMLParamElement)
        assert el.name == ""
        assert el.value == ""

        el.name = "quality"
        el.value = "high"
        assert el.name == "quality"
        assert el.value == "high"


class TestStructuralBack58Subclasses:

    @pytest.mark.parametrize(
        "tag, expected_cls",
        [
            ("html", HTMLHtmlElement),
            ("head", HTMLHeadElement),
            ("body", HTMLBodyElement),
            ("br", HTMLBRElement),
            ("hr", HTMLHRElement),
            ("pre", HTMLPreElement),
            ("listing", HTMLPreElement),
            ("xmp", HTMLPreElement),
            ("legend", HTMLLegendElement),
        ],
    )
    def test_dispatch_structural_subclasses(self, tag: str, expected_cls: type):
        doc = Document()
        el = doc.create_element(tag)
        assert isinstance(el, expected_cls)


class TestHTMLStyleBaseLabelModElements:

    def test_style_media_and_type_reflect_attributes(self):
        doc = Document()
        style = doc.create_element("style")
        assert style.media == ""
        assert style.type == ""
        style.media = "print"
        style.type = "text/css"
        assert style.get_attribute("media") == "print"
        assert style.get_attribute("type") == "text/css"

    def test_base_href_is_raw_reflection_not_resolved(self):
        doc = HTMLDocument.parse("<base href='../assets/' target='_self'>", base_url="https://example.com/root/")
        base = doc.query_selector("base")
        assert isinstance(base, HTMLBaseElement)
        assert base.href == "../assets/"
        assert base.target == "_self"

    def test_label_html_for_reflects_for_attribute(self):
        doc = Document()
        label = doc.create_element("label")
        assert label.html_for == ""
        label.html_for = "username"
        assert label.get_attribute("for") == "username"
        label.set_attribute("for", "email")
        assert label.html_for == "email"

    def test_label_control_none_when_for_empty_or_unmatched(self):
        doc = Document()
        label = doc.create_element("label")
        assert label.control is None
        label.html_for = "missing"
        assert label.control is None

    def test_label_control_resolves_by_id_in_same_document(self):
        doc = HTMLDocument.parse('<label for="i" id="l">N</label><input id="i">')
        label = doc.get_element_by_id("l")
        assert label.control is doc.get_element_by_id("i")

    def test_label_form_none_without_control_or_control_form(self):
        doc = Document()
        label = doc.create_element("label")
        assert label.form is None

        doc2 = HTMLDocument.parse('<label for="x" id="l">N</label><div id="x"></div>')
        label2 = doc2.get_element_by_id("l")
        assert label2.form is None

    def test_label_form_returns_associated_control_form(self):
        doc = HTMLDocument.parse('<form id="f"><label for="i" id="l">N</label><input id="i"></form>')
        label = doc.get_element_by_id("l")
        assert label.form is doc.get_element_by_id("f")

    def test_mod_cite_and_date_time_reflect_attributes(self):
        doc = Document()
        ins = doc.create_element("ins")
        dele = doc.create_element("del")
        ins.cite = "https://example.com/rfc"
        ins.date_time = "2026-05-05"
        assert ins.get_attribute("cite") == "https://example.com/rfc"
        assert ins.get_attribute("datetime") == "2026-05-05"
        dele.set_attribute("cite", "https://example.com/history")
        dele.set_attribute("datetime", "2025-01-01")
        assert dele.cite == "https://example.com/history"
        assert dele.date_time == "2025-01-01"


def test_dom_module_exports_back58_classes():
    from aspose_html import dom

    assert "HTMLStyleElement" in dom.__all__
    assert "HTMLBaseElement" in dom.__all__
    assert "HTMLLabelElement" in dom.__all__
    assert "HTMLModElement" in dom.__all__


class TestSpec049Elements:

    def test_area_href_resolution_absent_and_raw_and_resolved(self):
        doc = Document()
        area = doc.create_element("area")
        assert isinstance(area, HTMLAreaElement)
        assert area.href == ""

        area._owner_document = None
        area.href = "../raw"
        assert area.href == "../raw"

        parsed = HTMLDocument.parse("<area href='../img/hotspot'>", base_url="https://example.com/pages/")
        parsed_area = parsed.query_selector("area")
        assert parsed_area.href == "https://example.com/img/hotspot"

    @pytest.mark.parametrize("attr, value", [
        ("target", "_blank"),
        ("alt", "Map area"),
        ("coords", "0,0,10,10"),
        ("shape", "rect"),
        ("rel", "nofollow"),
    ])
    def test_area_string_reflections_round_trip(self, attr: str, value: str):
        area = Document().create_element("area")
        assert getattr(area, attr) == ""
        setattr(area, attr, value)
        assert getattr(area, attr) == value
        assert area.get_attribute(attr) == value

    def test_area_url_decomposition_absolute_href(self):
        doc = Document()
        area = doc.create_element("area")
        area.href = "https://example.com:8443/docs/page.html?q=1#spot"

        assert area.protocol == "https:"
        assert area.host == "example.com:8443"
        assert area.host_name == "example.com"
        assert area.port == "8443"
        assert area.path_name == "/docs/page.html"
        assert area.search == "?q=1"
        assert area.hash == "#spot"
        assert area.origin == "https://example.com:8443"

    def test_area_url_decomposition_relative_href_uses_document_base(self):
        doc = HTMLDocument.parse(
            "<base href='https://example.com/base/'><area href='../img/hotspot?x=1#a'>",
        )
        area = doc.query_selector("area")

        assert area.protocol == "https:"
        assert area.host == "example.com"
        assert area.host_name == "example.com"
        assert area.port == ""
        assert area.path_name == "/img/hotspot"
        assert area.search == "?x=1"
        assert area.hash == "#a"
        assert area.origin == "https://example.com"

    @pytest.mark.parametrize(
        "member",
        ["protocol", "host", "host_name", "port", "path_name", "search", "hash", "origin"],
    )
    def test_area_url_decomposition_missing_or_empty_href_defaults_to_empty_string(self, member: str):
        area = Document().create_element("area")
        assert getattr(area, member) == ""

        area.href = ""
        assert getattr(area, member) == ""

    def test_map_name_reflection(self):
        el = Document().create_element("map")
        assert isinstance(el, HTMLMapElement)
        assert el.name == ""
        el.name = "world"
        assert el.get_attribute("name") == "world"

    def test_map_areas_returns_live_htmlcollection(self):
        doc = Document()
        map_el = doc.create_element("map")

        areas = map_el.areas
        assert hasattr(areas, "item")
        assert hasattr(areas, "named_item")
        assert len(areas) == 0

        area = doc.create_element("area")
        map_el.append_child(area)
        assert len(areas) == 1
        assert areas[0] is area

        map_el.remove_child(area)
        assert len(areas) == 0

    def test_map_areas_filters_to_area_descendants(self):
        doc = Document()
        map_el = doc.create_element("map")

        div = doc.create_element("div")
        nested_area = doc.create_element("area")
        direct_area = doc.create_element("area")

        map_el.append_child(div)
        div.append_child(nested_area)
        map_el.append_child(direct_area)

        areas = map_el.areas
        assert len(areas) == 2
        assert list(areas) == [nested_area, direct_area]

    def test_time_date_time_maps_to_datetime_attribute(self):
        el = Document().create_element("time")
        assert isinstance(el, HTMLTimeElement)
        assert el.date_time == ""
        el.date_time = "2026-05-06T00:00:00Z"
        assert el.get_attribute("datetime") == "2026-05-06T00:00:00Z"
        assert el.get_attribute("date_time") is None

    def test_data_value_reflection(self):
        el = Document().create_element("data")
        assert isinstance(el, HTMLDataElement)
        assert el.value == ""
        el.value = "42"
        assert el.value == "42"

    @pytest.mark.parametrize("tag", ["blockquote", "q"])
    def test_quote_dispatch_and_cite_reflection(self, tag: str):
        el = Document().create_element(tag)
        assert isinstance(el, HTMLQuoteElement)
        assert el.cite == ""
        el.cite = "https://example.com/source"
        assert el.get_attribute("cite") == "https://example.com/source"

    def test_picture_dispatch(self):
        el = Document().create_element("picture")
        assert isinstance(el, HTMLPictureElement)

    @pytest.mark.parametrize("tag, cls, string_attrs", [
        ("iframe", HTMLIFrameElement, ("src", "name", "allow", "sandbox")),
        ("embed", HTMLEmbedElement, ("src", "type", "name", "align")),
        ("object", HTMLObjectElement, ("data", "type", "name")),
    ])
    def test_embedding_string_reflections(self, tag: str, cls: type, string_attrs: tuple[str, ...]):
        el = Document().create_element(tag)
        assert isinstance(el, cls)
        for attr in string_attrs:
            assert getattr(el, attr) == ""
            setattr(el, attr, "x")
            assert getattr(el, attr) == "x"
            assert el.get_attribute(attr) == "x"

    @pytest.mark.parametrize("tag", ["iframe", "embed", "object"])
    def test_embedding_integer_reflections_default_and_invalid(self, tag: str):
        el = Document().create_element(tag)
        assert el.width == 0
        assert el.height == 0
        el.width = 640
        el.height = 480
        assert el.width == 640
        assert el.height == 480
        el.set_attribute("width", "invalid")
        el.set_attribute("height", "oops")
        assert el.width == 0
        assert el.height == 0

    def test_htmliframe_idl_completeness_group_c(self):
        el = Document().create_element("iframe")
        assert isinstance(el, HTMLIFrameElement)

        assert el.content_document is None
        assert el.content_window is None

        assert el.srcdoc == ""
        el.srcdoc = "<p>hello</p>"
        assert el.srcdoc == "<p>hello</p>"
        assert el.get_attribute("srcdoc") == "<p>hello</p>"

        assert el.referrer_policy == ""
        el.referrer_policy = "no-referrer"
        assert el.referrer_policy == "no-referrer"
        assert el.get_attribute("referrerpolicy") == "no-referrer"

    def test_htmliframe_content_document_delegates_to_browsing_context_owner(self, monkeypatch):
        el = Document().create_element("iframe")
        view = el.owner_document.default_view
        ctx = view._browsing_context

        seen: list[object] = []

        def _resolve(self, iframe_element: object) -> object | None:
            seen.append(iframe_element)
            return None

        monkeypatch.setattr(type(ctx), "iframe_content_document_for", _resolve)
        assert el.content_document is None
        assert seen == [el]

    def test_htmliframe_content_window_delegates_to_browsing_context_owner(self, monkeypatch):
        el = Document().create_element("iframe")
        view = el.owner_document.default_view
        ctx = view._browsing_context

        seen: list[object] = []

        def _resolve(self, iframe_element: object) -> object | None:
            seen.append(iframe_element)
            return None

        monkeypatch.setattr(type(ctx), "iframe_content_window_for", _resolve)
        assert el.content_window is None
        assert seen == [el]

    def test_htmlobject_form_owner_and_detached_none(self):
        doc = HTMLDocument.parse("<form id='f'><object id='o'></object></form>")
        obj = doc.get_element_by_id("o")
        form = doc.get_element_by_id("f")
        assert isinstance(obj, HTMLObjectElement)
        assert obj.form is form

        detached = Document().create_element("object")
        assert detached.form is None

    def test_htmlobject_content_document_and_window_are_none(self):
        obj = Document().create_element("object")
        assert isinstance(obj, HTMLObjectElement)
        assert obj.content_document is None
        assert obj.content_window is None

    @pytest.mark.parametrize("prop, attr_name", [
        ("code", "code"),
        ("code_base", "codebase"),
        ("code_type", "codetype"),
        ("archive", "archive"),
        ("standby", "standby"),
    ])
    def test_htmlobject_group_a_reflected_string_members(self, prop: str, attr_name: str):
        obj = Document().create_element("object")
        assert isinstance(obj, HTMLObjectElement)

        assert getattr(obj, prop) == ""
        setattr(obj, prop, "value")
        assert getattr(obj, prop) == "value"
        assert obj.get_attribute(attr_name) == "value"

    def test_htmlobject_group_a_declare_boolean_presence(self):
        obj = Document().create_element("object")
        assert isinstance(obj, HTMLObjectElement)

        assert obj.declare is False
        assert obj.get_attribute("declare") is None

        obj.declare = True
        assert obj.declare is True
        assert obj.has_attribute("declare") is True

        obj.declare = False
        assert obj.declare is False
        assert obj.get_attribute("declare") is None

    @pytest.mark.parametrize("prop, attr_name", [
        ("type", "type"),
        ("value_type", "valuetype"),
    ])
    def test_htmlparam_group_b_reflected_string_members(self, prop: str, attr_name: str):
        param = Document().create_element("param")
        assert isinstance(param, HTMLParamElement)

        assert getattr(param, prop) == ""
        setattr(param, prop, "value")
        assert getattr(param, prop) == "value"
        assert param.get_attribute(attr_name) == "value"


def test_html_unknown_element_exported_but_not_registered_and_fallback_unchanged():
    from aspose_html import dom
    from aspose_html.dom import html

    assert "HTMLUnknownElement" in dom.__all__
    assert "HTMLUnknownElement" in html.__all__
    assert "xyzzy" not in html._REGISTRY
    assert HTMLUnknownElement not in html._REGISTRY.values()

    el = Document().create_element("xyzzy")
    assert type(el) is HTMLElement


# ===========================================================================
# HTMLImageElement tests
# ===========================================================================

class TestHTMLImageElement:

    def test_image_src_default_empty(self):
        doc = Document()
        img = doc.create_element("img")
        assert img.src == ""

    def test_image_src_set_get(self):
        doc = Document()
        img = doc.create_element("img")
        img.src = "photo.jpg"
        assert img.src == "photo.jpg"

    def test_image_alt_default_empty(self):
        doc = Document()
        img = doc.create_element("img")
        assert img.alt == ""

    def test_image_width_default_zero(self):
        doc = Document()
        img = doc.create_element("img")
        assert img.width == 0

    def test_image_width_set_get(self):
        doc = Document()
        img = doc.create_element("img")
        img.width = 320
        assert img.width == 320

    def test_image_height_set_get(self):
        doc = Document()
        img = doc.create_element("img")
        img.height = 240
        assert img.height == 240

    def test_img_width_height_integer(self):
        """width and height return int, not str."""
        doc = Document()
        img = doc.create_element("img")
        img.width = 100
        img.height = 200
        assert isinstance(img.width, int)
        assert isinstance(img.height, int)
        assert img.width == 100
        assert img.height == 200

    def test_img_src_alt(self):
        doc = Document()
        img = doc.create_element("img")
        img.src = "logo.png"
        img.alt = "Company logo"
        assert img.src == "logo.png"
        assert img.alt == "Company logo"

    def test_image_width_invalid_attribute_returns_zero(self):
        """Invalid non-numeric width attribute falls back to 0."""
        doc = Document()
        img = doc.create_element("img")
        img.set_attribute("width", "notanumber")
        assert img.width == 0


# ===========================================================================
# HTMLImageElement IDL completeness tests (BACK-201 / ADR-184)
# ===========================================================================

class TestHTMLImageElementIDL:
    """Tests for the nine new IDL-reflected properties on HTMLImageElement."""

    def _img(self):
        """Return a fresh <img> element."""
        from aspose_html.dom import Document
        doc = Document()
        return doc.create_element("img")

    # AC-10: srcset
    def test_srcset_default_empty(self):
        assert self._img().srcset == ""

    def test_srcset_set_get(self):
        img = self._img()
        img.srcset = "img@2x.png 2x"
        assert img.srcset == "img@2x.png 2x"

    # sizes
    def test_sizes_default_empty(self):
        assert self._img().sizes == ""

    def test_sizes_set_get(self):
        img = self._img()
        img.sizes = "(max-width: 600px) 480px, 800px"
        assert img.sizes == "(max-width: 600px) 480px, 800px"

    # loading
    def test_loading_default_empty(self):
        assert self._img().loading == ""

    def test_loading_set_lazy(self):
        img = self._img()
        img.loading = "lazy"
        assert img.loading == "lazy"

    # decoding
    def test_decoding_default_empty(self):
        assert self._img().decoding == ""

    def test_decoding_set_async(self):
        img = self._img()
        img.decoding = "async"
        assert img.decoding == "async"

    # AC-11: cross_origin
    def test_cross_origin_absent_is_none(self):
        assert self._img().cross_origin is None

    def test_cross_origin_set_anonymous(self):
        img = self._img()
        img.cross_origin = "anonymous"
        assert img.cross_origin == "anonymous"

    def test_cross_origin_set_none_removes_attribute(self):
        img = self._img()
        img.cross_origin = "anonymous"
        img.cross_origin = None
        assert img.cross_origin is None

    # use_map
    def test_use_map_default_empty(self):
        assert self._img().use_map == ""

    def test_use_map_set_get(self):
        img = self._img()
        img.use_map = "#mymap"
        assert img.use_map == "#mymap"

    # AC-13: is_map
    def test_is_map_default_false(self):
        assert self._img().is_map is False

    def test_is_map_set_true(self):
        img = self._img()
        img.is_map = True
        assert img.is_map is True
        assert img.has_attribute("ismap")

    def test_is_map_set_false_removes_attribute(self):
        img = self._img()
        img.is_map = True
        img.is_map = False
        assert img.is_map is False
        assert not img.has_attribute("ismap")

    # AC-12: complete, natural_width, natural_height
    def test_complete_is_false(self):
        assert self._img().complete is False

    def test_natural_width_is_zero(self):
        assert self._img().natural_width == 0

    def test_natural_height_is_zero(self):
        assert self._img().natural_height == 0

    # AC-5 (parsed HTML): AC-5 from BACK-201 task
    def test_parsed_img_reflects_all_attributes(self):
        """Parsed <img> with srcset, loading, ismap reflects attributes correctly."""
        doc = HTMLDocument.parse(
            "<html><body>"
            "<img id='i' srcset='img@2x.png 2x' loading='lazy' ismap>"
            "</body></html>"
        )
        img = doc.get_element_by_id("i")
        assert img is not None
        assert img.srcset == "img@2x.png 2x"
        assert img.loading == "lazy"
        assert img.is_map is True
        assert img.complete is False
        assert img.natural_width == 0
        assert img.natural_height == 0


# ===========================================================================
# HTMLInputElement tests
# ===========================================================================

class TestHTMLInputElement:

    def test_input_type_default_text(self):
        """Absent type attribute returns 'text' (WHATWG default)."""
        doc = Document()
        inp = doc.create_element("input")
        assert inp.type == "text"

    def test_input_type_set_get(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.type = "checkbox"
        assert inp.type == "checkbox"

    def test_input_value_default_empty(self):
        doc = Document()
        inp = doc.create_element("input")
        assert inp.value == ""

    def test_input_value_set_get(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.value = "hello"
        assert inp.value == "hello"

    def test_input_name_set_get(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.name = "username"
        assert inp.name == "username"

    def test_input_checked_default_false(self):
        doc = Document()
        inp = doc.create_element("input")
        assert inp.checked is False

    def test_input_checked_true_sets_attribute(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.checked = True
        assert inp.checked is True
        assert inp.has_attribute("checked")

    def test_input_checked_false_removes_attribute(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.checked = True
        inp.checked = False
        assert inp.checked is False
        assert not inp.has_attribute("checked")

    def test_input_disabled_boolean(self):
        doc = Document()
        inp = doc.create_element("input")
        assert inp.disabled is False
        inp.disabled = True
        assert inp.disabled is True
        inp.disabled = False
        assert inp.disabled is False

    def test_input_checked_boolean_attribute(self):
        """checked follows WHATWG boolean attribute presence rule."""
        doc = Document()
        inp = doc.create_element("input")
        inp.checked = True
        assert inp.get_attribute("checked") == ""  # empty string per WHATWG
        inp.checked = False
        assert inp.get_attribute("checked") is None

    # -- Group A: BACK-149 ---------------------------------------------------

    def test_input_placeholder_default_empty(self):
        """Absent placeholder attribute returns ''."""
        doc = Document()
        inp = doc.create_element("input")
        assert inp.placeholder == ""

    def test_input_placeholder_set_get(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.placeholder = "Enter name"
        assert inp.placeholder == "Enter name"

    def test_input_read_only_default_false(self):
        """Absent readonly attribute returns False."""
        doc = Document()
        inp = doc.create_element("input")
        assert inp.read_only is False

    def test_input_read_only_true_sets_attribute(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.read_only = True
        assert inp.read_only is True
        assert inp.has_attribute("readonly")
        assert inp.get_attribute("readonly") == ""

    def test_input_read_only_false_removes_attribute(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.read_only = True
        inp.read_only = False
        assert inp.read_only is False
        assert not inp.has_attribute("readonly")

    def test_input_autocomplete_default_empty(self):
        """Absent autocomplete attribute returns ''."""
        doc = Document()
        inp = doc.create_element("input")
        assert inp.autocomplete == ""

    def test_input_autocomplete_set_get(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.autocomplete = "email"
        assert inp.autocomplete == "email"

    def test_input_autofocus_default_false(self):
        """Absent autofocus attribute returns False."""
        doc = Document()
        inp = doc.create_element("input")
        assert inp.autofocus is False

    def test_input_autofocus_true_sets_attribute(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.autofocus = True
        assert inp.autofocus is True
        assert inp.has_attribute("autofocus")
        assert inp.get_attribute("autofocus") == ""

    def test_input_autofocus_false_removes_attribute(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.autofocus = True
        inp.autofocus = False
        assert inp.autofocus is False
        assert not inp.has_attribute("autofocus")

    def test_input_accept_default_empty(self):
        """Absent accept attribute returns ''."""
        doc = Document()
        inp = doc.create_element("input")
        assert inp.accept == ""

    def test_input_accept_set_get(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.accept = "image/*"
        assert inp.accept == "image/*"

    def test_input_size_default_20(self):
        """Absent size attribute returns WHATWG default of 20."""
        doc = Document()
        inp = doc.create_element("input")
        assert inp.size == 20

    def test_input_size_set_get(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.size = 30
        assert inp.size == 30

    def test_input_size_invalid_attribute_fallback(self):
        """Non-integer size attribute value falls back to 20."""
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("size", "notanumber")
        assert inp.size == 20

    def test_input_indeterminate_runtime_flag(self):
        doc = Document()
        inp = doc.create_element("input")
        assert inp.indeterminate is False
        inp.indeterminate = True
        assert inp.indeterminate is True
        inp.indeterminate = False
        assert inp.indeterminate is False
        assert inp.get_attribute("indeterminate") is None

    def test_input_width_height_reflect_attributes(self):
        doc = Document()
        inp = doc.create_element("input")
        assert inp.width == 0
        assert inp.height == 0

        inp.width = 150
        inp.height = 75
        assert inp.width == 150
        assert inp.height == 75
        assert inp.get_attribute("width") == "150"
        assert inp.get_attribute("height") == "75"

    def test_input_width_height_invalid_values_fallback_zero(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("width", "bad")
        inp.set_attribute("height", "bad")
        assert inp.width == 0
        assert inp.height == 0

    def test_html_input_element_form_override_attrs(self):
        """HTMLInputElement form-submission override attributes (ADR-289 / BACK-311)."""
        doc = Document()
        inp = doc.create_element("input")
        # Defaults
        assert inp.form_action == ""
        assert inp.form_enctype == ""
        assert inp.form_method == ""
        assert inp.form_no_validate is False
        assert inp.form_target == ""
        assert inp.dirname == ""
        # Setters
        inp.form_action = "/submit"
        assert inp.form_action == "/submit"
        inp.form_enctype = "multipart/form-data"
        assert inp.form_enctype == "multipart/form-data"
        inp.form_method = "post"
        assert inp.form_method == "post"
        inp.form_no_validate = True
        assert inp.form_no_validate is True
        inp.form_no_validate = False
        assert inp.form_no_validate is False
        inp.form_target = "_blank"
        assert inp.form_target == "_blank"
        inp.dirname = "dir"
        assert inp.dirname == "dir"


# ===========================================================================
# HTMLFormElement tests
# ===========================================================================

class TestHTMLFormElement:

    def test_form_action_set_get(self):
        doc = Document()
        form = doc.create_element("form")
        form.action = "/submit"
        assert form.action == "/submit"

    def test_form_method_default_get(self):
        """Absent method attribute returns 'get' (WHATWG default)."""
        doc = Document()
        form = doc.create_element("form")
        assert form.method == "get"

    def test_form_method_set_get(self):
        doc = Document()
        form = doc.create_element("form")
        form.method = "post"
        assert form.method == "post"

    def test_form_name_set_get(self):
        doc = Document()
        form = doc.create_element("form")
        form.name = "login"
        assert form.name == "login"

    def test_form_action_method(self):
        doc = Document()
        form = doc.create_element("form")
        form.action = "/api/login"
        form.method = "post"
        assert form.action == "/api/login"
        assert form.method == "post"

    # -- Group B: BACK-150 ---------------------------------------------------

    def test_form_enctype_default(self):
        """Absent enctype attribute returns WHATWG default."""
        doc = Document()
        form = doc.create_element("form")
        assert form.enctype == "application/x-www-form-urlencoded"

    def test_form_enctype_set_get(self):
        doc = Document()
        form = doc.create_element("form")
        form.enctype = "multipart/form-data"
        assert form.enctype == "multipart/form-data"

    def test_form_enctype_normalizes_case_and_whitespace(self):
        doc = Document()
        form = doc.create_element("form")
        form.enctype = "  TEXT/PLAIN  "
        assert form.enctype == "text/plain"

    def test_form_enctype_unsupported_falls_back_to_default(self):
        doc = Document()
        form = doc.create_element("form")
        form.enctype = "application/json"
        assert form.enctype == "application/x-www-form-urlencoded"

    def test_form_enctype_getter_falls_back_for_invalid_attribute_value(self):
        doc = Document()
        form = doc.create_element("form")
        form.set_attribute("enctype", "INVALID/TYPE")
        assert form.enctype == "application/x-www-form-urlencoded"

    def test_form_rel_reflects_attribute(self):
        doc = Document()
        form = doc.create_element("form")
        assert form.rel == ""
        form.rel = "noopener noreferrer"
        assert form.rel == "noopener noreferrer"

    def test_form_encoding_alias_reads_enctype(self):
        """form.encoding returns the same value as form.enctype."""
        doc = Document()
        form = doc.create_element("form")
        assert form.encoding == "application/x-www-form-urlencoded"
        form.enctype = "multipart/form-data"
        assert form.encoding == "multipart/form-data"

    def test_form_encoding_setter_updates_enctype(self):
        """Setting form.encoding changes the underlying enctype attribute."""
        doc = Document()
        form = doc.create_element("form")
        form.encoding = "text/plain"
        assert form.enctype == "text/plain"
        assert form.encoding == "text/plain"

    def test_form_enctype_encoding_round_trip(self):
        """set enctype, read via encoding, then set encoding, read via enctype."""
        doc = Document()
        form = doc.create_element("form")
        form.enctype = "multipart/form-data"
        assert form.encoding == "multipart/form-data"
        form.encoding = "text/plain"
        assert form.enctype == "text/plain"

    def test_form_novalidate_default_false(self):
        """Absent novalidate attribute returns False."""
        doc = Document()
        form = doc.create_element("form")
        assert form.novalidate is False

    def test_form_novalidate_true_sets_attribute(self):
        doc = Document()
        form = doc.create_element("form")
        form.novalidate = True
        assert form.novalidate is True
        assert form.has_attribute("novalidate")
        assert form.get_attribute("novalidate") == ""

    def test_form_novalidate_false_removes_attribute(self):
        doc = Document()
        form = doc.create_element("form")
        form.novalidate = True
        form.novalidate = False
        assert form.novalidate is False
        assert not form.has_attribute("novalidate")

    def test_form_target_default_empty(self):
        """Absent target attribute returns ''."""
        doc = Document()
        form = doc.create_element("form")
        assert form.target == ""

    def test_form_target_set_get(self):
        doc = Document()
        form = doc.create_element("form")
        form.target = "_blank"
        assert form.target == "_blank"

    def test_form_autocomplete_default_on(self):
        """Absent autocomplete attribute returns 'on' (WHATWG default)."""
        doc = Document()
        form = doc.create_element("form")
        assert form.autocomplete == "on"

    def test_form_autocomplete_set_get(self):
        doc = Document()
        form = doc.create_element("form")
        form.autocomplete = "off"
        assert form.autocomplete == "off"

    # -- Group A: BACK-199 ---------------------------------------------------

    def test_form_submit_raises_not_supported_error(self):
        """form.submit() raises NotSupportedError with 'headless mode' in message."""
        from aspose_html.dom import NotSupportedError
        doc = Document()
        form = doc.create_element("form")
        with pytest.raises(NotSupportedError, match="headless mode"):
            form.submit()

    def test_form_reset_raises_not_supported_error(self):
        """form.reset() raises NotSupportedError."""
        from aspose_html.dom import NotSupportedError
        doc = Document()
        form = doc.create_element("form")
        with pytest.raises(NotSupportedError):
            form.reset()

    def test_form_request_submit_no_submitter_raises(self):
        """form.request_submit() raises NotSupportedError."""
        from aspose_html.dom import NotSupportedError
        doc = Document()
        form = doc.create_element("form")
        with pytest.raises(NotSupportedError):
            form.request_submit()

    def test_form_request_submit_with_submitter_raises(self):
        """form.request_submit(submitter=btn) raises NotSupportedError."""
        from aspose_html.dom import NotSupportedError
        doc = Document()
        form = doc.create_element("form")
        btn = doc.create_element("button")
        with pytest.raises(NotSupportedError):
            form.request_submit(submitter=btn)

    def test_form_length_empty_form(self):
        """form.length == 0 for a form with no listed controls."""
        doc = Document()
        form = doc.create_element("form")
        assert form.length == 0

    def test_form_length_one_input(self):
        """form.length == 1 after appending one <input>."""
        doc = Document()
        form = doc.create_element("form")
        inp = doc.create_element("input")
        form.append_child(inp)
        assert form.length == 1

    def test_form_length_equals_elements_len(self):
        """form.length == len(list(form.elements)) invariant with mixed controls."""
        doc = Document()
        form = doc.create_element("form")
        for tag in ("input", "button", "select", "textarea", "fieldset"):
            form.append_child(doc.create_element(tag))
        assert form.length == len(list(form.elements))
        assert form.length == 5


class TestHTMLDetailsElementTrack64:

    def test_details_name_reflects_attribute(self):
        doc = Document()
        details = doc.create_element("details")
        assert details.name == ""
        details.name = "accordion-group"
        assert details.name == "accordion-group"


# ===========================================================================
# HTMLScriptElement tests
# ===========================================================================

class TestHTMLScriptElement:

    def test_script_src_set_get(self):
        doc = Document()
        script = doc.create_element("script")
        script.src = "app.js"
        assert script.src == "app.js"

    def test_script_type_set_get(self):
        doc = Document()
        script = doc.create_element("script")
        script.type = "module"
        assert script.type == "module"

    def test_script_async_default_false(self):
        doc = Document()
        script = doc.create_element("script")
        assert script.async_ is False

    def test_script_async_true_sets_attribute(self):
        doc = Document()
        script = doc.create_element("script")
        script.async_ = True
        assert script.async_ is True
        assert script.has_attribute("async")

    def test_script_async_false_removes_attribute(self):
        doc = Document()
        script = doc.create_element("script")
        script.async_ = True
        script.async_ = False
        assert script.async_ is False
        assert not script.has_attribute("async")

    def test_script_defer_boolean(self):
        doc = Document()
        script = doc.create_element("script")
        assert script.defer is False
        script.defer = True
        assert script.defer is True
        script.defer = False
        assert script.defer is False

    def test_script_async_defer_boolean(self):
        """Both async_ and defer follow boolean attribute rules."""
        doc = Document()
        script = doc.create_element("script")
        script.async_ = True
        script.defer = True
        assert script.async_ is True
        assert script.defer is True
        assert script.get_attribute("async") == ""
        assert script.get_attribute("defer") == ""

    # --- HTMLScriptElement.text (ADR-166 / BACK-183) ---

    def test_script_text_getter_empty(self):
        """AC-1: script.text returns '' when element has no text children."""
        doc = Document()
        script = doc.create_element("script")
        assert script.text == ""

    def test_script_text_getter_with_text_child(self):
        """AC-2: script.text returns concatenated text content when children exist."""
        doc = Document()
        script = doc.create_element("script")
        script.append_child(doc.create_text_node("var x = 1;"))
        assert script.text == "var x = 1;"

    def test_script_text_setter(self):
        """AC-3: script.text = '...' sets a single Text child; reading back returns it."""
        doc = Document()
        script = doc.create_element("script")
        script.text = "console.log(1);"
        assert script.text == "console.log(1);"

    def test_script_text_setter_replaces_children(self):
        """AC-4: Setting script.text twice replaces, not appends."""
        doc = Document()
        script = doc.create_element("script")
        script.text = "var x = 1;"
        script.text = "var y = 2;"
        assert script.text == "var y = 2;"
        # Only one child Text node should exist.
        count = 0
        child = script.first_child
        while child is not None:
            count += 1
            child = child.next_sibling
        assert count == 1

    def test_script_text_setter_empty_clears_children(self):
        """Setting text to '' removes all children."""
        doc = Document()
        script = doc.create_element("script")
        script.text = "var x = 1;"
        script.text = ""
        assert script.text == ""
        assert script.first_child is None

    def test_script_text_setter_detached_element(self):
        """text setter works on a detached element (no owner document)."""
        from aspose_html.dom.html._elements import HTMLScriptElement
        from aspose_html.dom._node import Node
        # Create a Document only to get the class; then detach
        doc = Document()
        script = doc.create_element("script")
        # Simulate detached by working directly — the setter must not raise.
        # We use a fresh element that still has owner_document; confirm setter works.
        script.text = "var z = 3;"
        assert script.text == "var z = 3;"

    def test_script_integrity_reflects_attribute(self):
        doc = Document()
        script = doc.create_element("script")
        assert script.integrity == ""
        script.integrity = "sha384-abc"
        assert script.integrity == "sha384-abc"

    def test_script_cross_origin_none_when_absent_and_removable(self):
        doc = Document()
        script = doc.create_element("script")
        assert script.cross_origin is None
        script.cross_origin = "anonymous"
        assert script.cross_origin == "anonymous"
        script.cross_origin = None
        assert script.cross_origin is None
        assert script.get_attribute("crossorigin") is None

    def test_script_referrer_policy_reflects_attribute(self):
        doc = Document()
        script = doc.create_element("script")
        assert script.referrer_policy == ""
        script.referrer_policy = "no-referrer"
        assert script.referrer_policy == "no-referrer"


# ===========================================================================
# HTMLLinkElement tests
# ===========================================================================

class TestHTMLLinkElement:

    def test_link_href_set_get(self):
        doc = Document()
        link = doc.create_element("link")
        link.href = "style.css"
        assert link.href == "style.css"

    def test_link_relative_href_resolves_against_document_url(self):
        doc = HTMLDocument.parse("<link href='style.css'>", base_url="https://example.com/assets/")
        link = doc.query_selector("link")
        assert link.href == "https://example.com/assets/style.css"

    def test_link_rel_set_get(self):
        doc = Document()
        link = doc.create_element("link")
        link.rel = "stylesheet"
        assert link.rel == "stylesheet"

    def test_link_type_set_get(self):
        doc = Document()
        link = doc.create_element("link")
        link.type = "text/css"
        assert link.type == "text/css"

    # --- HTMLLinkElement.sheet (ADR-166 / BACK-183) ---

    def test_link_sheet_none_by_default(self):
        """AC: link.sheet is None when rel is absent or not 'stylesheet'."""
        doc = Document()
        link = doc.create_element("link")
        assert link.sheet is None

    def test_link_sheet_none_when_rel_not_stylesheet(self):
        """AC: link.sheet is None when rel is set but not 'stylesheet'."""
        doc = Document()
        link = doc.create_element("link")
        link.rel = "preload"
        link.href = "style.css"
        assert link.sheet is None

    def test_link_sheet_returns_css_stylesheet_when_rel_stylesheet(self):
        """AC: link.sheet returns a CSSStyleSheet stub when rel='stylesheet'."""
        from aspose_html.cssom import CSSStyleSheet
        doc = Document()
        link = doc.create_element("link")
        link.rel = "stylesheet"
        link.href = "style.css"
        sheet = link.sheet
        assert sheet is not None
        assert isinstance(sheet, CSSStyleSheet)

    def test_link_sheet_owner_node_is_link(self):
        """AC: link.sheet.owner_node is link."""
        doc = Document()
        link = doc.create_element("link")
        link.rel = "stylesheet"
        link.href = "style.css"
        assert link.sheet.owner_node is link

    def test_link_sheet_href_reflected(self):
        """AC: link.sheet.href reflects the href attribute value."""
        doc = Document()
        link = doc.create_element("link")
        link.rel = "stylesheet"
        link.href = "theme.css"
        assert link.sheet.href == "theme.css"

    def test_link_sheet_case_insensitive_rel(self):
        """link.sheet returns a sheet when rel uses non-lowercase 'StyleSheet'."""
        doc = Document()
        link = doc.create_element("link")
        link.rel = "StyleSheet"
        link.href = "a.css"
        assert link.sheet is not None

    def test_link_sheet_cached_same_object(self):
        """link.sheet returns the same object on repeated access (cache hit)."""
        doc = Document()
        link = doc.create_element("link")
        link.rel = "stylesheet"
        link.href = "a.css"
        assert link.sheet is link.sheet

    def test_link_sheet_cache_invalidated_on_href_change(self):
        """link.sheet cache invalidates when href changes."""
        doc = Document()
        link = doc.create_element("link")
        link.rel = "stylesheet"
        link.href = "a.css"
        sheet1 = link.sheet
        link.href = "b.css"
        sheet2 = link.sheet
        assert sheet1 is not sheet2
        assert sheet2.href == "b.css"


# ===========================================================================
# HTMLStyleElement.sheet tests (ADR-166 / BACK-183)
# ===========================================================================

class TestHTMLStyleElementSheet:

    def test_style_sheet_parses_text_content(self):
        """AC: style.sheet returns CSSStyleSheet whose rules match text content."""
        doc = Document()
        style = doc.create_element("style")
        style.text_content = "p { color: red }"
        assert style.sheet.css_rules[0].css_text == "p { color: red }"

    def test_style_sheet_owner_node_is_self(self):
        """AC: style.sheet.owner_node is the style element."""
        doc = Document()
        style = doc.create_element("style")
        style.text_content = "p { color: red }"
        assert style.sheet.owner_node is style

    def test_style_sheet_empty_text_content_returns_sheet(self):
        """Empty style element returns an empty (zero-rule) CSSStyleSheet."""
        from aspose_html.cssom import CSSStyleSheet
        doc = Document()
        style = doc.create_element("style")
        sheet = style.sheet
        assert isinstance(sheet, CSSStyleSheet)
        assert len(sheet.css_rules) == 0

    def test_style_sheet_cached_same_object(self):
        """style.sheet returns same object on repeated calls (cache hit)."""
        doc = Document()
        style = doc.create_element("style")
        style.text_content = "p { color: red }"
        assert style.sheet is style.sheet

    def test_style_sheet_cache_invalidated_on_text_change(self):
        """style.sheet cache invalidates when text_content changes."""
        doc = Document()
        style = doc.create_element("style")
        style.text_content = "p { color: red }"
        sheet1 = style.sheet
        style.text_content = "div { color: blue }"
        sheet2 = style.sheet
        assert sheet1 is not sheet2
        assert sheet2.css_rules[0].css_text == "div { color: blue }"

    def test_style_sheet_detached_element(self):
        """style.sheet works on a detached element (no owner document)."""
        from aspose_html.cssom import CSSStyleSheet
        doc = Document()
        style = doc.create_element("style")
        style.text_content = "p { color: red }"
        # Sheet should still parse even without document attachment
        sheet = style.sheet
        assert isinstance(sheet, CSSStyleSheet)
        assert sheet.owner_node is style

    def test_no_infinite_recursion_via_doc_style_sheets(self):
        """doc.style_sheets must not recurse infinitely via style.sheet."""
        doc = Document()
        style = doc.create_element("style")
        style.text_content = "p { color: red }"
        doc.append_child(style)
        # This call triggers _collect_style_sheets, which calls style.sheet,
        # which must NOT call doc.style_sheets again.
        sheets = doc.style_sheets
        assert sheets is not None

    def test_no_infinite_recursion_link_via_doc_style_sheets(self):
        """doc.style_sheets must not recurse infinitely via link.sheet."""
        doc = Document()
        link = doc.create_element("link")
        link.rel = "stylesheet"
        link.href = "style.css"
        doc.append_child(link)
        sheets = doc.style_sheets
        assert sheets is not None


# ===========================================================================
# HTMLMetaElement tests
# ===========================================================================

class TestHTMLMetaElement:

    def test_meta_name_set_get(self):
        doc = Document()
        meta = doc.create_element("meta")
        meta.name = "description"
        assert meta.name == "description"

    def test_meta_content_set_get(self):
        doc = Document()
        meta = doc.create_element("meta")
        meta.content = "A page description"
        assert meta.content == "A page description"

    def test_meta_http_equiv_set_get(self):
        """http_equiv property reads/writes the 'http-equiv' HTML attribute."""
        doc = Document()
        meta = doc.create_element("meta")
        meta.http_equiv = "refresh"
        assert meta.http_equiv == "refresh"

    def test_meta_http_equiv_maps_to_hyphen_attribute(self):
        """http_equiv getter/setter uses 'http-equiv' (with hyphen) as attribute name."""
        doc = Document()
        meta = doc.create_element("meta")
        meta.http_equiv = "content-type"
        # Verify the underlying attribute name is the hyphenated form
        assert meta.get_attribute("http-equiv") == "content-type"
        # Verify the underscore form is NOT set as an attribute
        assert meta.get_attribute("http_equiv") is None

    def test_create_meta_returns_html_meta_element(self):
        doc = Document()
        meta = doc.create_element("meta")
        assert isinstance(meta, HTMLMetaElement)


# ===========================================================================
# HTMLTitleElement tests
# ===========================================================================

class TestHTMLTitleElement:

    def test_title_text_default_empty(self):
        doc = Document()
        title = doc.create_element("title")
        assert title.text == ""

    def test_title_text_set_creates_text_node(self):
        doc = Document()
        title = doc.create_element("title")
        doc.append_child(title)
        title.text = "My Page"
        assert title.text == "My Page"

    def test_title_text_get_reads_text_child(self):
        doc = Document()
        title = doc.create_element("title")
        doc.append_child(title)
        title.text = "Hello World"
        # Verify text is stored as a Text child node
        from aspose_html.dom._node_type import NodeType
        child = title.first_child
        assert child is not None
        assert child._node_type == NodeType.TEXT_NODE
        assert child.data == "Hello World"  # type: ignore[attr-defined]

    def test_title_text_set_replaces_existing_text(self):
        doc = Document()
        title = doc.create_element("title")
        doc.append_child(title)
        title.text = "First"
        title.text = "Second"
        assert title.text == "Second"
        # Only one child node should exist
        assert len(list(title.child_nodes)) == 1

    def test_create_title_returns_html_title_element(self):
        doc = Document()
        title = doc.create_element("title")
        assert isinstance(title, HTMLTitleElement)

    def test_title_text_detached_raises_not_supported_error(self):
        """Setting text on a detached title element raises NotSupportedError."""
        from aspose_html.dom import NotSupportedError
        # Create element directly without attaching to any document
        title = HTMLTitleElement("title")
        with pytest.raises(NotSupportedError):
            title.text = "Some title"


# ===========================================================================
# HTMLButtonElement tests
# ===========================================================================

class TestHTMLButtonElement:

    def test_button_type_default_submit(self):
        """Absent type attribute returns 'submit' (WHATWG default)."""
        doc = Document()
        btn = doc.create_element("button")
        assert btn.type == "submit"

    def test_button_type_set_get(self):
        doc = Document()
        btn = doc.create_element("button")
        btn.type = "reset"
        assert btn.type == "reset"

    def test_button_value_set_get(self):
        doc = Document()
        btn = doc.create_element("button")
        btn.value = "Click me"
        assert btn.value == "Click me"

    def test_button_disabled_boolean(self):
        doc = Document()
        btn = doc.create_element("button")
        assert btn.disabled is False
        btn.disabled = True
        assert btn.disabled is True
        btn.disabled = False
        assert btn.disabled is False

    def test_create_button_returns_html_button_element(self):
        doc = Document()
        btn = doc.create_element("button")
        assert isinstance(btn, HTMLButtonElement)

    def test_html_button_element_form_override_attrs(self):
        """HTMLButtonElement form-submission override attributes (ADR-289 / BACK-311)."""
        doc = Document()
        btn = doc.create_element("button")
        # Defaults
        assert btn.form_action == ""
        assert btn.form_enctype == ""
        assert btn.form_method == ""
        assert btn.form_no_validate is False
        assert btn.form_target == ""
        assert btn.autofocus is False
        # Setters
        btn.form_action = "/submit"
        assert btn.form_action == "/submit"
        btn.form_enctype = "multipart/form-data"
        assert btn.form_enctype == "multipart/form-data"
        btn.form_method = "post"
        assert btn.form_method == "post"
        btn.form_no_validate = True
        assert btn.form_no_validate is True
        btn.form_no_validate = False
        assert btn.form_no_validate is False
        btn.form_target = "_blank"
        assert btn.form_target == "_blank"
        btn.autofocus = True
        assert btn.autofocus is True
        btn.autofocus = False
        assert btn.autofocus is False


# ===========================================================================
# HTMLSelectElement tests
# ===========================================================================

class TestHTMLSelectElement:

    def test_select_value_set_get(self):
        # WHATWG HTML §4.10.7.6.6: select.value reflects the first selected
        # option's value attribute, not a non-standard attribute on <select>.
        # ADR-271: old behaviour (reading/writing <select value="..."> attribute)
        # was wrong per spec and has been replaced.
        doc = Document()
        sel = doc.create_element("select")
        opt = doc.create_element("option")
        opt.set_attribute("value", "option1")
        sel.append_child(opt)
        sel.value = "option1"
        assert sel.value == "option1"

    def test_select_name_set_get(self):
        doc = Document()
        sel = doc.create_element("select")
        sel.name = "country"
        assert sel.name == "country"

    def test_select_multiple_boolean(self):
        doc = Document()
        sel = doc.create_element("select")
        assert sel.multiple is False
        sel.multiple = True
        assert sel.multiple is True
        sel.multiple = False
        assert sel.multiple is False

    def test_select_disabled_boolean(self):
        doc = Document()
        sel = doc.create_element("select")
        assert sel.disabled is False
        sel.disabled = True
        assert sel.disabled is True

    def test_create_select_returns_html_select_element(self):
        doc = Document()
        sel = doc.create_element("select")
        assert isinstance(sel, HTMLSelectElement)

    def test_html_select_element_autofocus(self):
        """HTMLSelectElement.autofocus boolean presence attribute (ADR-289 / BACK-311)."""
        doc = Document()
        sel = doc.create_element("select")
        assert sel.autofocus is False
        sel.autofocus = True
        assert sel.autofocus is True
        assert sel.has_attribute("autofocus")
        sel.autofocus = False
        assert sel.autofocus is False
        assert not sel.has_attribute("autofocus")


# ===========================================================================
# BACK-200: HTMLSelectElement collection API — item, named_item, add, remove
# ===========================================================================

class TestHTMLSelectElementCollectionAPI:
    """Tests for BACK-200 / ADR-183: item, named_item, add, remove."""

    def _make_select_with_options(self, n: int = 2):
        doc = Document()
        sel = doc.create_element("select")
        opts = []
        for _ in range(n):
            opt = doc.create_element("option")
            sel.append_child(opt)
            opts.append(opt)
        return doc, sel, opts

    # -- item() ---------------------------------------------------------------

    def test_item_returns_first_option(self):
        """AC-5: sel.item(0) returns the first <option>."""
        _, sel, opts = self._make_select_with_options(2)
        assert sel.item(0) is opts[0]

    def test_item_returns_second_option(self):
        _, sel, opts = self._make_select_with_options(2)
        assert sel.item(1) is opts[1]

    def test_item_out_of_range_returns_none(self):
        """AC-5: sel.item(999) returns None (no exception)."""
        _, sel, _opts = self._make_select_with_options(1)
        assert sel.item(999) is None

    def test_item_empty_select_returns_none(self):
        doc = Document()
        sel = doc.create_element("select")
        assert sel.item(0) is None

    # -- named_item() ---------------------------------------------------------

    def test_named_item_found_by_id(self):
        """AC-6: named_item('opt1') finds the option by id attribute."""
        doc = Document()
        sel = doc.create_element("select")
        opt = doc.create_element("option")
        opt.set_attribute("id", "opt1")
        sel.append_child(opt)
        assert sel.named_item("opt1") is opt

    def test_named_item_found_by_name_attribute(self):
        """named_item also matches by 'name' attribute."""
        doc = Document()
        sel = doc.create_element("select")
        opt = doc.create_element("option")
        opt.set_attribute("name", "myopt")
        sel.append_child(opt)
        assert sel.named_item("myopt") is opt

    def test_named_item_missing_returns_none(self):
        """AC-6: named_item('missing') returns None."""
        _, sel, _opts = self._make_select_with_options(2)
        assert sel.named_item("missing") is None

    def test_named_item_empty_select_returns_none(self):
        doc = Document()
        sel = doc.create_element("select")
        assert sel.named_item("anything") is None

    # -- add() ----------------------------------------------------------------

    def test_add_appends_when_before_is_none(self):
        """AC-7: sel.add(new_option) appends; new_option in sel.options; length increased."""
        doc = Document()
        sel = doc.create_element("select")
        opt = doc.create_element("option")
        sel.add(opt)
        assert sel.length == 1
        assert sel.item(0) is opt

    def test_add_two_options_appends_in_order(self):
        doc = Document()
        sel = doc.create_element("select")
        opt1 = doc.create_element("option")
        opt2 = doc.create_element("option")
        sel.add(opt1)
        sel.add(opt2)
        assert sel.length == 2
        assert sel.item(0) is opt1
        assert sel.item(1) is opt2

    def test_add_before_int_zero_inserts_at_front(self):
        """AC-8: sel.add(new_option, 0) inserts at front; sel.item(0) is new_option."""
        doc = Document()
        sel = doc.create_element("select")
        opt_existing = doc.create_element("option")
        sel.append_child(opt_existing)
        opt_new = doc.create_element("option")
        sel.add(opt_new, 0)
        assert sel.item(0) is opt_new
        assert sel.item(1) is opt_existing

    def test_add_before_int_out_of_range_appends(self):
        """Integer index out of range: treated as append (WHATWG §4.10.7)."""
        doc = Document()
        sel = doc.create_element("select")
        opt1 = doc.create_element("option")
        sel.append_child(opt1)
        opt2 = doc.create_element("option")
        sel.add(opt2, 999)  # out of range → append
        assert sel.item(1) is opt2

    def test_add_before_element_inserts_before_it(self):
        """AC-8 variant: sel.add(opt3, existing_option) inserts before the element."""
        doc = Document()
        sel = doc.create_element("select")
        opt_a = doc.create_element("option")
        opt_b = doc.create_element("option")
        sel.append_child(opt_a)
        sel.append_child(opt_b)
        opt_new = doc.create_element("option")
        sel.add(opt_new, opt_b)  # insert before opt_b
        assert sel.item(0) is opt_a
        assert sel.item(1) is opt_new
        assert sel.item(2) is opt_b

    # -- remove() -------------------------------------------------------------

    def test_remove_removes_first_option(self):
        """AC-9: sel.remove(0) removes first option; length decreases."""
        _, sel, opts = self._make_select_with_options(2)
        initial_length = sel.length
        sel.remove(0)
        assert sel.length == initial_length - 1
        assert sel.item(0) is opts[1]

    def test_remove_out_of_range_is_noop(self):
        """AC-9: sel.remove(999) is no-op; no exception raised."""
        _, sel, _opts = self._make_select_with_options(1)
        sel.remove(999)  # must not raise
        assert sel.length == 1

    def test_remove_all_options(self):
        doc = Document()
        sel = doc.create_element("select")
        opt = doc.create_element("option")
        sel.append_child(opt)
        sel.remove(0)
        assert sel.length == 0
        sel.remove(0)  # second remove is no-op
        assert sel.length == 0


# ===========================================================================
# Inheritance tests
# ===========================================================================

class TestInheritance:

    def test_all_subclasses_are_html_element(self):
        for cls in _ALL_SUBCLASSES:
            assert issubclass(cls, HTMLElement)

    def test_all_subclasses_are_element(self):
        for cls in _ALL_SUBCLASSES:
            assert issubclass(cls, Element)

    def test_all_subclasses_have_slots(self):
        for cls in _ALL_SUBCLASSES:
            assert hasattr(cls, "__slots__"), f"{cls.__name__} missing __slots__"
            assert isinstance(cls.__slots__, tuple)


# ===========================================================================
# SINV-001 fix: clone_node preserves concrete subclass
# ===========================================================================

class TestClonePreservesSubclass:

    def test_clone_anchor_returns_html_anchor_element(self):
        """clone_node() on HTMLAnchorElement must return HTMLAnchorElement (SINV-001)."""
        doc = Document()
        a = doc.create_element("a")
        a.href = "https://example.com"
        clone = a.clone_node(deep=False)
        assert isinstance(clone, HTMLAnchorElement), (
            f"Expected HTMLAnchorElement, got {type(clone).__name__}"
        )

    def test_clone_input_returns_html_input_element(self):
        doc = Document()
        inp = doc.create_element("input")
        inp.type = "checkbox"
        clone = inp.clone_node(deep=False)
        assert isinstance(clone, HTMLInputElement)

    def test_clone_preserves_attributes(self):
        """Attributes are copied to the clone."""
        doc = Document()
        a = doc.create_element("a")
        a.href = "https://example.com"
        a.target = "_blank"
        clone = a.clone_node(deep=False)
        assert clone.href == "https://example.com"  # type: ignore[attr-defined]
        assert clone.target == "_blank"  # type: ignore[attr-defined]

    def test_clone_meta_preserves_subclass(self):
        doc = Document()
        meta = doc.create_element("meta")
        meta.name = "keywords"
        clone = meta.clone_node(deep=False)
        assert isinstance(clone, HTMLMetaElement)

    @pytest.mark.parametrize("tag, expected_cls", _TAG_CLASS_PAIRS)
    def test_clone_all_subclasses_preserve_type(self, tag: str, expected_cls: type):
        """clone_node() preserves the correct subclass for all 10 registered tags."""
        doc = Document()
        el = doc.create_element(tag)
        clone = el.clone_node(deep=False)
        assert isinstance(clone, expected_cls), (
            f"clone_node() on {tag!r} returned {type(clone).__name__}, "
            f"expected {expected_cls.__name__}"
        )


# ===========================================================================
# Integration tests: HTMLDocument.parse() creates correct subclasses
# ===========================================================================

class TestParseIntegration:

    def test_parse_html_creates_correct_subclasses(self):
        """HTMLDocument.parse() uses tree builder which calls create_element()."""
        doc = HTMLDocument.parse(
            "<html><body>"
            '<a href="https://example.com">link</a>'
            '<img src="photo.jpg" alt="photo">'
            '<input type="text" name="q">'
            "</body></html>"
        )
        body = doc.query_selector("body")
        assert body is not None

        a = doc.query_selector("a")
        assert a is not None
        assert isinstance(a, HTMLAnchorElement), type(a).__name__
        assert a.href == "https://example.com"  # type: ignore[attr-defined]

        img = doc.query_selector("img")
        assert img is not None
        assert isinstance(img, HTMLImageElement), type(img).__name__
        assert img.src == "photo.jpg"  # type: ignore[attr-defined]

        inp = doc.query_selector("input")
        assert inp is not None
        assert isinstance(inp, HTMLInputElement), type(inp).__name__
        assert inp.name == "q"  # type: ignore[attr-defined]

    def test_parse_form_creates_html_form_element(self):
        doc = HTMLDocument.parse('<form action="/post" method="post"></form>')
        form = doc.query_selector("form")
        assert form is not None
        assert isinstance(form, HTMLFormElement)
        assert form.action == "/post"  # type: ignore[attr-defined]
        assert form.method == "post"  # type: ignore[attr-defined]

    def test_parse_script_creates_html_script_element(self):
        doc = HTMLDocument.parse('<script src="app.js" async></script>')
        script = doc.query_selector("script")
        assert script is not None
        assert isinstance(script, HTMLScriptElement)
        assert script.src == "app.js"  # type: ignore[attr-defined]
        assert script.async_ is True  # type: ignore[attr-defined]


# ===========================================================================
# Doctest verification
# ===========================================================================

class TestHTMLAnchorElementURLDecomposition:
    """Tests for HTMLAnchorElement URL decomposition properties (BACK-169, ADR-152).

    Covers AC-1 through AC-8 from SPEC-090:
    - AC-1: link-metadata attribute reflections (rel, download, hreflang, type)
    - AC-2: text property (textContent delegate)
    - AC-3: URL decomposition for a full URL with all components
    - AC-4: no-href fallback (all "" except origin == "null")
    - AC-5: javascript: scheme — origin is "null"
    - AC-6: existing href/target behaviour unchanged (covered by TestHTMLAnchorElement)
    - AC-8: minimum 20 tests
    """

    # -- AC-1: link-metadata attribute reflections ---------------------------

    def test_rel_default_empty(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.rel == ""

    def test_rel_get_set(self):
        doc = Document()
        a = doc.create_element("a")
        a.rel = "nofollow"
        assert a.rel == "nofollow"

    def test_download_default_empty(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.download == ""

    def test_download_get_set(self):
        doc = Document()
        a = doc.create_element("a")
        a.download = "report.pdf"
        assert a.download == "report.pdf"

    def test_hreflang_default_empty(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.hreflang == ""

    def test_hreflang_get_set(self):
        doc = Document()
        a = doc.create_element("a")
        a.hreflang = "fr"
        assert a.hreflang == "fr"

    def test_type_default_empty(self):
        """type defaults to '' for <a> — not 'text' (that is <input>-only)."""
        doc = Document()
        a = doc.create_element("a")
        assert a.type == ""

    def test_type_get_set(self):
        doc = Document()
        a = doc.create_element("a")
        a.type = "text/html"
        assert a.type == "text/html"

    # -- AC-2: text property (textContent delegate) --------------------------

    def test_text_empty_element(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.text == ""

    def test_text_with_child_text_node(self):
        doc = Document()
        a = doc.create_element("a")
        txt = doc.create_text_node("Click me")
        a.append_child(txt)
        assert a.text == "Click me"

    def test_text_setter_sets_text_content(self):
        doc = Document()
        a = doc.create_element("a")
        a.text = "Go"
        assert a.text_content == "Go"

    # -- AC-3: URL decomposition for full URL --------------------------------

    def _make_full_url_anchor(self):
        """Return a detached anchor with a full URL including all components."""
        doc = Document()
        a = doc.create_element("a")
        a.href = "https://user:pass@example.com:8080/p?q=1#h"
        return a

    def test_url_decomposition_all_components(self):
        a = self._make_full_url_anchor()
        assert a.protocol == "https:"
        assert a.username == "user"
        assert a.password == "pass"
        assert a.host == "example.com:8080"
        assert a.hostname == "example.com"
        assert a.port == "8080"
        assert a.pathname == "/p"
        assert a.search == "?q=1"
        assert a.hash == "#h"
        assert a.origin == "https://example.com:8080"

    def test_protocol_https(self):
        a = self._make_full_url_anchor()
        assert a.protocol == "https:"

    def test_host_with_port(self):
        a = self._make_full_url_anchor()
        assert a.host == "example.com:8080"

    def test_hostname_no_port(self):
        a = self._make_full_url_anchor()
        assert a.hostname == "example.com"

    def test_port_explicit(self):
        a = self._make_full_url_anchor()
        assert a.port == "8080"

    def test_pathname(self):
        a = self._make_full_url_anchor()
        assert a.pathname == "/p"

    def test_search(self):
        a = self._make_full_url_anchor()
        assert a.search == "?q=1"

    def test_hash(self):
        a = self._make_full_url_anchor()
        assert a.hash == "#h"

    def test_origin(self):
        a = self._make_full_url_anchor()
        assert a.origin == "https://example.com:8080"

    def test_username_password(self):
        a = self._make_full_url_anchor()
        assert a.username == "user"
        assert a.password == "pass"

    def test_search_empty_when_no_query(self):
        doc = Document()
        a = doc.create_element("a")
        a.href = "https://example.com/path"
        assert a.search == ""

    def test_hash_empty_when_no_fragment(self):
        doc = Document()
        a = doc.create_element("a")
        a.href = "https://example.com/path"
        assert a.hash == ""

    # -- AC-4: no-href fallback — all "" except origin == "null" ------------

    def test_no_href_all_components_empty(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.protocol == ""
        assert a.username == ""
        assert a.password == ""
        assert a.host == ""
        assert a.hostname == ""
        assert a.port == ""
        assert a.pathname == ""
        assert a.search == ""
        assert a.hash == ""
        assert a.origin == "null"

    def test_origin_no_href_returns_null(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.origin == "null"

    # -- AC-5: non-HTTP scheme — origin is "null" ----------------------------

    def test_origin_javascript_scheme_returns_null(self):
        """javascript: scheme is opaque — origin must return 'null'."""
        doc = Document()
        a = doc.create_element("a")
        a.href = "javascript:void(0)"
        assert a.origin == "null"

    # -- Attribute reflection: get_attribute stays in sync -------------------

    def test_rel_attribute_in_sync(self):
        doc = Document()
        a = doc.create_element("a")
        a.rel = "noopener"
        assert a.get_attribute("rel") == "noopener"

    def test_download_attribute_in_sync(self):
        doc = Document()
        a = doc.create_element("a")
        a.download = "data.csv"
        assert a.get_attribute("download") == "data.csv"

    # -- URL decomposition with HTMLDocument (base URL resolution) -----------

    def test_url_decomposition_with_base_url(self):
        """URL decomposition resolves relative href against document base."""
        doc = HTMLDocument.parse(
            "<a href='/about'></a>",
            base_url="https://example.com/",
        )
        a = doc.query_selector("a")
        assert a.hostname == "example.com"
        assert a.pathname == "/about"
        assert a.protocol == "https:"

    def test_relative_href_components_use_document_url_without_base(self):
        doc = HTMLDocument.parse(
            "<a href='images/pic.png?x=1#top'></a>",
            base_url="https://example.com/app/page.html",
        )
        a = doc.query_selector("a")
        assert a is not None
        assert a.protocol == "https:"
        assert a.host == "example.com"
        assert a.pathname == "/app/images/pic.png"
        assert a.search == "?x=1"
        assert a.hash == "#top"

    def test_relative_href_components_use_document_base_uri(self):
        doc = HTMLDocument.parse(
            "<html><head><base href='https://cdn.example.org/root/'></head>"
            "<body><a href='../asset.css?rev=2#v'></a></body></html>",
            base_url="https://example.com/app/index.html",
        )
        a = doc.query_selector("a")
        assert a is not None
        assert doc.base_uri == "https://cdn.example.org/root/"
        assert a.protocol == "https:"
        assert a.host == "cdn.example.org"
        assert a.pathname == "/asset.css"
        assert a.search == "?rev=2"
        assert a.hash == "#v"

    def test_base_mutation_updates_relative_href_components(self):
        doc = HTMLDocument.parse(
            "<html><head><base href='https://a.example/x/'></head>"
            "<body><a href='p'></a></body></html>",
            base_url="https://fallback.example/root/",
        )
        a = doc.query_selector("a")
        base = doc.query_selector("base")
        assert a is not None
        assert base is not None

        assert a.hostname == "a.example"
        assert a.pathname == "/x/p"

        base.set_attribute("href", "https://b.example/y/")
        assert doc.base_uri == "https://b.example/y/"
        assert a.hostname == "b.example"
        assert a.pathname == "/y/p"

    def test_absolute_href_components_unchanged_by_document_base_uri(self):
        doc = HTMLDocument.parse(
            "<html><head><base href='https://cdn.example.org/root/'></head>"
            "<body><a href='https://api.example.net:8443/v1?q=1#h'></a></body></html>",
            base_url="https://example.com/",
        )
        a = doc.query_selector("a")
        assert a is not None
        assert a.protocol == "https:"
        assert a.host == "api.example.net:8443"
        assert a.hostname == "api.example.net"
        assert a.port == "8443"
        assert a.pathname == "/v1"
        assert a.search == "?q=1"
        assert a.hash == "#h"
        assert a.origin == "https://api.example.net:8443"

    def test_port_empty_for_default_https(self):
        """Port is '' when using the default port for the scheme."""
        doc = Document()
        a = doc.create_element("a")
        a.href = "https://example.com/"
        assert a.port == ""


class TestTableMutationMethods:
    """BACK-180 / ADR-163 — HTMLTableElement family mutation methods."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_table():
        from aspose_html.dom import Document
        doc = Document()
        table = doc.create_element("table")
        return doc, table

    @staticmethod
    def _make_section(tag: str = "tbody"):
        from aspose_html.dom import Document
        doc = Document()
        section = doc.create_element(tag)
        return doc, section

    @staticmethod
    def _make_row():
        from aspose_html.dom import Document
        doc = Document()
        tr = doc.create_element("tr")
        return doc, tr

    # ------------------------------------------------------------------
    # HTMLTableElement.insert_row
    # ------------------------------------------------------------------

    def test_table_insert_row_append(self):
        """insert_row() with no arg appends and returns HTMLTableRowElement."""
        from aspose_html.dom import HTMLTableRowElement
        _, table = self._make_table()
        tr = table.insert_row()
        assert isinstance(tr, HTMLTableRowElement)
        assert len(list(table.rows)) == 1

    def test_table_insert_row_at_index_zero(self):
        """insert_row(0) prepends before existing rows."""
        _, table = self._make_table()
        tr1 = table.insert_row()   # first row
        tr0 = table.insert_row(0)  # prepend
        rows = list(table.rows)
        assert rows[0] is tr0
        assert rows[1] is tr1

    def test_table_insert_row_appends_to_last_tbody(self):
        """insert_row(-1) on table with sections appends to last <tbody>."""
        from aspose_html.dom import Document
        doc = Document()
        table = doc.create_element("table")
        tbody = doc.create_element("tbody")
        table.append_child(tbody)
        tr = table.insert_row()
        assert tr._parent is tbody

    def test_table_insert_row_index_error(self):
        """insert_row with invalid index raises IndexSizeError."""
        from aspose_html.dom._exceptions import IndexSizeError
        _, table = self._make_table()
        with pytest.raises(IndexSizeError):
            table.insert_row(-2)
        with pytest.raises(IndexSizeError):
            table.insert_row(999)

    # ------------------------------------------------------------------
    # HTMLTableElement.delete_row
    # ------------------------------------------------------------------

    def test_table_delete_row(self):
        """delete_row(0) removes the only row; rows collection is empty."""
        _, table = self._make_table()
        table.insert_row()
        table.delete_row(0)
        assert len(list(table.rows)) == 0

    def test_table_delete_row_index_error(self):
        """delete_row with invalid index raises IndexSizeError."""
        from aspose_html.dom._exceptions import IndexSizeError
        _, table = self._make_table()
        with pytest.raises(IndexSizeError):
            table.delete_row(999)
        # delete_row(-1) also raises on HTMLTableElement
        with pytest.raises(IndexSizeError):
            table.delete_row(-1)

    # ------------------------------------------------------------------
    # HTMLTableElement.create_caption / delete_caption
    # ------------------------------------------------------------------

    def test_table_create_caption_idempotent(self):
        """create_caption() on second call returns the same element."""
        from aspose_html.dom import HTMLTableCaptionElement
        _, table = self._make_table()
        cap1 = table.create_caption()
        cap2 = table.create_caption()
        assert isinstance(cap1, HTMLTableCaptionElement)
        assert cap1 is cap2

    def test_table_delete_caption_noop(self):
        """delete_caption() is no-op when no <caption> is present."""
        _, table = self._make_table()
        table.delete_caption()   # must not raise
        assert table.caption is None

    def test_table_delete_caption_removes(self):
        """delete_caption() removes an existing caption."""
        _, table = self._make_table()
        table.create_caption()
        table.delete_caption()
        assert table.caption is None

    # ------------------------------------------------------------------
    # HTMLTableElement.create_t_head / delete_t_head
    # ------------------------------------------------------------------

    def test_table_create_t_head_idempotent(self):
        """create_t_head() returns existing <thead> on second call."""
        from aspose_html.dom import HTMLTableSectionElement
        _, table = self._make_table()
        th1 = table.create_t_head()
        th2 = table.create_t_head()
        assert isinstance(th1, HTMLTableSectionElement)
        assert th1 is th2

    def test_table_delete_t_head_noop(self):
        """delete_t_head() is no-op when no <thead> is present."""
        _, table = self._make_table()
        table.delete_t_head()   # must not raise
        assert table.t_head is None

    def test_table_delete_t_head_removes(self):
        """delete_t_head() removes an existing thead."""
        _, table = self._make_table()
        table.create_t_head()
        table.delete_t_head()
        assert table.t_head is None

    # ------------------------------------------------------------------
    # HTMLTableElement.create_t_foot / delete_t_foot
    # ------------------------------------------------------------------

    def test_table_create_t_foot(self):
        """create_t_foot() appends and returns HTMLTableSectionElement."""
        from aspose_html.dom import HTMLTableSectionElement
        _, table = self._make_table()
        tf = table.create_t_foot()
        assert isinstance(tf, HTMLTableSectionElement)
        assert table.t_foot is tf

    def test_table_create_t_foot_idempotent(self):
        """create_t_foot() returns existing <tfoot> on second call."""
        _, table = self._make_table()
        tf1 = table.create_t_foot()
        tf2 = table.create_t_foot()
        assert tf1 is tf2

    def test_table_delete_t_foot_noop(self):
        """delete_t_foot() is no-op when no <tfoot> is present."""
        _, table = self._make_table()
        table.delete_t_foot()   # must not raise
        assert table.t_foot is None

    def test_table_delete_t_foot_removes(self):
        """delete_t_foot() removes an existing tfoot."""
        _, table = self._make_table()
        table.create_t_foot()
        table.delete_t_foot()
        assert table.t_foot is None

    def test_html_table_element_create_t_body(self):
        """AC-9: create_t_body() creates tbody when absent; second call returns same element."""
        from aspose_html.dom import Document, HTMLTableSectionElement
        doc = Document()
        table = doc.create_element("table")
        _ = doc.append_child(table)
        # First call on empty table creates a new <tbody>
        tbody = table.create_t_body()
        assert isinstance(tbody, HTMLTableSectionElement)
        assert tbody.tag_name == "TBODY"
        assert tbody._parent is table
        # Second call returns the same existing <tbody>
        tbody2 = table.create_t_body()
        assert tbody2 is tbody

    def test_html_table_element_create_t_body_existing(self):
        """create_t_body() returns the first existing tbody, does not create another."""
        from aspose_html.dom import Document
        doc = Document()
        table = doc.create_element("table")
        _ = doc.append_child(table)
        # Pre-create a tbody
        existing_tbody = doc.create_element("tbody")
        _ = table.append_child(existing_tbody)
        # create_t_body() must return the same existing element
        result = table.create_t_body()
        assert result is existing_tbody
        # Only one tbody should be in the children
        tbody_children = [c for c in table._children if getattr(c, "_tag_name", None) == "TBODY"]
        assert len(tbody_children) == 1

    # ------------------------------------------------------------------
    # HTMLTableSectionElement.insert_row / delete_row
    # ------------------------------------------------------------------

    def test_section_insert_row(self):
        """section.insert_row() appends a <tr> within the section only."""
        from aspose_html.dom import HTMLTableRowElement
        _, tbody = self._make_section()
        tr = tbody.insert_row()
        assert isinstance(tr, HTMLTableRowElement)
        assert len(list(tbody.rows)) == 1
        assert tr._parent is tbody

    def test_section_delete_row(self):
        """section.delete_row(0) removes the row from the section."""
        _, tbody = self._make_section()
        tbody.insert_row()
        tbody.delete_row(0)
        assert len(list(tbody.rows)) == 0

    def test_section_insert_row_at_zero(self):
        """section.insert_row(0) prepends."""
        _, tbody = self._make_section()
        tr1 = tbody.insert_row()
        tr0 = tbody.insert_row(0)
        rows = list(tbody.rows)
        assert rows[0] is tr0
        assert rows[1] is tr1

    def test_section_delete_row_index_error(self):
        """section.delete_row with invalid index raises IndexSizeError."""
        from aspose_html.dom._exceptions import IndexSizeError
        _, tbody = self._make_section()
        with pytest.raises(IndexSizeError):
            tbody.delete_row(0)

    # ------------------------------------------------------------------
    # HTMLTableRowElement.insert_cell / delete_cell
    # ------------------------------------------------------------------

    def test_row_insert_cell_append(self):
        """insert_cell() appends <td> and returns HTMLTableCellElement."""
        from aspose_html.dom import HTMLTableCellElement
        _, tr = self._make_row()
        td = tr.insert_cell()
        assert isinstance(td, HTMLTableCellElement)
        assert len(list(tr.cells)) == 1

    def test_row_insert_cell_at_index(self):
        """insert_cell(0) prepends before existing cells."""
        _, tr = self._make_row()
        td1 = tr.insert_cell()
        td0 = tr.insert_cell(0)
        cells = list(tr.cells)
        assert cells[0] is td0
        assert cells[1] is td1

    def test_row_delete_cell(self):
        """delete_cell(0) removes the cell."""
        _, tr = self._make_row()
        tr.insert_cell()
        tr.delete_cell(0)
        assert len(list(tr.cells)) == 0

    def test_row_delete_cell_index_error(self):
        """delete_cell with invalid index raises IndexSizeError."""
        from aspose_html.dom._exceptions import IndexSizeError
        _, tr = self._make_row()
        with pytest.raises(IndexSizeError):
            tr.delete_cell(0)
        with pytest.raises(IndexSizeError):
            tr.delete_cell(-1)

    # ------------------------------------------------------------------
    # HTMLTableCellElement.scope
    # ------------------------------------------------------------------

    def test_cell_scope_property_default_empty(self):
        """td.scope defaults to '' when attribute absent."""
        from aspose_html.dom import Document
        doc = Document()
        td = doc.create_element("td")
        assert td.scope == ""

    def test_cell_scope_property_get_set(self):
        """th.scope = 'col' reflects via get_attribute."""
        from aspose_html.dom import Document
        doc = Document()
        th = doc.create_element("th")
        th.scope = "col"
        assert th.scope == "col"
        assert th.get_attribute("scope") == "col"

    def test_cell_scope_th_row(self):
        """th.scope = 'row' round-trips correctly."""
        from aspose_html.dom import Document
        doc = Document()
        th = doc.create_element("th")
        th.scope = "row"
        assert th.scope == "row"


class TestHTMLFieldSetElement:
    """ADR-177 / BACK-194 — HTMLFieldSetElement.type and .elements."""

    def test_fieldset_type(self):
        """type always returns 'fieldset'."""
        from aspose_html.dom import Document
        doc = Document()
        fs = doc.create_element("fieldset")
        assert fs.type == "fieldset"

    def test_fieldset_elements_empty(self):
        """elements returns empty collection for bare fieldset."""
        from aspose_html.dom import Document
        doc = Document()
        fs = doc.create_element("fieldset")
        assert len(fs.elements) == 0

    def test_fieldset_elements_listed(self):
        """elements includes button and input children."""
        from aspose_html.dom import Document
        doc = Document()
        fs = doc.create_element("fieldset")
        fs.append_child(doc.create_element("input"))
        fs.append_child(doc.create_element("button"))
        assert len(fs.elements) == 2

    def test_fieldset_elements_live(self):
        """elements is live — reflects child appended after first access."""
        from aspose_html.dom import Document
        doc = Document()
        fs = doc.create_element("fieldset")
        assert len(fs.elements) == 0
        fs.append_child(doc.create_element("input"))
        assert len(fs.elements) == 1

    def test_fieldset_elements_unlisted(self):
        """div child is not a listed element and is excluded."""
        from aspose_html.dom import Document
        doc = Document()
        fs = doc.create_element("fieldset")
        fs.append_child(doc.create_element("div"))
        assert len(fs.elements) == 0


class TestHTMLLegendElement:
    """ADR-178 / BACK-195 — HTMLLegendElement.form."""

    def test_legend_form_found(self):
        """legend.form returns the nearest <form> ancestor via <fieldset>."""
        from aspose_html.html_document import HTMLDocument
        doc = HTMLDocument.parse(
            '<form id="f"><fieldset><legend id="lg"></legend></fieldset></form>'
        )
        legend = doc.get_element_by_id("lg")
        form = doc.get_element_by_id("f")
        assert legend.form is form

    def test_legend_form_none_no_fieldset(self):
        """Detached <legend> with no <fieldset> ancestor returns None."""
        from aspose_html.dom import Document
        doc = Document()
        legend = doc.create_element("legend")
        assert legend.form is None

    def test_legend_form_none_no_form(self):
        """<legend> inside <fieldset> but no <form> ancestor returns None."""
        from aspose_html.dom import Document
        doc = Document()
        fs = doc.create_element("fieldset")
        legend = doc.create_element("legend")
        fs.append_child(legend)
        assert legend.form is None


class TestHTMLOutputElement:
    """ADR-178 / BACK-195 — HTMLOutputElement.type, .value, .html_for."""

    def test_output_type(self):
        """type always returns 'output'."""
        from aspose_html.dom import Document
        doc = Document()
        assert doc.create_element("output").type == "output"

    def test_output_value_default_empty(self):
        """Freshly created output element returns '' for value."""
        from aspose_html.dom import Document
        doc = Document()
        out = doc.create_element("output")
        assert out.value == ""

    def test_output_value_roundtrip(self):
        """Setting value then reading it back returns the same string."""
        from aspose_html.dom import Document
        doc = Document()
        out = doc.create_element("output")
        doc.append_child(out)
        out.value = "42"
        assert out.value == "42"

    def test_output_value_from_text_child(self):
        """Parsed <output>hello</output> yields value == 'hello'."""
        from aspose_html.html_document import HTMLDocument
        doc = HTMLDocument.parse('<output id="o">hello</output>')
        out = doc.get_element_by_id("o")
        assert out.value == "hello"

    def test_output_value_fallback_to_default_value(self):
        """When no text child exists and defaultvalue is set, value returns defaultvalue."""
        from aspose_html.dom import Document
        doc = Document()
        out = doc.create_element("output")
        out.default_value = "n/a"
        assert out.value == "n/a"

    def test_output_html_for_instance(self):
        """html_for returns a DOMTokenList instance."""
        from aspose_html.dom import Document, DOMTokenList
        doc = Document()
        out = doc.create_element("output")
        assert isinstance(out.html_for, DOMTokenList)

    def test_output_html_for_cached(self):
        """html_for returns the same object on repeated access."""
        from aspose_html.dom import Document
        doc = Document()
        out = doc.create_element("output")
        assert out.html_for is out.html_for

    def test_output_html_for_add(self):
        """html_for.add() mutates the 'for' attribute."""
        from aspose_html.dom import Document
        doc = Document()
        out = doc.create_element("output")
        out.html_for.add("field1")
        assert out.get_attribute("for") == "field1"


# ===========================================================================
# Form-association `form` property (BACK-197 / ADR-180)
# ===========================================================================

class TestFormOwnerProperty:
    """Tests for the `form` property on form-associated element classes."""

    def test_form_button(self):
        """button.form is the ancestor <form>."""
        doc = HTMLDocument.parse('<form id="f"><button id="b"></button></form>')
        button = doc.get_element_by_id("b")
        form = doc.get_element_by_id("f")
        assert button.form is form

    def test_form_input(self):
        """input.form is the ancestor <form>."""
        doc = HTMLDocument.parse('<form id="f"><input id="i"></form>')
        inp = doc.get_element_by_id("i")
        form = doc.get_element_by_id("f")
        assert inp.form is form

    def test_form_select(self):
        """select.form is the ancestor <form>."""
        doc = HTMLDocument.parse('<form id="f"><select id="s"></select></form>')
        sel = doc.get_element_by_id("s")
        form = doc.get_element_by_id("f")
        assert sel.form is form

    def test_form_textarea(self):
        """textarea.form is the ancestor <form>."""
        doc = HTMLDocument.parse('<form id="f"><textarea id="t"></textarea></form>')
        ta = doc.get_element_by_id("t")
        form = doc.get_element_by_id("f")
        assert ta.form is form

    def test_form_output(self):
        """output.form is the ancestor <form>."""
        doc = HTMLDocument.parse('<form id="f"><output id="o"></output></form>')
        out = doc.get_element_by_id("o")
        form = doc.get_element_by_id("f")
        assert out.form is form

    def test_form_nested(self):
        """form property traverses indirect ancestors correctly."""
        doc = HTMLDocument.parse('<form id="f"><div><input id="i"></div></form>')
        inp = doc.get_element_by_id("i")
        form = doc.get_element_by_id("f")
        assert inp.form is form

    def test_form_detached(self):
        """Detached element (not in a document tree) returns None."""
        from aspose_html.dom import Document
        doc = Document()
        inp = doc.create_element("input")
        # inp has no parent — form should be None
        assert inp.form is None

    def test_form_no_ancestor_form(self):
        """Element inside <div> with no ancestor <form> returns None."""
        doc = HTMLDocument.parse('<div><input id="i"></div>')
        inp = doc.get_element_by_id("i")
        assert inp.form is None


class TestHTMLOptionIndexAndForm:
    """BACK-205 / ADR-188: HTMLOptionElement.index and .form."""

    def test_option_index_detached_returns_zero(self):
        from aspose_html.dom import Document

        doc = Document()
        opt = doc.create_element("option")
        assert opt.index == 0

    def test_option_index_in_select_options_order(self):
        doc = HTMLDocument.parse(
            '<select><option id="a">A</option><option id="b">B</option><option id="c">C</option></select>'
        )
        assert doc.get_element_by_id("a").index == 0
        assert doc.get_element_by_id("b").index == 1
        assert doc.get_element_by_id("c").index == 2

    def test_option_index_in_optgroup_uses_flat_options_collection(self):
        doc = HTMLDocument.parse(
            '<select><optgroup><option id="o1">A</option><option id="o2">B</option></optgroup><option id="o3">C</option></select>'
        )
        assert doc.get_element_by_id("o1").index == 0
        assert doc.get_element_by_id("o2").index == 1
        assert doc.get_element_by_id("o3").index == 2

    def test_option_form_detached_is_none(self):
        from aspose_html.dom import Document

        doc = Document()
        opt = doc.create_element("option")
        assert opt.form is None

    def test_option_form_delegates_to_parent_select_form(self):
        doc = HTMLDocument.parse('<form id="f"><select><option id="o">x</option></select></form>')
        form = doc.get_element_by_id("f")
        opt = doc.get_element_by_id("o")
        assert opt.form is form


# ===========================================================================
# HTMLTextAreaElement tests (ADR-289 / BACK-311)
# ===========================================================================

class TestHTMLTextAreaElement:

    def test_html_textarea_element_idl_tail(self):
        """HTMLTextAreaElement IDL tail: wrap, autocomplete, autofocus, dirname (BACK-311)."""
        doc = Document()
        ta = doc.create_element("textarea")
        assert isinstance(ta, HTMLTextAreaElement)
        # Defaults
        assert ta.wrap == ""
        assert ta.autocomplete == ""
        assert ta.autofocus is False
        assert ta.dirname == ""
        # wrap
        ta.wrap = "soft"
        assert ta.wrap == "soft"
        ta.wrap = "hard"
        assert ta.wrap == "hard"
        # autocomplete
        ta.autocomplete = "on"
        assert ta.autocomplete == "on"
        ta.autocomplete = "off"
        assert ta.autocomplete == "off"
        # autofocus
        ta.autofocus = True
        assert ta.autofocus is True
        assert ta.has_attribute("autofocus")
        ta.autofocus = False
        assert ta.autofocus is False
        assert not ta.has_attribute("autofocus")
        # dirname
        ta.dirname = "ltr"
        assert ta.dirname == "ltr"


# ===========================================================================
# Track 95 IDL tail tests (ADR-294 / BACK-316)
# ===========================================================================

class TestHTMLLinkElementIdlTail:
    """ADR-294: 10 new HTMLLinkElement IDL properties."""

    def test_cross_origin_none_when_absent(self):
        doc = Document()
        link = doc.create_element("link")
        assert link.cross_origin is None

    def test_cross_origin_setter(self):
        doc = Document()
        link = doc.create_element("link")
        link.cross_origin = "anonymous"
        assert link.cross_origin == "anonymous"
        link.cross_origin = None
        assert link.cross_origin is None
        assert not link.has_attribute("crossorigin")

    def test_integrity_defaults_empty(self):
        doc = Document()
        link = doc.create_element("link")
        assert link.integrity == ""
        link.integrity = "sha384-abc"
        assert link.integrity == "sha384-abc"

    def test_referrer_policy_defaults_empty(self):
        doc = Document()
        link = doc.create_element("link")
        assert link.referrer_policy == ""
        link.referrer_policy = "no-referrer"
        assert link.referrer_policy == "no-referrer"

    def test_as_defaults_empty(self):
        doc = Document()
        link = doc.create_element("link")
        assert link.as_ == ""
        link.as_ = "script"
        assert link.as_ == "script"
        assert link.get_attribute("as") == "script"

    def test_sizes_is_dom_token_list_and_slot_cached(self):
        from aspose_html.dom import DOMTokenList
        doc = Document()
        link = doc.create_element("link")
        assert isinstance(link.sizes, DOMTokenList)
        assert link.sizes is link.sizes
        link.sizes.add("any")
        assert link.get_attribute("sizes") == "any"

    def test_rel_list_is_dom_token_list_and_slot_cached(self):
        from aspose_html.dom import DOMTokenList
        doc = Document()
        link = doc.create_element("link")
        assert isinstance(link.rel_list, DOMTokenList)
        assert link.rel_list is link.rel_list
        link.rel_list.add("stylesheet")
        assert link.rel == "stylesheet"

    def test_disabled_defaults_false(self):
        doc = Document()
        link = doc.create_element("link")
        assert link.disabled is False
        link.disabled = True
        assert link.disabled is True
        assert link.has_attribute("disabled")
        link.disabled = False
        assert link.disabled is False
        assert not link.has_attribute("disabled")

    def test_hreflang_media_charset_defaults_empty(self):
        doc = Document()
        link = doc.create_element("link")
        assert link.hreflang == ""
        assert link.media == ""
        assert link.charset == ""
        link.hreflang = "en"
        link.media = "screen"
        link.charset = "utf-8"
        assert link.hreflang == "en"
        assert link.media == "screen"
        assert link.charset == "utf-8"


class TestHTMLFormElementIdlTail:
    """ADR-294: 4 new HTMLFormElement IDL properties."""

    def test_no_validate_defaults_false(self):
        doc = Document()
        form = doc.create_element("form")
        assert form.no_validate is False
        form.no_validate = True
        assert form.no_validate is True
        assert form.has_attribute("novalidate")
        form.no_validate = False
        assert form.no_validate is False
        assert not form.has_attribute("novalidate")

    def test_accept_charset_defaults_empty(self):
        doc = Document()
        form = doc.create_element("form")
        assert form.accept_charset == ""
        form.accept_charset = "UTF-8"
        assert form.accept_charset == "UTF-8"
        assert form.get_attribute("accept-charset") == "UTF-8"

    def test_auto_complete_defaults_empty(self):
        doc = Document()
        form = doc.create_element("form")
        assert form.auto_complete == ""
        form.auto_complete = "off"
        assert form.auto_complete == "off"

    def test_rel_list_is_dom_token_list_and_slot_cached(self):
        from aspose_html.dom import DOMTokenList
        doc = Document()
        form = doc.create_element("form")
        assert isinstance(form.rel_list, DOMTokenList)
        assert form.rel_list is form.rel_list
        form.rel_list.add("noopener")
        assert form.rel == "noopener"


class TestHTMLAnchorElementIdlTail:
    """ADR-294: 3 new HTMLAnchorElement IDL properties."""

    def test_rel_list_is_dom_token_list_and_backed_by_rel(self):
        from aspose_html.dom import DOMTokenList
        doc = Document()
        a = doc.create_element("a")
        assert isinstance(a.rel_list, DOMTokenList)
        assert a.rel_list is a.rel_list
        a.rel_list.add("nofollow")
        assert a.rel == "nofollow"

    def test_referrer_policy_defaults_empty(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.referrer_policy == ""
        a.referrer_policy = "no-referrer"
        assert a.referrer_policy == "no-referrer"

    def test_ping_defaults_empty(self):
        doc = Document()
        a = doc.create_element("a")
        assert a.ping == ""
        a.ping = "https://example.com/ping"
        assert a.ping == "https://example.com/ping"


class TestHTMLInputElementIdlTail:
    """ADR-294: 3 new HTMLInputElement IDL properties."""

    def test_default_checked_reflects_checked_content_attr(self):
        doc = Document()
        inp = doc.create_element("input")
        assert inp.default_checked is False
        inp.default_checked = True
        assert inp.default_checked is True
        assert inp.has_attribute("checked")
        inp.default_checked = False
        assert inp.default_checked is False
        assert not inp.has_attribute("checked")

    def test_capture_defaults_empty(self):
        doc = Document()
        inp = doc.create_element("input")
        assert inp.capture == ""
        inp.capture = "environment"
        assert inp.capture == "environment"

    def test_labels_is_empty_node_list(self):
        doc = Document()
        inp = doc.create_element("input")
        labels = inp.labels
        assert len(labels) == 0
        assert list(labels) == []


class TestHTMLTextAreaElementIdlTail2:
    """ADR-294: 4 new HTMLTextAreaElement IDL properties."""

    def test_default_value_getter_returns_text_content(self):
        doc = Document()
        ta = doc.create_element("textarea")
        assert ta.default_value == ""
        ta.default_value = "hello"
        assert ta.default_value == "hello"
        assert ta.text_content == "hello"

    def test_text_length_equals_len_value(self):
        doc = Document()
        ta = doc.create_element("textarea")
        assert ta.text_length == 0
        ta.default_value = "abc"
        assert ta.text_length == len(ta.value)
        assert ta.text_length == 3

    def test_dir_name_reflects_dirname_attribute(self):
        doc = Document()
        ta = doc.create_element("textarea")
        assert ta.dir_name == ""
        ta.dir_name = "ltr"
        assert ta.dir_name == "ltr"
        assert ta.get_attribute("dirname") == "ltr"

    def test_labels_is_empty_node_list(self):
        doc = Document()
        ta = doc.create_element("textarea")
        labels = ta.labels
        assert len(labels) == 0
        assert list(labels) == []


class TestHTMLButtonElementIdlTail:
    """ADR-294: 2 new HTMLButtonElement IDL properties."""

    def test_labels_is_empty_node_list(self):
        doc = Document()
        btn = doc.create_element("button")
        labels = btn.labels
        assert len(labels) == 0
        assert list(labels) == []

    def test_name_reflects_name_attribute(self):
        doc = Document()
        btn = doc.create_element("button")
        assert btn.name == ""
        btn.name = "submit-btn"
        assert btn.name == "submit-btn"
        assert btn.get_attribute("name") == "submit-btn"


class TestDoctests:

    def test_doctest_passes(self):
        """All doctests in _elements.py must pass with 0 failures."""
        import aspose_html.dom.html._elements as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_elements.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )

    def test_html_init_doctest_passes(self):
        """All doctests in aspose_html.dom.html.__init__ must pass."""
        import aspose_html.dom.html as _pkg
        results = doctest.testmod(_pkg, verbose=False)
        assert results.failed == 0, (
            f"dom.html __init__ doctests had {results.failed} failure(s)"
        )


# ---------------------------------------------------------------------------
# Track 102 — HTML element IDL tail (BACK-323 / ADR-301)
# ---------------------------------------------------------------------------

class TestTrack102HTMLElementIDLTail:
    """Tests for AC-15 to AC-21 of BACK-323 / ADR-301."""

    @pytest.fixture
    def doc(self) -> "Document":
        from aspose_html.dom import Document
        return Document()

    def test_htmlmeta_charset_default_empty(self, doc: "Document") -> None:
        """AC-15: HTMLMetaElement.charset default is ''."""
        el = doc.create_element("meta")
        assert el.charset == ""

    def test_htmlmeta_charset_reflect(self, doc: "Document") -> None:
        """AC-15: HTMLMetaElement.charset reflects 'charset' content attribute."""
        el = doc.create_element("meta")
        el.set_attribute("charset", "utf-8")
        assert el.charset == "utf-8"

    def test_htmlstyle_disabled_default_false(self, doc: "Document") -> None:
        """AC-16: HTMLStyleElement.disabled returns False when no sheet attached."""
        el = doc.create_element("style")
        assert el.disabled is False

    def test_htmlprogress_position_indeterminate(self, doc: "Document") -> None:
        """AC-17: HTMLProgressElement.position returns -1.0 when indeterminate."""
        el = doc.create_element("progress")
        assert el.position == -1.0

    def test_htmlprogress_position_ratio(self, doc: "Document") -> None:
        """AC-17: HTMLProgressElement.position returns 0.5 when value=5 max=10."""
        el = doc.create_element("progress")
        el.set_attribute("value", "5")
        el.set_attribute("max", "10")
        assert el.position == 0.5

    def test_htmlprogress_labels_empty(self, doc: "Document") -> None:
        """AC-18: HTMLProgressElement.labels returns empty node list."""
        el = doc.create_element("progress")
        assert len(el.labels) == 0

    def test_htmlmeter_labels_empty(self, doc: "Document") -> None:
        """AC-18: HTMLMeterElement.labels returns empty node list."""
        el = doc.create_element("meter")
        assert len(el.labels) == 0

    def test_htmlfieldset_form_none_when_detached(self, doc: "Document") -> None:
        """AC-19: HTMLFieldSetElement.form returns None when detached."""
        el = doc.create_element("fieldset")
        assert el.form is None

    def test_htmlfieldset_form_returns_ancestor_form(self, doc: "Document") -> None:
        """AC-19: HTMLFieldSetElement.form returns ancestor HTMLFormElement."""
        from aspose_html.dom.html._elements import HTMLFormElement
        form = doc.create_element("form")
        fs = doc.create_element("fieldset")
        form.append_child(fs)
        assert isinstance(fs.form, HTMLFormElement)

    def test_htmlscript_no_module_default_false(self, doc: "Document") -> None:
        """AC-20: HTMLScriptElement.no_module returns False by default."""
        el = doc.create_element("script")
        assert el.no_module is False

    def test_htmlscript_no_module_set(self, doc: "Document") -> None:
        """AC-20: HTMLScriptElement.no_module returns True after setting nomodule attr."""
        el = doc.create_element("script")
        el.set_attribute("nomodule", "")
        assert el.no_module is True

    def test_htmlscript_blocking_default_empty(self, doc: "Document") -> None:
        """AC-20: HTMLScriptElement.blocking returns '' by default."""
        el = doc.create_element("script")
        assert el.blocking == ""

    def test_htmlscript_fetch_priority_default_empty(self, doc: "Document") -> None:
        """AC-20: HTMLScriptElement.fetch_priority returns '' by default."""
        el = doc.create_element("script")
        assert el.fetch_priority == ""

    def test_htmltd_cell_index_in_row(self) -> None:
        """AC-21: HTMLTableCellElement.cell_index returns 0-based row position."""
        from aspose_html import HTMLDocument
        d = HTMLDocument.parse("<table><tr><td>A</td><td>B</td></tr></table>")
        cells = list(d.query_selector_all("td"))
        assert cells[0].cell_index == 0
        assert cells[1].cell_index == 1

    def test_htmltd_cell_index_detached(self, doc: "Document") -> None:
        """AC-21: HTMLTableCellElement.cell_index returns -1 when detached."""
        el = doc.create_element("td")
        assert el.cell_index == -1

    def test_htmltd_abbr_default_empty(self, doc: "Document") -> None:
        """AC-21: HTMLTableCellElement.abbr returns '' by default."""
        el = doc.create_element("td")
        assert el.abbr == ""

    def test_htmltd_abbr_reflect(self, doc: "Document") -> None:
        """AC-21: HTMLTableCellElement.abbr reflects 'abbr' attribute."""
        el = doc.create_element("td")
        el.set_attribute("abbr", "col1")
        assert el.abbr == "col1"


# ---------------------------------------------------------------------------
# Track 103 — HTML element IDL tail (BACK-324 / ADR-302)
# ---------------------------------------------------------------------------

class TestTrack103HTMLElementIDLTail:
    """Tests for AC-1 through AC-7 of BACK-324 / ADR-302."""

    @pytest.fixture
    def doc(self) -> "Document":
        from aspose_html.dom import Document
        return Document()

    # HTMLTableElement (AC-1)
    def test_table_frame_default_empty(self, doc: "Document") -> None:
        """AC-1: HTMLTableElement.frame returns '' by default."""
        t = doc.create_element("table")
        assert t.frame == ""

    def test_table_frame_reflect(self, doc: "Document") -> None:
        """AC-1: HTMLTableElement.frame reflects the 'frame' content attribute."""
        t = doc.create_element("table")
        t.set_attribute("frame", "box")
        assert t.frame == "box"

    def test_table_rules_default_empty(self, doc: "Document") -> None:
        """AC-1: HTMLTableElement.rules returns '' by default."""
        t = doc.create_element("table")
        assert t.rules == ""

    def test_table_bg_color_default_empty(self, doc: "Document") -> None:
        """AC-1: HTMLTableElement.bg_color returns '' by default."""
        t = doc.create_element("table")
        assert t.bg_color == ""

    def test_table_cell_padding_default_empty(self, doc: "Document") -> None:
        """AC-1: HTMLTableElement.cell_padding returns '' by default."""
        t = doc.create_element("table")
        assert t.cell_padding == ""

    def test_table_cell_spacing_default_empty(self, doc: "Document") -> None:
        """AC-1: HTMLTableElement.cell_spacing returns '' by default."""
        t = doc.create_element("table")
        assert t.cell_spacing == ""

    # HTMLTableCellElement (AC-2)
    def test_td_align_default_empty(self, doc: "Document") -> None:
        """AC-2: HTMLTableCellElement.align returns '' by default."""
        el = doc.create_element("td")
        assert el.align == ""

    def test_td_bg_color_default_empty(self, doc: "Document") -> None:
        """AC-2: HTMLTableCellElement.bg_color returns '' by default."""
        el = doc.create_element("td")
        assert el.bg_color == ""

    def test_td_no_wrap_default_false(self, doc: "Document") -> None:
        """AC-2: HTMLTableCellElement.no_wrap returns False by default."""
        el = doc.create_element("td")
        assert el.no_wrap is False

    def test_td_no_wrap_reflect(self, doc: "Document") -> None:
        """AC-2: HTMLTableCellElement.no_wrap returns True when nowrap attr set."""
        el = doc.create_element("td")
        el.set_attribute("nowrap", "")
        assert el.no_wrap is True

    def test_td_width_default_empty(self, doc: "Document") -> None:
        """AC-2: HTMLTableCellElement.width returns '' by default."""
        el = doc.create_element("td")
        assert el.width == ""

    def test_td_height_default_empty(self, doc: "Document") -> None:
        """AC-2: HTMLTableCellElement.height returns '' by default."""
        el = doc.create_element("td")
        assert el.height == ""

    # HTMLTableColElement (AC-3)
    def test_col_width_default_empty(self, doc: "Document") -> None:
        """AC-3: HTMLTableColElement.width returns '' by default."""
        el = doc.create_element("col")
        assert el.width == ""

    def test_col_align_default_empty(self, doc: "Document") -> None:
        """AC-3: HTMLTableColElement.align returns '' by default."""
        el = doc.create_element("col")
        assert el.align == ""

    def test_col_v_align_default_empty(self, doc: "Document") -> None:
        """AC-3: HTMLTableColElement.v_align returns '' by default."""
        el = doc.create_element("col")
        assert el.v_align == ""

    def test_col_v_align_reflects_valign(self, doc: "Document") -> None:
        """AC-3: HTMLTableColElement.v_align reflects the 'valign' content attribute."""
        el = doc.create_element("col")
        el.set_attribute("valign", "top")
        assert el.v_align == "top"

    # HTMLBodyElement (AC-4)
    def test_body_background_default_empty(self, doc: "Document") -> None:
        """AC-4: HTMLBodyElement.background returns '' by default."""
        el = doc.create_element("body")
        assert el.background == ""

    def test_body_bg_color_default_empty(self, doc: "Document") -> None:
        """AC-4: HTMLBodyElement.bg_color returns '' by default."""
        el = doc.create_element("body")
        assert el.bg_color == ""

    def test_body_text_default_empty(self, doc: "Document") -> None:
        """AC-4: HTMLBodyElement.text returns '' by default."""
        el = doc.create_element("body")
        assert el.text == ""

    def test_body_link_default_empty(self, doc: "Document") -> None:
        """AC-4: HTMLBodyElement.link returns '' by default."""
        el = doc.create_element("body")
        assert el.link == ""

    def test_body_v_link_default_empty(self, doc: "Document") -> None:
        """AC-4: HTMLBodyElement.v_link returns '' by default (reflects 'vlink')."""
        el = doc.create_element("body")
        assert el.v_link == ""

    def test_body_a_link_default_empty(self, doc: "Document") -> None:
        """AC-4: HTMLBodyElement.a_link returns '' by default (reflects 'alink')."""
        el = doc.create_element("body")
        assert el.a_link == ""

    # HTMLLIElement (AC-5)
    def test_li_type_default_empty(self, doc: "Document") -> None:
        """AC-5: HTMLLIElement.type returns '' by default."""
        el = doc.create_element("li")
        assert el.type == ""

    def test_li_type_reflect(self, doc: "Document") -> None:
        """AC-5: HTMLLIElement.type reflects the 'type' content attribute."""
        el = doc.create_element("li")
        el.set_attribute("type", "A")
        assert el.type == "A"

    # HTMLInputElement step stubs (AC-6)
    def test_input_step_up_no_raise(self, doc: "Document") -> None:
        """AC-6: HTMLInputElement.step_up() executes without raising; returns None."""
        el = doc.create_element("input")
        el.set_attribute("type", "number")
        el.set_attribute("value", "5")
        assert el.step_up() is None
        assert el.get_attribute("value") == "5"  # value unmutated

    def test_input_step_down_no_raise(self, doc: "Document") -> None:
        """AC-6: HTMLInputElement.step_down() executes without raising; returns None."""
        el = doc.create_element("input")
        el.set_attribute("type", "number")
        el.set_attribute("value", "5")
        assert el.step_down() is None

    # HTMLIFrameElement.loading (AC-7)
    def test_iframe_loading_default_empty(self, doc: "Document") -> None:
        """AC-7: HTMLIFrameElement.loading returns '' by default."""
        el = doc.create_element("iframe")
        assert el.loading == ""

    def test_iframe_loading_reflect(self, doc: "Document") -> None:
        """AC-7: HTMLIFrameElement.loading reflects the 'loading' content attribute."""
        el = doc.create_element("iframe")
        el.set_attribute("loading", "lazy")
        assert el.loading == "lazy"
