"""Public API: ``EncodingDetectionResult`` and ``detect_encoding()``."""
from __future__ import annotations

from dataclasses import dataclass, field

from aspose_html.encoding._bom import sniff_bom
from aspose_html.encoding._decoder import UnsupportedEncodingError, decode_bytes
from aspose_html.encoding._labels import get_canonical_name
from aspose_html.encoding._prescan import prescan_meta_charset


@dataclass(frozen=True)
class EncodingDetectionResult:
    """Result of encoding detection and decoding for an HTML byte stream.

    Attributes
    ----------
    encoding:
        WHATWG canonical encoding name that was used to decode the input
        (e.g. ``"utf-8"``, ``"windows-1252"``).
    text:
        Decoded Unicode string with CRLF and lone CR normalised to LF.
    parse_errors:
        Sequence of parse-error strings encountered during decoding.
        Empty if the input decoded cleanly. These are informational;
        the caller decides whether to surface them.
    confidence:
        One of ``"certain"`` (BOM or caller override), ``"tentative"``
        (prescan or transport metadata), or ``"irrelevant"`` (UTF-8 default).

    Examples
    --------
    >>> import aspose_html.encoding as enc
    >>> result = enc.detect_encoding(b"<p>Hello</p>")
    >>> result.encoding
    'utf-8'
    >>> result.confidence
    'irrelevant'
    """

    encoding: str
    text: str
    parse_errors: tuple[str, ...] = field(default_factory=tuple)
    confidence: str = "irrelevant"


def detect_encoding(
    data: bytes,
    *,
    override_encoding: str | None = None,
) -> EncodingDetectionResult:
    """Detect the character encoding of *data* and return a decoded result.

    Detection follows the WHATWG HTML Living Standard encoding sniff sequence:

    1. BOM sniff (confidence: certain).
    2. Caller-supplied *override_encoding* if provided (confidence: certain).
    3. HTML prescan of first 1024 bytes for ``<meta charset>``
       (confidence: tentative).
    4. Default to UTF-8 (confidence: irrelevant).

    *override_encoding* accepts any WHATWG label (e.g. ``"latin1"``);
    it is normalised to the canonical name before use.

    Parameters
    ----------
    data:
        Raw byte sequence to detect and decode.
    override_encoding:
        Optional encoding label supplied by the transport layer
        (e.g. from an HTTP ``Content-Type`` header). Overrides prescan
        when provided. Must be a valid WHATWG label.

    Returns
    -------
    EncodingDetectionResult

    Raises
    ------
    UnsupportedEncodingError
        If the resolved encoding has no Python codec.
    ValueError
        If *override_encoding* is not a recognised WHATWG label.

    Examples
    --------
    >>> result = detect_encoding(b"\\xef\\xbb\\xbf<p>hi</p>")
    >>> result.encoding
    'utf-8'
    >>> result.confidence
    'certain'

    >>> result = detect_encoding(b"<p>hi</p>", override_encoding="latin1")
    >>> result.encoding
    'windows-1252'
    >>> result.confidence
    'certain'

    >>> result = detect_encoding(b'<meta charset="shift_jis"><p>\\x82\\xa0</p>')
    >>> result.encoding
    'shift_jis'
    >>> result.confidence
    'tentative'
    """
    # Step 1 — BOM sniff.
    bom = sniff_bom(data)
    if bom is not None:
        bom_encoding, bom_length = bom
        text, errors = decode_bytes(data[bom_length:], bom_encoding, bom_stripped=True)
        return EncodingDetectionResult(
            encoding=bom_encoding,
            text=text,
            parse_errors=tuple(errors),
            confidence="certain",
        )

    # Step 2 — caller-supplied override.
    if override_encoding is not None:
        canonical = get_canonical_name(override_encoding)
        if canonical is None:
            raise ValueError(f"Unrecognised encoding label: {override_encoding!r}")
        text, errors = decode_bytes(data, canonical)
        return EncodingDetectionResult(
            encoding=canonical,
            text=text,
            parse_errors=tuple(errors),
            confidence="certain",
        )

    # Step 3 — HTML prescan.
    prescan_result = prescan_meta_charset(data)
    if prescan_result is not None:
        text, errors = decode_bytes(data, prescan_result)
        return EncodingDetectionResult(
            encoding=prescan_result,
            text=text,
            parse_errors=tuple(errors),
            confidence="tentative",
        )

    # Step 4 — default UTF-8.
    text, errors = decode_bytes(data, "utf-8")
    return EncodingDetectionResult(
        encoding="utf-8",
        text=text,
        parse_errors=tuple(errors),
        confidence="irrelevant",
    )
