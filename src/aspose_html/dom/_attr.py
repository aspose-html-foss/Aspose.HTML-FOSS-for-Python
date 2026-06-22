"""Attr — DOM attribute node."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.dom._node import Node
from aspose_html.dom._node_type import NodeType

if TYPE_CHECKING:
    from aspose_html.dom._element import Element
    from aspose_html.dom._document import Document


class Attr(Node):
    """An attribute attached to an Element.

    ``Attr`` nodes are stored in ``Element._attributes`` (``NamedNodeMap``),
    **not** in ``Element._children``.  Inserting an ``Attr`` as a child node
    raises ``HierarchyRequestError``.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> el.set_attribute("id", "main")
    >>> attr = el.attributes["id"]
    >>> attr.name
    'id'
    >>> attr.value
    'main'
    """

    __slots__ = ("_name", "_value", "_owner_element", "_namespace_uri", "_local_name_ns")

    def __init__(
        self,
        name: str,
        value: str = "",
        owner_element: Element | None = None,
        owner_document: Document | None = None,
        namespace_uri: str | None = None,
        local_name_ns: str | None = None,
    ) -> None:
        super().__init__(NodeType.ATTRIBUTE_NODE, owner_document)
        self._name: str = name
        self._value: str = value
        self._owner_element: Element | None = owner_element
        self._namespace_uri: str | None = namespace_uri
        self._local_name_ns: str | None = local_name_ns

    @property
    def node_name(self) -> str:
        """The attribute name.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("span")
        >>> el.set_attribute("class", "box")
        >>> el.attributes["class"].node_name
        'class'
        """
        return self._name

    @property
    def node_value(self) -> str:  # type: ignore[override]
        """The attribute value string.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("span")
        >>> el.set_attribute("class", "box")
        >>> el.attributes["class"].node_value
        'box'
        """
        return self._value

    @node_value.setter
    def node_value(self, value: str | None) -> None:
        if value is not None:
            self._value = value

    @property
    def name(self) -> str:
        """The attribute name.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> el.set_attribute("data-x", "1")
        >>> el.attributes["data-x"].name
        'data-x'
        """
        return self._name

    @property
    def value(self) -> str:
        """The attribute value.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> el.set_attribute("data-x", "1")
        >>> el.attributes["data-x"].value
        '1'
        """
        return self._value

    @value.setter
    def value(self, val: str) -> None:
        """Set the attribute value.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> el.set_attribute("x", "a")
        >>> el.attributes["x"].value = "b"
        >>> el.get_attribute("x")
        'b'
        """
        self._value = val

    @property
    def owner_element(self) -> Element | None:
        """The Element this Attr is attached to, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("id", "x")
        >>> el.attributes["id"].owner_element is el
        True
        """
        return self._owner_element

    @property
    def namespace_uri(self) -> str | None:
        """The namespace URI of this attribute, or ``None`` for no namespace.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("svg")
        >>> el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#id")
        >>> attr = el.get_attribute_node("xlink:href")
        >>> attr.namespace_uri
        'http://www.w3.org/1999/xlink'
        """
        return self._namespace_uri

    @property
    def prefix(self) -> str | None:
        """The namespace prefix of this attribute, or ``None`` if no prefix.

        WHATWG DOM §4.6: the prefix is the part of the qualified name
        before the first colon, or ``None`` when the attribute has no
        namespace prefix.

        Examples
        --------
        >>> from aspose_html.dom._attr import Attr
        >>> a = Attr("xlink:href", "#foo",
        ...          namespace_uri="http://www.w3.org/1999/xlink",
        ...          local_name_ns="href")
        >>> a.prefix
        'xlink'
        >>> b = Attr("id", "main")
        >>> b.prefix is None
        True
        """
        if self._local_name_ns is not None and ":" in self._name:
            return self._name.split(":", 1)[0]
        return None

    @property
    def specified(self) -> bool:
        """Always ``True`` — DOM3 legacy attribute.

        WHATWG DOM §4.6 note: this attribute was introduced in DOM Level 2
        Core.  Its value is always true for attributes in the attribute list.

        Examples
        --------
        >>> from aspose_html.dom._attr import Attr
        >>> Attr("id", "main").specified
        True
        >>> Attr("xlink:href", "#foo",
        ...      namespace_uri="http://www.w3.org/1999/xlink",
        ...      local_name_ns="href").specified
        True
        """
        return True

    @property
    def local_name(self) -> str:
        """The local part of the attribute name.

        For non-namespaced attributes returns the full attribute name.
        For namespaced attributes (created via ``set_attribute_ns``) returns
        the local name portion of the qualified name (e.g. ``"href"`` for
        ``"xlink:href"``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("id", "x")
        >>> el.get_attribute_node("id").local_name
        'id'
        >>> el.set_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href", "#")
        >>> el.get_attribute_node("xlink:href").local_name
        'href'
        """
        return self._local_name_ns if self._local_name_ns is not None else self._name

    def _clone_self(self) -> Attr:
        return Attr(
            self._name,
            self._value,
            owner_element=None,
            owner_document=self._owner_document,
            namespace_uri=self._namespace_uri,
            local_name_ns=self._local_name_ns,
        )

    def __repr__(self) -> str:
        return f"<Attr {self._name!r}={self._value!r}>"

    __str__ = __repr__
