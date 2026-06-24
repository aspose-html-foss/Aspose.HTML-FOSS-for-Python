"""Tests for HTMLElement global reflected properties (, ).

Covers acceptance criteria AC-1 through AC-10 from .

Properties tested:
- hidden (boolean IDL attribute)
- title (string IDL attribute)
- lang (string IDL attribute)
- tab_index (integer IDL attribute)
- access_key (string IDL attribute)
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, HTMLElement
from aspose_html.dom.html import (
    HTMLAnchorElement,
    HTMLDivElement,
)


@pytest.fixture
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# hidden — AC-1, AC-2
# ---------------------------------------------------------------------------

def test_hidden_getter_absent(doc: Document) -> None:
    """AC-1: el.hidden returns False when 'hidden' attribute is absent."""
    el = doc.create_element("div")
    assert el.hidden is False


def test_hidden_getter_present(doc: Document) -> None:
    """AC-1: el.hidden returns True when 'hidden' attribute is present."""
    el = doc.create_element("div")
    el.set_attribute("hidden", "")
    assert el.hidden is True


def test_hidden_setter_true(doc: Document) -> None:
    """AC-2: el.hidden = True sets hidden='' and has_attribute returns True."""
    el = doc.create_element("p")
    el.hidden = True
    assert el.has_attribute("hidden")
    assert el.get_attribute("hidden") == ""


def test_hidden_setter_false(doc: Document) -> None:
    """AC-2: el.hidden = False removes the 'hidden' attribute."""
    el = doc.create_element("p")
    el.set_attribute("hidden", "")
    assert el.hidden is True
    el.hidden = False
    assert el.has_attribute("hidden") is False


def test_hidden_false_when_absent_no_op(doc: Document) -> None:
    """el.hidden = False when already absent does not add attribute."""
    el = doc.create_element("span")
    assert not el.has_attribute("hidden")
    el.hidden = False
    # remove_attribute is a no-op — attribute must still be absent
    assert not el.has_attribute("hidden")


def test_hidden_round_trip(doc: Document) -> None:
    """Set via property, read via get_attribute, then unset."""
    el = doc.create_element("div")
    el.hidden = True
    assert el.get_attribute("hidden") == ""
    el.hidden = False
    assert el.get_attribute("hidden") is None


# ---------------------------------------------------------------------------
# title — AC-3, AC-4
# ---------------------------------------------------------------------------

def test_title_getter_absent(doc: Document) -> None:
    """AC-3: el.title returns '' when 'title' attribute is absent."""
    el = doc.create_element("abbr")
    assert el.title == ""


def test_title_getter_present(doc: Document) -> None:
    """AC-3: el.title returns the attribute value when present."""
    el = doc.create_element("abbr")
    el.set_attribute("title", "World Health Organization")
    assert el.title == "World Health Organization"


def test_title_setter(doc: Document) -> None:
    """AC-4: el.title = 'tip' sets the title attribute."""
    el = doc.create_element("abbr")
    el.title = "tip"
    assert el.get_attribute("title") == "tip"


def test_title_empty_string_setter(doc: Document) -> None:
    """el.title = '' sets title attribute to empty string."""
    el = doc.create_element("div")
    el.title = ""
    # Empty string setter still calls set_attribute, attribute is present
    assert el.get_attribute("title") == ""


def test_title_round_trip(doc: Document) -> None:
    """Set via property, read via get_attribute."""
    el = doc.create_element("span")
    el.title = "My tooltip"
    assert el.get_attribute("title") == "My tooltip"
    assert el.title == "My tooltip"


# ---------------------------------------------------------------------------
# lang — AC-5
# ---------------------------------------------------------------------------

def test_lang_getter_absent(doc: Document) -> None:
    """AC-5: el.lang returns '' when 'lang' attribute is absent."""
    el = doc.create_element("p")
    assert el.lang == ""


def test_lang_getter_present(doc: Document) -> None:
    """AC-5: el.lang returns the attribute value when present."""
    el = doc.create_element("p")
    el.set_attribute("lang", "fr")
    assert el.lang == "fr"


def test_lang_setter(doc: Document) -> None:
    """AC-5: el.lang = 'en' sets the lang attribute."""
    el = doc.create_element("p")
    el.lang = "en"
    assert el.get_attribute("lang") == "en"


def test_lang_empty_string_setter(doc: Document) -> None:
    """el.lang = '' sets lang attribute to empty string."""
    el = doc.create_element("div")
    el.lang = ""
    assert el.get_attribute("lang") == ""


def test_lang_round_trip(doc: Document) -> None:
    """Set via property, read via get_attribute."""
    el = doc.create_element("span")
    el.lang = "de"
    assert el.get_attribute("lang") == "de"
    assert el.lang == "de"


# ---------------------------------------------------------------------------
# tab_index — AC-6, AC-7
# ---------------------------------------------------------------------------

def test_tab_index_getter_absent(doc: Document) -> None:
    """AC-6: el.tab_index returns 0 when 'tabindex' attribute is absent."""
    el = doc.create_element("button")
    assert el.tab_index == 0


def test_tab_index_getter_present(doc: Document) -> None:
    """AC-6: el.tab_index returns integer value of attribute."""
    el = doc.create_element("button")
    el.set_attribute("tabindex", "5")
    assert el.tab_index == 5


def test_tab_index_setter(doc: Document) -> None:
    """AC-7: el.tab_index = 3 sets tabindex='3'."""
    el = doc.create_element("button")
    el.tab_index = 3
    assert el.get_attribute("tabindex") == "3"


def test_tab_index_malformed_attribute(doc: Document) -> None:
    """tabindex='abc' → el.tab_index returns 0 (ValueError caught)."""
    el = doc.create_element("div")
    el.set_attribute("tabindex", "abc")
    assert el.tab_index == 0


def test_tab_index_negative(doc: Document) -> None:
    """el.tab_index = -1 sets tabindex='-1'; getter returns -1."""
    el = doc.create_element("div")
    el.tab_index = -1
    assert el.get_attribute("tabindex") == "-1"
    assert el.tab_index == -1


def test_tab_index_round_trip(doc: Document) -> None:
    """Set via property, read via get_attribute."""
    el = doc.create_element("input")
    el.tab_index = 7
    assert el.get_attribute("tabindex") == "7"
    assert el.tab_index == 7


# ---------------------------------------------------------------------------
# access_key — AC-8
# ---------------------------------------------------------------------------

def test_access_key_getter_absent(doc: Document) -> None:
    """AC-8: el.access_key returns '' when 'accesskey' attribute is absent."""
    el = doc.create_element("a")
    assert el.access_key == ""


def test_access_key_getter_present(doc: Document) -> None:
    """AC-8: el.access_key returns the attribute value when present."""
    el = doc.create_element("a")
    el.set_attribute("accesskey", "k")
    assert el.access_key == "k"


def test_access_key_setter(doc: Document) -> None:
    """AC-8: el.access_key = 'k' sets the accesskey attribute."""
    el = doc.create_element("a")
    el.access_key = "k"
    assert el.get_attribute("accesskey") == "k"


def test_access_key_round_trip(doc: Document) -> None:
    """Set via property, read via get_attribute."""
    el = doc.create_element("button")
    el.access_key = "s"
    assert el.get_attribute("accesskey") == "s"
    assert el.access_key == "s"


# ---------------------------------------------------------------------------
# Inheritance — AC-9
# ---------------------------------------------------------------------------

def test_properties_inherited_by_htmldivelement(doc: Document) -> None:
    """AC-9: HTMLDivElement inherits hidden, title, lang, tab_index, access_key."""
    el = doc.create_element("div")
    assert isinstance(el, HTMLDivElement)
    # All properties accessible without AttributeError
    assert el.hidden is False
    assert el.title == ""
    assert el.lang == ""
    assert el.tab_index == 0
    assert el.access_key == ""


def test_properties_inherited_by_htmlanchorelement(doc: Document) -> None:
    """AC-9: HTMLAnchorElement inherits hidden, title, lang, tab_index, access_key."""
    el = doc.create_element("a")
    assert isinstance(el, HTMLAnchorElement)
    assert el.hidden is False
    assert el.title == ""
    assert el.lang == ""
    assert el.tab_index == 0
    assert el.access_key == ""


def test_all_registered_tags_inherit_global_properties(doc: Document) -> None:
    """AC-9: all registered tag names produce elements with global properties."""
    registered_tags = [
        "a", "button", "div", "form", "h1", "h2", "h3", "h4", "h5", "h6",
        "img", "input", "link", "meta", "p", "script", "select", "span", "title",
    ]
    for tag in registered_tags:
        el = doc.create_element(tag)
        assert isinstance(el, HTMLElement), f"{tag} is not HTMLElement"
        # Verify properties exist and return correct types
        assert isinstance(el.hidden, bool), f"{tag}.hidden not bool"
        assert isinstance(el.title, str), f"{tag}.title not str"
        assert isinstance(el.lang, str), f"{tag}.lang not str"
        assert isinstance(el.tab_index, int), f"{tag}.tab_index not int"
        assert isinstance(el.access_key, str), f"{tag}.access_key not str"


# ---------------------------------------------------------------------------
# Type hints and docstrings — AC-10 ()
# ---------------------------------------------------------------------------

def test_type_hints_and_docstrings() -> None:
    """AC-10: all five properties have docstrings ()."""
    assert HTMLElement.hidden.__doc__ is not None and len(HTMLElement.hidden.__doc__) > 0
    assert HTMLElement.title.__doc__ is not None and len(HTMLElement.title.__doc__) > 0
    assert HTMLElement.lang.__doc__ is not None and len(HTMLElement.lang.__doc__) > 0
    assert HTMLElement.tab_index.__doc__ is not None and len(HTMLElement.tab_index.__doc__) > 0
    assert HTMLElement.access_key.__doc__ is not None and len(HTMLElement.access_key.__doc__) > 0


def test_return_types_correct(doc: Document) -> None:
    """AC-10: getter return values have the correct Python types."""
    el = doc.create_element("div")
    assert type(el.hidden) is bool
    assert type(el.title) is str
    assert type(el.lang) is str
    assert type(el.tab_index) is int
    assert type(el.access_key) is str


# ---------------------------------------------------------------------------
# Slots unchanged — NFR-1
# ---------------------------------------------------------------------------

def test_htmlelement_slots_unchanged(doc: Document) -> None:
    """NFR-1: HTMLElement.__slots__ is still () after adding property descriptors."""
    assert HTMLElement.__slots__ == ()


def test_concrete_subclass_slots_unchanged(doc: Document) -> None:
    """Property descriptors on HTMLElement do not affect subclass slots.

    HTMLDivElement has no slots. HTMLAnchorElement acquired _rel_list_cache
    in  (), so we check it doesn't grow unexpectedly beyond that.
    """
    assert HTMLDivElement.__slots__ == ()
    #  added _rel_list_cache to HTMLAnchorElement for DOMTokenList caching
    assert "_rel_list_cache" in HTMLAnchorElement.__slots__


# ---------------------------------------------------------------------------
#  — content_editable, is_content_editable, dir, draggable,
#             spell_check, translate
# ---------------------------------------------------------------------------

def test_content_editable_default_inherit(doc: Document) -> None:
    """content_editable returns 'inherit' when attribute is absent."""
    el = doc.create_element("div")
    assert el.content_editable == "inherit"


def test_content_editable_setter_valid_values(doc: Document) -> None:
    """content_editable accepts all four valid values."""
    el = doc.create_element("div")
    for val in ("true", "false", "inherit", "plaintext-only"):
        el.content_editable = val
        assert el.get_attribute("contenteditable") == val


def test_content_editable_setter_invalid_raises(doc: Document) -> None:
    """content_editable setter raises SyntaxError for invalid values."""
    from aspose_html.dom._exceptions import SyntaxError as _SyntaxError
    el = doc.create_element("div")
    with pytest.raises(_SyntaxError):
        el.content_editable = "yes"


def test_is_content_editable_default_false(doc: Document) -> None:
    """is_content_editable is False when contenteditable attribute is absent."""
    el = doc.create_element("div")
    assert el.is_content_editable is False


def test_is_content_editable_true_when_set(doc: Document) -> None:
    """is_content_editable is True only when contenteditable == 'true'."""
    el = doc.create_element("div")
    el.content_editable = "true"
    assert el.is_content_editable is True
    el.content_editable = "false"
    assert el.is_content_editable is False
    el.content_editable = "inherit"
    assert el.is_content_editable is False


def test_is_content_editable_read_only(doc: Document) -> None:
    """is_content_editable raises AttributeError on assignment."""
    el = doc.create_element("div")
    with pytest.raises(AttributeError):
        el.is_content_editable = True  # type: ignore[misc]


def test_dir_default_empty_string(doc: Document) -> None:
    """dir returns '' when dir attribute is absent."""
    el = doc.create_element("p")
    assert el.dir == ""


def test_dir_setter_round_trip(doc: Document) -> None:
    """dir setter writes the attribute; getter reads it back."""
    el = doc.create_element("p")
    el.dir = "rtl"
    assert el.dir == "rtl"
    assert el.get_attribute("dir") == "rtl"


def test_draggable_default_false(doc: Document) -> None:
    """draggable returns False when attribute is absent."""
    el = doc.create_element("img")
    assert el.draggable is False


def test_draggable_setter_true(doc: Document) -> None:
    """draggable = True writes 'true' to attribute."""
    el = doc.create_element("img")
    el.draggable = True
    assert el.draggable is True
    assert el.get_attribute("draggable") == "true"


def test_draggable_setter_false(doc: Document) -> None:
    """draggable = False writes 'false' to attribute."""
    el = doc.create_element("img")
    el.draggable = True
    el.draggable = False
    assert el.draggable is False
    assert el.get_attribute("draggable") == "false"


def test_spell_check_default_true(doc: Document) -> None:
    """spell_check returns True when spellcheck attribute is absent."""
    el = doc.create_element("textarea")
    assert el.spell_check is True


def test_spell_check_false_when_attribute_false(doc: Document) -> None:
    """spell_check returns False only when attribute value is 'false'."""
    el = doc.create_element("textarea")
    el.set_attribute("spellcheck", "false")
    assert el.spell_check is False


def test_spell_check_setter_round_trip(doc: Document) -> None:
    """spell_check setter writes correct string to attribute."""
    el = doc.create_element("textarea")
    el.spell_check = False
    assert el.get_attribute("spellcheck") == "false"
    el.spell_check = True
    assert el.get_attribute("spellcheck") == "true"


def test_translate_default_true(doc: Document) -> None:
    """translate returns True when attribute is absent."""
    el = doc.create_element("p")
    assert el.translate is True


def test_translate_false_when_no(doc: Document) -> None:
    """translate returns False when attribute value is 'no' (case-insensitive)."""
    el = doc.create_element("p")
    el.set_attribute("translate", "no")
    assert el.translate is False
    el.set_attribute("translate", "NO")
    assert el.translate is False


def test_translate_setter_round_trip(doc: Document) -> None:
    """translate setter writes 'yes'/'no' to attribute."""
    el = doc.create_element("p")
    el.translate = False
    assert el.get_attribute("translate") == "no"
    el.translate = True
    assert el.get_attribute("translate") == "yes"


def test_group_d_properties_inherited_by_subclass(doc: Document) -> None:
    """All six Group D properties are accessible on a concrete subclass."""
    el = doc.create_element("div")
    assert el.content_editable == "inherit"
    assert el.is_content_editable is False
    assert el.dir == ""
    assert el.draggable is False
    assert el.spell_check is True
    assert el.translate is True


# ---------------------------------------------------------------------------
#  — inner_text / outer_text (,  Group E)
# ---------------------------------------------------------------------------

# inner_text getter — AC-1

def test_inner_text_collapses_whitespace(doc: Document) -> None:
    """AC-1: inner_text collapses consecutive whitespace to a single space."""
    div = doc.create_element("div")
    div.inner_html = "<p>Hello   world</p><p>  end  </p>"
    assert div.inner_text == "Hello world end"


def test_inner_text_strips_leading_trailing(doc: Document) -> None:
    """AC-1: inner_text strips leading/trailing whitespace after collapsing."""
    div = doc.create_element("div")
    div.inner_html = "  <span>  hello  </span>  "
    assert div.inner_text == "hello"


def test_inner_text_empty_element(doc: Document) -> None:
    """AC-1: inner_text returns '' for an element with no children."""
    div = doc.create_element("div")
    assert div.inner_text == ""


def test_inner_text_single_text_node(doc: Document) -> None:
    """AC-1: inner_text on a plain text child returns collapsed text."""
    div = doc.create_element("div")
    div.inner_html = "Hello\n\tWorld"
    assert div.inner_text == "Hello World"


def test_inner_text_detached_element(doc: Document) -> None:
    """AC-1: inner_text works on a detached element (no parent)."""
    span = doc.create_element("span")
    span.inner_html = "  hello  "
    assert span.inner_text == "hello"


# inner_text setter — AC-2

def test_inner_text_setter_replaces_children(doc: Document) -> None:
    """AC-2: inner_text setter removes all children and inserts a Text node."""
    div = doc.create_element("div")
    _ = doc.append_child(div)
    div.inner_html = "<b>old</b><i>content</i>"
    assert len(div.child_nodes) == 2
    div.inner_text = "new text"
    assert len(div.child_nodes) == 1
    assert div.inner_html == "new text"


def test_inner_text_setter_empty_string_removes_children(doc: Document) -> None:
    """AC-2: setting inner_text to '' removes all children, inserts nothing."""
    div = doc.create_element("div")
    _ = doc.append_child(div)
    div.inner_html = "<p>content</p>"
    div.inner_text = ""
    assert len(div.child_nodes) == 0
    assert div.inner_html == ""


def test_inner_text_setter_uses_dom_primitives(doc: Document) -> None:
    """AC-2: inner_text setter result is readable via text_content."""
    div = doc.create_element("div")
    _ = doc.append_child(div)
    div.inner_text = "hello world"
    assert div.text_content == "hello world"
    assert div.inner_text == "hello world"


def test_inner_text_setter_replaces_mixed_children(doc: Document) -> None:
    """AC-2: setter removes element children and text node children alike."""
    div = doc.create_element("div")
    _ = doc.append_child(div)
    div.append_child(doc.create_text_node("first"))
    span = doc.create_element("span")
    div.append_child(span)
    assert len(div.child_nodes) == 2
    div.inner_text = "replaced"
    assert len(div.child_nodes) == 1
    assert div.inner_text == "replaced"


# outer_text getter — AC-3

def test_outer_text_mirrors_inner_text(doc: Document) -> None:
    """AC-3: outer_text getter returns the same value as inner_text."""
    span = doc.create_element("span")
    span.inner_html = "Hello   World"
    assert span.outer_text == span.inner_text
    assert span.outer_text == "Hello World"


def test_outer_text_empty_element(doc: Document) -> None:
    """AC-3: outer_text returns '' for an empty element."""
    span = doc.create_element("span")
    assert span.outer_text == ""
    assert span.outer_text == span.inner_text


# outer_text setter — AC-4

def test_outer_text_setter_replaces_in_parent(doc: Document) -> None:
    """AC-4: outer_text setter replaces the element in its parent with a Text node."""
    parent = doc.create_element("div")
    span = doc.create_element("span")
    _ = doc.append_child(parent)
    _ = parent.append_child(span)
    span.outer_text = "replaced"
    # span is removed; parent now contains only the Text node
    assert parent.inner_html == "replaced"
    assert span.parent_node is None


def test_outer_text_setter_text_node_inserted_at_correct_position(doc: Document) -> None:
    """AC-4: outer_text replacement preserves sibling order."""
    parent = doc.create_element("div")
    before = doc.create_element("b")
    target = doc.create_element("span")
    after = doc.create_element("em")
    _ = doc.append_child(parent)
    _ = parent.append_child(before)
    _ = parent.append_child(target)
    _ = parent.append_child(after)
    target.outer_text = "middle"
    # parent should now have: <b>, text "middle", <em>
    children = list(parent.child_nodes)
    assert len(children) == 3
    assert children[0].node_name == "B"
    assert children[1].node_type == 3  # TEXT_NODE
    assert children[1]._data == "middle"  # type: ignore[attr-defined]
    assert children[2].node_name == "EM"


def test_outer_text_setter_detached_raises(doc: Document) -> None:
    """AC-4: outer_text setter raises NoModificationAllowedError when detached."""
    from aspose_html.dom._exceptions import NoModificationAllowedError
    span = doc.create_element("span")
    # span has no parent — must raise
    with pytest.raises(NoModificationAllowedError):
        span.outer_text = "should fail"


def test_outer_text_setter_empty_string(doc: Document) -> None:
    """AC-4: outer_text = '' inserts an empty Text node and removes element."""
    parent = doc.create_element("div")
    span = doc.create_element("span")
    _ = doc.append_child(parent)
    _ = parent.append_child(span)
    span.outer_text = ""
    # Element removed; Text node with empty string inserted
    assert span.parent_node is None
    children = list(parent.child_nodes)
    assert len(children) == 1
    assert children[0].node_type == 3  # TEXT_NODE


# Type hints and docstrings — AC-5

def test_inner_text_outer_text_have_docstrings() -> None:
    """AC-5: both properties have non-empty docstrings ()."""
    assert HTMLElement.inner_text.__doc__ is not None
    assert len(HTMLElement.inner_text.__doc__) > 0
    assert HTMLElement.outer_text.__doc__ is not None
    assert len(HTMLElement.outer_text.__doc__) > 0


def test_inner_text_return_type(doc: Document) -> None:
    """AC-5: inner_text getter always returns str, never None."""
    el = doc.create_element("div")
    result = el.inner_text
    assert type(result) is str


def test_outer_text_return_type(doc: Document) -> None:
    """AC-5: outer_text getter always returns str, never None."""
    el = doc.create_element("span")
    result = el.outer_text
    assert type(result) is str


# ---------------------------------------------------------------------------
#  — click(), focus(), blur() (,  Group F)
# ---------------------------------------------------------------------------

def test_click_dispatches_event(doc: Document) -> None:
    """AC-1: click() fires the registered listener once."""
    btn = doc.create_element("button")
    _ = doc.append_child(btn)
    clicked: list[bool] = []
    btn.add_event_listener("click", lambda e: clicked.append(True))
    btn.click()
    assert clicked == [True]


def test_click_event_type_and_bubbles(doc: Document) -> None:
    """AC-1: click() dispatches an event with type='click', bubbles=True, cancelable=True."""
    from aspose_html.dom._event import Event as _Event
    btn = doc.create_element("button")
    _ = doc.append_child(btn)
    received: list[_Event] = []
    btn.add_event_listener("click", lambda e: received.append(e))
    btn.click()
    assert len(received) == 1
    evt = received[0]
    assert evt.type == "click"
    assert evt.bubbles is True
    assert evt.cancelable is True


def test_focus_dispatches_non_bubbling_event(doc: Document) -> None:
    """AC-2: focus() dispatches an event with type='focus', bubbles=False."""
    from aspose_html.dom._event import Event as _Event
    inp = doc.create_element("input")
    _ = doc.append_child(inp)
    received: list[_Event] = []
    inp.add_event_listener("focus", lambda e: received.append(e))
    inp.focus()
    assert len(received) == 1
    evt = received[0]
    assert evt.type == "focus"
    assert evt.bubbles is False


def test_blur_dispatches_non_bubbling_event(doc: Document) -> None:
    """AC-3: blur() dispatches an event with type='blur', bubbles=False."""
    from aspose_html.dom._event import Event as _Event
    inp = doc.create_element("input")
    _ = doc.append_child(inp)
    received: list[_Event] = []
    inp.add_event_listener("blur", lambda e: received.append(e))
    inp.blur()
    assert len(received) == 1
    evt = received[0]
    assert evt.type == "blur"
    assert evt.bubbles is False


def test_focus_accepts_options_dict_without_raising(doc: Document) -> None:
    """AC-4: focus(options={...}) must not raise."""
    inp = doc.create_element("input")
    _ = doc.append_child(inp)
    inp.focus(options={"preventScroll": True})  # must not raise


def test_focus_accepts_none_options_without_raising(doc: Document) -> None:
    """AC-4: focus(options=None) must not raise (default)."""
    inp = doc.create_element("input")
    _ = doc.append_child(inp)
    inp.focus(options=None)  # must not raise


def test_click_does_not_raise_when_no_listeners(doc: Document) -> None:
    """AC-1: click() on element with no registered listeners must not raise."""
    el = doc.create_element("div")
    _ = doc.append_child(el)
    el.click()  # must not raise


def test_focus_does_not_raise_when_no_listeners(doc: Document) -> None:
    """AC-2: focus() on element with no registered listeners must not raise."""
    el = doc.create_element("div")
    _ = doc.append_child(el)
    el.focus()  # must not raise


def test_blur_does_not_raise_when_no_listeners(doc: Document) -> None:
    """AC-3: blur() on element with no registered listeners must not raise."""
    el = doc.create_element("div")
    _ = doc.append_child(el)
    el.blur()  # must not raise


def test_click_bubbles_to_parent(doc: Document) -> None:
    """AC-1: click event bubbles — parent listener fires via bubble."""
    parent = doc.create_element("div")
    child = doc.create_element("span")
    _ = doc.append_child(parent)
    _ = parent.append_child(child)
    parent_received: list[str] = []
    parent.add_event_listener("click", lambda e: parent_received.append(e.type))
    child.click()
    assert parent_received == ["click"]


def test_focus_does_not_bubble_to_parent(doc: Document) -> None:
    """AC-2: focus event does not bubble — parent listener must NOT fire."""
    parent = doc.create_element("div")
    child = doc.create_element("input")
    _ = doc.append_child(parent)
    _ = parent.append_child(child)
    parent_received: list[str] = []
    parent.add_event_listener("focus", lambda e: parent_received.append(e.type))
    child.focus()
    assert parent_received == []


def test_blur_does_not_bubble_to_parent(doc: Document) -> None:
    """AC-3: blur event does not bubble — parent listener must NOT fire."""
    parent = doc.create_element("div")
    child = doc.create_element("input")
    _ = doc.append_child(parent)
    _ = parent.append_child(child)
    parent_received: list[str] = []
    parent.add_event_listener("blur", lambda e: parent_received.append(e.type))
    child.blur()
    assert parent_received == []


def test_interaction_methods_have_docstrings() -> None:
    """AC-5 / : click, focus, blur all have non-empty docstrings."""
    assert HTMLElement.click.__doc__ is not None and len(HTMLElement.click.__doc__) > 0
    assert HTMLElement.focus.__doc__ is not None and len(HTMLElement.focus.__doc__) > 0
    assert HTMLElement.blur.__doc__ is not None and len(HTMLElement.blur.__doc__) > 0


def test_interaction_methods_return_none(doc: Document) -> None:
    """AC-5: click(), focus(), blur() all return None."""
    el = doc.create_element("button")
    _ = doc.append_child(el)
    assert el.click() is None
    assert el.focus() is None
    assert el.blur() is None


# ---------------------------------------------------------------------------
#  — Group G cross-group integration tests ()
# Verify that Groups A–F compose correctly without breaking each other.
# ---------------------------------------------------------------------------

def test_click_fires_on_button_with_listener(doc: Document) -> None:
    """Group F: click() dispatches event to add_event_listener handler (AC-3)."""
    btn = doc.create_element("button")
    _ = doc.append_child(btn)
    received: list[str] = []
    btn.add_event_listener("click", lambda e: received.append(e.type))
    btn.click()
    assert received == ["click"]


def test_outer_text_setter_visible_via_inner_html(doc: Document) -> None:
    """Group E + DOM: outer_text setter tree mutation is reflected in inner_html (AC-4)."""
    parent = doc.create_element("div")
    span = doc.create_element("span")
    span.inner_html = "<b>old</b>"
    _ = doc.append_child(parent)
    _ = parent.append_child(span)
    # outer_text replaces <span> in parent with a text node
    span.outer_text = "new text"
    # span is detached; parent's inner_html reflects the replacement
    assert span.parent_node is None
    assert "new text" in parent.inner_html
    assert "<span>" not in parent.inner_html


def test_inner_text_setter_then_click_event(doc: Document) -> None:
    """Group E + F: after inner_text mutation, click() still dispatches correctly."""
    btn = doc.create_element("button")
    _ = doc.append_child(btn)
    btn.inner_text = "click me"
    received: list[str] = []
    btn.add_event_listener("click", lambda e: received.append(e.type))
    btn.click()
    assert received == ["click"]
    # Verify inner_text mutation did not corrupt the element's event listener state
    assert btn.inner_text == "click me"


def test_content_editable_roundtrip_with_event(doc: Document) -> None:
    """Group D + F: set content_editable, add click listener, click(), verify."""
    div = doc.create_element("div")
    _ = doc.append_child(div)
    div.content_editable = "true"
    assert div.is_content_editable is True
    fired: list[bool] = []
    div.add_event_listener("click", lambda e: fired.append(True))
    div.click()
    assert fired == [True]
    # content_editable state unaffected by click dispatch
    assert div.content_editable == "true"
    assert div.is_content_editable is True


def test_focus_blur_non_bubbling(doc: Document) -> None:
    """Group F: focus/blur events do not bubble — parent listener does not fire (AC-5)."""
    parent = doc.create_element("div")
    child = doc.create_element("input")
    _ = doc.append_child(parent)
    _ = parent.append_child(child)
    parent_focus: list[str] = []
    parent_blur: list[str] = []
    parent.add_event_listener("focus", lambda e: parent_focus.append(e.type))
    parent.add_event_listener("blur", lambda e: parent_blur.append(e.type))
    child.focus()
    child.blur()
    # focus and blur must NOT bubble to parent
    assert parent_focus == []
    assert parent_blur == []
