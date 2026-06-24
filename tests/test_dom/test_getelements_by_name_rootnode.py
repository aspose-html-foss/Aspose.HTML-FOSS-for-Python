"""Tests for : Document.get_elements_by_name() and Node.get_root_node().

Covers all acceptance criteria from .
"""
import pytest

from aspose_html.dom import Document


# ---------------------------------------------------------------------------
# Document.get_elements_by_name
# ---------------------------------------------------------------------------

class TestGetElementsByName:
    def test_returns_matching_elements(self) -> None:
        from aspose_html.html_document import HTMLDocument  # noqa: PLC0415
        doc = HTMLDocument.parse(
            '<body><input name="q"><input name="q"><input name="x"></body>'
        )
        coll = doc.get_elements_by_name("q")
        assert len(coll) == 2

    def test_empty_result_when_no_match(self) -> None:
        from aspose_html.html_document import HTMLDocument  # noqa: PLC0415
        doc = HTMLDocument.parse('<body><input name="q"></body>')
        coll = doc.get_elements_by_name("missing")
        assert len(coll) == 0

    def test_case_sensitive_q_vs_Q(self) -> None:
        from aspose_html.html_document import HTMLDocument  # noqa: PLC0415
        doc = HTMLDocument.parse('<body><input name="q"></body>')
        assert len(doc.get_elements_by_name("q")) == 1
        assert len(doc.get_elements_by_name("Q")) == 0

    def test_is_live_reflects_mutations(self) -> None:
        doc = Document()
        container = doc.create_element("div")
        doc.append_child(container)
        inp1 = doc.create_element("input")
        inp1.set_attribute("name", "q")
        container.append_child(inp1)
        coll = doc.get_elements_by_name("q")
        assert len(coll) == 1
        # Mutate: add another matching element
        inp2 = doc.create_element("input")
        inp2.set_attribute("name", "q")
        container.append_child(inp2)
        # Same collection object now reflects the mutation
        assert len(coll) == 2

    def test_elements_without_name_attribute_excluded(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        # "" is a valid name value — div has no name attribute at all,
        # so it should NOT match name=""
        coll = doc.get_elements_by_name("")
        assert len(coll) == 0

    def test_element_with_empty_name_matches_empty_string(self) -> None:
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("name", "")
        doc.append_child(inp)
        coll = doc.get_elements_by_name("")
        assert len(coll) == 1

    def test_returns_collection_object(self) -> None:
        doc = Document()
        # Returns a collection (not a list or None)
        coll = doc.get_elements_by_name("anything")
        assert hasattr(coll, "__len__")
        assert hasattr(coll, "__iter__")

    def test_single_element_can_be_accessed_by_index(self) -> None:
        doc = Document()
        inp = doc.create_element("input")
        inp.set_attribute("name", "q")
        doc.append_child(inp)
        coll = doc.get_elements_by_name("q")
        assert coll[0] is inp

    def test_all_element_types_matched_not_just_form_controls(self) -> None:
        doc = Document()
        container = doc.create_element("div")
        doc.append_child(container)
        div = doc.create_element("div")
        div.set_attribute("name", "section")
        container.append_child(div)
        span = doc.create_element("span")
        span.set_attribute("name", "section")
        container.append_child(span)
        coll = doc.get_elements_by_name("section")
        assert len(coll) == 2


# ---------------------------------------------------------------------------
# Node.get_root_node
# ---------------------------------------------------------------------------

class TestGetRootNode:
    def test_attached_returns_document(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        assert el.get_root_node() is doc

    def test_detached_element_returns_self(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        assert el.get_root_node() is el

    def test_detached_subtree_returns_topmost_ancestor(self) -> None:
        doc = Document()
        parent = doc.create_element("div")
        child = doc.create_element("span")
        parent.append_child(child)
        # parent is not attached to doc
        assert child.get_root_node() is parent

    def test_document_returns_self(self) -> None:
        doc = Document()
        assert doc.get_root_node() is doc

    def test_composed_true_accepted_and_returns_same_result(self) -> None:
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        assert el.get_root_node(composed=True) is doc
        assert el.get_root_node(composed=False) is doc
        assert el.get_root_node() is doc

    def test_deeply_nested_element_returns_document(self) -> None:
        doc = Document()
        outer = doc.create_element("div")
        inner = doc.create_element("p")
        leaf = doc.create_element("span")
        doc.append_child(outer)
        outer.append_child(inner)
        inner.append_child(leaf)
        assert leaf.get_root_node() is doc

    def test_text_node_attached_returns_document(self) -> None:
        doc = Document()
        el = doc.create_element("p")
        text = doc.create_text_node("hello")
        doc.append_child(el)
        el.append_child(text)
        assert text.get_root_node() is doc

    def test_text_node_detached_returns_self(self) -> None:
        doc = Document()
        text = doc.create_text_node("hello")
        assert text.get_root_node() is text

    def test_composed_is_keyword_only(self) -> None:
        """composed must be passed as keyword argument (*, composed=...)."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        with pytest.raises(TypeError):
            el.get_root_node(True)  # type: ignore[call-arg]  # positional not allowed
