"""Character reference resolution for the WHATWG HTML tokeniser.

Implements the lookup and validation logic required by §13.2.5.72–80 of the
WHATWG HTML Living Standard.

This module is an internal helper; its public names are used only by
``_tokenizer.py``.  Do not import from outside the tokenizer package.

See ADR-002, Decision 6.
"""
from __future__ import annotations

from aspose_html.tokenizer._char_ref_data import NAMED_CHAR_REFS

# WHATWG §13.2.5.80 — numeric character reference end state error/replacement
# table.  Maps illegal code points to their replacement (or flags an error).
# Surrogate range [0xD800, 0xDFFF] and code points > 0x10FFFF → U+FFFD.
_REPLACEMENT_CHARS: dict[int, str] = {
    0x00: "\uFFFD",  # null
    0x80: "\u20AC",  # EURO SIGN
    0x82: "\u201A",
    0x83: "\u0192",
    0x84: "\u201E",
    0x85: "\u2026",
    0x86: "\u2020",
    0x87: "\u2021",
    0x88: "\u02C6",
    0x89: "\u2030",
    0x8A: "\u0160",
    0x8B: "\u2039",
    0x8C: "\u0152",
    0x8E: "\u017D",
    0x91: "\u2018",
    0x92: "\u2019",
    0x93: "\u201C",
    0x94: "\u201D",
    0x95: "\u2022",
    0x96: "\u2013",
    0x97: "\u2014",
    0x98: "\u02DC",
    0x99: "\u2122",
    0x9A: "\u0161",
    0x9B: "\u203A",
    0x9C: "\u0153",
    0x9E: "\u017E",
    0x9F: "\u0178",
}

# Noncharacter code points per the WHATWG definition (Unicode noncharacters)
_NONCHARACTERS: frozenset[int] = frozenset(range(0xFDD0, 0xFDF0)) | frozenset(
    c for n in range(0, 17) for c in (0xFFFE + n * 0x10000, 0xFFFF + n * 0x10000)
)


def resolve_named_char_ref(name: str) -> str | None:
    """Look up *name* in the named character reference table.

    Returns the replacement string (one or two Unicode characters) if
    found, or ``None`` if the name is not in the table.

    The lookup is case-sensitive per the WHATWG standard.  The *name*
    parameter is the raw accumulated text between ``&`` and the end of
    the match (which may or may not include a trailing ``;``).

    Parameters
    ----------
    name:
        The entity name as it appears in source, without the leading ``&``.
        May include a trailing ``;`` for well-formed references.

    Examples
    --------
    >>> resolve_named_char_ref('amp;')
    '&'
    >>> resolve_named_char_ref('lt;')
    '<'
    >>> resolve_named_char_ref('AElig;')
    'Æ'
    >>> resolve_named_char_ref('notAName') is None
    True
    """
    return NAMED_CHAR_REFS.get(name)


def resolve_numeric_char_ref(code_point: int) -> tuple[str, list[str]]:
    """Convert a numeric code point to a character, applying WHATWG
    replacement and error rules (§13.2.5.80).

    Returns ``(character, parse_error_codes)`` where ``parse_error_codes``
    is a list of WHATWG error identifier strings (may be empty).

    Handles: null replacement, surrogate replacement, noncharacter
    errors, and the WHATWG §13.2.5.80 numeric character reference
    end state error table.

    Parameters
    ----------
    code_point:
        The integer code point value parsed from ``&#NNN;`` or ``&#xHHH;``.

    Examples
    --------
    >>> resolve_numeric_char_ref(38)
    ('&', [])
    >>> char, errs = resolve_numeric_char_ref(0)
    >>> errs
    ['null-character-reference']
    >>> char, errs = resolve_numeric_char_ref(0xD800)
    >>> errs
    ['surrogate-character-reference']
    """
    errors: list[str] = []

    # §13.2.5.80 step 1: if code_point > 0x10FFFF, parse error
    if code_point > 0x10FFFF:
        errors.append("character-reference-outside-unicode-range")
        return "\uFFFD", errors

    # §13.2.5.80 step 2: if surrogate, parse error
    if 0xD800 <= code_point <= 0xDFFF:
        errors.append("surrogate-character-reference")
        return "\uFFFD", errors

    # §13.2.5.80 step 3: if noncharacter, parse error (but still use the char)
    if code_point in _NONCHARACTERS:
        errors.append("noncharacter-character-reference")
        # Fall through — the code point is still used

    # §13.2.5.80 step 4: if 0x0D or a control character (excluding ASCII whitespace)
    if code_point == 0x0D or (
        0x0001 <= code_point <= 0x001F and code_point not in (0x09, 0x0A, 0x0C)
    ) or (0x007F <= code_point <= 0x009F and code_point not in (0x80,)):
        # Check the replacement table first
        if code_point in _REPLACEMENT_CHARS:
            errors.append("control-character-reference")
            return _REPLACEMENT_CHARS[code_point], errors
        elif 0x007F <= code_point <= 0x009F:
            errors.append("control-character-reference")
            # Fall through to use the code point directly

    # §13.2.5.80 step 5: null character
    if code_point == 0x0000:
        errors.append("null-character-reference")
        return "\uFFFD", errors

    # Use the replacement char from table if available (0x80–0x9F range)
    if code_point in _REPLACEMENT_CHARS:
        errors.append("control-character-reference")
        return _REPLACEMENT_CHARS[code_point], errors

    try:
        char = chr(code_point)
    except (ValueError, OverflowError):
        errors.append("character-reference-outside-unicode-range")
        return "\uFFFD", errors

    return char, errors


def find_named_char_ref_match(candidate: str) -> tuple[str, str] | None:
    """Find the longest matching named character reference for *candidate*.

    Used by the NAMED_CHARACTER_REFERENCE state (§13.2.5.73) to do a
    longest-prefix match.  The candidate is the accumulated text from
    after the ``&``.

    Returns ``(matched_name, replacement)`` for the longest match found,
    or ``None`` if no match exists at all.

    Parameters
    ----------
    candidate:
        The text accumulated so far (without the leading ``&``).

    Examples
    --------
    >>> find_named_char_ref_match('amp;')
    ('amp;', '&')
    >>> find_named_char_ref_match('lt;rest')
    ('lt;', '<')
    >>> find_named_char_ref_match('nope') is None
    True
    """
    best_name: str | None = None
    best_replacement: str | None = None
    # Try all lengths from longest to shortest; stop at first match
    for length in range(len(candidate), 0, -1):
        sub = candidate[:length]
        result = NAMED_CHAR_REFS.get(sub)
        if result is not None:
            best_name = sub
            best_replacement = result
            break
    if best_name is None:
        return None
    return (best_name, best_replacement)  # type: ignore[return-value]
