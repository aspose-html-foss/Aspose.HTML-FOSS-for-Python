"""Node — abstract base class for all DOM nodes."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from aspose_html.dom._event_target import EventTarget
from aspose_html.dom._node_type import NodeType
from aspose_html.dom._exceptions import (
    HierarchyRequestError,
    WrongDocumentError,
    NotFoundError,
)

if TYPE_CHECKING:
    from aspose_html.dom._document import Document
    from aspose_html.dom._element import Element
    from aspose_html.dom._collections import NodeList


# ---------------------------------------------------------------------------
# Duck-typed helpers (avoid circular imports at runtime)
# ---------------------------------------------------------------------------

class DocumentPosition:
    """Named constants for the bitmask returned by ``Node.compare_document_position``.

    Constants conform to WHATWG DOM §4.4.3.

    Examples
    --------
    >>> DocumentPosition.DOCUMENT_POSITION_FOLLOWING
    4
    >>> DocumentPosition.DOCUMENT_POSITION_PRECEDING
    2
    >>> DocumentPosition.DOCUMENT_POSITION_CONTAINS
    8
    """

    DOCUMENT_POSITION_DISCONNECTED = 1
    DOCUMENT_POSITION_PRECEDING = 2
    DOCUMENT_POSITION_FOLLOWING = 4
    DOCUMENT_POSITION_CONTAINS = 8
    DOCUMENT_POSITION_CONTAINED_BY = 16
    DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC = 32


def _register_ids(doc: object, node: Node) -> None:
    """Call ``doc._walk_register_ids(node)`` if available."""
    fn = getattr(doc, "_walk_register_ids", None)
    if fn is not None:
        fn(node)


def _unregister_ids(doc: object, node: Node) -> None:
    """Call ``doc._walk_unregister_ids(node)`` if available."""
    fn = getattr(doc, "_walk_unregister_ids", None)
    if fn is not None:
        fn(node)


def _walk_and_dispatch_connected(node: "Node") -> None:
    stack = [node]
    while stack:
        current = stack.pop(0)
        callback = getattr(current, "_inserted_into_tree", None)
        if callback is not None:
            callback()
        stack[0:0] = list(current._children)


def _walk_and_dispatch_disconnected(node: "Node") -> None:
    stack = [node]
    while stack:
        current = stack.pop(0)
        callback = getattr(current, "_removed_from_tree", None)
        if callback is not None:
            callback()
        stack[0:0] = list(current._children)


def _adopt(node: "Node", document: "Document | None") -> None:
    """Recursively set *node* and all its descendants' ``_owner_document``
    to *document*.

    This is the low-level "adopt" primitive. Callers that need the full
    WHATWG adopt algorithm (including parent removal) must call
    ``Document.adopt_node()`` instead.

    Uses ``node._children`` directly to avoid any risk of a cached NodeList
    being iterated during a structural modification. See ADR-026.
    """
    # INV-005: WHATWG DOM §4.6 adopt algorithm — recursively repoint owner_document.
    node._owner_document = document
    for child in node._children:
        _adopt(child, document)


class Node(EventTarget, ABC):  # See ADR-040: EventTarget before ABC in MRO
    """Abstract base class for all WHATWG DOM nodes.

    Do not instantiate directly — use the concrete subclasses or the
    factory methods on ``Document``.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> isinstance(el, Node)
    True
    """

    __slots__ = (
        "_node_type",
        "_parent",
        "_children",
        "_owner_document",
        "_child_nodes_cache",
        "_user_data_map",
    )

    def __init__(self, node_type: int, owner_document: Document | None = None) -> None:
        super().__init__()  # See ADR-040: initialises EventTarget._event_listeners = None
        self._node_type: int = node_type
        self._parent: Node | None = None
        self._children: list[Node] = []
        self._owner_document: Document | None = owner_document
        self._child_nodes_cache: NodeList | None = None
        self._user_data_map: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Read-only properties
    # ------------------------------------------------------------------

    @property
    def node_type(self) -> int:
        """Integer node type constant from ``NodeType``.

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeType
        >>> doc = Document()
        >>> doc.node_type == NodeType.DOCUMENT_NODE
        True
        """
        return self._node_type

    @property
    @abstractmethod
    def node_name(self) -> str:
        """The name of this node (tag name, ``'#text'``, etc.)."""

    @property
    def node_value(self) -> str | None:
        """Character data for CharacterData nodes; ``None`` otherwise.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.node_value is None
        True
        """
        return None

    @node_value.setter
    def node_value(self, value: str | None) -> None:
        """Setting node_value on non-CharacterData nodes is a no-op."""

    @property
    def text_content(self) -> str | None:
        """The text content of this node, or ``None`` for Document and DocumentType.

        Per WHATWG DOM §4.4. Concrete behaviour depends on node type:

        - Element, DocumentFragment: concatenation of all descendant Text
          node data (DFS order).
        - CharacterData (Text, Comment, CDATASection, ProcessingInstruction):
          returns ``data``.
        - Document, DocumentType: ``None`` (this base implementation).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.text_content is None
        True
        """
        return None  # See ADR-013: base default for Document/DocumentType

    @text_content.setter
    def text_content(self, value: str | None) -> None:
        """No-op for Document and DocumentType nodes (WHATWG DOM §4.4)."""

    @property
    def parent_node(self) -> Node | None:
        """The parent node, or ``None`` if this node has no parent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> el.parent_node is None
        True
        >>> doc.append_child(el)
        <Element 'P'>
        >>> el.parent_node is doc
        True
        """
        return self._parent

    @property
    def parent_element(self) -> Element | None:
        """The parent node if it is an Element; ``None`` otherwise.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> span = doc.create_element("span")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> el.append_child(span)
        <Element 'SPAN'>
        >>> span.parent_element is el
        True
        """
        p = self._parent
        if p is not None and p._node_type == NodeType.ELEMENT_NODE:
            return p  # type: ignore[return-value]
        return None

    @property
    def is_connected(self) -> bool:
        """Whether this node is part of a document's node tree (WHATWG DOM §4.4).

        Returns ``True`` when the node's root is a :class:`Document` instance,
        ``False`` for detached nodes or nodes whose root is a
        ``DocumentFragment`` (or any non-Document root).

        A ``Document`` itself always returns ``True``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.is_connected
        False
        >>> _ = doc.append_child(el)
        >>> el.is_connected
        True
        """
        from aspose_html.dom._document import Document  # local import — avoids circular import  # noqa: PLC0415
        node: Node | None = self
        while node is not None:
            if node._parent is None:
                return isinstance(node, Document)
            node = node._parent  # type: ignore[assignment]
        return False  # pragma: no cover

    def get_root_node(self, *, composed: bool = False) -> "Node":
        """Return the root of the node's tree.

        Walks the ancestor chain upward until a node with no parent is reached
        and returns that node.  For nodes attached to a document, this returns
        the ``Document`` node.  For detached nodes, this returns the topmost
        ancestor in the detached subtree (which may be the node itself if it
        has no parent).

        The *composed* parameter relates to Shadow DOM composition.  In this
        implementation Shadow DOM is not supported, so *composed* is accepted
        but has no effect — the method always returns the light-tree root.

        Per WHATWG DOM §4.4.

        Parameters
        ----------
        composed : bool, optional
            Ignored in this implementation (Shadow DOM is out of scope).
            Provided for API compatibility.  Defaults to ``False``.

        Returns
        -------
        Node
            The root node of this node's tree.  Never ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.get_root_node() is el
        True
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> el.get_root_node() is doc
        True
        >>> doc.get_root_node() is doc
        True
        """
        # INV-005: WHATWG DOM §4.4 — walk _parent until None.
        node: Node = self
        while node._parent is not None:
            node = node._parent
        return node

    @property
    def owner_document(self) -> Document | None:
        """The Document this node belongs to, or ``None`` for Document itself.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.owner_document is doc
        True
        """
        return self._owner_document

    @property
    def child_nodes(self) -> NodeList:
        """A live NodeList of all child nodes.

        The same object is returned on every call (cached per node).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> nl = doc.child_nodes
        >>> nl is doc.child_nodes
        True
        """
        if self._child_nodes_cache is None:
            from aspose_html.dom._collections import NodeList
            self._child_nodes_cache = NodeList(self._children)
        return self._child_nodes_cache

    @property
    def first_child(self) -> Node | None:
        """The first child node, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.first_child is None
        True
        """
        return self._children[0] if self._children else None

    @property
    def last_child(self) -> Node | None:
        """The last child node, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.last_child is None
        True
        """
        return self._children[-1] if self._children else None

    @property
    def previous_sibling(self) -> Node | None:
        """The preceding sibling node, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> el.previous_sibling is None
        True
        """
        p = self._parent
        if p is None:
            return None
        idx = p._children.index(self)
        return p._children[idx - 1] if idx > 0 else None

    @property
    def next_sibling(self) -> Node | None:
        """The following sibling node, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> el.next_sibling is None
        True
        """
        p = self._parent
        if p is None:
            return None
        idx = p._children.index(self)
        nxt = idx + 1
        return p._children[nxt] if nxt < len(p._children) else None

    def has_child_nodes(self) -> bool:
        """Return whether this node has at least one direct child node.

        Legacy compatibility alias for WHATWG DOM ``hasChildNodes`` and
        Aspose.HTML .NET ``HasChildNodes``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.has_child_nodes()
        False
        >>> doc.append_child(doc.create_element("div"))
        <Element 'DIV'>
        >>> doc.has_child_nodes()
        True
        >>> leaf = doc.create_text_node("x")
        >>> leaf.has_child_nodes()
        False
        """
        return self.first_child is not None

    def lookup_namespace_uri(self, prefix: str | None) -> str | None:
        """Return the effective namespace URI for *prefix* in this node context.

        Legacy compatibility alias for WHATWG DOM ``lookupNamespaceURI`` and
        Aspose.HTML .NET ``Node.LookupNamespaceURI(string)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> root = doc.create_element("root")
        >>> root.set_attribute("xmlns", "urn:default")
        >>> root.set_attribute("xmlns:svg", "http://www.w3.org/2000/svg")
        >>> doc.append_child(root)
        <Element 'ROOT'>
        >>> root.lookup_namespace_uri(None)
        'urn:default'
        >>> root.lookup_namespace_uri("svg")
        'http://www.w3.org/2000/svg'
        >>> root.lookup_namespace_uri("missing") is None
        True
        """
        element = self._namespace_lookup_context_element()
        normalized_prefix = None if prefix == "" else prefix

        if normalized_prefix == "xml":
            return "http://www.w3.org/XML/1998/namespace"
        if normalized_prefix == "xmlns":
            return "http://www.w3.org/2000/xmlns/"

        while element is not None:
            attrs = getattr(element, "_attributes", ())
            if normalized_prefix is None:
                for attr in attrs:
                    if attr.name == "xmlns":
                        return attr.value or None
            else:
                if (
                    element._prefix == normalized_prefix  # type: ignore[attr-defined]
                    and element._namespace_uri is not None  # type: ignore[attr-defined]
                ):
                    return element._namespace_uri  # type: ignore[attr-defined]
                xmlns_name = f"xmlns:{normalized_prefix}"
                for attr in attrs:
                    if attr.name == xmlns_name:
                        return attr.value or None

            element = element.parent_element

        if normalized_prefix is None:
            fallback_element = self._namespace_lookup_context_element()
            while fallback_element is not None:
                if (
                    fallback_element._prefix is None  # type: ignore[attr-defined]
                    and fallback_element._namespace_uri is not None  # type: ignore[attr-defined]
                ):
                    return fallback_element._namespace_uri  # type: ignore[attr-defined]
                fallback_element = fallback_element.parent_element

        return None

    def lookup_prefix(self, namespace_uri: str | None) -> str | None:
        """Return the effective prefix for *namespace_uri* in this node context.

        Legacy compatibility alias for WHATWG DOM ``lookupPrefix`` and
        Aspose.HTML .NET ``Node.LookupPrefix(string)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> root = doc.create_element("root")
        >>> root.set_attribute("xmlns", "urn:default")
        >>> root.set_attribute("xmlns:svg", "http://www.w3.org/2000/svg")
        >>> doc.append_child(root)
        <Element 'ROOT'>
        >>> root.lookup_prefix("http://www.w3.org/2000/svg")
        'svg'
        >>> root.lookup_prefix("urn:missing") is None
        True
        >>> root.lookup_prefix(None) is None
        True
        """
        if namespace_uri is None:
            return None
        if namespace_uri == "http://www.w3.org/XML/1998/namespace":
            return "xml"
        if namespace_uri == "http://www.w3.org/2000/xmlns/":
            return "xmlns"

        element = self._namespace_lookup_context_element()
        while element is not None:
            if (
                element._prefix is not None  # type: ignore[attr-defined]
                and element._namespace_uri == namespace_uri  # type: ignore[attr-defined]
            ):
                return element._prefix  # type: ignore[attr-defined]

            attrs = getattr(element, "_attributes", ())
            for attr in attrs:
                if attr.name.startswith("xmlns:") and attr.value == namespace_uri:
                    prefix = attr.name[6:]
                    if prefix:
                        return prefix

            element = element.parent_element

        return None

    def is_default_namespace(self, namespace_uri: str | None) -> bool:
        """Return whether *namespace_uri* equals this node context default namespace.

        Legacy compatibility alias for WHATWG DOM ``isDefaultNamespace`` and
        Aspose.HTML .NET ``Node.IsDefaultNamespace(string)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> root = doc.create_element("root")
        >>> root.set_attribute("xmlns", "urn:default")
        >>> doc.append_child(root)
        <Element 'ROOT'>
        >>> root.is_default_namespace("urn:default")
        True
        >>> root.is_default_namespace("urn:other")
        False
        >>> plain = doc.create_element("plain")
        >>> plain.is_default_namespace("urn:default")
        False
        """
        effective_default_namespace = self.lookup_namespace_uri(None)
        if effective_default_namespace is None:
            return False
        return namespace_uri == effective_default_namespace

    def is_supported(self, feature: str, version: str | None = None) -> bool:
        """Return legacy feature-probe compatibility status.

        Legacy compatibility alias for WHATWG DOM ``isSupported`` and
        Aspose.HTML .NET ``Node.IsSupported(string, string)``.

        This implementation intentionally does not advertise any runtime
        feature claims through legacy probes.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.is_supported("core")
        False
        >>> doc.is_supported("XML", "3.0")
        False
        >>> doc.is_supported("", None)
        False
        """
        _ = (feature, version)
        return False

    def get_feature(self, feature: str, version: str | None = None) -> object | None:
        """Return the legacy feature object for a probe, or ``None``.

        Legacy compatibility alias for WHATWG DOM ``getFeature`` and
        Aspose.HTML .NET ``Node.GetFeature(string, string)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_feature("core") is None
        True
        >>> doc.get_feature("XML", "3.0") is None
        True
        """
        _ = (feature, version)
        return None

    def set_user_data(
        self,
        key: str,
        data: object | None,
        handler: object | None = None,
    ) -> object | None:
        """Store or clear node-local user data and return the previous value.

        Legacy compatibility alias for WHATWG DOM ``setUserData`` and
        Aspose.HTML .NET ``Node.SetUserData(string, object, object)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.set_user_data("k", 1) is None
        True
        >>> doc.get_user_data("k")
        1
        >>> doc.set_user_data("k", None)
        1
        >>> doc.get_user_data("k") is None
        True
        """
        _ = handler
        previous = self._user_data_map.get(key)
        if data is None:
            self._user_data_map.pop(key, None)
        else:
            self._user_data_map[key] = data
        return previous

    def get_user_data(self, key: str) -> object | None:
        """Return node-local user data for *key* or ``None`` when absent.

        Legacy compatibility alias for WHATWG DOM ``getUserData`` and
        Aspose.HTML .NET ``Node.GetUserData(string)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_user_data("missing") is None
        True
        >>> _ = doc.set_user_data("answer", 42)
        >>> doc.get_user_data("answer")
        42
        """
        return self._user_data_map.get(key)

    def _namespace_lookup_context_element(self) -> "Node | None":
        if self._node_type == NodeType.ELEMENT_NODE:
            return self
        if self._node_type == NodeType.DOCUMENT_NODE:
            for child in self._children:
                if child._node_type == NodeType.ELEMENT_NODE:
                    return child
            return None
        return self.parent_element

    # ------------------------------------------------------------------
    # Tree mutation
    # ------------------------------------------------------------------

    def _validate_insertion(
        self, node: Node, replacing: Node | None = None
    ) -> None:
        """Validate that *node* can be inserted as a child of ``self``.

        Raises a ``DOMException`` subclass on any violation.
        """
        if node is self:
            raise HierarchyRequestError(
                "A node cannot be inserted into itself."
            )
        # Check that node is not an ancestor of self.
        ancestor = self._parent
        while ancestor is not None:
            if ancestor is node:
                raise HierarchyRequestError(
                    "The new node is an ancestor of the context node."
                )
            ancestor = ancestor._parent
        # Wrong-document check.
        if (
            node._owner_document is not None
            and self._owner_document is not None
            and node._owner_document is not self._owner_document
        ):
            raise WrongDocumentError(
                "The node belongs to a different document."
            )
        # Attr nodes may not be inserted as children.
        if node._node_type == NodeType.ATTRIBUTE_NODE:
            raise HierarchyRequestError(
                "Attr nodes cannot be inserted as child nodes."
            )

    def append_child(self, node: Node) -> Node:
        """Append *node* as the last child of this node.

        If *node* is a ``DocumentFragment``, all its children are appended
        in order and the fragment becomes empty.

        Returns the appended node (or last adopted child for a fragment).

        Raises ``HierarchyRequestError`` if the operation would violate
        DOM hierarchy rules.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el) is el
        True
        >>> el.parent_node is doc
        True
        """
        self._validate_insertion(node)

        if node._parent is not None:
            node._parent.remove_child(node)

        doc = self._owner_document

        if node._node_type == NodeType.DOCUMENT_FRAGMENT_NODE:
            children = list(node._children)
            node._children.clear()
            for child in children:
                self._children.append(child)
                child._parent = self
                if doc is not None:
                    _register_ids(doc, child)
            if children:
                self._notify_child_list(
                    added=tuple(children),
                    removed=(),
                    previous_sibling=self._children[-len(children) - 1] if len(self._children) > len(children) else None,
                    next_sibling=None,
                )
                if self.get_root_node()._node_type == NodeType.DOCUMENT_NODE:
                    for child in children:
                        _walk_and_dispatch_connected(child)
                self._invalidate_style_cache()  # AC-16
            return children[-1] if children else node

        prev = self._children[-1] if self._children else None
        self._children.append(node)
        node._parent = self
        if doc is not None:
            _register_ids(doc, node)
        self._notify_child_list(added=(node,), removed=(), previous_sibling=prev, next_sibling=None)
        if self.get_root_node()._node_type == NodeType.DOCUMENT_NODE:
            _walk_and_dispatch_connected(node)
        self._invalidate_style_cache()  # AC-16
        return node

    def insert_before(self, node: Node, reference: Node | None) -> Node:
        """Insert *node* before *reference* in the child list.

        If *reference* is ``None``, *node* is appended (equivalent to
        ``append_child``).

        Raises ``HierarchyRequestError`` on hierarchy violations.
        Raises ``NotFoundError`` if *reference* is not a child.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> a = doc.create_element("a")
        >>> b = doc.create_element("b")
        >>> doc.append_child(parent)
        <Element 'DIV'>
        >>> parent.append_child(a)
        <Element 'A'>
        >>> parent.insert_before(b, a) is b
        True
        >>> parent.first_child is b
        True
        """
        if reference is None:
            return self.append_child(node)

        if reference not in self._children:
            raise NotFoundError("reference is not a child of this node.")

        self._validate_insertion(node)

        if node._parent is not None:
            node._parent.remove_child(node)

        doc = self._owner_document
        idx = self._children.index(reference)
        prev = self._children[idx - 1] if idx > 0 else None
        nxt = self._children[idx]

        if node._node_type == NodeType.DOCUMENT_FRAGMENT_NODE:
            children = list(node._children)
            node._children.clear()
            for i, child in enumerate(children):
                self._children.insert(idx + i, child)
                child._parent = self
                if doc is not None:
                    _register_ids(doc, child)
            if children:
                self._notify_child_list(added=tuple(children), removed=(), previous_sibling=prev, next_sibling=nxt)
                if self.get_root_node()._node_type == NodeType.DOCUMENT_NODE:
                    for child in children:
                        _walk_and_dispatch_connected(child)
                self._invalidate_style_cache()  # AC-16
            return children[-1] if children else node

        self._children.insert(idx, node)
        node._parent = self
        if doc is not None:
            _register_ids(doc, node)
        self._notify_child_list(added=(node,), removed=(), previous_sibling=prev, next_sibling=nxt)
        if self.get_root_node()._node_type == NodeType.DOCUMENT_NODE:
            _walk_and_dispatch_connected(node)
        self._invalidate_style_cache()  # AC-16
        return node

    def remove_child(self, node: Node) -> Node:
        """Remove *node* from the child list and return it.

        Raises ``NotFoundError`` if *node* is not a child.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> doc.append_child(el)
        <Element 'P'>
        >>> doc.remove_child(el) is el
        True
        >>> el.parent_node is None
        True
        """
        if node not in self._children:
            raise NotFoundError("node is not a child of this node.")

        idx = self._children.index(node)
        prev = self._children[idx - 1] if idx > 0 else None
        nxt = self._children[idx + 1] if idx + 1 < len(self._children) else None

        doc = self._owner_document
        if self.get_root_node()._node_type == NodeType.DOCUMENT_NODE:
            _walk_and_dispatch_disconnected(node)
        if doc is not None:
            _unregister_ids(doc, node)

        self._children.remove(node)
        node._parent = None
        self._notify_child_list(added=(), removed=(node,), previous_sibling=prev, next_sibling=nxt)
        self._invalidate_style_cache()  # AC-16
        return node

    def replace_child(self, new_child: Node, old_child: Node) -> Node:
        """Replace *old_child* with *new_child*.

        Returns the removed *old_child*.

        Raises ``HierarchyRequestError`` if *new_child* violates hierarchy rules.
        Raises ``NotFoundError`` if *old_child* is not a child.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> b = doc.create_element("b")
        >>> doc.append_child(a)
        <Element 'A'>
        >>> doc.replace_child(b, a) is a
        True
        >>> doc.first_child is b
        True
        """
        if old_child not in self._children:
            raise NotFoundError("old_child is not a child of this node.")

        self._validate_insertion(new_child, replacing=old_child)

        if new_child._parent is not None and new_child is not old_child:
            new_child._parent.remove_child(new_child)

        idx = self._children.index(old_child)
        prev = self._children[idx - 1] if idx > 0 else None
        nxt = self._children[idx + 1] if idx + 1 < len(self._children) else None

        self._notify_child_list(added=(), removed=(old_child,), previous_sibling=prev, next_sibling=nxt)

        doc = self._owner_document
        if doc is not None:
            _unregister_ids(doc, old_child)

        self._children[idx] = new_child
        new_child._parent = self
        old_child._parent = None

        if doc is not None:
            _register_ids(doc, new_child)

        self._notify_child_list(added=(new_child,), removed=(), previous_sibling=prev, next_sibling=nxt)
        self._invalidate_style_cache()  # AC-16

        return old_child

    def _notify_child_list(
        self,
        *,
        added: tuple[Node, ...],
        removed: tuple[Node, ...],
        previous_sibling: Node | None,
        next_sibling: Node | None,
    ) -> None:
        doc = self._owner_document or (self if self._node_type == 9 else None)
        if doc is None:
            return
        signal = getattr(doc, "_mutation_signal", None)
        if signal is None:
            return
        signal.notify_child_list(self, added, removed, previous_sibling, next_sibling)

    def _invalidate_style_cache(self) -> None:
        """Bump the owning document's layout style epoch (M7.1 — SPEC-168/ADR-315).

        Tree mutations may add/remove elements that match existing selectors,
        so a structural change invalidates cached styles. Resolves the owning
        ``Document`` the same way :meth:`_notify_child_list` does (this node's
        ``owner_document``, or this node itself when it is the Document). A
        silent no-op when no document is reachable — orphan subtrees never
        bump (AC-16).
        """
        doc = self._owner_document or (self if self._node_type == 9 else None)
        bump = getattr(doc, "_bump_style_epoch", None)
        if bump is not None:
            bump()

    def clone_node(self, deep: bool = False) -> Node:
        """Return a copy of this node.

        Parameters
        ----------
        deep:
            If ``True``, clone the entire subtree. If ``False``, clone
            only this node (and its attributes for Element).

        Returns a new node with no parent. The clone has the same
        ``owner_document`` as the original.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> clone = el.clone_node()
        >>> clone.parent_node is None
        True
        >>> clone is not el
        True
        """
        clone = self._clone_self()
        if deep:
            for child in self._children:
                child_clone = child.clone_node(deep=True)
                clone._children.append(child_clone)
                child_clone._parent = clone
        return clone

    def _clone_self(self) -> Node:
        """Create a shallow copy of this node (no children).

        Subclasses must override.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement _clone_self()"
        )

    def normalize(self) -> None:
        """Put this node and its entire subtree into normalized form.

        Per WHATWG DOM §4.4.6: a normalized subtree contains no empty
        ``Text`` nodes and no two adjacent ``Text`` node siblings.

        Adjacent ``Text`` nodes are merged left-to-right into the first
        sibling (their ``data`` is concatenated). Empty ``Text`` nodes
        (``data == ""``) are then removed. Normalization recurses into all
        non-``Text`` children so that the full descendant tree is
        normalized.

        The method mutates the tree in-place and returns ``None``.
        The operation is idempotent: calling ``normalize()`` twice
        produces the same result as calling it once.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> doc.append_child(parent)
        <Element 'DIV'>
        >>> t1 = doc.create_text_node("hello ")
        >>> t2 = doc.create_text_node("world")
        >>> parent.append_child(t1)
        <Text data='hello '>
        >>> parent.append_child(t2)
        <Text data='world'>
        >>> len(parent.child_nodes)
        2
        >>> parent.normalize()
        >>> len(parent.child_nodes)
        1
        >>> parent.first_child.data
        'hello world'
        """
        # See ADR-019: snapshot iteration avoids index invalidation during removal.
        # INV-005: algorithm follows WHATWG DOM §4.4.6 exactly.
        snapshot = list(self._children)
        i = 0
        while i < len(snapshot):
            child = snapshot[i]
            if child._node_type == NodeType.TEXT_NODE:
                # Collect the run of consecutive Text siblings starting at i.
                j = i + 1
                while (
                    j < len(snapshot)
                    and snapshot[j]._node_type == NodeType.TEXT_NODE
                ):
                    j += 1
                run = snapshot[i:j]
                if len(run) > 1:
                    # Merge: concatenate all data into the first node.
                    merged = "".join(n.data for n in run)  # INV-003: public property
                    run[0].data = merged
                    # Remove subsequent nodes via remove_child to preserve
                    # id-map invariants (ADR-019 §Design point 4).
                    for extra in run[1:]:
                        self.remove_child(extra)
                surviving = run[0]
                if surviving.data == "":
                    self.remove_child(surviving)
                # Advance past the entire run regardless of whether it survived.
                i = j
            else:
                # Recurse into non-Text children (Text nodes are leaf nodes).
                child.normalize()
                i += 1

    def contains(self, other: Node | None) -> bool:
        """Return ``True`` if *other* is an inclusive descendant of this node.

        Per WHATWG DOM §4.4: returns ``True`` if *other* is ``self`` or is a
        descendant of ``self``; otherwise ``False``.

        Parameters
        ----------
        other:
            The node to test. ``None`` always returns ``False``.

        Returns
        -------
        bool
            ``True`` iff *other* is ``self`` or reachable from ``self``
            by following child links downward.

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
        >>> parent.contains(child)
        True
        >>> parent.contains(parent)
        True
        >>> parent.contains(None)
        False
        >>> child.contains(parent)
        False
        """
        # INV-005: WHATWG DOM §4.4 inclusive-descendant walk via ancestor chain.
        # Walking upward from other is O(depth) and avoids DFS over all children.
        if other is None:
            return False
        current: Node | None = other
        while current is not None:
            if current is self:
                return True
            current = current._parent
        return False

    # ------------------------------------------------------------------
    # Document position
    # ------------------------------------------------------------------

    def compare_document_position(self, other: "Node") -> int:
        """Return a bitmask describing the position of *other* relative to this node.

        The return value is a combination of zero or more ``DocumentPosition``
        constants.  A return of ``0`` means *other* is the same node.

        Conforms to WHATWG DOM §4.4.3.

        Parameters
        ----------
        other : Node
            The node to compare against.

        Returns
        -------
        int
            A bitmask of ``DocumentPosition`` constants.

        Examples
        --------
        >>> from aspose_html.dom import Document, DocumentPosition
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> child = doc.create_element("span")
        >>> doc.append_child(parent)
        <Element 'DIV'>
        >>> parent.append_child(child)
        <Element 'SPAN'>
        >>> result = child.compare_document_position(parent)
        >>> bool(result & DocumentPosition.DOCUMENT_POSITION_CONTAINS)
        True
        >>> result2 = parent.compare_document_position(child)
        >>> bool(result2 & DocumentPosition.DOCUMENT_POSITION_CONTAINED_BY)
        True
        """
        # INV-005: WHATWG DOM §4.4.3 algorithm. See ADR-036.
        # Step 1 — Same node check.
        if self is other:
            return 0

        DISCONNECTED = DocumentPosition.DOCUMENT_POSITION_DISCONNECTED      # 1
        PRECEDING    = DocumentPosition.DOCUMENT_POSITION_PRECEDING          # 2
        FOLLOWING    = DocumentPosition.DOCUMENT_POSITION_FOLLOWING          # 4
        CONTAINS     = DocumentPosition.DOCUMENT_POSITION_CONTAINS           # 8
        CONTAINED_BY = DocumentPosition.DOCUMENT_POSITION_CONTAINED_BY      # 16
        IMPL_SPECIFIC = DocumentPosition.DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC  # 32

        # Step 2 — Build ancestor chains (node itself is index 0; root is last).
        def _ancestors(node: "Node") -> list["Node"]:
            chain: list[Node] = []
            current: Node | None = node
            while current is not None:
                chain.append(current)
                current = current._parent
            return chain

        self_chain = _ancestors(self)
        other_chain = _ancestors(other)

        # Step 3 — Find tree roots and detect disconnection.
        self_root = self_chain[-1]
        other_root = other_chain[-1]

        if self_root is not other_root:
            # WHATWG §4.4.3: disconnected case — implementation-specific ordering.
            # Use id() as stable tiebreaker so the same pair always returns the
            # same result within a process lifetime. See ADR-036.
            if id(self) < id(other):
                return DISCONNECTED | IMPL_SPECIFIC | PRECEDING
            else:
                return DISCONNECTED | IMPL_SPECIFIC | FOLLOWING

        # Step 4 — Detect ancestor/descendant relationships.
        # other in self_chain → other is an ancestor of self.
        other_in_self_chain = other in self_chain
        self_in_other_chain = self in other_chain

        if other_in_self_chain:
            # other is an ancestor of self → other CONTAINS self.
            # Ancestor precedes descendant in document order.
            return CONTAINS | PRECEDING

        if self_in_other_chain:
            # self is an ancestor of other → other is CONTAINED_BY self.
            # Descendant follows ancestor in document order.
            return CONTAINED_BY | FOLLOWING

        # Step 5 — Neither is ancestor of the other. Find lowest common ancestor.
        self_ancestors = set(self_chain)

        lca: Node | None = None
        for node in other_chain:
            if node in self_ancestors:
                lca = node
                break

        # lca always exists: both chains share the same root (confirmed in step 3).
        assert lca is not None

        # Find the direct children of lca on the paths to self and other.
        self_branch_index = self_chain.index(lca) - 1
        other_branch_index = other_chain.index(lca) - 1

        self_branch = self_chain[self_branch_index]
        other_branch = other_chain[other_branch_index]

        # Compare positions of the two branches within lca's child list.
        lca_children = lca._children
        self_pos = lca_children.index(self_branch)
        other_pos = lca_children.index(other_branch)

        if other_pos < self_pos:
            # other_branch appears before self_branch → other PRECEDES self.
            return PRECEDING
        else:
            # other_branch appears after self_branch → other FOLLOWS self.
            return FOLLOWING

    def is_equal_node(self, other: Node | None) -> bool:
        """Return ``True`` if *other* has the same structure as this node.

        Per WHATWG DOM §4.4: two nodes are equal if they have the same type,
        the same type-specific properties, the same number of children, and
        each pair of corresponding children are equal.

        Parameters
        ----------
        other:
            The node to compare. ``None`` always returns ``False``.

        Returns
        -------
        bool
            ``True`` iff *other* is structurally identical to this node
            (recursively).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("p")
        >>> b = doc.create_element("p")
        >>> a.is_equal_node(b)
        True
        >>> a.set_attribute("id", "x")
        >>> a.is_equal_node(b)
        False
        >>> a.is_equal_node(None)
        False
        """
        # INV-005: WHATWG DOM §4.4 equality algorithm.
        if other is None:
            return False
        # Exact type check (not isinstance) — CDATASection extends Text but
        # they have different nodeType values and must not compare as equal.
        if type(self) is not type(other):
            return False

        # Per-type property comparison.  All reads; no mutations.
        if not self._is_equal_properties(other):
            return False

        # Children count check before recursion.
        if len(self._children) != len(other._children):
            return False

        # Recursive children comparison — short-circuits on first mismatch.
        for self_child, other_child in zip(self._children, other._children):
            if not self_child.is_equal_node(other_child):
                return False

        return True

    def is_same_node(self, other_node: Node | None) -> bool:
        """Return ``True`` when *other_node* is this node instance.

        Legacy identity alias for WHATWG DOM ``isSameNode`` and Aspose.HTML
        .NET ``Node.IsSameNode(Node)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("p")
        >>> b = doc.create_element("p")
        >>> a.is_same_node(a)
        True
        >>> a.is_same_node(b)
        False
        >>> a.is_same_node(None)
        False
        """
        return self is other_node

    def _is_equal_properties(self, other: Node) -> bool:
        """Compare per-type properties of this node against *other*.

        Called only when ``type(self) is type(other)``.  Returns ``False``
        as soon as any type-specific property differs.  Uses duck typing
        (``hasattr``) to avoid importing concrete subclass types here, which
        would create circular imports.

        This is an internal helper — not part of the public API.
        """
        # DocumentType: name, public_id, system_id.
        if hasattr(self, "_public_id"):
            return (
                self._name == other._name  # type: ignore[attr-defined]
                and self._public_id == other._public_id  # type: ignore[attr-defined]
                and self._system_id == other._system_id  # type: ignore[attr-defined]
            )

        # ProcessingInstruction: target + data.  Must be checked before the
        # plain CharacterData branch because PI also has _data but additionally
        # has _target, making it a distinct type.
        if hasattr(self, "_target"):
            return (
                self._target == other._target  # type: ignore[attr-defined]
                and self._data == other._data  # type: ignore[attr-defined]
            )

        # CharacterData (Text, Comment, CDATASection): data only.
        if hasattr(self, "_data"):
            return self._data == other._data  # type: ignore[attr-defined]

        # Attr: namespace_uri, local_name, and value (WHATWG DOM §4.4).
        if hasattr(self, "_owner_element"):
            return (
                self._name == other._name  # type: ignore[attr-defined]
                and self._value == other._value  # type: ignore[attr-defined]
                and self._namespace_uri == other._namespace_uri  # type: ignore[attr-defined]
                and self._local_name_ns == other._local_name_ns  # type: ignore[attr-defined]
            )

        # Element: namespace_uri, local_name, and attributes (order-independent).
        # INV-005: WHATWG §4.4 does not require attribute order equality.
        if hasattr(self, "_attributes"):
            if (
                self._local_name != other._local_name  # type: ignore[attr-defined]
                or self._namespace_uri != other._namespace_uri  # type: ignore[attr-defined]
            ):
                return False
            self_attrs = self._attributes  # type: ignore[attr-defined]
            other_attrs = other._attributes  # type: ignore[attr-defined]
            if len(self_attrs) != len(other_attrs):
                return False
            for attr in self_attrs:
                match = other_attrs.get_named_item(attr.name)
                if match is None or match.value != attr.value:
                    return False
            return True

        # Document, DocumentFragment: no extra properties to compare.
        return True

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"
