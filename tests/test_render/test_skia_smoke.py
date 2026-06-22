"""Skia rendering backend smoke test — M7.1 (SPEC-168 / ADR-314 §1).

First M7 conformance evidence: confirm the optional ``skia-python`` native
wheel loads and can emit a one-page PDF. When ``skia-python`` is not
installed the whole module is skipped with a clear reason, matching the
project's optional-native-dependency pattern (cf. ``quickjs`` in M6).
"""
from __future__ import annotations

import pytest

# Skip the entire module when skia-python is not installed (AC-19).
skia = pytest.importorskip("skia", reason="skia-python not installed")


def test_skia_emits_one_page_pdf() -> None:
    """A 1-page Skia PDF starts with the ``%PDF-`` magic byte sequence.

    Paints a 1x1 black rectangle on a single US-Letter (612x792 pt) page,
    closes the document, and asserts the resulting bytes are a non-empty
    PDF stream.
    """
    stream = skia.DynamicMemoryWStream()
    document = skia.PDF.MakeDocument(stream)
    canvas = document.beginPage(612, 792)
    paint = skia.Paint(Color=skia.ColorBLACK)
    canvas.drawRect(skia.Rect.MakeXYWH(0, 0, 1, 1), paint)
    document.endPage()
    document.close()

    data = bytes(stream.detachAsData())

    assert isinstance(data, bytes)
    assert data, "Skia produced an empty PDF byte stream"
    assert data.startswith(b"%PDF-"), f"unexpected PDF prefix: {data[:8]!r}"
