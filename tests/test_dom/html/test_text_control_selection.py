"""Tests for HTMLTextAreaElement and HTMLInputElement text-selection API stubs.

Covers WHATWG HTML §4.10.19.5 members added per  / .
"""

from __future__ import annotations

import pytest

from aspose_html.dom import Document
from aspose_html.dom.html._elements import HTMLInputElement, HTMLTextAreaElement
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def doc() -> Document:
    return Document()


@pytest.fixture()
def textarea(doc: Document) -> HTMLTextAreaElement:
    el = doc.create_element("textarea")
    assert isinstance(el, HTMLTextAreaElement)
    return el  # type: ignore[return-value]


@pytest.fixture()
def input_el(doc: Document) -> HTMLInputElement:
    el = doc.create_element("input")
    assert isinstance(el, HTMLInputElement)
    return el  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# HTMLTextAreaElement —  AC #1–#5
# ---------------------------------------------------------------------------


class TestHTMLTextAreaElementSelection:
    def test_selection_start_returns_zero(self, textarea: HTMLTextAreaElement) -> None:
        """AC #1 — selection_start is always 0."""
        assert textarea.selection_start == 0

    def test_selection_end_returns_zero(self, textarea: HTMLTextAreaElement) -> None:
        """AC #2 — selection_end is always 0."""
        assert textarea.selection_end == 0

    def test_selection_direction_returns_none_str(
        self, textarea: HTMLTextAreaElement
    ) -> None:
        """AC #3 — selection_direction is always 'none'."""
        assert textarea.selection_direction == "none"

    def test_set_selection_range_callable(self, textarea: HTMLTextAreaElement) -> None:
        """AC #4 — set_selection_range(0, 5) callable without error."""
        textarea.set_selection_range(0, 5)  # no-op, no exception

    def test_set_selection_range_with_direction(
        self, textarea: HTMLTextAreaElement
    ) -> None:
        """AC #5 variant — set_selection_range with direction kwarg."""
        textarea.set_selection_range(0, 5, "forward")  # no-op, no exception

    def test_set_selection_range_backward_direction(
        self, textarea: HTMLTextAreaElement
    ) -> None:
        textarea.set_selection_range(2, 8, direction="backward")  # no exception

    def test_select_callable(self, textarea: HTMLTextAreaElement) -> None:
        """AC #5 — select() callable without error."""
        textarea.select()  # no-op, no exception

    def test_no_new_slots(self, textarea: HTMLTextAreaElement) -> None:
        """AC #8 — no new __slots__ added."""
        assert "__slots__" not in HTMLTextAreaElement.__dict__ or set(
            HTMLTextAreaElement.__slots__  # type: ignore[attr-defined]
        ) == {"_custom_validity_message"}

    def test_properties_are_readonly(self, textarea: HTMLTextAreaElement) -> None:
        """selection_start, selection_end, selection_direction are read-only."""
        with pytest.raises(AttributeError):
            textarea.selection_start = 5  # type: ignore[misc]
        with pytest.raises(AttributeError):
            textarea.selection_end = 5  # type: ignore[misc]
        with pytest.raises(AttributeError):
            textarea.selection_direction = "forward"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# HTMLInputElement —  AC #6
# ---------------------------------------------------------------------------


class TestHTMLInputElementSelection:
    def test_selection_start_returns_zero(self, input_el: HTMLInputElement) -> None:
        """AC #7 — selection_start is always 0."""
        assert input_el.selection_start == 0

    def test_selection_end_returns_zero(self, input_el: HTMLInputElement) -> None:
        """AC #8 — selection_end is always 0."""
        assert input_el.selection_end == 0

    def test_selection_direction_returns_none_str(
        self, input_el: HTMLInputElement
    ) -> None:
        """AC #9 — selection_direction is always 'none'."""
        assert input_el.selection_direction == "none"

    def test_set_selection_range_callable(self, input_el: HTMLInputElement) -> None:
        """AC #10 — set_selection_range(0, 3) callable without error."""
        input_el.set_selection_range(0, 3)  # no-op, no exception

    def test_set_selection_range_with_direction(
        self, input_el: HTMLInputElement
    ) -> None:
        input_el.set_selection_range(0, 3, "forward")  # no exception

    def test_select_callable(self, input_el: HTMLInputElement) -> None:
        """AC #11 — select() callable without error."""
        input_el.select()  # no-op, no exception

    def test_no_new_slots(self, input_el: HTMLInputElement) -> None:
        """Selection API does not add slots beyond existing input state slots."""
        assert "__slots__" not in HTMLInputElement.__dict__ or set(
            HTMLInputElement.__slots__  # type: ignore[attr-defined]
        ) == {"_custom_validity_message", "_indeterminate"}

    def test_properties_are_readonly(self, input_el: HTMLInputElement) -> None:
        """selection_start, selection_end, selection_direction are read-only."""
        with pytest.raises(AttributeError):
            input_el.selection_start = 5  # type: ignore[misc]
        with pytest.raises(AttributeError):
            input_el.selection_end = 5  # type: ignore[misc]
        with pytest.raises(AttributeError):
            input_el.selection_direction = "forward"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Parsed document —  AC #7
# ---------------------------------------------------------------------------


class TestSelectionAPIViaParsedDocument:
    def test_textarea_parsed_selection_start(self) -> None:
        """AC #7 — textarea selection_start accessible via a parsed document."""
        doc = HTMLDocument.parse("<html><body><textarea id='t'></textarea></body></html>")
        ta = doc.get_element_by_id("t")
        assert isinstance(ta, HTMLTextAreaElement)
        assert ta.selection_start == 0

    def test_textarea_parsed_selection_end(self) -> None:
        doc = HTMLDocument.parse("<html><body><textarea id='t'></textarea></body></html>")
        ta = doc.get_element_by_id("t")
        assert isinstance(ta, HTMLTextAreaElement)
        assert ta.selection_end == 0

    def test_textarea_parsed_selection_direction(self) -> None:
        doc = HTMLDocument.parse("<html><body><textarea id='t'></textarea></body></html>")
        ta = doc.get_element_by_id("t")
        assert isinstance(ta, HTMLTextAreaElement)
        assert ta.selection_direction == "none"

    def test_input_parsed_selection_start(self) -> None:
        """AC #7 — input selection_start accessible via a parsed document."""
        doc = HTMLDocument.parse("<html><body><input id='i' /></body></html>")
        inp = doc.get_element_by_id("i")
        assert isinstance(inp, HTMLInputElement)
        assert inp.selection_start == 0

    def test_input_parsed_selection_end(self) -> None:
        doc = HTMLDocument.parse("<html><body><input id='i' /></body></html>")
        inp = doc.get_element_by_id("i")
        assert isinstance(inp, HTMLInputElement)
        assert inp.selection_end == 0

    def test_input_parsed_selection_direction(self) -> None:
        doc = HTMLDocument.parse("<html><body><input id='i' /></body></html>")
        inp = doc.get_element_by_id("i")
        assert isinstance(inp, HTMLInputElement)
        assert inp.selection_direction == "none"

    def test_textarea_parsed_set_selection_range(self) -> None:
        doc = HTMLDocument.parse("<html><body><textarea id='t'></textarea></body></html>")
        ta = doc.get_element_by_id("t")
        assert isinstance(ta, HTMLTextAreaElement)
        ta.set_selection_range(0, 5)  # no-op, no exception

    def test_input_parsed_select(self) -> None:
        doc = HTMLDocument.parse("<html><body><input id='i' /></body></html>")
        inp = doc.get_element_by_id("i")
        assert isinstance(inp, HTMLInputElement)
        inp.select()  # no-op, no exception
