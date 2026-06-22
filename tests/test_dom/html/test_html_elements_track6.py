"""Tests for BACK-43 (10 HTMLElement subclasses) and BACK-44 (HTMLTemplateElement).

Covers all acceptance criteria from ADR-037 and ADR-038.
"""
import pytest

from aspose_html.dom import Document
from aspose_html.dom.html._elements import (
    HTMLTextAreaElement,
    HTMLFieldSetElement,
    HTMLOptionElement,
    HTMLOptGroupElement,
    HTMLOutputElement,
    HTMLDataListElement,
    HTMLProgressElement,
    HTMLMeterElement,
    HTMLDetailsElement,
    HTMLDialogElement,
    HTMLTemplateElement,
)
from aspose_html.dom._document_fragment import DocumentFragment


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

@pytest.fixture()
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# BACK-43: HTMLTextAreaElement
# ---------------------------------------------------------------------------

class TestHTMLTextAreaElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("textarea")
        assert isinstance(el, HTMLTextAreaElement)

    def test_string_properties(self, doc: Document) -> None:
        el = doc.create_element("textarea")
        assert el.name == ""
        el.name = "bio"
        assert el.name == "bio"
        assert el.placeholder == ""
        el.placeholder = "Enter bio"
        assert el.placeholder == "Enter bio"

    def test_int_properties(self, doc: Document) -> None:
        el = doc.create_element("textarea")
        assert el.rows == 0
        el.rows = 5
        assert el.rows == 5
        assert el.cols == 0
        el.cols = 40
        assert el.cols == 40
        assert el.max_length == 0
        el.max_length = 200
        assert el.max_length == 200
        assert el.min_length == 0
        el.min_length = 10
        assert el.min_length == 10

    def test_bool_properties(self, doc: Document) -> None:
        el = doc.create_element("textarea")
        assert not el.disabled
        el.disabled = True
        assert el.disabled
        el.disabled = False
        assert not el.disabled
        assert not el.read_only
        el.read_only = True
        assert el.read_only
        el.read_only = False
        assert not el.read_only
        assert not el.required
        el.required = True
        assert el.required
        el.required = False
        assert not el.required

    def test_value_reads_text_child(self, doc: Document) -> None:
        el = doc.create_element("textarea")
        doc.append_child(el)
        assert el.value == ""
        el.append_child(doc.create_text_node("hello"))
        assert el.value == "hello"

    def test_readonly_attribute_name(self, doc: Document) -> None:
        """Ensure the HTML attribute name is 'readonly' (no space/hyphen)."""
        el = doc.create_element("textarea")
        el.read_only = True
        assert el.get_attribute("readonly") == ""

    def test_maxlength_attribute_name(self, doc: Document) -> None:
        """Ensure the HTML attribute name is 'maxlength'."""
        el = doc.create_element("textarea")
        el.max_length = 100
        assert el.get_attribute("maxlength") == "100"

    def test_minlength_attribute_name(self, doc: Document) -> None:
        """Ensure the HTML attribute name is 'minlength'."""
        el = doc.create_element("textarea")
        el.min_length = 5
        assert el.get_attribute("minlength") == "5"


# ---------------------------------------------------------------------------
# BACK-43: HTMLFieldSetElement
# ---------------------------------------------------------------------------

class TestHTMLFieldSetElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("fieldset")
        assert isinstance(el, HTMLFieldSetElement)

    def test_properties(self, doc: Document) -> None:
        fs = doc.create_element("fieldset")
        assert fs.name == ""
        fs.name = "personal"
        assert fs.name == "personal"
        assert not fs.disabled
        fs.disabled = True
        assert fs.disabled
        fs.disabled = False
        assert not fs.disabled


# ---------------------------------------------------------------------------
# BACK-43: HTMLOptionElement
# ---------------------------------------------------------------------------

class TestHTMLOptionElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("option")
        assert isinstance(el, HTMLOptionElement)

    def test_string_properties(self, doc: Document) -> None:
        opt = doc.create_element("option")
        assert opt.value == ""
        opt.value = "fr"
        assert opt.value == "fr"
        assert opt.label == ""
        opt.label = "France"
        assert opt.label == "France"

    def test_bool_properties(self, doc: Document) -> None:
        opt = doc.create_element("option")
        assert not opt.disabled
        opt.disabled = True
        assert opt.disabled
        assert not opt.selected
        opt.selected = True
        assert opt.selected
        # default_selected reflects same attribute as selected
        assert opt.default_selected

    def test_default_selected_reflects_selected_attribute(self, doc: Document) -> None:
        opt = doc.create_element("option")
        opt.default_selected = True
        assert opt.selected  # same underlying attribute
        assert opt.default_selected
        opt.default_selected = False
        assert not opt.selected
        assert not opt.default_selected

    def test_text_reads_text_child(self, doc: Document) -> None:
        opt = doc.create_element("option")
        doc.append_child(opt)
        assert opt.text == ""
        opt.append_child(doc.create_text_node("France"))
        assert opt.text == "France"


# ---------------------------------------------------------------------------
# BACK-43: HTMLOptGroupElement
# ---------------------------------------------------------------------------

class TestHTMLOptGroupElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("optgroup")
        assert isinstance(el, HTMLOptGroupElement)

    def test_properties(self, doc: Document) -> None:
        og = doc.create_element("optgroup")
        assert og.label == ""
        og.label = "Europe"
        assert og.label == "Europe"
        assert not og.disabled
        og.disabled = True
        assert og.disabled


# ---------------------------------------------------------------------------
# BACK-43: HTMLOutputElement
# ---------------------------------------------------------------------------

class TestHTMLOutputElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("output")
        assert isinstance(el, HTMLOutputElement)

    def test_properties(self, doc: Document) -> None:
        out = doc.create_element("output")
        assert out.name == ""
        out.name = "result"
        assert out.name == "result"
        assert out.default_value == ""
        out.default_value = "42"
        assert out.default_value == "42"

    def test_default_value_attribute_name(self, doc: Document) -> None:
        """Ensure the HTML attribute name is 'defaultvalue' (all lowercase)."""
        out = doc.create_element("output")
        out.default_value = "99"
        assert out.get_attribute("defaultvalue") == "99"


# ---------------------------------------------------------------------------
# BACK-43: HTMLDataListElement
# ---------------------------------------------------------------------------

class TestHTMLDataListElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("datalist")
        assert isinstance(el, HTMLDataListElement)


# ---------------------------------------------------------------------------
# BACK-43: HTMLProgressElement
# ---------------------------------------------------------------------------

class TestHTMLProgressElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("progress")
        assert isinstance(el, HTMLProgressElement)

    def test_float_properties(self, doc: Document) -> None:
        prog = doc.create_element("progress")
        assert prog.value == 0.0
        assert prog.max == 1.0
        prog.value = 0.5
        assert prog.value == 0.5
        prog.max = 2.0
        assert prog.max == 2.0

    def test_invalid_value_falls_back_to_default(self, doc: Document) -> None:
        prog = doc.create_element("progress")
        prog.set_attribute("value", "not-a-number")
        assert prog.value == 0.0
        prog.set_attribute("max", "also-not-a-number")
        assert prog.max == 1.0


# ---------------------------------------------------------------------------
# BACK-43: HTMLMeterElement
# ---------------------------------------------------------------------------

class TestHTMLMeterElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("meter")
        assert isinstance(el, HTMLMeterElement)

    def test_float_properties(self, doc: Document) -> None:
        meter = doc.create_element("meter")
        assert meter.value == 0.0
        assert meter.min == 0.0
        assert meter.max == 1.0
        assert meter.low == 0.0
        assert meter.high == 0.0
        assert meter.optimum == 0.0
        meter.value = 0.7
        assert meter.value == 0.7
        meter.min = 0.1
        assert meter.min == 0.1
        meter.max = 5.0
        assert meter.max == 5.0
        meter.low = 0.25
        assert meter.low == 0.25
        meter.high = 0.75
        assert meter.high == 0.75
        meter.optimum = 0.6
        assert meter.optimum == 0.6


# ---------------------------------------------------------------------------
# BACK-43: HTMLDetailsElement
# ---------------------------------------------------------------------------

class TestHTMLDetailsElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("details")
        assert isinstance(el, HTMLDetailsElement)

    def test_open_property(self, doc: Document) -> None:
        det = doc.create_element("details")
        assert not det.open
        det.open = True
        assert det.open
        det.open = False
        assert not det.open


# ---------------------------------------------------------------------------
# BACK-43: HTMLDialogElement
# ---------------------------------------------------------------------------

class TestHTMLDialogElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("dialog")
        assert isinstance(el, HTMLDialogElement)

    def test_open_property(self, doc: Document) -> None:
        dlg = doc.create_element("dialog")
        assert not dlg.open
        dlg.open = True
        assert dlg.open
        dlg.open = False
        assert not dlg.open


# ---------------------------------------------------------------------------
# BACK-43: Clone preserves concrete subclass
# ---------------------------------------------------------------------------

class TestClonePreservesSubclass:
    @pytest.mark.parametrize("tag", [
        "textarea", "fieldset", "option", "optgroup", "output",
        "datalist", "progress", "meter", "details", "dialog",
    ])
    def test_clone_node_preserves_subclass(self, doc: Document, tag: str) -> None:
        el = doc.create_element(tag)
        clone = el.clone_node(deep=True)
        assert type(clone) is type(el)

    def test_textarea_clone_copies_attributes(self, doc: Document) -> None:
        ta = doc.create_element("textarea")
        ta.name = "notes"
        ta.rows = 5
        clone = ta.clone_node(deep=True)
        assert isinstance(clone, HTMLTextAreaElement)
        assert clone.name == "notes"
        assert clone.rows == 5


# ---------------------------------------------------------------------------
# BACK-43: Importable from aspose_html.dom.html
# ---------------------------------------------------------------------------

class TestImports:
    def test_all_classes_importable_from_dom_html(self) -> None:
        from aspose_html.dom.html import (  # noqa: PLC0415
            HTMLTextAreaElement as A,
            HTMLFieldSetElement as B,
            HTMLOptionElement as C,
            HTMLOptGroupElement as D,
            HTMLOutputElement as E,
            HTMLDataListElement as F,
            HTMLProgressElement as G,
            HTMLMeterElement as H,
            HTMLDetailsElement as I,
            HTMLDialogElement as J,
            HTMLTemplateElement as K,
        )
        for cls in (A, B, C, D, E, F, G, H, I, J, K):
            assert cls is not None

    def test_all_classes_importable_from_dom(self) -> None:
        from aspose_html.dom import (  # noqa: PLC0415
            HTMLTextAreaElement,
            HTMLFieldSetElement,
            HTMLOptionElement,
            HTMLOptGroupElement,
            HTMLOutputElement,
            HTMLDataListElement,
            HTMLProgressElement,
            HTMLMeterElement,
            HTMLDetailsElement,
            HTMLDialogElement,
            HTMLTemplateElement,
        )
        for cls in (
            HTMLTextAreaElement, HTMLFieldSetElement, HTMLOptionElement,
            HTMLOptGroupElement, HTMLOutputElement, HTMLDataListElement,
            HTMLProgressElement, HTMLMeterElement, HTMLDetailsElement,
            HTMLDialogElement, HTMLTemplateElement,
        ):
            assert cls is not None


# ---------------------------------------------------------------------------
# BACK-44: HTMLTemplateElement
# ---------------------------------------------------------------------------

class TestHTMLTemplateElement:
    def test_create_element_returns_typed_instance(self, doc: Document) -> None:
        el = doc.create_element("template")
        assert isinstance(el, HTMLTemplateElement)

    def test_content_returns_document_fragment(self, doc: Document) -> None:
        tmpl = doc.create_element("template")
        assert isinstance(tmpl.content, DocumentFragment)

    def test_content_is_cached(self, doc: Document) -> None:
        tmpl = doc.create_element("template")
        frag1 = tmpl.content
        frag2 = tmpl.content
        assert frag1 is frag2

    def test_programmatic_template_content_is_empty_fragment(self, doc: Document) -> None:
        tmpl = doc.create_element("template")
        frag = tmpl.content
        assert len(list(frag.child_nodes)) == 0

    def test_parsed_template_content_has_children(self) -> None:
        from aspose_html.html_document import HTMLDocument  # noqa: PLC0415
        html_doc = HTMLDocument.parse('<template id="t"><p>hello</p></template>')
        tmpl = html_doc.get_element_by_id("t")
        assert tmpl is not None
        assert isinstance(tmpl, HTMLTemplateElement)
        # Direct children of template element are in content, not _children
        assert len(list(tmpl.child_nodes)) == 0
        p = tmpl.content.query_selector("p")
        assert p is not None
        assert p.text_content == "hello"

    def test_template_children_is_empty_after_parse(self) -> None:
        from aspose_html.html_document import HTMLDocument  # noqa: PLC0415
        html_doc = HTMLDocument.parse('<template><p>hi</p></template>')
        tmpl = html_doc.query_selector("template")
        assert tmpl is not None
        assert len(list(tmpl.children)) == 0

    def test_clone_node_deep_clones_content(self) -> None:
        from aspose_html.html_document import HTMLDocument  # noqa: PLC0415
        html_doc = HTMLDocument.parse('<template id="t"><p>hi</p></template>')
        tmpl = html_doc.get_element_by_id("t")
        assert tmpl is not None
        clone = tmpl.clone_node(deep=True)
        assert isinstance(clone, HTMLTemplateElement)
        assert clone.content is not tmpl.content  # distinct fragment
        p = clone.content.query_selector("p")
        assert p is not None
        assert p.text_content == "hi"

    def test_clone_node_shallow_does_not_clone_content(self) -> None:
        from aspose_html.html_document import HTMLDocument  # noqa: PLC0415
        html_doc = HTMLDocument.parse('<template id="t"><p>hi</p></template>')
        tmpl = html_doc.get_element_by_id("t")
        assert tmpl is not None
        clone = tmpl.clone_node(deep=False)
        assert isinstance(clone, HTMLTemplateElement)
        # Shallow clone: content not copied
        assert clone._template_content is None

    def test_import_htmltemplateelement_from_dom(self) -> None:
        from aspose_html.dom import HTMLTemplateElement as T  # noqa: PLC0415
        assert T is not None
