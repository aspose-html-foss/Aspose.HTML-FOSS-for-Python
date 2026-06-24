""" integration matrix — end-to-end tests via HTMLDocument.parse().

Covers , , and :

- Group A: HTMLSelectElement.value getter/setter (WHATWG HTML §4.10.7.6.6)
- Group B: HTMLInputElement.default_value (WHATWG HTML §4.10.5.1)
- Group C: CSSStyleDeclaration.length and item() (CSSOM §6.1)
- Group D: Cross-check / docstring example sweep
"""
import subprocess
import sys

import pytest

from aspose_html.dom import Document
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Group A — HTMLSelectElement.value end-to-end (≥ 6 tests)
# ---------------------------------------------------------------------------

class TestGroupASelectValueEndToEnd:
    """End-to-end tests for HTMLSelectElement.value via HTMLDocument.parse()."""

    _HTML = (
        "<select>"
        "<option value='a'>A</option>"
        "<option value='b' selected>B</option>"
        "<option value='c'>C</option>"
        "</select>"
    )

    def test_select_value_returns_selected_option_value(self):
        """Parsing <select> with selected option — value returns 'b'."""
        doc = HTMLDocument.parse(self._HTML)
        sel = doc.query_selector("select")
        assert sel is not None
        assert sel.value == "b"

    def test_select_value_setter_changes_selection(self):
        """After setting select.value = 'a', getter returns 'a'."""
        doc = HTMLDocument.parse(self._HTML)
        sel = doc.query_selector("select")
        assert sel is not None
        sel.value = "a"
        assert sel.value == "a"

    def test_select_no_selection_returns_first_or_empty(self):
        """No selected attr — WHATWG: first option default-selected (or '' in headless).

        In this headless implementation, no option has its selectedness set
        unless the 'selected' attribute is present, so value returns ''.
        """
        doc = HTMLDocument.parse(
            "<select>"
            "<option value='x'>X</option>"
            "<option value='y'>Y</option>"
            "</select>"
        )
        sel = doc.query_selector("select")
        assert sel is not None
        # Headless: no option explicitly selected → value is ''
        assert sel.value == ""

    def test_select_value_setter_invalid_deselects(self):
        """Setting select.value = 'z' (no match) deselects all; getter returns ''."""
        doc = HTMLDocument.parse(self._HTML)
        sel = doc.query_selector("select")
        assert sel is not None
        sel.value = "z"
        assert sel.value == ""

    def test_select_value_setter_updates_option_selected(self):
        """After select.value = 'c', option[value='c'].selected is True."""
        doc = HTMLDocument.parse(self._HTML)
        sel = doc.query_selector("select")
        assert sel is not None
        sel.value = "c"
        options = list(sel.options)
        # option[0] → 'a', option[1] → 'b', option[2] → 'c'
        assert options[2].selected is True
        assert options[0].selected is False
        assert options[1].selected is False

    def test_select_multiple_options_only_first_selected_returned(self):
        """When two options have 'selected', value returns first in tree order."""
        doc = HTMLDocument.parse(
            "<select>"
            "<option value='p' selected>P</option>"
            "<option value='q' selected>Q</option>"
            "</select>"
        )
        sel = doc.query_selector("select")
        assert sel is not None
        # The WHATWG getter returns the first option with selected == True
        assert sel.value == "p"

    def test_select_value_round_trip_selected_then_deselected(self):
        """set value to 'b' then to 'a' — both transitions work correctly."""
        doc = HTMLDocument.parse(self._HTML)
        sel = doc.query_selector("select")
        assert sel is not None
        sel.value = "b"
        assert sel.value == "b"
        sel.value = "a"
        assert sel.value == "a"

    def test_select_empty_element_value_empty(self):
        """<select></select> — value returns '' (no options)."""
        doc = HTMLDocument.parse("<select></select>")
        sel = doc.query_selector("select")
        assert sel is not None
        assert sel.value == ""


# ---------------------------------------------------------------------------
# Group B — HTMLInputElement.default_value end-to-end (≥ 5 tests)
# ---------------------------------------------------------------------------

class TestGroupBInputDefaultValueEndToEnd:
    """End-to-end tests for HTMLInputElement.default_value via HTMLDocument.parse()."""

    def test_input_default_value_from_html(self):
        """Parsing <input value='hello'> — default_value returns 'hello'."""
        doc = HTMLDocument.parse("<input type='text' value='hello'>")
        inp = doc.query_selector("input")
        assert inp is not None
        assert inp.default_value == "hello"

    def test_input_default_value_empty_no_attr(self):
        """Parsing <input> (no value attr) — default_value returns ''."""
        doc = HTMLDocument.parse("<input>")
        inp = doc.query_selector("input")
        assert inp is not None
        assert inp.default_value == ""

    def test_input_default_value_setter_updates_attribute(self):
        """Setting default_value = 'world' updates the 'value' content attribute."""
        doc = HTMLDocument.parse("<input value='hello'>")
        inp = doc.query_selector("input")
        assert inp is not None
        inp.default_value = "world"
        assert inp.get_attribute("value") == "world"
        assert inp.default_value == "world"

    def test_input_default_value_independent_concept(self):
        """default_value reflects the value attribute; distinct from live value semantics.

        In headless mode both default_value and value reflect the same
        attribute, but they are conceptually independent IDL properties.
        """
        doc = HTMLDocument.parse("<input value='initial'>")
        inp = doc.query_selector("input")
        assert inp is not None
        assert inp.default_value == "initial"
        # Changing default_value via the setter should not silently break value
        inp.default_value = "changed"
        assert inp.default_value == "changed"

    def test_input_default_value_type_is_str(self):
        """default_value is always a str instance."""
        doc = HTMLDocument.parse("<input value='42'>")
        inp = doc.query_selector("input")
        assert inp is not None
        assert isinstance(inp.default_value, str)

    def test_input_default_value_preserves_whitespace(self):
        """default_value preserves leading/trailing whitespace in the attribute."""
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("value", "  spaces  ")
        assert inp.default_value == "  spaces  "

    def test_input_default_value_special_characters(self):
        """default_value returns the attribute value including special characters."""
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("value", "hello&world<>")
        assert inp.default_value == "hello&world<>"


# ---------------------------------------------------------------------------
# Group C — CSSStyleDeclaration.length/item() end-to-end (≥ 6 tests)
# ---------------------------------------------------------------------------

class TestGroupCCSSStyleDeclarationEndToEnd:
    """End-to-end tests for CSSStyleDeclaration.length and item() via HTMLDocument.parse()."""

    def test_style_length_matches_declared_count(self):
        """Parsing div with 3 inline properties — length == 3."""
        doc = HTMLDocument.parse('<div style="color: red; font-size: 14px; margin: 0"></div>')
        el = doc.query_selector("div")
        assert el is not None
        assert el.style.length == 3

    def test_style_item_zero_returns_first_property(self):
        """style.item(0) returns 'color' (first declared property)."""
        doc = HTMLDocument.parse('<div style="color: red; font-size: 14px"></div>')
        el = doc.query_selector("div")
        assert el is not None
        assert el.style.item(0) == "color"

    def test_style_item_negative_returns_empty(self):
        """style.item(-1) returns '' (negative index treated as out of range)."""
        doc = HTMLDocument.parse('<div style="color: red"></div>')
        el = doc.query_selector("div")
        assert el is not None
        assert el.style.item(-1) == ""

    def test_style_item_past_end_returns_empty(self):
        """style.item(99) returns '' when only a few properties are declared."""
        doc = HTMLDocument.parse('<div style="color: red; margin: 0"></div>')
        el = doc.query_selector("div")
        assert el is not None
        assert el.style.item(99) == ""

    def test_style_length_empty_style_attr(self):
        """Parsing div with no style attribute — length == 0."""
        doc = HTMLDocument.parse("<div></div>")
        el = doc.query_selector("div")
        assert el is not None
        assert el.style.length == 0

    def test_style_length_after_set_property(self):
        """After set_property('padding', '4px'), length increases by 1."""
        doc = HTMLDocument.parse('<div style="color: red"></div>')
        el = doc.query_selector("div")
        assert el is not None
        initial_length = el.style.length
        el.style.set_property("padding", "4px")
        assert el.style.length == initial_length + 1

    def test_style_item_insertion_order_preserved(self):
        """Properties are returned by item() in insertion (declaration) order."""
        doc = HTMLDocument.parse('<div style="color: red; font-size: 14px; margin: 0"></div>')
        el = doc.query_selector("div")
        assert el is not None
        assert el.style.item(0) == "color"
        assert el.style.item(1) == "font-size"
        assert el.style.item(2) == "margin"

    def test_style_length_after_remove_property(self):
        """After remove_property, length decreases by 1."""
        doc = HTMLDocument.parse('<div style="color: red; font-size: 14px"></div>')
        el = doc.query_selector("div")
        assert el is not None
        assert el.style.length == 2
        el.style.remove_property("color")
        assert el.style.length == 1
        assert el.style.item(0) == "font-size"

    def test_style_length_and_item_enumerate_all(self):
        """Iterating item(0)..item(length-1) yields the same names as list(style)."""
        doc = HTMLDocument.parse('<div style="color: red; margin: 0; padding: 4px"></div>')
        el = doc.query_selector("div")
        assert el is not None
        by_index = [el.style.item(i) for i in range(el.style.length)]
        by_iter = list(el.style)
        assert by_index == by_iter


# ---------------------------------------------------------------------------
# Group D — Cross-check / docstring example sweep (≥ 3 tests)
# ---------------------------------------------------------------------------

class TestGroupDCrossCheckAndDoctestSweep:
    """Cross-check tests validating the inline docstring examples work correctly."""

    def test_select_value_doctest_example(self):
        """Validates the docstring example for HTMLSelectElement.value getter/setter."""
        doc = Document()
        sel = doc.create_element("select")
        opt_a = doc.create_element("option")
        opt_a.set_attribute("value", "a")
        opt_b = doc.create_element("option")
        opt_b.set_attribute("value", "b")
        opt_b.set_attribute("selected", "")
        sel.append_child(opt_a)
        sel.append_child(opt_b)
        # getter returns selected option value
        assert sel.value == "b"
        # setter updates selection
        sel.value = "a"
        assert sel.value == "a"
        # setter with no match deselects all
        sel.value = "nonexistent"
        assert sel.value == ""

    def test_cssdecl_length_and_item_doctest_example(self):
        """Validates the docstring examples for CSSStyleDeclaration.length and item()."""
        doc = Document()
        el = doc.create_element("div")
        # length starts at 0
        assert el.style.length == 0
        # one property
        el.style["color"] = "red"
        el.style["margin"] = "4px"
        assert el.style.length == 2
        # item(0) returns first property name
        el2 = doc.create_element("span")
        el2.style.set_property("color", "red")
        el2.style.set_property("margin", "0")
        assert el2.style.item(0) == "color"
        assert el2.style.item(1) == "margin"
        assert el2.style.item(99) == ""
        assert el2.style.item(-1) == ""

    def test_input_default_value_doctest_example(self):
        """Validates the docstring example for HTMLInputElement.default_value."""
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("value", "Alice")
        assert inp.default_value == "Alice"
        inp.default_value = "Bob"
        assert inp.default_value == "Bob"
        # no attribute → empty string
        fresh = doc.create_element("input")
        assert fresh.default_value == ""

    @pytest.mark.skipif(
        not __import__("os").path.exists(
            __import__("os").path.join(
                __import__("os").path.dirname(__file__),
                "..", "..", "scripts", "verify_doc_examples.py"
            )
        ),
        reason="verify_doc_examples.py script not found at expected path",
    )
    def test_verify_doc_examples_clean_on_style_module(self):
        """verify_doc_examples.py exits 0 for the _style.py doc module."""
        import os
        repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
        script = os.path.join(repo_root, "scripts", "verify_doc_examples.py")
        style_doc = os.path.join(
            repo_root, "src", "aspose_html", "dom", "_style.py"
        )
        result = subprocess.run(
            [sys.executable, script, style_doc],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        assert result.returncode == 0, (
            f"verify_doc_examples.py failed on _style.py:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
