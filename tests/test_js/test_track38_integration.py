""" cross-component integration tests (, ).

Verifies that , , and  components interact correctly:

- Group A: match_media() + @media cascade agreement ()
- Group B: CSSStyleDeclaration priority + cascade ()
- Group C: insert_rule / delete_rule + cascade live update ()
- Group D: JS setAttribute write-through + Python DOM (, quickjs-gated)
- Group E: Doctest sweep (module-level doctests pass)

Groups A–C are pure-Python and must not skip.
Group D uses a module-level ``pytest.importorskip`` guard stored in the
``quickjs`` module variable; all Group D tests use the ``_require_quickjs``
fixture which enforces the skip at test invocation time.  Groups A–C never
reference ``_require_quickjs`` so they are never skipped by it.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import Generator

import pytest

from aspose_html import HTMLDocument
from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import Document, IndexSizeError
from aspose_html.dom._window import MediaQueryList


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# QuickJS availability — evaluated once at import time.
# The `_quickjs` variable is None when the package is absent.
# ---------------------------------------------------------------------------
try:
    import quickjs as _quickjs_module  # type: ignore[import-untyped]
    _QUICKJS_AVAILABLE = True
except ImportError:
    _quickjs_module = None
    _QUICKJS_AVAILABLE = False


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture()
def _require_quickjs() -> None:
    """Skip the calling test when ``quickjs`` is not installed.

    All Group D tests declare this fixture as a parameter; Groups A–C do not,
    so they are never skipped by this guard.
    """
    if not _QUICKJS_AVAILABLE:
        pytest.skip("quickjs not installed")


@pytest.fixture()
def _doc_with_div() -> Document:
    """Document with one <div id='box'> for Group D tests."""
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("id", "box")
    doc.append_child(el)
    return doc


# ===========================================================================
# Group A — match_media() ↔ @media cascade agreement ()
# ===========================================================================


class TestGroupAMatchMediaCascadeAgreement:
    """Both match_media() and the cascade @media evaluator must agree."""

    def test_a1_screen_cascade_and_match_media_agree(self) -> None:
        """@media screen cascade includes rule and match_media('screen').matches is True.

        AC-1 cross-component: both the cascade engine and Window.match_media
        evaluate against the same _MEDIA_BASELINE_ENV default (type='screen').
        """
        doc = HTMLDocument.parse(
            "<style>@media screen { div { color: blue } }</style><div id='t'>hi</div>"
        )
        el = doc.get_element_by_id("t")
        assert el is not None

        # Cascade side: the @media screen block is included
        assert el.get_computed_style().get_property_value("color") == "blue"

        # match_media side: must agree
        assert doc.default_view.match_media("screen").matches is True

    def test_a2_print_rule_excluded_in_screen_env(self) -> None:
        """@media print rule is excluded in default screen env;
        match_media('print').matches is False.

        AC-2 cross-component: screen baseline means print rules are NOT applied
        by the cascade, and match_media('print') is also False.
        """
        doc = HTMLDocument.parse(
            "<style>@media print { div { color: olive } }</style><div id='t'>hi</div>"
        )
        el = doc.get_element_by_id("t")
        assert el is not None

        # Cascade side: @media print block is excluded
        assert el.get_computed_style().get_property_value("color") == ""

        # match_media side: must agree — print does not match
        assert doc.default_view.match_media("print").matches is False

    def test_a3_prefers_color_scheme_light_cascade_and_match_media(self) -> None:
        """@media (prefers-color-scheme: light) block is included + match_media agrees.

        AC-3 cross-component: baseline env has prefers-color-scheme: light.
        """
        doc = HTMLDocument.parse(
            "<style>@media (prefers-color-scheme: light) { div { color: green } }</style>"
            "<div id='t'>hi</div>"
        )
        el = doc.get_element_by_id("t")
        assert el is not None

        # Cascade side: prefers-color-scheme: light block is included
        assert el.get_computed_style().get_property_value("color") == "green"

        # match_media side: must agree
        assert doc.default_view.match_media("(prefers-color-scheme: light)").matches is True

    def test_a4_prefers_color_scheme_dark_excluded(self) -> None:
        """match_media('(prefers-color-scheme: dark)').matches is False (default env)."""
        doc = Document()
        assert doc.default_view.match_media("(prefers-color-scheme: dark)").matches is False


# ===========================================================================
# Group B — CSSStyleDeclaration priority ↔ cascade interaction ()
# ===========================================================================


class TestGroupBStyleDeclarationPriorityCascade:
    """Inline !important set via set_property() must be seen by the cascade."""

    def test_b4_inline_important_beats_normal_author_rule(self) -> None:
        """Inline !important declaration wins over normal author rule.

        AC-7: el.style.set_property('color','red','important') → cascade returns 'red'
        even when a normal stylesheet rule sets 'color: blue'.
        """
        doc = HTMLDocument.parse('<div id="x">hi</div>')
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: blue }")
        doc.attach_style_sheet(sheet)
        el = doc.get_element_by_id("x")
        assert el is not None

        # Normal author rule is the only candidate — blue wins
        assert el.get_computed_style().get_property_value("color") == "blue"

        # Inline !important must beat the normal author rule
        el.style.set_property("color", "red", "important")
        assert el.get_computed_style().get_property_value("color") == "red"

    def test_b5_inline_important_vs_author_important_cascade_edge_case(self) -> None:
        """Inline !important vs author !important — inline wins (higher specificity).

        CSS Cascade Level 4: both are author-origin important. The inline
        declaration has specificity (1,0,0); a bare element rule ('div') has
        specificity (0,0,1). Inline wins because both are author !important
        and (1,0,0) > (0,0,1). This is a regression-guard pin.
        """
        doc = HTMLDocument.parse('<div id="x">hi</div>')
        sheet = CSSStyleSheet()
        sheet.replace_sync("div { color: blue !important }")
        doc.attach_style_sheet(sheet)
        el = doc.get_element_by_id("x")
        assert el is not None

        # Author !important wins before any inline
        assert el.get_computed_style().get_property_value("color") == "blue"

        # Inline !important should win (higher specificity, same origin tier)
        el.style.set_property("color", "red", "important")
        assert el.get_computed_style().get_property_value("color") == "red"

    def test_b6_get_property_priority_roundtrip_and_css_text(self) -> None:
        """get_property_priority roundtrip: set with 'important', css_text contains !important.

        AC-5 + AC-6: both get_property_priority and css_text must reflect !important.
        """
        doc = Document()
        el = doc.create_element("div")

        el.style.set_property("color", "red", "important")

        # get_property_priority must return 'important'
        assert el.style.get_property_priority("color") == "important"

        # css_text must contain '!important'
        css_text = el.style.css_text
        assert "!important" in css_text
        assert "color" in css_text
        assert "red" in css_text


# ===========================================================================
# Group C — insert_rule ↔ cascade live update ()
# ===========================================================================


class TestGroupCInsertRuleCascadeInteraction:
    """Dynamically inserted rules must be picked up by the next get_computed_style()."""

    def test_c7_insert_rule_cascade_picks_up_new_rule(self) -> None:
        """insert_rule on live sheet — next get_computed_style sees the new rule.

        AC-8: cascade queries the live css_rules list, so a freshly inserted
        rule is immediately visible on the next cascade evaluation.
        """
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        doc.attach_style_sheet(sheet)

        # No rules yet — property absent
        assert el.get_computed_style().get_property_value("color") == ""

        # Insert a rule for div
        sheet.insert_rule("div { color: purple }")

        # Cascade must now return the inserted rule's value
        assert el.get_computed_style().get_property_value("color") == "purple"

    def test_c8_insert_then_delete_rule_cascade_reflects_both(self) -> None:
        """insert_rule then delete_rule — cascade uses and then discards the rule.

        After insert, cascade returns the value; after delete, cascade no
        longer returns that value.
        """
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        doc.attach_style_sheet(sheet)

        idx = sheet.insert_rule("div { color: teal }")
        assert el.get_computed_style().get_property_value("color") == "teal"

        sheet.delete_rule(idx)
        # After deletion, property should be absent (returns "")
        assert el.get_computed_style().get_property_value("color") == ""

    def test_c9_insert_rule_lower_specificity_does_not_override_higher(self) -> None:
        """insert_rule with lower specificity does not override a higher-specificity rule.

        A '.red' class selector (0,1,0) beats a bare 'div' selector (0,0,1).
        Inserting the lower-specificity rule at index 0 must not change the
        cascade winner.
        """
        doc = Document()
        el = doc.create_element("div")
        el.set_attribute("class", "red")
        doc.append_child(el)

        sheet = CSSStyleSheet()
        sheet.replace_sync(".red { color: red }")
        doc.attach_style_sheet(sheet)

        # Class selector wins
        assert el.get_computed_style().get_property_value("color") == "red"

        # Insert a lower-specificity rule at index 0 (before the class rule)
        sheet.insert_rule("div { color: green }", 0)

        # Specificity: .red (0,1,0) > div (0,0,1) — class rule still wins
        assert el.get_computed_style().get_property_value("color") == "red"


# ===========================================================================
# Group D — JS setAttribute write-through ↔ Python DOM ()
# All tests declare _require_quickjs fixture; skip when quickjs absent.
# ===========================================================================


class TestGroupDJsBridgeWriteThrough:
    """JS setAttribute must write through to the Python DOM element."""

    def test_d10_set_attribute_id_visible_to_python(
        self, _require_quickjs: None, _doc_with_div: Document
    ) -> None:
        """JS el.setAttribute('id', 'new-id') → Python el.get_attribute('id') == 'new-id'."""
        from aspose_html.css import select
        from aspose_html.js import JSContext

        elements = select(_doc_with_div, "div", first_only=True)
        el = elements[0]

        with JSContext(_doc_with_div) as ctx:
            ctx.evaluate("document.querySelector('div').setAttribute('id', 'new-id')")

        assert el.get_attribute("id") == "new-id"

    def test_d11_set_attribute_style_visible_to_cascade(
        self, _require_quickjs: None, _doc_with_div: Document
    ) -> None:
        """JS setAttribute('style', 'color: cyan') → Python cascade sees updated style.

        After JS writes the style attribute, Python's get_computed_style()
        must return 'cyan' because the cascade re-reads the live style attr.
        """
        from aspose_html.css import select
        from aspose_html.js import JSContext

        elements = select(_doc_with_div, "div", first_only=True)
        el = elements[0]

        with JSContext(_doc_with_div) as ctx:
            ctx.evaluate(
                "document.querySelector('div').setAttribute('style', 'color: cyan')"
            )

        # Cascade sees the new inline style
        assert el.get_computed_style().get_property_value("color") == "cyan"

    def test_d12_add_event_listener_plus_get_attribute_in_one_evaluate(
        self, _require_quickjs: None, _doc_with_div: Document
    ) -> None:
        """JS addEventListener + getAttribute in single evaluate() — no error, correct return."""
        from aspose_html.js import JSContext

        with JSContext(_doc_with_div) as ctx:
            result = ctx.evaluate(
                "(function(){"
                "  var el = document.querySelector('div');"
                "  el.addEventListener('click', function(){});"
                "  return el.getAttribute('id');"
                "})()"
            )
        assert result == "box"

    def test_d13_document_add_event_listener_no_error(
        self, _require_quickjs: None, _doc_with_div: Document
    ) -> None:
        """JS document.addEventListener('DOMContentLoaded', fn) does not throw."""
        from aspose_html.js import JSContext

        with JSContext(_doc_with_div) as ctx:
            result = ctx.evaluate(
                "document.addEventListener('DOMContentLoaded', function(){})"
            )
        assert result is None

    def test_d14_window_add_event_listener_no_error(
        self, _require_quickjs: None, _doc_with_div: Document
    ) -> None:
        """JS window.addEventListener('load', fn) does not throw."""
        from aspose_html.js import JSContext

        with JSContext(_doc_with_div) as ctx:
            result = ctx.evaluate(
                "window.addEventListener('load', function(){})"
            )
        assert result is None

    def test_d15_realistic_framework_snippet(
        self, _require_quickjs: None, _doc_with_div: Document
    ) -> None:
        """Realistic JS snippet: querySelector + addEventListener + setAttribute chain.

        This simulates a common framework bootstrap pattern:
        - Query an element
        - Attach a click handler (no-op stub)
        - Set an initialization attribute
        - Return the attribute

        All must succeed without error; the Python DOM must see the mutation.
        """
        from aspose_html.css import select
        from aspose_html.js import JSContext

        elements = select(_doc_with_div, "div", first_only=True)
        el = elements[0]

        snippet = (
            "(function(){"
            "  var el = document.querySelector('div');"
            "  el.addEventListener('click', function() {"
            "    el.setAttribute('data-clicked', '1');"
            "  });"
            "  el.setAttribute('data-init', 'true');"
            "  return el.getAttribute('data-init');"
            "})()"
        )

        with JSContext(_doc_with_div) as ctx:
            result = ctx.evaluate(snippet)

        # JS must return the value it just set
        assert result == "true"

        # Python DOM must see the mutation from JS
        assert el.get_attribute("data-init") == "true"


# ===========================================================================
# Group E — Doctest sweep
# ===========================================================================


class TestGroupEDoctestSweep:
    """Verify that module-level doctests pass for  modified modules.

    Each test runs pytest --doctest-modules on the target file as a subprocess
    so that import guards do not interfere with the parent process.
    """

    @staticmethod
    def _run_doctest(module_path: str) -> None:
        """Run pytest --doctest-modules on *module_path* and assert zero failures."""
        env = {**os.environ, "PYTHONPATH": "src"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--doctest-modules",
                module_path,
                "-q",
                "--tb=short",
                "--no-header",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env=env,
        )
        assert result.returncode == 0, (
            f"Doctest failures in {module_path}:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    def test_e16_window_module_doctests(self) -> None:
        """pytest --doctest-modules passes on src/aspose_html/dom/_window.py."""
        self._run_doctest("src/aspose_html/dom/_window.py")

    def test_e17_style_module_doctests(self) -> None:
        """pytest --doctest-modules passes on src/aspose_html/dom/_style.py."""
        self._run_doctest("src/aspose_html/dom/_style.py")

    def test_e18_stylesheet_module_doctests(self) -> None:
        """pytest --doctest-modules passes on src/aspose_html/cssom/_stylesheet.py."""
        self._run_doctest("src/aspose_html/cssom/_stylesheet.py")

    def test_e19_js_package_doctests(self) -> None:
        """pytest --doctest-modules passes on src/aspose_html/js/ (skip if no quickjs).

        When quickjs is absent the subprocess reports skips, not failures —
        the test passes either way.
        """
        if not _QUICKJS_AVAILABLE:
            pytest.skip("quickjs not installed — js/ doctest sweep skipped")
        self._run_doctest("src/aspose_html/js/")
