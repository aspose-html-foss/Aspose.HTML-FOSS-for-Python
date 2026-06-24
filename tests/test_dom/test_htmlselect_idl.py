"""Tests for HTMLSelectElement IDL completeness — .

Covers the three new properties added in  / :
  selected_index, size, length.

Test groups
-----------
A — selected_index getter
B — selected_index setter (single-select)
C — selected_index setter (multiple-select)
D — size
E — length
F — doctest sweep (pytest --doctest-modules)
G — interaction with selected_options
"""

from pathlib import Path
import subprocess
import sys

import pytest

from aspose_html.dom import Document
from aspose_html.dom.html._elements import HTMLSelectElement


PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_select(multiple: bool = False) -> tuple[HTMLSelectElement, list]:
    """Return a <select> with three <option> children and the option list."""
    doc = Document()
    sel = doc.create_element("select")
    if multiple:
        sel.set_attribute("multiple", "")
    opts = []
    for _ in range(3):
        opt = doc.create_element("option")
        sel.append_child(opt)
        opts.append(opt)
    return sel, opts  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Group A — selected_index getter
# ---------------------------------------------------------------------------

class TestSelectedIndexGetter:
    def test_a1_empty_select_returns_minus_one(self):
        """A-1: Empty <select> returns -1."""
        doc = Document()
        sel = doc.create_element("select")
        assert sel.selected_index == -1  # type: ignore[attr-defined]

    def test_a2_option_at_index_2_selected(self):
        """A-2: <select> with option at index 2 having selected returns 2."""
        sel, opts = make_select()
        opts[2].set_attribute("selected", "")
        assert sel.selected_index == 2

    def test_a3_multiple_selected_returns_first(self):
        """A-3: When multiple options carry selected, returns index of first."""
        sel, opts = make_select()
        opts[1].set_attribute("selected", "")
        opts[2].set_attribute("selected", "")
        assert sel.selected_index == 1

    def test_a4_first_option_selected_returns_zero(self):
        """Getter returns 0 when first option carries selected attribute."""
        sel, opts = make_select()
        opts[0].set_attribute("selected", "")
        assert sel.selected_index == 0

    def test_a5_non_option_children_not_counted(self):
        """Non-<option> children do not affect selected_index."""
        doc = Document()
        sel = doc.create_element("select")
        div = doc.create_element("div")
        div.set_attribute("selected", "")
        sel.append_child(div)
        opt = doc.create_element("option")
        opt.set_attribute("selected", "")
        sel.append_child(opt)
        # Only option children count — div is ignored, opt is index 0
        assert sel.selected_index == 0


# ---------------------------------------------------------------------------
# Group B — selected_index setter (single-select)
# ---------------------------------------------------------------------------

class TestSelectedIndexSetterSingleSelect:
    def test_b1_setter_selects_target_option(self):
        """B-1: Setting to a valid index selects that option."""
        sel, opts = make_select()
        sel.selected_index = 1
        assert opts[1].has_attribute("selected")

    def test_b2_setter_removes_selected_from_others(self):
        """B-2: Setting valid index removes selected from all other options."""
        sel, opts = make_select()
        opts[0].set_attribute("selected", "")
        opts[2].set_attribute("selected", "")
        sel.selected_index = 1
        assert not opts[0].has_attribute("selected")
        assert opts[1].has_attribute("selected")
        assert not opts[2].has_attribute("selected")

    def test_b3_setter_minus_one_deselects_all(self):
        """B-3: Setting to -1 deselects all options; getter returns -1."""
        sel, opts = make_select()
        opts[0].set_attribute("selected", "")
        sel.selected_index = -1
        assert not any(opt.has_attribute("selected") for opt in opts)
        assert sel.selected_index == -1

    def test_b4_setter_out_of_range_deselects_all(self):
        """B-4: Setting to an out-of-range positive index deselects all."""
        sel, opts = make_select()
        opts[1].set_attribute("selected", "")
        sel.selected_index = 99
        assert not any(opt.has_attribute("selected") for opt in opts)
        assert sel.selected_index == -1

    def test_b5_getter_reflects_setter(self):
        """Getter accurately reflects the index set by the setter."""
        sel, opts = make_select()
        sel.selected_index = 2
        assert sel.selected_index == 2

    def test_b6_setter_zero_selects_first(self):
        """Setting to 0 selects the first option."""
        sel, opts = make_select()
        opts[2].set_attribute("selected", "")
        sel.selected_index = 0
        assert opts[0].has_attribute("selected")
        assert not opts[2].has_attribute("selected")


# ---------------------------------------------------------------------------
# Group C — selected_index setter (multiple-select)
# ---------------------------------------------------------------------------

class TestSelectedIndexSetterMultipleSelect:
    def test_c1_multiple_select_does_not_clear_other_selected(self):
        """C-1: On <select multiple>, setting an index does NOT remove selected from others."""
        sel, opts = make_select(multiple=True)
        opts[0].set_attribute("selected", "")
        sel.selected_index = 2
        # On multiple-select, previously selected options remain selected
        assert opts[0].has_attribute("selected")
        assert opts[2].has_attribute("selected")


# ---------------------------------------------------------------------------
# Group D — size
# ---------------------------------------------------------------------------

class TestSize:
    def test_d1_default_size_is_zero(self):
        """D-1: Default value is 0 when attribute absent."""
        doc = Document()
        sel = doc.create_element("select")
        assert sel.size == 0  # type: ignore[attr-defined]

    def test_d2_setter_updates_getter(self):
        """D-2: Setting to 3 makes getter return 3."""
        doc = Document()
        sel = doc.create_element("select")
        sel.size = 3  # type: ignore[attr-defined]
        assert sel.size == 3

    def test_d3_reflects_set_attribute(self):
        """D-3: Getter after set_attribute("size", "5") returns 5."""
        doc = Document()
        sel = doc.create_element("select")
        sel.set_attribute("size", "5")
        assert sel.size == 5

    def test_d4_non_integer_attribute_returns_zero(self):
        """D-4: Getter with non-integer attribute value (e.g. "abc") returns 0."""
        doc = Document()
        sel = doc.create_element("select")
        sel.set_attribute("size", "abc")
        assert sel.size == 0

    def test_d5_setter_writes_string_to_attribute(self):
        """Setter stores the value as a string attribute."""
        doc = Document()
        sel = doc.create_element("select")
        sel.size = 7  # type: ignore[attr-defined]
        assert sel.get_attribute("size") == "7"


# ---------------------------------------------------------------------------
# Group E — length
# ---------------------------------------------------------------------------

class TestLength:
    def test_e1_empty_select_length_zero(self):
        """E-1: Empty <select> returns 0."""
        doc = Document()
        sel = doc.create_element("select")
        assert sel.length == 0  # type: ignore[attr-defined]

    def test_e2_two_options_returns_two(self):
        """E-2: After appending two <option> children returns 2."""
        doc = Document()
        sel = doc.create_element("select")
        sel.append_child(doc.create_element("option"))
        sel.append_child(doc.create_element("option"))
        assert sel.length == 2

    def test_e3_non_option_children_not_counted(self):
        """E-3: Non-option children (e.g. <div>) are not counted."""
        doc = Document()
        sel = doc.create_element("select")
        sel.append_child(doc.create_element("div"))
        sel.append_child(doc.create_element("option"))
        sel.append_child(doc.create_element("span"))
        assert sel.length == 1


# ---------------------------------------------------------------------------
# Group F — doctest sweep
# ---------------------------------------------------------------------------

class TestDoctestSweep:
    def test_f1_doctest_modules_pass(self):
        """F-1: pytest --doctest-modules for _elements.py passes cleanly."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--doctest-modules",
                "src/aspose_html/dom/html/_elements.py",
                "-q",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, (
            f"doctest-modules failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


# ---------------------------------------------------------------------------
# Group G — interaction with selected_options
# ---------------------------------------------------------------------------

class TestSelectedOptionsInteraction:
    def test_g1_selected_index_setter_reflects_in_selected_options(self):
        """G-1: After selected_index = 1, selected_options has len 1 and is correct option."""
        sel, opts = make_select()
        sel.selected_index = 1
        assert len(sel.selected_options) == 1
        assert sel.selected_options[0] is opts[1]

    def test_g2_selected_index_minus_one_empties_selected_options(self):
        """G-2: After selected_index = -1, selected_options is empty."""
        sel, opts = make_select()
        opts[0].set_attribute("selected", "")
        sel.selected_index = -1
        assert len(sel.selected_options) == 0
