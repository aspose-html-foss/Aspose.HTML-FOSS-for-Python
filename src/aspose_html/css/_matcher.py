"""CSS selector matcher — BACK-8.

Evaluates a parsed SelectorList (produced by _parser.py) against a DOM
subtree and returns matching Element nodes in document order.

Internal to aspose_html.css. Not part of the public API.
Public entry point: aspose_html.css.select() in __init__.py.

See ADR-008 for design rationale and algorithm details.
"""
from __future__ import annotations

from collections.abc import Iterator
from urllib.parse import unquote, urlsplit

from aspose_html.dom import Node, Element
from aspose_html.dom._node_type import NodeType

from ._ast import (
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
    PseudoClassSelector,
    NthArgument,
    Combinator,
    HasPseudoClass,
    IsPseudoClass,
    WherePseudoClass,
    ComplexNotPseudoClass,
    NthFilteredChildPseudoClass,
)

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def match(
    root: Node,
    selector_list: SelectorList,
    *,
    first_only: bool = False,
    scope_root: Node | None = None,
) -> list[Element]:
    """Evaluate selector_list against the subtree rooted at root.

    Parameters
    ----------
    root : Node
        The root of the subtree. All elements in tree order are candidates.
        The root itself is not a candidate (mirrors querySelectorAll scoping).
    selector_list : SelectorList
        The parsed selector AST produced by parse().
    first_only : bool
        If True, return after the first match.

    Returns
    -------
    list[Element]
        Matching elements in document order.
    """
    if scope_root is None:
        scope_root = root

    results: list[Element] = []
    for element in _iter_elements(root):
        if _matches_selector_list(element, selector_list, scope_root=scope_root):
            results.append(element)
            if first_only:
                return results
    return results


# ---------------------------------------------------------------------------
# Tree traversal
# ---------------------------------------------------------------------------


def _iter_elements(root: Node) -> Iterator[Element]:
    """Yield all Element nodes in the subtree rooted at root in document order.

    The root itself is NOT yielded — matches browser behaviour where
    querySelectorAll returns elements strictly within the scope root.
    Uses an iterative stack to avoid Python recursion limits on deep trees.
    """
    # Iterative DFS — reverse so leftmost child is popped first. See ADR-008 §4.
    stack = list(reversed(root._children))
    while stack:
        node = stack.pop()
        if isinstance(node, Element):
            yield node
        # Always push children so element descendants of non-element nodes
        # (e.g. children of Document) are still visited.
        if node._children:
            stack.extend(reversed(node._children))


# ---------------------------------------------------------------------------
# Selector list / complex selector matching
# ---------------------------------------------------------------------------


def _matches_selector_list(
    element: Element,
    selector_list: SelectorList,
    *,
    scope_root: Node | None = None,
) -> bool:
    """Return True if element matches any ComplexSelector in selector_list."""
    return any(
        _matches_complex(element, cs, scope_root=scope_root)
        for cs in selector_list.selectors
    )


def _matches_complex(
    element: Element,
    cs: ComplexSelector,
    *,
    scope_root: Node | None = None,
) -> bool:
    """Return True if element matches the complex selector cs.

    Uses right-to-left evaluation per ADR-008 §6:
    the rightmost compound must match the candidate element, then walk
    up the ancestor/sibling chain for each remaining part.
    """
    parts = cs.parts
    n = len(parts)

    # Rightmost compound must match the candidate element directly.
    if not _matches_compound(element, parts[n - 1][1], scope_root=scope_root):
        return False

    current: Element = element

    # Walk remaining parts right-to-left.
    # parts[idx][0] is the combinator that describes how parts[idx] relates
    # to its left neighbour parts[idx-1].
    for idx in range(n - 1, 0, -1):
        combinator = parts[idx][0]  # combinator at position idx
        left_compound = parts[idx - 1][1]

        if combinator is Combinator.CHILD:
            # Current must be a direct child of a node matching left_compound.
            parent = current.parent_node
            if not isinstance(parent, Element):
                return False
            if not _matches_compound(parent, left_compound, scope_root=scope_root):
                return False
            current = parent

        elif combinator is Combinator.DESCENDANT:
            # Any ancestor of current must match left_compound.
            ancestor: Node | None = current.parent_node
            matched = False
            while ancestor is not None:
                if isinstance(ancestor, Element) and _matches_compound(
                    ancestor, left_compound, scope_root=scope_root
                ):
                    current = ancestor
                    matched = True
                    break
                ancestor = ancestor.parent_node
            if not matched:
                return False

        elif combinator is Combinator.ADJACENT:
            # The immediately preceding element sibling must match.
            prev = _previous_element_sibling(current)
            if prev is None or not _matches_compound(prev, left_compound, scope_root=scope_root):
                return False
            current = prev

        elif combinator is Combinator.SIBLING:
            # Any preceding element sibling must match.
            prev = _previous_element_sibling(current)
            matched = False
            while prev is not None:
                if _matches_compound(prev, left_compound, scope_root=scope_root):
                    current = prev
                    matched = True
                    break
                prev = _previous_element_sibling(prev)
            if not matched:
                return False

        else:
            raise NotImplementedError(
                f"Unknown combinator: {combinator!r}"
            )

    return True


def _previous_element_sibling(el: Element) -> Element | None:
    """Return the previous sibling that is an Element, or None.

    Works for elements whose parent is a Document (not just another Element).
    """
    p = el.parent_node
    if p is None:
        return None
    siblings = p._children
    idx = siblings.index(el)
    for i in range(idx - 1, -1, -1):
        if siblings[i]._node_type == NodeType.ELEMENT_NODE:
            return siblings[i]  # type: ignore[return-value]
    return None


# ---------------------------------------------------------------------------
# Compound / simple selector matching
# ---------------------------------------------------------------------------


def _matches_compound(
    element: Element,
    compound: CompoundSelector,
    *,
    scope_root: Node | None = None,
) -> bool:
    """Return True if element matches all simple selectors in compound."""
    return all(
        _matches_simple(element, simple, scope_root=scope_root)
        for simple in compound.simple_selectors
    )


def _matches_simple(
    element: Element,
    simple: (
        "SimpleSelector | HasPseudoClass | IsPseudoClass | WherePseudoClass"
        " | ComplexNotPseudoClass | NthFilteredChildPseudoClass"
    ),
    *,
    scope_root: Node | None = None,
) -> bool:
    """Dispatch to the appropriate simple-selector matcher.

    Handles both Level 3 SimpleSelector variants and the Level 4 pseudo-class
    nodes (HasPseudoClass, IsPseudoClass, WherePseudoClass, ComplexNotPseudoClass,
    NthFilteredChildPseudoClass) added in ADR-042 and ADR-214.
    """
    match simple:
        case UniversalSelector():
            return True
        case TypeSelector(tag_name=tag):
            # INV-006: element.local_name is lowercase; TypeSelector.tag_name
            # is normalised to lowercase at parse time (ADR-007). Direct eq.
            return element.local_name == tag
        case ClassSelector(class_name=cls):
            return cls in element.class_list
        case IDSelector(id_value=id_val):
            return element.id == id_val
        case AttributeSelector():
            return _matches_attribute(element, simple)
        case PseudoClassSelector():
            return _matches_pseudo_class(element, simple, scope_root=scope_root)
        # ── Level 4 pseudo-classes (ADR-042) ──────────────────────────────────
        case HasPseudoClass():
            return _match_has(element, simple, scope_root=scope_root)
        case IsPseudoClass():
            return _match_is(element, simple, scope_root=scope_root)
        case WherePseudoClass():
            return _match_where(element, simple, scope_root=scope_root)
        case ComplexNotPseudoClass():
            return _match_complex_not(element, simple, scope_root=scope_root)
        # ── :nth-child(An+B of S) / :nth-last-child(An+B of S) (ADR-214) ─────
        case NthFilteredChildPseudoClass():
            if simple.reverse:
                return _pseudo_nth_filtered_last_child(element, simple)
            return _pseudo_nth_filtered_child(element, simple)
        case _:
            raise NotImplementedError(
                f"Unknown simple selector type: {type(simple).__name__}"
            )


# ---------------------------------------------------------------------------
# Attribute selector matching
# ---------------------------------------------------------------------------


def _matches_attribute(element: Element, sel: AttributeSelector) -> bool:
    """Evaluate an attribute selector against element.

    Handles all AttributeOperator values per CSS Selectors §6.3.
    """
    actual = element.get_attribute(sel.attr_name)
    if actual is None:
        return False
    if sel.operator == AttributeOperator.EXISTS:
        return True

    # For all value operators, sel.value is guaranteed non-None by the parser.
    expected: str = sel.value  # type: ignore[assignment]

    # INV-006: case-insensitive flag per CSS Selectors §6.3
    if sel.case_insensitive:
        actual = actual.lower()
        expected = expected.lower()

    match sel.operator:
        case AttributeOperator.EQUALS:
            return actual == expected
        case AttributeOperator.WORD:
            # [attr~=val]: value is a whitespace-separated word list
            return expected in actual.split()
        case AttributeOperator.DASHMATCH:
            # [attr|=val]: equals val or starts with val-
            return actual == expected or actual.startswith(expected + "-")
        case AttributeOperator.PREFIX:
            # Empty expected never matches per CSS Selectors §6.3
            return bool(expected) and actual.startswith(expected)
        case AttributeOperator.SUFFIX:
            return bool(expected) and actual.endswith(expected)
        case AttributeOperator.SUBSTRING:
            return bool(expected) and expected in actual
        case _:
            raise NotImplementedError(
                f"Unknown attribute operator: {sel.operator!r}"
            )


# ---------------------------------------------------------------------------
# Pseudo-class matching
# ---------------------------------------------------------------------------


def _matches_pseudo_class(
    element: Element,
    sel: PseudoClassSelector,
    *,
    scope_root: Node | None,
) -> bool:
    """Evaluate a pseudo-class selector against element.

    INV-006: Implemented pseudo-classes follow documented deterministic
    semantics in this headless engine. Selected stateful user-action
    pseudo-classes (e.g. :hover) are valid syntax and evaluate to no-match.
    Remaining out-of-scope dynamic pseudo-classes raise NotImplementedError.
    """
    match sel.name:
        case "root":
            return _pseudo_root(element)
        case "scope":
            return scope_root is not None and element is scope_root
        case "empty":
            return _pseudo_empty(element)
        case "first-child":
            return _pseudo_first_child(element)
        case "last-child":
            return _pseudo_last_child(element)
        case "only-child":
            return _pseudo_only_child(element)
        case "first-of-type":
            return _pseudo_first_of_type(element)
        case "last-of-type":
            return _pseudo_last_of_type(element)
        case "only-of-type":
            return _pseudo_only_of_type(element)
        case "nth-child":
            return _pseudo_nth_child(element, sel.argument)  # type: ignore[arg-type]
        case "nth-last-child":
            return _pseudo_nth_last_child(element, sel.argument)  # type: ignore[arg-type]
        case "nth-of-type":
            return _pseudo_nth_of_type(element, sel.argument)  # type: ignore[arg-type]
        case "nth-last-of-type":
            return _pseudo_nth_last_of_type(element, sel.argument)  # type: ignore[arg-type]
        case "not":
            return _pseudo_not(element, sel.argument)  # type: ignore[arg-type]
        case "link" | "any-link":
            return _pseudo_link(element)
        case "visited":
            # No browsing history in non-browser context — never matches.
            # Per CSS Selectors spec, this is not an error.
            return False
        case "hover" | "focus" | "active" | "focus-visible":
            # Headless deterministic mode has no interactive UI state.
            # Treat as valid selectors that never match.
            return False
        case "lang":
            return _pseudo_lang(element, sel.argument)  # type: ignore[arg-type]
        case "enabled":
            return _pseudo_enabled(element)
        case "disabled":
            return _pseudo_disabled(element)
        case "checked":
            return _pseudo_checked(element)
        case "target":
            return _pseudo_target(element)
        case "valid":
            return _pseudo_valid(element)
        case "invalid":
            return _pseudo_invalid(element)
        case "required":
            return _pseudo_required(element)
        case "optional":
            return _pseudo_optional(element)
        case "placeholder-shown":
            return _pseudo_placeholder_shown(element)
        case "default":
            return _pseudo_default(element)
        case "indeterminate":
            return _pseudo_indeterminate(element)
        case "read-only":
            return _pseudo_read_only(element)
        case "read-write":
            return _pseudo_read_write(element)
        case "blank":
            return _pseudo_blank(element)
        case "focus-within":
            # No focus propagation model in headless mode — never matches.
            return False
        case _:
            raise NotImplementedError(
                f"Pseudo-class :{sel.name!r} is not implemented"
            )


def _pseudo_target(element: Element) -> bool:
    """Deterministic :target matching using owning document URL fragment.

    Matches when the owning document URL has a non-empty fragment whose
    decoded token equals the candidate element's id.
    """
    owner_document = element.owner_document
    if owner_document is None:
        return False
    fragment = urlsplit(owner_document.url).fragment
    if not fragment:
        return False
    return element.id == unquote(fragment)


# ── Track 85 / ADR-284: form constraint-validation and UI-state helpers ─────


def _pseudo_valid(element: Element) -> bool:
    """True when element participates in constraint validation and is valid.

    Track 85 / ADR-284: only will_validate controls participate.
    Non-form elements always return False.
    """
    return bool(getattr(element, "will_validate", False)) and \
           bool(getattr(element, "check_validity", lambda: False)())


def _pseudo_invalid(element: Element) -> bool:
    """True when element participates in constraint validation and is invalid.

    Track 85 / ADR-284: only will_validate controls participate.
    Non-form elements always return False.
    """
    return bool(getattr(element, "will_validate", False)) and \
           not bool(getattr(element, "check_validity", lambda: True)())


def _pseudo_required(element: Element) -> bool:
    """True when element is a constraint-validatable control with required=True.

    Track 85 / ADR-284.
    """
    return bool(getattr(element, "will_validate", False)) and \
           bool(getattr(element, "required", False))


def _pseudo_optional(element: Element) -> bool:
    """True when element is a constraint-validatable control with required=False.

    Track 85 / ADR-284.
    """
    return bool(getattr(element, "will_validate", False)) and \
           not bool(getattr(element, "required", False))


def _pseudo_placeholder_shown(element: Element) -> bool:
    """True when input/textarea has a non-empty placeholder and empty value.

    Track 85 / ADR-284: matches the placeholder-shown CSS state per
    W3C Selectors Level 4 §14.
    """
    placeholder = element.get_attribute("placeholder")
    if not placeholder:
        return False
    value = getattr(element, "value", None)
    return value is not None and value == ""


def _pseudo_default(element: Element) -> bool:
    """True for submit/image inputs (default button semantics).

    Track 85 / ADR-284: default option and radio tracking are deferred
    (require sibling context not available in this track).
    """
    input_type = getattr(element, "type", None)
    if input_type is not None:
        return str(input_type).lower() in {"submit", "image"}
    return False


def _pseudo_indeterminate(element: Element) -> bool:
    """True for checkboxes with indeterminate=True.

    Track 85 / ADR-284: radio group indeterminate state is deferred
    (requires name-group traversal not available in this track).
    """
    input_type = getattr(element, "type", None)
    if input_type is not None and str(input_type).lower() == "checkbox":
        return bool(getattr(element, "indeterminate", False))
    return False


# Editable input types per Selectors Level 4 §14 / WHATWG HTML §4.10
_EDITABLE_INPUT_TYPES: frozenset[str] = frozenset({
    "text", "search", "url", "tel", "email", "password",
    "date", "month", "week", "time", "datetime-local",
    "number", "color", "range",
})


def _pseudo_read_only(element: Element) -> bool:
    """True for elements that are read-only per Selectors Level 4 §14.

    Covers: (a) input/textarea with readonly attribute;
            (b) any element that is not an editable control.

    Track 85 / ADR-284.
    """
    tag = element.tag_name.lower()
    if tag == "textarea":
        return element.has_attribute("readonly")
    if tag == "input":
        input_type = str(getattr(element, "type", "text") or "text").lower()
        if input_type not in _EDITABLE_INPUT_TYPES:
            return True  # non-editable input types are always read-only
        return element.has_attribute("readonly")
    # Non-form elements are always :read-only
    return True


def _pseudo_read_write(element: Element) -> bool:
    """True for editable inputs/textareas without readonly attribute.

    Track 85 / ADR-284: non-form elements and non-editable input types
    always return False.
    """
    tag = element.tag_name.lower()
    if tag == "textarea":
        return not element.has_attribute("readonly")
    if tag == "input":
        input_type = str(getattr(element, "type", "text") or "text").lower()
        if input_type not in _EDITABLE_INPUT_TYPES:
            return False
        return not element.has_attribute("readonly")
    return False


def _pseudo_blank(element: Element) -> bool:
    """True when input/textarea has an empty or whitespace-only value.

    Track 85 / ADR-284: uses value attribute; no user-input event model
    in headless mode.
    """
    tag = element.tag_name.lower()
    if tag in {"input", "textarea"}:
        value = element.get_attribute("value") or ""
        return value.strip() == ""
    return False


# ── :root ──────────────────────────────────────────────────────────────────


def _pseudo_root(element: Element) -> bool:
    """True if element has no parent element (is the document root element)."""
    return element.parent_element is None


# ── :empty ─────────────────────────────────────────────────────────────────


def _pseudo_empty(element: Element) -> bool:
    """True if element has no child nodes of any kind (including text nodes)."""
    # Use _children directly for O(1) length check — this is an internal module.
    return len(element._children) == 0


# ── Sibling list helpers ────────────────────────────────────────────────────


def _element_siblings(element: Element) -> list[Element]:
    """Return the ordered list of element-type siblings including element.

    Returns an empty list if element has no parent.
    Uses parent._children for elements-only filtering; parent may be Document.
    """
    parent = element.parent_node
    if parent is None:
        return []
    return [
        child  # type: ignore[misc]
        for child in parent._children
        if child._node_type == NodeType.ELEMENT_NODE
    ]


def _element_siblings_of_type(element: Element) -> list[Element]:
    """Return ordered list of element siblings with the same local_name."""
    parent = element.parent_node
    if parent is None:
        return []
    tag = element.local_name
    return [
        child  # type: ignore[misc]
        for child in parent._children
        if child._node_type == NodeType.ELEMENT_NODE
        and child.local_name == tag  # type: ignore[union-attr]
    ]


# ── :first-child, :last-child, :only-child ─────────────────────────────────


def _pseudo_first_child(element: Element) -> bool:
    siblings = _element_siblings(element)
    return bool(siblings) and siblings[0] is element


def _pseudo_last_child(element: Element) -> bool:
    siblings = _element_siblings(element)
    return bool(siblings) and siblings[-1] is element


def _pseudo_only_child(element: Element) -> bool:
    siblings = _element_siblings(element)
    return len(siblings) == 1 and siblings[0] is element


# ── :first-of-type, :last-of-type, :only-of-type ───────────────────────────


def _pseudo_first_of_type(element: Element) -> bool:
    siblings = _element_siblings_of_type(element)
    return bool(siblings) and siblings[0] is element


def _pseudo_last_of_type(element: Element) -> bool:
    siblings = _element_siblings_of_type(element)
    return bool(siblings) and siblings[-1] is element


def _pseudo_only_of_type(element: Element) -> bool:
    siblings = _element_siblings_of_type(element)
    return len(siblings) == 1 and siblings[0] is element


# ── :nth-* helpers ─────────────────────────────────────────────────────────


def _matches_nth(a: int, b: int, index: int) -> bool:
    """Return True if index matches the An+B formula (1-based index).

    INV-006: Implements the exact CSS Selectors §6.6.5.2 algorithm.
    Finds whether there exists n >= 0 such that a*n + b == index.
    """
    if a == 0:
        return index == b
    remainder = index - b
    if remainder % a != 0:
        return False
    return remainder // a >= 0


def _pseudo_nth_child(element: Element, arg: NthArgument) -> bool:
    siblings = _element_siblings(element)
    if not siblings:
        return False
    idx = siblings.index(element) + 1  # 1-based
    return _matches_nth(arg.a, arg.b, idx)


def _pseudo_nth_last_child(element: Element, arg: NthArgument) -> bool:
    siblings = _element_siblings(element)
    if not siblings:
        return False
    idx = len(siblings) - siblings.index(element)  # 1-based from end
    return _matches_nth(arg.a, arg.b, idx)


def _pseudo_nth_of_type(element: Element, arg: NthArgument) -> bool:
    siblings = _element_siblings_of_type(element)
    if not siblings:
        return False
    idx = siblings.index(element) + 1
    return _matches_nth(arg.a, arg.b, idx)


def _pseudo_nth_last_of_type(element: Element, arg: NthArgument) -> bool:
    siblings = _element_siblings_of_type(element)
    if not siblings:
        return False
    idx = len(siblings) - siblings.index(element)  # 1-based from end
    return _matches_nth(arg.a, arg.b, idx)


# ── :not() ─────────────────────────────────────────────────────────────────


def _pseudo_not(element: Element, arg: SimpleSelector) -> bool:
    """Negation pseudo-class: matches if element does NOT match arg.

    Guards against nested :not() (Level 4 only, not supported in Level 3).
    """
    if isinstance(arg, PseudoClassSelector) and arg.name == "not":
        raise NotImplementedError(
            ":not() cannot be nested (Level 4 construct, not Level 3)"
        )
    return not _matches_simple(element, arg)


# ── :link / :any-link ──────────────────────────────────────────────────────

_LINK_TAGS: frozenset[str] = frozenset({"a", "area", "link"})
_ENABLED_DISABLED_SUPPORTED_TAGS: frozenset[str] = frozenset(
    {"input", "button", "select", "textarea", "option", "fieldset"}
)


def _pseudo_link(element: Element) -> bool:
    """True if element is <a href>, <area href>, or <link href>."""
    return element.local_name in _LINK_TAGS and element.has_attribute("href")


def _is_enabled_disabled_supported_control(element: Element) -> bool:
    """Return True when :enabled/:disabled semantics are defined for element."""
    return element.local_name in _ENABLED_DISABLED_SUPPORTED_TAGS


def _pseudo_disabled(element: Element) -> bool:
    """Selectors-4 bounded support for :disabled in headless mode.

    Track 82 / ADR-281 scope: only supported form controls participate;
    non-supported elements must not match.
    """
    if not _is_enabled_disabled_supported_control(element):
        return False
    disabled = getattr(element, "disabled", None)
    return bool(disabled)


def _pseudo_enabled(element: Element) -> bool:
    """Selectors-4 bounded support for :enabled in headless mode."""
    if not _is_enabled_disabled_supported_control(element):
        return False
    disabled = getattr(element, "disabled", None)
    return not bool(disabled)


def _pseudo_checked(element: Element) -> bool:
    """Selectors-4 deterministic support for :checked.

    Track 83 / ADR-282 scope:
    - ``<input>`` matches when its ``checked`` property is true.
    - ``<option>`` matches when its ``selected`` property is true.
    - All other elements do not match.
    """
    if element.local_name == "input":
        return bool(getattr(element, "checked", False))
    if element.local_name == "option":
        return bool(getattr(element, "selected", False))
    return False


# ── :lang() ────────────────────────────────────────────────────────────────


def _pseudo_lang(element: Element, lang_range: str) -> bool:
    """True if element's effective language matches lang_range (BCP 47 §3.4).

    Walks up the ancestor chain to find the effective language attribute.
    Comparison is case-insensitive per CSS Selectors §6.6.4.
    """
    node: Node | None = element
    while node is not None:
        if isinstance(node, Element):
            lang_attr = node.get_attribute("lang")
            if lang_attr is not None:
                effective = lang_attr.lower()
                target = lang_range.lower()
                return effective == target or effective.startswith(target + "-")
        node = node.parent_node
    return False


# ---------------------------------------------------------------------------
# Level 4 pseudo-class matching (ADR-042)
# ---------------------------------------------------------------------------


def _iter_descendants(element: Element) -> Iterator[Element]:
    """Yield all descendant Element nodes of element in DFS pre-order.

    Unlike ``_iter_elements`` (which starts from a root's children and skips
    the root itself), this function starts from element's own children and
    is intended for :has() descendant matching. Non-element nodes are skipped
    but their children are still traversed. See ADR-042.
    """
    stack = list(reversed(element._children))
    while stack:
        node = stack.pop()
        if isinstance(node, Element):
            yield node
        # Always descend into children of non-element nodes too (e.g. text nodes
        # inside a shadow-like wrapper). In the current DOM model _children only
        # contains Element and text nodes, so this is safe.
        if node._children:
            stack.extend(reversed(node._children))


def _next_element_sibling(el: Element) -> "Element | None":
    """Return the first following sibling that is an Element, or None.

    Used by :has(+) and :has(~) relative selectors in ADR-042.
    """
    p = el.parent_node
    if p is None:
        return None
    siblings = p._children
    idx = siblings.index(el)
    for i in range(idx + 1, len(siblings)):
        if siblings[i]._node_type == NodeType.ELEMENT_NODE:
            return siblings[i]  # type: ignore[return-value]
    return None


def _match_has(
    element: Element,
    node: HasPseudoClass,
    *,
    scope_root: Node | None,
) -> bool:
    """Evaluate :has(relative-selector-list) against element.

    Returns True if any relative selector in the argument list matches at
    least one candidate relative to element. The leading combinator determines
    which candidates are tested:

    - None (implicit descendant): all descendant elements.
    - CHILD (``>``): direct element children only.
    - ADJACENT (``+``): the immediately following element sibling.
    - SIBLING (``~``): all following element siblings.

    INV-006: Implements W3C CSS Selectors Level 4 §4.6. See ADR-042.
    """
    for leading_combinator, inner_selector_list in node.relative_selectors:
        if leading_combinator is None:
            # Implicit descendant — test all descendants
            for candidate in _iter_descendants(element):
                if _matches_selector_list(candidate, inner_selector_list, scope_root=scope_root):
                    return True

        elif leading_combinator is Combinator.CHILD:
            # Direct children only
            for child in element._children:
                if (
                    child._node_type == NodeType.ELEMENT_NODE
                    and _matches_selector_list(child, inner_selector_list, scope_root=scope_root)  # type: ignore[arg-type]
                ):
                    return True

        elif leading_combinator is Combinator.ADJACENT:
            # Immediately following element sibling
            sibling = _next_element_sibling(element)
            if sibling is not None and _matches_selector_list(sibling, inner_selector_list, scope_root=scope_root):
                return True

        elif leading_combinator is Combinator.SIBLING:
            # All following element siblings
            sibling = _next_element_sibling(element)
            while sibling is not None:
                if _matches_selector_list(sibling, inner_selector_list, scope_root=scope_root):
                    return True
                sibling = _next_element_sibling(sibling)

    return False


def _match_is(element: Element, node: IsPseudoClass, *, scope_root: Node | None) -> bool:
    """Evaluate :is(selector-list) against element.

    Returns True if element matches any selector in the forgiving list.
    Specificity is handled at the _specificity.py level, not here.

    INV-006: Implements W3C CSS Selectors Level 4 §4.4. See ADR-042.
    """
    return _matches_selector_list(element, node.selector_list, scope_root=scope_root)


def _match_where(element: Element, node: WherePseudoClass, *, scope_root: Node | None) -> bool:
    """Evaluate :where(selector-list) against element.

    Identical matching semantics to _match_is(). The zero-specificity
    contribution of :where() is handled in _specificity.py, not here.

    INV-006: Implements W3C CSS Selectors Level 4 §4.7. See ADR-042.
    """
    return _matches_selector_list(element, node.selector_list, scope_root=scope_root)


def _match_complex_not(
    element: Element,
    node: ComplexNotPseudoClass,
    *,
    scope_root: Node | None,
) -> bool:
    """Evaluate Level 4 :not(selector-list) against element.

    Returns True if element does NOT match any selector in the argument list.
    Unlike the Level 3 :not() which accepted only a single simple selector,
    this version accepts a full selector list.

    INV-006: Implements W3C CSS Selectors Level 4 §4.5. See ADR-042.
    """
    return not _matches_selector_list(element, node.selector_list, scope_root=scope_root)


# ---------------------------------------------------------------------------
# :nth-child(An+B of S) / :nth-last-child(An+B of S) — ADR-214
# ---------------------------------------------------------------------------


def _element_matches_selector_list(
    element: Element,
    selector_list: "SelectorList",
    *,
    scope_root: Node | None,
) -> bool:
    """Return True if element matches any selector in selector_list.

    Used by the :nth-child(An+B of S) filtered matching logic.
    Avoids calling the public match() entry point (which traverses subtrees);
    uses _matches_complex directly for element-level matching.

    Parameters
    ----------
    element : Element
        The element to test.
    selector_list : SelectorList
        The filter selector list from NthFilteredChildPseudoClass.filter.

    Returns
    -------
    bool
        True iff the element matches at least one selector in the list.

    Examples
    --------
    >>> # (exercised via test_nth_of_selector.py matching tests)
    """
    return any(
        _matches_complex(element, complex_sel, scope_root=scope_root)
        for complex_sel in selector_list.selectors
    )


def _pseudo_nth_filtered_child(
    element: Element, node: NthFilteredChildPseudoClass
) -> bool:
    """Match :nth-child(An+B of S): count element's filtered siblings from start.

    Collects all element siblings (including element itself), filters to those
    matching ``node.filter``, then checks whether ``element`` is at the Nth
    1-based position in the filtered list.

    INV-006: Implements CSS Selectors Level 4 §8.3. See ADR-214.

    Parameters
    ----------
    element : Element
        The element being tested.
    node : NthFilteredChildPseudoClass
        The parsed pseudo-class node with ``nth`` and ``filter`` fields.

    Returns
    -------
    bool
        True iff element is the An+B-th matching sibling (1-based, from start).

    Examples
    --------
    >>> # (exercised via test_nth_of_selector.py)
    """
    siblings = _element_siblings(element)
    if not siblings:
        return False
    filtered = [
        s
        for s in siblings
        if _element_matches_selector_list(s, node.filter, scope_root=element)
    ]
    if element not in filtered:
        return False
    idx = filtered.index(element) + 1  # 1-based
    return _matches_nth(node.nth.a, node.nth.b, idx)


def _pseudo_nth_filtered_last_child(
    element: Element, node: NthFilteredChildPseudoClass
) -> bool:
    """Match :nth-last-child(An+B of S): count element's filtered siblings from end.

    Collects all element siblings (including element itself), filters to those
    matching ``node.filter``, then checks whether ``element`` is at the Nth
    1-based position counting from the end of the filtered list.

    INV-006: Implements CSS Selectors Level 4 §8.4. See ADR-214.

    Parameters
    ----------
    element : Element
        The element being tested.
    node : NthFilteredChildPseudoClass
        The parsed pseudo-class node (``node.reverse`` is True).

    Returns
    -------
    bool
        True iff element is the An+B-th matching sibling counting from end.

    Examples
    --------
    >>> # (exercised via test_nth_of_selector.py)
    """
    siblings = _element_siblings(element)
    if not siblings:
        return False
    filtered = [
        s
        for s in siblings
        if _element_matches_selector_list(s, node.filter, scope_root=element)
    ]
    if element not in filtered:
        return False
    idx = len(filtered) - filtered.index(element)  # 1-based from end
    return _matches_nth(node.nth.a, node.nth.b, idx)
