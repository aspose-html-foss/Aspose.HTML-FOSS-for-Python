"""Tests for Document factory methods and query methods."""
from __future__ import annotations

import pytest

from aspose_html import HTMLDocument
from aspose_html.cssom import CSSStyleSheet
from aspose_html.dom import (
    CustomEvent,
    DOMConfiguration,
    Document,
    DOMImplementation,
    DocumentType,
    Element,
    Event,
    Text,
    Comment,
    DocumentFragment,
    NodeType,
    WrongDocumentError,
)
from aspose_html.dom._exceptions import InvalidCharacterError, NotSupportedError


@pytest.fixture
def doc() -> Document:
    return Document()


def test_create_element_returns_element_with_tag(doc: Document) -> None:
    el = doc.create_element("div")
    assert isinstance(el, Element)
    assert el.tag_name == "DIV"
    assert el.local_name == "div"


def test_create_text_node(doc: Document) -> None:
    """AC-11: create_text_node returns a Text with the correct data."""
    t = doc.create_text_node("hello world")
    assert isinstance(t, Text)
    assert t.data == "hello world"
    assert t.node_type == NodeType.TEXT_NODE


def test_create_comment_node(doc: Document) -> None:
    c = doc.create_comment("a comment")
    assert isinstance(c, Comment)
    assert c.data == "a comment"
    assert c.node_type == NodeType.COMMENT_NODE


def test_create_document_fragment(doc: Document) -> None:
    frag = doc.create_document_fragment()
    assert isinstance(frag, DocumentFragment)
    assert frag.node_type == NodeType.DOCUMENT_FRAGMENT_NODE
    assert frag.owner_document is doc


def test_get_element_by_id_found(doc: Document) -> None:
    """AC-6: get_element_by_id returns the correct element."""
    el = doc.create_element("div")
    el.set_attribute("id", "main")
    doc.append_child(el)
    assert doc.get_element_by_id("main") is el


def test_get_element_by_id_not_found(doc: Document) -> None:
    assert doc.get_element_by_id("nonexistent") is None


def test_get_elements_by_tag_name_wildcard(doc: Document) -> None:
    el = doc.create_element("div")
    span = doc.create_element("span")
    el.append_child(span)
    doc.append_child(el)
    result = doc.get_elements_by_tag_name("*")
    tags = {n.tag_name for n in result}  # type: ignore[union-attr]
    assert "DIV" in tags
    assert "SPAN" in tags


def test_get_elements_by_tag_name_specific(doc: Document) -> None:
    el = doc.create_element("p")
    doc.append_child(el)
    result = list(doc.get_elements_by_tag_name("p"))
    assert len(result) == 1
    assert result[0].tag_name == "P"  # type: ignore[union-attr]


def test_get_elements_by_class_name(doc: Document) -> None:
    el = doc.create_element("div")
    el.set_attribute("class", "a b")
    doc.append_child(el)
    assert len(list(doc.get_elements_by_class_name("a"))) == 1
    assert len(list(doc.get_elements_by_class_name("a b"))) == 1
    assert len(list(doc.get_elements_by_class_name("c"))) == 0


def test_compat_mode_default(doc: Document) -> None:
    """AC-9: default compat_mode is 'CSS1Compat'."""
    assert doc.compat_mode == "CSS1Compat"


def test_compat_mode_can_be_set(doc: Document) -> None:
    doc.compat_mode = "BackCompat"
    assert doc.compat_mode == "BackCompat"


def test_adopted_style_sheets_default_empty_list(doc: Document) -> None:
    assert doc.adopted_style_sheets == []


def test_adopted_style_sheets_assignment_preserves_order(doc: Document) -> None:
    first = CSSStyleSheet()
    second = CSSStyleSheet()

    doc.adopted_style_sheets = [first, second]

    adopted = doc.adopted_style_sheets
    assert adopted == [first, second]
    assert adopted[0] is first
    assert adopted[1] is second


def test_adopted_style_sheets_accepts_tuple_assignment(doc: Document) -> None:
    first = CSSStyleSheet()
    second = CSSStyleSheet()

    doc.adopted_style_sheets = (first, second)

    assert doc.adopted_style_sheets == [first, second]


def test_adopted_style_sheets_rejects_non_stylesheet_entries(doc: Document) -> None:
    valid = CSSStyleSheet()

    with pytest.raises(TypeError):
        doc.adopted_style_sheets = [valid, object()]  # type: ignore[list-item]


def test_adopted_style_sheets_rejects_non_sequence_assignment(doc: Document) -> None:
    with pytest.raises(TypeError):
        doc.adopted_style_sheets = "not-a-list"  # type: ignore[assignment]


def test_adopted_style_sheets_getter_returns_shallow_copy(doc: Document) -> None:
    first = CSSStyleSheet()
    doc.adopted_style_sheets = [first]

    snapshot = doc.adopted_style_sheets
    snapshot.append(CSSStyleSheet())

    assert doc.adopted_style_sheets == [first]


def test_attach_style_sheet_appends_to_adopted_style_sheets(doc: Document) -> None:
    first = CSSStyleSheet()
    second = CSSStyleSheet()

    doc.attach_style_sheet(first)
    doc.attach_style_sheet(second)

    assert doc.adopted_style_sheets == [first, second]


def test_detach_style_sheet_updates_adopted_style_sheets(doc: Document) -> None:
    first = CSSStyleSheet()
    second = CSSStyleSheet()
    doc.adopted_style_sheets = [first, second]

    doc.detach_style_sheet(first)

    assert doc.adopted_style_sheets == [second]


def test_style_sheets_order_is_adopted_then_tree_order_styles(doc: Document) -> None:
    adopted = CSSStyleSheet()
    doc.attach_style_sheet(adopted)

    html = doc.create_element("html")
    head = doc.create_element("head")
    first_style = doc.create_element("style")
    first_style.text_content = "p { color: red }"
    second_style = doc.create_element("style")
    second_style.text_content = "div { color: blue }"
    head.append_child(first_style)
    head.append_child(second_style)
    html.append_child(head)
    doc.append_child(html)

    sheets = list(doc.style_sheets)
    assert sheets[0] is adopted
    assert sheets[1].owner_node is first_style
    assert sheets[2].owner_node is second_style


def test_adopted_style_sheets_setter_replaces_attach_style_sheet_state(doc: Document) -> None:
    attached = CSSStyleSheet()
    replacement = CSSStyleSheet()

    doc.attach_style_sheet(attached)
    doc.adopted_style_sheets = [replacement]

    assert doc.adopted_style_sheets == [replacement]
    assert list(doc.style_sheets)[0] is replacement


def test_attach_style_sheet_preserves_identity_deduplication_with_adopted_storage(doc: Document) -> None:
    sheet = CSSStyleSheet()

    doc.adopted_style_sheets = [sheet]
    doc.attach_style_sheet(sheet)

    assert doc.adopted_style_sheets == [sheet]


def test_document_element_is_root_element(doc: Document) -> None:
    assert doc.document_element is None
    el = doc.create_element("html")
    doc.append_child(el)
    assert doc.document_element is el


def test_implementation_returns_domimplementation_instance(doc: Document) -> None:
    """Document.implementation returns DOMImplementation."""
    assert isinstance(doc.implementation, DOMImplementation)


def test_implementation_repeated_access_returns_same_identity(doc: Document) -> None:
    """Document.implementation is stable per document instance."""
    assert doc.implementation is doc.implementation


def test_implementation_is_distinct_for_separate_documents() -> None:
    """Different documents have distinct DOMImplementation objects."""
    left = Document()
    right = Document()

    assert left.implementation is not right.implementation


def test_dom_config_repeated_access_returns_same_identity(doc: Document) -> None:
    """dom_config is stable per document instance."""
    assert isinstance(doc.dom_config, DOMConfiguration)
    assert doc.dom_config is doc.dom_config


def test_dom_config_is_distinct_for_separate_documents() -> None:
    """Different documents have distinct DOMConfiguration objects."""
    left = Document()
    right = Document()
    assert left.dom_config is not right.dom_config


def test_dom_config_supported_parameter_get_set_is_deterministic(doc: Document) -> None:
    """Supported baseline parameters can be read/written deterministically."""
    cfg = doc.dom_config
    assert cfg.get_parameter("comments") is True
    assert cfg.can_set_parameter("comments", False) is True
    cfg.set_parameter("comments", False)
    assert cfg.get_parameter("comments") is False
    assert cfg.get_parameter("COMMENTS") is False


def test_dom_config_unknown_parameter_operations_raise(doc: Document) -> None:
    """Unsupported parameter lookups and assignments raise NotSupportedError."""
    cfg = doc.dom_config
    assert cfg.can_set_parameter("unknown-param", True) is False

    with pytest.raises(NotSupportedError):
        cfg.get_parameter("unknown-param")

    with pytest.raises(NotSupportedError):
        cfg.set_parameter("unknown-param", True)

    with pytest.raises(NotSupportedError):
        cfg.set_parameter("comments", "yes")


def test_normalize_document_merges_adjacent_text_and_removes_empty(doc: Document) -> None:
    """normalize_document delegates to Node.normalize subtree semantics."""
    root = doc.create_element("div")
    doc.append_child(root)
    root.append_child(doc.create_text_node("hello"))
    root.append_child(doc.create_text_node(""))
    root.append_child(doc.create_text_node(" world"))

    doc.normalize_document()

    assert len(root.child_nodes) == 1
    assert root.first_child is not None
    assert root.first_child.data == "hello world"


def test_normalize_document_is_idempotent(doc: Document) -> None:
    """Repeated normalize_document calls are stable once normalized."""
    root = doc.create_element("p")
    doc.append_child(root)
    root.append_child(doc.create_text_node("a"))
    root.append_child(doc.create_text_node("b"))

    doc.normalize_document()
    first_snapshot = [child.data for child in root.child_nodes]

    doc.normalize_document()
    second_snapshot = [child.data for child in root.child_nodes]

    assert first_snapshot == ["ab"]
    assert second_snapshot == first_snapshot


def test_dom_config_lifecycle_stable_across_normalize_document_calls(doc: Document) -> None:
    """dom_config identity/values remain stable across normalize_document usage."""
    cfg = doc.dom_config
    cfg.set_parameter("comments", False)

    root = doc.create_element("div")
    doc.append_child(root)
    root.append_child(doc.create_text_node("x"))
    root.append_child(doc.create_text_node("y"))

    doc.normalize_document()

    assert doc.dom_config is cfg
    assert cfg.get_parameter("comments") is False
    assert len(root.child_nodes) == 1
    assert root.first_child is not None
    assert root.first_child.data == "xy"


def test_normalize_document_on_already_normalized_tree_is_no_op(doc: Document) -> None:
    """normalize_document does not alter structure when already normalized."""
    root = doc.create_element("section")
    doc.append_child(root)
    text = doc.create_text_node("stable")
    child = doc.create_element("span")
    root.append_child(text)
    root.append_child(child)

    before = list(root.child_nodes)
    doc.normalize_document()
    after = list(root.child_nodes)

    assert after == before


def test_base_uri_falls_back_to_document_url_without_base_href() -> None:
    parsed = HTMLDocument.parse("<html><head></head><body></body></html>", base_url="https://example.com/a/")
    assert parsed.base_uri == parsed.url


def test_base_uri_uses_first_parseable_base_href_in_tree_order() -> None:
    parsed = HTMLDocument.parse(
        "<html><head>"
        "<base href='http://%'>"
        "<base href='assets/'>"
        "<base href='https://ignored.example/'>"
        "</head><body></body></html>",
        base_url="https://example.com/root/page.html",
    )
    assert parsed.base_uri == "https://example.com/root/assets/"


def test_base_uri_ignores_empty_or_unparseable_base_href() -> None:
    parsed = HTMLDocument.parse(
        "<html><head>"
        "<base href=''>"
        "<base href='http://%'>"
        "<base href='../ok/'>"
        "</head><body></body></html>",
        base_url="https://example.com/root/page.html",
    )
    assert parsed.base_uri == "https://example.com/ok/"


def test_base_uri_updates_when_winning_base_href_changes_or_is_removed() -> None:
    parsed = HTMLDocument.parse(
        "<html><head>"
        "<base href='assets/'>"
        "<base href='fallback/'>"
        "</head><body></body></html>",
        base_url="https://example.com/root/page.html",
    )

    bases = list(parsed.get_elements_by_tag_name("base"))
    assert len(bases) == 2

    first_base, second_base = bases
    assert parsed.base_uri == "https://example.com/root/assets/"

    first_base.set_attribute("href", "changed/")
    assert parsed.base_uri == "https://example.com/root/changed/"

    first_base.remove()
    assert parsed.base_uri == "https://example.com/root/fallback/"

    second_base.remove_attribute("href")
    assert parsed.base_uri == parsed.url


def test_implementation_access_has_no_dom_mutation_side_effects(doc: Document) -> None:
    """Accessing implementation does not mutate children or ownership."""
    root = doc.create_element("html")
    doc.append_child(root)
    before_children = list(doc.child_nodes)
    before_owner = root.owner_document

    _ = doc.implementation

    assert list(doc.child_nodes) == before_children
    assert doc.document_element is root
    assert root.owner_document is before_owner


def test_implementation_create_document_builds_expected_structure(doc: Document) -> None:
    """Factories exposed via document.implementation build baseline document structure."""
    doctype = doc.implementation.create_document_type("html", "", "")
    built = doc.implementation.create_document("http://www.w3.org/1999/xhtml", "html", doctype)

    assert built.document_type is doctype
    assert built.document_element is not None
    assert built.document_element.tag_name == "HTML"


def test_implementation_create_html_document_exposes_document_convenience_properties(
    doc: Document,
) -> None:
    """create_html_document output is aligned with head/body/title properties."""
    built = doc.implementation.create_html_document("Hello")

    assert built.document_element is not None
    assert built.document_element.tag_name == "HTML"
    assert built.head is not None
    assert built.head.tag_name == "HEAD"
    assert built.body is not None
    assert built.body.tag_name == "BODY"
    assert built.title == "Hello"


def test_implementation_create_html_document_title_setter_interoperates_with_factory(
    doc: Document,
) -> None:
    built = doc.implementation.create_html_document("")

    assert built.head is not None
    assert built.title == ""
    assert len(list(built.head.get_elements_by_tag_name("title"))) == 0

    built.title = "Updated"

    titles = list(built.head.get_elements_by_tag_name("title"))
    assert built.title == "Updated"
    assert len(titles) == 1
    assert titles[0].text_content == "Updated"


@pytest.mark.parametrize(
    ("feature", "version", "expected_supported"),
    [
        ("Core", None, True),
        ("XML", "3.0", True),
        ("Unknown", None, False),
        ("Core", "9.9", False),
    ],
)
def test_implementation_get_feature_matches_standalone_semantics(
    doc: Document,
    feature: str,
    version: str | None,
    expected_supported: bool,
) -> None:
    standalone = DOMImplementation()
    via_document = doc.implementation

    standalone_result = standalone.get_feature(feature, version)
    document_result = via_document.get_feature(feature, version)

    assert (standalone_result is standalone) is expected_supported
    assert (document_result is via_document) is expected_supported


def test_implementation_identity_stable_across_get_feature_calls(doc: Document) -> None:
    impl = doc.implementation

    _ = impl.get_feature("Core")
    _ = impl.get_feature("Unknown", "1.0")
    _ = impl.get_feature("Core", "9.9")

    assert doc.implementation is impl


def test_implementation_get_feature_has_no_document_side_effects(doc: Document) -> None:
    root = doc.create_element("html")
    body = doc.create_element("body")
    doc.append_child(root)
    root.append_child(body)
    doc.compat_mode = "BackCompat"
    before_children = list(doc.child_nodes)
    before_document_element = doc.document_element
    before_title = doc.title
    before_compat_mode = doc.compat_mode

    _ = doc.implementation.get_feature("Core")
    _ = doc.implementation.get_feature("Unknown", "1.0")

    assert list(doc.child_nodes) == before_children
    assert doc.document_element is before_document_element
    assert doc.title == before_title
    assert doc.compat_mode == before_compat_mode


def test_domimplementation_probes_do_not_regress_node_get_feature_baseline(
    doc: Document,
) -> None:
    root = doc.create_element("html")
    doc.append_child(root)

    _ = doc.implementation.has_feature("Core")
    _ = doc.implementation.get_feature("Core")
    _ = doc.implementation.get_feature("Unknown", "9.9")

    assert doc.get_feature("Core") is None
    assert root.get_feature("Core", "3.0") is None


def test_create_event_supported_interfaces_return_expected_types(doc: Document) -> None:
    """create_event returns baseline Event/CustomEvent objects by interface."""
    assert isinstance(doc.create_event("Event"), Event)
    assert isinstance(doc.create_event("Events"), Event)
    assert isinstance(doc.create_event("HTMLEvents"), Event)
    assert isinstance(doc.create_event("CustomEvent"), CustomEvent)


def test_create_event_unsupported_interface_raises_not_supported(doc: Document) -> None:
    """Unsupported event interfaces raise NotSupportedError."""
    with pytest.raises(NotSupportedError):
        doc.create_event("UnsupportedEvent")


def test_create_attribute_returns_null_namespace_attr(doc: Document) -> None:
    """create_attribute creates an unattached null-namespace Attr."""
    attr = doc.create_attribute("data-id")

    assert attr.name == "data-id"
    assert attr.local_name == "data-id"
    assert attr.value == ""
    assert attr.namespace_uri is None
    assert attr.owner_element is None
    assert attr.owner_document is doc


@pytest.mark.parametrize("name", ["", "bad name", "xlink:href"])
def test_create_attribute_invalid_name_raises(name: str, doc: Document) -> None:
    """create_attribute rejects empty, whitespace, and colon-containing names."""
    with pytest.raises(InvalidCharacterError):
        doc.create_attribute(name)


def test_create_attribute_ns_semantics_unchanged(doc: Document) -> None:
    """create_attribute_ns still preserves namespace/local-name split."""
    attr = doc.create_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href")

    assert attr.name == "xlink:href"
    assert attr.local_name == "href"
    assert attr.namespace_uri == "http://www.w3.org/1999/xlink"


# ------------------------------------------------------------------
# adopt_node tests —  / 
# ------------------------------------------------------------------

def test_adopt_node_removes_from_source_parent() -> None:
    """adopt_node removes the node from its original parent and document."""
    src = Document()
    dst = Document()
    div = src.create_element("div")
    src.append_child(div)

    dst.adopt_node(div)

    assert div.parent_node is None
    assert div.owner_document is dst
    assert len(src.child_nodes) == 0


def test_adopt_node_sets_owner_document_recursively() -> None:
    """adopt_node recursively updates owner_document on all descendants."""
    src = Document()
    dst = Document()
    div = src.create_element("div")
    span = src.create_element("span")
    div.append_child(span)
    src.append_child(div)

    dst.adopt_node(div)

    assert div.owner_document is dst
    assert span.owner_document is dst


def test_adopt_node_returns_same_object() -> None:
    """adopt_node returns the identical Python object (not a copy)."""
    src = Document()
    dst = Document()
    el = src.create_element("p")

    result = dst.adopt_node(el)

    assert result is el


def test_adopt_node_document_raises_not_supported() -> None:
    """adopt_node(Document) raises NotSupportedError per WHATWG DOM §5.3.8."""
    src = Document()
    dst = Document()

    with pytest.raises(NotSupportedError):
        dst.adopt_node(src)


def test_adopt_node_detached_node() -> None:
    """adopt_node succeeds for a detached node; updates owner_document."""
    src = Document()
    dst = Document()
    el = src.create_element("div")
    # el has no parent — detached node

    dst.adopt_node(el)

    assert el.owner_document is dst
    assert el.parent_node is None


def test_adopt_node_then_append_does_not_raise_wrong_document() -> None:
    """After adopt_node, append_child must not raise WrongDocumentError (AC-3)."""
    src = Document()
    dst = Document()
    el = src.create_element("div")

    dst.adopt_node(el)

    # Must not raise WrongDocumentError
    dst.append_child(el)
    assert el.parent_node is dst


# ------------------------------------------------------------------
# import_node tests —  / 
# ------------------------------------------------------------------

def test_import_node_shallow() -> None:
    """import_node(deep=False) clones only the node, not its children."""
    src = Document()
    dst = Document()
    parent = src.create_element("div")
    child = src.create_element("span")
    parent.append_child(child)
    src.append_child(parent)

    clone = dst.import_node(parent, deep=False)

    assert clone is not parent
    assert clone.parent_node is None
    assert len(clone.child_nodes) == 0
    assert clone.owner_document is dst
    # Original tree unmodified
    assert parent.parent_node is src
    assert len(parent.child_nodes) == 1


def test_import_node_deep() -> None:
    """import_node(deep=True) clones the entire subtree."""
    src = Document()
    dst = Document()
    parent = src.create_element("div")
    child = src.create_element("span")
    parent.append_child(child)
    src.append_child(parent)

    clone = dst.import_node(parent, deep=True)

    assert len(clone.child_nodes) == 1
    cloned_child = clone.first_child
    assert cloned_child is not child
    assert clone.owner_document is dst
    assert cloned_child.owner_document is dst  # type: ignore[union-attr]
    # Original tree unmodified
    assert len(parent.child_nodes) == 1
    assert child.owner_document is src


def test_import_node_does_not_modify_original() -> None:
    """import_node leaves the original node in its original tree."""
    src = Document()
    dst = Document()
    el = src.create_element("p")
    src.append_child(el)

    dst.import_node(el, deep=False)

    assert el.parent_node is src
    assert el.owner_document is src


def test_import_node_document_raises_not_supported() -> None:
    """import_node(Document) raises NotSupportedError per WHATWG DOM §5.3.6."""
    src = Document()
    dst = Document()

    with pytest.raises(NotSupportedError):
        dst.import_node(src)


def test_import_node_default_deep_is_false() -> None:
    """import_node with no deep argument defaults to shallow clone."""
    src = Document()
    dst = Document()
    parent = src.create_element("div")
    child = src.create_element("span")
    parent.append_child(child)

    clone = dst.import_node(parent)  # no deep argument

    assert len(clone.child_nodes) == 0


# ---------------------------------------------------------------------------
# Document.character_set / charset / input_encoding / content_type ()
# ---------------------------------------------------------------------------

def test_character_set_default() -> None:
    """Document().character_set defaults to 'UTF-8'."""
    assert Document().character_set == "UTF-8"


def test_content_type_default() -> None:
    """Document().content_type is always 'text/html'."""
    assert Document().content_type == "text/html"


def test_charset_and_input_encoding_alias_character_set() -> None:
    """charset and input_encoding must return the same value as character_set."""
    doc = Document()
    assert doc.charset == doc.character_set
    assert doc.input_encoding == doc.character_set


def test_character_set_after_utf8_bytes_parse() -> None:
    """HTMLDocument.parse(bytes) with UTF-8 content sets character_set to the detected encoding label."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse(b"<p>hi</p>")
    # The encoding detection module returns WHATWG canonical names; for UTF-8
    # input the label is "utf-8" (lowercase as returned by the encoding module).
    assert doc.character_set.lower() == "utf-8"


def test_character_set_after_windows1252_bytes_parse() -> None:
    """HTMLDocument.parse(bytes) with windows-1252 charset meta propagates encoding."""
    from aspose_html.html_document import HTMLDocument
    html = b'<html><head><meta charset="windows-1252"></head><body>test</body></html>'
    doc = HTMLDocument.parse(html)
    assert doc.character_set == "windows-1252"


def test_character_set_after_str_parse_stays_utf8() -> None:
    """HTMLDocument.parse(str) leaves character_set at the default 'UTF-8'."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<p>hi</p>")
    assert doc.character_set == "UTF-8"


def test_character_set_is_read_only() -> None:
    """Assigning to character_set raises AttributeError (read-only property)."""
    doc = Document()
    with pytest.raises(AttributeError):
        doc.character_set = "iso-8859-1"  # type: ignore[misc]


# Document.create_cdata_section ()

def test_create_cdata_section_returns_correct_type() -> None:
    """AC-1: returns CDATASection with node_type 4 and correct data."""
    from aspose_html.dom import CDATASection
    doc = Document()
    cds = doc.create_cdata_section("some data")
    assert isinstance(cds, CDATASection)
    assert cds.node_type == 4
    assert cds.data == "some data"


def test_create_cdata_section_owner_document() -> None:
    """AC-1: returned node's owner_document is the creating document."""
    doc = Document()
    cds = doc.create_cdata_section("hello")
    assert cds.owner_document is doc


def test_create_cdata_section_invalid_character_error() -> None:
    """AC-2: ']]>' in data raises InvalidCharacterError."""
    doc = Document()
    with pytest.raises(InvalidCharacterError):
        doc.create_cdata_section("has ]]> embedded")


def test_create_cdata_section_empty_string() -> None:
    """AC-1: empty string is valid."""
    doc = Document()
    cds = doc.create_cdata_section("")
    assert cds.data == ""


def test_create_cdata_section_appendable() -> None:
    """AC-3: created node can be appended to a DOM element."""
    doc = Document()
    parent = doc.create_element("div")
    cds = doc.create_cdata_section("raw text")
    parent.append_child(cds)
    assert list(parent.child_nodes)[0] is cds


# Document.referrer / domain / last_modified ()

def test_referrer_default() -> None:
    """Document().referrer is always empty string."""
    assert Document().referrer == ""


def test_last_modified_default() -> None:
    """Document().last_modified is always empty string."""
    assert Document().last_modified == ""


def test_domain_default_about_blank() -> None:
    """Document().domain is empty string when url is 'about:blank'."""
    assert Document().domain == ""


def test_domain_from_base_url() -> None:
    """domain extracts hostname from base_url passed to HTMLDocument.parse."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse(b"<p>hi</p>", base_url="https://example.com/page")
    assert doc.domain == "example.com"


def test_referrer_is_read_only() -> None:
    """Setting referrer raises AttributeError."""
    doc = Document()
    with pytest.raises(AttributeError):
        doc.referrer = "x"  # type: ignore[misc]


def test_domain_is_read_only() -> None:
    """Setting domain raises AttributeError."""
    doc = Document()
    with pytest.raises(AttributeError):
        doc.domain = "x"  # type: ignore[misc]


def test_last_modified_is_read_only() -> None:
    """Setting last_modified raises AttributeError."""
    doc = Document()
    with pytest.raises(AttributeError):
        doc.last_modified = "x"  # type: ignore[misc]


# ---------------------------------------------------------------------------
#  — Group G cross-group integration tests ()
# Verify that Groups A–C compose correctly with the rest of the DOM API.
# ---------------------------------------------------------------------------

def test_create_cdata_section_node_type() -> None:
    """Group B integration: create_cdata_section returns node with correct node_type.

    Verifies that the CDATASection returned by create_cdata_section integrates
    correctly with the DOM node-type system (node_type == 4 per WHATWG DOM).
    """
    from aspose_html.dom import CDATASection
    doc = Document()
    cds = doc.create_cdata_section("integration data")
    assert cds.node_type == NodeType.CDATA_SECTION_NODE
    assert isinstance(cds, CDATASection)
    # Confirm it can be inserted into the tree (tree integration)
    parent = doc.create_element("div")
    parent.append_child(cds)
    assert list(parent.child_nodes)[0] is cds
    assert list(parent.child_nodes)[0].node_type == NodeType.CDATA_SECTION_NODE


def test_character_set_default_utf8() -> None:
    """Group A integration: character_set defaults to 'UTF-8' on a bare Document.

    Verifies that charset, character_set, and input_encoding all return the
    same UTF-8 default and agree with each other (cross-alias integration).
    """
    doc = Document()
    assert doc.character_set == "UTF-8"
    assert doc.charset == "UTF-8"
    assert doc.input_encoding == "UTF-8"
    # All three aliases return identical values
    assert doc.character_set == doc.charset == doc.input_encoding


def test_domain_from_parsed_url() -> None:
    """Group C integration: domain reflects host portion of document URL.

    Verifies that domain is extracted correctly from the base_url argument
    passed to HTMLDocument.parse, testing the URL-parsing integration path.
    """
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse(b"<p>content</p>", base_url="https://example.org/path/page")
    assert doc.domain == "example.org"
    # referrer is unset in this context (server-side, no navigation)
    assert doc.referrer == ""


# ---------------------------------------------------------------------------
#  — Document.forms / images / links / scripts / anchors
# Live HTMLCollection properties ( / )
# ---------------------------------------------------------------------------

def test_forms_live_collection() -> None:
    """Document.forms returns a live collection that rescans on every access."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body><form></form></body></html>")

    assert len(doc.forms) == 1

    # Liveness: appending a second form is reflected immediately.
    _ = doc.body.append_child(doc.create_element("form"))
    assert len(doc.forms) == 2


def test_forms_excludes_non_form_elements() -> None:
    """Document.forms excludes elements that are not <form>."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body><div></div><input/></body></html>")
    assert len(doc.forms) == 0


def test_images_basic() -> None:
    """Document.images returns all <img> elements."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse('<html><body><img src="a.png"/></body></html>')
    assert len(doc.images) == 1


def test_images_excludes_non_img_elements() -> None:
    """Document.images excludes elements that are not <img>."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body><picture></picture><figure></figure></body></html>")
    assert len(doc.images) == 0


def test_links_includes_a_href_and_area_href() -> None:
    """Document.links includes <a href> and <area href> but not bare <a>."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse(
        "<html><body>"
        '<a href="#">with-href</a>'
        "<a>no-href</a>"
        '<map><area href="b.html"/></map>'
        "</body></html>"
    )
    links = list(doc.links)
    assert len(links) == 2  # the <a href> and the <area href>
    tag_names = {el.tag_name for el in links}  # type: ignore[union-attr]
    assert "A" in tag_names
    assert "AREA" in tag_names


def test_links_excludes_a_without_href() -> None:
    """<a> elements without href are not in Document.links."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body><a name='top'>anchor</a></body></html>")
    assert len(doc.links) == 0


def test_scripts_basic() -> None:
    """Document.scripts returns all <script> elements."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><head><script></script></head></html>")
    assert len(doc.scripts) == 1


def test_scripts_excludes_non_script_elements() -> None:
    """Document.scripts excludes non-<script> elements."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><head><style></style></head></html>")
    assert len(doc.scripts) == 0


def test_anchors_name_only() -> None:
    """Document.anchors includes only <a name=...>, not bare <a href>."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse(
        "<html><body>"
        '<a name="top">named-only</a>'
        '<a href="#">href-only</a>'
        '<a href="#" name="both">href-and-name</a>'
        "</body></html>"
    )
    anchors = list(doc.anchors)
    # Both 'named-only' and 'href-and-name' carry name= so both appear.
    assert len(anchors) == 2
    for el in anchors:
        assert el.has_attribute("name")  # type: ignore[union-attr]


def test_anchors_excludes_a_without_name() -> None:
    """<a> elements without a name attribute are excluded from Document.anchors."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse('<html><body><a href="#">link</a></body></html>')
    assert len(doc.anchors) == 0


def test_all_five_properties_empty_document() -> None:
    """All five live-collection properties return empty collections on a bare Document."""
    doc = Document()
    assert len(doc.forms) == 0
    assert len(doc.images) == 0
    assert len(doc.links) == 0
    assert len(doc.scripts) == 0
    assert len(doc.anchors) == 0


def test_links_live_collection_reflects_insertion() -> None:
    """Document.links is live — a newly appended <a href> appears immediately."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body></body></html>")
    assert len(doc.links) == 0

    new_a = doc.create_element("a")
    new_a.set_attribute("href", "https://example.com")
    _ = doc.body.append_child(new_a)
    assert len(doc.links) == 1


def test_scripts_live_collection_reflects_insertion() -> None:
    """Document.scripts is live — a newly appended <script> appears immediately."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><head></head></html>")
    assert len(doc.scripts) == 0

    script = doc.create_element("script")
    _ = doc.head.append_child(script)
    assert len(doc.scripts) == 1


# ---------------------------------------------------------------------------
# : Document.ready_state, Document.embeds, Document.applets ()
# ---------------------------------------------------------------------------


def test_document_ready_state_empty_document() -> None:
    """AC-1: Document().ready_state is always 'complete'."""
    doc = Document()
    assert doc.ready_state == "complete"


def test_document_ready_state_parsed_document() -> None:
    """AC-2: ready_state is 'complete' on a parsed HTMLDocument."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body><p>hello</p></body></html>")
    assert doc.ready_state == "complete"


def test_document_ready_state_internal_navigation_progression_helpers() -> None:
    doc = Document()
    assert doc.ready_state == "complete"

    doc._navigation_prepare_replacement()
    assert doc.ready_state == "loading"

    doc._navigation_mark_parser_started()
    assert doc.ready_state == "interactive"

    doc._navigation_mark_complete()
    assert doc.ready_state == "complete"


def test_document_embeds_empty() -> None:
    """AC-3: Document().embeds returns an empty HTMLCollection for a bare document."""
    doc = Document()
    assert len(doc.embeds) == 0


def test_document_embeds_with_element() -> None:
    """AC-4: Parsed document with <embed> has len == 1 and correct tag_name."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse('<html><body><embed src="x.swf"></body></html>')
    assert len(doc.embeds) == 1
    assert doc.embeds[0].tag_name == "EMBED"  # type: ignore[union-attr]


def test_document_embeds_live_collection() -> None:
    """AC-4 (live): embeds collection reflects insertion after creation."""
    from aspose_html.html_document import HTMLDocument
    doc = HTMLDocument.parse("<html><body></body></html>")
    assert len(doc.embeds) == 0

    embed_el = doc.create_element("embed")
    _ = doc.body.append_child(embed_el)
    assert len(doc.embeds) == 1


def test_document_applets_always_empty() -> None:
    """AC-5: Document().applets always returns an empty HTMLCollection."""
    doc = Document()
    assert len(doc.applets) == 0


def test_all_live_collections_empty_document() -> None:
    """All live-collection properties return empty on a bare Document, including embeds/applets."""
    doc = Document()
    assert len(doc.forms) == 0
    assert len(doc.images) == 0
    assert len(doc.links) == 0
    assert len(doc.scripts) == 0
    assert len(doc.anchors) == 0
    assert len(doc.embeds) == 0
    assert len(doc.applets) == 0


# ------------------------------------------------------------------
#  / : ParentNode element-child properties + active_element
# ------------------------------------------------------------------

def test_document_first_element_child_parsed_html() -> None:
    """AC-14: first_element_child.tag_name == 'HTML' for a standard parsed document."""
    doc = HTMLDocument.parse("<html><body></body></html>")
    assert doc.first_element_child is not None
    assert doc.first_element_child.tag_name == "HTML"


def test_document_last_element_child_parsed_html() -> None:
    """AC-15: last_element_child.tag_name == 'HTML' for a standard parsed document."""
    doc = HTMLDocument.parse("<html><body></body></html>")
    assert doc.last_element_child is not None
    assert doc.last_element_child.tag_name == "HTML"


def test_document_child_element_count_parsed_html() -> None:
    """AC-16: child_element_count == 1 for a standard parsed document."""
    doc = HTMLDocument.parse("<html><body></body></html>")
    assert doc.child_element_count == 1


def test_document_active_element_is_none() -> None:
    """AC-17: active_element is None for any document state (headless stub)."""
    doc = HTMLDocument.parse("<html><body><input></body></html>")
    assert doc.active_element is None


def test_document_first_element_child_empty_document() -> None:
    """AC (empty): first_element_child is None for an empty Document."""
    doc = Document()
    assert doc.first_element_child is None


def test_document_last_element_child_empty_document() -> None:
    """AC (empty): last_element_child is None for an empty Document."""
    doc = Document()
    assert doc.last_element_child is None


def test_document_child_element_count_empty_document() -> None:
    """AC (empty): child_element_count == 0 for an empty Document."""
    doc = Document()
    assert doc.child_element_count == 0


def test_document_active_element_empty_document() -> None:
    """active_element is None on bare Document() as well."""
    doc = Document()
    assert doc.active_element is None


def test_document_first_last_element_child_skips_non_element_children() -> None:
    """first/last_element_child skip Comment and Text nodes; only return Elements."""
    doc = Document()
    comment = doc.create_comment("a comment")
    doc.append_child(comment)
    # No element child yet
    assert doc.first_element_child is None
    assert doc.last_element_child is None
    assert doc.child_element_count == 0
    # Now add an element
    el = doc.create_element("html")
    doc.append_child(el)
    assert doc.first_element_child is el
    assert doc.last_element_child is el
    assert doc.child_element_count == 1


def test_document_get_animations_returns_empty_list() -> None:
    doc = Document()

    animations = doc.get_animations()
    assert animations == []
    assert isinstance(animations, list)


# ---------------------------------------------------------------------------
#  — Document IDL tail (, )
# AC-25 through AC-27
# ---------------------------------------------------------------------------

def test_document_compatible_mode() -> None:
    """AC-25: compatible_mode returns 'CSS1Compat' for a base Document."""
    doc = Document()
    assert doc.compatible_mode == "CSS1Compat"


def test_document_get_elements_by_tag_name_ns_wildcard_namespace() -> None:
    """AC-26: get_elements_by_tag_name_ns('*', 'div') returns all div elements."""
    doc = Document()
    root = doc.create_element("html")
    _ = doc.append_child(root)
    div1 = doc.create_element("div")
    div2 = doc.create_element("div")
    p = doc.create_element("p")
    _ = root.append_child(div1)
    _ = root.append_child(div2)
    _ = root.append_child(p)
    results = doc.get_elements_by_tag_name_ns("*", "div")
    assert len(results) == 2
    assert div1 in results
    assert div2 in results
    assert p not in results


def test_document_get_elements_by_tag_name_ns_wildcard_both() -> None:
    """get_elements_by_tag_name_ns('*', '*') returns all elements."""
    doc = Document()
    root = doc.create_element("html")
    _ = doc.append_child(root)
    div = doc.create_element("div")
    p = doc.create_element("p")
    _ = root.append_child(div)
    _ = root.append_child(p)
    results = doc.get_elements_by_tag_name_ns("*", "*")
    assert root in results
    assert div in results
    assert p in results


def test_document_get_elements_by_tag_name_ns_specific_namespace() -> None:
    """AC-27: namespace filter returns only HTML-namespace p elements."""
    _XHTML = "http://www.w3.org/1999/xhtml"
    doc = Document()
    root = doc.create_element("html")
    _ = doc.append_child(root)
    p1 = doc.create_element("p")
    p2 = doc.create_element("p")
    div = doc.create_element("div")
    _ = root.append_child(p1)
    _ = root.append_child(p2)
    _ = root.append_child(div)
    # p elements created with create_element get xhtml namespace
    results = doc.get_elements_by_tag_name_ns(_XHTML, "p")
    assert p1 in results
    assert p2 in results
    assert div not in results


def test_document_get_elements_by_tag_name_ns_no_match() -> None:
    """Empty list when nothing matches namespace filter."""
    doc = Document()
    root = doc.create_element("html")
    _ = doc.append_child(root)
    _ = root.append_child(doc.create_element("div"))
    results = doc.get_elements_by_tag_name_ns("http://other.example.org/ns", "div")
    assert results == []


def test_document_get_elements_by_tag_name_ns_returns_list() -> None:
    """Return type is a list (not live HTMLCollection)."""
    doc = Document()
    results = doc.get_elements_by_tag_name_ns("*", "*")
    assert isinstance(results, list)


# ---------------------------------------------------------------------------
#  — Document IDL tail ( / )
# ---------------------------------------------------------------------------

def test_document_full_screen_enabled_false() -> None:
    """AC-10 (): Document.full_screen_enabled is False."""
    assert Document().full_screen_enabled is False


def test_document_fullscreen_element_none() -> None:
    """AC-10 (): Document.fullscreen_element is None."""
    assert Document().fullscreen_element is None


def test_document_pointer_lock_element_none() -> None:
    """AC-10 (): Document.pointer_lock_element is None."""
    assert Document().pointer_lock_element is None


def test_document_element_from_point_none() -> None:
    """AC-11 (): Document.element_from_point returns None."""
    assert Document().element_from_point(0, 0) is None


def test_document_elements_from_point_empty() -> None:
    """AC-11 (): Document.elements_from_point returns empty list."""
    assert Document().elements_from_point(0, 0) == []


def test_document_exec_command_false() -> None:
    """AC-12 (): Document.exec_command returns False."""
    assert Document().exec_command("bold") is False


def test_document_query_command_enabled_false() -> None:
    """AC-12 (): Document.query_command_enabled returns False."""
    assert Document().query_command_enabled("bold") is False


def test_document_timeline_current_time() -> None:
    """AC-13 (): Document.timeline is not None; current_time == 0.0."""
    from aspose_html.dom._document import _DocumentTimeline
    doc = Document()
    assert doc.timeline is not None
    assert doc.timeline.current_time == 0.0
    assert isinstance(doc.timeline, _DocumentTimeline)


def test_document_has_storage_access_true() -> None:
    """AC-14 (): Document.has_storage_access returns True."""
    assert Document().has_storage_access() is True


def test_document_request_storage_access_none() -> None:
    """AC-14 (): Document.request_storage_access returns None."""
    assert Document().request_storage_access() is None


# ---------------------------------------------------------------------------
#  — Document IDL tail ( / )
# ---------------------------------------------------------------------------

def test_document_all_nonempty() -> None:
    """AC-13: doc.all is not None; list(doc.all) is non-empty for a parsed document."""
    doc = HTMLDocument.parse("<html><body><p>Hi</p></body></html>")
    assert doc.all is not None
    assert len(list(doc.all)) > 0


def test_document_all_integer_index() -> None:
    """AC-13: doc.all[0] returns an Element."""
    doc = HTMLDocument.parse("<html><body><p>Hi</p></body></html>")
    first = doc.all[0]
    assert first is not None


def test_document_plugins_same_length_as_embeds() -> None:
    """AC-14: doc.plugins returns the same content as doc.embeds."""
    doc = HTMLDocument.parse("<html><body><embed src='a.swf'></body></html>")
    assert len(doc.plugins) == len(doc.embeds)


def test_document_plugins_empty_when_no_embeds() -> None:
    """AC-14: doc.plugins is empty when there are no <embed> elements."""
    doc = HTMLDocument.parse("<html><body></body></html>")
    assert len(doc.plugins) == 0
    assert len(doc.embeds) == 0


def test_document_children_returns_html_element() -> None:
    """AC-15: doc.children returns HTMLCollection with <html> as first item."""
    doc = HTMLDocument.parse("<html><body></body></html>")
    children = doc.children
    assert len(children) == 1
    assert children[0].tag_name == "HTML"
