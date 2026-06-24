"""CSS Selector AST node definitions.

All nodes are immutable frozen dataclasses. This allows  to cache
compiled selectors safely. See  for design rationale.

Internal to aspose_html.css — not part of the public API.
 imports from this module; the names listed here are frozen.
"""
from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Union


# ── Combinator ────────────────────────────────────────────────────────────────

class Combinator(Enum):
    """Selector combinator types (CSS Selectors Level 3)."""

    DESCENDANT = "descendant"  # whitespace between compound selectors
    CHILD      = "child"       # >
    ADJACENT   = "adjacent"    # + (immediately following sibling)
    SIBLING    = "sibling"     # ~ (any following sibling)


# ── Simple selectors ──────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class UniversalSelector:
    """Matches any element: ``*``."""


@dataclasses.dataclass(frozen=True)
class TypeSelector:
    """Matches elements by tag name: ``div``.

    tag_name is already lowercased (HTML-mode normalisation applied at parse
    time).  compares this against Element.local_name directly.
    """

    tag_name: str  # lowercase — : HTML-mode case normalisation at parse time


@dataclasses.dataclass(frozen=True)
class ClassSelector:
    """Matches elements whose class_list contains class_name: ``.foo``."""

    class_name: str  # exact token, case-sensitive


@dataclasses.dataclass(frozen=True)
class IDSelector:
    """Matches elements whose id attribute equals id_value: ``#main``."""

    id_value: str  # case-sensitive per HTML spec


class AttributeOperator(Enum):
    """Attribute selector operator types (CSS Selectors Level 3)."""

    EXISTS    = "exists"  # [attr]
    EQUALS    = "="       # [attr=val]
    WORD      = "~="      # [attr~=val] — value is a whitespace-separated word
    DASHMATCH = "|="      # [attr|=val] — equals val or starts with val-
    PREFIX    = "^="      # [attr^=val]
    SUFFIX    = "$="      # [attr$=val]
    SUBSTRING = "*="      # [attr*=val]


@dataclasses.dataclass(frozen=True)
class AttributeSelector:
    """Matches elements by attribute presence or value.

    attr_name: lowercased (attribute names are case-insensitive in HTML mode).
    value: None when operator is EXISTS. Otherwise the literal match value.
    case_insensitive: True when the optional ``i`` flag is present.
    """

    attr_name: str
    operator: AttributeOperator
    value: str | None
    case_insensitive: bool = False


@dataclasses.dataclass(frozen=True)
class NthArgument:
    """Parsed An+B argument for :nth-child and related pseudo-classes.

    a and b are integers; the formula is ``a*n + b`` (n >= 0).

    Examples::

        even      -> NthArgument(a=2, b=0)
        odd       -> NthArgument(a=2, b=1)
        3         -> NthArgument(a=0, b=3)
        2n+1      -> NthArgument(a=2, b=1)
        -n+3      -> NthArgument(a=-1, b=3)
    """

    a: int
    b: int


@dataclasses.dataclass(frozen=True)
class PseudoClassSelector:
    """A pseudo-class selector.

    name: the pseudo-class name without the leading colon, lowercase.
          E.g. ``"first-child"``, ``"nth-child"``, ``"not"``, ``"lang"``.
    argument: present only for functional pseudo-classes:

      - :nth-child, :nth-last-child, :nth-of-type, :nth-last-of-type ->
        NthArgument instance.
      - :not(simple-selector) -> a single SimpleSelector instance.
      - :lang(range) -> the language range string.
      - non-functional -> None.
    """

    name: str
    argument: "NthArgument | SimpleSelector | str | None" = None


# Union type for all simple selector variants.
# Used in CompoundSelector.simple_selectors and as :not() argument type.
# Frozen for compatibility — update dependent code before changing members.
SimpleSelector = Union[
    UniversalSelector,
    TypeSelector,
    ClassSelector,
    IDSelector,
    AttributeSelector,
    PseudoClassSelector,
]


# ── CSS Selectors Level 4 pseudo-class AST nodes ──────────────────────────────
# Added in  / . These are additive frozen dataclasses that do NOT
# join the SimpleSelector union (frozen per project_memory.md). They appear in
# CompoundSelector.simple_selectors via a widened type annotation.

@dataclasses.dataclass(frozen=True)
class HasPseudoClass:
    """Matches elements that have at least one relative match in their subtree.

    Represents ``:has(relative-selector-list)`` (CSS Selectors Level 4 §4.6).

    ``relative_selectors`` is a tuple of ``(leading_combinator, inner_selector_list)``
    pairs.  ``leading_combinator`` is ``None`` for an implicit descendant
    relationship, ``Combinator.CHILD`` for ``>``, ``Combinator.ADJACENT`` for
    ``+``, and ``Combinator.SIBLING`` for ``~``.

    Specificity equals the highest specificity among all argument selectors
    (Level 4 §16). See .
    """

    relative_selectors: "tuple[tuple[Combinator | None, SelectorList], ...]"


@dataclasses.dataclass(frozen=True)
class IsPseudoClass:
    """Matches elements that match any selector in a forgiving selector list.

    Represents ``:is(selector-list)`` (CSS Selectors Level 4 §4.4).

    Invalid selectors in the list are silently dropped at parse time (forgiving
    parsing). Specificity equals the highest-specificity matching argument
    (Level 4 §16). See .
    """

    selector_list: "SelectorList"


@dataclasses.dataclass(frozen=True)
class WherePseudoClass:
    """Identical matching semantics to IsPseudoClass; always contributes 0 specificity.

    Represents ``:where(selector-list)`` (CSS Selectors Level 4 §4.7).

    Uses the same forgiving parsing as :is(). Specificity is always (0, 0, 0)
    regardless of the specificity of the argument selectors (Level 4 §16).
    See .
    """

    selector_list: "SelectorList"


@dataclasses.dataclass(frozen=True)
class ComplexNotPseudoClass:
    """Matches elements that do NOT match any selector in the argument list.

    Represents Level 4 ``:not(selector-list)`` (CSS Selectors Level 4 §4.5).

    Unlike the Level 3 ``:not()`` (which accepted only a single simple selector),
    this node accepts a full selector list. Parsing is NOT forgiving — any
    invalid argument raises ``SyntaxError``. Specificity equals the most
    specific argument (Level 4 §16). See .
    """

    selector_list: "SelectorList"


@dataclasses.dataclass(frozen=True)
class NthFilteredChildPseudoClass:
    """Matches elements at An+B position among siblings filtered by a selector.

    Represents ``:nth-child(An+B of S)`` and ``:nth-last-child(An+B of S)``
    (CSS Selectors Level 4 §8.3 / §8.4).

    ``nth`` is the An+B argument; ``filter`` is the non-forgiving selector list
    that siblings must match to be counted. ``reverse`` is True for
    ``:nth-last-child``, False for ``:nth-child``.

    Specificity = (0, 1, 0) from the pseudo-class itself + max specificity of
    the ``filter`` selector list (CSS Level 4 §16). See  and .

    Examples::

        >>> from aspose_html.css._ast import NthFilteredChildPseudoClass, NthArgument
        >>> from aspose_html.css._parser import parse
        >>> node = parse(":nth-child(2 of .foo)").selectors[0].parts[0][1].simple_selectors[0]
        >>> isinstance(node, NthFilteredChildPseudoClass)
        True
        >>> node.nth
        NthArgument(a=0, b=2)
        >>> node.reverse
        False
        >>> node2 = parse(":nth-last-child(3 of p)").selectors[0].parts[0][1].simple_selectors[0]
        >>> node2.nth
        NthArgument(a=0, b=3)
        >>> node2.reverse
        True
    """

    nth: "NthArgument"
    filter: "SelectorList"
    reverse: bool = False  # True for :nth-last-child, False for :nth-child


# ── Compound and complex selectors ────────────────────────────────────────────

# Widened element type for CompoundSelector to include Level 4 pseudo-classes.
# See : the four new nodes are not added to SimpleSelector (that union
# is frozen for  cache compatibility); instead CompoundSelector accepts
# the broader AnySimpleSelector type.
# NthFilteredChildPseudoClass added in  /  for :nth-child(An+B of S).
AnySimpleSelector = Union[
    SimpleSelector,
    "HasPseudoClass",
    "IsPseudoClass",
    "WherePseudoClass",
    "ComplexNotPseudoClass",
    "NthFilteredChildPseudoClass",
]


@dataclasses.dataclass(frozen=True)
class CompoundSelector:
    """A sequence of simple selectors that all apply to the same element.

    E.g. ``div.box#main[href]`` -> CompoundSelector with four SimpleSelector entries.

    Constraints (enforced by the parser):
    - At most one TypeSelector or UniversalSelector; it must be first if present.
    - The empty compound selector is invalid and is never produced.

    ``simple_selectors`` may contain Level 4 pseudo-class nodes
    (``HasPseudoClass``, ``IsPseudoClass``, ``WherePseudoClass``,
    ``ComplexNotPseudoClass``, ``NthFilteredChildPseudoClass``) in addition to
    the original ``SimpleSelector`` union. This widening is additive and
    backward-compatible. See  and .
    """

    simple_selectors: "tuple[AnySimpleSelector, ...]"


@dataclasses.dataclass(frozen=True)
class ComplexSelector:
    """A chain of CompoundSelectors joined by Combinators.

    Stored as an alternating sequence: compound, (combinator, compound)*.
    Represented as a tuple of ``(Combinator | None, CompoundSelector)`` pairs
    where the first pair always has ``combinator=None`` (leftmost compound).

    Example — ``div > span.box``::

        ComplexSelector(parts=(
            (None,             CompoundSelector((TypeSelector("div"),))),
            (Combinator.CHILD, CompoundSelector((TypeSelector("span"), ClassSelector("box")))),
        ))
    """

    parts: tuple[tuple[Combinator | None, CompoundSelector], ...]


@dataclasses.dataclass(frozen=True)
class SelectorList:
    """The root AST node. A comma-separated list of complex selectors.

    selectors: one or more ComplexSelector instances.
    This is the type returned by parse() and consumed by 's matcher.
    """

    selectors: tuple[ComplexSelector, ...]
