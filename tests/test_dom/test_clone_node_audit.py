"""Clone node audit tests —  / .

Verifies that clone_node() correctly handles:
  - namespaced attributes ( /  fix)
  - lazy-init slots isolation (_class_list, _style_declaration, _dataset)
  - event listeners not copied
  - HTMLTemplateElement._template_content deep/shallow clone
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document
from aspose_html.html_document import HTMLDocument

XLINK = "http://www.w3.org/1999/xlink"
XML_NS = "http://www.w3.org/XML/1998/namespace"


@pytest.fixture()
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
#  fix: namespaced attributes preserved on clone
# ---------------------------------------------------------------------------

def test_namespaced_attr_preserved_on_clone(doc: Document) -> None:
    """Cloning an element with a namespaced attr preserves namespace_uri and local_name."""
    el = doc.create_element("svg")
    el.set_attribute_ns(XLINK, "xlink:href", "#target")

    clone = el.clone_node(deep=False)

    # get_attribute_ns must return the correct value on the clone.
    assert clone.get_attribute_ns(XLINK, "href") == "#target"  # type: ignore[union-attr]

    # Verify the Attr on the clone still carries namespace metadata.
    attr = clone.get_attribute_node("xlink:href")  # type: ignore[union-attr]
    assert attr is not None
    assert attr._namespace_uri == XLINK
    assert attr._local_name_ns == "href"


def test_namespaced_attr_independence_from_original(doc: Document) -> None:
    """Mutating a namespaced attr on the clone does not affect the original."""
    el = doc.create_element("svg")
    el.set_attribute_ns(XLINK, "xlink:href", "#original")

    clone = el.clone_node(deep=False)
    clone.set_attribute_ns(XLINK, "xlink:href", "#clone")  # type: ignore[union-attr]

    assert el.get_attribute_ns(XLINK, "href") == "#original"
    assert clone.get_attribute_ns(XLINK, "href") == "#clone"  # type: ignore[union-attr]


def test_multiple_namespaced_attrs_preserved_on_clone(doc: Document) -> None:
    """All namespaced attrs from multiple namespaces are preserved on clone."""
    el = doc.create_element("svg")
    el.set_attribute_ns(XLINK, "xlink:href", "#link")
    el.set_attribute_ns(XML_NS, "xml:lang", "en")
    el.set_attribute("id", "plain")

    clone = el.clone_node(deep=False)

    assert clone.get_attribute_ns(XLINK, "href") == "#link"  # type: ignore[union-attr]
    assert clone.get_attribute_ns(XML_NS, "lang") == "en"  # type: ignore[union-attr]
    assert clone.get_attribute("id") == "plain"  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Non-namespaced attributes — regression guard
# ---------------------------------------------------------------------------

def test_non_namespaced_attr_clone_unchanged(doc: Document) -> None:
    """Non-namespaced attrs still clone correctly (regression guard)."""
    el = doc.create_element("div")
    el.set_attribute("id", "foo")
    el.set_attribute("class", "bar baz")
    el.set_attribute("data-x", "1")

    clone = el.clone_node(deep=False)

    assert clone.get_attribute("id") == "foo"  # type: ignore[union-attr]
    assert clone.get_attribute("class") == "bar baz"  # type: ignore[union-attr]
    assert clone.get_attribute("data-x") == "1"  # type: ignore[union-attr]
    # All three attrs present, no extras
    assert len(clone.attributes) == 3  # type: ignore[union-attr]


def test_element_ns_clone_preserves_namespaced_attrs() -> None:
    doc = Document()
    el = doc.create_element_ns("http://www.w3.org/2000/svg", "svg")
    el.set_attribute_ns(XLINK, "xlink:href", "#target")

    clone = el.clone_node(deep=False)

    assert clone.get_attribute_ns(XLINK, "href") == "#target"  # type: ignore[union-attr]
    assert clone.is_equal_node(el)


def test_html_element_clone_preserves_namespaced_attrs() -> None:
    doc = Document()
    el = doc.create_element("a")
    el.set_attribute_ns(XLINK, "xlink:href", "#target")
    el.set_attribute("id", "plain")

    clone = el.clone_node(deep=False)

    assert clone.get_attribute_ns(XLINK, "href") == "#target"  # type: ignore[union-attr]
    assert clone.get_attribute("id") == "plain"  # type: ignore[union-attr]
    assert clone.is_equal_node(el)


# ---------------------------------------------------------------------------
# Lazy slots not aliased on clone
# ---------------------------------------------------------------------------

def test_lazy_slots_not_aliased_on_clone(doc: Document) -> None:
    """_class_list, _style_declaration, _dataset are not copied to clone.

    After a clone, mutating the clone's class_list / style / dataset must
    not affect the original. This is guaranteed when the lazy slots are
    reset to None on clone construction (confirmed by reading code — the
    fresh Element() constructor call sets all three to None).
    """
    el = doc.create_element("div")
    el.set_attribute("class", "foo")
    el.set_attribute("style", "color:red")
    el.set_attribute("data-x", "1")

    # Access lazy slots on original to initialise them.
    _ = el.class_list
    _ = el.style
    _ = el.dataset

    clone = el.clone_node(deep=False)

    # Clone's lazy slots must be None (not yet initialized) — they must not
    # be aliased from the original.
    assert clone._class_list is None  # type: ignore[union-attr]
    assert clone._style_declaration is None  # type: ignore[union-attr]
    assert clone._dataset is None  # type: ignore[union-attr]

    # After mutation on the clone, the original must be unchanged.
    clone.class_list.add("bar")  # type: ignore[union-attr]
    assert "bar" not in el.class_name
    assert "bar" in clone.class_name  # type: ignore[union-attr]


def test_dataset_independence_after_clone(doc: Document) -> None:
    """Mutations to the clone's dataset do not affect the original."""
    el = doc.create_element("div")
    el.set_attribute("data-x", "1")

    clone = el.clone_node(deep=False)
    clone.dataset["y"] = "2"  # type: ignore[union-attr]

    assert el.get_attribute("data-y") is None
    assert clone.get_attribute("data-y") == "2"  # type: ignore[union-attr]


def test_style_independence_after_clone(doc: Document) -> None:
    """Mutations to the clone's style do not affect the original."""
    el = doc.create_element("span")
    el.set_attribute("style", "color:red")

    clone = el.clone_node(deep=False)
    clone.style["font-size"] = "12px"  # type: ignore[union-attr]

    # Original style must not contain font-size
    original_css = el.style.css_text
    assert "font-size" not in original_css


# ---------------------------------------------------------------------------
# Event listeners not copied on clone
# ---------------------------------------------------------------------------

def test_event_listeners_not_copied_on_clone(doc: Document) -> None:
    """Cloned node has no event listeners from the original."""
    el = doc.create_element("button")
    called: list[object] = []
    el.add_event_listener("click", lambda e: called.append(e))

    clone = el.clone_node(deep=False)

    # Clone's _event_listeners must be None (never initialized) — not aliased
    # from the original. Per WHATWG DOM §4.5 step 3.
    assert clone._event_listeners is None  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# HTMLTemplateElement clone — depends on 
# ---------------------------------------------------------------------------

def test_template_content_deep_clone() -> None:
    """Deep clone of HTMLTemplateElement correctly clones content fragment."""
    from aspose_html.dom.html._elements import HTMLTemplateElement  # noqa: PLC0415
    from aspose_html.dom._document_fragment import DocumentFragment  # noqa: PLC0415

    doc = HTMLDocument.parse(
        "<!DOCTYPE html><html><body>"
        "<template id='t'><p>hello</p></template>"
        "</body></html>"
    )
    tmpl = doc.get_element_by_id("t")
    assert isinstance(tmpl, HTMLTemplateElement)

    # Ensure content fragment is populated by the tree builder.
    content = tmpl.content
    assert isinstance(content, DocumentFragment)
    assert len(content.child_nodes) > 0

    clone = tmpl.clone_node(deep=True)

    assert isinstance(clone, HTMLTemplateElement)
    # Deep clone must have its own content fragment (not the same object).
    assert clone._template_content is not None
    assert clone._template_content is not tmpl._template_content
    # The cloned content must have the same number of children.
    assert len(clone.content.child_nodes) == len(content.child_nodes)


def test_template_content_shallow_clone() -> None:
    """Shallow clone of HTMLTemplateElement does NOT copy content."""
    from aspose_html.dom.html._elements import HTMLTemplateElement  # noqa: PLC0415

    doc = HTMLDocument.parse(
        "<!DOCTYPE html><html><body>"
        "<template id='t'><p>hello</p></template>"
        "</body></html>"
    )
    tmpl = doc.get_element_by_id("t")
    assert isinstance(tmpl, HTMLTemplateElement)

    # Initialise content so the original has a populated fragment.
    _ = tmpl.content

    clone = tmpl.clone_node(deep=False)

    assert isinstance(clone, HTMLTemplateElement)
    # Shallow clone: _template_content must NOT be copied.
    assert clone._template_content is None
