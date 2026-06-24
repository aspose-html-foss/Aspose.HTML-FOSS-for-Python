""" integration hardening tests ( /  / )."""

from __future__ import annotations

import subprocess
import sys

from aspose_html.dom import Document, HTMLIFrameElement, HTMLInputElement, HTMLOptionElement
from aspose_html.html_document import HTMLDocument


class TestHTMLInputElementIDLStubs:
    """Group A — HTMLInputElement.indeterminate, width, height."""

    def test_group_a_input_idl_stubs(self) -> None:
        doc = Document()
        inp = doc.create_element("input")
        assert isinstance(inp, HTMLInputElement)

        # A-1/A-2/A-3
        assert inp.indeterminate is False
        inp.indeterminate = True
        assert inp.indeterminate is True
        inp.indeterminate = False
        assert inp.indeterminate is False
        assert inp.get_attribute("indeterminate") is None

        # A-4/A-5
        assert inp.width == 0
        assert inp.height == 0
        inp.set_attribute("width", "200")
        inp.set_attribute("height", "100")
        assert inp.width == 200
        assert inp.height == 100

        # A-6
        parsed = HTMLDocument.parse('<input id="i" type="image" width="50" height="30">')
        parsed_inp = parsed.get_element_by_id("i")
        assert isinstance(parsed_inp, HTMLInputElement)
        assert parsed_inp.width == 50
        assert parsed_inp.height == 30

        # A-7
        assert "_indeterminate" in HTMLInputElement.__slots__

        # A-8
        inp2 = doc.create_element("input")
        assert isinstance(inp2, HTMLInputElement)
        inp.indeterminate = True
        assert inp.indeterminate is True
        assert inp2.indeterminate is False


class TestHTMLOptionElementIndexAndForm:
    """Group B — HTMLOptionElement.index and .form."""

    def test_group_b_option_index_and_form(self) -> None:
        doc = Document()

        # B-1
        detached = doc.create_element("option")
        assert isinstance(detached, HTMLOptionElement)
        assert detached.index == 0

        # B-2/B-3
        sel = doc.create_element("select")
        opt0 = doc.create_element("option")
        opt1 = doc.create_element("option")
        opt2 = doc.create_element("option")
        sel.append_child(opt0)
        sel.append_child(opt1)
        sel.append_child(opt2)
        assert opt0.index == 0
        assert opt1.index == 1
        assert opt2.index == 2

        sel.remove_child(opt0)
        assert opt1.index == 0
        assert opt2.index == 1

        # B-4
        assert detached.form is None

        # B-5/B-6
        parsed = HTMLDocument.parse(
            '<form id="f"><select id="s"><option id="o"></option></select></form>'
            '<select id="s2"><option id="o2"></option></select>'
        )
        opt = parsed.get_element_by_id("o")
        form = parsed.get_element_by_id("f")
        opt2_parsed = parsed.get_element_by_id("o2")
        assert isinstance(opt, HTMLOptionElement)
        assert opt.form is form
        assert isinstance(opt2_parsed, HTMLOptionElement)
        assert opt2_parsed.form is None


class TestHTMLIFrameElementIDL:
    """Group C — HTMLIFrameElement IDL completeness."""

    def test_group_c_iframe_idl(self) -> None:
        doc = Document()
        iframe = doc.create_element("iframe")
        assert isinstance(iframe, HTMLIFrameElement)

        # C-1/C-2
        assert iframe.content_document is None
        assert iframe.content_window is None

        # C-3/C-4
        assert iframe.srcdoc == ""
        iframe.srcdoc = "<p>inline</p>"
        assert iframe.srcdoc == "<p>inline</p>"
        assert iframe.referrer_policy == ""
        iframe.referrer_policy = "no-referrer"
        assert iframe.referrer_policy == "no-referrer"

        # C-5
        parsed = HTMLDocument.parse(
            '<iframe id="fr" srcdoc="<p>hello</p>" referrerpolicy="no-referrer"></iframe>'
        )
        parsed_iframe = parsed.get_element_by_id("fr")
        assert isinstance(parsed_iframe, HTMLIFrameElement)
        assert parsed_iframe.srcdoc == "<p>hello</p>"
        assert parsed_iframe.referrer_policy == "no-referrer"

        # C-6
        clone = parsed_iframe.clone_node(True)
        assert isinstance(clone, HTMLIFrameElement)
        assert clone.srcdoc == "<p>hello</p>"


class TestHTMLScriptAndLabelElements:
    """Group D — HTMLScriptElement + HTMLLabelElement members."""

    def test_group_d_script_and_label(self) -> None:
        doc = Document()

        # D-1..D-6 (script)
        script = doc.create_element("script")
        assert script.integrity == ""
        script.integrity = "sha384-x"
        assert script.integrity == "sha384-x"
        assert script.cross_origin is None
        script.cross_origin = "anonymous"
        assert script.cross_origin == "anonymous"
        script.cross_origin = None
        assert script.get_attribute("crossorigin") is None
        assert script.referrer_policy == ""
        script.referrer_policy = "no-referrer"
        assert script.referrer_policy == "no-referrer"

        parsed = HTMLDocument.parse(
            '<script id="s" integrity="sha384-x" crossorigin="use-credentials" '
            'referrerpolicy="no-referrer"></script>'
        )
        parsed_script = parsed.get_element_by_id("s")
        assert parsed_script is not None
        assert parsed_script.integrity == "sha384-x"
        assert parsed_script.cross_origin == "use-credentials"
        assert parsed_script.referrer_policy == "no-referrer"

        # D-7..D-11 (label)
        label = doc.create_element("label")
        assert label.control is None
        label.html_for = "nonexistent"
        assert label.control is None
        assert label.form is None

        parsed2 = HTMLDocument.parse(
            '<form id="f"><label id="l" for="i">X</label><input id="i"></form>'
        )
        label2 = parsed2.get_element_by_id("l")
        control = parsed2.get_element_by_id("i")
        form = parsed2.get_element_by_id("f")
        assert label2 is not None
        assert label2.control is control
        assert label2.form is form


class TestDoctestSweep:
    """Group E — doctest sweep for touched public source."""

    def test_group_e_doctest_sweep_elements(self) -> None:
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
