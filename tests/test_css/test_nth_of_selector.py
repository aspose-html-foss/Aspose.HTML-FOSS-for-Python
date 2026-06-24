"""Tests for CSS :nth-child(An+B of S) and :nth-last-child(An+B of S).

Covers  Group A /  acceptance criteria (parsing):
  AC-1  :nth-child(2 of .foo) -> NthFilteredChildPseudoClass(nth=NthArgument(a=0,b=2))
  AC-2  :nth-child(2n+1 of p, .item) -> filter SelectorList with 2 entries
  AC-3  :nth-child(odd) -> PseudoClassSelector backward-compat (unchanged path)
  AC-4  :nth-last-child(3 of p) -> NthFilteredChildPseudoClass(reverse=True)
  AC-5  :nth-child(of .foo) -> SyntaxError (missing An+B)
  AC-6  :nth-child(2 of) -> SyntaxError (empty filter)
  AC-7  NthFilteredChildPseudoClass is a frozen dataclass
  AC-8  doctests verified via pytest --doctest-modules (separate run)

Covers  Group B /  acceptance criteria (matching + specificity):
  AC-1  select(ul, 'li:nth-child(1 of .x)') returns first .x element
  AC-2  select(ul, 'li:nth-child(2 of .x)') returns second .x element
  AC-3  select(ul, 'li:nth-last-child(1 of .x)') returns last .x element
  AC-4  select with ':nth-child(odd of li)' returns odd-positioned li elements
  AC-5  specificity of ':nth-child(2 of .foo)' is (0, 2, 0)
  AC-6  specificity of ':nth-child(2 of #id)' is (1, 1, 0)
  AC-7  specificity of ':nth-child(2 of p.item)' is (0, 2, 1)
  AC-8  existing ':nth-child(2)' matching unchanged
  AC-9  existing ':nth-of-type(2)' matching unchanged
  AC-10 all docstring >>> examples pass under pytest --doctest-modules
"""
from __future__ import annotations

import pytest

from aspose_html.css._parser import parse
from aspose_html.css._ast import (
    NthFilteredChildPseudoClass,
    NthArgument,
    PseudoClassSelector,
    ClassSelector,
    TypeSelector,
)


def _get_first_simple(selector_str: str):
    """Parse selector_str and return the first simple selector in the first compound."""
    result = parse(selector_str)
    return result.selectors[0].parts[0][1].simple_selectors[0]


# ── AC-1: :nth-child(2 of .foo) ───────────────────────────────────────────────

def test_nth_child_of_produces_filtered_node():
    """AC-1: parse(':nth-child(2 of .foo)') produces NthFilteredChildPseudoClass."""
    node = _get_first_simple(":nth-child(2 of .foo)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    assert node.nth == NthArgument(a=0, b=2)
    assert node.reverse is False


def test_nth_child_of_filter_class_selector():
    """AC-1 detail: the filter SelectorList contains a ClassSelector for .foo."""
    node = _get_first_simple(":nth-child(2 of .foo)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    # The filter is a SelectorList; its first selector's first compound has .foo
    filter_compound = node.filter.selectors[0].parts[0][1]
    assert filter_compound.simple_selectors[0] == ClassSelector(class_name="foo")


# ── AC-2: :nth-child(2n+1 of p, .item) ───────────────────────────────────────

def test_nth_child_of_multi_selector_filter():
    """AC-2: parse(':nth-child(2n+1 of p, .item)') filter has 2 selectors."""
    node = _get_first_simple(":nth-child(2n+1 of p, .item)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    assert node.nth == NthArgument(a=2, b=1)
    assert len(node.filter.selectors) == 2


def test_nth_child_of_multi_filter_first_is_type():
    """AC-2 detail: first selector in filter is TypeSelector('p')."""
    node = _get_first_simple(":nth-child(2n+1 of p, .item)")
    first_compound = node.filter.selectors[0].parts[0][1]
    assert first_compound.simple_selectors[0] == TypeSelector(tag_name="p")


def test_nth_child_of_multi_filter_second_is_class():
    """AC-2 detail: second selector in filter is ClassSelector('item')."""
    node = _get_first_simple(":nth-child(2n+1 of p, .item)")
    second_compound = node.filter.selectors[1].parts[0][1]
    assert second_compound.simple_selectors[0] == ClassSelector(class_name="item")


# ── AC-3: :nth-child(odd) — backward compatibility ────────────────────────────

def test_plain_nth_child_unchanged():
    """AC-3: parse(':nth-child(odd)') still produces PseudoClassSelector."""
    node = _get_first_simple(":nth-child(odd)")
    assert isinstance(node, PseudoClassSelector)
    assert node.name == "nth-child"
    assert node.argument == NthArgument(a=2, b=1)


def test_plain_nth_child_even_unchanged():
    """AC-3 variant: :nth-child(even) still produces PseudoClassSelector."""
    node = _get_first_simple(":nth-child(even)")
    assert isinstance(node, PseudoClassSelector)
    assert node.argument == NthArgument(a=2, b=0)


def test_plain_nth_child_integer_unchanged():
    """AC-3 variant: :nth-child(3) still produces PseudoClassSelector."""
    node = _get_first_simple(":nth-child(3)")
    assert isinstance(node, PseudoClassSelector)
    assert node.argument == NthArgument(a=0, b=3)


def test_plain_nth_child_2n1_unchanged():
    """AC-3 variant: :nth-child(2n+1) still produces PseudoClassSelector."""
    node = _get_first_simple(":nth-child(2n+1)")
    assert isinstance(node, PseudoClassSelector)
    assert node.argument == NthArgument(a=2, b=1)


# ── AC-4: :nth-last-child(3 of p) ────────────────────────────────────────────

def test_nth_last_child_of():
    """AC-4: parse(':nth-last-child(3 of p)') produces filtered node with reverse=True."""
    node = _get_first_simple(":nth-last-child(3 of p)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    assert node.nth == NthArgument(a=0, b=3)
    assert node.reverse is True


def test_nth_last_child_of_filter_type():
    """AC-4 detail: filter matches TypeSelector('p')."""
    node = _get_first_simple(":nth-last-child(3 of p)")
    filter_compound = node.filter.selectors[0].parts[0][1]
    assert filter_compound.simple_selectors[0] == TypeSelector(tag_name="p")


# ── AC-5: :nth-child(of .foo) — SyntaxError (missing An+B) ───────────────────

def test_nth_child_of_missing_anb_raises():
    """AC-5: parse(':nth-child(of .foo)') raises SyntaxError."""
    with pytest.raises(SyntaxError):
        parse(":nth-child(of .foo)")


# ── AC-6: :nth-child(2 of) — SyntaxError (empty filter) ─────────────────────

def test_nth_child_of_missing_filter_raises():
    """AC-6: parse(':nth-child(2 of)') raises SyntaxError."""
    with pytest.raises(SyntaxError):
        parse(":nth-child(2 of)")


# ── AC-7: NthFilteredChildPseudoClass is a frozen dataclass ──────────────────

def test_nth_filtered_child_is_frozen_dataclass():
    """AC-7: NthFilteredChildPseudoClass is immutable (frozen dataclass)."""
    node = _get_first_simple(":nth-child(1 of li)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    with pytest.raises((AttributeError, TypeError)):
        node.nth = NthArgument(a=0, b=99)  # type: ignore[misc]


def test_nth_filtered_child_frozen_filter_field():
    """AC-7 detail: the filter field is also immutable."""
    node = _get_first_simple(":nth-child(1 of li)")
    with pytest.raises((AttributeError, TypeError)):
        node.filter = None  # type: ignore[assignment]


# ── Additional robustness tests ───────────────────────────────────────────────

def test_nth_child_odd_of_li():
    """parse(':nth-child(odd of li)') produces NthFilteredChildPseudoClass."""
    node = _get_first_simple(":nth-child(odd of li)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    assert node.nth == NthArgument(a=2, b=1)


def test_nth_child_negative_n_of_selector():
    """parse(':nth-child(-n+3 of .highlight)') parses correctly."""
    node = _get_first_simple(":nth-child(-n+3 of .highlight)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    assert node.nth == NthArgument(a=-1, b=3)


def test_nth_of_type_not_affected():
    """nth-of-type is NOT extended with 'of S' — the 'of' is treated as invalid An+B."""
    # nth-of-type does not accept 'of S' per CSS Level 4; should raise SyntaxError
    # because the raw string "2 of .foo" is not valid An+B syntax
    with pytest.raises(SyntaxError):
        parse(":nth-of-type(2 of .foo)")


def test_nth_last_of_type_not_affected():
    """nth-last-of-type is NOT extended with 'of S' — same as nth-of-type."""
    with pytest.raises(SyntaxError):
        parse(":nth-last-of-type(3 of p)")


def test_nth_child_of_in_complex_selector():
    """parse('ul > li:nth-child(2 of .x)') correctly places the filtered node."""
    result = parse("ul > li:nth-child(2 of .x)")
    # ul > li:nth-child(2 of .x)
    # ComplexSelector with two parts: ul, > li:nth-child(2 of .x)
    assert len(result.selectors[0].parts) == 2
    li_compound = result.selectors[0].parts[1][1]
    # li compound has TypeSelector('li') + NthFilteredChildPseudoClass
    assert len(li_compound.simple_selectors) == 2
    node = li_compound.simple_selectors[1]
    assert isinstance(node, NthFilteredChildPseudoClass)
    assert node.nth == NthArgument(a=0, b=2)


def test_nth_child_of_in_selector_list():
    """parse('.a:nth-child(1 of .x), .b') produces two complex selectors."""
    result = parse(".a:nth-child(1 of .x), .b")
    assert len(result.selectors) == 2
    # First: .a:nth-child(1 of .x)
    compound = result.selectors[0].parts[0][1]
    node = compound.simple_selectors[1]
    assert isinstance(node, NthFilteredChildPseudoClass)
    # Second: .b
    compound2 = result.selectors[1].parts[0][1]
    assert compound2.simple_selectors[0] == ClassSelector(class_name="b")


def test_nth_last_child_even_of_selector():
    """:nth-last-child(even of p) produces reverse=True, nth=NthArgument(a=2, b=0)."""
    node = _get_first_simple(":nth-last-child(even of p)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    assert node.nth == NthArgument(a=2, b=0)
    assert node.reverse is True


def test_nth_filtered_child_equality():
    """Two NthFilteredChildPseudoClass nodes with same fields are equal (frozen dataclass)."""
    node1 = _get_first_simple(":nth-child(2 of .foo)")
    node2 = _get_first_simple(":nth-child(2 of .foo)")
    assert node1 == node2


def test_nth_child_of_id_selector_filter():
    """:nth-child(2 of #main) — filter uses IDSelector."""
    node = _get_first_simple(":nth-child(2 of #main)")
    assert isinstance(node, NthFilteredChildPseudoClass)
    from aspose_html.css._ast import IDSelector
    filter_compound = node.filter.selectors[0].parts[0][1]
    assert filter_compound.simple_selectors[0] == IDSelector(id_value="main")


# ============================================================================
#  Group B — Matcher and Specificity ( / )
# ============================================================================


def _make_ul_doc():
    """Return an HTMLDocument with <ul><li class='x'>A</li><li>B</li><li class='x'>C</li></ul>."""
    from aspose_html import HTMLDocument
    return HTMLDocument.parse(
        "<ul><li class='x'>A</li><li>B</li><li class='x'>C</li></ul>"
    )


# ── AC-1: select(ul, 'li:nth-child(1 of .x)') returns [A-element] ────────────

def test_nth_child_of_class_filter_first():
    """AC-1: :nth-child(1 of .x) selects the first .x sibling (A)."""
    from aspose_html.css import select
    doc = _make_ul_doc()
    ul = doc.query_selector("ul")
    result = select(ul, "li:nth-child(1 of .x)")
    assert len(result) == 1
    assert result[0].text_content == "A"


# ── AC-2: select(ul, 'li:nth-child(2 of .x)') returns [C-element] ────────────

def test_nth_child_of_class_filter_second():
    """AC-2: :nth-child(2 of .x) selects the second .x sibling (C)."""
    from aspose_html.css import select
    doc = _make_ul_doc()
    ul = doc.query_selector("ul")
    result = select(ul, "li:nth-child(2 of .x)")
    assert len(result) == 1
    assert result[0].text_content == "C"


# ── AC-3: select(ul, 'li:nth-last-child(1 of .x)') returns [C-element] ───────

def test_nth_last_child_of_class_filter():
    """AC-3: :nth-last-child(1 of .x) selects the last .x sibling (C)."""
    from aspose_html.css import select
    doc = _make_ul_doc()
    ul = doc.query_selector("ul")
    result = select(ul, "li:nth-last-child(1 of .x)")
    assert len(result) == 1
    assert result[0].text_content == "C"


# ── AC-4: ':nth-child(odd of li)' returns odd-positioned li siblings ──────────

def test_nth_child_odd_of_li():
    """AC-4: :nth-child(odd of li) returns odd-positioned li elements (A, C)."""
    from aspose_html import HTMLDocument
    from aspose_html.css import select
    doc = HTMLDocument.parse("<ul><li>A</li><li>B</li><li>C</li><li>D</li></ul>")
    ul = doc.query_selector("ul")
    result = select(ul, "li:nth-child(odd of li)")
    texts = [el.text_content for el in result]
    assert texts == ["A", "C"]


# ── AC-5: specificity of ':nth-child(2 of .foo)' is (0, 2, 0) ────────────────

def test_specificity_nth_child_of_class():
    """AC-5: specificity(':nth-child(2 of .foo)') == (0, 2, 0)."""
    from aspose_html.css._parser import parse
    from aspose_html.css._specificity import specificity
    sel = parse(":nth-child(2 of .foo)").selectors[0]
    assert specificity(sel) == (0, 2, 0)


# ── AC-6: specificity of ':nth-child(2 of #id)' is (1, 1, 0) ────────────────

def test_specificity_nth_child_of_id():
    """AC-6: specificity(':nth-child(2 of #id)') == (1, 1, 0)."""
    from aspose_html.css._parser import parse
    from aspose_html.css._specificity import specificity
    sel = parse(":nth-child(2 of #id)").selectors[0]
    assert specificity(sel) == (1, 1, 0)


# ── AC-7: specificity of ':nth-child(2 of p.item)' is (0, 2, 1) ─────────────

def test_specificity_nth_child_of_type_and_class():
    """AC-7: specificity(':nth-child(2 of p.item)') == (0, 2, 1)."""
    from aspose_html.css._parser import parse
    from aspose_html.css._specificity import specificity
    sel = parse(":nth-child(2 of p.item)").selectors[0]
    assert specificity(sel) == (0, 2, 1)


# ── AC-8: existing ':nth-child(2)' matching unchanged ────────────────────────

def test_plain_nth_child_matching_unchanged():
    """AC-8: :nth-child(2) without 'of S' still selects second child (B)."""
    from aspose_html import HTMLDocument
    from aspose_html.css import select
    doc = HTMLDocument.parse("<ul><li>A</li><li>B</li><li>C</li></ul>")
    ul = doc.query_selector("ul")
    result = select(ul, "li:nth-child(2)")
    assert len(result) == 1
    assert result[0].text_content == "B"


# ── AC-9: existing ':nth-of-type(2)' matching unchanged ──────────────────────

def test_nth_of_type_unchanged():
    """AC-9: :nth-of-type(2) without 'of S' still selects second of its type (P2)."""
    from aspose_html import HTMLDocument
    from aspose_html.css import select
    doc = HTMLDocument.parse("<div><p>P1</p><span>S1</span><p>P2</p></div>")
    div = doc.query_selector("div")
    result = select(div, "p:nth-of-type(2)")
    assert len(result) == 1
    assert result[0].text_content == "P2"


# ── Additional matcher edge-case tests ───────────────────────────────────────

def test_nth_child_of_filter_no_match_element():
    """Element not matching its own filter S returns False — does not match."""
    from aspose_html import HTMLDocument
    from aspose_html.css import select
    # <li> without class .x; :nth-child(1 of .x) must not select it
    doc = HTMLDocument.parse("<ul><li>A</li><li class='x'>B</li></ul>")
    ul = doc.query_selector("ul")
    result = select(ul, "li:nth-child(1 of .x)")
    # Only B (2nd child overall) matches .x and is 1st in filtered set
    assert len(result) == 1
    assert result[0].text_content == "B"


def test_nth_last_child_of_filter_multiple():
    """:nth-last-child(2 of .x) selects the second-to-last .x element."""
    from aspose_html import HTMLDocument
    from aspose_html.css import select
    doc = HTMLDocument.parse(
        "<ul>"
        "<li class='x'>A</li>"
        "<li>B</li>"
        "<li class='x'>C</li>"
        "<li class='x'>D</li>"
        "</ul>"
    )
    ul = doc.query_selector("ul")
    # Filtered set (by .x) from start: [A, C, D]; from end idx 1=D, 2=C
    result = select(ul, "li:nth-last-child(2 of .x)")
    assert len(result) == 1
    assert result[0].text_content == "C"


def test_nth_child_of_with_type_filter():
    """:nth-child(2 of p) selects the second <p> among element siblings."""
    from aspose_html import HTMLDocument
    from aspose_html.css import select
    doc = HTMLDocument.parse("<div><p>P1</p><span>S1</span><p>P2</p><p>P3</p></div>")
    div = doc.query_selector("div")
    result = select(div, "p:nth-child(2 of p)")
    assert len(result) == 1
    assert result[0].text_content == "P2"


def test_nth_child_of_empty_filtered_set_no_match():
    """When no siblings match filter S, no element matches."""
    from aspose_html import HTMLDocument
    from aspose_html.css import select
    # No .missing class anywhere
    doc = HTMLDocument.parse("<ul><li>A</li><li>B</li></ul>")
    ul = doc.query_selector("ul")
    result = select(ul, "li:nth-child(1 of .missing)")
    assert result == []
