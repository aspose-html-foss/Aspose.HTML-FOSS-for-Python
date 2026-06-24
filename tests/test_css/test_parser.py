"""Tests for the CSS Selector Level 3 parser ().

Covers all acceptance criteria AC-P1 through AC-P23 from .
These tests depend only on  and do not require  (matcher).

Run with:
    PYTHONPATH=src python -m pytest tests/test_css/test_parser.py -q
"""
import pytest

from aspose_html.css._parser import parse, _parse_nth_argument
from aspose_html.css._ast import (
    SelectorList,
    ComplexSelector,
    CompoundSelector,
    SimpleSelector,
    UniversalSelector,
    TypeSelector,
    ClassSelector,
    IDSelector,
    AttributeSelector,
    AttributeOperator,
    NthArgument,
    PseudoClassSelector,
    Combinator,
    ComplexNotPseudoClass,
)


# ── Helper ──────────────────────────────────────────────────────────────────

def _first_compound(selector_str: str) -> CompoundSelector:
    """Return the first CompoundSelector from parsing selector_str."""
    result = parse(selector_str)
    return result.selectors[0].parts[0][1]


def _first_simple(selector_str: str) -> SimpleSelector:
    """Return the first simple selector from the first compound selector."""
    return _first_compound(selector_str).simple_selectors[0]


# ── AC-P1: Type selector ────────────────────────────────────────────────────

def test_parse_type_selector() -> None:
    """AC-P1: parse('div') produces TypeSelector(tag_name='div')."""
    result = parse("div")
    assert isinstance(result, SelectorList)
    assert len(result.selectors) == 1
    complex_sel = result.selectors[0]
    assert isinstance(complex_sel, ComplexSelector)
    assert len(complex_sel.parts) == 1
    combinator, compound = complex_sel.parts[0]
    assert combinator is None
    assert isinstance(compound, CompoundSelector)
    assert len(compound.simple_selectors) == 1
    ts = compound.simple_selectors[0]
    assert isinstance(ts, TypeSelector)
    assert ts.tag_name == "div"


# ── AC-P2: Universal selector ───────────────────────────────────────────────

def test_parse_universal_selector() -> None:
    """AC-P2: parse('*') produces CompoundSelector containing UniversalSelector()."""
    compound = _first_compound("*")
    assert len(compound.simple_selectors) == 1
    assert isinstance(compound.simple_selectors[0], UniversalSelector)


# ── AC-P3: Class selector ────────────────────────────────────────────────────

def test_parse_class_selector() -> None:
    """AC-P3: parse('.box') produces ClassSelector(class_name='box')."""
    simple = _first_simple(".box")
    assert isinstance(simple, ClassSelector)
    assert simple.class_name == "box"


# ── AC-P4: ID selector ───────────────────────────────────────────────────────

def test_parse_id_selector() -> None:
    """AC-P4: parse('#main') produces IDSelector(id_value='main')."""
    simple = _first_simple("#main")
    assert isinstance(simple, IDSelector)
    assert simple.id_value == "main"


# ── AC-P5: Compound selector ─────────────────────────────────────────────────

def test_parse_compound_selector() -> None:
    """AC-P5: parse('div.box#main') produces TypeSelector, ClassSelector, IDSelector."""
    compound = _first_compound("div.box#main")
    assert len(compound.simple_selectors) == 3
    assert isinstance(compound.simple_selectors[0], TypeSelector)
    assert compound.simple_selectors[0].tag_name == "div"
    assert isinstance(compound.simple_selectors[1], ClassSelector)
    assert compound.simple_selectors[1].class_name == "box"
    assert isinstance(compound.simple_selectors[2], IDSelector)
    assert compound.simple_selectors[2].id_value == "main"


# ── AC-P6: Child combinator ──────────────────────────────────────────────────

def test_parse_child_combinator() -> None:
    """AC-P6: parse('ul > li') produces ComplexSelector with Combinator.CHILD."""
    result = parse("ul > li")
    complex_sel = result.selectors[0]
    assert len(complex_sel.parts) == 2
    combinator_1, compound_1 = complex_sel.parts[0]
    combinator_2, compound_2 = complex_sel.parts[1]
    assert combinator_1 is None
    assert isinstance(compound_1.simple_selectors[0], TypeSelector)
    assert compound_1.simple_selectors[0].tag_name == "ul"
    assert combinator_2 == Combinator.CHILD
    assert isinstance(compound_2.simple_selectors[0], TypeSelector)
    assert compound_2.simple_selectors[0].tag_name == "li"


# ── AC-P7: Descendant combinator ─────────────────────────────────────────────

def test_parse_descendant_combinator() -> None:
    """AC-P7: parse('div span') produces ComplexSelector with Combinator.DESCENDANT."""
    result = parse("div span")
    complex_sel = result.selectors[0]
    assert len(complex_sel.parts) == 2
    assert complex_sel.parts[1][0] == Combinator.DESCENDANT
    assert complex_sel.parts[1][1].simple_selectors[0] == TypeSelector("span")


# ── AC-P8: Adjacent sibling combinator ──────────────────────────────────────

def test_parse_adjacent_combinator() -> None:
    """AC-P8: parse('h1 + p') produces Combinator.ADJACENT."""
    result = parse("h1 + p")
    assert result.selectors[0].parts[1][0] == Combinator.ADJACENT


# ── AC-P9: General sibling combinator ───────────────────────────────────────

def test_parse_sibling_combinator() -> None:
    """AC-P9: parse('h1 ~ p') produces Combinator.SIBLING."""
    result = parse("h1 ~ p")
    assert result.selectors[0].parts[1][0] == Combinator.SIBLING


# ── AC-P10: Attribute selectors — all operators ──────────────────────────────

def test_parse_attribute_selectors() -> None:
    """AC-P10: All attribute operators and the case-insensitive flag."""
    # EXISTS
    a = _first_simple("[href]")
    assert isinstance(a, AttributeSelector)
    assert a.attr_name == "href"
    assert a.operator == AttributeOperator.EXISTS
    assert a.value is None
    assert a.case_insensitive is False

    # EQUALS
    a = _first_simple("[class=active]")
    assert a.operator == AttributeOperator.EQUALS
    assert a.value == "active"

    # WORD
    a = _first_simple("[class~=active]")
    assert a.operator == AttributeOperator.WORD
    assert a.value == "active"

    # DASHMATCH
    a = _first_simple("[lang|=en]")
    assert a.operator == AttributeOperator.DASHMATCH
    assert a.value == "en"

    # PREFIX
    a = _first_simple("[href^=https]")
    assert a.operator == AttributeOperator.PREFIX
    assert a.value == "https"

    # SUFFIX
    a = _first_simple("[href$=pdf]")
    assert a.operator == AttributeOperator.SUFFIX
    assert a.value == "pdf"

    # SUBSTRING
    a = _first_simple("[title*=hello]")
    assert a.operator == AttributeOperator.SUBSTRING
    assert a.value == "hello"

    # Case-insensitive flag
    a = _first_simple("[attr=val i]")
    assert a.operator == AttributeOperator.EQUALS
    assert a.value == "val"
    assert a.case_insensitive is True


# ── AC-P11: Structural pseudo-classes (no argument) ──────────────────────────

def test_parse_structural_pseudo_classes() -> None:
    """AC-P11: All no-argument structural pseudo-classes."""
    no_arg_pseudos = [
        "root", "empty", "first-child", "last-child", "only-child",
        "first-of-type", "last-of-type", "only-of-type",
    ]
    for name in no_arg_pseudos:
        result = parse(f":{name}")
        pseudo = _first_simple(f":{name}")
        assert isinstance(pseudo, PseudoClassSelector), f":{name} should be PseudoClassSelector"
        assert pseudo.name == name, f"name mismatch for :{name}"
        assert pseudo.argument is None, f":{name} should have no argument"


# ── AC-P12: :nth-child and An+B micro-syntax ─────────────────────────────────

def test_parse_nth_argument() -> None:
    """AC-P12: An+B micro-syntax parsing via :nth-child."""
    def nth(sel_str: str) -> NthArgument:
        pseudo = _first_simple(sel_str)
        assert isinstance(pseudo, PseudoClassSelector)
        assert isinstance(pseudo.argument, NthArgument)
        return pseudo.argument

    assert nth(":nth-child(2n+1)") == NthArgument(a=2, b=1)
    assert nth(":nth-child(even)") == NthArgument(a=2, b=0)
    assert nth(":nth-child(odd)") == NthArgument(a=2, b=1)
    assert nth(":nth-child(3)") == NthArgument(a=0, b=3)
    assert nth(":nth-child(-n+3)") == NthArgument(a=-1, b=3)
    assert nth(":nth-child(n)") == NthArgument(a=1, b=0)
    assert nth(":nth-child(-n)") == NthArgument(a=-1, b=0)
    assert nth(":nth-child(2n)") == NthArgument(a=2, b=0)
    assert nth(":nth-child(2n-1)") == NthArgument(a=2, b=-1)
    assert nth(":nth-child(-3)") == NthArgument(a=0, b=-3)

    # Spaces around + are permitted by CSS spec
    assert nth(":nth-child(2n + 1)") == NthArgument(a=2, b=1)

    # All four nth pseudo-classes
    for name in ("nth-child", "nth-last-child", "nth-of-type", "nth-last-of-type"):
        pseudo = _first_simple(f":{name}(2n+1)")
        assert isinstance(pseudo, PseudoClassSelector)
        assert pseudo.name == name
        assert pseudo.argument == NthArgument(a=2, b=1)


# ── AC-P13: :not() pseudo-class ──────────────────────────────────────────────

def test_parse_not_pseudo_class() -> None:
    """AC-P13 (updated for  Level 4): :not() now produces ComplexNotPseudoClass.

    The parser now produces ComplexNotPseudoClass for all :not() forms, including
    single-selector arguments. This is the Level 4 upgrade from .
    """
    # Single type selector — Level 4 form still works
    pseudo = _first_simple(":not(p)")
    assert isinstance(pseudo, ComplexNotPseudoClass)
    # The inner selector list has one complex selector with TypeSelector("p")
    inner_compound = pseudo.selector_list.selectors[0].parts[0][1]
    assert isinstance(inner_compound.simple_selectors[0], TypeSelector)
    assert inner_compound.simple_selectors[0].tag_name == "p"

    pseudo2 = _first_simple(":not(.active)")
    assert isinstance(pseudo2, ComplexNotPseudoClass)
    inner2 = pseudo2.selector_list.selectors[0].parts[0][1]
    assert isinstance(inner2.simple_selectors[0], ClassSelector)
    assert inner2.simple_selectors[0].class_name == "active"

    # :not(*) — universal selector argument
    pseudo3 = _first_simple(":not(*)")
    assert isinstance(pseudo3, ComplexNotPseudoClass)
    inner3 = pseudo3.selector_list.selectors[0].parts[0][1]
    assert isinstance(inner3.simple_selectors[0], UniversalSelector)

    # :not([href]) — attribute selector argument
    pseudo4 = _first_simple(":not([href])")
    assert isinstance(pseudo4, ComplexNotPseudoClass)
    inner4 = pseudo4.selector_list.selectors[0].parts[0][1]
    assert isinstance(inner4.simple_selectors[0], AttributeSelector)

    # :not(#id) — ID selector argument
    pseudo5 = _first_simple(":not(#foo)")
    assert isinstance(pseudo5, ComplexNotPseudoClass)
    inner5 = pseudo5.selector_list.selectors[0].parts[0][1]
    assert isinstance(inner5.simple_selectors[0], IDSelector)
    assert inner5.simple_selectors[0].id_value == "foo"

    # Level 4 extension: :not() now accepts selector lists
    pseudo6 = _first_simple(":not(p, div)")
    assert isinstance(pseudo6, ComplexNotPseudoClass)
    assert len(pseudo6.selector_list.selectors) == 2


# ── AC-P14: :lang() pseudo-class ─────────────────────────────────────────────

def test_parse_lang_pseudo_class() -> None:
    """AC-P14: :lang(en) -> PseudoClassSelector(name='lang', argument='en')."""
    pseudo = _first_simple(":lang(en)")
    assert isinstance(pseudo, PseudoClassSelector)
    assert pseudo.name == "lang"
    assert pseudo.argument == "en"

    # Quoted language range
    pseudo2 = _first_simple(":lang('zh-TW')")
    assert pseudo2.argument == "zh-TW"


# ── AC-P15: Link pseudo-classes ──────────────────────────────────────────────

def test_parse_link_pseudo_classes() -> None:
    """AC-P15: :link, :visited, :any-link."""
    for name in ("link", "visited", "any-link"):
        pseudo = _first_simple(f":{name}")
        assert isinstance(pseudo, PseudoClassSelector)
        assert pseudo.name == name
        assert pseudo.argument is None


# ── AC-P16: Selector list (comma-separated) ───────────────────────────────────

def test_parse_selector_list() -> None:
    """AC-P16: parse('div, span, p') -> SelectorList with three ComplexSelector entries."""
    result = parse("div, span, p")
    assert isinstance(result, SelectorList)
    assert len(result.selectors) == 3
    tags = [
        s.parts[0][1].simple_selectors[0].tag_name  # type: ignore[union-attr]
        for s in result.selectors
    ]
    assert tags == ["div", "span", "p"]


# ── AC-P17: Type selector lowercased at parse time ───────────────────────────

def test_type_selector_case_normalization() -> None:
    """AC-P17: parse('DIV') and parse('div') both produce TypeSelector(tag_name='div')."""
    assert _first_simple("DIV") == TypeSelector(tag_name="div")
    assert _first_simple("div") == TypeSelector(tag_name="div")
    assert _first_simple("Div") == TypeSelector(tag_name="div")


# ── AC-P18: Invalid selectors raise SyntaxError ──────────────────────────────

def test_syntax_error_on_invalid_selector() -> None:
    """AC-P18: Completely malformed selectors raise SyntaxError."""
    with pytest.raises(SyntaxError):
        parse("!!!")

    with pytest.raises(SyntaxError):
        parse("")

    with pytest.raises(SyntaxError):
        parse("   ")

    with pytest.raises(SyntaxError):
        parse("div >")  # trailing combinator

    with pytest.raises(SyntaxError):
        parse("div >   ")  # trailing combinator with trailing whitespace

    with pytest.raises(SyntaxError):
        parse("[attr")  # no closing bracket

    with pytest.raises(SyntaxError):
        parse(":nth-child()")  # empty An+B argument

    # NOTE: :not(p, div) is now VALID (Level 4 complex :not from ).
    # The old Level-3-only restriction is intentionally removed.


# ── AC-P19: Out-of-scope dynamic pseudo-classes raise NotImplementedError ─────

def test_dynamic_pseudo_class_contract_split() -> None:
    """AC-P19 (updated): selected stateful pseudos parse; remaining dynamic stay OOS."""
    #  / : valid in headless mode (deterministic no-match at matcher).
    for name in (":hover", ":focus", ":active", ":focus-visible"):
        result = parse(name)
        assert isinstance(result, SelectorList)

    #  / : :checked is now parsed and delegated to matcher
    # semantics.
    result_checked = parse(":checked")
    assert isinstance(result_checked, SelectorList)

    #  / : now parsed and delegated to matcher semantics.
    for name in (":disabled", ":enabled"):
        result = parse(name)
        assert isinstance(result, SelectorList)


# ── AC-P20: Level 4 pseudo-classes are now IMPLEMENTED () ─────────────

def test_not_implemented_for_level4_pseudo_classes() -> None:
    """AC-P20 (updated for ): :is(), :has(), :where() are now implemented.

    These no longer raise NotImplementedError. This test verifies they parse
    successfully and produce the correct Level 4 AST nodes.
    """
    from aspose_html.css._ast import IsPseudoClass, HasPseudoClass, WherePseudoClass

    # :is() now produces IsPseudoClass
    result_is = _first_simple(":is(div)")
    assert isinstance(result_is, IsPseudoClass)

    # :has() now produces HasPseudoClass
    result_has = _first_simple(":has(span)")
    assert isinstance(result_has, HasPseudoClass)

    # :where() now produces WherePseudoClass
    result_where = _first_simple(":where(p)")
    assert isinstance(result_where, WherePseudoClass)


# ── AC-P21: Pseudo-elements raise NotImplementedError ────────────────────────

def test_not_implemented_for_pseudo_elements() -> None:
    """AC-P21: ::before and :before (legacy) raise NotImplementedError."""
    with pytest.raises(NotImplementedError):
        parse("::before")
    with pytest.raises(NotImplementedError):
        parse(":before")
    with pytest.raises(NotImplementedError):
        parse("::after")
    with pytest.raises(NotImplementedError):
        parse(":after")
    with pytest.raises(NotImplementedError):
        parse("::first-line")
    with pytest.raises(NotImplementedError):
        parse("::first-letter")


# ── AC-P22: Forgiving selector list skips invalid entries ────────────────────

def test_forgiving_selector_list() -> None:
    """AC-P22: parse('div, !!!, span', forgiving=True) returns div and span."""
    result = parse("div, !!!, span", forgiving=True)
    assert len(result.selectors) == 2
    tags = [
        s.parts[0][1].simple_selectors[0].tag_name  # type: ignore[union-attr]
        for s in result.selectors
    ]
    assert "div" in tags
    assert "span" in tags


# ── AC-P23: Forgiving=True raises SyntaxError when all entries fail ───────────

def test_forgiving_all_fail_raises() -> None:
    """AC-P23: parse('!!!, ???', forgiving=True) raises SyntaxError."""
    with pytest.raises(SyntaxError):
        parse("!!!, ???", forgiving=True)


# ── Edge cases (from  Test Strategy) ──────────────────────────────────

def test_selector_with_only_whitespace_raises() -> None:
    """Whitespace-only selector string raises SyntaxError."""
    with pytest.raises(SyntaxError):
        parse("   \t\n")


def test_attribute_selector_quoted_value() -> None:
    """[attr='val'] and [attr="val"] are both valid."""
    a1 = _first_simple("[class='foo bar']")
    assert isinstance(a1, AttributeSelector)
    assert a1.value == "foo bar"

    a2 = _first_simple('[class="foo bar"]')
    assert isinstance(a2, AttributeSelector)
    assert a2.value == "foo bar"


def test_attribute_selector_unquoted_value() -> None:
    """[attr=val] with unquoted value is valid."""
    a = _first_simple("[type=text]")
    assert isinstance(a, AttributeSelector)
    assert a.value == "text"
    assert a.operator == AttributeOperator.EQUALS


def test_unicode_class_name() -> None:
    """Unicode identifiers in class names and IDs are valid."""
    pseudo = _first_simple(".mödule")
    assert isinstance(pseudo, ClassSelector)
    assert pseudo.class_name == "mödule"

    id_sel = _first_simple("#héros")
    assert isinstance(id_sel, IDSelector)
    assert id_sel.id_value == "héros"


def test_combinator_with_surrounding_whitespace() -> None:
    """Whitespace around explicit combinators is stripped correctly."""
    result = parse("div  >  span")
    assert result.selectors[0].parts[1][0] == Combinator.CHILD

    result2 = parse("div  +  span")
    assert result2.selectors[0].parts[1][0] == Combinator.ADJACENT

    result3 = parse("div  ~  span")
    assert result3.selectors[0].parts[1][0] == Combinator.SIBLING


def test_multiple_class_selectors() -> None:
    """div.foo.bar produces a compound selector with TypeSelector + 2 ClassSelectors."""
    compound = _first_compound("div.foo.bar")
    assert len(compound.simple_selectors) == 3
    assert isinstance(compound.simple_selectors[0], TypeSelector)
    assert isinstance(compound.simple_selectors[1], ClassSelector)
    assert compound.simple_selectors[1].class_name == "foo"
    assert isinstance(compound.simple_selectors[2], ClassSelector)
    assert compound.simple_selectors[2].class_name == "bar"


def test_deeply_nested_combinators() -> None:
    """div > ul > li.item produces a 3-part ComplexSelector."""
    result = parse("div > ul > li.item")
    parts = result.selectors[0].parts
    assert len(parts) == 3
    assert parts[0][0] is None
    assert parts[1][0] == Combinator.CHILD
    assert parts[2][0] == Combinator.CHILD
    compound_li = parts[2][1]
    assert compound_li.simple_selectors[0] == TypeSelector("li")
    assert compound_li.simple_selectors[1] == ClassSelector("item")


def test_nth_argument_direct() -> None:
    """Direct calls to _parse_nth_argument() cover edge cases."""
    assert _parse_nth_argument("even") == NthArgument(a=2, b=0)
    assert _parse_nth_argument("odd") == NthArgument(a=2, b=1)
    assert _parse_nth_argument("0") == NthArgument(a=0, b=0)
    assert _parse_nth_argument("n") == NthArgument(a=1, b=0)
    assert _parse_nth_argument("-n") == NthArgument(a=-1, b=0)
    assert _parse_nth_argument("3n") == NthArgument(a=3, b=0)
    assert _parse_nth_argument("3n+0") == NthArgument(a=3, b=0)
    assert _parse_nth_argument("3n-2") == NthArgument(a=3, b=-2)

    with pytest.raises(SyntaxError):
        _parse_nth_argument("abc")
    with pytest.raises(SyntaxError):
        _parse_nth_argument("")


def test_complex_selector_with_pseudo_and_attribute() -> None:
    """a[href]:link produces TypeSelector + AttributeSelector + PseudoClassSelector."""
    compound = _first_compound("a[href]:link")
    assert len(compound.simple_selectors) == 3
    assert compound.simple_selectors[0] == TypeSelector("a")
    assert isinstance(compound.simple_selectors[1], AttributeSelector)
    assert compound.simple_selectors[1].attr_name == "href"
    assert isinstance(compound.simple_selectors[2], PseudoClassSelector)
    assert compound.simple_selectors[2].name == "link"


def test_forgiving_parses_focus_within_as_valid_selector() -> None:
    """ : :focus-within is now a valid no-arg selector; forgiving list parses cleanly.

    Prior to , :focus-within was in _PSEUDO_DYNAMIC_OOS and raised
    NotImplementedError.  moves it to _PSEUDO_NO_ARG with deterministic
    no-match headless semantics, so it no longer raises any exception.
    """
    # :focus-within is now a valid parsed selector — no exception raised.
    result = parse("div, :focus-within, span", forgiving=True)
    # All three selectors in the list are valid.
    assert result is not None
    assert len(result.selectors) == 3


def test_ast_nodes_are_frozen() -> None:
    """All AST dataclasses are frozen (immutable)."""
    ts = TypeSelector(tag_name="div")
    with pytest.raises((TypeError, AttributeError)):
        ts.tag_name = "span"  # type: ignore[misc]

    cs = ClassSelector(class_name="foo")
    with pytest.raises((TypeError, AttributeError)):
        cs.class_name = "bar"  # type: ignore[misc]


def test_parse_returns_selector_list_type() -> None:
    """parse() always returns a SelectorList instance."""
    for sel in ("*", "div", ".cls", "#id", "[attr]", ":root", "div > span"):
        result = parse(sel)
        assert isinstance(result, SelectorList)
        assert len(result.selectors) >= 1


def test_import_css_without_matcher() -> None:
    """Importing aspose_html.css must not fail even without _matcher.py ()."""
    import aspose_html.css  # noqa: F401 — must not raise ImportError
