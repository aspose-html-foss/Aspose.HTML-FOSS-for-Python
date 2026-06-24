"""Tests for  — HTML Element / Document / Window / CSS IDL tail.

Covers  /  / .

All 29 acceptance criteria are exercised here.
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document
from aspose_html.dom._exceptions import NotSupportedError
from aspose_html.dom._token_list import DOMTokenList


# ---------------------------------------------------------------------------
# AC-1..5 — Element shadow-DOM stubs
# ---------------------------------------------------------------------------

class TestElementShadowDOMStubs:
    """Element.part, .shadow_root, .slot, .attach_shadow(), .assigned_slot."""

    def setup_method(self):
        self.doc = Document()
        self.el = self.doc.create_element("div")

    def test_part_returns_dom_token_list(self):
        """AC-1: el.part returns a DOMTokenList."""
        assert isinstance(self.el.part, DOMTokenList)

    def test_part_add_updates_attribute(self):
        """AC-1: part.add('foo') updates the part attribute."""
        self.el.part.add("foo")
        assert self.el.get_attribute("part") == "foo"

    def test_part_contains(self):
        """AC-1: part.contains('foo') returns True after add."""
        self.el.part.add("foo")
        assert self.el.part.contains("foo") is True

    def test_shadow_root_is_none(self):
        """AC-2: el.shadow_root is None."""
        assert self.el.shadow_root is None

    def test_slot_empty_when_absent(self):
        """AC-3: el.slot returns '' when absent."""
        assert self.el.slot == ""

    def test_slot_reflects_attribute(self):
        """AC-3: el.slot returns 'x' after set_attribute('slot', 'x')."""
        self.el.set_attribute("slot", "x")
        assert self.el.slot == "x"

    def test_slot_setter_updates_attribute(self):
        """AC-3: el.slot setter updates the attribute."""
        self.el.slot = "named"
        assert self.el.get_attribute("slot") == "named"

    def test_attach_shadow_raises_not_supported(self):
        """AC-4: attach_shadow() raises NotSupportedError."""
        with pytest.raises(NotSupportedError):
            self.el.attach_shadow({"mode": "open"})

    def test_assigned_slot_is_none(self):
        """AC-5: el.assigned_slot is None."""
        assert self.el.assigned_slot is None


# ---------------------------------------------------------------------------
# AC-6 — HTMLElement.popover
# ---------------------------------------------------------------------------

class TestHTMLElementPopover:
    """HTMLElement.popover attribute reflection."""

    def setup_method(self):
        self.doc = Document()
        self.el = self.doc.create_element("div")

    def test_popover_none_when_absent(self):
        """AC-6: html_el.popover is None when attribute absent."""
        assert self.el.popover is None

    def test_popover_returns_value_after_set_attribute(self):
        """AC-6: returns 'auto' after set_attribute('popover', 'auto')."""
        self.el.set_attribute("popover", "auto")
        assert self.el.popover == "auto"

    def test_popover_setter_sets_attribute(self):
        """AC-6: setter sets the attribute."""
        self.el.popover = "manual"
        assert self.el.get_attribute("popover") == "manual"

    def test_popover_setter_none_removes_attribute(self):
        """AC-6: setter removes attribute when None passed."""
        self.el.set_attribute("popover", "auto")
        self.el.popover = None
        assert not self.el.has_attribute("popover")


# ---------------------------------------------------------------------------
# AC-7..8 — HTMLInputElement.dir_name + show_picker
# ---------------------------------------------------------------------------

class TestHTMLInputElementTail:
    """HTMLInputElement.dir_name alias and show_picker()."""

    def setup_method(self):
        self.doc = Document()
        self.inp = self.doc.create_element("input")

    def test_dir_name_equals_dirname(self):
        """AC-7: inp.dir_name returns the same value as inp.dirname."""
        assert self.inp.dir_name == self.inp.dirname

    def test_dir_name_after_attribute_set(self):
        """AC-7: dir_name reflects the dirname attribute value."""
        self.inp.set_attribute("dirname", "ltr")
        assert self.inp.dir_name == "ltr"
        assert self.inp.dir_name == self.inp.dirname

    def test_dir_name_setter_propagates(self):
        """AC-7: dir_name setter propagates to dirname."""
        self.inp.dir_name = "rtl"
        assert self.inp.dirname == "rtl"

    def test_show_picker_raises_not_supported(self):
        """AC-8: inp.show_picker() raises NotSupportedError."""
        with pytest.raises(NotSupportedError):
            self.inp.show_picker()


# ---------------------------------------------------------------------------
# AC-9..12 — Document IDL tail
# ---------------------------------------------------------------------------

class TestDocumentIDLTail:
    """Document.fonts, picture_in_picture_enabled, picture_in_picture_element, prerendering."""

    def setup_method(self):
        self.doc = Document()

    def test_fonts_is_none(self):
        """AC-9: doc.fonts is None."""
        assert self.doc.fonts is None

    def test_picture_in_picture_enabled_false(self):
        """AC-10: doc.picture_in_picture_enabled is False."""
        assert self.doc.picture_in_picture_enabled is False

    def test_picture_in_picture_element_none(self):
        """AC-11: doc.picture_in_picture_element is None."""
        assert self.doc.picture_in_picture_element is None

    def test_prerendering_false(self):
        """AC-12: doc.prerendering is False."""
        assert self.doc.prerendering is False


# ---------------------------------------------------------------------------
# AC-13..18 — Window IDL tail
# ---------------------------------------------------------------------------

class TestWindowIDLTail:
    """Window.scheduler, report_error, pub_key_credential, cookie_store, text_decoder, text_encoder."""

    def setup_method(self):
        self.win = Document().default_view

    def test_scheduler_is_none(self):
        """AC-13: win.scheduler is None."""
        assert self.win.scheduler is None

    def test_report_error_completes_without_raising(self):
        """AC-14: win.report_error(Exception()) completes without raising."""
        self.win.report_error(Exception("test"))  # must not raise

    def test_pub_key_credential_is_none(self):
        """AC-15: win.pub_key_credential is None."""
        assert self.win.pub_key_credential is None

    def test_cookie_store_is_none(self):
        """AC-16: win.cookie_store is None."""
        assert self.win.cookie_store is None

    def test_text_decoder_is_none(self):
        """AC-17: win.text_decoder is None."""
        assert self.win.text_decoder is None

    def test_text_encoder_is_none(self):
        """AC-18: win.text_encoder is None."""
        assert self.win.text_encoder is None


# ---------------------------------------------------------------------------
# AC-19..21 — Navigator IDL tail
# ---------------------------------------------------------------------------

class TestNavigatorIDLTail:
    """Navigator.global_privacy_control, webdriver, get_gamepads."""

    def setup_method(self):
        self.nav = Document().default_view.navigator

    def test_global_privacy_control_false(self):
        """AC-19: nav.global_privacy_control is False."""
        assert self.nav.global_privacy_control is False

    def test_webdriver_true(self):
        """AC-20: nav.webdriver is True."""
        assert self.nav.webdriver is True

    def test_get_gamepads_returns_empty_list(self):
        """AC-21: nav.get_gamepads() == []."""
        assert self.nav.get_gamepads() == []


# ---------------------------------------------------------------------------
# AC-22..28 — CSS IVB additions
# ---------------------------------------------------------------------------

class TestCSSIDLTail:
    """CSS.supports() for all 7 new longhands."""

    @pytest.fixture(autouse=True)
    def _css(self):
        from aspose_html.cssom import CSS
        self.css = CSS

    def test_overflow_anchor(self):
        """AC-22: CSS.supports('overflow-anchor', 'auto') is True."""
        assert self.css.supports("overflow-anchor", "auto") is True

    def test_overscroll_behavior_block(self):
        """AC-23: CSS.supports('overscroll-behavior-block', 'auto') is True."""
        assert self.css.supports("overscroll-behavior-block", "auto") is True

    def test_overscroll_behavior_inline(self):
        """AC-24: CSS.supports('overscroll-behavior-inline', 'auto') is True."""
        assert self.css.supports("overscroll-behavior-inline", "auto") is True

    def test_offset_position(self):
        """AC-25: CSS.supports('offset-position', 'normal') is True."""
        assert self.css.supports("offset-position", "normal") is True

    def test_color_adjust(self):
        """AC-26: CSS.supports('color-adjust', 'economy') is True."""
        assert self.css.supports("color-adjust", "economy") is True

    def test_white_space_collapse(self):
        """AC-27: CSS.supports('white-space-collapse', 'collapse') is True."""
        assert self.css.supports("white-space-collapse", "collapse") is True

    def test_webkit_appearance(self):
        """AC-28: CSS.supports('-webkit-appearance', 'none') is True."""
        assert self.css.supports("-webkit-appearance", "none") is True

    def test_entries_in_initial_value_baseline(self):
        """All 7 new properties are present in _INITIAL_VALUE_BASELINE."""
        from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE
        new_props = [
            "overflow-anchor",
            "overscroll-behavior-block",
            "overscroll-behavior-inline",
            "offset-position",
            "color-adjust",
            "white-space-collapse",
            "-webkit-appearance",
        ]
        for prop in new_props:
            assert prop in _INITIAL_VALUE_BASELINE, f"{prop!r} missing from _INITIAL_VALUE_BASELINE"
