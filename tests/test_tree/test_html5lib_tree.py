"""html5lib tree-construction conformance suite (WHATWG parser algorithm).

Parses ``tests/test_tree/html5lib/*.dat`` fixtures and compares the produced
tree against html5lib's compact ``| ``-indented tree format.

Baseline management:
- Add known-failing cases to ``tests/test_tree/html5lib/_xfail_baseline.json``.
- Keep ``xfail`` strict: when a known failure starts passing, pytest reports
  XPASS so the baseline can be updated.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aspose_html.dom import Document
from aspose_html.html_document import HTMLDocument
from tests.test_tree.html5lib._tree_serialiser import serialise_fragment, serialise_tree
from tests.test_tree.html5lib.conftest import Html5libTreeCase, _parse_dat_file


_FIXTURE_DIR = Path(__file__).parent / "html5lib"
_XFAIL_BASELINE_PATH = _FIXTURE_DIR / "_xfail_baseline.json"
_XFAIL_BASELINE: dict[str, str] = json.loads(_XFAIL_BASELINE_PATH.read_text(encoding="utf-8"))
_ALLOWED_XFAIL_REASONS = {
    "tree-construction-deviation",
    "foreign-content-adjustment-gap",
    "foster-parenting-gap",
    "template-insertion-mode-gap",
    "adoption-agency-gap",
}

_SVG_NS = "http://www.w3.org/2000/svg"
_MATHML_NS = "http://www.w3.org/1998/Math/MathML"


def _build_context_element(context_spec: str):
    doc = Document()
    parts = context_spec.split(maxsplit=1)
    if len(parts) == 1:
        return doc.create_element(parts[0])

    ns_prefix, local_name = parts
    if ns_prefix == "svg":
        return doc.create_element_ns(_SVG_NS, local_name)
    if ns_prefix == "math":
        return doc.create_element_ns(_MATHML_NS, local_name)
    return doc.create_element(local_name)


def _collect_cases() -> list[tuple[str, Html5libTreeCase]]:
    all_cases: list[tuple[str, Html5libTreeCase]] = []
    for path in sorted(_FIXTURE_DIR.glob("*.dat")):
        for index, case in enumerate(_parse_dat_file(path)):
            test_id = f"{path.name}::{index}"
            all_cases.append((test_id, case))
    return all_cases


_ALL_CASES = _collect_cases()


def test_xfail_baseline_reasons_are_stable_categories() -> None:
    for case_id, reason in _XFAIL_BASELINE.items():
        assert isinstance(case_id, str) and "::" in case_id
        assert reason in _ALLOWED_XFAIL_REASONS, (
            f"Unexpected xfail reason category for {case_id!r}: {reason!r}. "
            "Use a stable taxonomy category rather than transient traceback text."
        )


@pytest.mark.parametrize(
    "case_id,case",
    [
        pytest.param(
            case_id,
            case,
            id=case_id,
            marks=([
                pytest.mark.xfail(strict=True, reason=_XFAIL_BASELINE[case_id])
            ] if case_id in _XFAIL_BASELINE else []),
        )
        for case_id, case in _ALL_CASES
    ],
)
def test_html5lib_tree_construction(case_id: str, case: Html5libTreeCase) -> None:
    if case.script_mode == "on":
        pytest.skip("Scripting-enabled html5lib cases are out of scope")

    if case.context:
        ctx = _build_context_element(case.context)
        fragment = HTMLDocument.parse_fragment(case.data, context_element=ctx)
        actual = serialise_fragment(fragment)
    else:
        actual = serialise_tree(HTMLDocument.parse(case.data))

    expected = case.expected_tree.strip()
    assert actual.strip() == expected, (
        f"\nFixture: {case.fixture_file}\nCase: {case_id}\n"
        f"Description: {case.description}\nContext: {case.context!r}\n"
        f"Expected:\n{expected}\n\nActual:\n{actual}"
    )
