"""DocumentFragment node."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.dom._node import Node
from aspose_html.dom._node_type import NodeType

if TYPE_CHECKING:
    from aspose_html.dom._document import Document
    from aspose_html.dom._element import Element
    from aspose_html.dom._collections import NodeList


def _coerce_nodes(
    nodes: "tuple[Node | str, ...]",
    owner_document: "Document | None",
) -> "list[Node]":
    """Convert a mixed tuple of Node and str into a list of Node objects.

    Strings are converted to Text nodes via *owner_document*.create_text_node().
    Used by the ParentNode mixin methods ().
    """
    result: list[Node] = []
    for item in nodes:
        if isinstance(item, str):
            if owner_document is not None:
                result.append(owner_document.create_text_node(item))
            else:
                from aspose_html.dom._character_data import Text  # noqa: PLC0415
                result.append(Text(item))
        else:
            result.append(item)
    return result


class DocumentFragment(Node):
    """A lightweight container for a sub-tree.

    When a ``DocumentFragment`` is passed to ``append_child`` or
    ``insert_before``, all its children are transferred to the new parent
    (fragment adoption) and the fragment's child list becomes empty.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> frag = doc.create_document_fragment()
    >>> frag.node_name
    '#document-fragment'
    >>> frag.node_type
    11
    """

    __slots__ = ()

    def __init__(self, owner_document: Document | None = None) -> None:
        super().__init__(NodeType.DOCUMENT_FRAGMENT_NODE, owner_document)

    @property
    def node_name(self) -> str:
        """``'#document-fragment'``

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_document_fragment().node_name
        '#document-fragment'
        """
        return "#document-fragment"

    @property
    def text_content(self) -> str | None:
        """The concatenation of all descendant Text node data (DFS order).

        Follows the same semantics as Element.text_content. Only TEXT_NODE
        (node type 3) nodes contribute. The setter removes all children and
        inserts a single Text node for non-empty values.

        WARNING: the setter is destructive — it removes all child nodes.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> frag = doc.create_document_fragment()
        >>> t = doc.create_text_node("hello")
        >>> frag.append_child(t)
        <Text data='hello'>
        >>> frag.text_content
        'hello'
        """
        # : identical DFS semantics to Element per WHATWG DOM §4.4.
        # See : DocumentFragment extends Node directly, not Element,
        # so this override is required (cannot inherit from Element).
        parts: list[str] = []
        stack: list = list(self._children)
        while stack:
            node = stack.pop(0)
            if node._node_type == NodeType.TEXT_NODE:
                parts.append(node._data)  # type: ignore[attr-defined]
            stack[:0] = node._children
        return "".join(parts)

    @text_content.setter
    def text_content(self, value: str | None) -> None:
        for child in list(self._children):
            self.remove_child(child)
        if value:
            doc = self._owner_document
            if doc is not None:
                text_node = doc.create_text_node(value)
            else:
                # Detached fragment — create Text directly. See .
                from aspose_html.dom._character_data import Text  # noqa: PLC0415
                text_node = Text(value)
            self.append_child(text_node)

    # ------------------------------------------------------------------
    # ParentNode mixin (WHATWG DOM §4.2.6)
    # ------------------------------------------------------------------

    def prepend(self, *nodes: "Node | str") -> None:
        """Insert *nodes* before the first child of this fragment.

        Strings are converted to Text nodes. No-op if *nodes* is empty.

        Per WHATWG DOM §4.2.6 ParentNode.prepend().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> frag = doc.create_document_fragment()
        >>> a = doc.create_element("a")
        >>> _ = frag.append_child(a)
        >>> b = doc.create_element("b")
        >>> frag.prepend(b)
        >>> frag.first_child is b
        True
        """
        if not nodes:
            return
        coerced = _coerce_nodes(nodes, self._owner_document)
        first = self.first_child
        for node in coerced:
            self.insert_before(node, first)

    def append(self, *nodes: "Node | str") -> None:
        """Append *nodes* as the last children of this fragment.

        Strings are converted to Text nodes. No-op if *nodes* is empty.

        Per WHATWG DOM §4.2.6 ParentNode.append().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> frag = doc.create_document_fragment()
        >>> a = doc.create_element("a")
        >>> frag.append(a, "text")
        >>> frag.first_child is a
        True
        >>> frag.last_child.data
        'text'
        """
        if not nodes:
            return
        coerced = _coerce_nodes(nodes, self._owner_document)
        for node in coerced:
            self.append_child(node)

    def replace_children(self, *nodes: "Node | str") -> None:
        """Remove all children of this fragment, then append *nodes*.

        Strings are converted to Text nodes. Calling with no arguments clears
        the fragment.

        Per WHATWG DOM §4.2.6 ParentNode.replaceChildren().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> frag = doc.create_document_fragment()
        >>> old = doc.create_element("span")
        >>> _ = frag.append_child(old)
        >>> new = doc.create_element("p")
        >>> frag.replace_children(new)
        >>> frag.first_child is new
        True
        >>> frag.replace_children()
        >>> len(frag.child_nodes)
        0
        """
        for child in list(self._children):
            self.remove_child(child)
        coerced = _coerce_nodes(nodes, self._owner_document)
        for node in coerced:
            self.append_child(node)

    # ------------------------------------------------------------------
    # Selector queries
    # ------------------------------------------------------------------

    def query_selector(self, selector: str) -> "Element | None":
        """Return the first element in this fragment matching *selector*.

        Delegates to ``aspose_html.css.select`` (lazy import). Returns
        ``None`` if no element matches.

        Parameters
        ----------
        selector : str
            A CSS selector string.

        Returns
        -------
        Element or None
            The first matching element in document order, or ``None``.

        Raises
        ------
        SyntaxError
            If *selector* is syntactically invalid.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> frag = doc.create_document_fragment()
        >>> p = doc.create_element("p")
        >>> frag.append_child(p)
        <Element 'P'>
        >>> frag.query_selector("p") is p
        True
        >>> frag.query_selector("div") is None
        True
        """
        # : delegates entirely to CSS engine — no custom matching. See .
        from aspose_html.css import select  # noqa: PLC0415
        results = select(self, selector, first_only=True)
        return results[0] if results else None

    def query_selector_all(self, selector: str) -> "NodeList":
        """Return a static NodeList of all elements in this fragment matching *selector*.

        Delegates to ``aspose_html.css.select`` (lazy import). Returns an
        empty ``NodeList`` if no elements match.

        Parameters
        ----------
        selector : str
            A CSS selector string.

        Returns
        -------
        NodeList
            A static (non-live) NodeList of all matching elements in document
            order.

        Raises
        ------
        SyntaxError
            If *selector* is syntactically invalid.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> frag = doc.create_document_fragment()
        >>> p1 = doc.create_element("p")
        >>> p2 = doc.create_element("p")
        >>> frag.append_child(p1)
        <Element 'P'>
        >>> frag.append_child(p2)
        <Element 'P'>
        >>> len(frag.query_selector_all("p"))
        2
        >>> len(frag.query_selector_all("div"))
        0
        """
        # : delegates entirely to CSS engine — no custom matching. See .
        from aspose_html.css import select  # noqa: PLC0415
        from aspose_html.dom._collections import _StaticNodeList  # noqa: PLC0415
        results = select(self, selector)
        return _StaticNodeList(results)

    def _clone_self(self) -> DocumentFragment:
        return DocumentFragment(self._owner_document)

    def __repr__(self) -> str:
        return "<DocumentFragment>"

    __str__ = __repr__
