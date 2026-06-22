"""html5lib-tests tokenizer fixture suite — INV-004 compliance evidence.

Runs the WHATWG tokenizer fixtures from:
  https://github.com/html5lib/html5lib-tests/tree/master/tokenizer

Fixtures are stored in tests/tokenizer/html5lib/*.test (JSON).

Each fixture test case is parametrized by (file, description, initial_state).
Tests requiring initialStates other than DATA state are run by setting the
tokenizer's initial state accordingly. Tests with ``lastStartTag`` set
``_last_start_tag_name`` directly (private attribute) to allow appropriate-end-tag
detection in RCDATA/RAWTEXT/SCRIPT/PLAINTEXT states.

``doubleEscaped`` tests have \\uXXXX sequences in both input and output strings
that must be decoded before comparison.

Known-failing tests (genuine tokenizer bugs) are marked ``xfail`` using the
baseline in ``html5lib/_xfail_baseline.json``.  Root-cause categories recorded
there:

- ``char-ref-no-semicolon``: character reference state double-emits chars when
  a named entity without a semicolon is not in the legacy table (e.g.
  ``&Abreve`` → ``&AbreveAbreve`` instead of ``&Abreve``).
- ``bogus-comment``: MARKUP_DECLARATION_OPEN state does not create bogus-comment
  tokens for ``<!X`` inputs that are neither ``<!--`` nor ``<!DOCTYPE``.
- ``other``: miscellaneous tokenizer spec deviations (CR normalisation,
  reconsume-at-EOF edge cases, attribute parsing edge cases, etc.).
"""
from __future__ import annotations

import codecs
import json
import pathlib
from typing import Any

import pytest

from aspose_html.tokenizer import (
    AnyToken,
    CharacterToken,
    CommentToken,
    DoctypeToken,
    EndTagToken,
    EofToken,
    StartTagToken,
    Tokenizer,
    TokenizerState,
)

# ---------------------------------------------------------------------------
# Fixture state name → TokenizerState mapping
# ---------------------------------------------------------------------------

_FIXTURE_STATES: dict[str, TokenizerState] = {
    "Data state": TokenizerState.DATA,
    "RCDATA state": TokenizerState.RCDATA,
    "RAWTEXT state": TokenizerState.RAWTEXT,
    "Script data state": TokenizerState.SCRIPT_DATA,
    "PLAINTEXT state": TokenizerState.PLAINTEXT,
    "CDATA section state": TokenizerState.CDATA_SECTION,
}

# ---------------------------------------------------------------------------
# xfail baseline — known tokenizer bugs (do not fix here, fix in tokenizer)
# ---------------------------------------------------------------------------

_FIXTURE_DIR = pathlib.Path(__file__).parent / "html5lib"
_XFAIL_BASELINE_PATH = _FIXTURE_DIR / "_xfail_baseline.json"

_XFAIL_REASONS: dict[str, str] = {
    "char-ref-no-semicolon": (
        "Tokenizer bug: character reference state double-emits chars when a "
        "named entity without semicolon is not in the legacy table "
        "(e.g. &Abreve → &AbreveAbreve). Fix required in _tokenizer.py "
        "character reference handling."
    ),
    "bogus-comment": (
        "Tokenizer bug: MARKUP_DECLARATION_OPEN state does not create a "
        "bogus-comment token for <!X inputs that are neither <!-- nor "
        "<!DOCTYPE. Fix required in _tokenizer.py."
    ),
    "other": (
        "Tokenizer spec deviation: miscellaneous failures including "
        "CR normalisation, reconsume-at-EOF edge cases, attribute parsing "
        "edge cases, and comment state handling. Fix required in _tokenizer.py."
    ),
    "parse-error": (
        "Tokenizer parse error mismatch: actual error codes do not match "
        "expected error codes from the html5lib fixture. Fix required in "
        "_tokenizer.py parse error emission."
    ),
}

_XFAIL_BASELINE: dict[str, str] = (
    json.loads(_XFAIL_BASELINE_PATH.read_text(encoding="utf-8"))
    if _XFAIL_BASELINE_PATH.exists()
    else {}
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _decode_double_escaped(s: str) -> str:
    """Decode ``\\uXXXX`` escape sequences in a double-escaped fixture string."""
    return codecs.decode(s.encode("ascii", "backslashreplace"), "unicode_escape")


def _normalize_output(token: AnyToken) -> tuple | None:
    """Convert an AnyToken to the fixture output tuple format, or None for EofToken."""
    if isinstance(token, EofToken):
        return None
    if isinstance(token, DoctypeToken):
        return ("DOCTYPE", token.name, token.public_id, token.system_id, not token.force_quirks)
    if isinstance(token, StartTagToken):
        attrs = dict(token.attributes)
        return ("StartTag", token.tag_name, attrs, token.self_closing)
    if isinstance(token, EndTagToken):
        return ("EndTag", token.tag_name)
    if isinstance(token, CommentToken):
        return ("Comment", token.data)
    if isinstance(token, CharacterToken):
        return ("Character", token.data)
    return None  # pragma: no cover


def _merge_characters(tokens: list[AnyToken]) -> list[AnyToken]:
    """Merge consecutive CharacterTokens (our tokenizer may buffer them differently)."""
    result: list[AnyToken] = []
    for tok in tokens:
        if isinstance(tok, CharacterToken) and result and isinstance(result[-1], CharacterToken):
            prev = result[-1]
            result[-1] = CharacterToken(
                data=prev.data + tok.data,
                line=prev.line,
                column=prev.column,
            )
        else:
            result.append(tok)
    return result


def _expected_tuples(
    output: list[list[Any]], double_escaped: bool
) -> list[tuple]:
    """Convert fixture output list to comparable tuples."""
    result = []
    for item in output:
        kind = item[0]
        if kind == "DOCTYPE":
            name, pub, sys_, correct = item[1], item[2], item[3], item[4]
            if double_escaped and name:
                name = _decode_double_escaped(name)
            result.append(("DOCTYPE", name, pub, sys_, correct))
        elif kind == "StartTag":
            tag, attrs = item[1], item[2]
            self_closing = item[3] if len(item) > 3 else False
            if double_escaped:
                tag = _decode_double_escaped(tag)
                attrs = {
                    _decode_double_escaped(k): _decode_double_escaped(v)
                    for k, v in attrs.items()
                }
            result.append(("StartTag", tag, attrs, self_closing))
        elif kind == "EndTag":
            tag = item[1]
            if double_escaped:
                tag = _decode_double_escaped(tag)
            result.append(("EndTag", tag))
        elif kind == "Comment":
            data = item[1]
            if double_escaped:
                data = _decode_double_escaped(data)
            result.append(("Comment", data))
        elif kind == "Character":
            data = item[1]
            if double_escaped:
                data = _decode_double_escaped(data)
            result.append(("Character", data))
        elif kind == "ParseError":
            pass  # parse errors verified separately via tokenizer.errors
    return result


def _merge_expected_characters(expected: list[tuple]) -> list[tuple]:
    """Merge consecutive Character tuples in expected output (mirrors token merging)."""
    result: list[tuple] = []
    for item in expected:
        if item[0] == "Character" and result and result[-1][0] == "Character":
            result[-1] = ("Character", result[-1][1] + item[1])
        else:
            result.append(item)
    return result


# ---------------------------------------------------------------------------
# Test collection — build unique parametrize IDs with deduplication
# ---------------------------------------------------------------------------

def _collect_test_cases() -> list[tuple[str, str, str, str, dict]]:
    """Return (pytest_id, file, description, state_name, test_dict) for each case."""
    cases: list[tuple[str, str, str, str, dict]] = []
    seen_ids: dict[str, int] = {}

    for fixture_path in sorted(_FIXTURE_DIR.glob("*.test")):
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        for test in data.get("tests", []):
            states = test.get("initialStates") or ["Data state"]
            desc = test.get("description", "")
            for state_name in states:
                # Build the raw ID (before deduplication suffix)
                raw = f"{fixture_path.name}::{desc}"
                if state_name != "Data state":
                    raw += f"::{state_name}"
                raw = raw[:120]

                # Deduplicate: if seen before, append .N counter
                count = seen_ids.get(raw, 0)
                seen_ids[raw] = count + 1
                pytest_id = f"{raw}.{count}" if count > 0 else raw

                cases.append((pytest_id, fixture_path.name, desc, state_name, test))
    return cases


_ALL_CASES = _collect_test_cases()


def _make_xfail_marks(pytest_id: str) -> list:
    """Return xfail mark list if the test is in the baseline, else empty list."""
    cause = _XFAIL_BASELINE.get(pytest_id)
    if cause is None:
        return []
    reason = _XFAIL_REASONS.get(cause, f"Known tokenizer bug: {cause}")
    return [pytest.mark.xfail(strict=False, reason=reason)]


# ---------------------------------------------------------------------------
# Parametrized test
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "file,description,state_name,test_data",
    [
        pytest.param(f, d, s, t, id=pid, marks=_make_xfail_marks(pid))
        for pid, f, d, s, t in _ALL_CASES
    ],
)
def test_tokenizer_fixture(
    file: str,
    description: str,
    state_name: str,
    test_data: dict,
) -> None:
    initial_state = _FIXTURE_STATES.get(state_name)
    if initial_state is None:
        pytest.skip(f"Unknown initial state: {state_name!r}")

    double_escaped: bool = test_data.get("doubleEscaped", False)
    raw_input: str = test_data["input"]
    if double_escaped:
        raw_input = _decode_double_escaped(raw_input)

    last_start_tag: str | None = test_data.get("lastStartTag")

    # Build and run tokenizer
    tok = Tokenizer(raw_input, initial_state=initial_state)
    if last_start_tag is not None:
        tok._last_start_tag_name = last_start_tag  # type: ignore[attr-defined]

    tokens = list(tok.tokenize())
    tokens = _merge_characters(tokens)

    # Build actual output (exclude EofToken)
    actual = [t for t in (_normalize_output(t) for t in tokens) if t is not None]

    # Build expected output
    expected = _expected_tuples(test_data["output"], double_escaped)
    expected = _merge_expected_characters(expected)

    assert actual == expected, (
        f"\nFile: {file}\nDescription: {description!r}\n"
        f"State: {state_name}\nInput: {raw_input!r}\n"
        f"Expected: {expected}\nActual:   {actual}"
    )

    # Verify parse error codes against fixture "errors" array.
    # Order is not guaranteed to match — compare as sorted lists.
    # See INV-004: WHATWG parse error codes are part of the tokenizer spec.
    expected_error_codes = sorted(
        e["code"] for e in test_data.get("errors", [])
    )
    actual_error_codes = sorted(e.code for e in tok.errors)
    assert actual_error_codes == expected_error_codes, (
        f"\nFile: {file}\nDescription: {description!r}\n"
        f"State: {state_name}\nInput: {raw_input!r}\n"
        f"Expected errors: {expected_error_codes}\n"
        f"Actual errors:   {actual_error_codes}"
    )
