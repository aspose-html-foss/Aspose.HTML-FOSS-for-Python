"""Range — WHATWG DOM §5 Range interface.

A Range represents a contiguous portion of a document tree, potentially
spanning partial text nodes. Live ranges are updated by the document's internal
mutation signal when child-list and character-data mutations occur.

See  and .
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom._node import Node
    from aspose_html.dom._document import Document
    from aspose_html.dom._document_fragment import DocumentFragment
    from aspose_html.dom._character_data import CharacterData


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _max_offset(node: "Node") -> int:
    """Return the maximum valid offset for *node*.

    For CharacterData nodes (Text, Comment, CDATASection,
    ProcessingInstruction) the maximum offset is the character length.
    For all other nodes it is the number of children.

    Per WHATWG DOM §5.3.
    """
    # : offset semantics per WHATWG DOM §5.
    from aspose_html.dom._node_type import NodeType  # noqa: PLC0415
    if node._node_type in (
        NodeType.TEXT_NODE,
        NodeType.COMMENT_NODE,
        NodeType.CDATA_SECTION_NODE,
        NodeType.PROCESSING_INSTRUCTION_NODE,
    ):
        return len(node._data)  # type: ignore[attr-defined]
    return len(node._children)


def _validate_offset(node: "Node", offset: int) -> None:
    """Raise IndexSizeError if *offset* is out of the valid range for *node*."""
    from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415
    if offset < 0 or offset > _max_offset(node):
        raise IndexSizeError(
            f"offset {offset} is out of range for node {node!r}"
        )


def _bp_compare(
    a: "tuple[Node, int]",
    b: "tuple[Node, int]",
) -> int:
    """Return -1, 0, or 1 comparing boundary point *a* against *b*.

    Implements the WHATWG DOM §5.1 "position of a boundary point relative
    to a boundary point" algorithm.

    Returns -1 if ``a`` is before ``b``, 0 if equal, 1 if after.

    The two boundary points must be in the same tree (otherwise the result
    is undefined; callers must ensure this).
    """
    a_node, a_off = a
    b_node, b_off = b

    # Step 2: same node — simple offset comparison.
    if a_node is b_node:
        if a_off < b_off:
            return -1
        if a_off > b_off:
            return 1
        return 0

    # Lazy import to avoid module-load cycles.
    from aspose_html.dom._node import DocumentPosition  # noqa: PLC0415

    # Determine tree-order relationship between a_node and b_node.
    # b_node.compare_document_position(a_node) returns the position of
    # *a_node* relative to *b_node*.
    pos = b_node.compare_document_position(a_node)
    a_follows_b = bool(pos & DocumentPosition.DOCUMENT_POSITION_FOLLOWING)
    a_contains_b = bool(pos & DocumentPosition.DOCUMENT_POSITION_CONTAINS)
    a_contained_by_b = bool(pos & DocumentPosition.DOCUMENT_POSITION_CONTAINED_BY)

    # Step 3: a_node is following b_node in tree order, AND not an
    # ancestor of b_node. Recurse with sides swapped and invert.
    # Pre-order tree order: descendants follow ancestors. So if a_node is
    # a descendant of b_node, a_follows_b is True AND a_contained_by_b is
    # True. The WHATWG algorithm in step 3 expects "following but not an
    # ancestor", which corresponds to the "neither contains" case.
    if a_follows_b and not a_contains_b:
        # a_node is in a later tree-order subtree. Recurse on (b, a) and
        # invert. Step 4 of the recursion handles the ancestor case.
        return -_bp_compare(b, a)

    # Step 4: a_node is an ancestor of b_node. Find the child of a_node
    # on the path to b_node; compare its index to a_off.
    if a_contains_b:
        child: "Node" = b_node
        while child._parent is not a_node:
            assert child._parent is not None  # noqa: S101 — guaranteed by ancestry
            child = child._parent
        child_idx = a_node._children.index(child)
        if child_idx < a_off:
            return 1  # a is after b
        return -1  # a is before b (offset puts boundary at/before pivot child)

    # Step 5: default — a_node is preceding b_node and is not an ancestor.
    return -1


def _bp_lte(
    a: "tuple[Node, int]",
    b: "tuple[Node, int]",
) -> bool:
    """Return True if boundary point *a* is before or equal to boundary point *b*.

    Per WHATWG DOM §5.1 boundary-point comparison.
    """
    return _bp_compare(a, b) <= 0


def _common_ancestor(a: "Node", b: "Node") -> "Node":
    """Return the deepest common ancestor of nodes *a* and *b*.

    Per WHATWG DOM §5.2 commonAncestorContainer algorithm.

    Raises
    ------
    ValueError
        If *a* and *b* have no common ancestor (different trees).
    """
    # Build ancestor chain for a (inclusive) keyed by id for O(depth) lookup.
    chain_a: set[int] = set()
    node: "Node | None" = a
    while node is not None:
        chain_a.add(id(node))
        node = node._parent

    # Walk b's chain upward until a match is found.
    node = b
    while node is not None:
        if id(node) in chain_a:
            # Verify by identity to guard against id reuse (rare in practice).
            candidate = node
            # Walk a's chain again to confirm identity.
            check: "Node | None" = a
            while check is not None:
                if check is candidate:
                    return candidate
                check = check._parent
            # id collision — continue walking b's chain.
        node = node._parent

    # Should never happen if a and b are in the same tree.
    raise ValueError("nodes have no common ancestor")


def _is_character_data(node: "Node") -> bool:
    """Return True if *node* is a CharacterData node (Text, Comment, CDATA, PI)."""
    from aspose_html.dom._node_type import NodeType  # noqa: PLC0415
    return node._node_type in (
        NodeType.TEXT_NODE,
        NodeType.COMMENT_NODE,
        NodeType.CDATA_SECTION_NODE,
        NodeType.PROCESSING_INSTRUCTION_NODE,
    )


def _node_document(node: "Node") -> "Document | None":
    """Return the owning Document for *node*, including Document itself."""
    from aspose_html.dom._node_type import NodeType  # noqa: PLC0415

    if node._node_type == NodeType.DOCUMENT_NODE:
        return node  # type: ignore[return-value]
    return node._owner_document


def _is_descendant_or_self(node: "Node", ancestor: "Node") -> bool:
    """Return True if *node* is *ancestor* or is below it."""
    cur: "Node | None" = node
    while cur is not None:
        if cur is ancestor:
            return True
        cur = cur._parent
    return False


def _is_contained(
    node: "Node",
    start_container: "Node",
    start_offset: int,
    end_container: "Node",
    end_offset: int,
) -> bool:
    """Return True if *node* is fully contained within the range.

    A node is fully contained if both the boundary point just before it
    and the boundary point just after it are within the range (inclusive).

    Per WHATWG DOM §5.2 "contained" definition.
    """
    parent = node._parent
    if parent is None:
        return False
    idx = parent._children.index(node)
    return (
        _bp_lte((start_container, start_offset), (parent, idx))
        and _bp_lte((parent, idx + 1), (end_container, end_offset))
    )


def _nodes_in_document_order(root: "Node") -> "list[Node]":
    """Return all descendants of *root* in document (pre-)order, *root* first."""
    result: list[Node] = []
    stack = [root]
    while stack:
        node = stack.pop(0)
        result.append(node)
        stack[:0] = node._children
    return result


# ---------------------------------------------------------------------------
# AbstractRange / Range classes
# ---------------------------------------------------------------------------


class AbstractRange:
    """Read-only boundary-point contract shared by range-family APIs.

    Defines the start/end container+offset properties and ``collapsed``.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> r = doc.create_range()
    >>> isinstance(r, AbstractRange)
    True
    >>> r.collapsed
    True
    """

    __slots__ = ()

    @property
    def start_container(self) -> "Node":
        """The node that contains the start of the range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> r.start_container is doc
        True
        """
        return self._start_container  # type: ignore[attr-defined]

    @property
    def start_offset(self) -> int:
        """The offset within ``start_container``.

        For CharacterData nodes: character offset.
        For other nodes: child-node index.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> r.start_offset
        0
        """
        return self._start_offset  # type: ignore[attr-defined]

    @property
    def end_container(self) -> "Node":
        """The node that contains the end of the range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> r.end_container is doc
        True
        """
        return self._end_container  # type: ignore[attr-defined]

    @property
    def end_offset(self) -> int:
        """The offset within ``end_container``.

        For CharacterData nodes: character offset.
        For other nodes: child-node index.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> r.end_offset
        0
        """
        return self._end_offset  # type: ignore[attr-defined]

    @property
    def collapsed(self) -> bool:
        """True if the start and end boundary points are identical.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> r.collapsed
        True
        """
        return (
            self._start_container is self._end_container  # type: ignore[attr-defined]
            and self._start_offset == self._end_offset  # type: ignore[attr-defined]
        )


class StaticRange(AbstractRange):
    """Immutable boundary-point range initialized from an init object.

    Unlike live ``Range`` objects, ``StaticRange`` endpoints do not auto-update
    on DOM mutations and cannot be changed after construction.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> root = doc.create_element("root")
    >>> _ = doc.append_child(root)
    >>> t = doc.create_text_node("hello")
    >>> _ = root.append_child(t)
    >>> sr = StaticRange({
    ...     "start_container": t,
    ...     "start_offset": 1,
    ...     "end_container": t,
    ...     "end_offset": 4,
    ... })
    >>> sr.to_string()
    'ell'
    >>> sr.start_offset = 0  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    AttributeError: ...
    """

    __slots__ = (
        "_start_container",
        "_start_offset",
        "_end_container",
        "_end_offset",
    )

    def __init__(self, init: dict) -> None:
        """Create an immutable range from endpoint init fields.

        Required keys: ``start_container``, ``start_offset``,
        ``end_container``, ``end_offset``.
        """
        if not isinstance(init, dict):
            raise TypeError("StaticRange init must be a dict")

        required_keys = (
            "start_container",
            "start_offset",
            "end_container",
            "end_offset",
        )
        missing = [k for k in required_keys if k not in init]
        if missing:
            raise TypeError(f"StaticRange init missing required key(s): {', '.join(missing)}")

        start_container = init["start_container"]
        end_container = init["end_container"]
        start_offset = init["start_offset"]
        end_offset = init["end_offset"]

        from aspose_html.dom._node import Node as _Node  # noqa: PLC0415
        from aspose_html.dom._exceptions import WrongDocumentError  # noqa: PLC0415

        if not isinstance(start_container, _Node):
            raise TypeError("start_container must be a Node")
        if not isinstance(end_container, _Node):
            raise TypeError("end_container must be a Node")
        if not isinstance(start_offset, int):
            raise TypeError("start_offset must be an int")
        if not isinstance(end_offset, int):
            raise TypeError("end_offset must be an int")

        _validate_offset(start_container, start_offset)
        _validate_offset(end_container, end_offset)

        start_doc = _node_document(start_container)
        end_doc = _node_document(end_container)
        if start_doc is not end_doc:
            raise WrongDocumentError("start_container and end_container must belong to the same document")

        if not _bp_lte((start_container, start_offset), (end_container, end_offset)):
            raise TypeError("StaticRange start boundary must not be after end boundary")

        self._start_container = start_container
        self._start_offset = start_offset
        self._end_container = end_container
        self._end_offset = end_offset

    def to_string(self) -> str:
        """Return text content within this static range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> t = doc.create_text_node("abcdef")
        >>> _ = p.append_child(t)
        >>> sr = StaticRange({
        ...     "start_container": t,
        ...     "start_offset": 2,
        ...     "end_container": t,
        ...     "end_offset": 5,
        ... })
        >>> sr.to_string()
        'cde'
        """
        temp = Range(self._start_container)
        temp._start_container = self._start_container
        temp._start_offset = self._start_offset
        temp._end_container = self._end_container
        temp._end_offset = self._end_offset
        return temp.to_string()


class Range(AbstractRange):
    """A contiguous portion of a document tree (WHATWG DOM §5).

    Create via ``Document.create_range()`` — do not instantiate directly.

    A Range is defined by two boundary points:

    - ``(start_container, start_offset)``
    - ``(end_container, end_offset)``

    For CharacterData nodes (Text, Comment, CDATASection,
    ProcessingInstruction), offset is a character index (0 to
    ``len(node.data)`` inclusive). For all other nodes, offset is a
    child-node index (0 to ``len(node._children)`` inclusive).

    Boundary points are live: child-list and character-data mutations update
    outstanding ranges through the owning document's internal mutation signal.

    : method names are snake_case equivalents of the WHATWG IDL names.
    : all public methods carry type hints and docstrings.
    : boundary semantics per WHATWG DOM §5.

    See  and .

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> r = doc.create_range()
    >>> r.collapsed
    True
    >>> r.start_container is doc
    True
    """

    __slots__ = (
        "_start_container",
        "_start_offset",
        "_end_container",
        "_end_offset",
        "_owner_document",
        "_detached",
        "__weakref__",
    )

    START_TO_START = 0
    START_TO_END = 1
    END_TO_END = 2
    END_TO_START = 3

    def __init__(self, owner_document: "Node") -> None:
        """Create a collapsed range at (owner_document, 0).

        Do not instantiate directly — use ``Document.create_range()``.

        Parameters
        ----------
        owner_document : Node
            The document node that anchors this range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> r.start_container is doc
        True
        >>> r.start_offset
        0
        """
        self._start_container: "Node" = owner_document
        self._start_offset: int = 0
        self._end_container: "Node" = owner_document
        self._end_offset: int = 0
        self._owner_document: "Document | None" = None
        self._detached: bool = False
        self._sync_owner_document()

    def _sync_owner_document(self) -> None:
        """Keep this live range registered with its current owner document."""
        if self._detached:
            return
        doc = _node_document(self._start_container) or _node_document(self._end_container)
        if doc is self._owner_document:
            return
        if self._owner_document is not None:
            self._owner_document._unregister_range(self)
        self._owner_document = doc
        if doc is not None:
            doc._register_range(self)

    def _removed_index(
        self,
        target: "Node",
        removed: tuple["Node", ...],
        previous_sibling: "Node | None",
        next_sibling: "Node | None",
    ) -> int:
        if removed and removed[0] in target._children:
            return target._children.index(removed[0])
        if previous_sibling is not None and previous_sibling in target._children:
            return target._children.index(previous_sibling) + 1
        if next_sibling is not None and next_sibling in target._children:
            return target._children.index(next_sibling)
        return len(target._children)

    def _adjust_boundary_for_child_list(
        self,
        container: "Node",
        offset: int,
        target: "Node",
        added: tuple["Node", ...],
        removed: tuple["Node", ...],
        previous_sibling: "Node | None",
        next_sibling: "Node | None",
    ) -> "tuple[Node, int]":
        if removed:
            removed_index = self._removed_index(target, removed, previous_sibling, next_sibling)
            for removed_node in removed:
                if _is_descendant_or_self(container, removed_node):
                    return target, removed_index
            if container is target and offset > removed_index:
                return container, max(removed_index, offset - len(removed))

        if added and container is target:
            insertion_index = target._children.index(added[0])
            if offset >= insertion_index:
                return container, offset + len(added)

        return container, offset

    def _handle_child_list_mutation(
        self,
        target: "Node",
        added: tuple["Node", ...],
        removed: tuple["Node", ...],
        previous_sibling: "Node | None",
        next_sibling: "Node | None",
    ) -> None:
        """Update boundary points after a child-list mutation."""
        if self._detached:
            return
        self._start_container, self._start_offset = self._adjust_boundary_for_child_list(
            self._start_container,
            self._start_offset,
            target,
            added,
            removed,
            previous_sibling,
            next_sibling,
        )
        self._end_container, self._end_offset = self._adjust_boundary_for_child_list(
            self._end_container,
            self._end_offset,
            target,
            added,
            removed,
            previous_sibling,
            next_sibling,
        )
        self._sync_owner_document()

    def _handle_character_data_mutation(self, target: "Node") -> None:
        """Clamp boundary points after a character-data mutation."""
        if self._detached:
            return
        max_offset = _max_offset(target)
        if self._start_container is target and self._start_offset > max_offset:
            self._start_offset = max_offset
        if self._end_container is target and self._end_offset > max_offset:
            self._end_offset = max_offset

    @property
    def common_ancestor_container(self) -> "Node":
        """The deepest node that contains both boundary points.

        Computed on each read by walking ancestor chains.
        Per WHATWG DOM §5.2.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> r = doc.create_range()
        >>> r.select_node_contents(div)
        >>> r.common_ancestor_container is div
        True
        """
        return _common_ancestor(self._start_container, self._end_container)

    # ------------------------------------------------------------------
    # Boundary setters
    # ------------------------------------------------------------------

    def set_start(self, node: "Node", offset: int) -> None:
        """Set the start boundary of the range.

        If the new start is after the current end, the range is collapsed
        to the new start. Per WHATWG DOM §5.3.5.

        Parameters
        ----------
        node : Node
            The container node for the start boundary.
        offset : int
            The offset within *node*. For CharacterData nodes: character
            offset. For other nodes: child-node index.

        Raises
        ------
        IndexSizeError
            If *offset* is negative or exceeds the maximum valid offset.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> t = doc.create_text_node("hello")
        >>> _ = p.append_child(t)
        >>> r = doc.create_range()
        >>> r.set_start(t, 2)
        >>> r.start_container is t
        True
        >>> r.start_offset
        2
        """
        _validate_offset(node, offset)
        self._start_container = node
        self._start_offset = offset
        # : if start > end, collapse to start per WHATWG §5.3.5.
        if not _bp_lte(
            (self._start_container, self._start_offset),
            (self._end_container, self._end_offset),
        ):
            self._end_container = node
            self._end_offset = offset
        self._sync_owner_document()

    def set_end(self, node: "Node", offset: int) -> None:
        """Set the end boundary of the range.

        If the new end is before the current start, the range is collapsed
        to the new end. Per WHATWG DOM §5.3.6.

        Parameters
        ----------
        node : Node
            The container node for the end boundary.
        offset : int
            The offset within *node*. For CharacterData nodes: character
            offset. For other nodes: child-node index.

        Raises
        ------
        IndexSizeError
            If *offset* is negative or exceeds the maximum valid offset.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> t = doc.create_text_node("hello")
        >>> _ = p.append_child(t)
        >>> r = doc.create_range()
        >>> r.set_end(t, 4)
        >>> r.end_offset
        4
        """
        _validate_offset(node, offset)
        self._end_container = node
        self._end_offset = offset
        # : if end < start, collapse to end per WHATWG §5.3.6.
        if not _bp_lte(
            (self._start_container, self._start_offset),
            (self._end_container, self._end_offset),
        ):
            self._start_container = node
            self._start_offset = offset
        self._sync_owner_document()

    def set_start_before(self, node: "Node") -> None:
        """Set the start to the position just before *node* in its parent.

        Equivalent to ``set_start(node.parent_node, index_of(node))``.
        Per WHATWG DOM §5.3.7.

        Parameters
        ----------
        node : Node
            The reference node. Must have a parent.

        Raises
        ------
        InvalidStateError
            If *node* has no parent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> span = doc.create_element("span")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(span)
        >>> r = doc.create_range()
        >>> r.set_start_before(span)
        >>> r.start_offset
        0
        """
        parent = node._parent
        if parent is None:
            from aspose_html.dom._exceptions import InvalidStateError  # noqa: PLC0415
            raise InvalidStateError("node has no parent")
        self.set_start(parent, parent._children.index(node))

    def set_start_after(self, node: "Node") -> None:
        """Set the start to the position just after *node* in its parent.

        Equivalent to ``set_start(node.parent_node, index_of(node) + 1)``.
        Per WHATWG DOM §5.3.8.

        Parameters
        ----------
        node : Node
            The reference node. Must have a parent.

        Raises
        ------
        InvalidStateError
            If *node* has no parent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> span = doc.create_element("span")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(span)
        >>> r = doc.create_range()
        >>> r.set_start_after(span)
        >>> r.start_offset
        1
        """
        parent = node._parent
        if parent is None:
            from aspose_html.dom._exceptions import InvalidStateError  # noqa: PLC0415
            raise InvalidStateError("node has no parent")
        self.set_start(parent, parent._children.index(node) + 1)

    def set_end_before(self, node: "Node") -> None:
        """Set the end to the position just before *node* in its parent.

        Equivalent to ``set_end(node.parent_node, index_of(node))``.
        Per WHATWG DOM §5.3.9.

        Parameters
        ----------
        node : Node
            The reference node. Must have a parent.

        Raises
        ------
        InvalidStateError
            If *node* has no parent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> span = doc.create_element("span")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(span)
        >>> r = doc.create_range()
        >>> r.set_end_before(span)
        >>> r.end_offset
        0
        """
        parent = node._parent
        if parent is None:
            from aspose_html.dom._exceptions import InvalidStateError  # noqa: PLC0415
            raise InvalidStateError("node has no parent")
        self.set_end(parent, parent._children.index(node))

    def set_end_after(self, node: "Node") -> None:
        """Set the end to the position just after *node* in its parent.

        Equivalent to ``set_end(node.parent_node, index_of(node) + 1)``.
        Per WHATWG DOM §5.3.10.

        Parameters
        ----------
        node : Node
            The reference node. Must have a parent.

        Raises
        ------
        InvalidStateError
            If *node* has no parent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> span = doc.create_element("span")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(span)
        >>> r = doc.create_range()
        >>> r.set_end_after(span)
        >>> r.end_offset
        1
        """
        parent = node._parent
        if parent is None:
            from aspose_html.dom._exceptions import InvalidStateError  # noqa: PLC0415
            raise InvalidStateError("node has no parent")
        self.set_end(parent, parent._children.index(node) + 1)

    def collapse(self, to_start: bool = True) -> None:
        """Collapse the range to its start or end boundary point.

        Parameters
        ----------
        to_start : bool, optional
            If True (default), collapse to the start. If False, collapse
            to the end.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> t = doc.create_text_node("hello")
        >>> _ = p.append_child(t)
        >>> r = doc.create_range()
        >>> r.set_start(t, 1)
        >>> r.set_end(t, 4)
        >>> r.collapse(to_start=True)
        >>> r.collapsed
        True
        >>> r.start_offset
        1
        """
        if to_start:
            self._end_container = self._start_container
            self._end_offset = self._start_offset
        else:
            self._start_container = self._end_container
            self._start_offset = self._end_offset

    def select_node(self, node: "Node") -> None:
        """Select *node* and all its contents.

        Sets start to just before *node* and end to just after *node*
        within *node*'s parent. Per WHATWG DOM §5.3.11.

        Parameters
        ----------
        node : Node
            The node to select. Must have a parent.

        Raises
        ------
        InvalidStateError
            If *node* has no parent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> r = doc.create_range()
        >>> r.select_node(div)
        >>> r.start_container is doc
        True
        >>> r.end_container is doc
        True
        >>> r.start_offset
        0
        >>> r.end_offset
        1
        """
        parent = node._parent
        if parent is None:
            from aspose_html.dom._exceptions import InvalidStateError  # noqa: PLC0415
            raise InvalidStateError("node has no parent")
        idx = parent._children.index(node)
        self._start_container = parent
        self._start_offset = idx
        self._end_container = parent
        self._end_offset = idx + 1
        self._sync_owner_document()

    def select_node_contents(self, node: "Node") -> None:
        """Select the contents of *node* (not the node itself).

        Sets start to (node, 0) and end to (node, len(node.children))
        or (node, len(node.data)) for CharacterData nodes.
        Per WHATWG DOM §5.3.12.

        Parameters
        ----------
        node : Node
            The node whose contents are to be selected.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(doc.create_text_node("hi"))
        >>> r = doc.create_range()
        >>> r.select_node_contents(div)
        >>> r.start_container is div
        True
        >>> r.start_offset
        0
        >>> r.end_offset
        1
        """
        self._start_container = node
        self._start_offset = 0
        self._end_container = node
        self._end_offset = _max_offset(node)
        self._sync_owner_document()

    # ------------------------------------------------------------------
    # Content manipulation
    # ------------------------------------------------------------------

    def _make_fragment(self) -> "DocumentFragment":
        """Create an output DocumentFragment owned by the right document.

        The fragment's owner document is ``start_container.owner_document``,
        or ``start_container`` itself when start_container is a Document node
        (because Document._owner_document is None per WHATWG).
        """
        from aspose_html.dom._document_fragment import DocumentFragment  # noqa: PLC0415
        from aspose_html.dom._node_type import NodeType  # noqa: PLC0415

        owner_doc = self._start_container._owner_document
        if owner_doc is None and self._start_container._node_type == NodeType.DOCUMENT_NODE:
            # start_container IS the Document — use it as owner.
            owner_doc = self._start_container  # type: ignore[assignment]
        return DocumentFragment(owner_document=owner_doc)  # type: ignore[arg-type]

    def _process_partial_start(
        self,
        node: "Node",
        start_container: "Node",
        start_offset: int,
        remove: bool,
    ) -> "Node":
        """Build a clone of *node* containing only its portion from start.

        ``node`` is an inclusive ancestor of ``start_container``. The
        returned clone is shallow-copied from ``node`` and populated with
        content from ``start_container`` onward (per WHATWG DOM §5.4.3
        partial-extract recursion).

        When ``remove=True``, the matching content is removed from
        ``node`` in the live tree.
        """
        clone = node._clone_self()  # noqa: SLF001 — shallow same-type clone

        # Special case: node itself is the start_container — take its child
        # nodes from start_offset onwards (only happens at the top level
        # when start_container is the partial-start ancestor itself).
        if start_container is node:
            children = list(node._children[start_offset:])
            if remove:
                for c in children:
                    node.remove_child(c)
                    clone.append_child(c)
            else:
                for c in children:
                    clone.append_child(c.clone_node(deep=True))
            return clone

        # Find the pivot child of *node* on the path to start_container.
        # If start_container is itself a child of node, pivot IS start_container.
        # Otherwise the pivot is the ancestor of start_container that is a
        # direct child of node.
        pivot: "Node" = start_container
        while pivot._parent is not node:
            assert pivot._parent is not None  # noqa: S101 — guaranteed by ancestry check
            pivot = pivot._parent
        pivot_idx = node._children.index(pivot)

        # 1. Process the pivot child.
        if pivot is start_container:
            # Pivot IS the start container.
            if _is_character_data(pivot):
                # Take a partial slice from start_offset to end of data.
                data = pivot._data  # type: ignore[attr-defined]
                if data[start_offset:]:
                    pivot_clone = pivot._clone_self()  # noqa: SLF001
                    pivot_clone._data = data[start_offset:]  # type: ignore[attr-defined]
                    clone.append_child(pivot_clone)
                if remove:
                    pivot._data = data[:start_offset]  # type: ignore[attr-defined]
            else:
                # Take child nodes from start_offset onwards.
                pivot_children = list(pivot._children[start_offset:])
                if remove:
                    for c in pivot_children:
                        pivot.remove_child(c)
                        clone.append_child(c)
                else:
                    for c in pivot_children:
                        clone.append_child(c.clone_node(deep=True))
        else:
            # Pivot CONTAINS start_container — recurse.
            sub_clone = self._process_partial_start(
                pivot, start_container, start_offset, remove
            )
            clone.append_child(sub_clone)

        # 2. Append remaining siblings of pivot (those after pivot_idx).
        # These are entirely within the range so they move/clone fully.
        trailing = list(node._children[pivot_idx + 1 :])
        if remove:
            for c in trailing:
                node.remove_child(c)
                clone.append_child(c)
        else:
            for c in trailing:
                clone.append_child(c.clone_node(deep=True))

        return clone

    def _process_partial_end(
        self,
        node: "Node",
        end_container: "Node",
        end_offset: int,
        remove: bool,
    ) -> "Node":
        """Build a clone of *node* containing only its portion up to end.

        Symmetric counterpart of :meth:`_process_partial_start`.
        Per WHATWG DOM §5.4.3.
        """
        clone = node._clone_self()  # noqa: SLF001

        if end_container is node:
            children = list(node._children[:end_offset])
            if remove:
                for c in children:
                    node.remove_child(c)
                    clone.append_child(c)
            else:
                for c in children:
                    clone.append_child(c.clone_node(deep=True))
            return clone

        pivot: "Node" = end_container
        while pivot._parent is not node:
            assert pivot._parent is not None  # noqa: S101
            pivot = pivot._parent
        pivot_idx = node._children.index(pivot)

        # 1. Append leading siblings of pivot (those before pivot_idx).
        leading = list(node._children[:pivot_idx])
        if remove:
            for c in leading:
                node.remove_child(c)
                clone.append_child(c)
        else:
            for c in leading:
                clone.append_child(c.clone_node(deep=True))

        # 2. Process the pivot child.
        if pivot is end_container:
            if _is_character_data(pivot):
                data = pivot._data  # type: ignore[attr-defined]
                if data[:end_offset]:
                    pivot_clone = pivot._clone_self()  # noqa: SLF001
                    pivot_clone._data = data[:end_offset]  # type: ignore[attr-defined]
                    clone.append_child(pivot_clone)
                if remove:
                    pivot._data = data[end_offset:]  # type: ignore[attr-defined]
            else:
                pivot_children = list(pivot._children[:end_offset])
                if remove:
                    for c in pivot_children:
                        pivot.remove_child(c)
                        clone.append_child(c)
                else:
                    for c in pivot_children:
                        clone.append_child(c.clone_node(deep=True))
        else:
            # Pivot CONTAINS end_container — recurse.
            sub_clone = self._process_partial_end(
                pivot, end_container, end_offset, remove
            )
            clone.append_child(sub_clone)

        return clone

    def _extract(self, remove: bool) -> "DocumentFragment":
        """Shared implementation for extract_contents and clone_contents.

        Parameters
        ----------
        remove : bool
            If True, nodes are removed from the document (extract).
            If False, nodes are cloned in place (clone).

        Returns
        -------
        DocumentFragment
            A fragment containing the extracted/cloned content.

        Per WHATWG DOM §5.4.3 (extract) / §5.4.4 (clone).
        """
        fragment = self._make_fragment()

        # Step 2: collapsed range → return empty fragment.
        if self.collapsed:
            return fragment

        original_start_node = self._start_container
        original_start_offset = self._start_offset
        original_end_node = self._end_container
        original_end_offset = self._end_offset

        # Step 3: Same-container, CharacterData case.
        if original_start_node is original_end_node and _is_character_data(original_start_node):
            data = original_start_node._data  # type: ignore[attr-defined]
            cloned_data = data[original_start_offset:original_end_offset]
            clone = original_start_node._clone_self()  # noqa: SLF001
            clone._data = cloned_data  # type: ignore[attr-defined]
            fragment.append_child(clone)
            if remove:
                # Mutate the original: delete the selected substring.
                original_start_node._data = (  # type: ignore[attr-defined]
                    data[:original_start_offset] + data[original_end_offset:]
                )
                # Collapse range to its (preserved) start position.
                self._end_container = original_start_node
                self._end_offset = original_start_offset
            return fragment

        # Step 4: Same-container, non-CharacterData case.
        if original_start_node is original_end_node:
            children = list(
                original_start_node._children[original_start_offset:original_end_offset]
            )
            if remove:
                for child in children:
                    original_start_node.remove_child(child)
                    fragment.append_child(child)
                # Collapse range to start.
                self._end_container = original_start_node
                self._end_offset = original_start_offset
            else:
                for child in children:
                    fragment.append_child(child.clone_node(deep=True))
            return fragment

        # Step 5: Cross-container case.
        ancestor = _common_ancestor(original_start_node, original_end_node)

        # Step 5a/b: find the partially contained nodes.
        # A "first partially contained node" is the child of `ancestor`
        # that is an inclusive ancestor of start_container, when
        # start_container is itself not the ancestor.
        first_partially_contained: "Node | None" = None
        if original_start_node is not ancestor:
            walker: "Node" = original_start_node
            while walker._parent is not ancestor:
                assert walker._parent is not None  # noqa: S101
                walker = walker._parent
            first_partially_contained = walker

        last_partially_contained: "Node | None" = None
        if original_end_node is not ancestor:
            walker = original_end_node
            while walker._parent is not ancestor:
                assert walker._parent is not None  # noqa: S101
                walker = walker._parent
            last_partially_contained = walker

        # Step 6: build the slice of ancestor's children that are entirely
        # within the range. Determine bounds carefully when start_container
        # or end_container IS the ancestor — then the offset is a child
        # index directly.
        children_of_ancestor = list(ancestor._children)

        if first_partially_contained is not None:
            start_slice_idx = (
                children_of_ancestor.index(first_partially_contained) + 1
            )
        else:
            # start_container IS ancestor — offset is a child index.
            start_slice_idx = original_start_offset

        if last_partially_contained is not None:
            end_slice_idx = children_of_ancestor.index(last_partially_contained)
        else:
            end_slice_idx = original_end_offset

        contained_children = children_of_ancestor[start_slice_idx:end_slice_idx]

        # Step 7: process the first partially contained node (start side).
        if first_partially_contained is not None:
            if _is_character_data(first_partially_contained):
                data = first_partially_contained._data  # type: ignore[attr-defined]
                cloned_data = data[original_start_offset:]
                clone = first_partially_contained._clone_self()  # noqa: SLF001
                clone._data = cloned_data  # type: ignore[attr-defined]
                fragment.append_child(clone)
                if remove:
                    first_partially_contained._data = data[:original_start_offset]  # type: ignore[attr-defined]
            else:
                start_clone = self._process_partial_start(
                    first_partially_contained,
                    original_start_node,
                    original_start_offset,
                    remove,
                )
                fragment.append_child(start_clone)

        # Step 8: handle fully contained nodes.
        if remove:
            for child in contained_children:
                ancestor.remove_child(child)
                fragment.append_child(child)
        else:
            for child in contained_children:
                fragment.append_child(child.clone_node(deep=True))

        # Step 9: process the last partially contained node (end side).
        if last_partially_contained is not None:
            if _is_character_data(last_partially_contained):
                data = last_partially_contained._data  # type: ignore[attr-defined]
                cloned_data = data[:original_end_offset]
                clone = last_partially_contained._clone_self()  # noqa: SLF001
                clone._data = cloned_data  # type: ignore[attr-defined]
                fragment.append_child(clone)
                if remove:
                    last_partially_contained._data = data[original_end_offset:]  # type: ignore[attr-defined]
            else:
                end_clone = self._process_partial_end(
                    last_partially_contained,
                    original_end_node,
                    original_end_offset,
                    remove,
                )
                fragment.append_child(end_clone)

        # Step 10: collapse the live range to a single boundary point.
        # WHATWG specifies new boundary at (original common ancestor of the
        # *new* start node, …). The simple v1.0 invariant: collapse to the
        # original start position. If first_partially_contained was a
        # non-CharacterData ancestor, original_start_node may now be
        # detached; fall back to ancestor + index of first_partially_contained
        # (or 0 if first_partially_contained was removed entirely).
        if remove:
            if first_partially_contained is not None and _is_character_data(
                first_partially_contained
            ):
                # CharacterData: original_start_node is preserved; offset stays.
                self._start_container = first_partially_contained
                self._start_offset = original_start_offset
            elif first_partially_contained is not None:
                # Non-CharacterData ancestor: position just after it (its
                # interior portion was preserved when remove=True kept
                # the leading children of the start side). For simplicity
                # collapse to ancestor at the index of first_partially_contained
                # plus one.
                self._start_container = ancestor
                self._start_offset = (
                    ancestor._children.index(first_partially_contained) + 1
                    if first_partially_contained in ancestor._children
                    else 0
                )
            else:
                # start_container was the ancestor itself.
                self._start_container = ancestor
                self._start_offset = original_start_offset
            self._end_container = self._start_container
            self._end_offset = self._start_offset

        return fragment

    def extract_contents(self) -> "DocumentFragment":
        """Remove and return the selected content as a DocumentFragment.

        Partial CharacterData nodes at boundaries are split at the boundary
        offsets. The range is collapsed to its original start position after
        extraction.

        Live range boundary points are updated when child-list or
        character-data mutations occur through DOM primitives.

        Returns
        -------
        DocumentFragment
            A fragment containing all removed nodes and partial text.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(doc.create_text_node("hello"))
        >>> r = doc.create_range()
        >>> r.select_node_contents(div)
        >>> frag = r.extract_contents()
        >>> frag.first_child.data
        'hello'
        >>> len(div.child_nodes)
        0
        """
        return self._extract(remove=True)

    def clone_contents(self) -> "DocumentFragment":
        """Return a DocumentFragment with deep copies of the selected content.

        The document is not modified.

        Returns
        -------
        DocumentFragment
            A fragment containing deep clones of all selected nodes.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(doc.create_text_node("hello"))
        >>> r = doc.create_range()
        >>> r.select_node_contents(div)
        >>> frag = r.clone_contents()
        >>> frag.first_child.data
        'hello'
        >>> len(div.child_nodes)
        1
        """
        return self._extract(remove=False)

    def delete_contents(self) -> None:
        """Remove the selected content from the document.

        Equivalent to calling ``extract_contents()`` and discarding the
        returned fragment.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(doc.create_text_node("hello"))
        >>> r = doc.create_range()
        >>> r.select_node_contents(div)
        >>> r.delete_contents()
        >>> len(div.child_nodes)
        0
        """
        self._extract(remove=True)

    def insert_node(self, node: "Node") -> None:
        """Insert *node* at the start of the range.

        If ``start_container`` is a CharacterData node, it is split at
        ``start_offset`` and *node* is inserted before the right half.
        Otherwise *node* is inserted as a child of ``start_container``
        at index ``start_offset``.

        Per WHATWG DOM §5.4.6.

        Parameters
        ----------
        node : Node
            The node to insert.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> span = doc.create_element("span")
        >>> r = doc.create_range()
        >>> r.select_node_contents(div)
        >>> r.insert_node(span)
        >>> div.first_child is span
        True
        """
        sc = self._start_container
        so = self._start_offset
        if _is_character_data(sc):
            # Split the CharacterData at start_offset.
            # After split: right_half = sc.next_sibling (inserted in parent).
            # We insert *node* before right_half.
            right_half = sc.split_text(so)  # type: ignore[attr-defined]
            # split_text inserts right_half into sc's parent automatically.
            parent = right_half._parent
            if parent is not None:
                parent.insert_before(node, right_half)
            else:
                # sc was detached — right_half has no parent.
                # Insert node before right_half by appending to sc's parent.
                # In detached case we cannot insert structurally — no-op guard.
                pass
        else:
            # Insert as child of sc at index so.
            ref = sc._children[so] if so < len(sc._children) else None
            sc.insert_before(node, ref)

    def surround_contents(self, new_parent: "Node") -> None:
        """Surround the range's contents with *new_parent*.

        Equivalent to extracting contents, appending them to *new_parent*,
        then inserting *new_parent* at the start of the range.

        Per WHATWG DOM §5.4.7 (simplified).

        Parameters
        ----------
        new_parent : Node
            The node that will wrap the range's contents.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> _ = div.append_child(doc.create_text_node("hello"))
        >>> r = doc.create_range()
        >>> r.select_node_contents(div)
        >>> wrapper = doc.create_element("span")
        >>> r.surround_contents(wrapper)
        >>> div.first_child is wrapper
        True
        >>> wrapper.first_child.data
        'hello'
        """
        frag = self.extract_contents()
        self.insert_node(new_parent)
        new_parent.append_child(frag)
        self.select_node_contents(new_parent)

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def clone_range(self) -> "Range":
        """Return a new Range with identical boundary points.

        The returned range is independent of this range — modifying one
        does not affect the other.

        Returns
        -------
        Range
            A new Range with the same start and end boundary points.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> r2 = r.clone_range()
        >>> r2 is not r
        True
        >>> r2.collapsed
        True
        """
        r = Range(self._start_container)
        r._start_container = self._start_container
        r._start_offset = self._start_offset
        r._end_container = self._end_container
        r._end_offset = self._end_offset
        r._sync_owner_document()
        return r

    def detach(self) -> None:
        """Unregister this range from live mutation tracking.

        The boundary points remain readable, but future DOM mutations no longer
        update this range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> r.detach()
        """
        if self._owner_document is not None:
            self._owner_document._unregister_range(self)
        self._owner_document = None
        self._detached = True

    def is_point_in_range(self, node: "Node", offset: int) -> bool:
        """Return True if (node, offset) falls within the range (inclusive).

        Per WHATWG DOM §5.5.1.

        Parameters
        ----------
        node : Node
            The node to test.
        offset : int
            The offset within *node*.

        Returns
        -------
        bool
            True if the point is within the range (start <= point <= end).

        Raises
        ------
        IndexSizeError
            If *offset* exceeds the maximum valid offset for *node*.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> t = doc.create_text_node("hello")
        >>> _ = p.append_child(t)
        >>> r = doc.create_range()
        >>> r.set_start(t, 1)
        >>> r.set_end(t, 4)
        >>> r.is_point_in_range(t, 2)
        True
        >>> r.is_point_in_range(t, 0)
        False
        """
        if offset > _max_offset(node):
            from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415
            raise IndexSizeError(f"offset {offset} out of range")
        point = (node, offset)
        return (
            _bp_lte((self._start_container, self._start_offset), point)
            and _bp_lte(point, (self._end_container, self._end_offset))
        )

    def compare_point(self, node: "Node", offset: int) -> int:
        """Return -1, 0, or 1 comparing (node, offset) against the range.

        Per WHATWG DOM §5.5.2.

        Parameters
        ----------
        node : Node
            The node to compare.
        offset : int
            The offset within *node*.

        Returns
        -------
        int
            -1 if the point is before the range start.
             0 if the point is within the range (inclusive).
             1 if the point is after the range end.

        Raises
        ------
        IndexSizeError
            If *offset* exceeds the maximum valid offset for *node*.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> t = doc.create_text_node("hello")
        >>> _ = p.append_child(t)
        >>> r = doc.create_range()
        >>> r.set_start(t, 1)
        >>> r.set_end(t, 4)
        >>> r.compare_point(t, 0)
        -1
        >>> r.compare_point(t, 2)
        0
        >>> r.compare_point(t, 5)
        1
        """
        if offset > _max_offset(node):
            from aspose_html.dom._exceptions import IndexSizeError  # noqa: PLC0415
            raise IndexSizeError(f"offset {offset} out of range")
        if not _bp_lte((self._start_container, self._start_offset), (node, offset)):
            return -1
        if not _bp_lte((node, offset), (self._end_container, self._end_offset)):
            return 1
        return 0

    def compare_boundary_points(self, how: int, source_range: "Range") -> int:
        """Compare this range with ``source_range`` using boundary mode ``how``.

        Parameters
        ----------
        how : int
            One of ``Range.START_TO_START``, ``Range.START_TO_END``,
            ``Range.END_TO_END``, ``Range.END_TO_START``.
        source_range : Range
            The range whose boundary point participates in the comparison.

        Returns
        -------
        int
            ``-1`` when this range's selected boundary point is before the
            source boundary point, ``0`` when equal, ``1`` when after.

        Examples
        --------
        >>> from aspose_html.dom import Document, Range
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = doc.append_child(host)
        >>> t = doc.create_text_node("hello")
        >>> _ = host.append_child(t)
        >>> left = doc.create_range()
        >>> left.set_start(t, 1)
        >>> left.set_end(t, 2)
        >>> right = doc.create_range()
        >>> right.set_start(t, 3)
        >>> right.set_end(t, 4)
        >>> left.compare_boundary_points(Range.START_TO_START, right)
        -1
        >>> left.compare_boundary_points(Range.END_TO_END, right)
        -1
        """
        from aspose_html.dom._exceptions import (  # noqa: PLC0415
            NotSupportedError,
            WrongDocumentError,
        )

        this_root = self._start_container
        while this_root._parent is not None:
            this_root = this_root._parent

        source_root = source_range._start_container
        while source_root._parent is not None:
            source_root = source_root._parent

        if this_root is not source_root:
            raise WrongDocumentError("Ranges belong to different documents")

        if how == self.START_TO_START:
            this_point = (self._start_container, self._start_offset)
            source_point = (source_range._start_container, source_range._start_offset)
        elif how == self.START_TO_END:
            this_point = (self._end_container, self._end_offset)
            source_point = (source_range._start_container, source_range._start_offset)
        elif how == self.END_TO_END:
            this_point = (self._end_container, self._end_offset)
            source_point = (source_range._end_container, source_range._end_offset)
        elif how == self.END_TO_START:
            this_point = (self._start_container, self._start_offset)
            source_point = (source_range._end_container, source_range._end_offset)
        else:
            raise NotSupportedError("how must be one of Range boundary comparison constants")

        return _bp_compare(this_point, source_point)

    def create_contextual_fragment(self, fragment: str) -> "DocumentFragment":
        """Parse ``fragment`` in this range's start-boundary element context.

        For the baseline behavior (), element-start ranges use
        ``start_container`` as the HTML fragment parsing context.

        Parameters
        ----------
        fragment : str
            HTML markup to parse.

        Returns
        -------
        DocumentFragment
            A new fragment owned by this range's owner document containing
            the parsed nodes.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = doc.append_child(host)
        >>> r = doc.create_range()
        >>> r.select_node_contents(host)
        >>> frag = r.create_contextual_fragment("<p>ok</p>")
        >>> frag.first_child.tag_name
        'P'
        >>> frag.owner_document is doc
        True
        """
        from aspose_html.dom._node import _adopt  # noqa: PLC0415
        from aspose_html.dom._node_type import NodeType  # noqa: PLC0415
        from aspose_html.html_document import HTMLDocument as _HTMLDocument  # noqa: PLC0415

        context_element = None
        start = self._start_container
        if start._node_type == NodeType.ELEMENT_NODE:
            context_element = start  # type: ignore[assignment]
        elif start._node_type in (NodeType.TEXT_NODE, NodeType.COMMENT_NODE):
            parent = start._parent
            if parent is not None and parent._node_type == NodeType.ELEMENT_NODE:
                context_element = parent  # type: ignore[assignment]

        # WHATWG HTML fragment parsing edge rule: if the effective context is
        # <html>, parse as if context were <body>.
        if (
            context_element is not None
            and getattr(context_element, "_tag_name", None) == "HTML"
        ):
            owner_doc = context_element._owner_document
            if owner_doc is not None and getattr(owner_doc, "body", None) is not None:
                context_element = owner_doc.body

        parsed = _HTMLDocument.parse_fragment(fragment, context_element=context_element)
        out = self._make_fragment()
        target_doc = out.owner_document
        for child in list(parsed.child_nodes):
            _adopt(child, target_doc)
            out.append_child(child)
        return out

    def intersects_node(self, node: "Node") -> bool:
        """Return True if *node* is partially or fully within the range.

        Per WHATWG DOM §5.5.3.

        Parameters
        ----------
        node : Node
            The node to test.

        Returns
        -------
        bool
            True if the node intersects the range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> r = doc.create_range()
        >>> r.select_node_contents(div)
        >>> r.intersects_node(div)
        True
        """
        parent = node._parent
        if parent is None:
            # Detached node: intersects only if it IS a boundary container.
            return (
                node is self._start_container
                or node is self._end_container
            )
        idx = parent._children.index(node)
        # Node is entirely before range if (parent, idx+1) <= (start, start_offset).
        if _bp_lte((parent, idx + 1), (self._start_container, self._start_offset)):
            return False
        # Node is entirely after range if (end, end_offset) <= (parent, idx).
        if _bp_lte((self._end_container, self._end_offset), (parent, idx)):
            return False
        return True

    def to_string(self) -> str:
        """Return the concatenated text content of the range.

        Visits all nodes in the range in document order. CharacterData
        nodes (Text, CDATASection) contribute their relevant substring.
        Other node types contribute nothing directly (their descendant
        CharacterData nodes are visited separately).

        Returns
        -------
        str
            The text of all CharacterData nodes within the range,
            with partial-boundary nodes trimmed to the range boundaries.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> t = doc.create_text_node("hello world")
        >>> _ = p.append_child(t)
        >>> r = doc.create_range()
        >>> r.set_start(t, 0)
        >>> r.set_end(t, 5)
        >>> r.to_string()
        'hello'
        """
        from aspose_html.dom._node_type import NodeType  # noqa: PLC0415

        if self.collapsed:
            return ""

        parts: list[str] = []
        start_node = self._start_container
        start_off = self._start_offset
        end_node = self._end_container
        end_off = self._end_offset

        # Same-container case.
        if start_node is end_node:
            if _is_character_data(start_node) and start_node._node_type == NodeType.TEXT_NODE:
                parts.append(start_node._data[start_off:end_off])  # type: ignore[attr-defined]
            return "".join(parts)

        # Cross-container: walk all text nodes within the range.
        ancestor = _common_ancestor(start_node, end_node)
        for node in _nodes_in_document_order(ancestor):
            if node._node_type != NodeType.TEXT_NODE:
                continue
            data = node._data  # type: ignore[attr-defined]
            if node is start_node:
                parts.append(data[start_off:])
            elif node is end_node:
                parts.append(data[:end_off])
            elif _is_contained(node, start_node, start_off, end_node, end_off):
                parts.append(data)

        return "".join(parts)

    def __repr__(self) -> str:
        return (
            f"<Range [{self._start_container!r}:{self._start_offset}"
            f"..{self._end_container!r}:{self._end_offset}]>"
        )

    __str__ = __repr__
