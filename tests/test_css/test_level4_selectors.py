"""Tests for CSS Selectors Level 4 pseudo-classes ().

Covers all acceptance criteria from  and :
  :has(), :is(), :where(), complex :not()

Acceptance criteria tested:
  AC #1 — :is(h1, h2, h3) returns all matching heading elements
  AC #2 — :where(nav, aside) a returns anchors; :where contributes 0 specificity
  AC #3 — div:has(> p) matches only divs with a direct child p
  AC #4 — div:has(.note) matches divs with any descendant .note
  AC #5 — :not(p, .skip) matches elements that are neither p nor .skip
  AC #6 — :is(h1, ##invalid) is forgiving — invalid selector dropped, no SyntaxError
  AC #7 — :where() specificity is (0, 0, 0)
  AC #8 — :is(#id) specificity is (1, 0, 0)
  AC #9 — div:has(~ .sibling) matches a div that has a following .sibling
  AC #10 — all changes confined to src/aspose_html/css/ (verified by structure)
  AC #11 — all existing 93 tests still pass (run full suite)

Run with:
    PYTHONPATH=src python -m pytest tests/test_css/test_level4_selectors.py -v
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document, Element
from aspose_html.css import select
from aspose_html.css._parser import parse
from aspose_html.css._specificity import specificity, max_specificity
from aspose_html.css._ast import (
    HasPseudoClass,
    IsPseudoClass,
    WherePseudoClass,
    ComplexNotPseudoClass,
    TypeSelector,
    ClassSelector,
    IDSelector,
    SelectorList,
)


# ---------------------------------------------------------------------------
# DOM fixture helpers
# ---------------------------------------------------------------------------


def _make_heading_doc() -> Document:
    """Build a small document with mixed heading and text elements.

    Structure::

        Document
          html
            body
              h1 "Title"
              h2 "Subtitle"
              h3 "Section"
              p  "Paragraph"
              span "Span"
    """
    doc = Document()
    html = doc.create_element("html")
    body = doc.create_element("body")
    h1 = doc.create_element("h1")
    h2 = doc.create_element("h2")
    h3 = doc.create_element("h3")
    p = doc.create_element("p")
    span = doc.create_element("span")

    doc.append_child(html)
    html.append_child(body)
    body.append_child(h1)
    body.append_child(h2)
    body.append_child(h3)
    body.append_child(p)
    body.append_child(span)
    return doc


def _make_nav_doc() -> Document:
    """Build a document with nav and aside containing anchor elements.

    Structure::

        Document
          html
            body
              nav
                a[href="#nav-link"] "Nav link"
              aside
                a[href="#aside-link"] "Aside link"
              div
                a[href="#div-link"] "Div link" (should NOT match :where(nav,aside) a)
    """
    doc = Document()
    html = doc.create_element("html")
    body = doc.create_element("body")
    nav = doc.create_element("nav")
    nav_a = doc.create_element("a")
    nav_a.set_attribute("href", "#nav-link")
    aside = doc.create_element("aside")
    aside_a = doc.create_element("a")
    aside_a.set_attribute("href", "#aside-link")
    div = doc.create_element("div")
    div_a = doc.create_element("a")
    div_a.set_attribute("href", "#div-link")

    doc.append_child(html)
    html.append_child(body)
    body.append_child(nav)
    nav.append_child(nav_a)
    body.append_child(aside)
    aside.append_child(aside_a)
    body.append_child(div)
    div.append_child(div_a)
    return doc


def _make_has_doc() -> Document:
    """Build a document for testing :has() pseudo-class.

    Structure::

        Document
          html
            body
              div#with-child-p         (has direct child p → matches :has(> p))
                p "child paragraph"
              div#with-descendant-note  (has descendant .note → matches :has(.note))
                span
                  em.note "note"
              div#with-sibling          (has a following sibling .sibling → matches :has(~ .sibling))
              div.sibling               (the following sibling)
              div#empty                 (no p, no .note, no sibling → does not match either)
    """
    doc = Document()
    html = doc.create_element("html")
    body = doc.create_element("body")

    div_with_child = doc.create_element("div")
    div_with_child.set_attribute("id", "with-child-p")
    p_child = doc.create_element("p")
    div_with_child.append_child(p_child)

    div_with_desc = doc.create_element("div")
    div_with_desc.set_attribute("id", "with-descendant-note")
    span_inner = doc.create_element("span")
    em_note = doc.create_element("em")
    em_note.set_attribute("class", "note")
    span_inner.append_child(em_note)
    div_with_desc.append_child(span_inner)

    div_with_sibling = doc.create_element("div")
    div_with_sibling.set_attribute("id", "with-sibling")

    div_sibling = doc.create_element("div")
    div_sibling.set_attribute("class", "sibling")

    div_empty = doc.create_element("div")
    div_empty.set_attribute("id", "empty")

    doc.append_child(html)
    html.append_child(body)
    body.append_child(div_with_child)
    body.append_child(div_with_desc)
    body.append_child(div_with_sibling)
    body.append_child(div_sibling)
    body.append_child(div_empty)
    return doc


def _make_not_doc() -> Document:
    """Build a document for testing complex :not(p, .skip).

    Structure::

        Document
          html
            body
              p "paragraph"        (is <p> → excluded)
              div.skip "skip div"  (has .skip → excluded)
              h2 "heading"         (not p, not .skip → matches)
              span "span"          (not p, not .skip → matches)
    """
    doc = Document()
    html = doc.create_element("html")
    body = doc.create_element("body")
    p = doc.create_element("p")
    div_skip = doc.create_element("div")
    div_skip.set_attribute("class", "skip")
    h2 = doc.create_element("h2")
    span = doc.create_element("span")

    doc.append_child(html)
    html.append_child(body)
    body.append_child(p)
    body.append_child(div_skip)
    body.append_child(h2)
    body.append_child(span)
    return doc


# ---------------------------------------------------------------------------
# AC #1 — :is(h1, h2, h3) returns all heading elements
# ---------------------------------------------------------------------------


def test_is_matches_multiple_types() -> None:
    """AC #1: select(doc, ':is(h1, h2, h3)') returns all h1, h2, and h3 elements."""
    doc = _make_heading_doc()
    results = select(doc, ":is(h1, h2, h3)")
    tags = [el.local_name for el in results]
    assert sorted(tags) == ["h1", "h2", "h3"]
    # p and span are NOT in the result
    assert all(t not in tags for t in ["p", "span"])


def test_is_single_selector() -> None:
    """AC #1 edge case: :is(h1) is equivalent to h1."""
    doc = _make_heading_doc()
    results = select(doc, ":is(h1)")
    assert len(results) == 1
    assert results[0].local_name == "h1"


# ---------------------------------------------------------------------------
# AC #2 — :where(nav, aside) a returns anchors inside nav or aside
# ---------------------------------------------------------------------------


def test_where_matches_anchors_in_nav_aside() -> None:
    """AC #2: :where(nav, aside) a returns anchors inside nav or aside only."""
    doc = _make_nav_doc()
    results = select(doc, ":where(nav, aside) a")
    hrefs = [el.get_attribute("href") for el in results]
    assert "#nav-link" in hrefs
    assert "#aside-link" in hrefs
    # Anchor inside plain div is NOT matched
    assert "#div-link" not in hrefs


# ---------------------------------------------------------------------------
# AC #3 — div:has(> p) matches only divs with direct child p
# ---------------------------------------------------------------------------


def test_has_child_combinator() -> None:
    """AC #3: div:has(> p) matches only divs that have a direct child <p>."""
    doc = _make_has_doc()
    results = select(doc, "div:has(> p)")
    ids = [el.get_attribute("id") for el in results]
    assert "with-child-p" in ids
    # The div with a nested em.note does NOT have a direct p child
    assert "with-descendant-note" not in ids
    assert "empty" not in ids


# ---------------------------------------------------------------------------
# AC #4 — div:has(.note) matches divs with any descendant .note
# ---------------------------------------------------------------------------


def test_has_descendant_implicit() -> None:
    """AC #4: div:has(.note) matches divs that have any descendant with class .note."""
    doc = _make_has_doc()
    results = select(doc, "div:has(.note)")
    ids = [el.get_attribute("id") for el in results]
    # The div with a deep nested .note descendant matches
    assert "with-descendant-note" in ids
    # The div with only a direct <p> child has no .note descendant
    assert "with-child-p" not in ids
    assert "empty" not in ids


# ---------------------------------------------------------------------------
# AC #5 — :not(p, .skip) matches elements that are neither p nor .skip
# ---------------------------------------------------------------------------


def test_complex_not_with_selector_list() -> None:
    """AC #5: :not(p, .skip) matches elements that are not <p> and not .skip."""
    doc = _make_not_doc()
    results = select(doc, ":not(p, .skip)")
    tags = [el.local_name for el in results]
    # p is excluded
    assert "p" not in tags
    # div.skip is excluded
    for el in results:
        assert not (el.local_name == "div" and "skip" in el.class_list)
    # h2 and span are included
    assert "h2" in tags
    assert "span" in tags


# ---------------------------------------------------------------------------
# AC #6 — :is() forgiving parsing drops invalid selectors silently
# ---------------------------------------------------------------------------


def test_is_forgiving_drops_invalid_selector() -> None:
    """AC #6: :is(h1, ##invalid) is forgiving — ##invalid is dropped, no SyntaxError."""
    # ##invalid is two ## which tokenises as INVALID + INVALID — triggers SyntaxError
    # in strict mode but is silently dropped in :is() forgiving mode.
    doc = _make_heading_doc()
    # This must NOT raise SyntaxError
    results = select(doc, ":is(h1, ##invalid)")
    # Should still match h1 elements
    assert len(results) == 1
    assert results[0].local_name == "h1"


def test_where_forgiving_drops_invalid_selector() -> None:
    """AC #6 (where): :where(h2, ##bad) is forgiving — invalid selector silently dropped."""
    doc = _make_heading_doc()
    results = select(doc, ":where(h2, ##bad)")
    assert len(results) == 1
    assert results[0].local_name == "h2"


def test_enabled_disabled_element_matches_is_deterministic() -> None:
    """: Element.matches(':enabled'|':disabled') is deterministic."""
    doc = Document()
    body = doc.create_element("body")
    button = doc.create_element("button")
    doc.append_child(body)
    body.append_child(button)

    assert button.matches(":enabled") is True
    assert button.matches(":disabled") is False

    button.set_attribute("disabled", "")
    assert button.matches(":enabled") is False
    assert button.matches(":disabled") is True


def test_focus_within_no_match_headless() -> None:
    """ : :focus-within is now a valid selector with no-match headless semantics.

    Prior to  this selector raised NotImplementedError;  moves it
    from _PSEUDO_DYNAMIC_OOS into _PSEUDO_NO_ARG and the matcher returns False
    deterministically (no focus propagation model in headless mode).
    """
    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)

    # Must not raise; returns empty list since nothing has focus in headless mode.
    result = select(doc, ":focus-within")
    assert result == []


def test_checked_element_matches_is_deterministic() -> None:
    """: Element.matches(':checked') follows checked/selected state."""
    doc = Document()
    body = doc.create_element("body")
    doc.append_child(body)

    checkbox = doc.create_element("input")
    checkbox.set_attribute("type", "checkbox")
    body.append_child(checkbox)

    option = doc.create_element("option")
    body.append_child(option)

    div = doc.create_element("div")
    div.set_attribute("checked", "")
    body.append_child(div)

    assert checkbox.matches(":checked") is False
    checkbox.checked = True
    assert checkbox.matches(":checked") is True

    assert option.matches(":checked") is False
    option.selected = True
    assert option.matches(":checked") is True

    assert div.matches(":checked") is False


def test_is_all_invalid_raises_syntax_error() -> None:
    """AC #6 edge: :is(##invalid) — all entries invalid → SyntaxError."""
    with pytest.raises(SyntaxError):
        parse(":is(##invalid)")


# ---------------------------------------------------------------------------
# AC #7 — :where() contributes 0 specificity
# ---------------------------------------------------------------------------


def test_where_zero_specificity() -> None:
    """AC #7: :where(nav, aside) contributes (0, 0, 0) to specificity."""
    result = parse(":where(nav, aside)")
    spec = specificity(result.selectors[0])
    assert spec == (0, 0, 0), f"Expected (0, 0, 0) but got {spec}"


def test_where_in_compound_zero_specificity() -> None:
    """AC #7 compound: :where(nav, aside) a — the :where part contributes 0."""
    # The full selector "a" has specificity (0,0,1); :where(nav, aside) adds 0.
    # So the combined specificity should be (0, 0, 1).
    result = parse(":where(nav, aside) a")
    spec = specificity(result.selectors[0])
    # :where adds 0, "a" type selector adds (0,0,1)
    assert spec == (0, 0, 1), f"Expected (0, 0, 1) but got {spec}"


# ---------------------------------------------------------------------------
# AC #8 — :is(#id) contributes specificity (1, 0, 0)
# ---------------------------------------------------------------------------


def test_is_specificity_max_of_arguments() -> None:
    """AC #8: :is(#id) contributes specificity (1, 0, 0) — max of argument list."""
    result = parse(":is(#myid)")
    spec = specificity(result.selectors[0])
    assert spec == (1, 0, 0), f"Expected (1, 0, 0) but got {spec}"


def test_is_specificity_multiple_args_max() -> None:
    """AC #8 variant: :is(h1, #id, .cls) — specificity is the max, which is (1,0,0)."""
    result = parse(":is(h1, #id, .cls)")
    spec = specificity(result.selectors[0])
    assert spec == (1, 0, 0), f"Expected (1, 0, 0) but got {spec}"


def test_not_specificity_max_of_arguments() -> None:
    """AC #8 variant: :not(p, #id) — specificity is max of arguments = (1, 0, 0)."""
    result = parse(":not(p, #id)")
    spec = specificity(result.selectors[0])
    assert spec == (1, 0, 0), f"Expected (1, 0, 0) but got {spec}"


def test_has_specificity_max_of_arguments() -> None:
    """AC #8 variant: div:has(> #id) — specificity of :has() = max arg = (1, 0, 0)."""
    result = parse("div:has(> #myid)")
    spec = specificity(result.selectors[0])
    # div contributes (0,0,1), :has(> #myid) contributes (1,0,0) → total (1,0,1)
    assert spec == (1, 0, 1), f"Expected (1, 0, 1) but got {spec}"


# ---------------------------------------------------------------------------
# AC #9 — div:has(~ .sibling) matches div with following .sibling
# ---------------------------------------------------------------------------


def test_has_following_sibling() -> None:
    """AC #9: div:has(~ .sibling) matches a div that has a following sibling .sibling."""
    doc = _make_has_doc()
    results = select(doc, "div:has(~ .sibling)")
    ids = [el.get_attribute("id") for el in results]
    # div#with-sibling has div.sibling as following sibling
    assert "with-sibling" in ids
    # div#empty has no following element siblings → does not match
    assert "empty" not in ids


def test_has_adjacent_sibling() -> None:
    """Extra: div:has(+ .sibling) matches only divs with .sibling as immediate next sibling."""
    doc = _make_has_doc()
    results = select(doc, "div:has(+ .sibling)")
    ids = [el.get_attribute("id") for el in results]
    # div#with-sibling is immediately followed by div.sibling → matches
    assert "with-sibling" in ids


# ---------------------------------------------------------------------------
# Parser-level AST structure tests
# ---------------------------------------------------------------------------


def test_parse_is_produces_is_pseudo_class_node() -> None:
    """Parser produces IsPseudoClass node for :is()."""
    result = parse(":is(div, span)")
    simple = result.selectors[0].parts[0][1].simple_selectors[0]
    assert isinstance(simple, IsPseudoClass)
    assert len(simple.selector_list.selectors) == 2


def test_parse_where_produces_where_pseudo_class_node() -> None:
    """Parser produces WherePseudoClass node for :where()."""
    result = parse(":where(nav, aside)")
    simple = result.selectors[0].parts[0][1].simple_selectors[0]
    assert isinstance(simple, WherePseudoClass)
    assert len(simple.selector_list.selectors) == 2


def test_parse_has_produces_has_pseudo_class_node() -> None:
    """Parser produces HasPseudoClass node for :has()."""
    result = parse(":has(> p)")
    simple = result.selectors[0].parts[0][1].simple_selectors[0]
    assert isinstance(simple, HasPseudoClass)
    assert len(simple.relative_selectors) == 1


def test_parse_has_with_implicit_descendant() -> None:
    """Parser correctly sets leading_combinator=None for :has(.note)."""
    from aspose_html.css._ast import Combinator
    result = parse(":has(.note)")
    simple = result.selectors[0].parts[0][1].simple_selectors[0]
    assert isinstance(simple, HasPseudoClass)
    leading_combinator, _ = simple.relative_selectors[0]
    assert leading_combinator is None  # implicit descendant


def test_parse_has_with_child_combinator() -> None:
    """Parser sets Combinator.CHILD for :has(> p)."""
    from aspose_html.css._ast import Combinator
    result = parse(":has(> p)")
    simple = result.selectors[0].parts[0][1].simple_selectors[0]
    assert isinstance(simple, HasPseudoClass)
    leading_combinator, _ = simple.relative_selectors[0]
    assert leading_combinator is Combinator.CHILD


def test_parse_has_with_sibling_combinator() -> None:
    """Parser sets Combinator.SIBLING for :has(~ .sibling)."""
    from aspose_html.css._ast import Combinator
    result = parse(":has(~ .sibling)")
    simple = result.selectors[0].parts[0][1].simple_selectors[0]
    assert isinstance(simple, HasPseudoClass)
    leading_combinator, _ = simple.relative_selectors[0]
    assert leading_combinator is Combinator.SIBLING


def test_parse_complex_not_produces_complex_not_node() -> None:
    """Parser produces ComplexNotPseudoClass for all :not() forms ()."""
    result = parse(":not(p, .skip)")
    simple = result.selectors[0].parts[0][1].simple_selectors[0]
    assert isinstance(simple, ComplexNotPseudoClass)
    assert len(simple.selector_list.selectors) == 2


def test_parse_not_single_arg_still_produces_complex_not() -> None:
    """Single-arg :not(p) also produces ComplexNotPseudoClass (uniform dispatch)."""
    result = parse(":not(p)")
    simple = result.selectors[0].parts[0][1].simple_selectors[0]
    assert isinstance(simple, ComplexNotPseudoClass)
    inner_compound = simple.selector_list.selectors[0].parts[0][1]
    assert isinstance(inner_compound.simple_selectors[0], TypeSelector)


def test_has_empty_argument_raises_syntax_error() -> None:
    """:has() with empty argument list raises SyntaxError (non-forgiving per Level 4)."""
    with pytest.raises(SyntaxError):
        parse(":has()")


def test_has_non_forgiving_invalid_selector() -> None:
    """:has() is non-forgiving — invalid selector propagates as SyntaxError."""
    with pytest.raises(SyntaxError):
        parse(":has(##invalid)")


def test_not_non_forgiving() -> None:
    """:not() is non-forgiving — invalid selector raises SyntaxError."""
    with pytest.raises(SyntaxError):
        parse(":not(##invalid)")


def test_nested_not_raises_syntax_error() -> None:
    """: :not(:not(p)) is forbidden by CSS Selectors Level 4 §4.5."""
    with pytest.raises(SyntaxError, match="Nested :not\\(\\)"):
        parse(":not(:not(p))")


def test_nested_not_with_class_raises_syntax_error() -> None:
    """: :not(:not(.cls)) is forbidden by CSS Selectors Level 4 §4.5."""
    with pytest.raises(SyntaxError, match="Nested :not\\(\\)"):
        parse(":not(:not(.cls))")


def test_not_inside_is_is_valid() -> None:
    """:is(:not(p)) is valid — :not() nested inside :is() is allowed."""
    # Should not raise; :not() inside :is() arguments is permitted.
    result = parse(":is(:not(p))")
    assert result is not None


def test_not_with_selector_list_no_regression() -> None:
    """:not(p, .cls) with a plain selector list must not raise ( regression guard)."""
    result = parse(":not(p, .cls)")
    assert result is not None


def test_not_simple_no_regression() -> None:
    """:not(p) simple case must still parse and match correctly ( regression guard)."""
    result = parse(":not(p)")
    assert result is not None


def test_is_trailing_comma_raises_syntax_error() -> None:
    with pytest.raises(SyntaxError):
        parse(":is(h1,)")


def test_is_duplicate_comma_raises_syntax_error() -> None:
    with pytest.raises(SyntaxError):
        parse(":is(h1,,h2)")


def test_where_duplicate_comma_raises_syntax_error() -> None:
    with pytest.raises(SyntaxError):
        parse(":where(nav,,aside)")


def test_not_leading_combinator_rejected() -> None:
    with pytest.raises(SyntaxError):
        parse(":not(> p)")


def test_not_empty_argument_raises_syntax_error() -> None:
    with pytest.raises(SyntaxError):
        parse(":not()")


def test_where_empty_argument_raises_syntax_error() -> None:
    with pytest.raises(SyntaxError):
        parse(":where()")


def test_valid_neighbors_for_invalid_cases_still_parse() -> None:
    assert parse(":is(h1, h2)") is not None
    assert parse(":where(nav, aside)") is not None
    assert parse(":not(p, .skip)") is not None


# ---------------------------------------------------------------------------
# Specificity calculations for all four new pseudo-classes
# ---------------------------------------------------------------------------


def test_specificity_where_always_zero() -> None:
    """Specificity: :where(#id) still contributes (0, 0, 0)."""
    result = parse(":where(#id)")
    spec = specificity(result.selectors[0])
    assert spec == (0, 0, 0)


def test_specificity_is_class_arg() -> None:
    """Specificity: :is(.cls) contributes (0, 1, 0)."""
    result = parse(":is(.cls)")
    spec = specificity(result.selectors[0])
    assert spec == (0, 1, 0)


def test_specificity_has_class_arg() -> None:
    """Specificity: :has(.cls) contributes (0, 1, 0)."""
    result = parse(":has(.cls)")
    spec = specificity(result.selectors[0])
    assert spec == (0, 1, 0)


def test_specificity_complex_not_id_arg() -> None:
    """Specificity: :not(#foo) contributes (1, 0, 0) — max of arguments."""
    result = parse(":not(#foo)")
    spec = specificity(result.selectors[0])
    assert spec == (1, 0, 0)


def test_specificity_is_in_compound() -> None:
    """Specificity: div:is(#id) == (0,0,1) + (1,0,0) = (1, 0, 1)."""
    result = parse("div:is(#id)")
    spec = specificity(result.selectors[0])
    assert spec == (1, 0, 1)


# ---------------------------------------------------------------------------
#  — deterministic no-match for selected stateful pseudo-classes
# ---------------------------------------------------------------------------


def test_stateful_pseudo_class_query_selector_all_no_match() -> None:
    """ AC #1/#2: :hover and :focus-visible are valid and match nothing."""
    doc = _make_heading_doc()
    assert select(doc, ":hover") == []
    assert select(doc, ":focus-visible") == []


def test_stateful_pseudo_class_element_matches_false() -> None:
    """ AC #3: element.matches(':active') returns False, no exception."""
    doc = _make_heading_doc()
    html = doc.document_element
    assert html is not None
    body = html.first_element_child
    assert body is not None
    target = body.first_element_child
    assert target is not None
    assert target.matches(":active") is False


def test_stateful_pseudo_class_inside_not_remains_matchable() -> None:
    """: valid no-match pseudo-classes work in composition (:not)."""
    doc = _make_heading_doc()
    # Since :hover never matches in headless mode, :not(:hover) matches all elements.
    results = select(doc, ":not(:hover)")
    tags = [el.local_name for el in results]
    assert "html" in tags
    assert "body" in tags
    assert "h1" in tags and "h2" in tags and "h3" in tags and "p" in tags and "span" in tags


def test_target_parser_accepts_no_arg_form() -> None:
    """: parser accepts :target as a no-argument pseudo-class."""
    parsed = parse(":target")
    assert parsed is not None


def test_target_element_matches_agrees_with_select() -> None:
    """: Element.matches(':target') aligns with select(doc, ':target')."""
    doc = Document()
    doc._url = "https://example.com/page#hero"
    body = doc.create_element("body")
    doc.append_child(body)

    hero = doc.create_element("section")
    hero.set_attribute("id", "hero")
    other = doc.create_element("section")
    other.set_attribute("id", "other")
    body.append_child(hero)
    body.append_child(other)

    assert hero.matches(":target") is True
    assert other.matches(":target") is False
    assert select(doc, ":target") == [hero]


def test_unknown_pseudo_class_still_raises_syntax_error() -> None:
    """ AC #4: unrecognized pseudo-classes still fail with SyntaxError."""
    with pytest.raises(SyntaxError):
        parse(":totally-not-a-real-pseudo")


def test_scope_parser_recognized_as_no_arg_pseudo_class() -> None:
    """ AC #3: parser accepts :scope as a regular no-arg pseudo-class."""
    parsed = parse(":scope:not(.missing)")
    assert parsed is not None


# ---------------------------------------------------------------------------
#  /  — form constraint-validation and UI-state pseudo-classes
# ---------------------------------------------------------------------------


def _make_form_doc() -> "Document":
    """Build a small form document for  tests.

    Structure::

        Document
          form
            input#required-empty  [type=text required value=""]
            input#required-filled  [type=text required value="filled"]
            input#optional-empty  [type=text value=""]
            input#placeholder-input  [type=text placeholder="hint" value=""]
            input#submit-btn  [type=submit]
            input#checkbox-indet  [type=checkbox]
            input#readonly-input  [type=text readonly value="locked"]
            textarea#textarea-empty
            div#just-a-div
    """
    doc = Document()
    form = doc.create_element("form")
    doc.append_child(form)

    req_empty = doc.create_element("input")
    req_empty.set_attribute("id", "required-empty")
    req_empty.set_attribute("type", "text")
    req_empty.set_attribute("required", "")
    req_empty.set_attribute("value", "")
    form.append_child(req_empty)

    req_filled = doc.create_element("input")
    req_filled.set_attribute("id", "required-filled")
    req_filled.set_attribute("type", "text")
    req_filled.set_attribute("required", "")
    req_filled.set_attribute("value", "filled")
    form.append_child(req_filled)

    opt_empty = doc.create_element("input")
    opt_empty.set_attribute("id", "optional-empty")
    opt_empty.set_attribute("type", "text")
    opt_empty.set_attribute("value", "")
    form.append_child(opt_empty)

    placeholder_inp = doc.create_element("input")
    placeholder_inp.set_attribute("id", "placeholder-input")
    placeholder_inp.set_attribute("type", "text")
    placeholder_inp.set_attribute("placeholder", "hint")
    placeholder_inp.set_attribute("value", "")
    form.append_child(placeholder_inp)

    submit_btn = doc.create_element("input")
    submit_btn.set_attribute("id", "submit-btn")
    submit_btn.set_attribute("type", "submit")
    form.append_child(submit_btn)

    checkbox = doc.create_element("input")
    checkbox.set_attribute("id", "checkbox-indet")
    checkbox.set_attribute("type", "checkbox")
    form.append_child(checkbox)

    readonly_inp = doc.create_element("input")
    readonly_inp.set_attribute("id", "readonly-input")
    readonly_inp.set_attribute("type", "text")
    readonly_inp.set_attribute("readonly", "")
    readonly_inp.set_attribute("value", "locked")
    form.append_child(readonly_inp)

    textarea = doc.create_element("textarea")
    textarea.set_attribute("id", "textarea-empty")
    form.append_child(textarea)

    div = doc.create_element("div")
    div.set_attribute("id", "just-a-div")
    form.append_child(div)

    return doc


def _el(doc: "Document", id_: str) -> "Element":
    """Return element by id using query_selector."""
    result = select(doc, f"#{id_}")
    assert result, f"Element #{id_!r} not found"
    return result[0]


def test_track85_parser_accepts_all_new_pseudo_classes() -> None:
    """ AC-10: all eleven pseudo-class names parse without SyntaxError."""
    names = [
        "valid", "invalid", "required", "optional",
        "placeholder-shown", "default", "indeterminate",
        "read-only", "read-write", "blank", "focus-within",
    ]
    for name in names:
        parsed = parse(f":{name}")
        assert parsed is not None, f":{name} did not parse"


def test_track85_pseudo_dynamic_oos_is_empty() -> None:
    """ : _PSEUDO_DYNAMIC_OOS is an empty frozenset after ."""
    from aspose_html.css._parser import _PSEUDO_DYNAMIC_OOS
    assert _PSEUDO_DYNAMIC_OOS == frozenset()


def test_track85_valid_invalid_required_empty() -> None:
    """ AC-1: :invalid matches required input with empty value."""
    doc = _make_form_doc()
    req_empty = _el(doc, "required-empty")
    # required text input with value="" is invalid (value_missing=True)
    assert req_empty.matches(":invalid") is True
    assert req_empty.matches(":valid") is False


def test_track85_valid_required_filled() -> None:
    """ AC-1: :valid matches required input with non-empty value."""
    doc = _make_form_doc()
    req_filled = _el(doc, "required-filled")
    assert req_filled.matches(":valid") is True
    assert req_filled.matches(":invalid") is False


def test_track85_valid_optional_empty() -> None:
    """ AC-1: :valid matches optional input (required=False, value='')."""
    doc = _make_form_doc()
    opt_empty = _el(doc, "optional-empty")
    assert opt_empty.matches(":valid") is True
    assert opt_empty.matches(":invalid") is False


def test_track85_valid_invalid_non_form_element() -> None:
    """ AC-1: :valid and :invalid never match non-form elements."""
    doc = _make_form_doc()
    div = _el(doc, "just-a-div")
    assert div.matches(":valid") is False
    assert div.matches(":invalid") is False


def test_track85_required_pseudo_class() -> None:
    """ AC-2: :required matches input with required attribute."""
    doc = _make_form_doc()
    req_empty = _el(doc, "required-empty")
    req_filled = _el(doc, "required-filled")
    opt_empty = _el(doc, "optional-empty")
    assert req_empty.matches(":required") is True
    assert req_filled.matches(":required") is True
    assert opt_empty.matches(":required") is False


def test_track85_optional_pseudo_class() -> None:
    """ AC-2: :optional matches will_validate input without required."""
    doc = _make_form_doc()
    opt_empty = _el(doc, "optional-empty")
    req_empty = _el(doc, "required-empty")
    div = _el(doc, "just-a-div")
    assert opt_empty.matches(":optional") is True
    assert req_empty.matches(":optional") is False
    # non-form elements: will_validate=False → not :optional
    assert div.matches(":optional") is False


def test_track85_placeholder_shown() -> None:
    """ AC-3: :placeholder-shown matches input with placeholder and empty value."""
    doc = _make_form_doc()
    ph_inp = _el(doc, "placeholder-input")
    req_filled = _el(doc, "required-filled")
    opt_empty = _el(doc, "optional-empty")

    # has placeholder + value=""  → matches
    assert ph_inp.matches(":placeholder-shown") is True
    # no placeholder → does not match
    assert opt_empty.matches(":placeholder-shown") is False
    # has value (non-empty) → does not match even if it had a placeholder
    assert req_filled.matches(":placeholder-shown") is False


def test_track85_default_submit() -> None:
    """ AC-4: :default matches input[type=submit] and input[type=image]."""
    doc = _make_form_doc()
    submit_btn = _el(doc, "submit-btn")
    req_empty = _el(doc, "required-empty")
    div = _el(doc, "just-a-div")
    assert submit_btn.matches(":default") is True
    assert req_empty.matches(":default") is False
    assert div.matches(":default") is False


def test_track85_default_image_input() -> None:
    """ AC-4: :default also matches input[type=image]."""
    doc = Document()
    img_inp = doc.create_element("input")
    img_inp.set_attribute("type", "image")
    doc.append_child(img_inp)
    assert img_inp.matches(":default") is True


def test_track85_indeterminate_checkbox() -> None:
    """ AC-5: :indeterminate matches checkbox with indeterminate=True."""
    doc = _make_form_doc()
    checkbox = _el(doc, "checkbox-indet")
    # indeterminate defaults to False
    assert checkbox.matches(":indeterminate") is False
    # set via property
    checkbox.indeterminate = True
    assert checkbox.matches(":indeterminate") is True
    checkbox.indeterminate = False
    assert checkbox.matches(":indeterminate") is False


def test_track85_indeterminate_non_checkbox() -> None:
    """ AC-5: :indeterminate never matches non-checkbox elements."""
    doc = _make_form_doc()
    div = _el(doc, "just-a-div")
    req_empty = _el(doc, "required-empty")  # type=text
    assert div.matches(":indeterminate") is False
    assert req_empty.matches(":indeterminate") is False


def test_track85_read_only_input_with_readonly() -> None:
    """ AC-6: :read-only matches input with readonly attribute."""
    doc = _make_form_doc()
    readonly_inp = _el(doc, "readonly-input")
    assert readonly_inp.matches(":read-only") is True
    assert readonly_inp.matches(":read-write") is False


def test_track85_read_write_regular_input() -> None:
    """ AC-6: :read-write matches editable input without readonly."""
    doc = _make_form_doc()
    req_empty = _el(doc, "required-empty")
    assert req_empty.matches(":read-write") is True
    assert req_empty.matches(":read-only") is False


def test_track85_read_only_textarea_with_readonly() -> None:
    """ AC-6: :read-only matches textarea with readonly attribute."""
    doc = Document()
    ta = doc.create_element("textarea")
    ta.set_attribute("readonly", "")
    doc.append_child(ta)
    assert ta.matches(":read-only") is True
    assert ta.matches(":read-write") is False


def test_track85_read_write_textarea_without_readonly() -> None:
    """ AC-6: :read-write matches textarea without readonly."""
    doc = _make_form_doc()
    textarea = _el(doc, "textarea-empty")
    assert textarea.matches(":read-write") is True
    assert textarea.matches(":read-only") is False


def test_track85_read_only_non_form_element() -> None:
    """ AC-6: :read-only matches non-form elements (always read-only)."""
    doc = _make_form_doc()
    div = _el(doc, "just-a-div")
    assert div.matches(":read-only") is True
    assert div.matches(":read-write") is False


def test_track85_blank_empty_input() -> None:
    """ AC-7: :blank matches input with empty value attribute."""
    doc = _make_form_doc()
    req_empty = _el(doc, "required-empty")
    opt_empty = _el(doc, "optional-empty")
    assert req_empty.matches(":blank") is True
    assert opt_empty.matches(":blank") is True


def test_track85_blank_whitespace_value() -> None:
    """ AC-7: :blank matches input with whitespace-only value."""
    doc = Document()
    inp = doc.create_element("input")
    inp.set_attribute("type", "text")
    inp.set_attribute("value", "   ")
    doc.append_child(inp)
    assert inp.matches(":blank") is True


def test_track85_blank_non_empty_input() -> None:
    """ AC-7: :blank does not match input with non-empty value."""
    doc = _make_form_doc()
    req_filled = _el(doc, "required-filled")
    assert req_filled.matches(":blank") is False


def test_track85_blank_non_form_element() -> None:
    """ AC-7: :blank does not match non-form elements."""
    doc = _make_form_doc()
    div = _el(doc, "just-a-div")
    assert div.matches(":blank") is False


def test_track85_blank_textarea_empty() -> None:
    """ AC-7: :blank matches textarea with no value attribute."""
    doc = _make_form_doc()
    textarea = _el(doc, "textarea-empty")
    assert textarea.matches(":blank") is True


def test_track85_focus_within_no_match() -> None:
    """ AC-8: :focus-within parses without error and matches nothing."""
    doc = _make_form_doc()
    result = select(doc, ":focus-within")
    assert result == []


def test_track85_focus_within_element_matches_false() -> None:
    """ AC-8: Element.matches(':focus-within') returns False, no error."""
    doc = _make_form_doc()
    div = _el(doc, "just-a-div")
    assert div.matches(":focus-within") is False


def test_track85_compound_valid_required() -> None:
    """ AC-9: input:valid:required composes correctly."""
    doc = _make_form_doc()
    # required-filled: required + valid
    req_filled = _el(doc, "required-filled")
    assert req_filled.matches("input:valid:required") is True
    # required-empty: required + invalid
    req_empty = _el(doc, "required-empty")
    assert req_empty.matches("input:valid:required") is False


def test_track85_compound_invalid_required() -> None:
    """ AC-9: input:invalid:required composes correctly."""
    doc = _make_form_doc()
    req_empty = _el(doc, "required-empty")
    assert req_empty.matches("input:invalid:required") is True
    req_filled = _el(doc, "required-filled")
    assert req_filled.matches("input:invalid:required") is False


def test_track85_has_invalid_in_form() -> None:
    """ AC-9: form:has(:invalid) matches when form contains invalid control."""
    doc = _make_form_doc()
    form_results = select(doc, "form:has(:invalid)")
    # Our form has required-empty which is invalid
    assert len(form_results) == 1
    assert form_results[0].local_name == "form"


def test_track85_select_all_required_inputs() -> None:
    """ AC-2: select(doc, 'input:required') returns both required inputs."""
    doc = _make_form_doc()
    results = select(doc, "input:required")
    ids = {el.get_attribute("id") for el in results}
    assert "required-empty" in ids
    assert "required-filled" in ids
    assert "optional-empty" not in ids


def test_track85_select_all_valid_inputs() -> None:
    """ AC-1: select(doc, 'input:valid') returns valid inputs only."""
    doc = _make_form_doc()
    results = select(doc, "input:valid")
    ids = {el.get_attribute("id") for el in results}
    # required-empty is invalid; submit/checkbox have type that affects will_validate
    assert "required-filled" in ids
    assert "optional-empty" in ids
    assert "required-empty" not in ids


def test_track85_no_regression_enabled_disabled() -> None:
    """ AC-10: :enabled/:disabled still work after  changes."""
    doc = Document()
    form = doc.create_element("form")
    doc.append_child(form)
    enabled = doc.create_element("input")
    enabled.set_attribute("type", "text")
    disabled = doc.create_element("input")
    disabled.set_attribute("type", "text")
    disabled.set_attribute("disabled", "")
    form.append_child(enabled)
    form.append_child(disabled)
    assert enabled.matches(":enabled") is True
    assert disabled.matches(":disabled") is True


def test_track85_no_regression_checked() -> None:
    """ AC-10: :checked still works after  changes."""
    doc = Document()
    cb = doc.create_element("input")
    cb.set_attribute("type", "checkbox")
    doc.append_child(cb)
    assert cb.matches(":checked") is False
    cb.checked = True
    assert cb.matches(":checked") is True
