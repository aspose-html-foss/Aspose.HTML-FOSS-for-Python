""" integration hardening tests ( /  / ).

Cross-component integration checks for ..:
  Group A — HTMLFormElement action stubs and length: 6 assertions.
  Group B — HTMLSelectElement indexed/named collection API: 7 assertions.
  Group C — HTMLImageElement IDL completeness via parsed HTML + clone: 6 assertions.
  Group D — Document ParentNode properties and active_element: 6 assertions.
  Group E — Doctest sweep for _elements.py and _document.py.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from aspose_html.dom import (
    Document,
    HTMLFormElement,
    HTMLImageElement,
    HTMLInputElement,
    HTMLOptGroupElement,
    HTMLOptionElement,
    HTMLSelectElement,
    NotSupportedError,
)
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Group A — HTMLFormElement action stubs and length ()
# ---------------------------------------------------------------------------


def test_a1_form_submit_raises_not_supported() -> None:
    """A-1: form.submit() raises NotSupportedError in headless mode."""
    doc = Document()
    form = doc.create_element("form")
    assert isinstance(form, HTMLFormElement)
    with pytest.raises(NotSupportedError):
        form.submit()


def test_a2_form_reset_raises_not_supported() -> None:
    """A-2: form.reset() raises NotSupportedError in headless mode."""
    doc = Document()
    form = doc.create_element("form")
    with pytest.raises(NotSupportedError):
        form.reset()


def test_a3_form_request_submit_raises_not_supported() -> None:
    """A-3: form.request_submit() raises NotSupportedError in headless mode."""
    doc = Document()
    form = doc.create_element("form")
    with pytest.raises(NotSupportedError):
        form.request_submit()


def test_a4_form_length_zero_then_three() -> None:
    """A-4: form.length == 0 for empty form; == 3 after adding three <input> elements."""
    doc = Document()
    form = doc.create_element("form")
    assert form.length == 0

    for _ in range(3):
        form.append_child(doc.create_element("input"))
    assert form.length == 3


def test_a5_form_length_matches_elements_count() -> None:
    """A-5: form.length == len(list(form.elements)) after mixed element types."""
    doc = Document()
    form = doc.create_element("form")
    for tag in ("input", "button", "select", "textarea"):
        form.append_child(doc.create_element(tag))
    # <div> is not a listed element — must not affect length
    form.append_child(doc.create_element("div"))
    assert form.length == len(list(form.elements))


def test_a6_parsed_form_length_matches_listed_controls() -> None:
    """A-6: Parsed HTML: doc.forms[0].length equals count of listed controls."""
    doc = HTMLDocument.parse(
        '<form id="f">'
        "<input><button></button><select></select><textarea></textarea>"
        # <p> is NOT a listed form control
        "<p></p>"
        "</form>"
    )
    form = doc.forms[0]
    assert isinstance(form, HTMLFormElement)
    assert form.length == 4


# ---------------------------------------------------------------------------
# Group B — HTMLSelectElement indexed/named collection API ()
# ---------------------------------------------------------------------------


def test_b1_item_returns_first_option_and_none_out_of_range() -> None:
    """B-1: sel.item(0) returns first <option>; sel.item(99) returns None."""
    doc = Document()
    sel = doc.create_element("select")
    opt = doc.create_element("option")
    sel.append_child(opt)

    assert isinstance(sel, HTMLSelectElement)
    assert sel.item(0) is opt
    assert sel.item(99) is None


def test_b2_named_item_finds_by_id_and_returns_none_on_miss() -> None:
    """B-2: named_item('myid') finds option by id; returns None for miss."""
    doc = Document()
    sel = doc.create_element("select")
    opt = doc.create_element("option")
    opt.set_attribute("id", "myid")
    sel.append_child(opt)

    assert sel.named_item("myid") is opt
    assert sel.named_item("nope") is None


def test_b3_add_appends_option_and_collection_is_live() -> None:
    """B-3: sel.add(new_opt) appends; sel.length increases; options is live."""
    doc = Document()
    sel = doc.create_element("select")
    sel.append_child(doc.create_element("option"))
    assert sel.length == 1

    new_opt = doc.create_element("option")
    sel.add(new_opt)
    assert sel.length == 2
    assert sel.item(1) is new_opt


def test_b4_add_with_index_inserts_at_front() -> None:
    """B-4: sel.add(new_opt, 0) inserts at front; sel.item(0) is new_opt."""
    doc = Document()
    sel = doc.create_element("select")
    existing = doc.create_element("option")
    sel.append_child(existing)

    new_opt = doc.create_element("option")
    sel.add(new_opt, 0)
    assert sel.item(0) is new_opt
    assert sel.item(1) is existing


def test_b5_remove_decreases_length_and_collection_is_live() -> None:
    """B-5: sel.remove(0) removes first option; sel.length decreases."""
    doc = Document()
    sel = doc.create_element("select")
    opt1 = doc.create_element("option")
    opt2 = doc.create_element("option")
    sel.append_child(opt1)
    sel.append_child(opt2)
    assert sel.length == 2

    sel.remove(0)
    assert sel.length == 1
    # The remaining option should be opt2
    assert sel.item(0) is opt2


def test_b6_remove_out_of_range_is_noop() -> None:
    """B-6: sel.remove(999) is a no-op; sel.length unchanged."""
    doc = Document()
    sel = doc.create_element("select")
    sel.append_child(doc.create_element("option"))
    assert sel.length == 1

    sel.remove(999)  # must not raise
    assert sel.length == 1


def test_b7_parsed_select_item_and_named_item() -> None:
    """B-7: Parsed HTML select: item() and named_item() work on parsed content."""
    doc = HTMLDocument.parse(
        '<select id="s">'
        '<option id="o1" value="a">Alpha</option>'
        '<option id="o2" value="b">Beta</option>'
        "</select>"
    )
    sel = doc.get_element_by_id("s")
    assert isinstance(sel, HTMLSelectElement)
    assert sel.item(0) is not None
    assert sel.item(1) is not None
    assert sel.item(2) is None
    o1 = sel.named_item("o1")
    assert o1 is not None
    assert o1.get_attribute("value") == "a"


# ---------------------------------------------------------------------------
# Group C — HTMLImageElement IDL completeness ()
# ---------------------------------------------------------------------------


def test_c1_fresh_img_string_properties_are_empty() -> None:
    """C-1: Fresh <img>: srcset, sizes, loading, decoding are empty strings."""
    doc = Document()
    img = doc.create_element("img")
    assert isinstance(img, HTMLImageElement)
    assert img.srcset == ""
    assert img.sizes == ""
    assert img.loading == ""
    assert img.decoding == ""


def test_c2_cross_origin_none_for_fresh_element_and_roundtrip() -> None:
    """C-2: img.cross_origin is None for fresh element; set and read back."""
    doc = Document()
    img = doc.create_element("img")
    assert img.cross_origin is None

    img.cross_origin = "anonymous"
    assert img.cross_origin == "anonymous"

    # Setting to None removes the attribute
    img.cross_origin = None
    assert img.cross_origin is None


def test_c3_is_map_boolean_presence_attribute() -> None:
    """C-3: img.is_map = True sets 'ismap' attribute; img.is_map = False removes it."""
    doc = Document()
    img = doc.create_element("img")
    assert img.is_map is False

    img.is_map = True
    assert img.is_map is True
    assert img.has_attribute("ismap")

    img.is_map = False
    assert img.is_map is False
    assert not img.has_attribute("ismap")


def test_c4_headless_stubs_complete_natural_width_height() -> None:
    """C-4: img.complete is False; natural_width == 0; natural_height == 0."""
    doc = Document()
    img = doc.create_element("img")
    assert img.complete is False
    assert img.natural_width == 0
    assert img.natural_height == 0


def test_c5_parsed_img_properties_reflect_parsed_attributes() -> None:
    """C-5: Parsed <img srcset='img@2x.png 2x' loading='lazy' ismap>: properties reflect attrs."""
    doc = HTMLDocument.parse(
        '<html><body><img id="i" srcset="img@2x.png 2x" loading="lazy" ismap></body></html>'
    )
    img = doc.get_element_by_id("i")
    assert img is not None, "img element not found in parsed document"
    assert isinstance(img, HTMLImageElement)
    assert img.srcset == "img@2x.png 2x"
    assert img.loading == "lazy"
    assert img.is_map is True


def test_c6_clone_node_preserves_img_idl_properties() -> None:
    """C-6: clone_node(True) on <img> preserves srcset, loading, is_map, cross_origin."""
    doc = Document()
    img = doc.create_element("img")
    img.set_attribute("srcset", "img@2x.png 2x")
    img.set_attribute("sizes", "100vw")
    img.set_attribute("loading", "lazy")
    img.cross_origin = "anonymous"
    img.is_map = True

    clone = img.clone_node(True)
    assert isinstance(clone, HTMLImageElement)
    assert clone.srcset == "img@2x.png 2x"
    assert clone.sizes == "100vw"
    assert clone.loading == "lazy"
    assert clone.cross_origin == "anonymous"
    assert clone.is_map is True


# ---------------------------------------------------------------------------
# Group D — Document ParentNode properties and active_element ()
# ---------------------------------------------------------------------------


def test_d1_standard_doc_first_element_child_is_html() -> None:
    """D-1: Standard parsed document: doc.first_element_child.tag_name == 'HTML'."""
    doc = HTMLDocument.parse("<html><head></head><body></body></html>")
    first = doc.first_element_child
    assert first is not None
    assert first.tag_name == "HTML"


def test_d2_standard_doc_last_element_child_is_html() -> None:
    """D-2: Standard parsed document: doc.last_element_child.tag_name == 'HTML'."""
    doc = HTMLDocument.parse("<html><head></head><body></body></html>")
    last = doc.last_element_child
    assert last is not None
    assert last.tag_name == "HTML"


def test_d3_standard_doc_child_element_count_is_one() -> None:
    """D-3: Standard parsed document: doc.child_element_count == 1."""
    doc = HTMLDocument.parse("<html><head></head><body></body></html>")
    assert doc.child_element_count == 1


def test_d4_empty_document_element_child_properties() -> None:
    """D-4: Empty Document(): first/last_element_child is None; child_element_count == 0."""
    doc = Document()
    assert doc.first_element_child is None
    assert doc.last_element_child is None
    assert doc.child_element_count == 0


def test_d5_active_element_is_none() -> None:
    """D-5: doc.active_element is None regardless of document state."""
    doc = Document()
    assert doc.active_element is None

    doc2 = HTMLDocument.parse("<html><body><input id='i'></body></html>")
    assert doc2.active_element is None


def test_d6_first_element_child_is_document_element() -> None:
    """D-6: doc.first_element_child is the same object as doc.document_element."""
    doc = HTMLDocument.parse("<html><head></head><body></body></html>")
    assert doc.first_element_child is doc.document_element


# ---------------------------------------------------------------------------
# Group E — Doctest sweep (touched source files for )
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    [
        "src/aspose_html/dom/html/_elements.py",
        "src/aspose_html/dom/_document.py",
    ],
)
def test_e_doctest_sweep(module_path: str) -> None:
    """E: All >>> docstring examples in the given source file execute cleanly."""
    import pathlib  # noqa: PLC0415

    repo_root = str(pathlib.Path(__file__).parent.parent.parent)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--doctest-modules", module_path, "-q"],
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert result.returncode == 0, (
        f"doctest failed for {module_path}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
