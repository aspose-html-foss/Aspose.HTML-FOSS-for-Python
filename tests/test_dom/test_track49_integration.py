""" integration hardening tests ( /  / )."""

from __future__ import annotations

import subprocess
import sys

from aspose_html.dom import HTMLEmbedElement, HTMLObjectElement, HTMLParamElement
from aspose_html.html_document import HTMLDocument


class TestTrack49Integration:
    """Groups A-B integration: object/embed/param reflected members in one flow."""

    def test_group_ab_cross_component_reflections(self) -> None:
        doc = HTMLDocument.parse(
            "<object id='obj' code='game.jar' codebase='/assets/' codetype='application/java' "
            "declare archive='core.zip,extras.zip' standby='Loading'>"
            "  <param id='p' type='text/plain' valuetype='data'>"
            "</object>"
            "<embed id='emb' align='middle'>"
        )

        obj = doc.get_element_by_id("obj")
        param = doc.get_element_by_id("p")
        embed = doc.get_element_by_id("emb")

        assert isinstance(obj, HTMLObjectElement)
        assert isinstance(param, HTMLParamElement)
        assert isinstance(embed, HTMLEmbedElement)

        # Group A: HTMLObjectElement reflected members.
        assert obj.code == "game.jar"
        assert obj.code_base == "/assets/"
        assert obj.code_type == "application/java"
        assert obj.declare is True
        assert obj.archive == "core.zip,extras.zip"
        assert obj.standby == "Loading"

        obj.code = "viewer.swf"
        obj.code_base = "https://cdn.example/static/"
        obj.code_type = "application/x-shockwave-flash"
        obj.declare = False
        obj.archive = "fallback.zip"
        obj.standby = "Ready"

        assert obj.get_attribute("code") == "viewer.swf"
        assert obj.get_attribute("codebase") == "https://cdn.example/static/"
        assert obj.get_attribute("codetype") == "application/x-shockwave-flash"
        assert obj.has_attribute("declare") is False
        assert obj.get_attribute("archive") == "fallback.zip"
        assert obj.get_attribute("standby") == "Ready"

        # Group B: HTMLEmbedElement.align + HTMLParamElement.type/value_type.
        assert embed.align == "middle"
        embed.align = "left"
        assert embed.get_attribute("align") == "left"

        assert param.type == "text/plain"
        assert param.value_type == "data"
        param.type = "image/svg+xml"
        param.value_type = "ref"
        assert param.get_attribute("type") == "image/svg+xml"
        assert param.get_attribute("valuetype") == "ref"


class TestDoctestSweep:
    """Group C — doctest sweep for touched public source."""

    def test_group_c_doctest_sweep_elements(self) -> None:
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
