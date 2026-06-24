"""test_open_elements.py — unit tests for StackOfOpenElements."""
import pytest
from aspose_html.dom import Document
from aspose_html.tree._open_elements import StackOfOpenElements


@pytest.fixture
def doc():
    return Document()


@pytest.fixture
def stack():
    return StackOfOpenElements()


def test_push_pop_current(doc, stack):
    """Pushing and popping elements updates current."""
    html_el = doc.create_element("html")
    body_el = doc.create_element("body")

    assert stack.current is None
    stack.push(html_el)
    assert stack.current is html_el
    stack.push(body_el)
    assert stack.current is body_el
    popped = stack.pop()
    assert popped is body_el
    assert stack.current is html_el


def test_has_in_scope_basic(doc, stack):
    """has_in_scope returns True when element is present and not blocked."""
    html_el = doc.create_element("html")
    body_el = doc.create_element("body")
    p_el = doc.create_element("p")

    stack.push(html_el)
    stack.push(body_el)
    stack.push(p_el)

    assert stack.has_in_scope("p")
    assert stack.has_in_scope("body")
    assert not stack.has_in_scope("div")


def test_has_in_scope_boundary_element_stops_search(doc, stack):
    """has_in_scope stops at scope boundary elements (e.g. table)."""
    html_el = doc.create_element("html")
    body_el = doc.create_element("body")
    p_el = doc.create_element("p")
    table_el = doc.create_element("table")

    stack.push(html_el)
    stack.push(body_el)
    stack.push(p_el)
    stack.push(table_el)

    # <p> is below <table> which is a scope boundary
    assert not stack.has_in_scope("p")


def test_has_in_button_scope(doc, stack):
    """has_in_button_scope stops at button in addition to scope elements."""
    html_el = doc.create_element("html")
    body_el = doc.create_element("body")
    p_el = doc.create_element("p")
    button_el = doc.create_element("button")

    stack.push(html_el)
    stack.push(body_el)
    stack.push(p_el)
    stack.push(button_el)

    assert stack.has_in_button_scope("button")
    # <p> is below <button> which is a button scope boundary
    assert not stack.has_in_button_scope("p")


def test_has_in_table_scope(doc, stack):
    """has_in_table_scope uses the table scope element set."""
    html_el = doc.create_element("html")
    body_el = doc.create_element("body")
    table_el = doc.create_element("table")
    tbody_el = doc.create_element("tbody")
    tr_el = doc.create_element("tr")
    td_el = doc.create_element("td")

    stack.push(html_el)
    stack.push(body_el)
    stack.push(table_el)
    stack.push(tbody_el)
    stack.push(tr_el)
    stack.push(td_el)

    assert stack.has_in_table_scope("td")
    assert stack.has_in_table_scope("table")
    assert not stack.has_in_table_scope("body")  # body is above table scope


def test_pop_until_tag_name(doc, stack):
    """pop_until removes elements until the named element is popped."""
    for name in ("html", "body", "div", "p"):
        stack.push(doc.create_element(name))

    stack.pop_until("div")
    # After popping to and including div, only html and body remain
    assert stack.current._local_name == "body"  # type: ignore[union-attr]
    assert len(stack) == 2


def test_pop_until_node(doc, stack):
    """pop_until_node removes elements until the specific node is popped."""
    html_el = doc.create_element("html")
    body_el = doc.create_element("body")
    div_el = doc.create_element("div")

    stack.push(html_el)
    stack.push(body_el)
    stack.push(div_el)

    stack.pop_until_node(body_el)
    assert stack.current is html_el


def test_contains(doc, stack):
    """__contains__ checks by tag name."""
    html_el = doc.create_element("html")
    stack.push(html_el)
    assert "html" in stack
    assert "body" not in stack


def test_contains_node(doc, stack):
    """contains_node checks by identity."""
    html_el = doc.create_element("html")
    other = doc.create_element("html")
    stack.push(html_el)
    assert stack.contains_node(html_el)
    assert not stack.contains_node(other)


def test_index_of(doc, stack):
    """index_of returns the 0-based index or -1."""
    html_el = doc.create_element("html")
    body_el = doc.create_element("body")
    stack.push(html_el)
    stack.push(body_el)
    assert stack.index_of(html_el) == 0
    assert stack.index_of(body_el) == 1
    other = doc.create_element("div")
    assert stack.index_of(other) == -1
