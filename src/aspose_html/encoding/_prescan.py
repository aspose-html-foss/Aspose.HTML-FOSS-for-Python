"""HTML prescan algorithm — WHATWG HTML Living Standard §12.2.3.5.

Scans raw bytes (not decoded text) for a ``<meta charset>`` or
``<meta http-equiv="Content-Type">`` declaration.
"""
from __future__ import annotations

import re

from aspose_html.encoding._labels import get_canonical_name

# ASCII whitespace bytes as a frozenset for fast membership tests.
_ASCII_WS: frozenset[int] = frozenset(b" \t\n\r\x0c")
_SLASH = ord("/")
_GT    = ord(">")
_LT    = ord("<")
_EQ    = ord("=")


def prescan_meta_charset(data: bytes, limit: int = 1024) -> str | None:
    """Scan up to *limit* bytes of raw HTML for a ``<meta charset>`` or
    ``<meta http-equiv="Content-Type">`` declaration.

    Returns the canonical WHATWG encoding name if found, or ``None`` if no
    encoding declaration is present in the scanned region.

    The algorithm follows the WHATWG HTML Living Standard prescan procedure
    exactly: it does not parse HTML — it performs byte-level scanning only.

    Examples
    --------
    >>> prescan_meta_charset(b'<meta charset="utf-8">')
    'utf-8'
    >>> prescan_meta_charset(b'<meta charset="windows-1252">')
    'windows-1252'
    >>> prescan_meta_charset(b'<html><body>') is None
    True
    """
    data = data[:limit]
    pos = 0
    length = len(data)

    while pos < length:
        # Locate the next '<'.
        lt = data.find(b"<", pos)
        if lt == -1:
            return None
        pos = lt + 1
        if pos >= length:
            return None

        byte = data[pos]

        # <!-- ... --> comment
        if byte == ord("!"):
            if data[pos : pos + 3] == b"!--":
                pos += 3
                end = data.find(b"-->", pos)
                if end == -1:
                    return None
                pos = end + 3
                continue
            # <! ... > (DOCTYPE, etc.)
            end = data.find(b">", pos)
            if end == -1:
                return None
            pos = end + 1
            continue

        # <? ... >
        if byte == ord("?"):
            end = data.find(b">", pos)
            if end == -1:
                return None
            pos = end + 1
            continue

        # </tag>
        if byte == _SLASH:
            end = data.find(b">", pos)
            if end == -1:
                return None
            pos = end + 1
            continue

        # Start tag — must begin with ASCII alpha.
        if not (0x41 <= byte <= 0x5A or 0x61 <= byte <= 0x7A):
            continue

        # Collect the tag name.
        tag_start = pos
        while pos < length and data[pos] not in _ASCII_WS and data[pos] != _SLASH and data[pos] != _GT:
            pos += 1
        tag_name = data[tag_start:pos].lower()

        if tag_name != b"meta":
            # Skip to closing '>'.
            end = data.find(b">", pos)
            if end == -1:
                return None
            pos = end + 1
            continue

        # Parse <meta> attribute list.
        attrs: dict[str, str] = {}
        while pos < length:
            # Skip ASCII whitespace and '/'.
            while pos < length and (data[pos] in _ASCII_WS or data[pos] == _SLASH):
                pos += 1
            if pos >= length:
                break
            if data[pos] == _GT:
                pos += 1
                break

            # Attribute name.
            attr_start = pos
            while pos < length and data[pos] not in _ASCII_WS and data[pos] != _SLASH and data[pos] != _GT and data[pos] != _EQ:
                pos += 1
            attr_name = data[attr_start:pos].lower().decode("ascii", errors="replace")

            # Skip whitespace.
            while pos < length and data[pos] in _ASCII_WS:
                pos += 1
            if pos >= length:
                attrs[attr_name] = ""
                break

            if data[pos] != _EQ:
                # Boolean attribute (no value).
                attrs.setdefault(attr_name, "")
                continue

            pos += 1  # consume '='

            # Skip whitespace.
            while pos < length and data[pos] in _ASCII_WS:
                pos += 1
            if pos >= length:
                break

            # Attribute value.
            quote = data[pos]
            if quote in (ord('"'), ord("'")):
                pos += 1
                val_start = pos
                end = data.find(bytes([quote]), pos)
                if end == -1:
                    val = data[val_start:]
                    pos = length
                else:
                    val = data[val_start:end]
                    pos = end + 1
            else:
                val_start = pos
                while pos < length and data[pos] not in _ASCII_WS and data[pos] != _GT:
                    pos += 1
                val = data[val_start:pos]

            attrs[attr_name] = val.decode("ascii", errors="replace").strip()

        # Inspect collected attributes.
        if "charset" in attrs:
            canonical = get_canonical_name(attrs["charset"])
            if canonical is not None:
                return canonical

        if attrs.get("http-equiv", "").lower() == "content-type":
            content = attrs.get("content", "")
            m = re.search(r"charset\s*=\s*([^\s;]+)", content, re.IGNORECASE)
            if m:
                canonical = get_canonical_name(m.group(1))
                if canonical is not None:
                    return canonical

    return None
