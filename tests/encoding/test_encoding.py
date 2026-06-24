"""Tests for  — Encoding Detection and Input Preprocessing.

All acceptance criteria from  and  are covered here.
"""
from __future__ import annotations

import doctest
import importlib

import pytest

import aspose_html.encoding as enc
from aspose_html.encoding._bom import sniff_bom
from aspose_html.encoding._decoder import UnsupportedEncodingError, _CODEC_MAP, decode_bytes
from aspose_html.encoding._labels import WHATWG_LABELS, get_canonical_name
from aspose_html.encoding._prescan import prescan_meta_charset
from aspose_html.encoding.detection import EncodingDetectionResult, detect_encoding


# ---------------------------------------------------------------------------
# BOM detection  (FR-1, AC-2, AC-3)
# ---------------------------------------------------------------------------

def test_bom_utf8():
    result = detect_encoding(b"\xef\xbb\xbf<p>x</p>")
    assert result.encoding == "utf-8"
    assert result.confidence == "certain"
    # BOM bytes must not appear in decoded text
    assert "\ufeff" not in result.text
    assert result.text == "<p>x</p>"


def test_bom_utf16_le():
    payload = "<p>x</p>".encode("utf-16-le")
    data = b"\xff\xfe" + payload
    result = detect_encoding(data)
    assert result.encoding == "utf-16-le"
    assert result.confidence == "certain"


def test_bom_utf16_be():
    payload = "<p>x</p>".encode("utf-16-be")
    data = b"\xfe\xff" + payload
    result = detect_encoding(data)
    assert result.encoding == "utf-16-be"
    assert result.confidence == "certain"


def test_bom_overrides_prescan():
    # UTF-8 BOM present AND a windows-1252 meta charset in first 1024 bytes.
    body = b'<meta charset="windows-1252"><p>hi</p>'
    data = b"\xef\xbb\xbf" + body
    result = detect_encoding(data)
    # BOM must win.
    assert result.encoding == "utf-8"
    assert result.confidence == "certain"


# ---------------------------------------------------------------------------
# Prescan  (FR-2, AC-4)
# ---------------------------------------------------------------------------

def test_prescan_meta_charset_double_quote():
    assert prescan_meta_charset(b'<meta charset="windows-1252">') == "windows-1252"


def test_prescan_meta_charset_single_quote():
    assert prescan_meta_charset(b"<meta charset='utf-8'>") == "utf-8"


def test_prescan_http_equiv():
    data = b'<meta http-equiv="Content-Type" content="text/html; charset=gbk">'
    assert prescan_meta_charset(data) == "gbk"


def test_prescan_limit_1024():
    # <meta charset> appears at byte 1025 — must NOT be detected.
    padding = b" " * 1024
    data = padding + b'<meta charset="windows-1252">'
    assert prescan_meta_charset(data) is None


def test_prescan_no_charset():
    assert prescan_meta_charset(b"<html><body>") is None


# ---------------------------------------------------------------------------
# Override encoding  (FR-3, AC-5)
# ---------------------------------------------------------------------------

def test_override_latin1_maps_to_windows1252():
    result = detect_encoding(b"<p>hello</p>", override_encoding="latin1")
    assert result.encoding == "windows-1252"
    assert result.confidence == "certain"


def test_override_invalid_label():
    with pytest.raises(ValueError):
        detect_encoding(b"<p>hello</p>", override_encoding="not-real")


# ---------------------------------------------------------------------------
# Default fallback  (FR-4, AC-1, AC-6)
# ---------------------------------------------------------------------------

def test_default_utf8():
    result = detect_encoding(b"<p>Hello, world!</p>")
    assert result.encoding == "utf-8"
    assert result.confidence == "irrelevant"


def test_empty_bytes():
    result = detect_encoding(b"")
    assert result.encoding == "utf-8"
    assert result.text == ""
    # No exception raised.


# ---------------------------------------------------------------------------
# Label normalisation  (FR-5)
# ---------------------------------------------------------------------------

def test_label_case_insensitive():
    assert get_canonical_name("UTF-8") == "utf-8"


def test_label_whitespace():
    assert get_canonical_name("  windows-1252  ") == "windows-1252"


def test_label_aliases():
    # At least 5 aliases verified against their documented canonical names.
    cases = [
        ("latin1",        "windows-1252"),
        ("iso-8859-1",    "windows-1252"),
        ("us-ascii",      "windows-1252"),
        ("shift-jis",     "shift_jis"),
        ("euc-kr",        "euc-kr"),
        ("csbig5",        "big5"),
        ("gb2312",        "gbk"),
    ]
    for label, expected in cases:
        assert get_canonical_name(label) == expected, (
            f"Expected {label!r} → {expected!r}, "
            f"got {get_canonical_name(label)!r}"
        )


# ---------------------------------------------------------------------------
# Decoding  (FR-6, AC-9)
# ---------------------------------------------------------------------------

def test_decode_windows1252_non_ascii():
    text, errors = decode_bytes(b"caf\xe9", "windows-1252")
    assert text == "caf\u00e9"
    assert errors == []


def test_decode_gbk():
    original = "你好"
    gbk_bytes = original.encode("gbk")
    text, errors = decode_bytes(gbk_bytes, "gbk")
    assert text == original
    assert errors == []


def test_decode_shift_jis():
    original = "テスト"
    sjis_bytes = original.encode("shift_jis")
    text, errors = decode_bytes(sjis_bytes, "shift_jis")
    assert text == original
    assert errors == []


# ---------------------------------------------------------------------------
# Normalisation  (FR-7, AC-7)
# ---------------------------------------------------------------------------

def test_crlf_normalised():
    data = "line1\r\nline2\r\nline3".encode("utf-8")
    result = detect_encoding(data)
    assert "\r" not in result.text
    assert result.text == "line1\nline2\nline3"


def test_lone_cr_normalised():
    data = "line1\rline2".encode("utf-8")
    result = detect_encoding(data)
    assert "\r" not in result.text
    assert result.text == "line1\nline2"


# ---------------------------------------------------------------------------
# Parse error flagging  (FR-8)
# ---------------------------------------------------------------------------

def test_replacement_char_recorded():
    # 0x81 is undefined in cp1252 → produces U+FFFD with errors='replace'.
    text, errors = decode_bytes(b"\x81", "windows-1252")
    assert "\ufffd" in text
    assert any("decode-error" in e for e in errors)


# ---------------------------------------------------------------------------
# Result object  (FR-10, AC-8, AC-10)
# ---------------------------------------------------------------------------

def test_result_has_encoding_attr():
    result = detect_encoding(b"<p>hello</p>")
    assert isinstance(result.encoding, str)
    assert result.encoding


def test_public_api_doctest():
    import aspose_html.encoding.detection as mod
    results = doctest.testmod(mod, verbose=False)
    assert results.failed == 0, f"{results.failed} doctest(s) failed in detection.py"


# ---------------------------------------------------------------------------
# Supported encodings smoke test  (FR-9)
# ---------------------------------------------------------------------------

_SMOKE_PAYLOADS: dict[str, bytes] = {
    "utf-8":        "Hello".encode("utf-8"),
    "utf-16-be":    "Hi".encode("utf-16-be"),
    "utf-16-le":    "Hi".encode("utf-16-le"),
    "windows-1252": b"Hello",
    "iso-8859-1":   b"Hello",
    "iso-8859-15":  b"Hello",
    "gbk":          "你好".encode("gbk"),
    "gb18030":      "你好".encode("gb18030"),
    "big5":         "你好".encode("big5"),
    "shift_jis":    "テスト".encode("shift_jis"),
    "euc-jp":       "テスト".encode("euc_jp"),
    "euc-kr":       "안녕".encode("euc_kr"),
}


@pytest.mark.parametrize("canonical_name", list(_CODEC_MAP.keys()))
def test_smoke_all_codecs(canonical_name: str):
    payload = _SMOKE_PAYLOADS.get(canonical_name, b"Hello")
    text, errors = decode_bytes(payload, canonical_name)
    assert isinstance(text, str)
    # No unexpected exception raised.


# ---------------------------------------------------------------------------
# Public __init__ exports
# ---------------------------------------------------------------------------

def test_public_exports():
    assert hasattr(enc, "detect_encoding")
    assert hasattr(enc, "EncodingDetectionResult")
    assert hasattr(enc, "UnsupportedEncodingError")


def test_unsupported_encoding_raises():
    with pytest.raises(UnsupportedEncodingError):
        decode_bytes(b"hello", "iso-2022-jp")
