"""Track 36 integration tests (BACK-154, ADR-137, SPEC-083 Group F).

Cross-component integration tests covering all Track 36 groups:
- Group A: HTMLInputElement IDL properties (placeholder, read_only, autocomplete,
  autofocus, accept, size)
- Group B: HTMLFormElement IDL properties (enctype, encoding alias, novalidate,
  target, autocomplete)
- Group C: Navigator extended stubs (platform, language, languages, online,
  cookie_enabled, vendor) and Window.navigator delegation
- Group D: Document.ready_state, Document.embeds live collection,
  Document.applets always empty
- Group E: Window.alert/confirm/prompt stubs, Window.match_media,
  Window.get_computed_style cascade
- Cross-group: parsed-form integration, Navigator from document.default_view,
  computed style from parsed document with stylesheet
"""
from __future__ import annotations

import doctest

import pytest

from aspose_html.dom import Document, Navigator, MediaQueryList, Window
from aspose_html.dom._document import Document as DocumentImpl
from aspose_html.html_document import HTMLDocument


# ===========================================================================
# Group A — HTMLInputElement IDL properties (BACK-149)
# ===========================================================================


class TestGroupAHTMLInputElementDefaults:
    """Default values for the six new IDL properties — all without a document parse."""

    def test_placeholder_default_empty(self):
        inp = Document().create_element("input")
        assert inp.placeholder == ""

    def test_read_only_default_false(self):
        inp = Document().create_element("input")
        assert inp.read_only is False

    def test_autocomplete_default_empty(self):
        inp = Document().create_element("input")
        assert inp.autocomplete == ""

    def test_autofocus_default_false(self):
        inp = Document().create_element("input")
        assert inp.autofocus is False

    def test_accept_default_empty(self):
        inp = Document().create_element("input")
        assert inp.accept == ""

    def test_size_default_twenty(self):
        inp = Document().create_element("input")
        assert inp.size == 20

    def test_read_only_boolean_presence(self):
        """readonly attribute follows WHATWG boolean-presence rule."""
        inp = Document().create_element("input")
        inp.read_only = True
        assert inp.has_attribute("readonly")
        assert inp.get_attribute("readonly") == ""
        inp.read_only = False
        assert not inp.has_attribute("readonly")

    def test_autofocus_boolean_remove(self):
        """Clearing autofocus removes the boolean attribute entirely."""
        inp = Document().create_element("input")
        inp.autofocus = True
        assert inp.autofocus is True
        inp.autofocus = False
        assert inp.autofocus is False
        assert not inp.has_attribute("autofocus")


# ===========================================================================
# Group B — HTMLFormElement IDL properties (BACK-150)
# ===========================================================================


class TestGroupBHTMLFormElementDefaults:
    """Default values and encoding alias contract."""

    def test_enctype_default(self):
        form = Document().create_element("form")
        assert form.enctype == "application/x-www-form-urlencoded"

    def test_encoding_alias_reads_enctype(self):
        form = Document().create_element("form")
        form.enctype = "multipart/form-data"
        assert form.encoding == "multipart/form-data"

    def test_encoding_setter_writes_enctype(self):
        form = Document().create_element("form")
        form.encoding = "text/plain"
        assert form.enctype == "text/plain"

    def test_novalidate_default_false(self):
        form = Document().create_element("form")
        assert form.novalidate is False

    def test_novalidate_set_get(self):
        form = Document().create_element("form")
        form.novalidate = True
        assert form.novalidate is True
        assert form.has_attribute("novalidate")

    def test_target_default_empty(self):
        form = Document().create_element("form")
        assert form.target == ""

    def test_autocomplete_default_on(self):
        form = Document().create_element("form")
        assert form.autocomplete == "on"


# ===========================================================================
# Group C — Navigator extended stubs (BACK-151)
# ===========================================================================


class TestGroupCNavigatorStubs:
    """All six new Navigator stub properties and Window.navigator delegation."""

    def test_platform_returns_python(self):
        assert Navigator().platform == "Python"

    def test_language_returns_en(self):
        assert Navigator().language == "en"

    def test_languages_returns_tuple(self):
        langs = Navigator().languages
        assert langs == ("en",)
        assert isinstance(langs, tuple)

    def test_online_returns_true(self):
        assert Navigator().online is True

    def test_cookie_enabled_returns_false(self):
        assert Navigator().cookie_enabled is False

    def test_vendor_returns_empty_string(self):
        assert Navigator().vendor == ""

    def test_window_navigator_delegation(self):
        """Window.navigator returns a Navigator with expected stub values."""
        doc = Document()
        nav = doc.default_view.navigator
        assert isinstance(nav, Navigator)
        assert nav.platform == "Python"
        assert nav.online is True


# ===========================================================================
# Group D — Document lifecycle and collection stubs (BACK-152)
# ===========================================================================


class TestGroupDDocumentStubs:
    """Document.ready_state, Document.embeds live collection, Document.applets."""

    def test_ready_state_empty_document(self):
        assert Document().ready_state == "complete"

    def test_ready_state_parsed_document(self):
        doc = HTMLDocument.parse("<html><body><p>hi</p></body></html>")
        assert doc.ready_state == "complete"

    def test_embeds_empty_document_is_empty(self):
        assert len(Document().embeds) == 0

    def test_embeds_live_collection_with_embed_tags(self):
        doc = HTMLDocument.parse(
            "<html><body><embed src='a.swf'><embed src='b.swf'></body></html>"
        )
        col = doc.embeds
        assert len(col) == 2

    def test_embeds_first_element_tag_name(self):
        doc = HTMLDocument.parse("<html><body><embed src='x.swf'></body></html>")
        assert doc.embeds[0].tag_name == "EMBED"

    def test_applets_always_empty(self):
        """applets collection is always empty (applet is obsolete)."""
        assert len(Document().applets) == 0

    def test_applets_parsed_document_empty(self):
        doc = HTMLDocument.parse("<html><body><p>content</p></body></html>")
        assert len(doc.applets) == 0


# ===========================================================================
# Group E — Window interaction stubs (BACK-153)
# ===========================================================================


class TestGroupEWindowStubs:
    """alert/confirm/prompt no-ops, match_media stub, get_computed_style cascade."""

    def test_alert_returns_none(self):
        w = Document().default_view
        assert w.alert("Hello") is None

    def test_alert_no_args_returns_none(self):
        w = Document().default_view
        assert w.alert() is None

    def test_confirm_returns_false(self):
        w = Document().default_view
        assert w.confirm("Are you sure?") is False

    def test_confirm_no_args_returns_false(self):
        w = Document().default_view
        assert w.confirm() is False

    def test_prompt_returns_none(self):
        w = Document().default_view
        assert w.prompt("Enter value") is None

    def test_prompt_no_args_returns_none(self):
        w = Document().default_view
        assert w.prompt() is None

    def test_match_media_returns_mediaquerylist(self):
        w = Document().default_view
        mql = w.match_media("screen")
        assert isinstance(mql, MediaQueryList)

    def test_match_media_unsupported_query_false(self):
        """Unsupported feature query (min-width) returns False."""
        w = Document().default_view
        mql = w.match_media("screen and (min-width: 768px)")
        assert mql.matches is False

    def test_match_media_media_attribute(self):
        w = Document().default_view
        query = "print"
        mql = w.match_media(query)
        assert mql.media == query

    def test_get_computed_style_with_cascade(self):
        """get_computed_style returns cascade result from parsed document."""
        doc = HTMLDocument.parse(
            "<style>p { color: red; }</style><p id='x'>hi</p>"
        )
        el = doc.get_element_by_id("x")
        cs = doc.default_view.get_computed_style(el)
        assert cs.get_property_value("color") == "red"

    def test_match_media_and_get_computed_style_same_window(self):
        """match_media and get_computed_style can be called on the same Window."""
        doc = HTMLDocument.parse(
            "<style>span { font-size: 12px; }</style><span id='s'>x</span>"
        )
        w = doc.default_view
        # "all" matches in the default env
        mql = w.match_media("all")
        assert mql.matches is True
        # "print" does not match in the default screen env
        assert w.match_media("print").matches is False
        el = doc.get_element_by_id("s")
        cs = w.get_computed_style(el)
        assert cs.get_property_value("font-size") == "12px"


# ===========================================================================
# Cross-group integration
# ===========================================================================


class TestCrossGroupIntegration:
    """Cross-component tests combining multiple Track 36 groups."""

    def test_input_in_parsed_form_idl_properties(self):
        """Group A + HTML parser: input IDL properties from parsed HTML."""
        doc = HTMLDocument.parse(
            "<form><input placeholder='Name' readonly autofocus size='30'></form>"
        )
        inp = doc.query_selector("input")
        assert inp is not None
        assert inp.placeholder == "Name"
        assert inp.read_only is True
        assert inp.autofocus is True
        assert inp.size == 30

    def test_form_idl_properties_from_parsed_html(self):
        """Group B + HTML parser: form IDL properties from parsed HTML."""
        doc = HTMLDocument.parse(
            "<form enctype='multipart/form-data' novalidate target='_blank' autocomplete='off'>"
            "</form>"
        )
        form = doc.query_selector("form")
        assert form is not None
        assert form.enctype == "multipart/form-data"
        assert form.novalidate is True
        assert form.target == "_blank"
        assert form.autocomplete == "off"

    def test_navigator_from_document_default_view(self):
        """Group C + Window: navigator accessible through document.default_view."""
        doc = HTMLDocument.parse("<html><body></body></html>")
        nav = doc.default_view.navigator
        assert isinstance(nav, Navigator)
        assert nav.platform == "Python"
        assert nav.language == "en"
        assert nav.online is True

    def test_computed_style_from_parsed_document_with_stylesheet(self):
        """Group E + cascade + HTML parser: get_computed_style on parsed doc."""
        doc = HTMLDocument.parse(
            "<style>div { font-size: 16px; }</style><div id='d'>x</div>"
        )
        el = doc.get_element_by_id("d")
        cs = doc.default_view.get_computed_style(el)
        assert cs.get_property_value("font-size") == "16px"


# ===========================================================================
# Doctest sweep — INV-008 compliance
# ===========================================================================


class TestDoctestSweepTrack36:
    """Verify all docstring >>> blocks in the three Track 36 source files.

    These assertions satisfy INV-008: public API docstring examples must
    execute in CI under pytest --doctest-modules.
    """

    def test_elements_py_doctests_pass(self):
        """All doctests in dom/html/_elements.py must pass with 0 failures."""
        import aspose_html.dom.html._elements as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_elements.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )

    def test_window_py_doctests_pass(self):
        """All doctests in dom/_window.py must pass with 0 failures."""
        import aspose_html.dom._window as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_window.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )

    def test_document_py_doctests_pass(self):
        """All doctests in dom/_document.py must pass with 0 failures."""
        import aspose_html.dom._document as _mod
        results = doctest.testmod(_mod, verbose=False)
        assert results.failed == 0, (
            f"_document.py doctests had {results.failed} failure(s) "
            f"(attempted {results.attempted})"
        )
