"""Tests for HTMLDocument.load() and Document.save() —  / ."""
from __future__ import annotations

import pathlib

import pytest

from aspose_html.dom import Document
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Load tests
# ---------------------------------------------------------------------------


def test_load_returns_document(tmp_path: pathlib.Path) -> None:
    """load() returns a Document with an HTML root element."""
    html_file = tmp_path / "page.html"
    html_file.write_bytes(b"<p>Hello</p>")
    doc = HTMLDocument.load(html_file)
    assert isinstance(doc, Document)
    assert doc.document_element.tag_name == "HTML"


def test_load_accepts_string_path(tmp_path: pathlib.Path) -> None:
    """load() accepts a plain str path without raising TypeError."""
    html_file = tmp_path / "page.html"
    html_file.write_bytes(b"<p>Hello</p>")
    # Must not raise
    doc = HTMLDocument.load(str(html_file))
    assert isinstance(doc, Document)


def test_load_accepts_pathlib_path(tmp_path: pathlib.Path) -> None:
    """load() accepts a pathlib.Path directly."""
    html_file = tmp_path / "page.html"
    html_file.write_bytes(b"<p>Hello</p>")
    doc = HTMLDocument.load(html_file)
    assert isinstance(doc, Document)


def test_load_file_not_found_raises(tmp_path: pathlib.Path) -> None:
    """load() propagates FileNotFoundError for a missing path."""
    missing = tmp_path / "nonexistent.html"
    with pytest.raises(FileNotFoundError):
        HTMLDocument.load(missing)


def test_load_encoding_detected_from_bytes(tmp_path: pathlib.Path) -> None:
    """load() runs the WHATWG encoding detection pipeline.

    Writing a Windows-1252 byte sequence with a matching <meta charset>
    should yield U+00E9 (é) in the parsed text node.
    """
    html_file = tmp_path / "latin.html"
    # b'\xe9' is 'é' in Windows-1252
    html_file.write_bytes(b'<meta charset="windows-1252"><p>caf\xe9</p>')
    doc = HTMLDocument.load(html_file)
    # Navigate to the <p> body text
    body = doc.body
    assert body is not None
    p_elements = list(doc.get_elements_by_tag_name("p"))
    assert p_elements, "Expected a <p> element"
    text_node = list(p_elements[0].child_nodes)[0]
    assert "é" in text_node.data


def test_load_utf8_bom(tmp_path: pathlib.Path) -> None:
    """load() handles a UTF-8 BOM at the start of the file."""
    html_file = tmp_path / "bom.html"
    # UTF-8 BOM followed by a minimal HTML5 document
    html_file.write_bytes(b"\xef\xbb\xbf<!DOCTYPE html><html></html>")
    doc = HTMLDocument.load(html_file)
    assert doc.document_element.tag_name == "HTML"


# ---------------------------------------------------------------------------
# Save tests
# ---------------------------------------------------------------------------


def test_save_round_trip(tmp_path: pathlib.Path) -> None:
    """save() output can be reloaded and yields equivalent structure."""
    src = "<!DOCTYPE html><html><body><p>Round trip</p></body></html>"
    doc = HTMLDocument.parse(src)
    out_file = tmp_path / "out.html"
    doc.save(out_file)

    content = out_file.read_text(encoding="utf-8")
    assert content.startswith("<!DOCTYPE"), "saved file must start with DOCTYPE"

    # Re-parse the saved file and check structure is preserved
    doc2 = HTMLDocument.parse(content)
    p_elements = list(doc2.get_elements_by_tag_name("p"))
    assert p_elements, "Re-parsed document must contain a <p> element"
    assert p_elements[0].text_content == "Round trip"


def test_save_accepts_string_path(tmp_path: pathlib.Path) -> None:
    """save() accepts a plain str path."""
    doc = HTMLDocument.parse("<p>test</p>")
    out_path = str(tmp_path / "out.html")
    doc.save(out_path)
    assert pathlib.Path(out_path).exists()


def test_save_accepts_pathlib_path(tmp_path: pathlib.Path) -> None:
    """save() accepts a pathlib.Path and writes a non-empty file."""
    doc = HTMLDocument.parse("<p>test</p>")
    out_file = tmp_path / "out.html"
    doc.save(out_file)
    assert out_file.exists()
    assert out_file.stat().st_size > 0


def test_save_explicit_encoding(tmp_path: pathlib.Path) -> None:
    """save() honours the encoding parameter — utf-8-sig starts with BOM."""
    doc = HTMLDocument.parse("<p>café</p>")
    out_file = tmp_path / "out.html"
    doc.save(out_file, encoding="utf-8-sig")
    raw = out_file.read_bytes()
    # UTF-8 BOM is 0xEF 0xBB 0xBF
    assert raw[:3] == b"\xef\xbb\xbf", "File must start with UTF-8 BOM for utf-8-sig"


def test_save_doctype_prefix_present_when_doctype_child_exists(
    tmp_path: pathlib.Path,
) -> None:
    """save() output starts with <!DOCTYPE html> exactly once when the document
    was parsed with a doctype (serialise() emits it; save() does not double it).
    """
    doc = HTMLDocument.parse("<!DOCTYPE html><html><body></body></html>")
    out_file = tmp_path / "out.html"
    doc.save(out_file)
    content = out_file.read_text(encoding="utf-8")

    assert content.lower().startswith("<!doctype html"), (
        "Output must start with <!DOCTYPE html>"
    )
    # Ensure the doctype appears exactly once (not doubled)
    assert content.lower().count("<!doctype") == 1, (
        "DOCTYPE must appear exactly once in the output"
    )


def test_save_doctype_prefix_absent_when_no_doctype_child(
    tmp_path: pathlib.Path,
) -> None:
    """save() prepends '<!DOCTYPE html>\\n' when document has no DocumentType child."""
    # Programmatically create a document with no DocumentType node
    doc = Document()
    html_el = doc.create_element("html")
    body_el = doc.create_element("body")
    p_el = doc.create_element("p")
    p_el.text_content = "test"
    doc.append_child(html_el)
    html_el.append_child(body_el)
    body_el.append_child(p_el)

    out_file = tmp_path / "out.html"
    doc.save(out_file)
    content = out_file.read_text(encoding="utf-8")

    assert content.startswith("<!DOCTYPE html>\n"), (
        "save() must prepend '<!DOCTYPE html>\\n' when no DocumentType is present"
    )


def test_save_default_encoding_is_utf8(tmp_path: pathlib.Path) -> None:
    """save() with no encoding argument writes valid UTF-8."""
    doc = HTMLDocument.parse("<p>café</p>")
    out_file = tmp_path / "out.html"
    doc.save(out_file)
    raw = out_file.read_bytes()
    # Must decode without error as UTF-8 and preserve the accented character
    text = raw.decode("utf-8")
    assert "café" in text


def test_save_creates_or_overwrites_file(tmp_path: pathlib.Path) -> None:
    """save() overwrites an existing file (does not append)."""
    out_file = tmp_path / "out.html"
    # Pre-populate with content that must not appear in the final output
    out_file.write_text("ORIGINAL CONTENT", encoding="utf-8")

    doc = HTMLDocument.parse("<p>New</p>")
    doc.save(out_file)

    content = out_file.read_text(encoding="utf-8")
    assert "ORIGINAL CONTENT" not in content
    assert "New" in content
