"""Tests for  IDL fixes: HTMLSelectElement.value, HTMLInputElement.default_value,
and CSSStyleDeclaration.length/item().

Covers  and  acceptance criteria.
"""
import pytest

from aspose_html.dom import Document
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_select_with_options(doc: Document):
    """Return (sel, opt_a, opt_b, opt_c) with values 'a', 'b', 'c'."""
    sel = doc.create_element("select")
    opt_a = doc.create_element("option")
    opt_a.set_attribute("value", "a")
    opt_b = doc.create_element("option")
    opt_b.set_attribute("value", "b")
    opt_c = doc.create_element("option")
    opt_c.set_attribute("value", "c")
    sel.append_child(opt_a)
    sel.append_child(opt_b)
    sel.append_child(opt_c)
    return sel, opt_a, opt_b, opt_c


# ---------------------------------------------------------------------------
# HTMLSelectElement.value
# ---------------------------------------------------------------------------

class TestHTMLSelectElementValue:
    def test_select_value_empty_when_no_selection(self):
        """select.value returns '' when no option has selected attribute."""
        doc = Document()
        sel, opt_a, opt_b, opt_c = _make_select_with_options(doc)
        assert sel.value == ""

    def test_select_value_returns_selected_option(self):
        """select.value returns value of the first option with selected flag."""
        doc = Document()
        sel, opt_a, opt_b, opt_c = _make_select_with_options(doc)
        opt_b.set_attribute("selected", "")
        assert sel.value == "b"

    def test_select_value_returns_first_selected_when_multiple(self):
        """When two options are selected, returns value of the first one."""
        doc = Document()
        sel, opt_a, opt_b, opt_c = _make_select_with_options(doc)
        opt_a.set_attribute("selected", "")
        opt_c.set_attribute("selected", "")
        assert sel.value == "a"

    def test_select_value_setter_selects_option(self):
        """select.value = 'b' causes select.value to return 'b'."""
        doc = Document()
        sel, opt_a, opt_b, opt_c = _make_select_with_options(doc)
        sel.value = "b"
        assert sel.value == "b"

    def test_select_value_setter_deselects_others(self):
        """select.value = 'b' deselects all options except 'b'."""
        doc = Document()
        sel, opt_a, opt_b, opt_c = _make_select_with_options(doc)
        opt_a.set_attribute("selected", "")  # pre-select a
        sel.value = "b"
        assert opt_a.selected is False
        assert opt_b.selected is True
        assert opt_c.selected is False

    def test_select_value_setter_no_match_deselects_all(self):
        """select.value = 'nonexistent' deselects all and returns ''."""
        doc = Document()
        sel, opt_a, opt_b, opt_c = _make_select_with_options(doc)
        opt_b.set_attribute("selected", "")
        sel.value = "nonexistent"
        assert sel.value == ""
        assert opt_a.selected is False
        assert opt_b.selected is False
        assert opt_c.selected is False

    def test_select_value_round_trip_from_parsed_html(self):
        """Round-trip: parse HTML with selected option, assert value returns 'b'."""
        doc = HTMLDocument.parse(
            "<select>"
            "<option value='a'>A</option>"
            "<option value='b' selected>B</option>"
            "<option value='c'>C</option>"
            "</select>"
        )
        sel = doc.query_selector("select")
        assert sel is not None
        assert sel.value == "b"

    def test_select_value_empty_select(self):
        """select.value on a <select> with no options returns ''."""
        doc = Document()
        sel = doc.create_element("select")
        assert sel.value == ""

    def test_select_value_setter_then_selected_index(self):
        """After select.value = 'c', selected_index should point to option c."""
        doc = Document()
        sel, opt_a, opt_b, opt_c = _make_select_with_options(doc)
        sel.value = "c"
        assert sel.selected_index == 2
        assert sel.value == "c"


# ---------------------------------------------------------------------------
# HTMLInputElement.default_value
# ---------------------------------------------------------------------------

class TestHTMLInputElementDefaultValue:
    def test_input_default_value_reflects_html_attribute(self):
        """input.default_value returns the value content attribute."""
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("value", "Alice")
        assert inp.default_value == "Alice"

    def test_input_default_value_empty_when_no_attribute(self):
        """input.default_value returns '' when no value attribute is set."""
        doc = Document()
        inp = doc.create_element("input")
        assert inp.default_value == ""

    def test_input_default_value_setter(self):
        """input.default_value = 'Bob' updates the content attribute."""
        doc = Document()
        inp = doc.create_element("input")
        inp.default_value = "Bob"
        assert inp.default_value == "Bob"
        assert inp.get_attribute("value") == "Bob"

    def test_input_default_value_parsed_html(self):
        """Parsed <input value='Alice'> has default_value == 'Alice'."""
        doc = HTMLDocument.parse("<input value='Alice'>")
        inp = doc.query_selector("input")
        assert inp is not None
        assert inp.default_value == "Alice"

    def test_input_default_value_is_distinct_concept_from_live_value(self):
        """default_value and value both return attribute; no separate live state."""
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("value", "initial")
        assert inp.default_value == "initial"
        assert inp.value == "initial"
        # Setting default_value also changes value (headless — no user state)
        inp.default_value = "changed"
        assert inp.default_value == "changed"

    def test_input_default_value_setter_empty_string(self):
        """Setting default_value to '' keeps the attribute present with ''."""
        doc = Document()
        inp = doc.create_element("input")
        inp.default_value = ""
        # set_attribute("value", "") sets the attribute to ""
        assert inp.get_attribute("value") == ""

    def test_input_default_value_hasattr(self):
        """HTMLInputElement.default_value property exists (was missing before fix)."""
        doc = Document()
        inp = doc.create_element("input")
        assert hasattr(inp, "default_value")


# ---------------------------------------------------------------------------
# CSSStyleDeclaration.length and item()
# ---------------------------------------------------------------------------

class TestCSSStyleDeclarationLengthAndItem:
    def test_style_length_empty(self):
        """style.length returns 0 for an element with no inline style."""
        doc = Document()
        el = doc.create_element("div")
        assert el.style.length == 0

    def test_style_length_counts_properties(self):
        """style.length returns the number of declared CSS properties."""
        doc = Document()
        el = doc.create_element("div")
        el.style["color"] = "red"
        el.style["margin"] = "4px"
        assert el.style.length == 2

    def test_style_length_from_parsed_html(self):
        """style.length counts properties parsed from HTML style attribute."""
        doc = HTMLDocument.parse('<div style="color: red; margin: 4px"></div>')
        el = doc.query_selector("div")
        assert el is not None
        assert el.style.length == 2

    def test_style_length_after_remove(self):
        """style.length decreases after removing a property."""
        doc = Document()
        el = doc.create_element("div")
        el.style["color"] = "red"
        el.style["padding"] = "0"
        assert el.style.length == 2
        el.style.remove_property("color")
        assert el.style.length == 1

    def test_style_item_returns_property_name(self):
        """style.item(0) returns the first property name."""
        doc = Document()
        el = doc.create_element("div")
        el.style["color"] = "red"
        assert el.style.item(0) == "color"

    def test_style_item_second_property(self):
        """style.item(1) returns the second property name in insertion order."""
        doc = Document()
        el = doc.create_element("div")
        el.style["color"] = "red"
        el.style["font-size"] = "12px"
        assert el.style.item(1) == "font-size"

    def test_style_item_out_of_range_returns_empty(self):
        """style.item(index) returns '' when index >= length."""
        doc = Document()
        el = doc.create_element("div")
        el.style["color"] = "red"
        assert el.style.item(99) == ""
        assert el.style.item(1) == ""

    def test_style_item_negative_returns_empty(self):
        """style.item(-1) returns '' (negative index treated as out of range)."""
        doc = Document()
        el = doc.create_element("div")
        el.style["color"] = "red"
        assert el.style.item(-1) == ""

    def test_style_item_empty_declaration(self):
        """style.item(0) returns '' when there are no declared properties."""
        doc = Document()
        el = doc.create_element("div")
        assert el.style.item(0) == ""

    def test_style_length_and_item_consistent(self):
        """Enumerate all properties by index and verify they match list(style)."""
        doc = Document()
        el = doc.create_element("div")
        el.style["color"] = "red"
        el.style["margin"] = "0"
        el.style["padding"] = "4px"
        props_by_index = [el.style.item(i) for i in range(el.style.length)]
        props_by_iter = list(el.style)
        assert props_by_index == props_by_iter
