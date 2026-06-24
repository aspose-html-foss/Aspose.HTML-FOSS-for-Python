"""Tests for CSS specificity calculation ().

Covers AC-P24 from .
These tests depend only on  and do not require  (matcher).

Run with:
    PYTHONPATH=src python -m pytest tests/test_css/test_specificity.py -q
"""
from aspose_html.css._parser import parse
from aspose_html.css._specificity import specificity, max_specificity


def _spec(selector_str: str) -> tuple[int, int, int]:
    """Parse selector_str and return specificity of the first selector."""
    result = parse(selector_str)
    return specificity(result.selectors[0])


# ── AC-P24: Specificity calculation ──────────────────────────────────────────

def test_specificity_calculation() -> None:
    """AC-P24: Core specificity examples from ."""
    # #id .class div -> (1, 1, 1)
    assert _spec("#id .class div") == (1, 1, 1)

    # * -> (0, 0, 0)
    assert _spec("*") == (0, 0, 0)

    # .a.b.c -> (0, 3, 0)
    assert _spec(".a.b.c") == (0, 3, 0)

    # :not(p) -> (0, 0, 1)  — :not() itself is 0, argument p is (0, 0, 1)
    assert _spec(":not(p)") == (0, 0, 1)


def test_specificity_id() -> None:
    """ID selector contributes a=1."""
    assert _spec("#main") == (1, 0, 0)
    assert _spec("#a#b") == (2, 0, 0)


def test_specificity_class() -> None:
    """Class selector contributes b=1."""
    assert _spec(".foo") == (0, 1, 0)
    assert _spec(".foo.bar") == (0, 2, 0)


def test_specificity_type() -> None:
    """Type selector contributes c=1."""
    assert _spec("div") == (0, 0, 1)
    assert _spec("div span") == (0, 0, 2)


def test_specificity_universal() -> None:
    """Universal selector contributes nothing."""
    assert _spec("*") == (0, 0, 0)
    assert _spec("*.foo") == (0, 1, 0)


def test_specificity_attribute() -> None:
    """Attribute selector contributes b=1."""
    assert _spec("[href]") == (0, 1, 0)
    assert _spec("[href][title]") == (0, 2, 0)


def test_specificity_pseudo_class() -> None:
    """Pseudo-class selector contributes b=1."""
    assert _spec(":first-child") == (0, 1, 0)
    assert _spec(":nth-child(2n+1)") == (0, 1, 0)
    assert _spec(":root") == (0, 1, 0)
    assert _spec(":link") == (0, 1, 0)


def test_specificity_not_with_id() -> None:
    """:not(#id) -> (1, 0, 0) — argument ID contributes a=1."""
    assert _spec(":not(#foo)") == (1, 0, 0)


def test_specificity_not_with_class() -> None:
    """:not(.cls) -> (0, 1, 0) — argument class contributes b=1."""
    assert _spec(":not(.cls)") == (0, 1, 0)


def test_specificity_not_with_universal() -> None:
    """:not(*) -> (0, 0, 0)."""
    assert _spec(":not(*)") == (0, 0, 0)


def test_specificity_complex_compound() -> None:
    """div#main.foo[href]:first-child -> (1, 3, 1)."""
    assert _spec("div#main.foo[href]:first-child") == (1, 3, 1)


def test_specificity_combinator_sums() -> None:
    """Specificity is summed across all compounds in a complex selector."""
    # ul > li.item — ul is (0,0,1), li is (0,0,1), .item is (0,1,0)
    assert _spec("ul > li.item") == (0, 1, 2)

    # #nav a.active — #nav=(1,0,0), a=(0,0,1), .active=(0,1,0)
    assert _spec("#nav a.active") == (1, 1, 1)


def test_max_specificity() -> None:
    """max_specificity returns the highest specificity from a selector list."""
    result = parse("div, #main, .cls")
    ms = max_specificity(result)
    assert ms == (1, 0, 0)  # #main has the highest specificity


def test_max_specificity_single() -> None:
    """max_specificity on a single-entry list returns that entry's specificity."""
    result = parse(".foo")
    assert max_specificity(result) == (0, 1, 0)
