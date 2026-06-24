"""BOM sniff algorithm — WHATWG Encoding Standard §10.2."""
from __future__ import annotations

_BOM_UTF8    = b"\xef\xbb\xbf"
_BOM_UTF16BE = b"\xfe\xff"
_BOM_UTF16LE = b"\xff\xfe"


def sniff_bom(data: bytes) -> tuple[str, int] | None:
    """Detect a BOM at the start of *data*.

    Returns a 2-tuple ``(canonical_encoding_name, bom_byte_length)`` if a
    recognised BOM is found, or ``None`` if no BOM is present.

    The caller must strip the returned number of bytes from the start of
    *data* before decoding.

    Examples
    --------
    >>> sniff_bom(b"\\xef\\xbb\\xbf<html>")
    ('utf-8', 3)
    >>> sniff_bom(b"\\xfe\\xff<html>")
    ('utf-16-be', 2)
    >>> sniff_bom(b"\\xff\\xfe<html>")
    ('utf-16-le', 2)
    >>> sniff_bom(b"<html>") is None
    True
    """
    if data[:3] == _BOM_UTF8:
        return ("utf-8", 3)
    if data[:2] == _BOM_UTF16BE:
        return ("utf-16-be", 2)
    if data[:2] == _BOM_UTF16LE:
        return ("utf-16-le", 2)
    return None
