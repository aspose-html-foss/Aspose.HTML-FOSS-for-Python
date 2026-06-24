""" integration hardening tests ( /  / )."""

from __future__ import annotations

from aspose_html.dom import Document, Range, StaticRange


class TestTrack50Integration:
    """Cross-behavior matrix for Range / AbstractRange / StaticRange."""

    def test_live_and_static_ranges_keep_expected_endpoint_semantics(self) -> None:
        doc = Document()
        root = doc.create_element("div")
        doc.append_child(root)
        text = doc.create_text_node("abcdef")
        root.append_child(text)

        live = doc.create_range()
        live.set_start(text, 1)
        live.set_end(text, 4)

        static = StaticRange(
            {
                "start_container": text,
                "start_offset": 1,
                "end_container": text,
                "end_offset": 4,
            }
        )

        assert isinstance(live, Range)
        assert live.start_offset == 1
        assert live.end_offset == 4
        assert static.start_offset == 1
        assert static.end_offset == 4
        assert live.to_string() == "bcd"
        assert static.to_string() == "bcd"

        # Live range remains mutable; static range remains immutable.
        live.set_start(text, 2)
        assert live.to_string() == "cd"
        assert static.to_string() == "bcd"

    def test_compare_boundary_points_and_contextual_fragment_compose(self) -> None:
        doc = Document()
        table = doc.create_element("table")
        doc.append_child(table)
        row = doc.create_element("tr")
        table.append_child(row)
        cell = doc.create_element("td")
        row.append_child(cell)
        text = doc.create_text_node("seed")
        cell.append_child(text)

        first = doc.create_range()
        first.set_start(text, 0)
        first.set_end(text, 2)

        second = doc.create_range()
        second.set_start(text, 2)
        second.set_end(text, 4)

        assert first.compare_boundary_points(Range.START_TO_START, second) == -1
        assert second.compare_boundary_points(Range.END_TO_END, first) == 1

        first.select_node_contents(table)
        frag = first.create_contextual_fragment("<tr><td>patched</td></tr>")

        assert len(frag.child_nodes) == 1
        assert frag.first_child.tag_name == "TBODY"
        assert frag.first_child.first_child.tag_name == "TR"
        assert frag.first_child.first_child.first_child.tag_name == "TD"
        assert frag.first_child.first_child.first_child.text_content == "patched"
