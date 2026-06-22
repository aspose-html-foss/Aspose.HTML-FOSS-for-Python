"""Track 48 integration hardening tests (BACK-212 / SPEC-103 / ADR-195)."""

from __future__ import annotations

import subprocess
import sys

from aspose_html.dom import HTMLAreaElement, HTMLEmbedElement, HTMLMapElement, HTMLObjectElement
from aspose_html.html_document import HTMLDocument


class TestTrack48Integration:
    """Groups A-C integration: map/area/object/embed in one parsed tree."""

    def test_group_abc_cross_component_flow(self) -> None:
        doc = HTMLDocument.parse(
            "<base href='https://example.com/root/'>"
            "<map id='m'>"
            "  <area id='a1' href='images/pic.png?size=2#crop'>"
            "  <area id='a2'>"
            "</map>"
            "<form id='f'>"
            "  <object id='o'></object>"
            "</form>"
            "<embed id='e' name='hero-embed'>"
        )

        map_el = doc.get_element_by_id("m")
        area1 = doc.get_element_by_id("a1")
        area2 = doc.get_element_by_id("a2")
        object_el = doc.get_element_by_id("o")
        form_el = doc.get_element_by_id("f")
        embed_el = doc.get_element_by_id("e")

        assert isinstance(map_el, HTMLMapElement)
        assert isinstance(area1, HTMLAreaElement)
        assert isinstance(area2, HTMLAreaElement)
        assert isinstance(object_el, HTMLObjectElement)
        assert isinstance(embed_el, HTMLEmbedElement)

        # Group A: HTMLMapElement.areas is live and filters area descendants.
        assert len(map_el.areas) == 2
        map_el.remove_child(area2)
        assert len(map_el.areas) == 1
        map_el.append_child(doc.create_element("div"))
        assert len(map_el.areas) == 1

        # Group B: HTMLAreaElement URL decomposition mirrors anchor semantics.
        assert area1.protocol == "https:"
        assert area1.host == "example.com"
        assert area1.host_name == "example.com"
        assert area1.path_name == "/root/images/pic.png"
        assert area1.search == "?size=2"
        assert area1.hash == "#crop"
        assert area1.origin == "https://example.com"
        assert area2.protocol == ""
        assert area2.host == ""
        assert area2.path_name == ""

        # Group C: HTMLObjectElement + HTMLEmbedElement completeness.
        assert object_el.form is form_el
        assert object_el.content_document is None
        assert object_el.content_window is None
        assert embed_el.name == "hero-embed"
        embed_el.name = "secondary"
        assert embed_el.get_attribute("name") == "secondary"


class TestDoctestSweep:
    """Group D — doctest sweep for touched public source."""

    def test_group_d_doctest_sweep_elements(self) -> None:
        import pathlib  # noqa: PLC0415

        repo_root = str(pathlib.Path(__file__).parent.parent.parent)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--doctest-modules",
                "src/aspose_html/dom/html/_elements.py",
                "-q",
            ],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        assert result.returncode == 0, (
            "doctest failed for src/aspose_html/dom/html/_elements.py\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
