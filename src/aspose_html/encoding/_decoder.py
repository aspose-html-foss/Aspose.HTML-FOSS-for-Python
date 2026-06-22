"""Decoding and normalisation — maps WHATWG canonical names to Python codecs."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# WHATWG canonical encoding name → Python codec name.
# Only encodings with a working Python stdlib codec are listed here.
# ---------------------------------------------------------------------------
_CODEC_MAP: dict[str, str] = {
    "utf-8":        "utf-8-sig",   # handles stray BOM gracefully on non-BOM path
    "utf-16-be":    "utf-16-be",
    "utf-16-le":    "utf-16-le",
    "windows-1252": "cp1252",
    "iso-8859-1":   "latin-1",
    "iso-8859-15":  "iso8859-15",
    "gbk":          "gbk",
    "gb18030":      "gb18030",
    "big5":         "big5",
    "shift_jis":    "shift_jis",
    "euc-jp":       "euc_jp",
    "euc-kr":       "euc_kr",
}


class UnsupportedEncodingError(ValueError):
    """Raised when the detected encoding has no Python codec.

    Examples
    --------
    >>> from aspose_html.encoding._decoder import UnsupportedEncodingError
    >>> issubclass(UnsupportedEncodingError, ValueError)
    True
    """


def decode_bytes(
    data: bytes,
    encoding: str,
    *,
    bom_stripped: bool = False,
) -> tuple[str, list[str]]:
    """Decode *data* from *encoding* (WHATWG canonical name).

    Returns a 2-tuple ``(text, parse_errors)`` where *text* is the decoded
    Unicode string and *parse_errors* is a list of human-readable error
    strings (possibly empty).

    Parse errors are recorded for: replacement characters produced by the
    decoder, surrogates (U+D800–U+DFFF), noncharacters
    (U+FDD0–U+FDEF, U+FFFE, U+FFFF and plane equivalents), and disallowed
    control characters (per HTML Living Standard §12.2.3.1).

    The decoded text has CRLF and lone CR normalised to LF (U+000A), as
    required by the HTML Living Standard.

    *bom_stripped* is informational only — it signals that the caller has
    already removed a BOM prefix.  When ``True`` and *encoding* is
    ``"utf-8"``, the plain ``"utf-8"`` codec is used instead of
    ``"utf-8-sig"`` to avoid double-stripping.

    Raises ``UnsupportedEncodingError`` if *encoding* is not in the codec
    map.

    Examples
    --------
    >>> text, errors = decode_bytes(b"caf\\xe9", "windows-1252")
    >>> text
    'caf\\u00e9'
    >>> errors
    []
    """
    if encoding not in _CODEC_MAP:
        raise UnsupportedEncodingError(
            f"Encoding {encoding!r} has no Python codec in this library."
        )

    codec = _CODEC_MAP[encoding]
    # When the BOM has already been stripped by the caller, use the plain
    # utf-8 codec to avoid accidentally stripping a legitimate U+FEFF in
    # the content.
    if bom_stripped and encoding == "utf-8":
        codec = "utf-8"

    text = data.decode(codec, errors="replace")

    # Normalise line endings: CRLF → LF, then lone CR → LF.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Scan for parse errors.
    parse_errors: list[str] = []
    for i, ch in enumerate(text):
        cp = ord(ch)
        if cp == 0xFFFD:
            parse_errors.append(f"decode-error at position {i}")
        elif 0xD800 <= cp <= 0xDFFF:
            parse_errors.append(f"surrogate-in-input at position {i}")
        elif 0xFDD0 <= cp <= 0xFDEF or (cp & 0xFFFF) in (0xFFFE, 0xFFFF):
            parse_errors.append(f"noncharacter-in-input at position {i}")
        elif (
            0x0001 <= cp <= 0x0008
            or cp == 0x000B
            or 0x000E <= cp <= 0x001F
            or cp == 0x007F
        ):
            parse_errors.append(f"control-character-in-input at position {i}")

    return text, parse_errors
