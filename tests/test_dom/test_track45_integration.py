""" integration hardening tests ( /  / ).

Cross-component integration checks for ..:
  Group A — HTMLFieldSetElement.type + elements live collection: 7 assertions.
  Group B — HTMLLegendElement.form + HTMLOutputElement IDL: 10 assertions.
  Group C — form property on 5 form-associated element classes: 8 assertions.
  Group D — CSS.supports() and @supports cascade agreement: 8 assertions.
  Group E — Doctest sweep for _elements.py and cssom/__init__.py.

Note on D-2/D-3/D-4: The  spec listed ``CSS.supports("color: red")``
(bare string without outer parens), ``CSS.supports("display", "grid")``, and
``CSS.supports("--custom-flag", "1")`` as returning ``True``.  The actual
engine requires @supports condition syntax with outer parens for the one-argument
form, does not include ``display`` in its known-property table, and does not
recognise custom-property names (``--*``).  Tests D-2, D-3, D-4 are written
against actual runtime behavior per  resolution.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from aspose_html.dom import (
    Document,
    DOMTokenList,
    HTMLButtonElement,
    HTMLFieldSetElement,
    HTMLInputElement,
    HTMLLegendElement,
    HTMLOutputElement,
    HTMLSelectElement,
    HTMLTextAreaElement,
)
from aspose_html.cssom import CSS
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# Group A — HTMLFieldSetElement.type and .elements live collection ()
# ---------------------------------------------------------------------------


def test_a1_fieldset_type_constant() -> None:
    """A-1: HTMLFieldSetElement.type always returns 'fieldset'."""
    doc = Document()
    fs = doc.create_element("fieldset")
    assert isinstance(fs, HTMLFieldSetElement)
    assert fs.type == "fieldset"


def test_a2_empty_fieldset_elements_length_zero() -> None:
    """A-2: An empty fieldset has an elements collection of length 0."""
    doc = Document()
    fs = doc.create_element("fieldset")
    assert len(fs.elements) == 0


def test_a3_fieldset_elements_includes_input() -> None:
    """A-3: Appending <input> to fieldset; elements has length 1."""
    doc = Document()
    fs = doc.create_element("fieldset")
    inp = doc.create_element("input")
    fs.append_child(inp)
    assert len(fs.elements) == 1


def test_a4_fieldset_elements_includes_button() -> None:
    """A-4: Appending <input> then <button>; elements has length 2."""
    doc = Document()
    fs = doc.create_element("fieldset")
    fs.append_child(doc.create_element("input"))
    fs.append_child(doc.create_element("button"))
    assert len(fs.elements) == 2


def test_a5_fieldset_elements_excludes_div() -> None:
    """A-5: Appending <div> (unlisted) does not increase elements count."""
    doc = Document()
    fs = doc.create_element("fieldset")
    fs.append_child(doc.create_element("input"))
    fs.append_child(doc.create_element("button"))
    fs.append_child(doc.create_element("div"))
    assert len(fs.elements) == 2


def test_a6_fieldset_elements_live_after_removal() -> None:
    """A-6: Remove <input> from fieldset; elements shrinks (live collection)."""
    doc = Document()
    fs = doc.create_element("fieldset")
    inp = doc.create_element("input")
    btn = doc.create_element("button")
    fs.append_child(inp)
    fs.append_child(btn)
    assert len(fs.elements) == 2

    fs.remove_child(inp)
    # The collection is live — no need to call .elements again before the
    # mutation; this re-access reflects the updated subtree.
    assert len(fs.elements) == 1


def test_a7_nested_fieldset_counted_in_outer_elements() -> None:
    """A-7: An inner <fieldset> is a listed element and is counted in outer .elements."""
    doc = Document()
    outer = doc.create_element("fieldset")
    inner = doc.create_element("fieldset")
    outer.append_child(inner)
    # Only inner is counted (inner has no children of its own)
    assert len(outer.elements) == 1


# ---------------------------------------------------------------------------
# Group B — HTMLLegendElement.form + HTMLOutputElement IDL ()
# ---------------------------------------------------------------------------


def test_b1_legend_form_returns_ancestor_form() -> None:
    """B-1: <legend> inside <fieldset> inside <form> returns the form element."""
    doc = HTMLDocument.parse(
        '<form id="f"><fieldset><legend id="lg"></legend></fieldset></form>'
    )
    legend = doc.get_element_by_id("lg")
    form = doc.get_element_by_id("f")
    assert legend is not None and form is not None
    assert isinstance(legend, HTMLLegendElement)
    assert legend.form is form


def test_b2_detached_legend_form_is_none() -> None:
    """B-2: A detached <legend> returns None for .form."""
    doc = Document()
    lg = doc.create_element("legend")
    assert isinstance(lg, HTMLLegendElement)
    assert lg.form is None


def test_b3_legend_in_fieldset_with_no_ancestor_form_is_none() -> None:
    """B-3: <legend> in <fieldset> with no ancestor <form> returns None."""
    doc = Document()
    fs = doc.create_element("fieldset")
    lg = doc.create_element("legend")
    fs.append_child(lg)
    assert lg.form is None


def test_b4_output_type_constant() -> None:
    """B-4: HTMLOutputElement.type always returns 'output'."""
    doc = Document()
    out = doc.create_element("output")
    assert isinstance(out, HTMLOutputElement)
    assert out.type == "output"


def test_b5_output_value_empty_for_fresh_element() -> None:
    """B-5: .value returns '' for a freshly created output element."""
    doc = Document()
    out = doc.create_element("output")
    assert out.value == ""


def test_b6_output_value_setter_roundtrip() -> None:
    """B-6: Setting out.value = '42' makes out.value == '42'."""
    doc = Document()
    out = doc.create_element("output")
    doc.append_child(out)
    out.value = "42"
    assert out.value == "42"


def test_b7_parsed_output_value_reflects_text_content() -> None:
    """B-7: Parsed <output>hello</output> has .value == 'hello'."""
    doc = HTMLDocument.parse("<output>hello</output>")
    out = doc.body.first_child
    assert out is not None
    assert out.value == "hello"


def test_b8_output_html_for_is_dom_token_list() -> None:
    """B-8: out.html_for is a DOMTokenList instance."""
    doc = Document()
    out = doc.create_element("output")
    assert isinstance(out.html_for, DOMTokenList)


def test_b9_output_html_for_is_cached() -> None:
    """B-9: out.html_for returns the same object on repeated access."""
    doc = Document()
    out = doc.create_element("output")
    assert out.html_for is out.html_for


def test_b10_output_html_for_add_updates_for_attribute() -> None:
    """B-10: Adding a token to html_for sets it on the 'for' attribute."""
    doc = Document()
    out = doc.create_element("output")
    out.html_for.add("f1")
    assert out.get_attribute("for") == "f1"


# ---------------------------------------------------------------------------
# Group C — form property on form-associated elements ()
# ---------------------------------------------------------------------------


def test_c1_button_form_returns_ancestor_form() -> None:
    """C-1: HTMLButtonElement.form returns the nearest ancestor <form>."""
    doc = HTMLDocument.parse('<form id="f"><button id="btn"></button></form>')
    assert doc.get_element_by_id("btn").form is doc.get_element_by_id("f")


def test_c2_input_form_returns_ancestor_form() -> None:
    """C-2: HTMLInputElement.form returns the nearest ancestor <form>."""
    doc = HTMLDocument.parse('<form id="f"><input id="inp"></form>')
    assert doc.get_element_by_id("inp").form is doc.get_element_by_id("f")


def test_c3_select_form_returns_ancestor_form() -> None:
    """C-3: HTMLSelectElement.form returns the nearest ancestor <form>."""
    doc = HTMLDocument.parse('<form id="f"><select id="sel"></select></form>')
    assert doc.get_element_by_id("sel").form is doc.get_element_by_id("f")


def test_c4_textarea_form_returns_ancestor_form() -> None:
    """C-4: HTMLTextAreaElement.form returns the nearest ancestor <form>."""
    doc = HTMLDocument.parse('<form id="f"><textarea id="ta"></textarea></form>')
    assert doc.get_element_by_id("ta").form is doc.get_element_by_id("f")


def test_c5_output_form_returns_ancestor_form() -> None:
    """C-5: HTMLOutputElement.form returns the nearest ancestor <form>."""
    doc = HTMLDocument.parse('<form id="f"><output id="out"></output></form>')
    assert doc.get_element_by_id("out").form is doc.get_element_by_id("f")


def test_c6_input_form_through_intermediate_div() -> None:
    """C-6: <input> nested inside <div> inside <form> still finds the form."""
    doc = HTMLDocument.parse('<form id="f"><div><input id="inp"></div></form>')
    assert doc.get_element_by_id("inp").form is doc.get_element_by_id("f")


def test_c7_element_without_ancestor_form_returns_none() -> None:
    """C-7: An element with no ancestor <form> returns None from .form."""
    doc = Document()
    inp = doc.create_element("input")
    div = doc.create_element("div")
    div.append_child(inp)
    assert inp.form is None


def test_c8_detached_element_form_is_none() -> None:
    """C-8: A detached element (not yet inserted anywhere) returns None from .form."""
    doc = Document()
    inp = doc.create_element("input")
    assert inp.form is None


# ---------------------------------------------------------------------------
# Group D — CSS.supports() and @supports cascade agreement ()
# ---------------------------------------------------------------------------


def test_d1_css_supports_known_property_value_pair() -> None:
    """D-1: CSS.supports('color', 'red') returns True for a known property."""
    assert CSS.supports("color", "red") is True


def test_d2_css_supports_condition_with_parens_returns_true() -> None:
    """D-2: CSS.supports('(color: red)') returns True (outer-paren condition form)."""
    # The one-argument form requires @supports condition syntax — '(prop: val)'.
    # The bare 'color: red' without parens returns False per _eval_supports_clause.
    assert CSS.supports("(color: red)") is True


def test_d3_css_supports_display_grid_returns_true() -> None:
    """D-3: CSS.supports('display', 'grid') returns True — 'display' added by  ()."""
    #  () expanded _INITIAL_VALUE_BASELINE to include 'display',
    # so _KNOWN_PROPERTIES now contains it and CSS.supports() correctly returns True.
    assert CSS.supports("display", "grid") is True


def test_d4_css_supports_custom_property_returns_false() -> None:
    """D-4: CSS.supports('--custom-flag', '1') returns False — custom-property names not matched."""
    # _SUPPORTED_NAME_RE requires '^[a-z][a-z0-9-]*$' — the '--' prefix is not
    # accepted by the regex, so custom properties always evaluate to False.
    assert CSS.supports("--custom-flag", "1") is False


def test_d5_css_supports_selector_form_returns_false() -> None:
    """D-5: CSS.supports('selector(div > p)') returns False (selector() always False)."""
    assert CSS.supports("selector(div > p)") is False


def test_d6_css_supports_bogus_property_returns_false() -> None:
    """D-6: CSS.supports('bogus-prop', 'val') returns False for unknown property."""
    assert CSS.supports("bogus-prop", "val") is False


def test_d7_css_importable_from_cssom() -> None:
    """D-7: 'from aspose_html.cssom import CSS' does not raise."""
    from aspose_html.cssom import CSS as _CSS  # noqa: PLC0415
    assert _CSS is CSS


def test_d8_supports_and_at_supports_cascade_agree() -> None:
    """D-8: @supports cascade and CSS.supports() share the same evaluator.

    A CSSSupportsRule with condition '(color: red)' — CSS.supports passes
    and the cascade applies the inner rule.  A CSSSupportsRule with condition
    '(bogus: val)' — CSS.supports fails and the cascade does NOT apply it.
    """
    # Verify CSS.supports agrees with what the cascade will do
    assert CSS.supports("(color: red)") is True
    assert CSS.supports("(bogus: val)") is False

    # Verify the cascade actually applies / skips the @supports rules consistently
    html = (
        "<html><head><style>"
        "@supports (color: red) { p { color: green; } }"
        "@supports (bogus: val) { p { color: purple; } }"
        "</style></head><body><p id='p'>hello</p></body></html>"
    )
    doc = HTMLDocument.parse(html)
    p = doc.get_element_by_id("p")
    assert p is not None, "paragraph element not found"

    computed = p.get_computed_style()
    # The @supports (color: red) rule IS applied — color is green.
    assert computed.get_property_value("color") == "green", (
        f"expected 'green' from @supports (color: red) rule, "
        f"got {computed.get_property_value('color')!r}"
    )


# ---------------------------------------------------------------------------
# Group E — Doctest sweep (.. touched files)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_path",
    [
        "src/aspose_html/dom/html/_elements.py",
        "src/aspose_html/cssom/__init__.py",
    ],
)
def test_e_doctest_sweep(module_path: str) -> None:
    """E-1/E-2: All >>> docstring examples in the given source file execute cleanly."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--doctest-modules", module_path, "-q"],
        capture_output=True,
        text=True,
        cwd=str(__import__("pathlib").Path(__file__).parent.parent.parent),
    )
    assert result.returncode == 0, (
        f"doctest failed for {module_path}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
