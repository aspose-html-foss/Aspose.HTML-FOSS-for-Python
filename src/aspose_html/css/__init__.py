"""aspose_html.css — CSS selector engine public surface.

Public API: select() and element_matches(). All other names are internal.
"""
from __future__ import annotations

from aspose_html.dom import Node, Element
from ._parser import parse
from ._ast import SelectorList

__all__ = ["select", "element_matches"]


def select(root: Node, selector: str, first_only: bool = False) -> list[Element]:
    """Find elements matching a CSS selector rooted at the given node.

    Parameters
    ----------
    root : Node
        The root of the subtree to search. Usually a Document or Element.
    selector : str
        A CSS selector string. Supports CSS Selectors Level 3 plus
        Level 4 pseudo-classes :has(), :is(), :where(), and complex :not()
        for DOM querying workflows.
    first_only : bool, optional
        If True, stop after the first match and return a one-element list
        (or an empty list if no match). Default False.

    Returns
    -------
    list[Element]
        Matching elements in tree order. Empty list if no match.

    Raises
    ------
    SyntaxError
        If selector is completely unparseable.
    NotImplementedError
        If selector uses a syntactically valid but unimplemented construct.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> html = doc.create_element("html")
    >>> body = doc.create_element("body")
    >>> div = doc.create_element("div")
    >>> div.set_attribute("class", "box")
    >>> doc.append_child(html)
    <Element 'HTML'>
    >>> html.append_child(body)
    <Element 'BODY'>
    >>> body.append_child(div)
    <Element 'DIV' class='box'>
    >>> from aspose_html.css import select
    >>> select(doc, "div.box")
    [<Element 'DIV' class='box'>]
    """
    # forgiving=True for query_selector_all (first_only=False) per  §7
    # forgiving=False for query_selector (first_only=True) per DOM Standard §4.2.2
    try:
        parsed: SelectorList = parse(selector, forgiving=not first_only)
    except NotImplementedError as exc:
        #  (): pseudo-elements are invalid for query-selector APIs
        # and must surface as SyntaxError rather than parser-internal
        # NotImplementedError.
        if str(exc).startswith("Pseudo-elements are not implemented:"):
            raise SyntaxError(str(exc)) from exc
        raise

    # Lazy import —  provides this module. Until  is implemented,
    # importing aspose_html.css succeeds; the ImportError surfaces only here.
    from ._matcher import match  # type: ignore[import]
    return match(root, parsed, first_only=first_only, scope_root=root)


def element_matches(element: Element, selector: str) -> bool:
    """Return ``True`` if *element* matches the CSS *selector*.

    Unlike ``select(root, selector)``, this function tests the element
    directly — including detached elements that have no owner document.
    It is the correct implementation primitive for ``Element.matches()``.

    Parameters
    ----------
    element : Element
        The element to test against *selector*.
    selector : str
        A CSS selector string.

    Returns
    -------
    bool
        ``True`` if *element* satisfies *selector*.

    Raises
    ------
    SyntaxError
        If *selector* is completely unparseable.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> from aspose_html.css import element_matches
    >>> doc = Document()
    >>> div = doc.create_element("div")
    >>> div.set_attribute("class", "box")
    >>> element_matches(div, "div")
    True
    >>> element_matches(div, ".box")
    True
    >>> element_matches(div, "span")
    False
    """
    parsed: SelectorList = parse(selector, forgiving=True)
    from ._matcher import _matches_selector_list  # type: ignore[import]
    return _matches_selector_list(element, parsed, scope_root=element)
