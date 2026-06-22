"""Unit tests for the W3C Selectors fixture loader (ADR-253, BACK-275).

Covers:
- Valid fixture round-trip: load → verify case count and field values.
- Missing required field raises ValueError.
- Empty ``cases`` array returns an empty list without error.
- ``collect_all_w3c_cases`` returns deterministically sorted case list.
- ``load_xfail_baseline`` returns {} when file is absent.
"""
from __future__ import annotations

import json
import pathlib
import tempfile
from typing import Any

import pytest

from tests.test_css.w3c.conftest import (
    W3cSelectorCase,
    collect_all_w3c_cases,
    load_w3c_fixture_file,
    load_xfail_baseline,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_fixture(dirpath: pathlib.Path, filename: str, data: Any) -> pathlib.Path:
    """Write *data* as JSON to *dirpath/filename* and return the path."""
    path = dirpath / filename
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


_VALID_CASE: dict = {
    "selector": "a[href]",
    "html": "<a id='a1' href='#'>link</a><a id='a2'>no-href</a>",
    "scope": None,
    "targets": ["#a1"],
    "should_match": True,
    "notes": "Attribute presence selector",
}

_VALID_FIXTURE: dict = {
    "group": "level3-attribute-selectors",
    "cases": [_VALID_CASE],
}


# ---------------------------------------------------------------------------
# load_w3c_fixture_file — valid round-trip
# ---------------------------------------------------------------------------


def test_load_single_case_returns_one_item(tmp_path: pathlib.Path) -> None:
    path = _write_fixture(tmp_path, "test.json", _VALID_FIXTURE)
    cases = load_w3c_fixture_file(path)
    assert len(cases) == 1


def test_load_single_case_field_values(tmp_path: pathlib.Path) -> None:
    path = _write_fixture(tmp_path, "test.json", _VALID_FIXTURE)
    case = load_w3c_fixture_file(path)[0]
    assert case.fixture_file == "test.json"
    assert case.group == "level3-attribute-selectors"
    assert case.case_id == "test.json::level3-attribute-selectors::0"
    assert case.selector == "a[href]"
    assert case.html == "<a id='a1' href='#'>link</a><a id='a2'>no-href</a>"
    assert case.scope is None
    assert case.targets == ["#a1"]
    assert case.should_match is True
    assert case.notes == "Attribute presence selector"


def test_load_multiple_cases_index_in_case_id(tmp_path: pathlib.Path) -> None:
    fixture: dict = {
        "group": "grp",
        "cases": [
            {"selector": "p", "html": "<p/>", "targets": [], "should_match": True},
            {"selector": "a", "html": "<a/>", "targets": [], "should_match": False},
        ],
    }
    path = _write_fixture(tmp_path, "multi.json", fixture)
    cases = load_w3c_fixture_file(path)
    assert len(cases) == 2
    assert cases[0].case_id == "multi.json::grp::0"
    assert cases[1].case_id == "multi.json::grp::1"


def test_load_optional_fields_use_defaults(tmp_path: pathlib.Path) -> None:
    """scope defaults to None, notes defaults to empty string."""
    fixture: dict = {
        "group": "g",
        "cases": [
            {"selector": "p", "html": "<p/>", "targets": [], "should_match": True}
        ],
    }
    path = _write_fixture(tmp_path, "defaults.json", fixture)
    case = load_w3c_fixture_file(path)[0]
    assert case.scope is None
    assert case.notes == ""


def test_load_scope_preserved_when_present(tmp_path: pathlib.Path) -> None:
    fixture: dict = {
        "group": "g",
        "cases": [
            {
                "selector": "p",
                "html": "<div id='root'><p/></div>",
                "scope": "#root",
                "targets": [],
                "should_match": True,
            }
        ],
    }
    path = _write_fixture(tmp_path, "scoped.json", fixture)
    case = load_w3c_fixture_file(path)[0]
    assert case.scope == "#root"


def test_case_is_frozen(tmp_path: pathlib.Path) -> None:
    """W3cSelectorCase is a frozen dataclass — attributes cannot be mutated."""
    path = _write_fixture(tmp_path, "test.json", _VALID_FIXTURE)
    case = load_w3c_fixture_file(path)[0]
    with pytest.raises(AttributeError):
        case.selector = "div"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# load_w3c_fixture_file — empty cases array
# ---------------------------------------------------------------------------


def test_empty_cases_array_returns_empty_list(tmp_path: pathlib.Path) -> None:
    fixture: dict = {"group": "g", "cases": []}
    path = _write_fixture(tmp_path, "empty.json", fixture)
    assert load_w3c_fixture_file(path) == []


# ---------------------------------------------------------------------------
# load_w3c_fixture_file — missing required fields raise ValueError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("missing_field", ["selector", "html", "targets", "should_match"])
def test_missing_required_field_raises_value_error(
    tmp_path: pathlib.Path, missing_field: str
) -> None:
    bad_case = {k: v for k, v in _VALID_CASE.items() if k != missing_field}
    fixture: dict = {"group": "g", "cases": [bad_case]}
    path = _write_fixture(tmp_path, "bad.json", fixture)
    with pytest.raises(ValueError, match=missing_field):
        load_w3c_fixture_file(path)


def test_value_error_message_includes_index_and_filename(tmp_path: pathlib.Path) -> None:
    bad_case = {"html": "<p/>", "targets": [], "should_match": True}  # missing selector
    fixture: dict = {"group": "g", "cases": [bad_case]}
    path = _write_fixture(tmp_path, "named.json", fixture)
    with pytest.raises(ValueError, match="named.json") as exc_info:
        load_w3c_fixture_file(path)
    assert "0" in str(exc_info.value)


# ---------------------------------------------------------------------------
# collect_all_w3c_cases — sorting and baseline exclusion
# ---------------------------------------------------------------------------


def test_collect_all_w3c_cases_deterministic_order(tmp_path: pathlib.Path) -> None:
    """Result is sorted by case_id regardless of file system order."""
    fixture_z: dict = {
        "group": "zzz",
        "cases": [{"selector": "span", "html": "<span/>", "targets": [], "should_match": True}],
    }
    fixture_a: dict = {
        "group": "aaa",
        "cases": [{"selector": "div", "html": "<div/>", "targets": [], "should_match": True}],
    }
    _write_fixture(tmp_path, "z-file.json", fixture_z)
    _write_fixture(tmp_path, "a-file.json", fixture_a)
    cases = collect_all_w3c_cases(tmp_path)
    assert len(cases) == 2
    # Sorted by case_id — "a-file.json::aaa::0" < "z-file.json::zzz::0"
    assert cases[0].case_id < cases[1].case_id


def test_collect_all_w3c_cases_excludes_xfail_baseline(tmp_path: pathlib.Path) -> None:
    """_xfail_baseline.json must never be loaded as fixture cases."""
    _write_fixture(tmp_path, "_xfail_baseline.json", {"some-case-id": "reason"})
    fixture: dict = {
        "group": "g",
        "cases": [{"selector": "p", "html": "<p/>", "targets": [], "should_match": True}],
    }
    _write_fixture(tmp_path, "real.json", fixture)
    cases = collect_all_w3c_cases(tmp_path)
    assert len(cases) == 1
    assert cases[0].fixture_file == "real.json"


def test_collect_all_w3c_cases_empty_dir(tmp_path: pathlib.Path) -> None:
    assert collect_all_w3c_cases(tmp_path) == []


def test_collect_all_w3c_cases_aggregates_multiple_files(tmp_path: pathlib.Path) -> None:
    for i in range(3):
        fixture: dict = {
            "group": f"g{i}",
            "cases": [
                {
                    "selector": "p",
                    "html": "<p/>",
                    "targets": [],
                    "should_match": True,
                }
                for _ in range(2)
            ],
        }
        _write_fixture(tmp_path, f"file{i}.json", fixture)
    cases = collect_all_w3c_cases(tmp_path)
    assert len(cases) == 6


# ---------------------------------------------------------------------------
# load_xfail_baseline
# ---------------------------------------------------------------------------


def test_load_xfail_baseline_absent_returns_empty(tmp_path: pathlib.Path) -> None:
    assert load_xfail_baseline(tmp_path) == {}


def test_load_xfail_baseline_empty_file_returns_empty(tmp_path: pathlib.Path) -> None:
    (tmp_path / "_xfail_baseline.json").write_text("{}", encoding="utf-8")
    assert load_xfail_baseline(tmp_path) == {}


def test_load_xfail_baseline_returns_mapping(tmp_path: pathlib.Path) -> None:
    baseline = {
        "selectors-level3.json::level3-pseudo-classes::7": "nth-child-argument-parsing-edge",
        "selectors-level4-pseudoclasses.json::level4-has::3": "has-with-complex-argument-gap",
    }
    _write_fixture(tmp_path, "_xfail_baseline.json", baseline)
    result = load_xfail_baseline(tmp_path)
    assert result == baseline


def test_load_xfail_baseline_whitespace_only_file_returns_empty(tmp_path: pathlib.Path) -> None:
    (tmp_path / "_xfail_baseline.json").write_text("   \n", encoding="utf-8")
    assert load_xfail_baseline(tmp_path) == {}


# ---------------------------------------------------------------------------
# W3cSelectorCase dataclass shape
# ---------------------------------------------------------------------------


def test_w3c_selector_case_has_all_fields() -> None:
    case = W3cSelectorCase(
        fixture_file="f.json",
        group="g",
        case_id="f.json::g::0",
        selector="p",
        html="<p/>",
        scope=None,
        targets=[],
        should_match=True,
        notes="",
    )
    assert case.fixture_file == "f.json"
    assert case.group == "g"
    assert case.case_id == "f.json::g::0"
    assert case.selector == "p"
    assert case.scope is None
    assert case.targets == []
    assert case.should_match is True
    assert case.notes == ""
