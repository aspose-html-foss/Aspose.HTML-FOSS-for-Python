"""Tests for Document.create_element_ns — ADR-023 / BACK-29.

Verifies the corrected WHATWG DOM §5.3.3 parameter order (namespace_uri first,
qualified_name second) and the backward-compatibility deprecation heuristic.
"""
from __future__ import annotations

import warnings

import pytest

from aspose_html.dom import Document, Element
from aspose_html.dom._html_element import HTMLElement


@pytest.fixture
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# Correct calling convention
# ---------------------------------------------------------------------------

def test_correct_order_sets_namespace_uri(doc: Document) -> None:
    """namespace_uri is stored correctly when arguments are in the right order."""
    el = doc.create_element_ns("http://www.w3.org/2000/svg", "svg")
    assert el.namespace_uri == "http://www.w3.org/2000/svg"
    assert el.local_name == "svg"
    assert el.owner_document is doc


def test_correct_order_mathml(doc: Document) -> None:
    """MathML namespace is stored correctly."""
    el = doc.create_element_ns("http://www.w3.org/1998/Math/MathML", "math")
    assert el.namespace_uri == "http://www.w3.org/1998/Math/MathML"
    assert el.local_name == "math"


def test_correct_order_html_namespace(doc: Document) -> None:
    """HTML namespace element is a plain Element, not dispatched through registry.

    create_element_ns does not use the HTMLElement registry — that is exclusive
    to create_element(). See ADR-023 / ADR-010.
    """
    el = doc.create_element_ns("http://www.w3.org/1999/xhtml", "div")
    assert el.namespace_uri == "http://www.w3.org/1999/xhtml"
    assert el.local_name == "div"
    assert isinstance(el, Element)
    assert not isinstance(el, HTMLElement)  # INV-005: no registry dispatch


# ---------------------------------------------------------------------------
# Backward-compatibility: deprecated old calling convention
# ---------------------------------------------------------------------------

def test_deprecated_old_order_emits_warning(doc: Document) -> None:
    """Old order (tag first, uri second) triggers DeprecationWarning and still works."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        el = doc.create_element_ns("svg", "http://www.w3.org/2000/svg")
    assert len(w) == 1
    assert issubclass(w[0].category, DeprecationWarning)
    assert "argument order has changed" in str(w[0].message)
    # Args must have been swapped so result is still correct
    assert el.namespace_uri == "http://www.w3.org/2000/svg"
    assert el.local_name == "svg"


def test_deprecated_old_order_html_namespace_emits_warning(doc: Document) -> None:
    """Old order with HTML namespace URI also triggers warning and is corrected."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        el = doc.create_element_ns("div", "http://www.w3.org/1999/xhtml")
    assert len(w) == 1
    assert issubclass(w[0].category, DeprecationWarning)
    assert el.local_name == "div"
    assert el.namespace_uri == "http://www.w3.org/1999/xhtml"


# ---------------------------------------------------------------------------
# No spurious warning for correct calls
# ---------------------------------------------------------------------------

def test_no_warning_for_correct_call(doc: Document) -> None:
    """A correct call emits no DeprecationWarning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        doc.create_element_ns("http://www.w3.org/2000/svg", "circle")
    deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
    assert len(deprecation_warnings) == 0


# ---------------------------------------------------------------------------
# Ownership and tree attachment
# ---------------------------------------------------------------------------

def test_returned_element_is_owned_by_document(doc: Document) -> None:
    """Newly created element is owned by the creating document."""
    el = doc.create_element_ns("http://www.w3.org/2000/svg", "rect")
    assert el.owner_document is doc


def test_element_has_no_parent_on_creation(doc: Document) -> None:
    """Newly created element is detached — no parent_node."""
    el = doc.create_element_ns("http://www.w3.org/2000/svg", "path")
    assert el.parent_node is None


# ---------------------------------------------------------------------------
# Track 75 / ADR-269: qualified-name split (WHATWG DOM §4.6)
# ---------------------------------------------------------------------------

SVG_NS = "http://www.w3.org/2000/svg"
HTML_NS = "http://www.w3.org/1999/xhtml"
MATHML_NS = "http://www.w3.org/1998/Math/MathML"


def test_svg_qualified_name_splits_prefix(doc: Document) -> None:
    """create_element_ns with 'svg:path' sets prefix='svg'."""
    el = doc.create_element_ns(SVG_NS, "svg:path")
    assert el.prefix == "svg"


def test_svg_qualified_name_splits_local_name(doc: Document) -> None:
    """create_element_ns with 'svg:path' sets local_name='path'."""
    el = doc.create_element_ns(SVG_NS, "svg:path")
    assert el.local_name == "path"


def test_no_prefix_prefix_is_none(doc: Document) -> None:
    """Unqualified name produces prefix=None."""
    el = doc.create_element_ns(SVG_NS, "path")
    assert el.prefix is None


def test_no_prefix_local_name(doc: Document) -> None:
    """Unqualified name stores the full string as local_name."""
    el = doc.create_element_ns(SVG_NS, "path")
    assert el.local_name == "path"


def test_html_ns_no_prefix(doc: Document) -> None:
    """HTML-namespace element created without prefix has prefix=None."""
    el = doc.create_element_ns(HTML_NS, "div")
    assert el.prefix is None


def test_multiple_colons_keeps_first_as_prefix(doc: Document) -> None:
    """Multiple colons: only the first colon splits; prefix='a', local_name='b:c'.

    WHATWG DOM does not raise on multiple colons at the createElement level;
    only one colon split is performed (split-on-first).
    """
    el = doc.create_element_ns(SVG_NS, "a:b:c")
    assert el.prefix == "a"
    assert el.local_name == "b:c"


def test_mathml_qualified_name_prefix(doc: Document) -> None:
    """MathML qualified name sets prefix and local_name correctly."""
    el = doc.create_element_ns(MATHML_NS, "m:math")
    assert el.prefix == "m"


def test_mathml_qualified_name_local_name(doc: Document) -> None:
    """MathML qualified name sets local_name to the part after the colon."""
    el = doc.create_element_ns(MATHML_NS, "m:math")
    assert el.local_name == "math"


def test_tag_name_is_qualified_name_when_prefix_set(doc: Document) -> None:
    """Element.tag_name returns 'prefix:local_name' for namespaced elements."""
    el = doc.create_element_ns(SVG_NS, "svg:path")
    assert el.tag_name == "svg:path"


def test_namespace_uri_stored_correctly_with_prefix(doc: Document) -> None:
    """namespace_uri is preserved correctly even when prefix is extracted."""
    el = doc.create_element_ns(SVG_NS, "svg:circle")
    assert el.namespace_uri == SVG_NS
