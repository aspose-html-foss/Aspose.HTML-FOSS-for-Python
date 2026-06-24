"""Integration tests for aspose_html.css.select() (AC-P25 and ).

These tests require  (_matcher.py) to be implemented.
Tests added in  are marked with pytest.mark.integration.

AC-P25: select() has type hints and docstring with runnable example.
        Importing aspose_html.css must succeed without _matcher.py.
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, Element


# ---------------------------------------------------------------------------
# Fixture helper
# ---------------------------------------------------------------------------


def _make_doc() -> Document:
    """Build a small DOM tree for testing.

    Structure:
      Document
        HTML
          HEAD
          BODY
            H1 #title
            P.intro
            UL
              LI (first)
              LI.active (second)
              LI (third)
            A[href="https://example.com"]
    """
    doc = Document()
    html = doc.create_element("html")
    head = doc.create_element("head")
    body = doc.create_element("body")

    h1 = doc.create_element("h1")
    h1.set_attribute("id", "title")

    p = doc.create_element("p")
    p.set_attribute("class", "intro")

    ul = doc.create_element("ul")

    li1 = doc.create_element("li")
    li2 = doc.create_element("li")
    li2.set_attribute("class", "active")
    li3 = doc.create_element("li")

    a = doc.create_element("a")
    a.set_attribute("href", "https://example.com")

    doc.append_child(html)
    html.append_child(head)
    html.append_child(body)
    body.append_child(h1)
    body.append_child(p)
    body.append_child(ul)
    ul.append_child(li1)
    ul.append_child(li2)
    ul.append_child(li3)
    body.append_child(a)

    return doc


# ---------------------------------------------------------------------------
# Pre- test (no _matcher.py required)
# ---------------------------------------------------------------------------


def test_css_import_does_not_fail_without_matcher() -> None:
    """AC-P25 (no-matcher): importing aspose_html.css does not raise ImportError.

    The ImportError from missing _matcher must surface lazily (only when
    select() is actually called), not at import time.
    """
    import aspose_html.css  # noqa: F401
    from aspose_html.css import select  # noqa: F401 — function object must be importable


# ---------------------------------------------------------------------------
# Docstring example test (requires )
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_docstring_example() -> None:
    """AC-P25: The doctest in select() passes (requires )."""
    import doctest
    import aspose_html.css
    results = doctest.testmod(aspose_html.css, verbose=False, optionflags=doctest.SKIP)
    assert results.failed == 0


# ---------------------------------------------------------------------------
# Type selector and universal selector (AC-1)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_type_selector() -> None:
    """AC-1: div matches all div elements."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li")
    assert len(result) == 3
    assert all(el.local_name == "li" for el in result)


@pytest.mark.integration
def test_select_universal_selector() -> None:
    """* matches all elements in the subtree."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "*")
    # html, head, body, h1, p, ul, li x3, a = 10 elements
    assert len(result) == 10


@pytest.mark.integration
def test_select_case_insensitive_tag() -> None:
    """AC-8: Tag names in selectors are case-insensitive (DIV == div)."""
    from aspose_html.css import select
    doc = _make_doc()
    # Parser normalises to lowercase; element.local_name is lowercase.
    result_lower = select(doc, "ul")
    result_upper = select(doc, "UL")
    assert len(result_lower) == 1
    assert result_lower == result_upper


# ---------------------------------------------------------------------------
# Class selector (AC-2)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_class_selector() -> None:
    """AC-2: .intro matches element with class 'intro'."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, ".intro")
    assert len(result) == 1
    assert result[0].local_name == "p"


@pytest.mark.integration
def test_select_compound_class() -> None:
    """.foo.bar matches element that has both classes."""
    from aspose_html.css import select
    doc = Document()
    el = doc.create_element("div")
    el.set_attribute("class", "foo bar")
    doc.append_child(el)
    assert select(doc, ".foo.bar") == [el]
    assert select(doc, ".foo.baz") == []


# ---------------------------------------------------------------------------
# ID selector
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_id_selector() -> None:
    """#title matches element with id='title'."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "#title")
    assert len(result) == 1
    assert result[0].local_name == "h1"


# ---------------------------------------------------------------------------
# Attribute selectors (AC-6, AC-7)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_attribute_exists() -> None:
    """[href] matches elements that have the href attribute."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "[href]")
    assert len(result) == 1
    assert result[0].local_name == "a"


@pytest.mark.integration
def test_select_attribute_equals() -> None:
    """[type=text] matches elements with exact attribute value."""
    from aspose_html.css import select
    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)
    inp = doc.create_element("input")
    inp.set_attribute("type", "text")
    inp2 = doc.create_element("input")
    inp2.set_attribute("type", "checkbox")
    body.append_child(inp)
    body.append_child(inp2)
    result = select(doc, '[type="text"]')
    assert result == [inp]


@pytest.mark.integration
def test_select_attribute_word() -> None:
    """AC-7: [class~='active'] matches element whose class list contains 'active'."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, '[class~="active"]')
    assert len(result) == 1
    assert result[0].local_name == "li"


@pytest.mark.integration
def test_select_attribute_dashmatch() -> None:
    """AC-6: [lang|='en'] matches 'en' or 'en-*'."""
    from aspose_html.css import select
    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)
    el1 = doc.create_element("p")
    el1.set_attribute("lang", "en")
    el2 = doc.create_element("p")
    el2.set_attribute("lang", "en-US")
    el3 = doc.create_element("p")
    el3.set_attribute("lang", "fr")
    body.append_child(el1)
    body.append_child(el2)
    body.append_child(el3)
    result = select(doc, "[lang|=en]")
    assert result == [el1, el2]


@pytest.mark.integration
def test_select_attribute_prefix() -> None:
    """AC-6: [href^='https'] matches href starting with 'https'."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "[href^='https']")
    assert len(result) == 1
    assert result[0].local_name == "a"


@pytest.mark.integration
def test_select_attribute_suffix() -> None:
    """[href$='.pdf'] matches href ending with '.pdf'."""
    from aspose_html.css import select
    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)
    a = doc.create_element("a")
    a.set_attribute("href", "doc.pdf")
    b = doc.create_element("a")
    b.set_attribute("href", "doc.html")
    body.append_child(a)
    body.append_child(b)
    result = select(doc, "[href$='.pdf']")
    assert result == [a]


@pytest.mark.integration
def test_select_attribute_substring() -> None:
    """[href*='example'] matches href containing 'example'."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "[href*='example']")
    assert len(result) == 1


@pytest.mark.integration
def test_select_attribute_case_insensitive() -> None:
    """[attr=Val i] matches regardless of value case."""
    from aspose_html.css import select
    doc = Document()
    el = doc.create_element("input")
    el.set_attribute("type", "TEXT")
    doc.append_child(el)
    result = select(doc, "[type=text i]")
    assert result == [el]


# ---------------------------------------------------------------------------
# Combinator tests (AC-3, AC-4)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_descendant_combinator() -> None:
    """div span matches span anywhere inside div."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "body li")
    assert len(result) == 3


@pytest.mark.integration
def test_select_child_combinator() -> None:
    """AC-3: ul > li matches only direct li children of ul."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "ul > li")
    assert len(result) == 3
    # body > li should return nothing (li is not a direct child of body)
    assert select(doc, "body > li") == []


@pytest.mark.integration
def test_select_adjacent_combinator() -> None:
    """AC-4: h1 + p matches p immediately following h1."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "h1 + p")
    assert len(result) == 1
    assert result[0].local_name == "p"


@pytest.mark.integration
def test_select_sibling_combinator() -> None:
    """h1 ~ p matches any p following h1 as sibling."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "h1 ~ ul")
    assert len(result) == 1
    assert result[0].local_name == "ul"


# ---------------------------------------------------------------------------
# Pseudo-classes
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_first_child() -> None:
    """:first-child matches first element child."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li:first-child")
    assert len(result) == 1
    assert len(result[0].class_list) == 0


@pytest.mark.integration
def test_select_last_child() -> None:
    """:last-child matches last element child."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li:last-child")
    assert len(result) == 1
    assert len(result[0].class_list) == 0  # third li has no class


@pytest.mark.integration
def test_select_only_child() -> None:
    """:only-child matches element that is the sole element child."""
    from aspose_html.css import select
    doc = Document()
    parent = doc.create_element("div")
    child = doc.create_element("span")
    doc.append_child(parent)
    parent.append_child(child)
    result = select(doc, "span:only-child")
    assert result == [child]
    # Add a sibling; now neither is only-child
    sibling = doc.create_element("span")
    parent.append_child(sibling)
    assert select(doc, "span:only-child") == []


@pytest.mark.integration
def test_select_nth_child() -> None:
    """AC-5: :nth-child(2n+1) matches odd-positioned children."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li:nth-child(2n+1)")
    # li positions are 1,2,3; odd = 1,3
    assert len(result) == 2


@pytest.mark.integration
def test_select_nth_child_even_odd() -> None:
    """:nth-child(even) and :nth-child(odd) work correctly."""
    from aspose_html.css import select
    doc = _make_doc()
    odd = select(doc, "li:nth-child(odd)")
    even = select(doc, "li:nth-child(even)")
    assert len(odd) == 2
    assert len(even) == 1


@pytest.mark.integration
def test_select_nth_last_child() -> None:
    """:nth-last-child(1) matches the last child."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li:nth-last-child(1)")
    assert len(result) == 1
    assert result[0] is select(doc, "li:last-child")[0]


@pytest.mark.integration
def test_select_first_of_type() -> None:
    """:first-of-type matches first element of its type among siblings."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li:first-of-type")
    assert len(result) == 1


@pytest.mark.integration
def test_select_last_of_type() -> None:
    """:last-of-type matches last element of its type among siblings."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li:last-of-type")
    assert len(result) == 1


@pytest.mark.integration
def test_select_only_of_type() -> None:
    """:only-of-type matches when element is the only one of its tag."""
    from aspose_html.css import select
    doc = _make_doc()
    # ul is the only ul among body's children
    result = select(doc, "ul:only-of-type")
    assert len(result) == 1


@pytest.mark.integration
def test_select_nth_of_type() -> None:
    """:nth-of-type(2n) matches even-positioned elements of their type."""
    from aspose_html.css import select
    doc = _make_doc()
    # 3 li's; :nth-of-type(2n) = position 2 only
    result = select(doc, "li:nth-of-type(2n)")
    assert len(result) == 1


@pytest.mark.integration
def test_select_nth_last_of_type() -> None:
    """:nth-last-of-type(1) matches the last element of its type."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li:nth-last-of-type(1)")
    assert len(result) == 1


@pytest.mark.integration
def test_select_root() -> None:
    """:root matches the root element (no parent element)."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, ":root")
    assert len(result) == 1
    assert result[0].local_name == "html"
    # html has no parent element (parent is Document)
    assert result[0].parent_element is None


@pytest.mark.integration
def test_select_empty() -> None:
    """:empty matches elements with no children at all."""
    from aspose_html.css import select
    doc = _make_doc()
    # head has no children in our fixture
    result = select(doc, "head:empty")
    assert len(result) == 1
    assert result[0].local_name == "head"


@pytest.mark.integration
def test_select_not_pseudo_class() -> None:
    """AC-11: :not(p) matches all elements that are not p."""
    from aspose_html.css import select
    doc = _make_doc()
    all_elements = select(doc, "*")
    not_p = select(doc, ":not(p)")
    p_elements = select(doc, "p")
    assert len(not_p) == len(all_elements) - len(p_elements)


@pytest.mark.integration
def test_select_link() -> None:
    """:link and :any-link match <a href> elements."""
    from aspose_html.css import select
    doc = _make_doc()
    assert len(select(doc, ":link")) == 1
    assert len(select(doc, ":any-link")) == 1
    assert select(doc, ":link") == select(doc, ":any-link")


@pytest.mark.integration
def test_select_visited_never_matches() -> None:
    """:visited never matches (no browsing history in non-browser context)."""
    from aspose_html.css import select
    doc = _make_doc()
    assert select(doc, ":visited") == []


@pytest.mark.integration
def test_select_lang() -> None:
    """:lang(en) matches element with effective language 'en' or 'en-*'."""
    from aspose_html.css import select
    doc = Document()
    div = doc.create_element("div")
    div.set_attribute("lang", "en-US")
    span = doc.create_element("span")
    doc.append_child(div)
    div.append_child(span)
    # span inherits lang from div ancestor
    result = select(doc, "span:lang(en)")
    assert result == [span]
    # exact match also works
    result2 = select(doc, "div:lang(en-US)")
    assert result2 == [div]


# ---------------------------------------------------------------------------
# Selector list (comma)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_selector_list() -> None:
    """"div, span" matches both types."""
    from aspose_html.css import select
    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)
    d = doc.create_element("div")
    s = doc.create_element("span")
    p = doc.create_element("p")
    body.append_child(d)
    body.append_child(s)
    body.append_child(p)
    result = select(doc, "div, span")
    assert set(result) == {d, s}


# ---------------------------------------------------------------------------
# first_only flag
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_first_only() -> None:
    """match() with first_only=True returns at most one element."""
    from aspose_html.css import select
    doc = _make_doc()
    result = select(doc, "li", first_only=True)
    assert len(result) == 1
    assert result[0].local_name == "li"


# ---------------------------------------------------------------------------
# Empty result
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_empty_result() -> None:
    """No match returns an empty list."""
    from aspose_html.css import select
    doc = _make_doc()
    assert select(doc, "table") == []


# ---------------------------------------------------------------------------
# Syntax error (AC-9)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_syntax_error() -> None:
    """AC-9: completely unparseable selector raises SyntaxError."""
    from aspose_html.css import select
    doc = _make_doc()
    with pytest.raises(SyntaxError):
        select(doc, "!!invalid!!", first_only=True)


# ---------------------------------------------------------------------------
# Dynamic pseudo-classes / form-state pseudo-classes
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_checked_matches_checked_inputs_and_selected_options() -> None:
    """: :checked matches checked inputs and selected options."""
    from aspose_html.css import select

    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)

    checked_input = doc.create_element("input")
    checked_input.set_attribute("type", "checkbox")
    checked_input.checked = True
    body.append_child(checked_input)

    unchecked_input = doc.create_element("input")
    unchecked_input.set_attribute("type", "radio")
    unchecked_input.checked = False
    body.append_child(unchecked_input)

    select_el = doc.create_element("select")
    opt_selected = doc.create_element("option")
    opt_selected.selected = True
    opt_unselected = doc.create_element("option")
    select_el.append_child(opt_selected)
    select_el.append_child(opt_unselected)
    body.append_child(select_el)

    div = doc.create_element("div")
    div.set_attribute("checked", "")
    body.append_child(div)

    assert select(doc, ":checked") == [checked_input, opt_selected]


@pytest.mark.integration
def test_select_disabled_enabled_supported_controls() -> None:
    """: :disabled/:enabled partition supported controls deterministically."""
    from aspose_html.css import select

    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)

    input_disabled = doc.create_element("input")
    input_disabled.set_attribute("disabled", "")
    body.append_child(input_disabled)

    input_enabled = doc.create_element("input")
    body.append_child(input_enabled)

    button_disabled = doc.create_element("button")
    button_disabled.set_attribute("disabled", "")
    body.append_child(button_disabled)

    textarea_enabled = doc.create_element("textarea")
    body.append_child(textarea_enabled)

    disabled_results = select(doc, ":disabled")
    enabled_results = select(doc, ":enabled")

    assert disabled_results == [input_disabled, button_disabled]
    assert enabled_results == [input_enabled, textarea_enabled]


@pytest.mark.integration
def test_select_enabled_disabled_non_form_elements_do_not_match() -> None:
    """: non-supported elements never match :enabled or :disabled."""
    from aspose_html.css import select

    doc = Document()
    body = doc.create_element("body")
    div = doc.create_element("div")
    div.set_attribute("disabled", "")
    span = doc.create_element("span")
    doc.append_child(body)
    body.append_child(div)
    body.append_child(span)

    assert select(doc, ":disabled") == []
    assert select(doc, ":enabled") == []


@pytest.mark.integration
def test_select_target_matches_only_fragment_id() -> None:
    """: :target matches only the id named by document URL fragment."""
    from aspose_html.css import select

    doc = Document()
    doc._url = "https://example.com/page#foo"
    body = doc.create_element("body")
    doc.append_child(body)

    target = doc.create_element("div")
    target.set_attribute("id", "foo")
    other = doc.create_element("div")
    other.set_attribute("id", "bar")
    no_id = doc.create_element("div")

    body.append_child(target)
    body.append_child(other)
    body.append_child(no_id)

    assert select(doc, ":target") == [target]


@pytest.mark.integration
def test_select_target_without_fragment_matches_nothing() -> None:
    """: documents with no fragment produce no :target matches."""
    from aspose_html.css import select

    doc = Document()
    doc._url = "https://example.com/page"
    body = doc.create_element("body")
    doc.append_child(body)

    el = doc.create_element("div")
    el.set_attribute("id", "foo")
    body.append_child(el)

    assert select(doc, ":target") == []


# ---------------------------------------------------------------------------
# Nth formula edge cases
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_select_nth_formula_edge_cases() -> None:
    """a=0, b=3 matches index 3 only; a=-1 never matches for large lists."""
    from aspose_html.css._matcher import _matches_nth

    # a=0, b=3: exactly index 3
    assert _matches_nth(0, 3, 3) is True
    assert _matches_nth(0, 3, 1) is False
    assert _matches_nth(0, 3, 4) is False

    # a=2, b=1: odd indices (1, 3, 5, ...)
    assert _matches_nth(2, 1, 1) is True
    assert _matches_nth(2, 1, 2) is False
    assert _matches_nth(2, 1, 3) is True

    # a=-1, b=3: indices <= 3 (3, 2, 1)
    assert _matches_nth(-1, 3, 3) is True
    assert _matches_nth(-1, 3, 2) is True
    assert _matches_nth(-1, 3, 1) is True
    assert _matches_nth(-1, 3, 4) is False  # n=-1 < 0


# ---------------------------------------------------------------------------
#  /  — integration tests for form pseudo-classes
# ---------------------------------------------------------------------------


def _make_track85_form_doc() -> Document:
    """Build a realistic form document for  integration tests.

    Structure::

        Document
          form
            input[type=text required value=""]         #req-empty   → :invalid :required :blank
            input[type=text required value="filled"]   #req-filled  → :valid :required
            input[type=text value=""]                  #opt-empty   → :valid :optional :blank
            input[type=text placeholder="hint" value=""] #ph-shown  → :placeholder-shown
            input[type=submit]                         #submit      → :default
            input[type=checkbox]                       #checkbox    → :read-only (non-editable type)
            input[type=text readonly value="locked"]   #ro-text     → :read-only
            textarea                                   #textarea    → :read-write :blank
    """
    doc = Document()
    form = doc.create_element("form")
    doc.append_child(form)

    def make_input(**attrs: str) -> Element:
        el = doc.create_element("input")
        for k, v in attrs.items():
            el.set_attribute(k, v)
        form.append_child(el)
        return el

    make_input(id="req-empty", type="text", required="", value="")
    make_input(id="req-filled", type="text", required="", value="filled")
    make_input(id="opt-empty", type="text", value="")
    make_input(id="ph-shown", type="text", placeholder="hint", value="")
    make_input(id="submit", type="submit")
    make_input(id="checkbox", type="checkbox")
    make_input(id="ro-text", type="text", readonly="", value="locked")

    ta = doc.create_element("textarea")
    ta.set_attribute("id", "textarea")
    form.append_child(ta)

    return doc


@pytest.mark.integration
def test_track85_integration_invalid_required_blank() -> None:
    """: input[required value=''] is :invalid, :required, and :blank."""
    from aspose_html.css import select

    doc = _make_track85_form_doc()
    invalid_els = select(doc, "input:invalid")
    invalid_ids = {el.get_attribute("id") for el in invalid_els}
    assert "req-empty" in invalid_ids
    assert "req-filled" not in invalid_ids

    required_els = select(doc, "input:required")
    required_ids = {el.get_attribute("id") for el in required_els}
    assert "req-empty" in required_ids
    assert "req-filled" in required_ids
    assert "opt-empty" not in required_ids

    blank_els = select(doc, "input:blank")
    blank_ids = {el.get_attribute("id") for el in blank_els}
    assert "req-empty" in blank_ids
    assert "opt-empty" in blank_ids
    assert "req-filled" not in blank_ids


@pytest.mark.integration
def test_track85_integration_placeholder_shown() -> None:
    """: input[placeholder][value=''] matches :placeholder-shown."""
    from aspose_html.css import select

    doc = _make_track85_form_doc()
    results = select(doc, "input:placeholder-shown")
    ids = {el.get_attribute("id") for el in results}
    assert "ph-shown" in ids
    assert "req-empty" not in ids  # no placeholder


@pytest.mark.integration
def test_track85_integration_default_and_read_only() -> None:
    """: :default matches submit; :read-only matches readonly text, checkbox."""
    from aspose_html.css import select

    doc = _make_track85_form_doc()
    default_els = select(doc, "input:default")
    ids = {el.get_attribute("id") for el in default_els}
    assert "submit" in ids
    assert "req-empty" not in ids

    ro_els = select(doc, ":read-only")
    ro_ids = {el.get_attribute("id") for el in ro_els}
    assert "ro-text" in ro_ids
    # form element itself is :read-only (non-editable)
    # checkbox type is non-editable input type → :read-only
    assert "checkbox" in ro_ids


@pytest.mark.integration
def test_track85_integration_read_write() -> None:
    """: :read-write matches editable inputs and textarea without readonly."""
    from aspose_html.css import select

    doc = _make_track85_form_doc()
    rw_els = select(doc, ":read-write")
    rw_ids = {el.get_attribute("id") for el in rw_els}
    assert "req-empty" in rw_ids
    assert "req-filled" in rw_ids
    assert "opt-empty" in rw_ids
    assert "ph-shown" in rw_ids
    assert "textarea" in rw_ids
    # readonly text and checkbox are not :read-write
    assert "ro-text" not in rw_ids
    assert "submit" not in rw_ids
    assert "checkbox" not in rw_ids


@pytest.mark.integration
def test_track85_integration_focus_within_empty_result() -> None:
    """: :focus-within returns empty list and raises no error."""
    from aspose_html.css import select

    doc = _make_track85_form_doc()
    assert select(doc, ":focus-within") == []


@pytest.mark.integration
def test_track85_integration_compound_selectors() -> None:
    """ AC-9: compound selectors compose correctly in real document."""
    from aspose_html.css import select

    doc = _make_track85_form_doc()
    # input:valid:required → only req-filled
    results = select(doc, "input:valid:required")
    ids = {el.get_attribute("id") for el in results}
    assert "req-filled" in ids
    assert "req-empty" not in ids
    assert "opt-empty" not in ids

    # input:invalid:required → only req-empty
    results2 = select(doc, "input:invalid:required")
    ids2 = {el.get_attribute("id") for el in results2}
    assert "req-empty" in ids2
    assert "req-filled" not in ids2

    # form:has(:invalid) → the form contains an invalid control
    form_results = select(doc, "form:has(:invalid)")
    assert len(form_results) == 1
    assert form_results[0].local_name == "form"


@pytest.mark.integration
def test_track85_integration_textarea_blank_read_write() -> None:
    """: textarea without value is :blank and :read-write."""
    from aspose_html.css import select

    doc = _make_track85_form_doc()
    textarea_els = select(doc, "textarea:blank")
    assert len(textarea_els) == 1
    assert textarea_els[0].get_attribute("id") == "textarea"

    textarea_rw = select(doc, "textarea:read-write")
    assert len(textarea_rw) == 1
    assert textarea_rw[0].get_attribute("id") == "textarea"
