"""Tests for HTMLSummaryElement and HTMLMenuElement stubs — BACK-187 / ADR-170.

Covers all acceptance criteria from ADR-170:
  AC-1  doc.create_element('summary') returns HTMLSummaryElement
  AC-2  doc.create_element('menu') returns HTMLMenuElement
  AC-3  isinstance(el, HTMLElement) is True for both
  AC-4  Parsed <details><summary>…</summary></details> summary child is HTMLSummaryElement
  AC-5  Parsed <menu><li>item</li></menu> menu element is HTMLMenuElement
  AC-6  from aspose_html.dom import HTMLSummaryElement, HTMLMenuElement imports without error
  AC-7  Serialising an HTMLSummaryElement produces <summary>…</summary> (not self-closing)
  AC-8  Serialising an HTMLMenuElement produces <menu>…</menu>
  AC-9  All new docstring examples pass pytest --doctest-modules (covered by CI)
"""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    Document,
    Element,
    HTMLElement,
    HTMLSummaryElement,
    HTMLMenuElement,
)
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# AC-1 / AC-2: create_element dispatch
# ---------------------------------------------------------------------------

class TestDispatch:
    def test_create_summary_returns_html_summary_element(self, doc: Document) -> None:
        """AC-1: create_element('summary') returns HTMLSummaryElement."""
        el = doc.create_element("summary")
        assert isinstance(el, HTMLSummaryElement)
        assert type(el) is HTMLSummaryElement

    def test_create_menu_returns_html_menu_element(self, doc: Document) -> None:
        """AC-2: create_element('menu') returns HTMLMenuElement."""
        el = doc.create_element("menu")
        assert isinstance(el, HTMLMenuElement)
        assert type(el) is HTMLMenuElement


# ---------------------------------------------------------------------------
# AC-3: isinstance hierarchy
# ---------------------------------------------------------------------------

class TestIsInstanceHierarchy:
    def test_summary_is_html_element(self, doc: Document) -> None:
        """AC-3: HTMLSummaryElement is an HTMLElement and Element."""
        el = doc.create_element("summary")
        assert isinstance(el, HTMLElement)
        assert isinstance(el, Element)

    def test_menu_is_html_element(self, doc: Document) -> None:
        """AC-3: HTMLMenuElement is an HTMLElement and Element."""
        el = doc.create_element("menu")
        assert isinstance(el, HTMLElement)
        assert isinstance(el, Element)

    def test_summary_tag_name_uppercased(self, doc: Document) -> None:
        el = doc.create_element("summary")
        assert el.tag_name == "SUMMARY"

    def test_menu_tag_name_uppercased(self, doc: Document) -> None:
        el = doc.create_element("menu")
        assert el.tag_name == "MENU"


# ---------------------------------------------------------------------------
# AC-4 / AC-5: Tree builder produces typed instances from parsed HTML
# ---------------------------------------------------------------------------

class TestParsedHtml:
    def test_summary_child_of_details_is_typed(self) -> None:
        """AC-4: Parsed <details><summary>…</summary></details> summary is HTMLSummaryElement."""
        html_doc = HTMLDocument.parse("<details><summary>Open</summary></details>")
        details = html_doc.query_selector("details")
        assert details is not None
        # Find the first element child named SUMMARY
        summary = None
        for child in details.child_nodes:
            if hasattr(child, "tag_name") and child.tag_name == "SUMMARY":
                summary = child
                break
        assert summary is not None
        assert isinstance(summary, HTMLSummaryElement)

    def test_menu_element_is_typed_after_parse(self) -> None:
        """AC-5: Parsed <menu><li>item</li></menu> menu element is HTMLMenuElement."""
        html_doc = HTMLDocument.parse("<menu><li>item</li></menu>")
        menu = html_doc.query_selector("menu")
        assert menu is not None
        assert isinstance(menu, HTMLMenuElement)


# ---------------------------------------------------------------------------
# AC-6: Importable from aspose_html.dom
# ---------------------------------------------------------------------------

class TestImports:
    def test_import_from_dom(self) -> None:
        """AC-6: Both classes importable from aspose_html.dom without error."""
        from aspose_html.dom import HTMLSummaryElement as S, HTMLMenuElement as M  # noqa: PLC0415
        assert S is not None
        assert M is not None

    def test_import_from_dom_html(self) -> None:
        from aspose_html.dom.html import HTMLSummaryElement as S, HTMLMenuElement as M  # noqa: PLC0415
        assert S is not None
        assert M is not None

    def test_in_dom_all(self) -> None:
        import aspose_html.dom as dom  # noqa: PLC0415
        assert "HTMLSummaryElement" in dom.__all__
        assert "HTMLMenuElement" in dom.__all__

    def test_in_dom_html_all(self) -> None:
        import aspose_html.dom.html as dom_html  # noqa: PLC0415
        assert "HTMLSummaryElement" in dom_html.__all__
        assert "HTMLMenuElement" in dom_html.__all__


# ---------------------------------------------------------------------------
# AC-7 / AC-8: Serialisation produces open/close tags, not self-closing
# ---------------------------------------------------------------------------

class TestSerialisation:
    def test_summary_serialises_with_open_close_tags(self, doc: Document) -> None:
        """AC-7: <summary>…</summary> — not a void/self-closing element."""
        el = doc.create_element("summary")
        assert el.outer_html == "<summary></summary>"

    def test_menu_serialises_with_open_close_tags(self, doc: Document) -> None:
        """AC-8: <menu>…</menu> — not a void/self-closing element."""
        el = doc.create_element("menu")
        assert el.outer_html == "<menu></menu>"

    def test_summary_with_text_content_serialises_correctly(self, doc: Document) -> None:
        el = doc.create_element("summary")
        el.append_child(doc.create_text_node("Details"))
        assert el.outer_html == "<summary>Details</summary>"

    def test_menu_with_child_serialises_correctly(self, doc: Document) -> None:
        el = doc.create_element("menu")
        li = doc.create_element("li")
        li.append_child(doc.create_text_node("item"))
        el.append_child(li)
        assert el.outer_html == "<menu><li>item</li></menu>"


# ---------------------------------------------------------------------------
# Clone preserves concrete subclass
# ---------------------------------------------------------------------------

class TestClone:
    @pytest.mark.parametrize("tag", ["summary", "menu"])
    def test_clone_node_preserves_subclass(self, doc: Document, tag: str) -> None:
        el = doc.create_element(tag)
        clone = el.clone_node(deep=True)
        assert type(clone) is type(el)

    def test_summary_clone_copies_attributes(self, doc: Document) -> None:
        el = doc.create_element("summary")
        el.set_attribute("id", "s1")
        clone = el.clone_node(deep=True)
        assert isinstance(clone, HTMLSummaryElement)
        assert clone.get_attribute("id") == "s1"

    def test_menu_clone_copies_attributes(self, doc: Document) -> None:
        el = doc.create_element("menu")
        el.set_attribute("class", "toolbar")
        clone = el.clone_node(deep=True)
        assert isinstance(clone, HTMLMenuElement)
        assert clone.get_attribute("class") == "toolbar"
