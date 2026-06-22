"""Track 40 integration hardening tests (BACK-174 / SPEC-095 / ADR-157).

Cross-component integration checks for BACK-168..BACK-173.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from aspose_html.cssom import CSSLayerBlockRule, CSSLayerStatementRule, CSSStyleSheet, CSSSupportsRule
from aspose_html.dom import Document
from aspose_html.dom._exceptions import NotSupportedError
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Group A — HTMLSelectElement IDL
# ---------------------------------------------------------------------------


def test_group_a_selected_index_size_length() -> None:
    doc = Document()
    sel = doc.create_element("select")
    assert sel.selected_index == -1

    opt0 = doc.create_element("option")
    opt1 = doc.create_element("option")
    sel.append_child(opt0)
    sel.append_child(opt1)

    sel.selected_index = 1
    assert not opt0.has_attribute("selected")
    assert opt1.has_attribute("selected")

    sel.size = 4
    assert sel.size == 4
    assert sel.length == sel.options.length == 2


# ---------------------------------------------------------------------------
# Group B — HTMLAnchorElement URL decomposition
# ---------------------------------------------------------------------------


def test_group_b_anchor_decomposition_and_reflections() -> None:
    doc = HTMLDocument.parse(
        "<a id='a' href='https://example.com:8080/path?q=1#frag'>Go</a>"
    )
    a = doc.get_element_by_id("a")
    assert a is not None

    assert a.protocol == "https:"
    assert a.host == "example.com:8080"
    assert a.hostname == "example.com"
    assert a.port == "8080"
    assert a.pathname == "/path"
    assert a.search == "?q=1"
    assert a.hash == "#frag"
    assert a.origin == "https://example.com:8080"

    a.rel = "noopener"
    a.download = "file.txt"
    a.hreflang = "en"
    a.type = "text/html"
    assert a.text == "Go"
    assert a.rel == "noopener"
    assert a.download == "file.txt"
    assert a.hreflang == "en"
    assert a.type == "text/html"


def test_group_b_anchor_unresolvable_href_fallback() -> None:
    a = Document().create_element("a")
    a.href = "http://[::1"
    assert a.protocol == ""
    assert a.host == ""
    assert a.hostname == ""
    assert a.port == ""
    assert a.pathname == ""
    assert a.search == ""
    assert a.hash == ""
    assert a.origin == "null"


# ---------------------------------------------------------------------------
# Group C — @supports cascade participation
# ---------------------------------------------------------------------------


def test_group_c_supports_known_vs_unknown_and_media_coexistence() -> None:
    doc = HTMLDocument.parse("<html><body><div id='d'>x</div></body></html>")
    div = doc.get_element_by_id("d")
    assert div is not None

    sheet = CSSStyleSheet()
    sheet.replace_sync(
        "@media all { div { background-color: yellow } }"
        " @supports (color: red) { div { color: purple } }"
        " @supports (--unknown: x) { div { color: green } }"
    )
    doc.attach_style_sheet(sheet)

    style = div.get_computed_style()
    assert style.get_property_value("background-color") == "yellow"
    assert style.get_property_value("color") == "purple"


def test_group_c_supports_rule_present_in_cssom() -> None:
    sheet = CSSStyleSheet.from_text("@supports (color: red) { div { color: purple } }")
    assert sheet.css_rules.length == 1
    assert isinstance(sheet.css_rules[0], CSSSupportsRule)


# ---------------------------------------------------------------------------
# Group D — @layer stubs
# ---------------------------------------------------------------------------


def test_group_d_layer_rule_types_css_text_and_cascade() -> None:
    css = "@layer base, components; @layer base { p { color: red } }"
    sheet = CSSStyleSheet.from_text(css)
    assert sheet.css_rules.length == 2
    assert isinstance(sheet.css_rules[0], CSSLayerStatementRule)
    assert isinstance(sheet.css_rules[1], CSSLayerBlockRule)
    assert "@layer base, components;" in sheet.css_text
    assert "@layer base" in sheet.css_text

    doc = HTMLDocument.parse("<html><body><p id='p'>x</p></body></html>")
    doc.attach_style_sheet(sheet)
    p = doc.get_element_by_id("p")
    assert p is not None
    assert p.get_computed_style().get_property_value("color") == "red"


# ---------------------------------------------------------------------------
# Group E — Document/Window stubs
# ---------------------------------------------------------------------------


def test_group_e_document_stubs_raise_notsupported_per_adr_155() -> None:
    doc = Document()
    with pytest.raises(NotSupportedError):
        doc.open()
    with pytest.raises(NotSupportedError):
        doc.close()
    with pytest.raises(NotSupportedError):
        doc.write("<p>x</p>")
    with pytest.raises(NotSupportedError):
        doc.writeln("<p>x</p>")


def test_group_e_window_stubs_callable_and_return_none() -> None:
    win = Document().default_view
    assert win.open() is None
    assert win.open("https://example.com", "_self", "noopener") is None
    assert win.close() is None
    assert win.focus() is None
    assert win.blur() is None


# ---------------------------------------------------------------------------
# Group F — Doctest sweep for touched source modules
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    [
        "src/aspose_html/dom/html/_elements.py",
        "src/aspose_html/dom/_cascade.py",
        "src/aspose_html/cssom/_rules.py",
        "src/aspose_html/cssom/_parser.py",
        "src/aspose_html/dom/_document.py",
        "src/aspose_html/dom/_window.py",
    ],
)
def test_group_f_doctest_modules(module_path: str) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--doctest-modules",
            module_path,
            "-q",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"doctest failed for {module_path}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
