"""Element — the primary DOM node for HTML elements."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.dom._node import Node, _adopt
from aspose_html.dom._node_type import NodeType
from aspose_html.dom._collections import (
    HTMLCollection,
    NamedNodeMap,
    _StaticNodeList,
    _SubtreeHTMLCollection,
)

if TYPE_CHECKING:
    from aspose_html.dom._document import Document
    from aspose_html.dom._collections import NodeList
    from aspose_html.dom._style_sheets import StyleSheetList
    from aspose_html.dom._style import CSSStyleDeclaration  # added by ; 
    from aspose_html.dom._token_list import DOMTokenList  # added by ; 
    from aspose_html.dom._dataset import DOMStringMap  # added by ; 
    from aspose_html.dom._geometry import DOMRect, DOMRectList  # added by ; 


_HTML_NS = "http://www.w3.org/1999/xhtml"
# _adopt imported from _node — see  for rationale on the move.

# M7.1 (/): attribute names whose mutation invalidates the
# layout style cache — class/id feed selector matching, style feeds the
# inline-style path. Immutable module-level constant (frozenset).
_STYLE_AFFECTING_ATTRS: frozenset[str] = frozenset({"class", "id", "style"})


def _norm_ns(ns: str | None) -> str | None:
    """Treat empty string as null namespace (WHATWG DOM §1.3)."""
    return None if not ns else ns


def _coerce_nodes(
    nodes: "tuple[Node | str, ...]",
    owner_document: "Document | None",
) -> "list[Node]":
    """Convert a mixed tuple of Node and str into a list of Node objects.

    Strings are converted to Text nodes using *owner_document*.create_text_node()
    when *owner_document* is not None, or to a standalone Text(s) when detached.

    This helper is used by the ChildNode mixin methods () and the
    ParentNode mixin methods ().
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


class Element(Node):
    """An HTML or XML element node.

    Create via ``Document.create_element()`` rather than instantiating
    directly.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> el.tag_name
    'DIV'
    >>> el.local_name
    'div'
    """

    __slots__ = (
        "_tag_name",
        "_namespace_uri",
        "_prefix",
        "_local_name",
        "_attributes",
        "_children_cache",
        "_template_content",  # DocumentFragment | None — set by tree builder for <template>; See 
        "_style_declaration",  # CSSStyleDeclaration | None — created lazily on first access; see 
        "_class_list",  # DOMTokenList | None — created lazily on first access; see 
        "_dataset",  # DOMStringMap | None — created lazily on first access; see 
    )

    def __init__(
        self,
        local_name: str,
        namespace_uri: str | None = None,
        prefix: str | None = None,
        owner_document: Document | None = None,
    ) -> None:
        super().__init__(NodeType.ELEMENT_NODE, owner_document)
        self._local_name: str = local_name
        self._namespace_uri: str | None = namespace_uri
        self._prefix: str | None = prefix
        self._attributes: NamedNodeMap = NamedNodeMap()
        self._children_cache: HTMLCollection | None = None
        self._template_content = None  # DocumentFragment | None — additive slot
        self._style_declaration = None  # CSSStyleDeclaration | None — additive slot
        self._class_list = None  # DOMTokenList | None — additive slot
        self._dataset = None  # DOMStringMap | None — additive slot

        # Derived qualified name (uppercase for HTML elements)
        qualified = (f"{prefix}:{local_name}" if prefix else local_name)
        if namespace_uri == _HTML_NS:
            self._tag_name: str = qualified.upper()
        else:
            self._tag_name = qualified

    # ------------------------------------------------------------------
    # Node interface
    # ------------------------------------------------------------------

    @property
    def node_name(self) -> str:
        """The qualified tag name (uppercase for HTML elements).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> el.node_name
        'P'
        """
        return self._tag_name

    # ------------------------------------------------------------------
    # Element properties
    # ------------------------------------------------------------------

    @property
    def tag_name(self) -> str:
        """The qualified tag name in uppercase (HTML elements).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("section")
        >>> el.tag_name
        'SECTION'
        """
        return self._tag_name

    @property
    def local_name(self) -> str:
        """The local part of the qualified name (lowercase).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("DIV")
        >>> el.local_name
        'div'
        """
        return self._local_name

    @property
    def namespace_uri(self) -> str | None:
        """The namespace URI, or ``None`` for no namespace.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.namespace_uri
        'http://www.w3.org/1999/xhtml'
        """
        return self._namespace_uri

    @property
    def style_sheets(self) -> "StyleSheetList":
        """Live stylesheet list applicable to this element's document.

         baseline exposes document-level discovery order for element
        cascade entry points.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> sheet = CSSStyleSheet()
        >>> doc.attach_style_sheet(sheet)
        >>> el.style_sheets.item(0) is sheet
        True
        """
        doc = self.owner_document
        if doc is None:
            from aspose_html.dom._style_sheets import StyleSheetList  # noqa: PLC0415
            return StyleSheetList(lambda: [])
        return doc.style_sheets

    def get_computed_style(self) -> "ComputedStyleDeclaration":
        """Return phase-2 cascade-resolved declarations for this element.

        Resolution is deterministic and read-only (): precedence is
        `!important` > selector specificity > source order, with inline
        ``style`` declarations participating in the same winner model.
        Missing local winners for the phase-2 inherited subset (`color`,
        `font-family`, `font-size`, `font-style`, `font-weight`,
        `line-height`) fall back to nearest ancestor computed values, else ``''``.
        Matching `@media` blocks (`all`, `screen`, and baseline
        `prefers-color-scheme`) participate; unsupported/invalid media conditions
        are treated as non-matching.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> sheet = CSSStyleSheet()
        >>> sheet.replace_sync("div { color: red }")
        >>> doc.attach_style_sheet(sheet)
        >>> el.get_computed_style().get_property_value("color")
        'red'
        >>> el.style.set_property("color", "green")
        >>> el.get_computed_style().get_property_value("color")
        'green'
        >>> second = CSSStyleSheet()
        >>> second.replace_sync("div { color: blue !important }")
        >>> doc.attach_style_sheet(second)
        >>> el.get_computed_style().get_property_value("color")
        'blue'
        >>> media = CSSStyleSheet()
        >>> media.replace_sync("@media print { div { color: black } }")
        >>> doc.attach_style_sheet(media)
        >>> el.get_computed_style().get_property_value("color")
        'blue'
        >>> child = doc.create_element("span")
        >>> el.append_child(child)
        <Element 'SPAN'>
        >>> el.style.set_property("font-size", "18px")
        >>> child.get_computed_style().get_property_value("font-size")
        '18px'
        >>> child.get_computed_style().get_property_value("line-height")
        ''
        """
        from aspose_html.dom._cascade import get_computed_style  # noqa: PLC0415

        return get_computed_style(self)

    @property
    def prefix(self) -> str | None:
        """The namespace prefix, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.prefix is None
        True
        """
        return self._prefix

    @property
    def id(self) -> str:
        """The value of the ``id`` attribute, or ``''`` if not present.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.id
        ''
        >>> el.set_attribute("id", "main")
        >>> el.id
        'main'
        """
        return self.get_attribute("id") or ""

    @property
    def class_name(self) -> str:
        """The value of the ``class`` attribute, or ``''``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "a b c")
        >>> el.class_name
        'a b c'
        """
        return self.get_attribute("class") or ""

    @property
    def class_list(self) -> "DOMTokenList":
        """Live mutable set of CSS class tokens backed by the ``class`` attribute.

        Returns the same ``DOMTokenList`` instance on every call (cached per
        element). The list is live — every read operation re-reads the ``class``
        attribute, and every mutation writes back immediately via
        ``set_attribute`` / ``remove_attribute``.

        If the ``class`` attribute is modified externally via ``set_attribute``,
        the change is immediately visible through the returned object.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "foo bar")
        >>> el.class_list.contains("foo")
        True
        >>> el.class_list.add("baz")
        >>> el.get_attribute("class")
        'foo bar baz'
        >>> el.class_list is el.class_list
        True
        """
        if self._class_list is None:
            from aspose_html.dom._token_list import DOMTokenList  # noqa: PLC0415
            self._class_list = DOMTokenList(self)
        return self._class_list

    @property
    def dataset(self) -> "DOMStringMap":
        """Live dict-like view of the element's ``data-*`` custom attributes.

        Keys are camelCase equivalents of ``data-*`` attribute names (WHATWG
        §2.6.8). Changes to ``data-*`` attributes via ``set_attribute`` are
        immediately visible through this object.

        The same ``DOMStringMap`` instance is returned on every call (cached
        per element).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-user-id", "42")
        >>> el.dataset["userId"]
        '42'
        >>> el.dataset["userName"] = "Alice"
        >>> el.get_attribute("data-user-name")
        'Alice'
        >>> el.dataset is el.dataset
        True
        """
        if self._dataset is None:
            from aspose_html.dom._dataset import DOMStringMap  # noqa: PLC0415
            self._dataset = DOMStringMap(self)
        return self._dataset

    @property
    def attributes(self) -> NamedNodeMap:
        """The ordered map of Attr objects for this element.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("id", "x")
        >>> len(el.attributes)
        1
        """
        return self._attributes

    @property
    def children(self) -> HTMLCollection:
        """A live HTMLCollection of Element-type children only.

        The same object is returned on every call.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> child = doc.create_element("span")
        >>> doc.append_child(parent)
        <Element 'DIV'>
        >>> parent.append_child(child)
        <Element 'SPAN'>
        >>> len(parent.children)
        1
        >>> parent.children is parent.children
        True
        """
        if self._children_cache is None:
            self._children_cache = HTMLCollection(self._children)
        return self._children_cache

    @property
    def first_element_child(self) -> Element | None:
        """The first Element child, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.first_element_child is None
        True
        """
        for child in self._children:
            if child._node_type == NodeType.ELEMENT_NODE:
                return child  # type: ignore[return-value]
        return None

    @property
    def last_element_child(self) -> Element | None:
        """The last Element child, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.last_element_child is None
        True
        """
        for child in reversed(self._children):
            if child._node_type == NodeType.ELEMENT_NODE:
                return child  # type: ignore[return-value]
        return None

    @property
    def next_element_sibling(self) -> Element | None:
        """The next sibling that is an Element, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> b = doc.create_element("b")
        >>> root = doc.create_element("div")
        >>> doc.append_child(root)
        <Element 'DIV'>
        >>> root.append_child(a)
        <Element 'A'>
        >>> root.append_child(b)
        <Element 'B'>
        >>> a.next_element_sibling is b
        True
        """
        p = self._parent
        if p is None:
            return None
        siblings = p._children
        idx = siblings.index(self)
        for i in range(idx + 1, len(siblings)):
            if siblings[i]._node_type == NodeType.ELEMENT_NODE:
                return siblings[i]  # type: ignore[return-value]
        return None

    @property
    def previous_element_sibling(self) -> Element | None:
        """The previous sibling that is an Element, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> b = doc.create_element("b")
        >>> root = doc.create_element("div")
        >>> doc.append_child(root)
        <Element 'DIV'>
        >>> root.append_child(a)
        <Element 'A'>
        >>> root.append_child(b)
        <Element 'B'>
        >>> b.previous_element_sibling is a
        True
        """
        p = self._parent
        if p is None:
            return None
        siblings = p._children
        idx = siblings.index(self)
        for i in range(idx - 1, -1, -1):
            if siblings[i]._node_type == NodeType.ELEMENT_NODE:
                return siblings[i]  # type: ignore[return-value]
        return None

    @property
    def child_element_count(self) -> int:
        """The number of Element children.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("ul")
        >>> doc.append_child(el)
        <Element 'UL'>
        >>> el.child_element_count
        0
        >>> li = doc.create_element("li")
        >>> el.append_child(li)
        <Element 'LI'>
        >>> el.child_element_count
        1
        """
        return sum(1 for c in self._children if c._node_type == NodeType.ELEMENT_NODE)

    @property
    def inner_html(self) -> str:
        """The serialised HTML content of all children (innerHTML).

        Returns the serialisation of all child nodes without the element's
        own open/close tags.  Conforms to WHATWG HTML Living Standard §13.3.
        An element with no children returns ``''``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> child = doc.create_element("span")
        >>> el.append_child(child)
        <Element 'SPAN'>
        >>> el.inner_html
        '<span></span>'
        """
        from aspose_html.serialiser import inner_html as _inner_html_fn  # noqa: PLC0415
        return _inner_html_fn(self)

    @inner_html.setter
    def inner_html(self, value: str) -> None:
        """Replace all children with the parsed HTML fragment *value*.

        Parses *value* as an HTML fragment in the context of this element
        (WHATWG fragment parsing algorithm §13.2.8), removes all current
        children, then appends the resulting ``DocumentFragment`` so all
        parsed nodes are adopted into this element.

        Passing an empty string removes all children.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.inner_html = ""
        >>> el.inner_html
        ''
        """
        from aspose_html.html_document import HTMLDocument as _HTMLDocument  # noqa: PLC0415
        fragment = _HTMLDocument.parse_fragment(value, context_element=self)
        # Remove all existing children
        for child in list(self._children):
            self.remove_child(child)
        # Adopt fragment children into this document before insertion.
        # parse_fragment() creates a standalone document; nodes must be
        # re-parented to self._owner_document to pass the wrong-document check.
        target_doc = self._owner_document
        for child in list(fragment.child_nodes):
            _adopt(child, target_doc)
            self.append_child(child)

    @property
    def outer_html(self) -> str:
        """The serialised HTML of this element and all its descendants (outerHTML).

        Equivalent to calling ``serialiser.serialise(self)``.  Conforms to
        WHATWG HTML Living Standard §13.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> el.outer_html
        '<p></p>'
        """
        from aspose_html.serialiser import outer_html as _outer_html_fn  # noqa: PLC0415
        return _outer_html_fn(self)

    @outer_html.setter
    def outer_html(self, value: str) -> None:
        """Replace this element in its parent with parsed HTML markup.

        Raises
        ------
        NoModificationAllowedError
            If this element has no parent node.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = doc.append_child(host)
        >>> el = doc.create_element("span")
        >>> _ = host.append_child(el)
        >>> el.outer_html = "<b>x</b>"
        >>> host.first_child.node_name
        'B'
        >>> el.parent_node is None
        True
        """
        parent = self.parent_node
        if parent is None:
            from aspose_html.dom._exceptions import NoModificationAllowedError  # noqa: PLC0415

            raise NoModificationAllowedError(
                "Cannot set outer_html on an element with no parent node."
            )

        from aspose_html.html_document import HTMLDocument as _HTMLDocument  # noqa: PLC0415

        context = self.parent_element if self.parent_element is not None else self
        fragment = _HTMLDocument.parse_fragment(value, context_element=context)
        anchor = self.next_sibling
        target_doc = parent.owner_document
        if target_doc is None and parent.node_type == NodeType.DOCUMENT_NODE:
            target_doc = parent  # type: ignore[assignment]

        replacement_children = list(fragment.child_nodes)
        if parent.node_type == NodeType.DOCUMENT_NODE and replacement_children:
            self._validate_outer_html_document_replacement(parent, replacement_children)
            first = replacement_children[0]
            _adopt(first, target_doc)
            parent.replace_child(first, self)
            for child in replacement_children[1:]:
                _adopt(child, target_doc)
                parent.insert_before(child, anchor)
            return

        for child in replacement_children:
            # : use DOM insertion primitives, but adopt parser-owned
            # fragment children first so the wrong-document guard remains valid.
            _adopt(child, target_doc)
            parent.insert_before(child, anchor)
        parent.remove_child(self)

    def _validate_outer_html_document_replacement(
        self,
        parent: Node,
        replacement_children: "list[Node]",
    ) -> None:
        """Validate a Document-level outer_html replacement before mutation."""
        from aspose_html.dom._exceptions import HierarchyRequestError  # noqa: PLC0415

        element_children = [
            child for child in replacement_children
            if child.node_type == NodeType.ELEMENT_NODE
        ]
        doctype_children = [
            child for child in replacement_children
            if child.node_type == NodeType.DOCUMENT_TYPE_NODE
        ]
        if len(element_children) > 1:
            raise HierarchyRequestError("Document can only have one Element child.")
        if len(doctype_children) > 1:
            raise HierarchyRequestError("Document can only have one DocumentType child.")
        for child in replacement_children:
            if child.node_type not in (
                NodeType.ELEMENT_NODE,
                NodeType.DOCUMENT_TYPE_NODE,
                NodeType.COMMENT_NODE,
                NodeType.PROCESSING_INSTRUCTION_NODE,
            ):
                raise HierarchyRequestError(
                    f"Document cannot contain node type {child.node_type}."
                )

        existing_element = getattr(parent, "document_element", None)
        if element_children and existing_element is not None and existing_element is not self:
            raise HierarchyRequestError("Document can only have one Element child.")
        existing_doctype = getattr(parent, "document_type", None)
        if doctype_children and existing_doctype is not None and existing_doctype is not self:
            raise HierarchyRequestError("Document can only have one DocumentType child.")

    def insert_adjacent_html(self, position: str, html: str) -> None:
        """Insert parsed HTML markup relative to this element.

        Parameters
        ----------
        position:
            Case-insensitive insertion point.  Must be one of:
            ``"beforebegin"``, ``"afterbegin"``, ``"beforeend"``, ``"afterend"``.
        html:
            Markup to parse as an HTML fragment and insert.

        Raises
        ------
        SyntaxError
            If *position* is not one of the four recognised strings
            (case-insensitive comparison).
        NoModificationAllowedError
            If *position* is ``"beforebegin"`` or ``"afterend"`` and this
            element has no parent node.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = doc.append_child(host)
        >>> child = doc.create_element("span")
        >>> _ = host.append_child(child)
        >>> child.insert_adjacent_html("beforebegin", "<b>A</b>")
        >>> host.first_child.node_name
        'B'
        >>> child.insert_adjacent_html("afterend", "<i>Z</i>")
        >>> host.last_child.node_name
        'I'
        >>> child.insert_adjacent_html("afterbegin", "<u>1</u>")
        >>> child.first_child.node_name
        'U'
        >>> child.insert_adjacent_html("beforeend", "<s>2</s>")
        >>> child.last_child.node_name
        'S'
        """
        _VALID_POSITIONS = {"beforebegin", "afterbegin", "beforeend", "afterend"}
        pos = position.lower()
        if pos not in _VALID_POSITIONS:
            from aspose_html.dom._exceptions import SyntaxError as _SyntaxError  # noqa: PLC0415
            raise _SyntaxError(
                f"Invalid position: {position!r}. Must be one of"
                " 'beforebegin', 'afterbegin', 'beforeend', 'afterend'."
            )
        parent = self.parent_node
        if pos in ("beforebegin", "afterend") and parent is None:
            from aspose_html.dom._exceptions import NoModificationAllowedError  # noqa: PLC0415
            raise NoModificationAllowedError(
                f"Cannot use position {position!r} on an element with no parent node."
            )
        from aspose_html.html_document import HTMLDocument as _HTMLDocument  # noqa: PLC0415

        if pos in ("beforebegin", "afterend"):
            context = self.parent_element if self.parent_element is not None else self
        else:
            context = self
        fragment = _HTMLDocument.parse_fragment(html, context_element=context)

        if pos in ("beforebegin", "afterend"):
            target_doc = parent.owner_document  # type: ignore[union-attr]
            if target_doc is None and parent.node_type == NodeType.DOCUMENT_NODE:  # type: ignore[union-attr]
                target_doc = parent  # type: ignore[assignment]
        else:
            target_doc = self._owner_document

        children = list(fragment.child_nodes)
        for child in children:
            _adopt(child, target_doc)

        if pos == "beforebegin":
            for child in children:
                parent.insert_before(child, self)  # type: ignore[union-attr]
        elif pos == "afterbegin":
            # Insert in reverse order so each lands at first_child
            for child in reversed(children):
                self.insert_before(child, self.first_child)
        elif pos == "beforeend":
            for child in children:
                self.append_child(child)
        else:  # afterend
            # anchor starts as next_sibling; after each insert anchor advances
            anchor = self.next_sibling
            for child in children:
                parent.insert_before(child, anchor)  # type: ignore[union-attr]

    def insert_adjacent_text(self, position: str, text: str) -> None:
        """Insert a text node relative to this element.

        Parameters
        ----------
        position:
            Case-insensitive insertion point.  Must be one of:
            ``"beforebegin"``, ``"afterbegin"``, ``"beforeend"``, ``"afterend"``.
        text:
            Plain text to insert as a ``Text`` node.  The string is NOT
            parsed as HTML — characters are not entity-encoded before
            insertion.

        Raises
        ------
        SyntaxError
            If *position* is not one of the four recognised strings
            (case-insensitive comparison).
        NoModificationAllowedError
            If *position* is ``"beforebegin"`` or ``"afterend"`` and this
            element has no parent node.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> host = doc.create_element("div")
        >>> _ = doc.append_child(host)
        >>> child = doc.create_element("span")
        >>> _ = host.append_child(child)
        >>> child.insert_adjacent_text("beforebegin", "hello ")
        >>> host.first_child.node_value
        'hello '
        >>> child.insert_adjacent_text("afterend", " world")
        >>> host.last_child.node_value
        ' world'
        >>> child.insert_adjacent_text("afterbegin", "inner-start")
        >>> child.first_child.node_value
        'inner-start'
        >>> child.insert_adjacent_text("beforeend", "inner-end")
        >>> child.last_child.node_value
        'inner-end'
        """
        _VALID_POSITIONS = {"beforebegin", "afterbegin", "beforeend", "afterend"}
        pos = position.lower()
        if pos not in _VALID_POSITIONS:
            from aspose_html.dom._exceptions import SyntaxError as _SyntaxError  # noqa: PLC0415
            raise _SyntaxError(
                f"Invalid position: {position!r}. Must be one of"
                " 'beforebegin', 'afterbegin', 'beforeend', 'afterend'."
            )
        parent = self.parent_node
        if pos in ("beforebegin", "afterend") and parent is None:
            from aspose_html.dom._exceptions import NoModificationAllowedError  # noqa: PLC0415
            raise NoModificationAllowedError(
                f"Cannot use position {position!r} on an element with no parent node."
            )

        if pos in ("beforebegin", "afterend"):
            owner_doc = parent.owner_document  # type: ignore[union-attr]
            if owner_doc is None and parent.node_type == NodeType.DOCUMENT_NODE:  # type: ignore[union-attr]
                owner_doc = parent  # type: ignore[assignment]
        else:
            owner_doc = self._owner_document

        if owner_doc is not None:
            text_node = owner_doc.create_text_node(text)
        else:
            from aspose_html.dom._character_data import Text as _Text  # noqa: PLC0415
            text_node = _Text(text)

        if pos == "beforebegin":
            parent.insert_before(text_node, self)  # type: ignore[union-attr]
        elif pos == "afterbegin":
            self.insert_before(text_node, self.first_child)
        elif pos == "beforeend":
            self.append_child(text_node)
        else:  # afterend
            parent.insert_before(text_node, self.next_sibling)  # type: ignore[union-attr]

    def insert_adjacent_element(
        self,
        position: str,
        element: "Element | None",
    ) -> "Element | None":
        """Insert *element* at *position* relative to this element.

        *position* is case-insensitive and must be one of:
        ``"beforebegin"``, ``"afterbegin"``, ``"beforeend"``, ``"afterend"``.

        Returns *element* after insertion, or ``None`` when *element* is ``None``.

        Raises :class:`~aspose_html.dom.SyntaxError` for an invalid position.
        Raises :class:`~aspose_html.dom.NoModificationAllowedError` when
        ``"beforebegin"`` or ``"afterend"`` is used on a detached element.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> child = doc.create_element("span")
        >>> _ = parent.append_child(child)
        >>> new = doc.create_element("b")
        >>> result = parent.insert_adjacent_element("afterbegin", new)
        >>> result is new
        True
        >>> parent.first_child is new
        True
        """
        if element is None:
            return None

        pos = position.lower()
        _VALID_POSITIONS = {"beforebegin", "afterbegin", "beforeend", "afterend"}
        if pos not in _VALID_POSITIONS:
            from aspose_html.dom._exceptions import SyntaxError as _SyntaxError  # noqa: PLC0415
            raise _SyntaxError(f"Invalid position: {position!r}")

        parent = self.parent_node
        if pos in ("beforebegin", "afterend") and parent is None:
            from aspose_html.dom._exceptions import NoModificationAllowedError  # noqa: PLC0415
            raise NoModificationAllowedError(
                f"Cannot use position {position!r} on an element with no parent node."
            )

        if pos == "beforebegin":
            parent.insert_before(element, self)  # type: ignore[union-attr]
        elif pos == "afterbegin":
            self.insert_before(element, self.first_child)
        elif pos == "beforeend":
            self.append_child(element)
        else:  # afterend
            parent.insert_before(element, self.next_sibling)  # type: ignore[union-attr]

        return element

    @property
    def text_content(self) -> str | None:
        """The concatenation of all descendant Text node data (DFS order).

        Only TEXT_NODE (node type 3) nodes contribute. Comment,
        ProcessingInstruction, CDATASection, and Element nodes do not.

        Setter removes all existing children and inserts a single Text node
        if *value* is a non-empty string. Passing ``""`` or ``None`` removes
        all children and inserts nothing.

        WARNING: the setter is destructive — it removes all child nodes,
        including element children. This matches WHATWG DOM §4.4 semantics.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> el.text_content
        ''
        >>> el.text_content = "hello"
        >>> el.text_content
        'hello'
        """
        # : DFS traversal in document order (prepend children to stack)
        # See  for the rationale on stack[:0] prepend ordering.
        parts: list[str] = []
        stack: list[Node] = list(self._children)
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
                # Detached element — create Text directly. See .
                from aspose_html.dom._character_data import Text  # noqa: PLC0415
                text_node = Text(value)
            self.append_child(text_node)

    @property
    def style(self) -> "CSSStyleDeclaration":
        """The inline style of this element as a live CSSStyleDeclaration.

        The returned object reads from and writes to the element's ``style``
        attribute directly. The same object is returned on every call
        (cached per element). If the ``style`` attribute is modified externally
        via ``set_attribute``, the change is immediately visible through the
        returned object because it re-parses the attribute on every access.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style["color"] = "red"
        >>> el.get_attribute("style")
        'color: red'
        """
        if self._style_declaration is None:
            from aspose_html.dom._style import CSSStyleDeclaration  # noqa: PLC0415
            self._style_declaration = CSSStyleDeclaration(self)
        return self._style_declaration

    # ------------------------------------------------------------------
    # Attribute methods
    # ------------------------------------------------------------------

    def _inserted_into_tree(self) -> None:
        doc = self._owner_document
        if doc is None:
            return
        win = doc._get_cached_default_view()
        if win is None or win._custom_elements is None:
            return
        win._custom_elements._fire_connected(self)

    def _removed_from_tree(self) -> None:
        doc = self._owner_document
        if doc is None:
            return
        win = doc._get_cached_default_view()
        if win is None or win._custom_elements is None:
            return
        win._custom_elements._fire_disconnected(self)

    def get_attribute(self, name: str) -> str | None:
        """Return the value of attribute *name*, or ``None`` if absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.get_attribute("id") is None
        True
        >>> el.set_attribute("id", "x")
        >>> el.get_attribute("id")
        'x'
        """
        attr = self._attributes.get_named_item(name)
        if attr is None:
            return None
        return attr.value  # type: ignore[union-attr]

    def set_attribute(self, name: str, value: str) -> None:
        """Set attribute *name* to *value*, creating it if not present.

        If *name* is ``'id'``, the owner document's ``_id_map`` is updated.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "box")
        >>> el.get_attribute("class")
        'box'
        """
        from aspose_html.dom._attr import Attr

        old_val = self.get_attribute(name)
        existing: Attr | None = self._attributes.get_named_item(name)  # type: ignore[assignment]

        if name == "id":
            doc = self._owner_document
            if doc is not None:
                old_id = existing.value if existing is not None else None
                if old_id:
                    fn = getattr(doc, "_unregister_id", None)
                    if fn:
                        fn(self)

        if existing is not None:
            existing._value = value
        else:
            attr = Attr(name, value, owner_element=self, owner_document=self._owner_document)
            self._attributes.set_named_item(attr)

        if name == "id" and value:
            doc = self._owner_document
            if doc is not None:
                fn = getattr(doc, "_register_id", None)
                if fn:
                    fn(self, value)

        doc = self._owner_document
        if doc is not None:
            win = doc._get_cached_default_view()
            if win is not None and win._custom_elements is not None and win._custom_elements._is_observed(self, name):
                win._custom_elements._fire_attribute_changed(self, name, old_val, value)

        signal = getattr(doc, "_mutation_signal", None) if doc is not None else None
        if signal is not None and signal._observers:
            signal.notify_attribute(self, name, None, old_val)

        # M7.1 layout style cache (/): class/id/style affect
        # selector matching and the inline-style path. set_property /
        # remove_property funnel through here for "style", so this single hook
        # also covers AC-13/AC-14 with exactly one bump per logical edit.
        if name in _STYLE_AFFECTING_ATTRS and doc is not None:
            doc._bump_style_epoch()

    def remove_attribute(self, name: str) -> None:
        """Remove attribute *name*. No-op if not present.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-x", "1")
        >>> el.remove_attribute("data-x")
        >>> el.has_attribute("data-x")
        False
        """
        if name not in self._attributes:
            return
        old_val = self.get_attribute(name)
        if name == "id":
            doc = self._owner_document
            if doc is not None:
                fn = getattr(doc, "_unregister_id", None)
                if fn:
                    fn(self)
        self._attributes.remove_named_item(name)
        doc = self._owner_document
        if doc is not None:
            win = doc._get_cached_default_view()
            if win is not None and win._custom_elements is not None and win._custom_elements._is_observed(self, name):
                win._custom_elements._fire_attribute_changed(self, name, old_val, None)
        signal = getattr(doc, "_mutation_signal", None) if doc is not None else None
        if signal is not None and signal._observers:
            signal.notify_attribute(self, name, None, old_val)

        # M7.1 layout style cache invalidation (/).
        if name in _STYLE_AFFECTING_ATTRS and doc is not None:
            doc._bump_style_epoch()

    def has_attribute(self, name: str) -> bool:
        """Return ``True`` if attribute *name* exists on this element.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.has_attribute("id")
        False
        >>> el.set_attribute("id", "x")
        >>> el.has_attribute("id")
        True
        """
        return name in self._attributes

    def get_attribute_node(self, name: str) -> "Attr | None":
        """Return the ``Attr`` object for attribute *name*, or ``None`` if absent.

        Delegates to ``self.attributes.get_named_item(name)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("id", "main")
        >>> attr = el.get_attribute_node("id")
        >>> attr.name
        'id'
        >>> attr.value
        'main'
        >>> el.get_attribute_node("missing") is None
        True
        """
        return self._attributes.get_named_item(name)  # type: ignore[return-value]

    def set_attribute_node(self, attr: "Attr") -> "Attr | None":
        """Insert or replace *attr* in this element's attribute set.

        If an attribute with the same name already exists, it is replaced and
        the displaced ``Attr`` is returned.  If no attribute with that name
        exists, *attr* is inserted and ``None`` is returned.

        Raises ``InUseAttributeError`` if *attr* already belongs to a different
        element.

        Examples
        --------
        >>> from aspose_html.dom import Document, Attr
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> attr = Attr("class", "box", owner_element=None)
        >>> displaced = el.set_attribute_node(attr)
        >>> displaced is None
        True
        >>> el.get_attribute("class")
        'box'
        """
        from aspose_html.dom._exceptions import InUseAttributeError  # noqa: PLC0415
        owner = attr._owner_element
        if owner is not None and owner is not self:
            raise InUseAttributeError(
                f"Attr {attr.name!r} is already owned by another element."
            )
        old = self._attributes.set_named_item(attr)  # type: ignore[assignment]
        attr._owner_element = self
        if old is not None:
            old._owner_element = None  # type: ignore[union-attr]
        return old  # type: ignore[return-value]

    def remove_attribute_node(self, attr: "Attr") -> "Attr":
        """Remove *attr* from this element's attribute set and return it.

        Raises ``NotFoundError`` if *attr* is not present on this element.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-x", "1")
        >>> attr = el.get_attribute_node("data-x")
        >>> removed = el.remove_attribute_node(attr)
        >>> removed is attr
        True
        >>> el.has_attribute("data-x")
        False
        """
        from aspose_html.dom._exceptions import NotFoundError  # noqa: PLC0415
        existing = self._attributes.get_named_item(attr.name)
        if existing is not attr:
            raise NotFoundError(
                f"Attr {attr.name!r} is not present on this element."
            )
        removed = self._attributes.remove_named_item(attr.name)  # type: ignore[assignment]
        removed._owner_element = None  # type: ignore[union-attr]
        return removed  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Namespaced Attr-node methods  (WHATWG DOM §6.5)
    # ------------------------------------------------------------------

    def get_attribute_node_ns(
        self,
        namespace_uri: str | None,
        local_name: str,
    ) -> "Attr | None":
        """Return the ``Attr`` node matching *namespace_uri* and *local_name*, or ``None``.

        Per WHATWG DOM §6.5.

        Parameters
        ----------
        namespace_uri : str | None
            Namespace URI to match. ``None`` and ``""`` both match the null namespace.
        local_name : str
            Local name to match.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("svg")
        >>> el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#a")
        >>> attr = el.get_attribute_node_ns("http://www.w3.org/1999/xlink", "href")
        >>> attr.value
        '#a'
        """
        ns = _norm_ns(namespace_uri)
        for attr in self._attributes:
            if _norm_ns(attr._namespace_uri) == ns and attr.local_name == local_name:  # type: ignore[union-attr]
                return attr  # type: ignore[return-value]
        return None

    def set_attribute_node_ns(
        self,
        attr: "Attr",
    ) -> "Attr | None":
        """Insert or replace a namespaced ``Attr`` node.

        Per WHATWG DOM §6.5. The replacement key is ``(namespace_uri, local_name)``
        from *attr*. Returns the displaced ``Attr`` or ``None``.

        Raises
        ------
        WrongDocumentError
            If *attr* is already owned by a different element.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("svg")
        >>> attr = doc.create_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href")
        >>> attr.value = "#b"
        >>> displaced = el.set_attribute_node_ns(attr)
        >>> displaced is None
        True
        >>> el.get_attribute_ns("http://www.w3.org/1999/xlink", "href")
        '#b'
        """
        from aspose_html.dom._exceptions import WrongDocumentError  # noqa: PLC0415

        owner = attr._owner_element
        if owner is not None and owner is not self:
            raise WrongDocumentError(
                f"Attr {attr.name!r} is already owned by another element."
            )

        ns = _norm_ns(attr._namespace_uri)
        local = attr.local_name
        old: "Attr | None" = None
        for existing in self._attributes:
            if (  # type: ignore[union-attr]
                _norm_ns(existing._namespace_uri) == ns  # type: ignore[union-attr]
                and existing.local_name == local  # type: ignore[union-attr]
            ):
                old = existing  # type: ignore[assignment]
                break

        if old is not None:
            old_val = old._value  # type: ignore[union-attr]
            # Replace in-place: remove by old qualified name, then insert new
            self._attributes._data.pop(old._name, None)  # type: ignore[union-attr]
            self._attributes._data[attr._name] = attr
            old._owner_element = None  # type: ignore[union-attr]
        else:
            old_val = None
            self._attributes._data[attr._name] = attr

        attr._owner_element = self

        if attr.local_name == "id" and attr._value:
            doc = self._owner_document
            if doc is not None:
                fn = getattr(doc, "_register_id", None)
                if fn:
                    fn(self, attr._value)

        doc = self._owner_document
        signal = getattr(doc, "_mutation_signal", None) if doc is not None else None
        if signal is not None and signal._observers:
            signal.notify_attribute(self, attr._name, None, old_val)

        return old

    def remove_attribute_node_ns(
        self,
        namespace_uri: str | None,
        local_name: str,
    ) -> "Attr":
        """Remove and return the ``Attr`` node matching *namespace_uri* and *local_name*.

        Per WHATWG DOM §6.5. Raises ``NotFoundError`` if absent.

        Parameters
        ----------
        namespace_uri : str | None
            Namespace URI to match (``""`` treated as ``None``).
        local_name : str
            Local name to match.

        Raises
        ------
        NotFoundError
            If no matching attribute exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("svg")
        >>> el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#c")
        >>> attr = el.remove_attribute_node_ns("http://www.w3.org/1999/xlink", "href")
        >>> attr.value
        '#c'
        >>> el.has_attribute_ns("http://www.w3.org/1999/xlink", "href")
        False
        """
        from aspose_html.dom._exceptions import NotFoundError  # noqa: PLC0415

        target = self.get_attribute_node_ns(namespace_uri, local_name)
        if target is None:
            raise NotFoundError(
                f"No attribute with namespace {namespace_uri!r} and local name {local_name!r}."
            )

        old_val = target._value
        self._attributes._data.pop(target._name, None)
        target._owner_element = None

        doc = self._owner_document
        signal = getattr(doc, "_mutation_signal", None) if doc is not None else None
        if signal is not None and signal._observers:
            signal.notify_attribute(self, target._name, None, old_val)

        return target

    # ------------------------------------------------------------------
    # Namespaced attribute methods  (WHATWG DOM §4.9.3)
    # ------------------------------------------------------------------

    def get_attribute_ns(
        self, namespace_uri: str | None, local_name: str
    ) -> str | None:
        """Return the value of the namespaced attribute, or ``None`` if absent.

        Parameters
        ----------
        namespace_uri : str or None
            The namespace URI to match, or ``None`` for the null namespace.
        local_name : str
            The local name of the attribute (without namespace prefix).

        Returns
        -------
        str or None
            The attribute value, or ``None`` if no matching attribute exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("svg")
        >>> el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#id")
        >>> el.get_attribute_ns("http://www.w3.org/1999/xlink", "href")
        '#id'
        >>> el.get_attribute_ns("http://www.w3.org/1999/xlink", "missing") is None
        True
        """
        for attr in self._attributes:
            if attr._namespace_uri == namespace_uri and attr.local_name == local_name:
                return attr._value
        return None

    def set_attribute_ns(
        self,
        namespace_uri: str | None,
        qualified_name: str,
        value: str,
    ) -> None:
        """Set a namespaced attribute to *value*, creating it if not present.

        The *qualified_name* may include a namespace prefix (e.g.
        ``"xlink:href"``).  The local name is the part after the colon, or
        the entire name if no colon is present.

        Parameters
        ----------
        namespace_uri : str or None
            The namespace URI, or ``None`` for the null namespace.
        qualified_name : str
            The qualified attribute name, e.g. ``"xlink:href"``.
        value : str
            The attribute value to set.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("svg")
        >>> el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#id")
        >>> el.get_attribute_ns("http://www.w3.org/1999/xlink", "href")
        '#id'
        """
        from aspose_html.dom._attr import Attr  # noqa: PLC0415

        local_name = qualified_name.split(":", 1)[1] if ":" in qualified_name else qualified_name

        for attr in self._attributes:
            if attr._namespace_uri == namespace_uri and attr.local_name == local_name:
                old_val = attr._value
                attr._value = value
                doc = self._owner_document
                if doc is not None:
                    win = doc._get_cached_default_view()
                    if win is not None and win._custom_elements is not None and win._custom_elements._is_observed(self, local_name):
                        win._custom_elements._fire_attribute_changed(self, local_name, old_val, value)
                return

        new_attr = Attr(
            qualified_name,
            value,
            owner_element=self,
            owner_document=self._owner_document,
            namespace_uri=namespace_uri,
            local_name_ns=local_name,
        )
        self._attributes.set_named_item(new_attr)
        doc = self._owner_document
        if doc is not None:
            win = doc._get_cached_default_view()
            if win is not None and win._custom_elements is not None and win._custom_elements._is_observed(self, local_name):
                win._custom_elements._fire_attribute_changed(self, local_name, None, value)

    def has_attribute_ns(
        self, namespace_uri: str | None, local_name: str
    ) -> bool:
        """Return ``True`` if a namespaced attribute with the given local name exists.

        Parameters
        ----------
        namespace_uri : str or None
            The namespace URI to match, or ``None`` for the null namespace.
        local_name : str
            The local name of the attribute.

        Returns
        -------
        bool

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("svg")
        >>> el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#id")
        >>> el.has_attribute_ns("http://www.w3.org/1999/xlink", "href")
        True
        >>> el.has_attribute_ns("http://www.w3.org/1999/xlink", "title")
        False
        """
        return self.get_attribute_ns(namespace_uri, local_name) is not None

    def remove_attribute_ns(
        self, namespace_uri: str | None, local_name: str
    ) -> None:
        """Remove the namespaced attribute. No-op if absent.

        Parameters
        ----------
        namespace_uri : str or None
            The namespace URI, or ``None`` for the null namespace.
        local_name : str
            The local name of the attribute to remove.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("svg")
        >>> el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#id")
        >>> el.remove_attribute_ns("http://www.w3.org/1999/xlink", "href")
        >>> el.has_attribute_ns("http://www.w3.org/1999/xlink", "href")
        False
        >>> el.remove_attribute_ns("http://www.w3.org/1999/xlink", "href")
        """
        target = None
        for attr in self._attributes:
            if attr._namespace_uri == namespace_uri and attr.local_name == local_name:
                target = attr
                break
        if target is not None:
            old_val = target._value
            self._attributes.remove_named_item(target._name)
            target._owner_element = None
            doc = self._owner_document
            if doc is not None:
                win = doc._get_cached_default_view()
                if win is not None and win._custom_elements is not None and win._custom_elements._is_observed(self, local_name):
                    win._custom_elements._fire_attribute_changed(self, local_name, old_val, None)

    def toggle_attribute(self, name: str, force: bool | None = None) -> bool:
        """Toggle attribute *name* and return its new presence state.

        When *force* is ``None`` (default), the attribute is toggled.
        When *force* is ``True``, the attribute is ensured present.
        When *force* is ``False``, the attribute is ensured absent.

        Raises ``InvalidCharacterError`` when *name* is empty, contains
        whitespace, or contains ``':'``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.toggle_attribute("hidden")
        True
        >>> el.has_attribute("hidden")
        True
        >>> el.toggle_attribute("hidden")
        False
        >>> el.has_attribute("hidden")
        False
        >>> el.toggle_attribute("disabled", force=True)
        True
        """
        from aspose_html.dom._exceptions import InvalidCharacterError  # noqa: PLC0415

        if name == "":
            raise InvalidCharacterError("Attribute local_name must not be empty.")
        if any(ch.isspace() for ch in name):
            raise InvalidCharacterError("Attribute local_name must not contain whitespace.")
        if ":" in name:
            raise InvalidCharacterError("Attribute local_name must not contain ':'.")

        has = self.has_attribute(name)
        if force is None:
            if has:
                self.remove_attribute(name)
                return False
            self.set_attribute(name, "")
            return True

        if force and not has:
            self.set_attribute(name, "")
        elif not force and has:
            self.remove_attribute(name)
        return bool(force)

    def get_attribute_names(self) -> list[str]:
        """Return the qualified names of all attributes in collection order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "box")
        >>> el.set_attribute("id", "main")
        >>> el.get_attribute_names()
        ['class', 'id']
        """
        return [attr._name for attr in self._attributes]

    def has_attributes(self) -> bool:
        """Return ``True`` when this element has one or more attributes.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("span")
        >>> el.has_attributes()
        False
        >>> el.set_attribute("id", "x")
        >>> el.has_attributes()
        True
        """
        return len(self._attributes) > 0

    def scroll_into_view(self, arg: bool | dict | None = True) -> None:
        """Scroll this element into view (no-op in server-side context).

        The optional *arg* accepts browser-compatible forms
        (``bool`` or options ``dict``) and is ignored.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.scroll_into_view()
        >>> el.scroll_into_view(False)
        >>> el.scroll_into_view({"behavior": "smooth"})
        """

    def scroll(
        self,
        x_or_options: float | dict | None = None,
        y: float | None = None,
    ) -> None:
        """Scroll this element to coordinates (no-op in server-side context).

        Accepts browser-compatible forms: ``scroll(x, y)`` or
        ``scroll({"top": ..., "left": ...})``. Arguments are ignored.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.scroll(0, 0)
        >>> el.scroll({"top": 100, "left": 0})
        """

    # ------------------------------------------------------------------
    # CSSOM View / Pointer Events / Fullscreen IDL stubs
    # ------------------------------------------------------------------

    def scroll_into_view_if_needed(self, center_if_needed: bool = True) -> None:
        """Scroll this element into view if it is not already visible (no-op in headless mode).

        Per the CSSOM View extension (Safari-origin, widely adopted). The
        *center_if_needed* parameter controls whether to centre the element
        when scrolling is required; it is accepted for API compatibility but
        ignored in this headless implementation.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.scroll_into_view_if_needed()
        >>> el.scroll_into_view_if_needed(False)
        """

    def set_pointer_capture(self, pointer_id: int) -> None:
        """Designate this element as the capture target for the given pointer (no-op).

        Per Pointer Events Level 2 §4.1. In a headless environment there is no
        pointer-input system, so this method is a no-op for API compatibility.

        Parameters
        ----------
        pointer_id:
            The identifier of the pointer to capture.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_pointer_capture(1)
        """

    def release_pointer_capture(self, pointer_id: int) -> None:
        """Release pointer capture for the given pointer id (no-op).

        Per Pointer Events Level 2 §4.1. Counterpart to :meth:`set_pointer_capture`.
        In a headless environment this is a no-op.

        Parameters
        ----------
        pointer_id:
            The identifier of the pointer to release.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.release_pointer_capture(1)
        """

    def has_pointer_capture(self, pointer_id: int) -> bool:
        """Return whether this element has pointer capture for the given id.

        Per Pointer Events Level 2 §4.1. In a headless environment no pointer
        capture state exists, so this always returns ``False``.

        Parameters
        ----------
        pointer_id:
            The identifier of the pointer to query.

        Returns
        -------
        bool
            Always ``False`` in headless mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.has_pointer_capture(1)
        False
        """
        return False

    def request_pointer_lock(self) -> None:
        """Request that the pointer be locked to this element (no-op).

        Per the Pointer Lock API §3.1. In a headless environment there is no
        pointer-lock mechanism; this method is a no-op for API compatibility.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("canvas")
        >>> el.request_pointer_lock()
        """

    def request_fullscreen(self, options: "dict | None" = None) -> None:
        """Request that this element be displayed in fullscreen mode (no-op).

        Per the Fullscreen API §5. In a headless environment there is no
        display surface; this method is a no-op for API compatibility. The
        optional *options* dict (``navigationUI`` key) is accepted but ignored.

        Parameters
        ----------
        options:
            Optional ``RequestFullscreenOptions`` dict, ignored in headless mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.request_fullscreen()
        >>> el.request_fullscreen({"navigationUI": "hide"})
        """

    def check_visibility(self, options: "dict | None" = None) -> bool:
        """Return whether this element is visible in the current rendering (always ``True``).

        Per CSSOM View Level 1 §11.1. In a headless environment there is no
        layout engine to determine visibility; all elements are considered visible.
        The optional *options* dict (keys: ``checkOpacity``, ``checkVisibilityCSS``,
        ``contentVisibilityAuto``, ``opacityProperty``, ``visibilityProperty``) is
        accepted but ignored.

        Parameters
        ----------
        options:
            Optional ``CheckVisibilityOptions`` dict, ignored in headless mode.

        Returns
        -------
        bool
            Always ``True`` in headless mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.check_visibility()
        True
        >>> el.check_visibility({"visibilityProperty": True})
        True
        """
        return True

    # ------------------------------------------------------------------
    # Selector queries
    # ------------------------------------------------------------------

    def query_selector(self, selector: str) -> Element | None:
        """Return the first element in the subtree matching *selector*.

        Delegates to ``aspose_html.css.select`` (lazy import).

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> el = doc.create_element("div")  # doctest: +SKIP
        >>> el.query_selector("p")  # doctest: +SKIP
        """
        from aspose_html.css import select  # lazy import — module added in /8
        results = select(self, selector, first_only=True)
        return results[0] if results else None

    def query_selector_all(self, selector: str) -> NodeList:
        """Return a static NodeList of all elements matching *selector*.

        Delegates to ``aspose_html.css.select`` (lazy import).

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> el = doc.create_element("div")  # doctest: +SKIP
        >>> el.query_selector_all("p")  # doctest: +SKIP
        """
        from aspose_html.css import select  # lazy import
        results = select(self, selector, first_only=False)
        return _StaticNodeList(results)

    def matches(self, selector: str) -> bool:
        """Return ``True`` if this element matches the CSS *selector*.

        Delegates to ``aspose_html.css.element_matches`` (lazy import).
        Works for both attached and detached elements.

        Raises ``SyntaxError`` if *selector* is syntactically invalid.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> div.set_attribute("class", "active")
        >>> doc.append_child(div)
        <Element 'DIV' class='active'>
        >>> div.matches("div")
        True
        >>> div.matches(".active")
        True
        >>> div.matches("span")
        False
        """
        # : delegate to CSS module — no custom selector logic here.
        # element_matches() () tests self directly, so it works for both
        # attached and detached elements without bypassing the select() boundary.
        from aspose_html.css import element_matches  # noqa: PLC0415

        return element_matches(self, selector)

    def webkit_matches_selector(self, selector: str) -> bool:
        """Browser-compat alias for :meth:`matches`.

        Equivalent to ``self.matches(selector)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.webkit_matches_selector("div")
        True
        >>> el.webkit_matches_selector("span")
        False
        """
        return self.matches(selector)

    def closest(self, selector: str) -> "Element | None":
        """Return the nearest ancestor (inclusive) matching the CSS *selector*.

        Starting from ``self``, walks up the ancestor chain via
        ``parent_element`` and returns the first element for which
        ``element.matches(selector)`` is ``True``.  Returns ``None`` if no
        ancestor (including ``self``) matches, or if the chain is exhausted.

        Never reaches the ``Document`` node — stops when ``parent_element``
        is ``None``.

        Raises ``SyntaxError`` if *selector* is syntactically invalid.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> outer = doc.create_element("div")
        >>> inner = doc.create_element("span")
        >>> doc.append_child(outer)
        <Element 'DIV'>
        >>> outer.append_child(inner)
        <Element 'SPAN'>
        >>> inner.closest("div") is outer
        True
        >>> inner.closest("article") is None
        True
        >>> outer.closest("div") is outer
        True
        """
        # : self-inclusive; walk via parent_element (never reaches Document).
        # See : must NOT call select(ancestor, selector) directly because
        # that returns all matching descendants of ancestor, not just ancestors.
        node: Element | None = self
        while node is not None:
            if node.matches(selector):
                return node
            node = node.parent_element
        return None

    # ------------------------------------------------------------------
    # Subtree query methods  # See 
    # ------------------------------------------------------------------

    def get_elements_by_tag_name(self, qualified_name: str) -> HTMLCollection:
        """Return all descendant elements whose tag name matches *qualified_name*.

        The comparison is case-insensitive (comparison is performed on
        ``local_name``, which is always lowercase for HTML-namespace elements).
        Passing ``'*'`` returns all descendant elements regardless of tag name.

        Results are in tree order (depth-first, pre-order) and the returned
        collection re-scans the subtree on every access (live semantics).

        Parameters
        ----------
        qualified_name : str
            The tag name to match, case-insensitively, or ``'*'`` for all.

        Returns
        -------
        HTMLCollection
            A live collection of matching descendant elements.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> p1 = doc.create_element("p")
        >>> p2 = doc.create_element("p")
        >>> doc.append_child(div)
        <Element 'DIV'>
        >>> div.append_child(p1)
        <Element 'P'>
        >>> div.append_child(p2)
        <Element 'P'>
        >>> len(div.get_elements_by_tag_name("p"))
        2
        >>> len(div.get_elements_by_tag_name("P"))
        2
        >>> len(div.get_elements_by_tag_name("*"))
        2
        >>> len(div.get_elements_by_tag_name("span"))
        0
        """
        if qualified_name == "*":
            filter_fn = lambda el: True  # noqa: E731
        else:
            name_lower = qualified_name.lower()
            filter_fn = lambda el: el._local_name == name_lower  # noqa: E731
        # : delegates to _SubtreeHTMLCollection which performs
        # depth-first pre-order traversal conforming to WHATWG DOM §4.2.6.
        return _SubtreeHTMLCollection(self, filter_fn)  # type: ignore[return-value]

    def get_elements_by_class_name(self, class_names: str) -> HTMLCollection:
        """Return all descendant elements that carry all of the given class tokens.

        *class_names* is a whitespace-separated string of one or more class
        tokens.  An element matches only if it has ALL of the requested tokens
        in its ``class`` attribute.  Token matching is case-sensitive (WHATWG
        DOM Standard §4.2.6).

        An empty *class_names* string (or one composed entirely of whitespace)
        splits to the empty set, which every element satisfies — all descendants
        are returned.

        Results are in tree order (depth-first, pre-order) and the returned
        collection re-scans the subtree on every access (live semantics).

        Parameters
        ----------
        class_names : str
            Space-separated CSS class tokens that a matching element must all
            carry.

        Returns
        -------
        HTMLCollection
            A live collection of matching descendant elements.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> a = doc.create_element("span")
        >>> b = doc.create_element("span")
        >>> a.set_attribute("class", "foo bar")
        >>> b.set_attribute("class", "foo")
        >>> doc.append_child(div)
        <Element 'DIV'>
        >>> div.append_child(a)
        <Element 'SPAN' class='foo bar'>
        >>> div.append_child(b)
        <Element 'SPAN' class='foo'>
        >>> len(div.get_elements_by_class_name("foo"))
        2
        >>> len(div.get_elements_by_class_name("foo bar"))
        1
        >>> len(div.get_elements_by_class_name("baz"))
        0
        """
        class_set = set(class_names.split())

        def filter_fn(el: "Element") -> bool:
            # : class_list re-reads the class attribute on every call
            # providing live semantics consistent with Document equivalent.
            return class_set.issubset(set(el.class_list))

        # : delegates to _SubtreeHTMLCollection which performs
        # depth-first pre-order traversal conforming to WHATWG DOM §4.2.6.
        return _SubtreeHTMLCollection(self, filter_fn)  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Hierarchy rules
    # ------------------------------------------------------------------

    def _validate_insertion(
        self, node: Node, replacing: Node | None = None
    ) -> None:
        super()._validate_insertion(node, replacing)
        # Element can contain any node type except Document, DocumentType,
        # and Attr (Attr is handled by base class).
        nt = node._node_type
        if nt in (NodeType.DOCUMENT_NODE, NodeType.DOCUMENT_TYPE_NODE):
            from aspose_html.dom._exceptions import HierarchyRequestError as HRE
            raise HRE(f"Element cannot contain node type {nt}.")

    # ------------------------------------------------------------------
    # ChildNode mixin (WHATWG DOM §4.2.4)
    # ------------------------------------------------------------------

    def remove(self) -> None:
        """Remove this element from its parent node.

        No-op if this element has no parent (detached).

        Per WHATWG DOM §4.2.4 ChildNode.remove().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> child = doc.create_element("span")
        >>> _ = doc.append_child(parent)
        >>> _ = parent.append_child(child)
        >>> child.remove()
        >>> len(parent.child_nodes)
        0
        >>> child.parent_node is None
        True
        """
        if self._parent is not None:
            self._parent.remove_child(self)

    def before(self, *nodes: "Node | str") -> None:
        """Insert *nodes* immediately before this element in its parent.

        Strings in *nodes* are converted to Text nodes using
        ``owner_document.create_text_node()``. No-op if detached or *nodes* is empty.

        Per WHATWG DOM §4.2.4 ChildNode.before().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> child = doc.create_element("span")
        >>> _ = doc.append_child(parent)
        >>> _ = parent.append_child(child)
        >>> sibling = doc.create_element("p")
        >>> child.before(sibling)
        >>> parent.first_child is sibling
        True
        """
        if self._parent is None or not nodes:
            return
        coerced = _coerce_nodes(nodes, self._owner_document)
        for node in coerced:
            self._parent.insert_before(node, self)

    def after(self, *nodes: "Node | str") -> None:
        """Insert *nodes* immediately after this element in its parent.

        Strings are converted to Text nodes. No-op if detached or *nodes* is empty.

        Per WHATWG DOM §4.2.4 ChildNode.after().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> child = doc.create_element("span")
        >>> _ = doc.append_child(parent)
        >>> _ = parent.append_child(child)
        >>> following = doc.create_element("p")
        >>> child.after(following)
        >>> parent.last_child is following
        True
        """
        if self._parent is None or not nodes:
            return
        coerced = _coerce_nodes(nodes, self._owner_document)
        next_ref = self.next_sibling
        if next_ref is None:
            for node in coerced:
                self._parent.append_child(node)
        else:
            for node in coerced:
                self._parent.insert_before(node, next_ref)

    def replace_with(self, *nodes: "Node | str") -> None:
        """Replace this element with *nodes* in its parent.

        Inserts *nodes* immediately before this element, then removes self.
        Strings are converted to Text nodes. No-op if detached.

        Per WHATWG DOM §4.2.4 ChildNode.replaceWith().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> old = doc.create_element("span")
        >>> new = doc.create_element("p")
        >>> _ = doc.append_child(parent)
        >>> _ = parent.append_child(old)
        >>> old.replace_with(new)
        >>> parent.first_child is new
        True
        >>> old.parent_node is None
        True
        """
        if self._parent is None:
            return
        coerced = _coerce_nodes(nodes, self._owner_document)
        for node in coerced:
            self._parent.insert_before(node, self)
        self._parent.remove_child(self)

    # ------------------------------------------------------------------
    # ParentNode mixin (WHATWG DOM §4.2.6)
    # ------------------------------------------------------------------

    def prepend(self, *nodes: "Node | str") -> None:
        """Insert *nodes* before the first child of this element.

        Strings are converted to Text nodes. No-op if *nodes* is empty.

        Per WHATWG DOM §4.2.6 ParentNode.prepend().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> _ = doc.append_child(parent)
        >>> a = doc.create_element("a")
        >>> _ = parent.append_child(a)
        >>> b = doc.create_element("b")
        >>> parent.prepend(b)
        >>> parent.first_child is b
        True
        """
        if not nodes:
            return
        coerced = _coerce_nodes(nodes, self._owner_document)
        first = self.first_child
        for node in coerced:
            self.insert_before(node, first)

    def append(self, *nodes: "Node | str") -> None:
        """Append *nodes* as the last children of this element.

        Strings are converted to Text nodes. Accepts multiple arguments and
        strings, unlike ``append_child`` (single node only).
        No-op if *nodes* is empty.

        Per WHATWG DOM §4.2.6 ParentNode.append().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> _ = doc.append_child(parent)
        >>> a = doc.create_element("a")
        >>> parent.append(a, "text")
        >>> parent.child_nodes[0] is a
        True
        >>> parent.child_nodes[1].data
        'text'
        """
        if not nodes:
            return
        coerced = _coerce_nodes(nodes, self._owner_document)
        for node in coerced:
            self.append_child(node)

    def replace_children(self, *nodes: "Node | str") -> None:
        """Remove all children, then append *nodes* as new children.

        Strings are converted to Text nodes. Calling with no arguments clears
        all children.

        Per WHATWG DOM §4.2.6 ParentNode.replaceChildren().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> _ = doc.append_child(parent)
        >>> old = doc.create_element("span")
        >>> _ = parent.append_child(old)
        >>> new = doc.create_element("p")
        >>> parent.replace_children(new)
        >>> parent.first_child is new
        True
        >>> parent.replace_children()
        >>> len(parent.child_nodes)
        0
        """
        for child in list(self._children):
            self.remove_child(child)
        coerced = _coerce_nodes(nodes, self._owner_document)
        for node in coerced:
            self.append_child(node)

    # ------------------------------------------------------------------
    # CSSOM View geometry stubs ( / )
    # ------------------------------------------------------------------
    # All geometry values are constant zero.  This library has no layout
    # engine; the stubs let calling code run without AttributeError in a
    # server-side context.  See  for rationale and .NET parity notes.
    # ------------------------------------------------------------------

    def get_bounding_client_rect(self) -> "DOMRect":
        """Return the bounding client rectangle (all-zero stub).

        In a server-side context there is no layout engine, so the returned
        rectangle always has ``x``, ``y``, ``width``, and ``height`` equal to
        ``0.0``.  This mirrors the .NET ``GetBoundingClientRect()`` behaviour
        in headless mode ().

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMRect
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> r = el.get_bounding_client_rect()
        >>> isinstance(r, DOMRect)
        True
        >>> r.width
        0.0
        """
        from aspose_html.dom._geometry import DOMRect  # noqa: PLC0415
        return DOMRect()

    def get_client_rects(self) -> "DOMRectList":
        """Return the client rectangle list (empty in server-side context).

        Returns an empty :class:`DOMRectList` because there is no layout
        engine available.  This mirrors .NET ``GetClientRects()`` in headless
        mode ().

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMRectList
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> rects = el.get_client_rects()
        >>> isinstance(rects, DOMRectList)
        True
        >>> len(rects)
        0
        """
        from aspose_html.dom._geometry import DOMRectList  # noqa: PLC0415
        return DOMRectList([])

    def get_animations(self) -> list[object]:
        """Return active animations for this element (headless stub: always ``[]``).

        This runtime has no animation timeline/renderer, so element animation
        inspection is deterministic and always empty.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.get_animations()
        []
        """
        return []

    @property
    def scroll_width(self) -> int:
        """Content scroll width in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").scroll_width
        0
        """
        return 0

    @property
    def scroll_height(self) -> int:
        """Content scroll height in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").scroll_height
        0
        """
        return 0

    @property
    def client_width(self) -> int:
        """Inner width including padding, excluding border (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").client_width
        0
        """
        return 0

    @property
    def client_height(self) -> int:
        """Inner height including padding, excluding border (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").client_height
        0
        """
        return 0

    @property
    def scroll_top(self) -> int:
        """Vertical scroll offset in CSS pixels (stub: 0).

        The setter is a no-op — scroll position cannot be tracked without a
        layout/rendering engine.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").scroll_top
        0
        """
        return 0

    @scroll_top.setter
    def scroll_top(self, value: int) -> None:
        """Set vertical scroll offset (no-op in server-side context)."""

    @property
    def scroll_left(self) -> int:
        """Horizontal scroll offset in CSS pixels (stub: 0).

        The setter is a no-op — scroll position cannot be tracked without a
        layout/rendering engine.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").scroll_left
        0
        """
        return 0

    @scroll_left.setter
    def scroll_left(self, value: int) -> None:
        """Set horizontal scroll offset (no-op in server-side context)."""

    @property
    def offset_width(self) -> int:
        """Layout border-box width in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").offset_width
        0
        """
        return 0

    @property
    def offset_height(self) -> int:
        """Layout border-box height in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").offset_height
        0
        """
        return 0

    @property
    def offset_top(self) -> int:
        """Top offset from ``offsetParent`` in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").offset_top
        0
        """
        return 0

    @property
    def offset_left(self) -> int:
        """Left offset from ``offsetParent`` in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("div").offset_left
        0
        """
        return 0

    @property
    def offset_parent(self) -> None:
        """The offset parent element; always ``None`` in headless mode.

        CSSOM View §5.5 — in a real browser this returns the nearest positioned
        ancestor; in headless mode there is no layout context.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.offset_parent is None
        True
        """
        return None

    @property
    def client_top(self) -> int:
        """Width of the top CSS border in pixels; always ``0`` in headless mode.

        CSSOM View §5.4.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().create_element("div").client_top
        0
        """
        return 0

    @property
    def client_left(self) -> int:
        """Width of the left CSS border in pixels; always ``0`` in headless mode.

        CSSOM View §5.4.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().create_element("div").client_left
        0
        """
        return 0

    # ------------------------------------------------------------------
    #  — Shadow DOM / slot stubs ( / )
    # ------------------------------------------------------------------

    @property
    def part(self) -> "DOMTokenList":
        """Live DOMTokenList reflecting the element ``part`` attribute.

        DOM §4.2.3.  Creates a fresh DOMTokenList on each access backed by
        the ``part`` attribute (same pattern as ``options`` on
        HTMLDataListElement — no slot caching required for rare-access lists).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.part.add("highlighted")
        >>> el.get_attribute("part")
        'highlighted'
        >>> el.part.contains("highlighted")
        True
        """
        from aspose_html.dom._token_list import DOMTokenList  # noqa: PLC0415
        return DOMTokenList(self, "part")

    @property
    def shadow_root(self):
        """Always ``None`` in headless mode.

        DOM §4.2.3 — returns the element's shadow root when attached.
        Headless execution has no shadow tree; returns None.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().create_element("div").shadow_root is None
        True
        """
        return None

    @property
    def slot(self) -> str:
        """Reflects the ``slot`` content attribute (DOM §4.2.3).

        Returns ``""`` when the attribute is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("span")
        >>> el.slot
        ''
        >>> el.slot = "named"
        >>> el.get_attribute("slot")
        'named'
        """
        return self.get_attribute("slot") or ""

    @slot.setter
    def slot(self, value: str) -> None:
        self.set_attribute("slot", value)

    def attach_shadow(self, init: "dict | None" = None) -> None:
        """Raise ``NotSupportedError`` — shadow trees are not supported in headless mode.

        DOM §4.2.3.  A full shadow-tree implementation requires a rendering
        context; headless execution does not provide one.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> el = Document().create_element("div")
        >>> try:
        ...     el.attach_shadow({"mode": "open"})
        ... except NotSupportedError:
        ...     print("raised")
        raised
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "attachShadow is not supported in headless mode"
        )

    @property
    def assigned_slot(self):
        """Always ``None`` in headless mode.

        DOM Slottable mixin §4.2.6 — returns the HTMLSlotElement the element
        is assigned to. No slot assignment is possible without shadow DOM.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().create_element("span").assigned_slot is None
        True
        """
        return None

    # ------------------------------------------------------------------
    # Clone
    # ------------------------------------------------------------------

    def _clone_self(self) -> Element:
        """Create a shallow copy of this element (no children).

        Copies the element's tag name, namespace URI, prefix, and all
        attributes.  Namespaced attributes are copied through
        ``set_attribute_ns()`` to preserve ``_namespace_uri`` and
        ``_local_name_ns`` ( / WHATWG DOM §4.5).  Plain attributes
        are copied through ``set_attribute()``.

        Lazy-initialised slots (``_class_list``, ``_style_declaration``,
        ``_dataset``) and ``_event_listeners`` are **not** copied — the
        fresh ``Element`` constructor sets them to ``None``, so they are
        independently recreated on first access on the clone.

        Not part of the public API.  Called by ``Node.clone_node()``.
        """
        el = Element(
            self._local_name,
            namespace_uri=self._namespace_uri,
            prefix=self._prefix,
            owner_document=self._owner_document,
        )
        for attr in self._attributes:
            # : preserve namespace context per WHATWG DOM §4.5 clone algorithm.
            # set_attribute() would create a plain (non-namespaced) Attr, losing
            # _namespace_uri and _local_name_ns for namespaced attributes ().
            if attr._namespace_uri is not None:
                el.set_attribute_ns(attr._namespace_uri, attr.name, attr.value)  # type: ignore[union-attr]
            else:
                el.set_attribute(attr.name, attr.value)  # type: ignore[union-attr]
        return el

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        parts = [f"'{ self._tag_name}'"]
        el_id = self.id
        el_cls = self.class_name
        if el_id:
            parts.append(f"id={el_id!r}")
        if el_cls:
            parts.append(f"class={el_cls!r}")
        return f"<Element { ' '.join(parts)}>"

    __str__ = __repr__
