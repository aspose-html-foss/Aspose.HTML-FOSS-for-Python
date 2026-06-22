"""CSS Selector specificity calculation.

Implements the specificity algorithm from CSS Selectors Level 3 §11 /
Level 4 §16. Returns a 3-tuple (a, b, c) where:

  a — count of ID selectors
  b — count of class, attribute, and pseudo-class selectors
      (:not() itself is not counted; its argument's specificity is counted)
  c — count of type selectors and pseudo-elements (pseudo-elements not
      implemented in Level 3 parser, so always 0 from pseudo-elements)

See ADR-007 §9 and INV-006 (no invented behaviour).
"""
from __future__ import annotations

from ._ast import (
    ComplexSelector,
    CompoundSelector,
    SelectorList,
    SimpleSelector,
    UniversalSelector,
    TypeSelector,
    ClassSelector,
    IDSelector,
    AttributeSelector,
    PseudoClassSelector,
    NthArgument,
    HasPseudoClass,
    IsPseudoClass,
    WherePseudoClass,
    ComplexNotPseudoClass,
    NthFilteredChildPseudoClass,
)


def _specificity_of_simple(
    sel: (
        "SimpleSelector | HasPseudoClass | IsPseudoClass | WherePseudoClass"
        " | ComplexNotPseudoClass | NthFilteredChildPseudoClass"
    ),
) -> tuple[int, int, int]:
    """Return (a, b, c) specificity contribution of a single simple selector.

    Handles Level 3 simple selectors and the Level 4 pseudo-class nodes added
    in ADR-042. Specificity rules follow CSS Selectors Level 4 §16:

    - :is() and :not() — max specificity of the argument selectors.
    - :where() — always (0, 0, 0).
    - :has() — max specificity across all relative-selector arguments.
    """
    if isinstance(sel, UniversalSelector):
        return (0, 0, 0)
    if isinstance(sel, TypeSelector):
        return (0, 0, 1)
    if isinstance(sel, IDSelector):
        return (1, 0, 0)
    if isinstance(sel, (ClassSelector, AttributeSelector)):
        return (0, 1, 0)
    if isinstance(sel, PseudoClassSelector):
        if sel.name == "not":
            # Level-3 :not() path — kept for cached AST backward-compat (ADR-042)
            # :not() itself is not counted; the argument's specificity is counted
            if sel.argument is not None and not isinstance(sel.argument, (NthArgument, str)):
                # argument is a SimpleSelector
                return _specificity_of_simple(sel.argument)  # type: ignore[arg-type]
            return (0, 0, 0)
        # All other pseudo-classes contribute b += 1
        return (0, 1, 0)

    # ── Level 4 pseudo-class specificity (ADR-042) ────────────────────────────

    if isinstance(sel, IsPseudoClass):
        # INV-006: specificity = max across all argument selectors (Level 4 §16)
        return max_specificity(sel.selector_list)

    if isinstance(sel, WherePseudoClass):
        # INV-006: :where() always contributes zero specificity (Level 4 §16)
        return (0, 0, 0)

    if isinstance(sel, ComplexNotPseudoClass):
        # INV-006: specificity = max of argument selectors (Level 4 §16)
        return max_specificity(sel.selector_list)

    if isinstance(sel, HasPseudoClass):
        # INV-006: specificity = max over all relative-selector arguments (Level 4 §16)
        all_specs = [
            max_specificity(inner_sl)
            for _comb, inner_sl in sel.relative_selectors
        ]
        return max(all_specs, default=(0, 0, 0))

    if isinstance(sel, NthFilteredChildPseudoClass):
        # INV-006: pseudo-class contributes (0, 1, 0) + max specificity of the
        # 'of S' filter selector list (CSS Selectors Level 4 §16). See ADR-214.
        ma, mb, mc = max_specificity(sel.filter)
        return (ma, mb + 1, mc)

    return (0, 0, 0)


def _specificity_of_compound(compound: CompoundSelector) -> tuple[int, int, int]:
    """Sum specificity over all simple selectors in a compound selector."""
    a = b = c = 0
    for sel in compound.simple_selectors:
        da, db, dc = _specificity_of_simple(sel)
        a += da
        b += db
        c += dc
    return (a, b, c)


def specificity(selector: ComplexSelector) -> tuple[int, int, int]:
    """Return the (a, b, c) specificity of a single complex selector.

    a counts ID simple selectors.
    b counts class, attribute, and pseudo-class simple selectors.
      Exception: :not() is not counted; its argument's specificity is counted.
    c counts type selectors. Universal selector contributes 0 to all.

    Parameters
    ----------
    selector : ComplexSelector
        A single parsed complex selector (one entry from SelectorList.selectors).

    Returns
    -------
    tuple[int, int, int]
        The (a, b, c) specificity triple.

    Examples
    --------
    >>> # (tested via named tests in tests/test_css/test_specificity.py)
    """
    a = b = c = 0
    for _combinator, compound in selector.parts:
        da, db, dc = _specificity_of_compound(compound)
        a += da
        b += db
        c += dc
    return (a, b, c)


def max_specificity(selector_list: SelectorList) -> tuple[int, int, int]:
    """Return the highest specificity among all selectors in a SelectorList.

    Parameters
    ----------
    selector_list : SelectorList
        A parsed selector list (root AST node from parse()).

    Returns
    -------
    tuple[int, int, int]
        The maximum (a, b, c) specificity triple across all selectors.
    """
    return max(
        (specificity(sel) for sel in selector_list.selectors),
        default=(0, 0, 0),
    )
