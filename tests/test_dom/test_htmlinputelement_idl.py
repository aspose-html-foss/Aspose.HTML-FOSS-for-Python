"""Tests for HTMLInputElement IDL completeness — .

Covers the seven new properties added in  / :
  step, min, max, multiple, value_as_number, files, list.

Test groups
-----------
A — step / min / max (string-reflected attributes)
B — multiple (boolean presence attribute)
C — value_as_number getter
D — value_as_number setter (type validation)
E — files / list stubs
"""

import math

import pytest

from aspose_html.dom import Document
from aspose_html.dom._exceptions import InvalidStateError
from aspose_html.dom.html._elements import HTMLInputElement


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_input(type_: str = "text") -> HTMLInputElement:
    doc = Document()
    inp = doc.create_element("input")
    if type_ != "text":
        inp.set_attribute("type", type_)
    return inp  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Group A — step / min / max
# ---------------------------------------------------------------------------

class TestStepMinMax:
    def test_step_default_empty(self):
        # AC-1
        inp = make_input()
        assert inp.step == ""

    def test_min_default_empty(self):
        # AC-1
        inp = make_input()
        assert inp.min == ""

    def test_max_default_empty(self):
        # AC-1
        inp = make_input()
        assert inp.max == ""

    def test_step_reflects_set_attribute(self):
        # AC-2
        inp = make_input()
        inp.set_attribute("step", "0.5")
        assert inp.step == "0.5"

    def test_min_reflects_set_attribute(self):
        inp = make_input()
        inp.set_attribute("min", "10")
        assert inp.min == "10"

    def test_max_reflects_set_attribute(self):
        inp = make_input()
        inp.set_attribute("max", "99")
        assert inp.max == "99"

    def test_step_setter_writes_attribute(self):
        # AC-3
        inp = make_input()
        inp.step = "any"
        assert inp.get_attribute("step") == "any"

    def test_min_setter_writes_attribute(self):
        inp = make_input()
        inp.min = "0"
        assert inp.get_attribute("min") == "0"

    def test_max_setter_writes_attribute(self):
        inp = make_input()
        inp.max = "100"
        assert inp.get_attribute("max") == "100"

    def test_step_round_trip(self):
        inp = make_input()
        inp.step = "5"
        assert inp.step == "5"

    def test_min_round_trip(self):
        inp = make_input()
        inp.min = "1"
        assert inp.min == "1"

    def test_max_round_trip(self):
        inp = make_input()
        inp.max = "50"
        assert inp.max == "50"


# ---------------------------------------------------------------------------
# Group B — multiple
# ---------------------------------------------------------------------------

class TestMultiple:
    def test_multiple_default_false(self):
        # AC-4
        inp = make_input()
        assert inp.multiple is False

    def test_multiple_set_true_adds_attribute(self):
        # AC-4
        inp = make_input()
        inp.multiple = True
        assert inp.multiple is True
        assert inp.has_attribute("multiple")

    def test_multiple_set_false_removes_attribute(self):
        inp = make_input()
        inp.multiple = True
        inp.multiple = False
        assert inp.multiple is False
        assert not inp.has_attribute("multiple")

    def test_multiple_attribute_value_is_empty_string(self):
        # boolean attribute stores ""
        inp = make_input()
        inp.multiple = True
        assert inp.get_attribute("multiple") == ""

    def test_multiple_via_set_attribute(self):
        inp = make_input()
        inp.set_attribute("multiple", "")
        assert inp.multiple is True

    def test_multiple_returns_bool_type(self):
        inp = make_input()
        assert isinstance(inp.multiple, bool)


# ---------------------------------------------------------------------------
# Group C — value_as_number getter
# ---------------------------------------------------------------------------

class TestValueAsNumberGetter:
    def test_valid_float(self):
        # AC-5
        inp = make_input()
        inp.value = "3.14"
        assert inp.value_as_number == pytest.approx(3.14)

    def test_valid_integer(self):
        inp = make_input()
        inp.value = "42"
        assert inp.value_as_number == pytest.approx(42.0)

    def test_non_parseable_returns_nan(self):
        # AC-6
        inp = make_input()
        inp.value = "not-a-number"
        assert math.isnan(inp.value_as_number)

    def test_empty_string_returns_nan(self):
        inp = make_input()
        inp.value = ""
        assert math.isnan(inp.value_as_number)

    def test_negative_float(self):
        inp = make_input()
        inp.value = "-7.5"
        assert inp.value_as_number == pytest.approx(-7.5)

    def test_scientific_notation(self):
        inp = make_input()
        inp.value = "1e3"
        assert inp.value_as_number == pytest.approx(1000.0)


# ---------------------------------------------------------------------------
# Group D — value_as_number setter
# ---------------------------------------------------------------------------

class TestValueAsNumberSetter:
    def test_type_number_sets_value(self):
        # AC-8
        inp = make_input("number")
        inp.value_as_number = 42.0
        assert inp.value == "42.0"

    def test_type_range_sets_value(self):
        inp = make_input("range")
        inp.value_as_number = 7.5
        assert inp.value == "7.5"

    def test_type_text_raises_invalid_state_error(self):
        # AC-7
        inp = make_input("text")
        with pytest.raises(InvalidStateError):
            inp.value_as_number = 5.0

    def test_type_search_raises_invalid_state_error(self):
        inp = make_input("search")
        with pytest.raises(InvalidStateError):
            inp.value_as_number = 1.0

    def test_type_password_raises_invalid_state_error(self):
        inp = make_input("password")
        with pytest.raises(InvalidStateError):
            inp.value_as_number = 0.0

    def test_type_email_raises_invalid_state_error(self):
        inp = make_input("email")
        with pytest.raises(InvalidStateError):
            inp.value_as_number = 3.0

    def test_type_hidden_raises_invalid_state_error(self):
        inp = make_input("hidden")
        with pytest.raises(InvalidStateError):
            inp.value_as_number = 2.0

    def test_type_url_raises_invalid_state_error(self):
        inp = make_input("url")
        with pytest.raises(InvalidStateError):
            inp.value_as_number = 9.0

    def test_type_tel_raises_invalid_state_error(self):
        inp = make_input("tel")
        with pytest.raises(InvalidStateError):
            inp.value_as_number = 4.0

    def test_error_message_contains_type(self):
        inp = make_input("text")
        with pytest.raises(InvalidStateError, match="text"):
            inp.value_as_number = 5.0


# ---------------------------------------------------------------------------
# Group E — files / list stubs
# ---------------------------------------------------------------------------

class TestFilesAndList:
    def test_files_is_none(self):
        # AC-9
        inp = make_input()
        assert inp.files is None

    def test_list_is_none(self):
        # AC-10
        inp = make_input()
        assert inp.list is None

    def test_files_none_for_file_type(self):
        inp = make_input("file")
        assert inp.files is None

    def test_list_none_regardless_of_type(self):
        inp = make_input("number")
        assert inp.list is None
