"""Tests for HTMLFormElement.elements —  / ."""
from __future__ import annotations

import pytest

from aspose_html.html_document import HTMLDocument
from aspose_html.dom import Document, HTMLFormElement, HTMLElement, HTMLOptionsCollection, ValidityState


@pytest.fixture()
def doc() -> Document:
    return Document()


@pytest.fixture()
def form_doc() -> HTMLDocument:
    return HTMLDocument.parse(
        "<form>"
        "<input name='q'>"
        "<button type='submit'>Go</button>"
        "<select name='s'><option>A</option></select>"
        "<textarea name='t'></textarea>"
        "<fieldset><input name='nested'></fieldset>"
        "<label>Not a control</label>"
        "</form>"
    )


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

class TestHTMLFormElementDispatch:
    def test_form_dispatch(self, doc: Document) -> None:
        el = doc.create_element("form")
        assert isinstance(el, HTMLFormElement)

    def test_form_is_html_element(self, doc: Document) -> None:
        el = doc.create_element("form")
        assert isinstance(el, HTMLElement)


# ---------------------------------------------------------------------------
# elements — basic inclusion / exclusion
# ---------------------------------------------------------------------------

class TestFormElementsCollection:
    def test_elements_returns_collection(self, form_doc: HTMLDocument) -> None:
        form = form_doc.query_selector("form")
        assert form is not None
        coll = form.elements
        assert coll is not None

    def test_elements_includes_input(self, form_doc: HTMLDocument) -> None:
        form = form_doc.query_selector("form")
        tags = [el.tag_name for el in form.elements]
        assert "INPUT" in tags

    def test_elements_includes_button(self, form_doc: HTMLDocument) -> None:
        form = form_doc.query_selector("form")
        tags = [el.tag_name for el in form.elements]
        assert "BUTTON" in tags

    def test_elements_includes_select(self, form_doc: HTMLDocument) -> None:
        form = form_doc.query_selector("form")
        tags = [el.tag_name for el in form.elements]
        assert "SELECT" in tags

    def test_elements_includes_textarea(self, form_doc: HTMLDocument) -> None:
        form = form_doc.query_selector("form")
        tags = [el.tag_name for el in form.elements]
        assert "TEXTAREA" in tags

    def test_elements_includes_fieldset(self, form_doc: HTMLDocument) -> None:
        form = form_doc.query_selector("form")
        tags = [el.tag_name for el in form.elements]
        assert "FIELDSET" in tags

    def test_elements_excludes_label(self, form_doc: HTMLDocument) -> None:
        form = form_doc.query_selector("form")
        tags = [el.tag_name for el in form.elements]
        assert "LABEL" not in tags

    def test_elements_excludes_option(self, form_doc: HTMLDocument) -> None:
        form = form_doc.query_selector("form")
        tags = [el.tag_name for el in form.elements]
        assert "OPTION" not in tags

    def test_elements_count(self, form_doc: HTMLDocument) -> None:
        # input, button, select, textarea, fieldset, input(nested) = 6
        form = form_doc.query_selector("form")
        assert len(form.elements) == 6


# ---------------------------------------------------------------------------
# elements — empty form
# ---------------------------------------------------------------------------

class TestFormElementsEmpty:
    def test_empty_form_length_zero(self, doc: Document) -> None:
        form = doc.create_element("form")
        assert len(form.elements) == 0

    def test_empty_form_iteration(self, doc: Document) -> None:
        form = doc.create_element("form")
        assert list(form.elements) == []


# ---------------------------------------------------------------------------
# elements — liveness
# ---------------------------------------------------------------------------

class TestFormElementsLive:
    def test_elements_live_after_append(self, doc: Document) -> None:
        form = doc.create_element("form")
        assert len(form.elements) == 0
        inp = doc.create_element("input")
        form.append_child(inp)
        assert len(form.elements) == 1

    def test_elements_live_after_remove(self, doc: Document) -> None:
        form = doc.create_element("form")
        inp = doc.create_element("input")
        form.append_child(inp)
        assert len(form.elements) == 1
        form.remove_child(inp)
        assert len(form.elements) == 0


# ---------------------------------------------------------------------------
# elements — tree order
# ---------------------------------------------------------------------------

class TestFormElementsOrder:
    def test_elements_tree_order(self, doc: Document) -> None:
        form = doc.create_element("form")
        inp = doc.create_element("input")
        btn = doc.create_element("button")
        form.append_child(inp)
        form.append_child(btn)
        tags = [el.tag_name for el in form.elements]
        assert tags == ["INPUT", "BUTTON"]

    def test_elements_includes_nested_descendants(self, doc: Document) -> None:
        form = doc.create_element("form")
        fieldset = doc.create_element("fieldset")
        inp = doc.create_element("input")
        fieldset.append_child(inp)
        form.append_child(fieldset)
        # both fieldset and the nested input should appear
        tags = [el.tag_name for el in form.elements]
        assert "FIELDSET" in tags
        assert "INPUT" in tags


# ---------------------------------------------------------------------------
# __slots__ unchanged
# ---------------------------------------------------------------------------

class TestHTMLFormElementSlots:
    def test_slots_contains_rel_list_cache(self, doc: Document) -> None:
        """: HTMLFormElement.__slots__ now includes _rel_list_cache."""
        form = doc.create_element("form")
        assert "_rel_list_cache" in HTMLFormElement.__slots__


class TestConstraintValidationAPI:
    def test_validity_state_exported_and_has_flags(self) -> None:
        state = ValidityState()
        assert state.valid is True
        assert state.custom_error is False
        assert state.value_missing is False

    def test_validity_state_flags_are_read_only(self) -> None:
        state = ValidityState(value_missing=True)
        with pytest.raises(AttributeError):
            state.value_missing = False

    def test_input_validity_flags_are_read_only_from_consumer(self, doc: Document) -> None:
        inp = doc.create_element("input")
        inp.required = True
        validity = inp.validity
        with pytest.raises(AttributeError):
            validity.custom_error = True

    def test_input_required_empty_is_invalid(self, doc: Document) -> None:
        inp = doc.create_element("input")
        inp.required = True
        assert inp.check_validity() is False
        assert inp.validity.value_missing is True

    def test_input_required_filled_is_valid(self, doc: Document) -> None:
        inp = doc.create_element("input")
        inp.required = True
        inp.value = "x"
        assert inp.check_validity() is True

    def test_input_custom_validity_sets_and_clears_custom_error(self, doc: Document) -> None:
        inp = doc.create_element("input")
        inp.set_custom_validity("bad")
        assert inp.validity.custom_error is True
        assert inp.validation_message == "bad"
        assert inp.validity.valid is False

        inp.set_custom_validity("")
        assert inp.validity.custom_error is False
        assert inp.validation_message == ""

    def test_input_pattern_mismatch(self, doc: Document) -> None:
        inp = doc.create_element("input")
        inp.pattern = "[0-9]+"
        inp.value = "abc"
        assert inp.validity.pattern_mismatch is True

    def test_input_too_long_and_too_short(self, doc: Document) -> None:
        inp = doc.create_element("input")
        inp.max_length = 3
        inp.value = "abcd"
        assert inp.validity.too_long is True

        inp2 = doc.create_element("input")
        inp2.min_length = 3
        inp2.value = "ab"
        assert inp2.validity.too_short is True

    def test_input_will_validate_false_for_disabled_and_hidden(self, doc: Document) -> None:
        inp = doc.create_element("input")
        inp.disabled = True
        assert inp.will_validate is False

        hidden = doc.create_element("input")
        hidden.type = "hidden"
        assert hidden.will_validate is False

    def test_textarea_constraints(self, doc: Document) -> None:
        ta = doc.create_element("textarea")
        ta.required = True
        assert ta.check_validity() is False
        assert ta.validity.value_missing is True

    def test_select_required_without_selection_is_invalid_and_selected_is_valid(self, doc: Document) -> None:
        sel = doc.create_element("select")
        sel.required = True
        assert sel.check_validity() is False

        opt = doc.create_element("option")
        opt.set_attribute("selected", "")
        opt.set_attribute("value", "x")
        sel.append_child(opt)
        assert sel.check_validity() is True

    def test_button_and_output_expose_validation_api_default_valid_true(self, doc: Document) -> None:
        button = doc.create_element("button")
        output = doc.create_element("output")
        assert button.check_validity() is True
        assert output.check_validity() is True
        button.set_custom_validity("bad")
        assert button.check_validity() is False


class TestSelectOptionsCollection:
    def test_options_is_live_collection(self, doc: Document) -> None:
        sel = doc.create_element("select")
        assert isinstance(sel.options, HTMLOptionsCollection)
        assert sel.options.length == 0

        opt = doc.create_element("option")
        sel.options.add(opt)
        assert sel.options.length == 1
        assert sel.options[0] is opt

    def test_options_item_and_named_item(self, doc: Document) -> None:
        sel = doc.create_element("select")
        opt = doc.create_element("option")
        opt.set_attribute("id", "o1")
        sel.append_child(opt)

        assert sel.options.item(0) is opt
        assert sel.options.item(9) is None
        assert sel.options.named_item("o1") is opt
        assert sel.options.namedItem("o1") is opt

    def test_options_remove_updates_dom(self, doc: Document) -> None:
        sel = doc.create_element("select")
        first = doc.create_element("option")
        second = doc.create_element("option")
        sel.append_child(first)
        sel.append_child(second)

        sel.options.remove(0)
        assert sel.options.length == 1
        assert sel.options[0] is second

    def test_options_add_before_index_and_node(self, doc: Document) -> None:
        sel = doc.create_element("select")
        a = doc.create_element("option")
        b = doc.create_element("option")
        c = doc.create_element("option")
        sel.append_child(a)
        sel.append_child(c)

        sel.options.add(b, 1)
        assert [opt is x for opt, x in zip(sel.options, [a, b, c])] == [True, True, True]

        d = doc.create_element("option")
        sel.options.add(d, c)
        assert [opt is x for opt, x in zip(sel.options, [a, b, d, c])] == [True, True, True, True]

    def test_selected_index_and_selected_options(self, doc: Document) -> None:
        sel = doc.create_element("select")
        a = doc.create_element("option")
        b = doc.create_element("option")
        c = doc.create_element("option")
        sel.append_child(a)
        sel.append_child(b)
        sel.append_child(c)

        assert sel.options.selected_index == -1
        assert sel.options.selectedIndex == -1
        assert len(sel.selected_options) == 0

        b.set_attribute("selected", "")
        c.set_attribute("selected", "")
        assert sel.options.selected_index == 1
        assert [opt is x for opt, x in zip(sel.selected_options, [b, c])] == [True, True]

    def test_options_includes_options_inside_optgroup(self, doc: Document) -> None:
        sel = doc.create_element("select")
        grp = doc.create_element("optgroup")
        opt = doc.create_element("option")
        grp.append_child(opt)
        sel.append_child(grp)

        assert sel.options.length == 1
        assert sel.options[0] is opt
