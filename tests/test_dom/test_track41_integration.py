"""Track 41 integration hardening tests (BACK-179 / SPEC-096 / ADR-162).

Cross-component integration checks for BACK-175..BACK-178.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from aspose_html import URL
from aspose_html.cssom import CSSImportRule, CSSStyleSheet
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Group A — Document base URI selection/fallback
# ---------------------------------------------------------------------------


def test_group_a_document_base_uri_first_parseable_wins() -> None:
    doc = HTMLDocument.parse(
        "<html><head>"
        "<base href='http://%'>"
        "<base href='assets/'>"
        "</head><body></body></html>",
        base_url="https://example.com/root/page.html",
    )
    assert doc.base_uri == "https://example.com/root/assets/"


def test_group_a_document_base_uri_falls_back_without_base() -> None:
    doc = HTMLDocument.parse(
        "<html><head></head><body></body></html>",
        base_url="https://example.com/fallback/",
    )
    assert doc.base_uri == doc.url


# ---------------------------------------------------------------------------
# Group B — Anchor decomposition on Document.base_uri
# ---------------------------------------------------------------------------


def test_group_b_anchor_relative_decomposition_uses_document_base_uri() -> None:
    doc = HTMLDocument.parse(
        "<html><head><base href='https://cdn.example.com/static/'></head>"
        "<body><a id='a' href='img/logo.svg?x=1#hash'>logo</a></body></html>",
        base_url="https://app.example.com/root/index.html",
    )
    a = doc.get_element_by_id("a")
    assert a is not None

    assert a.protocol == "https:"
    assert a.host == "cdn.example.com"
    assert a.pathname == "/static/img/logo.svg"
    assert a.search == "?x=1"
    assert a.hash == "#hash"
    assert a.origin == "https://cdn.example.com"


# ---------------------------------------------------------------------------
# Group C — CSS @import resolved/raw href behavior
# ---------------------------------------------------------------------------


def test_group_c_css_import_rule_keeps_raw_href_and_resolves_against_base() -> None:
    sheet = CSSStyleSheet.from_text(
        '@import "css/reset.css" screen',
        href="https://example.com/assets/site.css",
    )
    rule = sheet.css_rules[0]
    assert isinstance(rule, CSSImportRule)
    assert rule.href == "css/reset.css"
    assert rule.resolved_href == "https://example.com/assets/css/reset.css"
    assert rule.media == "screen"


# ---------------------------------------------------------------------------
# Group D — URL.can_parse probes
# ---------------------------------------------------------------------------


def test_group_d_url_can_parse_matches_constructor_outcomes() -> None:
    cases = [
        ("https://example.com/p", None, True),
        ("http://%", None, False),
        ("child", "https://example.com/root/", True),
    ]
    for raw, base, expected in cases:
        assert URL.can_parse(raw, base=base) is expected


# ---------------------------------------------------------------------------
# Group E — End-to-end base mutation scenario
# ---------------------------------------------------------------------------


def test_group_e_dynamic_base_mutation_recoordinates_anchor_css_url_layers() -> None:
    doc = HTMLDocument.parse(
        "<html><head><base id='b' href='https://one.example/assets/'></head>"
        "<body><a id='a' href='img/pic.png'>link</a></body></html>",
        base_url="https://origin.example/app/index.html",
    )
    base_el = doc.get_element_by_id("b")
    anchor = doc.get_element_by_id("a")
    assert base_el is not None
    assert anchor is not None

    assert doc.base_uri == "https://one.example/assets/"
    assert anchor.href == "https://one.example/assets/img/pic.png"
    assert URL.can_parse(anchor.get_attribute("href"), base=doc.base_uri) is True

    sheet = CSSStyleSheet.from_text('@import "theme.css"', href=doc.base_uri)
    import_rule = sheet.css_rules[0]
    assert isinstance(import_rule, CSSImportRule)
    assert import_rule.resolved_href == "https://one.example/assets/theme.css"

    base_el.href = "https://two.example/newbase/"
    assert doc.base_uri == "https://two.example/newbase/"
    assert anchor.href == "https://two.example/newbase/img/pic.png"
    assert URL.can_parse(anchor.get_attribute("href"), base=doc.base_uri) is True

    sheet2 = CSSStyleSheet.from_text('@import "theme.css"', href=doc.base_uri)
    import_rule2 = sheet2.css_rules[0]
    assert isinstance(import_rule2, CSSImportRule)
    assert import_rule2.resolved_href == "https://two.example/newbase/theme.css"


# ---------------------------------------------------------------------------
# Group F — Doctest sweep for touched public modules
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    [
        "src/aspose_html/dom/_document.py",
        "src/aspose_html/dom/html/_elements.py",
        "src/aspose_html/cssom/_rules.py",
        "src/aspose_html/url/_url.py",
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
