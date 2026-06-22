"""Tests for the Range API (BACK-47, ADR-044, WHATWG DOM §5)."""
from __future__ import annotations

import pytest

from aspose_html.dom import (
    AbstractRange,
    Document,
    DocumentFragment,
    IndexSizeError,
    InvalidStateError,
    NotSupportedError,
    Range,
    StaticRange,
    WrongDocumentError,
)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestCreateRange:
    def test_range_class_subclasses_abstract_range(self) -> None:
        assert issubclass(Range, AbstractRange)

    def test_create_range_returns_range_instance(self) -> None:
        doc = Document()
        r = doc.create_range()
        assert isinstance(r, Range)

    def test_freshly_created_range_is_collapsed_at_document(self) -> None:
        doc = Document()
        r = doc.create_range()
        assert r.collapsed is True
        assert r.start_container is doc
        assert r.end_container is doc
        assert r.start_offset == 0
        assert r.end_offset == 0

    def test_range_is_abstract_range_subclass_instance(self) -> None:
        doc = Document()
        r = doc.create_range()
        assert isinstance(r, AbstractRange)

    def test_abstract_range_properties_are_read_only(self) -> None:
        doc = Document()
        r = doc.create_range()

        with pytest.raises(AttributeError):
            r.start_container = doc  # type: ignore[misc]
        with pytest.raises(AttributeError):
            r.start_offset = 1  # type: ignore[misc]
        with pytest.raises(AttributeError):
            r.end_container = doc  # type: ignore[misc]
        with pytest.raises(AttributeError):
            r.end_offset = 1  # type: ignore[misc]
        with pytest.raises(AttributeError):
            r.collapsed = False  # type: ignore[misc]

    def test_range_importable_from_aspose_html_dom(self) -> None:
        # Acceptance criterion #11.
        from aspose_html import dom
        assert hasattr(dom, "Range")
        assert dom.Range is Range

    def test_abstract_range_importable_from_aspose_html_dom(self) -> None:
        from aspose_html import dom
        assert hasattr(dom, "AbstractRange")
        assert dom.AbstractRange is AbstractRange

    def test_static_range_importable_from_aspose_html_dom(self) -> None:
        from aspose_html import dom
        assert hasattr(dom, "StaticRange")
        assert dom.StaticRange is StaticRange


class TestStaticRange:
    def _setup_text(self) -> tuple[Document, "Document.Text"]:  # type: ignore[name-defined]
        doc = Document()
        root = doc.create_element("root")
        doc.append_child(root)
        text = doc.create_text_node("hello")
        root.append_child(text)
        return doc, text

    def test_static_range_subclasses_abstract_range(self) -> None:
        assert issubclass(StaticRange, AbstractRange)

    def test_constructor_happy_path_sets_endpoints(self) -> None:
        _, text = self._setup_text()
        sr = StaticRange(
            {
                "start_container": text,
                "start_offset": 1,
                "end_container": text,
                "end_offset": 4,
            }
        )
        assert sr.start_container is text
        assert sr.start_offset == 1
        assert sr.end_container is text
        assert sr.end_offset == 4
        assert sr.collapsed is False
        assert sr.to_string() == "ell"

    def test_constructor_missing_required_key_raises_type_error(self) -> None:
        _, text = self._setup_text()
        with pytest.raises(TypeError):
            StaticRange(
                {
                    "start_container": text,
                    "start_offset": 0,
                    "end_container": text,
                }
            )

    def test_constructor_rejects_non_node_containers(self) -> None:
        _, text = self._setup_text()
        with pytest.raises(TypeError):
            StaticRange(
                {
                    "start_container": "not-a-node",
                    "start_offset": 0,
                    "end_container": text,
                    "end_offset": 1,
                }
            )

    def test_constructor_rejects_non_int_offsets(self) -> None:
        _, text = self._setup_text()
        with pytest.raises(TypeError):
            StaticRange(
                {
                    "start_container": text,
                    "start_offset": "1",
                    "end_container": text,
                    "end_offset": 1,
                }
            )

    def test_constructor_rejects_out_of_range_offsets(self) -> None:
        _, text = self._setup_text()
        with pytest.raises(IndexSizeError):
            StaticRange(
                {
                    "start_container": text,
                    "start_offset": 0,
                    "end_container": text,
                    "end_offset": 99,
                }
            )

    def test_constructor_rejects_cross_document_boundaries(self) -> None:
        doc1 = Document()
        doc2 = Document()
        t1 = doc1.create_text_node("abc")
        t2 = doc2.create_text_node("abc")
        with pytest.raises(WrongDocumentError):
            StaticRange(
                {
                    "start_container": t1,
                    "start_offset": 0,
                    "end_container": t2,
                    "end_offset": 1,
                }
            )

    def test_constructor_rejects_start_after_end(self) -> None:
        _, text = self._setup_text()
        with pytest.raises(TypeError):
            StaticRange(
                {
                    "start_container": text,
                    "start_offset": 4,
                    "end_container": text,
                    "end_offset": 1,
                }
            )

    def test_endpoint_properties_are_immutable(self) -> None:
        _, text = self._setup_text()
        sr = StaticRange(
            {
                "start_container": text,
                "start_offset": 1,
                "end_container": text,
                "end_offset": 3,
            }
        )
        with pytest.raises(AttributeError):
            sr.start_container = text  # type: ignore[misc]
        with pytest.raises(AttributeError):
            sr.start_offset = 0  # type: ignore[misc]
        with pytest.raises(AttributeError):
            sr.end_container = text  # type: ignore[misc]
        with pytest.raises(AttributeError):
            sr.end_offset = 0  # type: ignore[misc]
        with pytest.raises(AttributeError):
            sr.collapsed = True  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Boundary setters
# ---------------------------------------------------------------------------


class TestBoundarySetters:
    def _setup(self) -> tuple[Document, "Document.Element", "Document.Text"]:  # type: ignore[name-defined]
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello world")
        p.append_child(t)
        return doc, p, t

    def test_set_start_assigns_start_boundary(self) -> None:
        doc, _, t = self._setup()
        r = doc.create_range()
        r.set_end(t, 11)  # set end first to avoid auto-collapse
        r.set_start(t, 2)
        assert r.start_container is t
        assert r.start_offset == 2

    def test_set_end_assigns_end_boundary(self) -> None:
        doc, _, t = self._setup()
        r = doc.create_range()
        r.set_end(t, 5)
        assert r.end_container is t
        assert r.end_offset == 5

    def test_set_start_after_end_collapses_range(self) -> None:
        doc, _, t = self._setup()
        r = doc.create_range()
        r.set_start(t, 0)
        r.set_end(t, 5)
        # Now move start past current end: should collapse to new start.
        r.set_start(t, 8)
        assert r.collapsed is True
        assert r.start_offset == 8
        assert r.end_offset == 8

    def test_set_end_before_start_collapses_range(self) -> None:
        doc, _, t = self._setup()
        r = doc.create_range()
        r.set_start(t, 5)
        r.set_end(t, 8)
        # Now set end before start: should collapse to new end.
        r.set_end(t, 2)
        assert r.collapsed is True
        assert r.start_offset == 2
        assert r.end_offset == 2

    def test_set_start_negative_offset_raises(self) -> None:
        doc, _, t = self._setup()
        r = doc.create_range()
        with pytest.raises(IndexSizeError):
            r.set_start(t, -1)

    def test_set_start_offset_too_large_raises(self) -> None:
        doc, _, t = self._setup()
        r = doc.create_range()
        with pytest.raises(IndexSizeError):
            r.set_start(t, 100)

    def test_set_start_before(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        span = doc.create_element("span")
        div.append_child(span)
        r = doc.create_range()
        r.set_start_before(span)
        assert r.start_container is div
        assert r.start_offset == 0

    def test_set_start_after(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        span = doc.create_element("span")
        div.append_child(span)
        r = doc.create_range()
        r.set_start_after(span)
        assert r.start_container is div
        assert r.start_offset == 1

    def test_set_end_before(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        span = doc.create_element("span")
        div.append_child(span)
        r = doc.create_range()
        r.set_end_before(span)
        assert r.end_container is div
        assert r.end_offset == 0

    def test_set_end_after(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        span = doc.create_element("span")
        div.append_child(span)
        r = doc.create_range()
        r.set_end_after(span)
        assert r.end_container is div
        assert r.end_offset == 1

    def test_set_start_before_orphan_raises(self) -> None:
        doc = Document()
        orphan = doc.create_element("span")
        r = doc.create_range()
        with pytest.raises(InvalidStateError):
            r.set_start_before(orphan)

    def test_select_node(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        span = doc.create_element("span")
        div.append_child(span)
        r = doc.create_range()
        r.select_node(span)
        assert r.start_container is div
        assert r.start_offset == 0
        assert r.end_container is div
        assert r.end_offset == 1

    def test_select_node_orphan_raises(self) -> None:
        doc = Document()
        orphan = doc.create_element("span")
        r = doc.create_range()
        with pytest.raises(InvalidStateError):
            r.select_node(orphan)

    def test_select_node_contents_element(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        a = doc.create_element("a")
        b = doc.create_element("b")
        div.append_child(a)
        div.append_child(b)
        r = doc.create_range()
        r.select_node_contents(div)
        assert r.start_container is div
        assert r.start_offset == 0
        assert r.end_container is div
        assert r.end_offset == 2

    def test_select_node_contents_text(self) -> None:
        doc = Document()
        t = doc.create_text_node("hello")
        r = doc.create_range()
        r.select_node_contents(t)
        assert r.start_offset == 0
        assert r.end_offset == 5  # length of 'hello'

    def test_collapse_to_start(self) -> None:
        doc, _, t = self._setup()
        r = doc.create_range()
        r.set_start(t, 1)
        r.set_end(t, 4)
        r.collapse(to_start=True)
        assert r.collapsed is True
        assert r.start_offset == 1
        assert r.end_offset == 1

    def test_collapse_to_end(self) -> None:
        doc, _, t = self._setup()
        r = doc.create_range()
        r.set_start(t, 1)
        r.set_end(t, 4)
        r.collapse(to_start=False)
        assert r.collapsed is True
        assert r.start_offset == 4
        assert r.end_offset == 4


# ---------------------------------------------------------------------------
# Common ancestor
# ---------------------------------------------------------------------------


class TestCommonAncestor:
    def test_common_ancestor_same_container(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        r = doc.create_range()
        r.select_node_contents(div)
        assert r.common_ancestor_container is div

    def test_common_ancestor_cross_container(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        s1 = doc.create_element("section")
        s2 = doc.create_element("section")
        div.append_child(s1)
        div.append_child(s2)
        t1 = doc.create_text_node("hello")
        t2 = doc.create_text_node("world")
        s1.append_child(t1)
        s2.append_child(t2)
        r = doc.create_range()
        r.set_start(t1, 0)
        r.set_end(t2, 5)
        assert r.common_ancestor_container is div


# ---------------------------------------------------------------------------
# extract_contents / clone_contents / delete_contents
# ---------------------------------------------------------------------------


class TestExtractContents:
    def test_collapsed_range_returns_empty_fragment(self) -> None:
        doc = Document()
        r = doc.create_range()
        frag = r.extract_contents()
        assert isinstance(frag, DocumentFragment)
        assert len(frag.child_nodes) == 0

    def test_select_node_contents_extract_moves_children(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        a = doc.create_element("a")
        b = doc.create_element("b")
        div.append_child(a)
        div.append_child(b)
        r = doc.create_range()
        r.select_node_contents(div)
        frag = r.extract_contents()
        assert isinstance(frag, DocumentFragment)
        assert len(frag.child_nodes) == 2
        assert frag.first_child is a
        assert frag.last_child is b
        # Originals removed from div.
        assert len(div.child_nodes) == 0

    def test_partial_text_extract(self) -> None:
        # Acceptance criterion #6: r.set_start(t, 2); r.set_end(t, 5);
        # extract_contents() returns t.data[2:5].
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello world")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 2)
        r.set_end(t, 5)
        frag = r.extract_contents()
        assert len(frag.child_nodes) == 1
        assert frag.first_child.data == "llo"
        # Original text was mutated to remove the slice.
        assert t.data == "he world"

    def test_cross_text_node_extract(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        t1 = doc.create_text_node("hello")
        div.append_child(t1)
        span = doc.create_element("span")
        div.append_child(span)
        t2 = doc.create_text_node("world")
        span.append_child(t2)
        r = doc.create_range()
        r.set_start(t1, 2)
        r.set_end(t2, 3)
        frag = r.extract_contents()
        assert len(frag.child_nodes) == 2
        # First child is a Text "llo".
        assert frag.first_child.data == "llo"
        # Second child is the cloned span containing only "wor".
        cloned_span = frag.last_child
        assert cloned_span.tag_name == "SPAN"
        assert cloned_span.first_child.data == "wor"
        # Original document keeps the trimmed pieces.
        assert t1.data == "he"
        assert t2.data == "ld"


class TestCloneContents:
    def test_clone_contents_does_not_modify_document(self) -> None:
        # Acceptance criterion #4.
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        a = doc.create_element("a")
        div.append_child(a)
        t = doc.create_text_node("hello")
        a.append_child(t)
        r = doc.create_range()
        r.select_node_contents(div)
        frag = r.clone_contents()
        assert isinstance(frag, DocumentFragment)
        assert len(frag.child_nodes) == 1
        # Frag's child is a deep clone, NOT the original.
        cloned_a = frag.first_child
        assert cloned_a is not a
        assert cloned_a.tag_name == "A"
        # Document unchanged.
        assert div.first_child is a
        assert a.first_child is t

    def test_clone_contents_partial_text(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello world")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 2)
        r.set_end(t, 7)
        frag = r.clone_contents()
        assert frag.first_child.data == "llo w"
        # Original text unchanged.
        assert t.data == "hello world"


class TestDeleteContents:
    def test_delete_contents_returns_none(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        t = doc.create_text_node("hello")
        div.append_child(t)
        r = doc.create_range()
        r.select_node_contents(div)
        result = r.delete_contents()
        assert result is None
        assert len(div.child_nodes) == 0

    def test_delete_contents_collapsed_no_op(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        t = doc.create_text_node("hello")
        div.append_child(t)
        r = doc.create_range()
        r.set_start(t, 2)
        r.collapse(to_start=True)
        r.delete_contents()
        # Tree unchanged.
        assert div.first_child is t
        assert t.data == "hello"


# ---------------------------------------------------------------------------
# insert_node and surround_contents
# ---------------------------------------------------------------------------


class TestInsertNode:
    def test_insert_node_at_element_offset(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        a = doc.create_element("a")
        div.append_child(a)
        r = doc.create_range()
        r.select_node_contents(div)
        # range is (div, 0)..(div, 1); start offset = 0
        span = doc.create_element("span")
        r.insert_node(span)
        assert div.first_child is span

    def test_insert_node_inside_text_splits(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello world")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 5)
        r.set_end(t, 5)  # collapsed inside text
        span = doc.create_element("span")
        r.insert_node(span)
        # The original text was split at offset 5: 'hello' before, ' world' after
        # span is inserted between them.
        assert p.child_nodes[0] is t
        assert t.data == "hello"
        assert p.child_nodes[1] is span
        assert p.child_nodes[2].data == " world"


class TestSurroundContents:
    def test_surround_contents_wraps_range(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        t = doc.create_text_node("hello")
        div.append_child(t)
        r = doc.create_range()
        r.select_node_contents(div)
        wrapper = doc.create_element("span")
        r.surround_contents(wrapper)
        # div now contains wrapper, wrapper contains the text.
        assert div.first_child is wrapper
        assert wrapper.first_child.data == "hello"


# ---------------------------------------------------------------------------
# clone_range and detach
# ---------------------------------------------------------------------------


class TestCloneRange:
    def test_clone_range_returns_independent_object(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 1)
        r.set_end(t, 4)
        r2 = r.clone_range()
        assert isinstance(r2, Range)
        assert r2 is not r
        # Same boundaries.
        assert r2.start_container is t
        assert r2.start_offset == 1
        assert r2.end_container is t
        assert r2.end_offset == 4
        # Modifying the clone does not affect the original.
        r2.set_start(t, 0)
        assert r.start_offset == 1


class TestDetach:
    def test_detach_is_noop(self) -> None:
        doc = Document()
        r = doc.create_range()
        # Should not raise; should not change anything.
        result = r.detach()
        assert result is None
        assert r.collapsed is True


# ---------------------------------------------------------------------------
# Query methods
# ---------------------------------------------------------------------------


class TestIsPointInRange:
    def test_point_inside_range_returns_true(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 1)
        r.set_end(t, 4)
        assert r.is_point_in_range(t, 2) is True
        # Inclusive at boundaries.
        assert r.is_point_in_range(t, 1) is True
        assert r.is_point_in_range(t, 4) is True

    def test_point_outside_range_returns_false(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 1)
        r.set_end(t, 4)
        assert r.is_point_in_range(t, 0) is False
        assert r.is_point_in_range(t, 5) is False

    def test_invalid_offset_raises(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 1)
        r.set_end(t, 4)
        with pytest.raises(IndexSizeError):
            r.is_point_in_range(t, 100)


class TestComparePoint:
    def test_before_start_returns_minus_one(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 2)
        r.set_end(t, 4)
        assert r.compare_point(t, 0) == -1

    def test_within_returns_zero(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 2)
        r.set_end(t, 4)
        assert r.compare_point(t, 3) == 0

    def test_after_end_returns_one(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 2)
        r.set_end(t, 4)
        assert r.compare_point(t, 5) == 1


class TestCompareBoundaryPoints:
    def test_exposes_comparison_constants(self) -> None:
        assert Range.START_TO_START == 0
        assert Range.START_TO_END == 1
        assert Range.END_TO_END == 2
        assert Range.END_TO_START == 3

    def test_start_to_start_returns_minus_one_when_this_start_is_before(self) -> None:
        doc = Document()
        host = doc.create_element("div")
        doc.append_child(host)
        t = doc.create_text_node("abcdef")
        host.append_child(t)

        left = doc.create_range()
        left.set_start(t, 1)
        left.set_end(t, 2)

        right = doc.create_range()
        right.set_start(t, 4)
        right.set_end(t, 5)

        assert left.compare_boundary_points(Range.START_TO_START, right) == -1

    def test_start_to_end_returns_zero_when_boundaries_equal(self) -> None:
        doc = Document()
        host = doc.create_element("div")
        doc.append_child(host)
        t = doc.create_text_node("abcdef")
        host.append_child(t)

        left = doc.create_range()
        left.set_start(t, 0)
        left.set_end(t, 3)

        right = doc.create_range()
        right.set_start(t, 3)
        right.set_end(t, 5)

        assert left.compare_boundary_points(Range.START_TO_END, right) == 0

    def test_end_to_end_returns_minus_one_for_earlier_end(self) -> None:
        doc = Document()
        host = doc.create_element("div")
        doc.append_child(host)
        t = doc.create_text_node("abcdef")
        host.append_child(t)

        left = doc.create_range()
        left.set_start(t, 1)
        left.set_end(t, 2)

        right = doc.create_range()
        right.set_start(t, 4)
        right.set_end(t, 5)

        assert left.compare_boundary_points(Range.END_TO_END, right) == -1

    def test_end_to_start_returns_plus_one_when_this_start_is_after_source_end(self) -> None:
        doc = Document()
        host = doc.create_element("div")
        doc.append_child(host)
        t = doc.create_text_node("abcdef")
        host.append_child(t)

        left = doc.create_range()
        left.set_start(t, 4)
        left.set_end(t, 5)

        right = doc.create_range()
        right.set_start(t, 1)
        right.set_end(t, 2)

        assert left.compare_boundary_points(Range.END_TO_START, right) == 1

    def test_invalid_how_raises_not_supported_error(self) -> None:
        doc = Document()
        host = doc.create_element("div")
        doc.append_child(host)
        t = doc.create_text_node("abcdef")
        host.append_child(t)

        left = doc.create_range()
        left.set_start(t, 1)
        left.set_end(t, 2)

        right = doc.create_range()
        right.set_start(t, 3)
        right.set_end(t, 4)

        with pytest.raises(NotSupportedError):
            left.compare_boundary_points(99, right)

    def test_cross_document_ranges_raise_wrong_document_error(self) -> None:
        left_doc = Document()
        left_host = left_doc.create_element("div")
        left_doc.append_child(left_host)
        left_text = left_doc.create_text_node("abcdef")
        left_host.append_child(left_text)

        right_doc = Document()
        right_host = right_doc.create_element("div")
        right_doc.append_child(right_host)
        right_text = right_doc.create_text_node("abcdef")
        right_host.append_child(right_text)

        left = left_doc.create_range()
        left.set_start(left_text, 1)
        left.set_end(left_text, 2)

        right = right_doc.create_range()
        right.set_start(right_text, 3)
        right.set_end(right_text, 4)

        with pytest.raises(WrongDocumentError):
            left.compare_boundary_points(Range.START_TO_START, right)


class TestCreateContextualFragment:
    def test_returns_document_fragment_for_element_start_context(self) -> None:
        doc = Document()
        host = doc.create_element("div")
        doc.append_child(host)

        r = doc.create_range()
        r.select_node_contents(host)

        frag = r.create_contextual_fragment("<p>Hello</p><span>!</span>")

        assert isinstance(frag, DocumentFragment)
        assert len(frag.child_nodes) == 2
        assert frag.first_child.tag_name == "P"
        assert frag.first_child.first_child.data == "Hello"
        assert frag.last_child.tag_name == "SPAN"
        assert frag.last_child.first_child.data == "!"

    def test_uses_start_boundary_element_as_parsing_context(self) -> None:
        doc = Document()
        table = doc.create_element("table")
        doc.append_child(table)

        r = doc.create_range()
        r.select_node_contents(table)

        frag = r.create_contextual_fragment("<tr><td>x</td></tr>")

        assert len(frag.child_nodes) == 1
        assert frag.first_child.tag_name == "TBODY"
        assert frag.first_child.first_child.tag_name == "TR"
        assert frag.first_child.first_child.first_child.tag_name == "TD"
        assert frag.first_child.first_child.first_child.first_child.data == "x"

    def test_result_fragment_and_children_belong_to_range_document(self) -> None:
        doc = Document()
        host = doc.create_element("div")
        doc.append_child(host)

        r = doc.create_range()
        r.select_node_contents(host)

        frag = r.create_contextual_fragment("<p>owned</p>")

        assert frag.owner_document is doc
        assert frag.first_child.owner_document is doc
        assert frag.first_child.first_child.owner_document is doc

    def test_text_start_container_uses_parent_element_as_context(self) -> None:
        doc = Document()
        table = doc.create_element("table")
        doc.append_child(table)
        text = doc.create_text_node("ctx")
        table.append_child(text)

        r = doc.create_range()
        r.set_start(text, 1)
        r.set_end(text, 1)

        frag = r.create_contextual_fragment("<tr><td>x</td></tr>")

        assert frag.first_child.tag_name == "TBODY"
        assert frag.first_child.first_child.tag_name == "TR"
        assert frag.first_child.first_child.first_child.tag_name == "TD"

    def test_comment_start_container_uses_parent_element_as_context(self) -> None:
        doc = Document()
        table = doc.create_element("table")
        doc.append_child(table)
        comment = doc.create_comment("ctx")
        table.append_child(comment)

        r = doc.create_range()
        r.set_start(comment, 1)
        r.set_end(comment, 1)

        frag = r.create_contextual_fragment("<tr><td>x</td></tr>")

        assert frag.first_child.tag_name == "TBODY"
        assert frag.first_child.first_child.tag_name == "TR"
        assert frag.first_child.first_child.first_child.tag_name == "TD"

    def test_html_context_falls_back_to_body_context(self) -> None:
        doc = Document()
        html = doc.create_element("html")
        doc.append_child(html)
        body = doc.create_element("body")
        html.append_child(body)

        r = doc.create_range()
        r.select_node_contents(html)

        frag = r.create_contextual_fragment("<tr><td>x</td></tr>")

        # Body-context parsing of table rows yields text content in this parser,
        # and avoids html-context HEAD/BODY wrapper artifacts.
        assert len(frag.child_nodes) == 1
        assert frag.first_child.node_type == 3
        assert frag.first_child.data == "x"


class TestIntersectsNode:
    def test_intersects_node_inside_selection(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        span = doc.create_element("span")
        div.append_child(span)
        r = doc.create_range()
        r.select_node_contents(div)
        assert r.intersects_node(span) is True

    def test_does_not_intersect_node_before_range(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        before = doc.create_element("a")
        after = doc.create_element("b")
        div.append_child(before)
        div.append_child(after)
        r = doc.create_range()
        # Range covers only 'after'.
        r.set_start(div, 1)
        r.set_end(div, 2)
        assert r.intersects_node(before) is False
        assert r.intersects_node(after) is True

    def test_orphan_node_intersects_only_if_boundary(self) -> None:
        doc = Document()
        orphan = doc.create_element("span")
        r = doc.create_range()
        # Orphan is the start_container; must intersect.
        assert r.intersects_node(orphan) is False  # orphan != doc (start)
        r2 = doc.create_range()
        r2._start_container = orphan
        r2._end_container = orphan
        assert r2.intersects_node(orphan) is True


# ---------------------------------------------------------------------------
# to_string
# ---------------------------------------------------------------------------


class TestToString:
    def test_collapsed_returns_empty_string(self) -> None:
        doc = Document()
        r = doc.create_range()
        assert r.to_string() == ""

    def test_partial_text_node(self) -> None:
        doc = Document()
        p = doc.create_element("p")
        doc.append_child(p)
        t = doc.create_text_node("hello world")
        p.append_child(t)
        r = doc.create_range()
        r.set_start(t, 0)
        r.set_end(t, 5)
        assert r.to_string() == "hello"

    def test_cross_text_nodes(self) -> None:
        doc = Document()
        div = doc.create_element("div")
        doc.append_child(div)
        t1 = doc.create_text_node("hello")
        div.append_child(t1)
        span = doc.create_element("span")
        div.append_child(span)
        t2 = doc.create_text_node("world")
        span.append_child(t2)
        r = doc.create_range()
        r.set_start(t1, 2)
        r.set_end(t2, 3)
        assert r.to_string() == "llowor"


# ---------------------------------------------------------------------------
# Acceptance criteria coverage smoke-tests
# ---------------------------------------------------------------------------


class TestAcceptanceCriteria:
    def test_ac1_create_range_collapsed(self) -> None:
        doc = Document()
        r = doc.create_range()
        assert r.collapsed is True

    def test_ac2_select_node_contents_body(self) -> None:
        doc = Document()
        html = doc.create_element("html")
        doc.append_child(html)
        body = doc.create_element("body")
        html.append_child(body)
        body.append_child(doc.create_element("p"))
        body.append_child(doc.create_element("p"))
        r = doc.create_range()
        r.select_node_contents(body)
        assert r.start_container is body
        assert r.start_offset == 0
        assert r.end_container is body
        assert r.end_offset == len(body.child_nodes)

    def test_ac11_range_importable(self) -> None:
        from aspose_html.dom import Range as ImportedRange
        assert ImportedRange is Range
