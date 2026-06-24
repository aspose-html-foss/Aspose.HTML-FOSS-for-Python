"""Selection — document-scoped DOM Selection API.

Implements the single-range baseline from  on top of the live
``Range`` behavior implemented in .
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.dom._exceptions import IndexSizeError, InvalidStateError, WrongDocumentError
from aspose_html.dom._range import _bp_compare, _max_offset, _node_document

if TYPE_CHECKING:
    from aspose_html.dom._document import Document
    from aspose_html.dom._node import Node
    from aspose_html.dom._range import Range


class Selection:
    """Document-scoped selection with single-range semantics.

    Use :meth:`Document.get_selection <aspose_html.dom.Document.get_selection>`
    to access the document's singleton selection object.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> sel = doc.get_selection()
    >>> sel.range_count
    0
    """

    __slots__ = ("_owner_document", "_range", "_direction")

    def __init__(self, owner_document: "Document") -> None:
        self._owner_document: "Document" = owner_document
        self._range: "Range | None" = None
        self._direction: str = "none"

    @property
    def range_count(self) -> int:
        """Number of ranges in this selection (``0`` or ``1``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_selection().range_count
        0
        """
        return 0 if self._range is None else 1

    @property
    def anchor_node(self) -> "Node | None":
        """Anchor node for the current selection direction.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_selection().anchor_node is None
        True
        """
        if self._range is None:
            return None
        if self._direction == "backwards":
            return self._range.end_container
        return self._range.start_container

    @property
    def anchor_offset(self) -> int:
        """Anchor offset for the current selection direction.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_selection().anchor_offset
        0
        """
        if self._range is None:
            return 0
        if self._direction == "backwards":
            return self._range.end_offset
        return self._range.start_offset

    @property
    def focus_node(self) -> "Node | None":
        """Focus node for the current selection direction.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_selection().focus_node is None
        True
        """
        if self._range is None:
            return None
        if self._direction == "backwards":
            return self._range.start_container
        return self._range.end_container

    @property
    def focus_offset(self) -> int:
        """Focus offset for the current selection direction.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_selection().focus_offset
        0
        """
        if self._range is None:
            return 0
        if self._direction == "backwards":
            return self._range.start_offset
        return self._range.end_offset

    @property
    def is_collapsed(self) -> bool:
        """True when selection is empty or underlying range is collapsed.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_selection().is_collapsed
        True
        """
        return self._range is None or self._range.collapsed

    def get_range_at(self, index: int) -> "Range":
        """Return the selected range at *index*.

        Only index ``0`` is valid in this single-range baseline.

        Raises
        ------
        IndexSizeError
            If selection is empty or *index* is not ``0``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> sel = doc.get_selection()
        >>> sel.add_range(r)
        >>> sel.get_range_at(0) is r
        True
        """
        if index != 0 or self._range is None:
            raise IndexSizeError("index out of range for single-range Selection")
        return self._range

    def add_range(self, range_obj: "Range") -> None:
        """Set this selection's single range to *range_obj*.

        Raises
        ------
        InvalidStateError
            If *range_obj* is detached.
        WrongDocumentError
            If *range_obj* belongs to a different document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> r = doc.create_range()
        >>> sel = doc.get_selection()
        >>> sel.add_range(r)
        >>> sel.range_count
        1
        """
        if range_obj._detached:
            raise InvalidStateError("Cannot add a detached Range to Selection")
        if range_obj._owner_document is not self._owner_document:
            raise WrongDocumentError("Range belongs to a different document")
        self._range = range_obj
        self._direction = "none" if range_obj.collapsed else "forwards"

    def remove_all_ranges(self) -> None:
        """Clear the current selection.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.get_selection()
        >>> sel.add_range(doc.create_range())
        >>> sel.remove_all_ranges()
        >>> sel.range_count
        0
        """
        self._range = None
        self._direction = "none"

    def collapse(self, node: "Node | None", offset: int = 0) -> None:
        """Collapse selection to a single boundary point.

        Passing ``None`` clears the selection.

        Parameters
        ----------
        node : Node | None
            Boundary node in this selection's owner document, or ``None``.
        offset : int, default=0
            Boundary offset in *node*.

        Raises
        ------
        WrongDocumentError
            If *node* belongs to a different document.
        IndexSizeError
            If *offset* is out of bounds for *node*.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> root = doc.create_element("div")
        >>> _ = doc.append_child(root)
        >>> sel = doc.get_selection()
        >>> sel.collapse(root, 0)
        >>> sel.is_collapsed
        True
        """
        if node is None:
            self.remove_all_ranges()
            return
        if _node_document(node) is not self._owner_document:
            raise WrongDocumentError("Node belongs to a different document")
        r = self._owner_document.create_range()
        r.set_start(node, offset)
        r.set_end(node, offset)
        self._range = r
        self._direction = "none"

    def set_position(self, node: "Node | None", offset: int = 0) -> None:
        """Alias for :meth:`collapse`.

        Parameters
        ----------
        node : Node | None
            Boundary node in this selection's owner document, or ``None``.
        offset : int, default=0
            Boundary offset in *node*.

        Raises
        ------
        WrongDocumentError
            If *node* belongs to a different document.
        IndexSizeError
            If *offset* is out of bounds for *node*.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = doc.append_child(host)
        >>> sel = doc.get_selection()
        >>> sel.set_position(host, 0)
        >>> sel.is_collapsed
        True
        """
        self.collapse(node, offset)

    def collapse_to_start(self) -> None:
        """Collapse selection to the current start boundary point.

        Raises
        ------
        InvalidStateError
            If selection is empty.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = host.append_child(doc.create_element("a"))
        >>> _ = host.append_child(doc.create_element("b"))
        >>> _ = doc.append_child(host)
        >>> sel = doc.get_selection()
        >>> sel.select_all_children(host)
        >>> sel.collapse_to_start()
        >>> sel.anchor_offset == sel.focus_offset == 0
        True
        """
        if self._range is None:
            raise InvalidStateError("Cannot collapse_to_start() with empty Selection")
        sc = self._range.start_container
        so = self._range.start_offset
        r = self._owner_document.create_range()
        r.set_start(sc, so)
        r.set_end(sc, so)
        self._range = r
        self._direction = "none"

    def collapse_to_end(self) -> None:
        """Collapse selection to the current end boundary point.

        Raises
        ------
        InvalidStateError
            If selection is empty.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = host.append_child(doc.create_element("a"))
        >>> _ = host.append_child(doc.create_element("b"))
        >>> _ = doc.append_child(host)
        >>> sel = doc.get_selection()
        >>> sel.select_all_children(host)
        >>> sel.collapse_to_end()
        >>> sel.anchor_offset == sel.focus_offset == 2
        True
        """
        if self._range is None:
            raise InvalidStateError("Cannot collapse_to_end() with empty Selection")
        ec = self._range.end_container
        eo = self._range.end_offset
        r = self._owner_document.create_range()
        r.set_start(ec, eo)
        r.set_end(ec, eo)
        self._range = r
        self._direction = "none"

    def select_all_children(self, node: "Node") -> None:
        """Select all children of *node*.

        Raises
        ------
        WrongDocumentError
            If *node* belongs to a different document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = host.append_child(doc.create_element("a"))
        >>> _ = host.append_child(doc.create_element("b"))
        >>> _ = doc.append_child(host)
        >>> sel = doc.get_selection()
        >>> sel.select_all_children(host)
        >>> sel.anchor_offset, sel.focus_offset
        (0, 2)
        """
        if _node_document(node) is not self._owner_document:
            raise WrongDocumentError("Node belongs to a different document")
        r = self._owner_document.create_range()
        r.select_node_contents(node)
        self._range = r
        self._direction = "none" if r.collapsed else "forwards"

    # ------------------------------------------------------------------
    # Phase 3 —  /  / 
    # ------------------------------------------------------------------

    def extend(self, node: "Node", offset: int = 0) -> None:
        """Move the focus of the selection to (*node*, *offset*).

        The anchor point stays fixed.  The live ``Range`` object is mutated
        via its public boundary setters — it is never replaced — preserving
        any external reference obtained via :meth:`get_range_at`.

        Follows WHATWG Selection §5.5.6.

        Parameters
        ----------
        node : Node
            The new focus node.
        offset : int, default=0
            The new focus offset within *node*.

        Raises
        ------
        WrongDocumentError
            If *node* belongs to a different document (propagated from
            ``Range.set_start`` / ``Range.set_end``).
        IndexSizeError
            If *offset* is out of bounds for *node* (propagated from
            ``Range.set_start`` / ``Range.set_end``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> a = doc.create_element("a")
        >>> b = doc.create_element("b")
        >>> _ = host.append_child(a)
        >>> _ = host.append_child(b)
        >>> _ = doc.append_child(host)
        >>> sel = doc.get_selection()
        >>> sel.select_all_children(host)
        >>> r = sel.get_range_at(0)
        >>> sel.extend(host, 1)
        >>> sel.get_range_at(0) is r
        True
        >>> sel._direction
        'forwards'
        """
        if self._range is None:
            return

        anchor_node = self.anchor_node
        anchor_offset = self.anchor_offset

        cmp = _bp_compare((node, offset), (anchor_node, anchor_offset))

        if cmp <= 0:
            # Focus is before or equal to anchor — backwards or collapsed.
            # Set end first (to anchor) so start can safely move to the
            # earlier focus position without triggering auto-collapse.
            self._range.set_end(anchor_node, anchor_offset)
            self._range.set_start(node, offset)
            self._direction = "none" if self._range.collapsed else "backwards"
        else:
            # Focus is strictly after anchor — forwards.
            # Set start first (to anchor), then end to the later focus.
            self._range.set_start(anchor_node, anchor_offset)
            self._range.set_end(node, offset)
            self._direction = "forwards"

    def to_string(self) -> str:
        """Return the plain-text content of the selected range.

        Returns an empty string when the selection is empty or the range is
        collapsed.  Follows WHATWG Selection §5.5.11.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> t = doc.create_text_node("hello world")
        >>> _ = p.append_child(t)
        >>> sel = doc.get_selection()
        >>> r = doc.create_range()
        >>> r.set_start(t, 0)
        >>> r.set_end(t, 5)
        >>> sel.add_range(r)
        >>> sel.to_string()
        'hello'
        >>> str(sel)
        'hello'
        """
        if self._range is None or self._range.collapsed:
            return ""
        return self._range.to_string()

    def __str__(self) -> str:
        """Return the plain-text content of the selected range.

        Delegates to :meth:`to_string`.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.get_selection()
        >>> str(sel)
        ''
        """
        return self.to_string()

    def contains_node(
        self, node: "Node", allow_partial_containment: bool = False
    ) -> bool:
        """Return ``True`` if the selection contains *node*.

        Parameters
        ----------
        node : Node
            The node to test.
        allow_partial_containment : bool, default=False
            When ``False`` (default), *node* must be fully within the selected
            range.  When ``True``, *node* needs only to partially overlap.

        Follows WHATWG Selection §5.5.10.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> inner = doc.create_element("span")
        >>> _ = host.append_child(inner)
        >>> _ = doc.append_child(host)
        >>> sel = doc.get_selection()
        >>> sel.select_all_children(host)
        >>> sel.contains_node(inner)
        True
        >>> sel.contains_node(inner, allow_partial_containment=True)
        True
        """
        if self._range is None:
            return False
        if allow_partial_containment:
            return self._range.intersects_node(node)
        node_length = _max_offset(node)
        return (
            self._range.compare_point(node, 0) <= 0
            and self._range.compare_point(node, node_length) >= 0
        )
