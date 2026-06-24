"""Tests for Element.inner_html and Element.outer_html properties.

Covers  /  and  / .
"""
from __future__ import annotations

import doctest
import sys

import pytest

from aspose_html.dom import (
    Document,
    HierarchyRequestError,
    NoModificationAllowedError,
    NodeType,
)
from aspose_html.html_document import HTMLDocument


@pytest.fixture
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# inner_html getter tests
# ---------------------------------------------------------------------------


def test_inner_html_getter_empty(doc: Document) -> None:
    """AC-1 / test_inner_html_getter_empty: empty element returns ''."""
    el = doc.create_element("div")
    assert el.inner_html == ""


def test_inner_html_getter_with_child(doc: Document) -> None:
    """AC-1: element with one Element child returns serialised child markup."""
    el = doc.create_element("div")
    span = doc.create_element("span")
    el.append_child(span)
    assert el.inner_html == "<span></span>"


def test_inner_html_getter_nested(doc: Document) -> None:
    """AC-1: nested elements serialise correctly — inner gives content without outer tags."""
    outer = doc.create_element("div")
    p = doc.create_element("p")
    span = doc.create_element("span")
    p.append_child(span)
    outer.append_child(p)
    # outer_html would be '<div><p><span></span></p></div>'
    # inner_html of outer excludes the outer div's own tags
    assert outer.inner_html == "<p><span></span></p>"


def test_inner_html_getter_text_node(doc: Document) -> None:
    """AC-1 / test_inner_html_getter_text_node: text containing '<' is escaped."""
    el = doc.create_element("p")
    text = doc.create_text_node("a < b")
    el.append_child(text)
    assert el.inner_html == "a &lt; b"


# ---------------------------------------------------------------------------
# outer_html getter tests
# ---------------------------------------------------------------------------


def test_outer_html_getter_void_element(doc: Document) -> None:
    """AC-2 / test_outer_html_getter_void_element: void element returns self-closing markup."""
    br = doc.create_element("br")
    assert br.outer_html == "<br>"


def test_outer_html_getter_with_content(doc: Document) -> None:
    """AC-2: element with children includes own tags and child content."""
    el = doc.create_element("ul")
    li = doc.create_element("li")
    el.append_child(li)
    assert el.outer_html == "<ul><li></li></ul>"


def test_outer_html_matches_serialise_function(doc: Document) -> None:
    """AC-2: outer_html equals direct call to serialiser.outer_html(element)."""
    from aspose_html.serialiser import outer_html as _outer_html_fn

    el = doc.create_element("section")
    child = doc.create_element("p")
    el.append_child(child)
    assert el.outer_html == _outer_html_fn(el)


# ---------------------------------------------------------------------------
# inner_html setter tests
# ---------------------------------------------------------------------------


def test_inner_html_setter_replaces_children() -> None:
    """AC-3: after assignment child count and type match parsed content."""
    # Use a freshly parsed document so the element has an ownerDocument for
    # parse_fragment's context_element path.
    doc2 = HTMLDocument.parse("<section></section>")
    section = doc2.document_element.query_selector("section")
    assert section is not None
    section.inner_html = "<p></p>"
    assert section.child_element_count == 1
    first = section.first_element_child
    assert first is not None
    assert first.tag_name == "P"


def test_inner_html_setter_empty_string_clears_children() -> None:
    """AC-4: inner_html = '' removes all children; child_nodes is empty."""
    doc2 = HTMLDocument.parse("<div><span></span><em></em></div>")
    div = doc2.document_element.query_selector("div")
    assert div is not None
    div.inner_html = ""
    assert len(list(div.child_nodes)) == 0


def test_inner_html_setter_text_content() -> None:
    """Setter with plain text produces a Text child node with correct data."""
    doc2 = HTMLDocument.parse("<p></p>")
    p = doc2.document_element.query_selector("p")
    assert p is not None
    p.inner_html = "hello"
    children = list(p.child_nodes)
    assert len(children) == 1
    assert children[0].node_type == NodeType.TEXT_NODE
    assert children[0].node_value == "hello"


def test_inner_html_round_trip() -> None:
    """AC-3 + AC-1: set then get returns the same markup (modulo normalisation)."""
    doc2 = HTMLDocument.parse("<div></div>")
    div = doc2.document_element.query_selector("div")
    assert div is not None
    div.inner_html = "<em>x</em>"
    assert div.inner_html == "<em>x</em>"


def test_inner_html_setter_multiple_elements() -> None:
    """Setter with multiple sibling elements results in correct child count."""
    doc2 = HTMLDocument.parse("<ul></ul>")
    ul = doc2.document_element.query_selector("ul")
    assert ul is not None
    ul.inner_html = "<li>a</li><li>b</li><li>c</li>"
    assert ul.child_element_count == 3


# ---------------------------------------------------------------------------
# outer_html setter tests ( / )
# ---------------------------------------------------------------------------


def test_outer_html_setter_replaces_element_in_parent() -> None:
    """ AC-1: assigning outer_html replaces the element in place."""
    doc2 = HTMLDocument.parse("<main><span>old</span><em>after</em></main>")
    main = doc2.query_selector("main")
    span = doc2.query_selector("span")
    assert main is not None
    assert span is not None

    span.outer_html = "<p>new</p><strong>two</strong>"

    children = list(main.children)
    assert [child.tag_name for child in children] == ["P", "STRONG", "EM"]
    assert children[0].text_content == "new"
    assert children[1].text_content == "two"


def test_outer_html_setter_detaches_original() -> None:
    """ AC-2: the replaced element is detached."""
    doc2 = HTMLDocument.parse("<div><span>old</span></div>")
    span = doc2.query_selector("span")
    assert span is not None

    span.outer_html = "<b>new</b>"

    assert span.parent_node is None


def test_outer_html_setter_detached_raises(doc: Document) -> None:
    """ AC-3: detached element assignment raises DOM exception."""
    el = doc.create_element("span")

    with pytest.raises(NoModificationAllowedError):
        el.outer_html = "<b>new</b>"


def test_no_modification_allowed_error_exported() -> None:
    """ AC-3: exception is part of aspose_html.dom public exports."""
    from aspose_html.dom import NoModificationAllowedError as Exported

    assert Exported is NoModificationAllowedError


def test_outer_html_getter_still_serialises(doc: Document) -> None:
    """ AC-4: getter behaviour is unchanged."""
    el = doc.create_element("article")
    child = doc.create_element("p")
    el.append_child(child)

    assert el.outer_html == "<article><p></p></article>"


def test_outer_html_setter_does_not_regress_inner_html() -> None:
    """ AC-5: inner_html remains readable and writable."""
    doc2 = HTMLDocument.parse("<section><div></div></section>")
    div = doc2.query_selector("div")
    assert div is not None

    div.inner_html = "<span>kept</span>"

    assert div.inner_html == "<span>kept</span>"


def test_outer_html_round_trip_preserves_structure() -> None:
    """ AC-6: assigning outer_html to itself preserves parent markup."""
    doc2 = HTMLDocument.parse("<main><div><span>x</span></div><p>after</p></main>")
    main = doc2.query_selector("main")
    div = doc2.query_selector("div")
    assert main is not None
    assert div is not None
    before = main.inner_html

    div.outer_html = div.outer_html

    assert main.inner_html == before


def test_outer_html_setter_document_parent_context() -> None:
    """ DoD: parent may be Document with no parent_element."""
    doc2 = Document()
    old = doc2.create_element("section")
    doc2.append_child(old)

    old.outer_html = "<article><p>new</p></article>"

    assert old.parent_node is None
    assert doc2.first_child is not None
    assert doc2.first_child.node_name == "ARTICLE"
    assert doc2.first_child.first_child is not None
    assert doc2.first_child.first_child.node_name == "P"


def test_outer_html_document_parent_rejects_two_elements_atomically() -> None:
    """Document replacement validates hierarchy before detaching original."""
    doc2 = Document()
    old = doc2.create_element("section")
    doc2.append_child(old)

    with pytest.raises(HierarchyRequestError):
        old.outer_html = "<article></article><aside></aside>"

    assert old.parent_node is doc2
    assert doc2.first_child is old


# ---------------------------------------------------------------------------
# Doctest pass-through (AC-6 / )
# ---------------------------------------------------------------------------


def test_doctest_passes() -> None:
    """AC-6: doctests in _element module report zero failures."""
    import aspose_html.dom._element as _element_module

    results = doctest.testmod(_element_module, verbose=False)
    assert results.failed == 0, (
        f"{results.failed} doctest(s) failed in aspose_html.dom._element"
    )


# ---------------------------------------------------------------------------
# No circular import at module load time (AC-7)
# ---------------------------------------------------------------------------


def test_no_circular_import() -> None:
    """AC-7: aspose_html.dom._element contains no top-level serialiser import.

    The lazy-import pattern (imports inside property bodies) ensures that
    importing _element.py does not eagerly load aspose_html.serialiser.
    Verified statically to avoid subprocess/sys.modules complexity.
    """
    import ast
    import pathlib

    src = pathlib.Path(__file__).parent.parent.parent / "src" / "aspose_html" / "dom" / "_element.py"
    tree = ast.parse(src.read_text())

    # Walk only top-level statements (not inside function/class bodies)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [n.name for n in getattr(node, "names", [])]
            module = getattr(node, "module", "") or ""
            assert "serialiser" not in module and not any("serialiser" in n for n in names), (
                f"Top-level import of serialiser found at line {node.lineno}"
            )
