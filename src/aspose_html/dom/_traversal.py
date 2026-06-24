"""_traversal — NodeFilter, NodeIterator, TreeWalker.

Implements WHATWG DOM §6.1–§6.3 filtered DOM traversal objects.

Created via Document.create_node_iterator() and Document.create_tree_walker().
Do NOT import aspose_html.dom at module level — all DOM types are imported
lazily or referenced via TYPE_CHECKING to avoid circular imports.  # See 
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from aspose_html.dom._node import Node


# ---------------------------------------------------------------------------
# WHATWG DOM §6.1 — NodeFilter
# ---------------------------------------------------------------------------

class NodeFilter:
    """Constants for TreeWalker and NodeIterator filtering.

    Per WHATWG DOM §6.1 NodeFilter interface.

    ``what_to_show`` bitmask constants select which node types are visited.
    ``FILTER_*`` constants are returned by user-supplied filter callables.

    Examples
    --------
    >>> NodeFilter.SHOW_ELEMENT
    1
    >>> NodeFilter.SHOW_ALL == 0xFFFFFFFF
    True
    >>> NodeFilter.FILTER_ACCEPT
    1
    >>> NodeFilter.FILTER_REJECT
    2
    >>> NodeFilter.FILTER_SKIP
    3
    """

    # ------------------------------------------------------------------
    # what_to_show bitmask constants  # : values match WHATWG DOM §6.1
    # ------------------------------------------------------------------
    SHOW_ALL: int                    = 0xFFFFFFFF
    SHOW_ELEMENT: int                = 0x1
    SHOW_ATTRIBUTE: int              = 0x2
    SHOW_TEXT: int                   = 0x4
    SHOW_CDATA_SECTION: int          = 0x8
    SHOW_PROCESSING_INSTRUCTION: int = 0x40
    SHOW_COMMENT: int                = 0x80
    SHOW_DOCUMENT: int               = 0x100
    SHOW_DOCUMENT_TYPE: int          = 0x200
    SHOW_DOCUMENT_FRAGMENT: int      = 0x400

    # ------------------------------------------------------------------
    # Filter result constants  # : FILTER_ACCEPT=1, REJECT=2, SKIP=3
    # ------------------------------------------------------------------
    FILTER_ACCEPT: int = 1
    FILTER_REJECT: int = 2
    FILTER_SKIP: int   = 3


# ---------------------------------------------------------------------------
# WHATWG DOM Table 1 — node_type → SHOW_* bit mapping
# ---------------------------------------------------------------------------
# Keys are the integer NodeType constants (avoiding the import at module level).
_NODE_TYPE_TO_SHOW_BIT: dict[int, int] = {
    1:  NodeFilter.SHOW_ELEMENT,
    2:  NodeFilter.SHOW_ATTRIBUTE,
    3:  NodeFilter.SHOW_TEXT,
    4:  NodeFilter.SHOW_CDATA_SECTION,
    7:  NodeFilter.SHOW_PROCESSING_INSTRUCTION,
    8:  NodeFilter.SHOW_COMMENT,
    9:  NodeFilter.SHOW_DOCUMENT,
    10: NodeFilter.SHOW_DOCUMENT_TYPE,
    11: NodeFilter.SHOW_DOCUMENT_FRAGMENT,
}


# ---------------------------------------------------------------------------
# Private helpers — tree navigation
# ---------------------------------------------------------------------------

def _filter_node(
    node: "Node",
    what_to_show: int,
    filter_fn: "Callable[[Node], int] | None",
) -> int:
    """Apply what_to_show bitmask then the filter callable.

    Returns one of NodeFilter.FILTER_ACCEPT / FILTER_REJECT / FILTER_SKIP.

    Per WHATWG DOM §6.1 "filter" algorithm:
    1. Map node_type to a SHOW_* bit.
    2. If bit not in what_to_show → return FILTER_SKIP without calling filter.
    3. If no filter_fn → return FILTER_ACCEPT.
    4. Delegate to filter_fn; return its result.

    Exceptions from filter_fn propagate to the caller.  # See  §Error handling
    """
    bit = _NODE_TYPE_TO_SHOW_BIT.get(node._node_type, 0)
    if (what_to_show & bit) == 0:
        return NodeFilter.FILTER_SKIP
    if filter_fn is None:
        return NodeFilter.FILTER_ACCEPT
    return filter_fn(node)


def _next_node_in_tree(node: "Node", root: "Node") -> "Node | None":
    """Return the next node in DFS pre-order after *node*, constrained to *root*.

    Used by NodeIterator.next_node().  Returns None when the subtree is
    exhausted.
    """
    # Try first child
    if node._children:
        return node._children[0]
    # Try next sibling, walking up toward root
    current = node
    while current is not root:
        parent = current._parent
        if parent is None:
            return None
        siblings = parent._children
        idx = siblings.index(current)
        if idx + 1 < len(siblings):
            return siblings[idx + 1]
        current = parent
    return None


def _last_descendant(node: "Node") -> "Node":
    """Return the last node in DFS pre-order within *node*'s subtree.

    Used by _previous_node_in_tree().
    """
    while node._children:
        node = node._children[-1]
    return node


def _previous_node_in_tree(node: "Node", root: "Node") -> "Node | None":
    """Return the previous node in DFS pre-order before *node*, constrained to *root*.

    Used by NodeIterator.previous_node().  Returns None when *node* is already
    the root (the root is the first node in document order within its subtree).

    Note: when *node*'s parent IS the root, the parent (root) IS the previous
    node — NodeIterator visits the root itself.  Per WHATWG DOM §6.2 the root
    is included in the iteration sequence.
    """
    if node is root:
        return None
    parent = node._parent
    if parent is None:
        return None
    siblings = parent._children
    idx = siblings.index(node)
    if idx > 0:
        # Go to the last DFS node in the left sibling's subtree
        return _last_descendant(siblings[idx - 1])
    # No left sibling — parent is the previous node (which may be root itself).
    return parent


# ---------------------------------------------------------------------------
# WHATWG DOM §6.2 — NodeIterator
# ---------------------------------------------------------------------------

class NodeIterator:
    """Flat, stateful iteration over DOM nodes matching a filter.

    Per WHATWG DOM §6.2.

    Create via ``Document.create_node_iterator()`` — do not instantiate directly.

    The iterator maintains a *reference node* and a *pointer-before* flag.
    ``next_node()`` advances in document order; ``previous_node()`` retreats.
    ``FILTER_REJECT`` is treated identically to ``FILTER_SKIP`` (NodeIterator
    has no subtree concept — see WHATWG DOM §6.2).

    Examples
    --------
    >>> from aspose_html.dom import Document, NodeFilter
    >>> doc = Document()
    >>> body = doc.create_element("body")
    >>> p = doc.create_element("p")
    >>> t = doc.create_text_node("hello")
    >>> p.append_child(t)
    <Text data='hello'>
    >>> body.append_child(p)
    <Element 'P'>
    >>> doc.append_child(body)
    <Element 'BODY'>
    >>> it = doc.create_node_iterator(body, NodeFilter.SHOW_TEXT)
    >>> it.next_node().node_value
    'hello'
    """

    __slots__ = (
        "_root",
        "_what_to_show",
        "_filter",
        "_reference_node",
        "_pointer_before_reference_node",
    )

    def __init__(
        self,
        root: "Node",
        what_to_show: int = NodeFilter.SHOW_ALL,
        node_filter: "Callable[[Node], int] | None" = None,
    ) -> None:
        """Initialise a NodeIterator.

        Parameters
        ----------
        root : Node
            The root of the iteration subtree.
        what_to_show : int
            Bitmask of ``NodeFilter.SHOW_*`` constants.
        node_filter : callable or None
            Called for each candidate node; returns FILTER_ACCEPT/REJECT/SKIP.
        """
        self._root: "Node" = root
        self._what_to_show: int = what_to_show
        self._filter: "Callable[[Node], int] | None" = node_filter
        self._reference_node: "Node" = root
        self._pointer_before_reference_node: bool = True

    # ------------------------------------------------------------------
    # Read-only properties
    # ------------------------------------------------------------------

    @property
    def root(self) -> "Node":
        """The root node of this iterator's subtree.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> it = doc.create_node_iterator(el)
        >>> it.root is el
        True
        """
        return self._root

    @property
    def what_to_show(self) -> int:
        """The ``what_to_show`` bitmask passed at construction.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> it = doc.create_node_iterator(el, NodeFilter.SHOW_TEXT)
        >>> it.what_to_show == NodeFilter.SHOW_TEXT
        True
        """
        return self._what_to_show

    @property
    def filter(self) -> "Callable[[Node], int] | None":
        """The user-supplied filter callable, or None.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> it = doc.create_node_iterator(el)
        >>> it.filter is None
        True
        """
        return self._filter

    @property
    def reference_node(self) -> "Node":
        """The current reference node of this iterator.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> it = doc.create_node_iterator(el)
        >>> it.reference_node is el
        True
        """
        return self._reference_node

    @property
    def pointer_before_reference_node(self) -> bool:
        """``True`` if the iterator position is *before* the reference node.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> it = doc.create_node_iterator(el)
        >>> it.pointer_before_reference_node
        True
        """
        return self._pointer_before_reference_node

    # ------------------------------------------------------------------
    # Traversal methods
    # ------------------------------------------------------------------

    def next_node(self) -> "Node | None":
        """Advance the iterator and return the next accepted node.

        Per WHATWG DOM §6.2.4 (traverse in forward direction).  Returns
        ``None`` when no more nodes match.

        In NodeIterator, ``FILTER_REJECT`` is treated identically to
        ``FILTER_SKIP`` — there is no subtree pruning concept.

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> body.append_child(p)
        <Element 'P'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> it = doc.create_node_iterator(body, NodeFilter.SHOW_ELEMENT)
        >>> it.next_node().node_name
        'BODY'
        >>> it.next_node().node_name
        'P'
        >>> it.next_node() is None
        True
        """
        # WHATWG DOM §6.2.4 "traverse" with direction=next
        pointer = self._pointer_before_reference_node
        node = self._reference_node

        while True:
            if not pointer:
                # Advance to next node in tree order
                next_candidate = _next_node_in_tree(node, self._root)
                if next_candidate is None:
                    return None
                node = next_candidate
            pointer = False

            result = _filter_node(node, self._what_to_show, self._filter)
            if result == NodeFilter.FILTER_ACCEPT:
                self._reference_node = node
                self._pointer_before_reference_node = False
                return node
            # FILTER_SKIP or FILTER_REJECT: both treated as skip in NodeIterator
            # Continue to next node in tree order

    def previous_node(self) -> "Node | None":
        """Retreat the iterator and return the previous accepted node.

        Per WHATWG DOM §6.2.4 (traverse in reverse direction).  Returns
        ``None`` when no more nodes precede the current position.

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> body.append_child(p)
        <Element 'P'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> it = doc.create_node_iterator(body, NodeFilter.SHOW_ELEMENT)
        >>> _ = it.next_node()  # body
        >>> _ = it.next_node()  # p
        >>> it.previous_node().node_name
        'P'
        >>> it.previous_node().node_name
        'BODY'
        >>> it.previous_node() is None
        True
        """
        # WHATWG DOM §6.2.4 "traverse" with direction=previous
        pointer = self._pointer_before_reference_node
        node = self._reference_node

        while True:
            if pointer:
                # Retreat to previous node in tree order
                prev_candidate = _previous_node_in_tree(node, self._root)
                if prev_candidate is None:
                    return None
                node = prev_candidate
            pointer = True

            result = _filter_node(node, self._what_to_show, self._filter)
            if result == NodeFilter.FILTER_ACCEPT:
                self._reference_node = node
                self._pointer_before_reference_node = True
                return node
            # FILTER_SKIP or FILTER_REJECT: skip in NodeIterator

    def detach(self) -> None:
        """No-op — kept for API compatibility.

        WHATWG Living Standard §6.2.5 removed the effect of ``detach()``;
        the method is retained so existing code that calls it does not fail.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> it = doc.create_node_iterator(el)
        >>> it.detach()  # no-op; no return value, no exception
        """


# ---------------------------------------------------------------------------
# WHATWG DOM §6.3 — TreeWalker
# ---------------------------------------------------------------------------

class TreeWalker:
    """Cursor-style DOM traversal bounded to a root subtree.

    Per WHATWG DOM §6.3.

    Create via ``Document.create_tree_walker()`` — do not instantiate directly.

    ``current_node`` is readable and writable; setting it repositions the
    cursor for subsequent navigation calls.

    Examples
    --------
    >>> from aspose_html.dom import Document, NodeFilter
    >>> doc = Document()
    >>> body = doc.create_element("body")
    >>> div = doc.create_element("div")
    >>> p = doc.create_element("p")
    >>> div.append_child(p)
    <Element 'P'>
    >>> body.append_child(div)
    <Element 'DIV'>
    >>> doc.append_child(body)
    <Element 'BODY'>
    >>> walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
    >>> walker.next_node().node_name
    'DIV'
    >>> walker.next_node().node_name
    'P'
    >>> walker.next_node() is None
    True
    """

    __slots__ = ("_root", "_what_to_show", "_filter", "_current_node")

    def __init__(
        self,
        root: "Node",
        what_to_show: int = NodeFilter.SHOW_ALL,
        node_filter: "Callable[[Node], int] | None" = None,
    ) -> None:
        """Initialise a TreeWalker.

        Parameters
        ----------
        root : Node
            The root of the traversal subtree.  ``current_node`` starts here.
        what_to_show : int
            Bitmask of ``NodeFilter.SHOW_*`` constants.
        node_filter : callable or None
            Called for each candidate node; returns FILTER_ACCEPT/REJECT/SKIP.
        """
        self._root: "Node" = root
        self._what_to_show: int = what_to_show
        self._filter: "Callable[[Node], int] | None" = node_filter
        self._current_node: "Node" = root

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def root(self) -> "Node":
        """The root node of this walker's subtree.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> walker = doc.create_tree_walker(el)
        >>> walker.root is el
        True
        """
        return self._root

    @property
    def what_to_show(self) -> int:
        """The ``what_to_show`` bitmask passed at construction.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> walker = doc.create_tree_walker(el, NodeFilter.SHOW_ELEMENT)
        >>> walker.what_to_show == NodeFilter.SHOW_ELEMENT
        True
        """
        return self._what_to_show

    @property
    def filter(self) -> "Callable[[Node], int] | None":
        """The user-supplied filter callable, or None.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> walker = doc.create_tree_walker(el)
        >>> walker.filter is None
        True
        """
        return self._filter

    @property
    def current_node(self) -> "Node":
        """The walker's current position node.

        This property is read/write.  Setting it repositions the cursor for
        subsequent navigation calls.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> walker = doc.create_tree_walker(el)
        >>> walker.current_node is el
        True
        """
        return self._current_node

    @current_node.setter
    def current_node(self, node: "Node") -> None:
        """Reposition the walker's cursor to *node*.

        Parameters
        ----------
        node : Node
            The new current node.  May be any node; it is not validated
            against the root boundary (WHATWG DOM §6.3.3 allows this).
        """
        self._current_node = node

    # ------------------------------------------------------------------
    # Navigation methods
    # ------------------------------------------------------------------

    def parent_node(self) -> "Node | None":
        """Move to and return the nearest accepted ancestor within the root boundary.

        Per WHATWG DOM §6.3.4.  Walks ancestors from ``current_node`` upward
        toward (but not past) ``root``.  Returns the first ancestor for which
        the filter returns ``FILTER_ACCEPT``, or ``None`` if none is found before
        the root boundary.

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> body.append_child(p)
        <Element 'P'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        >>> walker.current_node = p
        >>> walker.parent_node() is body
        True
        >>> walker.parent_node() is None  # already at root
        True
        """
        # WHATWG DOM §6.3.4: walk ancestors; root is the boundary (never returned).
        node = self._current_node
        while node is not self._root:
            node = node._parent
            if node is None:
                return None
            result = _filter_node(node, self._what_to_show, self._filter)
            if result == NodeFilter.FILTER_ACCEPT:
                self._current_node = node
                return node
        return None

    def first_child(self) -> "Node | None":
        """Move to and return the first accepted child of ``current_node``.

        Per WHATWG DOM §6.3.5 traverse children (direction=first).

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> span = doc.create_element("span")
        >>> body.append_child(p)
        <Element 'P'>
        >>> body.append_child(span)
        <Element 'SPAN'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        >>> walker.first_child().node_name
        'P'
        """
        return self._traverse_children(first=True)

    def last_child(self) -> "Node | None":
        """Move to and return the last accepted child of ``current_node``.

        Per WHATWG DOM §6.3.5 traverse children (direction=last).

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> span = doc.create_element("span")
        >>> body.append_child(p)
        <Element 'P'>
        >>> body.append_child(span)
        <Element 'SPAN'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        >>> walker.last_child().node_name
        'SPAN'
        """
        return self._traverse_children(first=False)

    def previous_sibling(self) -> "Node | None":
        """Move to and return the previous accepted sibling.

        Per WHATWG DOM §6.3.6 traverse siblings (direction=previous).

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> span = doc.create_element("span")
        >>> body.append_child(p)
        <Element 'P'>
        >>> body.append_child(span)
        <Element 'SPAN'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        >>> walker.current_node = span
        >>> walker.previous_sibling().node_name
        'P'
        """
        return self._traverse_siblings(next_direction=False)

    def next_sibling(self) -> "Node | None":
        """Move to and return the next accepted sibling.

        Per WHATWG DOM §6.3.6 traverse siblings (direction=next).

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> span = doc.create_element("span")
        >>> body.append_child(p)
        <Element 'P'>
        >>> body.append_child(span)
        <Element 'SPAN'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        >>> walker.current_node = p
        >>> walker.next_sibling().node_name
        'SPAN'
        """
        return self._traverse_siblings(next_direction=True)

    def next_node(self) -> "Node | None":
        """Move to and return the next node in document order.

        Per WHATWG DOM §6.3.7 (depth-first forward traversal).  Descends
        into children unless the filter returns ``FILTER_REJECT``.  Returns
        ``None`` when the subtree is exhausted.

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> body.append_child(p)
        <Element 'P'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        >>> walker.next_node().node_name
        'P'
        >>> walker.next_node() is None
        True
        """
        # WHATWG DOM §6.3.7 "to traverse to next node"
        node = self._current_node
        result = NodeFilter.FILTER_ACCEPT

        while True:
            # Step 3a: descend while FILTER_ACCEPT and children exist
            while result != NodeFilter.FILTER_REJECT and node._children:
                node = node._children[0]
                result = _filter_node(node, self._what_to_show, self._filter)
                if result == NodeFilter.FILTER_ACCEPT:
                    self._current_node = node
                    return node

            # Step 3b–d: find next sibling walking up
            sibling = None
            temporary = node
            while temporary is not None:
                if temporary is self._root:
                    return None
                sibling = _get_next_sibling(temporary)
                if sibling is not None:
                    node = sibling
                    break
                temporary = temporary._parent

            if sibling is None:
                return None

            # Step 3e–f: filter the found node
            result = _filter_node(node, self._what_to_show, self._filter)
            if result == NodeFilter.FILTER_ACCEPT:
                self._current_node = node
                return node

    def previous_node(self) -> "Node | None":
        """Move to and return the previous node in document order.

        Per WHATWG DOM §6.3.7 (depth-first backward traversal).  Descends
        into the last children of previous siblings.  Unlike :meth:`next_node`,
        ``previous_node`` *can* return the root node itself before exhausting.

        Returns
        -------
        Node or None

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> body = doc.create_element("body")
        >>> p = doc.create_element("p")
        >>> body.append_child(p)
        <Element 'P'>
        >>> doc.append_child(body)
        <Element 'BODY'>
        >>> walker = doc.create_tree_walker(body, NodeFilter.SHOW_ELEMENT)
        >>> _ = walker.next_node()  # move to p
        >>> walker.previous_node().node_name  # p's parent = body (root)
        'BODY'
        >>> walker.previous_node() is None    # already at root, no further
        True
        """
        # WHATWG DOM §6.3.7 "to traverse to previous node"
        node = self._current_node

        while node is not self._root:
            sibling = _get_previous_sibling(node)
            while sibling is not None:
                node = sibling
                result = _filter_node(node, self._what_to_show, self._filter)
                # Descend into last child while not FILTER_REJECT
                while result != NodeFilter.FILTER_REJECT and node._children:
                    node = node._children[-1]
                    result = _filter_node(node, self._what_to_show, self._filter)
                if result == NodeFilter.FILTER_ACCEPT:
                    self._current_node = node
                    return node
                sibling = _get_previous_sibling(node)

            if node is self._root or node._parent is None:
                return None
            node = node._parent
            result = _filter_node(node, self._what_to_show, self._filter)
            if result == NodeFilter.FILTER_ACCEPT:
                self._current_node = node
                return node

        return None

    # ------------------------------------------------------------------
    # Private traversal helpers
    # ------------------------------------------------------------------

    def _traverse_children(self, first: bool) -> "Node | None":
        """Implement WHATWG DOM §6.3.5 traverse children.

        *first=True* → first_child semantics.
        *first=False* → last_child semantics.
        """
        # Step 1-2: get first/last child of current_node
        children = self._current_node._children
        if not children:
            return None
        node: "Node | None" = children[0] if first else children[-1]

        # Step 3: loop
        while node is not None:
            result = _filter_node(node, self._what_to_show, self._filter)

            # Step 3b: FILTER_ACCEPT → done
            if result == NodeFilter.FILTER_ACCEPT:
                self._current_node = node
                return node

            # Step 3c: FILTER_SKIP → try first/last child of this node
            if result == NodeFilter.FILTER_SKIP:
                child_list = node._children
                if child_list:
                    node = child_list[0] if first else child_list[-1]
                    continue

            # result == FILTER_REJECT or FILTER_SKIP with no children:
            # Step 3d: find next/previous sibling (or backtrack)
            while node is not None:
                sibling = _get_next_sibling(node) if first else _get_previous_sibling(node)
                if sibling is not None:
                    node = sibling
                    break
                parent = node._parent
                if parent is None or parent is self._root or parent is self._current_node:
                    return None
                node = parent

        return None

    def _traverse_siblings(self, next_direction: bool) -> "Node | None":
        """Implement WHATWG DOM §6.3.6 traverse siblings.

        *next_direction=True* → next_sibling semantics.
        *next_direction=False* → previous_sibling semantics.
        """
        # Step 1-2: start from current_node; return None if at root
        node = self._current_node
        if node is self._root:
            return None

        # Step 3: outer loop
        while True:
            # Step 3a: get first sibling
            sibling = _get_next_sibling(node) if next_direction else _get_previous_sibling(node)

            # Step 3b: inner loop over siblings
            while sibling is not None:
                node = sibling
                result = _filter_node(node, self._what_to_show, self._filter)

                # Step 3b-iii: FILTER_ACCEPT → done
                if result == NodeFilter.FILTER_ACCEPT:
                    self._current_node = node
                    return node

                # Step 3b-iv: get first/last child as potential next candidate
                child_list = node._children
                sibling = (child_list[0] if next_direction else child_list[-1]) if child_list else None

                # Step 3b-v: FILTER_REJECT or no child → move to next/prev sibling
                if result == NodeFilter.FILTER_REJECT or sibling is None:
                    sibling = _get_next_sibling(node) if next_direction else _get_previous_sibling(node)

            # Step 3c-d: move to parent; return None if at root or no parent
            node = node._parent
            if node is None or node is self._root:
                return None

            # Step 3e: if parent is FILTER_ACCEPT → return None (per WHATWG §6.3.6)
            if _filter_node(node, self._what_to_show, self._filter) == NodeFilter.FILTER_ACCEPT:
                return None


# ---------------------------------------------------------------------------
# Module-level sibling helpers (used by both TreeWalker and _traverse_*)
# ---------------------------------------------------------------------------

def _get_next_sibling(node: "Node") -> "Node | None":
    """Return the next sibling of *node*, or None."""
    parent = node._parent
    if parent is None:
        return None
    siblings = parent._children
    idx = siblings.index(node)
    if idx + 1 < len(siblings):
        return siblings[idx + 1]
    return None


def _get_previous_sibling(node: "Node") -> "Node | None":
    """Return the previous sibling of *node*, or None."""
    parent = node._parent
    if parent is None:
        return None
    siblings = parent._children
    idx = siblings.index(node)
    if idx > 0:
        return siblings[idx - 1]
    return None
