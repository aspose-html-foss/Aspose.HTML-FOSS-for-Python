"""Tests for  — HTML Element / Window / Navigator / CSS IDL tail.

Covers  /  acceptance criteria AC-1 through AC-40.
"""
from __future__ import annotations

import pytest

from aspose_html.dom._document import Document
from aspose_html.dom import DOMTokenList


# ---------------------------------------------------------------------------
# HTMLAreaElement (AC-1 through AC-6)
# ---------------------------------------------------------------------------

class TestHTMLAreaElementTail:
    """AC-1..6 — HTMLAreaElement IDL tail additions."""

    def setup_method(self) -> None:
        self.doc = Document()
        self.area = self.doc.create_element("area")

    def test_ac1_download_absent(self) -> None:
        """AC-1: area.download returns empty string when attribute absent."""
        assert self.area.download == ""

    def test_ac1_download_roundtrip(self) -> None:
        self.area.download = "report.pdf"
        assert self.area.download == "report.pdf"

    def test_ac2_rel_list_is_domtokenlist(self) -> None:
        """AC-2: area.rel_list returns DOMTokenList."""
        assert isinstance(self.area.rel_list, DOMTokenList)

    def test_ac2_rel_list_add_updates_rel(self) -> None:
        """AC-2: add('nofollow') updates area.rel."""
        self.area.rel_list.add("nofollow")
        assert self.area.rel == "nofollow"

    def test_ac2_rel_list_same_instance(self) -> None:
        """AC-2: same instance on every access."""
        assert self.area.rel_list is self.area.rel_list

    def test_ac3_referrer_policy_absent(self) -> None:
        """AC-3: area.referrer_policy returns empty string when absent."""
        assert self.area.referrer_policy == ""

    def test_ac3_referrer_policy_roundtrip(self) -> None:
        self.area.referrer_policy = "no-referrer"
        assert self.area.referrer_policy == "no-referrer"

    def test_ac4_ping_absent(self) -> None:
        """AC-4: area.ping returns empty string when ping absent."""
        assert self.area.ping == ""

    def test_ac4_ping_roundtrip(self) -> None:
        self.area.ping = "https://example.com/ping"
        assert self.area.ping == "https://example.com/ping"

    def test_ac5_hostname(self) -> None:
        """AC-5: area.hostname returns 'example.com' for href='https://example.com/path'."""
        self.area.set_attribute("href", "https://example.com/path")
        assert self.area.hostname == "example.com"

    def test_ac5_hostname_absent(self) -> None:
        assert self.area.hostname == ""

    def test_ac6_pathname(self) -> None:
        """AC-6: area.pathname returns '/path' for href='https://example.com/path'."""
        self.area.set_attribute("href", "https://example.com/path")
        assert self.area.pathname == "/path"

    def test_ac6_pathname_absent(self) -> None:
        assert self.area.pathname == ""


# ---------------------------------------------------------------------------
# HTMLOListElement (AC-7 through AC-8)
# ---------------------------------------------------------------------------

class TestHTMLOListElementTail:
    """AC-7..8 — HTMLOListElement IDL tail additions."""

    def setup_method(self) -> None:
        self.doc = Document()
        self.ol = self.doc.create_element("ol")

    def test_ac7_type_absent(self) -> None:
        """AC-7: ol.type reflects type attribute; default empty string."""
        assert self.ol.type == ""

    def test_ac7_type_roundtrip(self) -> None:
        self.ol.type = "A"
        assert self.ol.type == "A"

    def test_ac8_compact_absent(self) -> None:
        """AC-8: ol.compact reflects compact boolean; default False."""
        assert self.ol.compact is False

    def test_ac8_compact_set(self) -> None:
        self.ol.compact = True
        assert self.ol.compact is True

    def test_ac8_compact_unset(self) -> None:
        self.ol.compact = True
        self.ol.compact = False
        assert self.ol.compact is False


# ---------------------------------------------------------------------------
# HTMLObjectElement (AC-9 through AC-15)
# ---------------------------------------------------------------------------

class TestHTMLObjectElementTail:
    """AC-9..15 — HTMLObjectElement constraint validation + use_map."""

    def setup_method(self) -> None:
        self.doc = Document()
        self.obj = self.doc.create_element("object")

    def test_ac9_use_map_absent(self) -> None:
        """AC-9: obj.use_map reflects usemap attribute; default empty string."""
        assert self.obj.use_map == ""

    def test_ac9_use_map_roundtrip(self) -> None:
        self.obj.set_attribute("usemap", "#mymap")
        assert self.obj.use_map == "#mymap"

    def test_ac10_will_validate_false(self) -> None:
        """AC-10: obj.will_validate is False."""
        assert self.obj.will_validate is False

    def test_ac11_validity_valid(self) -> None:
        """AC-11: obj.validity is a ValidityState with valid == True."""
        vs = self.obj.validity
        assert vs.valid is True

    def test_ac12_validation_message_empty(self) -> None:
        """AC-12: obj.validation_message is empty string."""
        assert self.obj.validation_message == ""

    def test_ac13_check_validity_returns_true(self) -> None:
        """AC-13: obj.check_validity() returns True."""
        assert self.obj.check_validity() is True

    def test_ac14_report_validity_returns_true(self) -> None:
        """AC-14: obj.report_validity() returns True."""
        assert self.obj.report_validity() is True

    def test_ac15_set_custom_validity_no_raise(self) -> None:
        """AC-15: obj.set_custom_validity('e') does not raise."""
        self.obj.set_custom_validity("e")  # must not raise


# ---------------------------------------------------------------------------
# HTMLIFrameElement (AC-16)
# ---------------------------------------------------------------------------

class TestHTMLIFrameElementTail:
    """AC-16 — HTMLIFrameElement.allow_fullscreen."""

    def setup_method(self) -> None:
        self.doc = Document()
        self.iframe = self.doc.create_element("iframe")

    def test_ac16_allow_fullscreen_absent(self) -> None:
        """AC-16: iframe.allow_fullscreen is False when allowfullscreen absent."""
        assert self.iframe.allow_fullscreen is False

    def test_ac16_allow_fullscreen_set(self) -> None:
        self.iframe.set_attribute("allowfullscreen", "")
        assert self.iframe.allow_fullscreen is True

    def test_ac16_allow_fullscreen_setter(self) -> None:
        self.iframe.allow_fullscreen = True
        assert self.iframe.allow_fullscreen is True
        self.iframe.allow_fullscreen = False
        assert self.iframe.allow_fullscreen is False


# ---------------------------------------------------------------------------
# HTMLOutputElement (AC-17)
# ---------------------------------------------------------------------------

class TestHTMLOutputElementTail:
    """AC-17 — HTMLOutputElement.labels."""

    def test_ac17_labels_no_raise(self) -> None:
        """AC-17: out.labels returns empty node list without raising."""
        doc = Document()
        out = doc.create_element("output")
        labels = out.labels
        assert len(labels) == 0

    def test_ac17_labels_is_iterable(self) -> None:
        doc = Document()
        out = doc.create_element("output")
        assert list(out.labels) == []


# ---------------------------------------------------------------------------
# Window (AC-18 through AC-23)
# ---------------------------------------------------------------------------

class TestWindowTail:
    """AC-18..23 — Window IDL tail additions."""

    def setup_method(self) -> None:
        self.win = Document().default_view

    def test_ac18_screen_width(self) -> None:
        """AC-18: window.screen_width == 0."""
        assert self.win.screen_width == 0

    def test_ac18_screen_height(self) -> None:
        """AC-18: window.screen_height == 0."""
        assert self.win.screen_height == 0

    def test_ac19_trusted_types_none(self) -> None:
        """AC-19: window.trusted_types is None."""
        assert self.win.trusted_types is None

    def test_ac20_external_add_search_provider(self) -> None:
        """AC-20: window.external.add_search_provider('x') does not raise."""
        self.win.external.add_search_provider("https://example.com/search")

    def test_ac20_external_not_none(self) -> None:
        assert self.win.external is not None

    def test_ac21_speech_synthesis_none(self) -> None:
        """AC-21: window.speech_synthesis is None."""
        assert self.win.speech_synthesis is None

    def test_ac22_caches_none(self) -> None:
        """AC-22: window.caches is None."""
        assert self.win.caches is None

    def test_ac23_index_db_none(self) -> None:
        """AC-23: window.index_db is None."""
        assert self.win.index_db is None


# ---------------------------------------------------------------------------
# Navigator (AC-24 through AC-29)
# ---------------------------------------------------------------------------

class TestNavigatorTail:
    """AC-24..29 — Navigator IDL tail additions."""

    def setup_method(self) -> None:
        self.nav = Document().default_view.navigator

    def test_ac24_media_capabilities_none(self) -> None:
        """AC-24: navigator.media_capabilities is None."""
        assert self.nav.media_capabilities is None

    def test_ac25_permissions_none(self) -> None:
        """AC-25: navigator.permissions is None."""
        assert self.nav.permissions is None

    def test_ac26_service_worker_none(self) -> None:
        """AC-26: navigator.service_worker is None."""
        assert self.nav.service_worker is None

    def test_ac27_user_activation_none(self) -> None:
        """AC-27: navigator.user_activation is None."""
        assert self.nav.user_activation is None

    def test_ac28_keyboard_none(self) -> None:
        """AC-28: navigator.keyboard is None."""
        assert self.nav.keyboard is None

    def test_ac29_presentation_none(self) -> None:
        """AC-29: navigator.presentation is None."""
        assert self.nav.presentation is None


# ---------------------------------------------------------------------------
# CSS property tail (AC-30 through AC-39)
# ---------------------------------------------------------------------------

class TestCSSPropertyTail:
    """AC-30..39 — 10 new CSS property registrations."""

    @pytest.fixture(autouse=True)
    def _import_css(self) -> None:
        from aspose_html.cssom import CSS
        self.CSS = CSS

    def test_ac30_overflow_clip_margin(self) -> None:
        """AC-30: CSS.supports('overflow-clip-margin', '0px') returns True."""
        assert self.CSS.supports("overflow-clip-margin", "0px") is True

    def test_ac31_font_synthesis_weight(self) -> None:
        """AC-31: CSS.supports('font-synthesis-weight', 'auto') returns True."""
        assert self.CSS.supports("font-synthesis-weight", "auto") is True

    def test_ac32_font_synthesis_style(self) -> None:
        """AC-32: CSS.supports('font-synthesis-style', 'auto') returns True."""
        assert self.CSS.supports("font-synthesis-style", "auto") is True

    def test_ac33_font_synthesis_small_caps(self) -> None:
        """AC-33: CSS.supports('font-synthesis-small-caps', 'auto') returns True."""
        assert self.CSS.supports("font-synthesis-small-caps", "auto") is True

    def test_ac34_font_synthesis_position(self) -> None:
        """AC-34: CSS.supports('font-synthesis-position', 'auto') returns True."""
        assert self.CSS.supports("font-synthesis-position", "auto") is True

    def test_ac35_transition_behavior(self) -> None:
        """AC-35: CSS.supports('transition-behavior', 'normal') returns True."""
        assert self.CSS.supports("transition-behavior", "normal") is True

    def test_ac36_hanging_punctuation(self) -> None:
        """AC-36: CSS.supports('hanging-punctuation', 'none') returns True."""
        assert self.CSS.supports("hanging-punctuation", "none") is True

    def test_ac37_background_position_x(self) -> None:
        """AC-37: CSS.supports('background-position-x', '0%') returns True."""
        assert self.CSS.supports("background-position-x", "0%") is True

    def test_ac38_background_position_y(self) -> None:
        """AC-38: CSS.supports('background-position-y', '0%') returns True."""
        assert self.CSS.supports("background-position-y", "0%") is True

    def test_ac39_text_decoration_skip(self) -> None:
        """AC-39: CSS.supports('text-decoration-skip', 'objects') returns True."""
        assert self.CSS.supports("text-decoration-skip", "objects") is True


# ---------------------------------------------------------------------------
# AC-40: Full test suite — 0 new failures (verified by running this file)
# ---------------------------------------------------------------------------
