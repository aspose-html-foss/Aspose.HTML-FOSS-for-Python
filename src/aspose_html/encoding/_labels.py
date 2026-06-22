"""WHATWG Encoding Standard §4.1 — label-to-canonical-name table.

AUTO-GENERATED — do not edit by hand.
Regenerate with: python scripts/gen_encoding_labels.py

Source: https://encoding.spec.whatwg.org/encodings.json

This module is data only.  No logic lives here except the public helper
``get_canonical_name()``.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Label → canonical WHATWG encoding name.
#
# Keys   : lowercase label strings (as received from a document or caller).
# Values : canonical WHATWG encoding names (lowercase, as in the spec).
#
# Source : https://encoding.spec.whatwg.org/encodings.json
# ---------------------------------------------------------------------------
WHATWG_LABELS: dict[str, str] = {
    # big5
    'big5': 'big5',
    'big5-hkscs': 'big5',
    'cn-big5': 'big5',
    'csbig5': 'big5',
    'x-x-big5': 'big5',

    # euc-jp
    'cseucpkdfmtjapanese': 'euc-jp',
    'euc-jp': 'euc-jp',
    'x-euc-jp': 'euc-jp',

    # euc-kr
    'cseuckr': 'euc-kr',
    'csksc56011987': 'euc-kr',
    'euc-kr': 'euc-kr',
    'iso-ir-149': 'euc-kr',
    'korean': 'euc-kr',
    'ks_c_5601-1987': 'euc-kr',
    'ks_c_5601-1989': 'euc-kr',
    'ksc5601': 'euc-kr',
    'ksc_5601': 'euc-kr',
    'windows-949': 'euc-kr',

    # gb18030
    'gb18030': 'gb18030',

    # gbk
    'chinese': 'gbk',
    'csgb2312': 'gbk',
    'csiso58gb231280': 'gbk',
    'gb2312': 'gbk',
    'gb_2312': 'gbk',
    'gb_2312-80': 'gbk',
    'gbk': 'gbk',
    'iso-ir-58': 'gbk',
    'x-gbk': 'gbk',

    # ibm866
    '866': 'ibm866',
    'cp866': 'ibm866',
    'csibm866': 'ibm866',
    'ibm866': 'ibm866',

    # iso-2022-jp
    'csiso2022jp': 'iso-2022-jp',
    'iso-2022-jp': 'iso-2022-jp',

    # iso-8859-10
    'csisolatin6': 'iso-8859-10',
    'iso-8859-10': 'iso-8859-10',
    'iso-ir-157': 'iso-8859-10',
    'iso8859-10': 'iso-8859-10',
    'iso885910': 'iso-8859-10',
    'l6': 'iso-8859-10',
    'latin6': 'iso-8859-10',

    # iso-8859-13
    'iso-8859-13': 'iso-8859-13',
    'iso8859-13': 'iso-8859-13',
    'iso885913': 'iso-8859-13',

    # iso-8859-14
    'iso-8859-14': 'iso-8859-14',
    'iso8859-14': 'iso-8859-14',
    'iso885914': 'iso-8859-14',

    # iso-8859-15
    'csisolatin9': 'iso-8859-15',
    'iso-8859-15': 'iso-8859-15',
    'iso8859-15': 'iso-8859-15',
    'iso885915': 'iso-8859-15',
    'iso_8859-15': 'iso-8859-15',
    'l9': 'iso-8859-15',

    # iso-8859-16
    'iso-8859-16': 'iso-8859-16',

    # iso-8859-2
    'csisolatin2': 'iso-8859-2',
    'iso-8859-2': 'iso-8859-2',
    'iso-ir-101': 'iso-8859-2',
    'iso8859-2': 'iso-8859-2',
    'iso88592': 'iso-8859-2',
    'iso_8859-2': 'iso-8859-2',
    'iso_8859-2:1987': 'iso-8859-2',
    'l2': 'iso-8859-2',
    'latin2': 'iso-8859-2',

    # iso-8859-3
    'csisolatin3': 'iso-8859-3',
    'iso-8859-3': 'iso-8859-3',
    'iso-ir-109': 'iso-8859-3',
    'iso8859-3': 'iso-8859-3',
    'iso88593': 'iso-8859-3',
    'iso_8859-3': 'iso-8859-3',
    'iso_8859-3:1988': 'iso-8859-3',
    'l3': 'iso-8859-3',
    'latin3': 'iso-8859-3',

    # iso-8859-4
    'csisolatin4': 'iso-8859-4',
    'iso-8859-4': 'iso-8859-4',
    'iso-ir-110': 'iso-8859-4',
    'iso8859-4': 'iso-8859-4',
    'iso88594': 'iso-8859-4',
    'iso_8859-4': 'iso-8859-4',
    'iso_8859-4:1988': 'iso-8859-4',
    'l4': 'iso-8859-4',
    'latin4': 'iso-8859-4',

    # iso-8859-5
    'csisolatincyrillic': 'iso-8859-5',
    'cyrillic': 'iso-8859-5',
    'iso-8859-5': 'iso-8859-5',
    'iso-ir-144': 'iso-8859-5',
    'iso8859-5': 'iso-8859-5',
    'iso88595': 'iso-8859-5',
    'iso_8859-5': 'iso-8859-5',
    'iso_8859-5:1988': 'iso-8859-5',

    # iso-8859-6
    'arabic': 'iso-8859-6',
    'asmo-708': 'iso-8859-6',
    'csiso88596e': 'iso-8859-6',
    'csiso88596i': 'iso-8859-6',
    'csisolatinarabic': 'iso-8859-6',
    'ecma-114': 'iso-8859-6',
    'iso-8859-6': 'iso-8859-6',
    'iso-8859-6-e': 'iso-8859-6',
    'iso-8859-6-i': 'iso-8859-6',
    'iso-ir-127': 'iso-8859-6',
    'iso8859-6': 'iso-8859-6',
    'iso88596': 'iso-8859-6',
    'iso_8859-6': 'iso-8859-6',
    'iso_8859-6:1987': 'iso-8859-6',

    # iso-8859-7
    'csisolatingreek': 'iso-8859-7',
    'ecma-118': 'iso-8859-7',
    'elot_928': 'iso-8859-7',
    'greek': 'iso-8859-7',
    'greek8': 'iso-8859-7',
    'iso-8859-7': 'iso-8859-7',
    'iso-ir-126': 'iso-8859-7',
    'iso8859-7': 'iso-8859-7',
    'iso88597': 'iso-8859-7',
    'iso_8859-7': 'iso-8859-7',
    'iso_8859-7:1987': 'iso-8859-7',
    'sun_eu_greek': 'iso-8859-7',

    # iso-8859-8
    'csiso88598e': 'iso-8859-8',
    'csisolatinhebrew': 'iso-8859-8',
    'hebrew': 'iso-8859-8',
    'iso-8859-8': 'iso-8859-8',
    'iso-8859-8-e': 'iso-8859-8',
    'iso-ir-138': 'iso-8859-8',
    'iso8859-8': 'iso-8859-8',
    'iso88598': 'iso-8859-8',
    'iso_8859-8': 'iso-8859-8',
    'iso_8859-8:1988': 'iso-8859-8',
    'visual': 'iso-8859-8',

    # iso-8859-8-i
    'csiso88598i': 'iso-8859-8-i',
    'iso-8859-8-i': 'iso-8859-8-i',
    'logical': 'iso-8859-8-i',

    # koi8-r
    'cskoi8r': 'koi8-r',
    'koi': 'koi8-r',
    'koi8': 'koi8-r',
    'koi8-r': 'koi8-r',
    'koi8_r': 'koi8-r',

    # koi8-u
    'koi8-ru': 'koi8-u',
    'koi8-u': 'koi8-u',

    # macintosh
    'csmacintosh': 'macintosh',
    'mac': 'macintosh',
    'macintosh': 'macintosh',
    'x-mac-roman': 'macintosh',

    # replacement
    'csiso2022kr': 'replacement',
    'hz-gb-2312': 'replacement',
    'iso-2022-cn': 'replacement',
    'iso-2022-cn-ext': 'replacement',
    'iso-2022-kr': 'replacement',
    'replacement': 'replacement',

    # shift_jis
    'csshiftjis': 'shift_jis',
    'ms932': 'shift_jis',
    'ms_kanji': 'shift_jis',
    'shift-jis': 'shift_jis',
    'shift_jis': 'shift_jis',
    'sjis': 'shift_jis',
    'windows-31j': 'shift_jis',
    'x-sjis': 'shift_jis',

    # utf-16be
    'unicodefffe': 'utf-16be',
    'utf-16be': 'utf-16be',

    # utf-16le
    'csunicode': 'utf-16le',
    'iso-10646-ucs-2': 'utf-16le',
    'ucs-2': 'utf-16le',
    'unicode': 'utf-16le',
    'unicodefeff': 'utf-16le',
    'utf-16': 'utf-16le',
    'utf-16le': 'utf-16le',

    # utf-8
    'unicode-1-1-utf-8': 'utf-8',
    'unicode11utf8': 'utf-8',
    'unicode20utf8': 'utf-8',
    'utf-8': 'utf-8',
    'utf8': 'utf-8',
    'x-unicode20utf8': 'utf-8',

    # windows-1250
    'cp1250': 'windows-1250',
    'windows-1250': 'windows-1250',
    'x-cp1250': 'windows-1250',

    # windows-1251
    'cp1251': 'windows-1251',
    'windows-1251': 'windows-1251',
    'x-cp1251': 'windows-1251',

    # windows-1252
    'ansi_x3.4-1968': 'windows-1252',
    'ascii': 'windows-1252',
    'cp1252': 'windows-1252',
    'cp819': 'windows-1252',
    'csisolatin1': 'windows-1252',
    'ibm819': 'windows-1252',
    'iso-8859-1': 'windows-1252',
    'iso-ir-100': 'windows-1252',
    'iso8859-1': 'windows-1252',
    'iso88591': 'windows-1252',
    'iso_8859-1': 'windows-1252',
    'iso_8859-1:1987': 'windows-1252',
    'l1': 'windows-1252',
    'latin1': 'windows-1252',
    'us-ascii': 'windows-1252',
    'windows-1252': 'windows-1252',
    'x-cp1252': 'windows-1252',

    # windows-1253
    'cp1253': 'windows-1253',
    'windows-1253': 'windows-1253',
    'x-cp1253': 'windows-1253',

    # windows-1254
    'cp1254': 'windows-1254',
    'csisolatin5': 'windows-1254',
    'iso-8859-9': 'windows-1254',
    'iso-ir-148': 'windows-1254',
    'iso8859-9': 'windows-1254',
    'iso88599': 'windows-1254',
    'iso_8859-9': 'windows-1254',
    'iso_8859-9:1989': 'windows-1254',
    'l5': 'windows-1254',
    'latin5': 'windows-1254',
    'windows-1254': 'windows-1254',
    'x-cp1254': 'windows-1254',

    # windows-1255
    'cp1255': 'windows-1255',
    'windows-1255': 'windows-1255',
    'x-cp1255': 'windows-1255',

    # windows-1256
    'cp1256': 'windows-1256',
    'windows-1256': 'windows-1256',
    'x-cp1256': 'windows-1256',

    # windows-1257
    'cp1257': 'windows-1257',
    'windows-1257': 'windows-1257',
    'x-cp1257': 'windows-1257',

    # windows-1258
    'cp1258': 'windows-1258',
    'windows-1258': 'windows-1258',
    'x-cp1258': 'windows-1258',

    # windows-874
    'dos-874': 'windows-874',
    'iso-8859-11': 'windows-874',
    'iso8859-11': 'windows-874',
    'iso885911': 'windows-874',
    'tis-620': 'windows-874',
    'windows-874': 'windows-874',

    # x-mac-cyrillic
    'x-mac-cyrillic': 'x-mac-cyrillic',
    'x-mac-ukrainian': 'x-mac-cyrillic',

    # x-user-defined
    'x-user-defined': 'x-user-defined',
}


def get_canonical_name(label: str) -> str | None:
    """Return the canonical WHATWG encoding name for *label*, or ``None``.

    The lookup is case-insensitive and strips leading/trailing ASCII whitespace
    per the WHATWG Encoding Standard §4.1.

    Parameters
    ----------
    label:
        An encoding label as it might appear in an HTML document, HTTP header,
        or BOM detection result.

    Returns
    -------
    str | None
        The canonical WHATWG name (e.g. ``"utf-8"``, ``"windows-1252"``) or
        ``None`` if the label is not in the WHATWG table.

    Examples
    --------
    >>> get_canonical_name("UTF-8")
    'utf-8'
    >>> get_canonical_name("latin1")
    'windows-1252'
    >>> get_canonical_name("not-a-real-encoding") is None
    True
    """
    return WHATWG_LABELS.get(label.strip().lower())
