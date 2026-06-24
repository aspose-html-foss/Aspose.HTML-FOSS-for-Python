"""CharacterData, Text, Comment, and CDATASection nodes."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.dom._node import Node
from aspose_html.dom._node_type import NodeType
from aspose_html.dom._exceptions import (
    HierarchyRequestError,
    IndexSizeError,
)

if TYPE_CHECKING:
    from aspose_html.dom._document import Document


class CharacterData(Node):
    """Abstract base for Text, Comment, CDATASection, and ProcessingInstruction.

    Provides the ``data`` property and character-data manipulation methods.

    Examples
    --------
    >>> from aspose_html.dom import Document, Text
    >>> doc = Document()
    >>> t = doc.create_text_node("hello")
    >>> t.data
    'hello'
    >>> t.length
    5
    """

    __slots__ = ("_data",)

    def __init__(
        self, node_type: int, data: str = "", owner_document: Document | None = None
    ) -> None:
        super().__init__(node_type, owner_document)
        self._data: str = data

    # ------------------------------------------------------------------
    # Node interface
    # ------------------------------------------------------------------

    @property
    def node_value(self) -> str:  # type: ignore[override]
        """The character data content (same as ``data``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hi")
        >>> t.node_value
        'hi'
        """
        return self._data

    @node_value.setter
    def node_value(self, value: str | None) -> None:
        if value is not None:
            self._data = value

    @property
    def text_content(self) -> str | None:
        """The character data content (same as ``data``).

        Per WHATWG DOM §4.4. For Text, Comment, CDATASection, and
        ProcessingInstruction nodes, textContent is identical to ``data``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hello")
        >>> t.text_content
        'hello'
        """
        return self._data  # See 

    @text_content.setter
    def text_content(self, value: str | None) -> None:
        """Set the character data content.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("old")
        >>> t.text_content = "new"
        >>> t.text_content
        'new'
        """
        if value is not None:
            self._data = value  # See : None guard matches node_value pattern

    # ------------------------------------------------------------------
    # CharacterData interface
    # ------------------------------------------------------------------

    @property
    def data(self) -> str:
        """The character data content.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> c = doc.create_comment("a comment")
        >>> c.data
        'a comment'
        """
        return self._data

    @data.setter
    def data(self, value: str) -> None:
        """Set the character data content.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("old")
        >>> t.data = "new"
        >>> t.data
        'new'
        """
        old_val = self._data
        self._data = value
        doc = self._owner_document
        signal = getattr(doc, "_mutation_signal", None) if doc is not None else None
        if signal is not None:
            signal.notify_character_data(self, old_val)

    @property
    def length(self) -> int:
        """The number of code units in ``data``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hello")
        >>> t.length
        5
        """
        return len(self._data)

    def substring_data(self, offset: int, count: int) -> str:
        """Return a substring of ``data`` starting at *offset* for *count* chars.

        Raises ``IndexSizeError`` if *offset* > ``length``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hello world")
        >>> t.substring_data(6, 5)
        'world'
        """
        if offset > len(self._data):
            raise IndexSizeError(
                f"offset {offset} is greater than data length {len(self._data)}."
            )
        return self._data[offset: offset + count]

    def append_data(self, data: str) -> None:
        """Append *data* to the existing character data.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hello")
        >>> t.append_data(" world")
        >>> t.data
        'hello world'
        """
        self._data += data

    def insert_data(self, offset: int, data: str) -> None:
        """Insert *data* at *offset*.

        Raises ``IndexSizeError`` if *offset* > ``length``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("helo")
        >>> t.insert_data(3, "l")
        >>> t.data
        'hello'
        """
        if offset > len(self._data):
            raise IndexSizeError(
                f"offset {offset} is greater than data length {len(self._data)}."
            )
        self._data = self._data[:offset] + data + self._data[offset:]

    def delete_data(self, offset: int, count: int) -> None:
        """Delete *count* characters starting at *offset*.

        *count* is clamped if it exceeds the available length past *offset*.
        Raises ``IndexSizeError`` if *offset* > ``length``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hello world")
        >>> t.delete_data(5, 6)
        >>> t.data
        'hello'
        """
        if offset > len(self._data):
            raise IndexSizeError(
                f"offset {offset} is greater than data length {len(self._data)}."
            )
        self._data = self._data[:offset] + self._data[offset + count:]

    def replace_data(self, offset: int, count: int, data: str) -> None:
        """Replace *count* characters from *offset* with *data*.

        Raises ``IndexSizeError`` if *offset* > ``length``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hello world")
        >>> t.replace_data(6, 5, "there")
        >>> t.data
        'hello there'
        """
        if offset > len(self._data):
            raise IndexSizeError(
                f"offset {offset} is greater than data length {len(self._data)}."
            )
        self._data = self._data[:offset] + data + self._data[offset + count:]

    # ------------------------------------------------------------------
    # ChildNode mixin (WHATWG DOM §4.2.4)
    # ------------------------------------------------------------------

    def remove(self) -> None:
        """Remove this node from its parent node.

        No-op if this node has no parent (detached).

        Per WHATWG DOM §4.2.4 ChildNode.remove().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> text = doc.create_text_node("hello")
        >>> _ = doc.append_child(parent)
        >>> _ = parent.append_child(text)
        >>> text.remove()
        >>> len(parent.child_nodes)
        0
        >>> text.parent_node is None
        True
        """
        if self._parent is not None:
            self._parent.remove_child(self)

    # ------------------------------------------------------------------
    # CharacterData nodes may not have children
    # ------------------------------------------------------------------

    def _validate_insertion(
        self, node: Node, replacing: Node | None = None
    ) -> None:
        raise HierarchyRequestError(
            f"{type(self).__name__} nodes cannot have children."
        )

    def __repr__(self) -> str:
        preview = self._data[:40]
        ellipsis_ = "…" if len(self._data) > 40 else ""
        return f"<{type(self).__name__} data={preview + ellipsis_!r}>"

    __str__ = __repr__


class Text(CharacterData):
    """A text node.

    Create via ``Document.create_text_node()``.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> t = doc.create_text_node("hello")
    >>> t.node_name
    '#text'
    >>> t.node_type
    3
    """

    __slots__ = ()

    def __init__(self, data: str = "", owner_document: Document | None = None) -> None:
        super().__init__(NodeType.TEXT_NODE, data, owner_document)

    @property
    def node_name(self) -> str:
        """``'#text'``

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_text_node("x").node_name
        '#text'
        """
        return "#text"

    def split_text(self, offset: int) -> "Text":
        """Split this Text node at *offset*, returning the new trailing node.

        Implements WHATWG DOM §4.5.6.

        1. Raises ``IndexSizeError`` if *offset* > ``length``.
        2. Creates a new ``Text`` node with ``data[offset:]``, owned by
           ``self.owner_document``.
        3. If this node has a parent, inserts the new node immediately after
           this node via ``parent.insert_before(new_node, self.next_sibling)``.
        4. Truncates ``self.data`` to ``data[:offset]`` via ``delete_data``.
        5. Returns the new ``Text`` node.

        Parameters
        ----------
        offset : int
            The character offset at which to split.  ``0`` moves all data to
            the new node; ``length`` leaves this node unchanged and returns an
            empty Text node.

        Returns
        -------
        Text
            The new trailing ``Text`` node containing ``data[offset:]``.

        Raises
        ------
        IndexSizeError
            If *offset* is greater than ``length``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hello")
        >>> new_t = t.split_text(3)
        >>> t.data
        'hel'
        >>> new_t.data
        'lo'
        >>> new_t.owner_document is doc
        True
        """
        # : WHATWG DOM §4.5.6 algorithm — tree insertion before data truncation
        length = len(self._data)
        if offset > length:
            raise IndexSizeError(
                f"offset {offset} exceeds text length {length}."
            )
        count = length - offset
        new_data = self.substring_data(offset, count)
        new_node = Text(new_data, owner_document=self._owner_document)
        parent = self._parent
        if parent is not None:
            # insert_before(node, None) appends when self is the last child
            parent.insert_before(new_node, self.next_sibling)
        self.delete_data(offset, count)
        return new_node

    @property
    def whole_text(self) -> str:
        """Concatenated data of all contiguous ``Text`` nodes around this node.

        Implements WHATWG DOM §4.10.  Traverses preceding and following
        siblings collecting data from each node whose runtime type is exactly
        ``Text`` (``CDATASection`` nodes, which subclass ``Text``, are
        excluded).  Stops at the first non-``Text`` sibling or the parent
        boundary.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> t1 = doc.create_text_node("foo")
        >>> t2 = doc.create_text_node("bar")
        >>> _ = parent.append_child(t1)
        >>> _ = parent.append_child(t2)
        >>> t1.whole_text
        'foobar'
        >>> t2.whole_text
        'foobar'
        """
        preceding: list[str] = []
        sib = self.previous_sibling
        while sib is not None and type(sib) is Text:
            preceding.append(sib._data)
            sib = sib.previous_sibling
        following: list[str] = []
        sib = self.next_sibling
        while sib is not None and type(sib) is Text:
            following.append(sib._data)
            sib = sib.next_sibling
        return "".join(reversed(preceding)) + self._data + "".join(following)

    def _clone_self(self) -> Text:
        return Text(self._data, self._owner_document)


class Comment(CharacterData):
    """An HTML comment node.

    Create via ``Document.create_comment()``.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> c = doc.create_comment("hello")
    >>> c.node_name
    '#comment'
    """

    __slots__ = ()

    def __init__(self, data: str = "", owner_document: Document | None = None) -> None:
        super().__init__(NodeType.COMMENT_NODE, data, owner_document)

    @property
    def node_name(self) -> str:
        """``'#comment'``

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_comment("x").node_name
        '#comment'
        """
        return "#comment"

    def _clone_self(self) -> Comment:
        return Comment(self._data, self._owner_document)


class CDATASection(Text):
    """A CDATA section node (extends Text per WHATWG DOM Standard).

    Examples
    --------
    >>> from aspose_html.dom import CDATASection, Document
    >>> doc = Document()
    >>> cds = CDATASection("data", owner_document=doc)
    >>> cds.node_name
    '#cdata-section'
    >>> cds.node_type
    4
    """

    __slots__ = ()

    def __init__(self, data: str = "", owner_document: Document | None = None) -> None:
        # Bypass Text.__init__ to set the correct node_type.
        CharacterData.__init__(self, NodeType.CDATA_SECTION_NODE, data, owner_document)

    @property
    def node_name(self) -> str:
        """``'#cdata-section'``

        Examples
        --------
        >>> from aspose_html.dom import CDATASection, Document
        >>> CDATASection("x").node_name
        '#cdata-section'
        """
        return "#cdata-section"

    def _clone_self(self) -> CDATASection:
        return CDATASection(self._data, self._owner_document)
