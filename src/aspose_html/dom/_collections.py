"""NodeList, HTMLCollection, and NamedNodeMap — WHATWG DOM collections."""
from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from aspose_html.dom._node import Node

from aspose_html.dom._node_type import NodeType
from aspose_html.dom._exceptions import NotFoundError


class NodeList:
    """A live, ordered collection of Node objects.

    Wraps a reference to the underlying ``_children`` list of a node.
    All mutations to the source list are immediately visible through this
    collection.  Do not mutate via this object.

    Supports ``len()``, iteration, and integer index access.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("p")
    >>> doc.append_child(el)
    <Element 'P'>
    >>> nl = doc.child_nodes
    >>> len(nl)
    1
    >>> nl[0] is el
    True
    """

    __slots__ = ("_live_list",)

    def __init__(self, live_list: list[Node]) -> None:
        self._live_list = live_list

    def __len__(self) -> int:
        return len(self._live_list)

    def __iter__(self) -> Iterator[Node]:
        return iter(list(self._live_list))

    def __getitem__(self, index: int) -> Node:
        return self._live_list[index]

    def item(self, index: int) -> Node | None:
        """Return node at *index*, or ``None`` if out of range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.child_nodes.item(0) is None
        True
        """
        try:
            return self._live_list[index]
        except IndexError:
            return None

    def __repr__(self) -> str:
        return f"NodeList({list(self._live_list)!r})"


class _StaticNodeList(NodeList):
    """A non-live NodeList wrapping a snapshot list.

    Returned by ``query_selector_all`` — does not reflect subsequent
    tree mutations.
    """

    __slots__ = ()

    def __iter__(self) -> Iterator[Node]:
        return iter(self._live_list)


class HTMLCollection:
    """A live, ordered collection of Element-type children only.

    Wraps a reference to an element's ``_children`` list and filters by
    ``node_type == NodeType.ELEMENT_NODE`` dynamically on each access.

    Supports ``len()``, iteration, and integer index access.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> doc.append_child(el)
    <Element 'DIV'>
    >>> coll = doc.document_element.children
    >>> len(coll)
    0
    """

    __slots__ = ("_live_list",)

    def __init__(self, live_list: list[Node]) -> None:
        self._live_list = live_list

    def _elements(self) -> list[Node]:
        return [n for n in self._live_list if n._node_type == NodeType.ELEMENT_NODE]

    def __len__(self) -> int:
        return len(self._elements())

    def __iter__(self) -> Iterator[Node]:
        return iter(self._elements())

    def __getitem__(self, index: int) -> Node:
        return self._elements()[index]

    def item(self, index: int) -> Node | None:
        """Return element at *index*, or ``None`` if out of range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("span")
        <Element 'SPAN'>
        >>> doc.document_element  # None — document has no element child yet
        """
        items = self._elements()
        try:
            return items[index]
        except IndexError:
            return None

    def named_item(self, name: str) -> Node | None:
        """Return the first Element with the given id or name attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("id", "main")
        >>> doc.append_child(el)
        <Element 'DIV' id='main'>
        >>> doc.child_nodes.item(0).get_attribute("id")
        'main'
        """
        for el in self._elements():
            if el.get_attribute("id") == name or el.get_attribute("name") == name:  # type: ignore[attr-defined]
                return el
        return None

    def __repr__(self) -> str:
        return f"HTMLCollection({self._elements()!r})"


class _SubtreeHTMLCollection:
    """Live collection built by walking a subtree with an optional filter.

    Used by ``get_elements_by_tag_name`` and ``get_elements_by_class_name``.
    Re-scans the subtree on every access, so it is always current.
    """

    __slots__ = ("_root", "_filter_fn")

    def __init__(self, root: Node, filter_fn) -> None:  # type: ignore[type-arg]
        self._root = root
        self._filter_fn = filter_fn

    def _items(self) -> list[Node]:
        return list(self._walk(self._root))

    def _walk(self, node: Node) -> Iterator[Node]:
        for child in node._children:
            if child._node_type == NodeType.ELEMENT_NODE:
                if self._filter_fn(child):
                    yield child
            yield from self._walk(child)

    def __len__(self) -> int:
        return len(self._items())

    def __iter__(self) -> Iterator[Node]:
        return iter(self._items())

    def __getitem__(self, index: int) -> Node:
        return self._items()[index]

    def item(self, index: int) -> Node | None:
        """Return element at *index*, or ``None`` if out of range."""
        items = self._items()
        try:
            return items[index]
        except IndexError:
            return None

    def named_item(self, name: str) -> Node | None:
        """Return the first Element with the given id or name attribute."""
        for el in self._items():
            if el.get_attribute("id") == name or el.get_attribute("name") == name:  # type: ignore[attr-defined]
                return el
        return None

    def __repr__(self) -> str:
        return f"_SubtreeHTMLCollection({self._items()!r})"


class HTMLOptionsCollection:
    """Live collection of ``<option>`` elements for a ``<select>``.

    The collection is live and re-walks the select subtree on every access,
    including options inside nested ``<optgroup>`` elements.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> sel = doc.create_element("select")
    >>> opt = doc.create_element("option")
    >>> _ = sel.append_child(opt)
    >>> sel.options.length
    1
    >>> sel.options[0] is opt
    True
    """

    __slots__ = ("_select",)

    def __init__(self, select_element: Node) -> None:
        self._select = select_element

    def _options(self) -> list[Node]:
        items: list[Node] = []

        def _walk(node: Node) -> None:
            for child in node._children:
                if child._node_type == NodeType.ELEMENT_NODE:
                    if child._local_name == "option":
                        items.append(child)
                    _walk(child)

        _walk(self._select)
        return items

    def __len__(self) -> int:
        return len(self._options())

    def __iter__(self) -> Iterator[Node]:
        return iter(self._options())

    def __getitem__(self, index: int) -> Node:
        return self._options()[index]

    @property
    def length(self) -> int:
        """Number of ``<option>`` elements in the collection.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> _ = sel.append_child(doc.create_element("option"))
        >>> sel.options.length
        1
        """
        return len(self)

    def item(self, index: int) -> Node | None:
        """Return option at *index*, or ``None`` if out of range.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt = doc.create_element("option")
        >>> _ = sel.append_child(opt)
        >>> sel.options.item(0) is opt
        True
        >>> sel.options.item(1) is None
        True
        """
        opts = self._options()
        try:
            return opts[index]
        except IndexError:
            return None

    def named_item(self, name: str) -> Node | None:
        """Return first option whose ``id`` or ``name`` equals *name*.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt = doc.create_element("option")
        >>> opt.set_attribute("id", "primary")
        >>> _ = sel.append_child(opt)
        >>> sel.options.named_item("primary") is opt
        True
        >>> sel.options.named_item("missing") is None
        True
        """
        for option in self._options():
            if option.get_attribute("id") == name or option.get_attribute("name") == name:  # type: ignore[attr-defined]
                return option
        return None

    def namedItem(self, name: str) -> Node | None:
        """Alias for :meth:`named_item` (Web IDL casing).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> opt = doc.create_element("option")
        >>> opt.set_attribute("name", "choice")
        >>> _ = sel.append_child(opt)
        >>> sel.options.namedItem("choice") is opt
        True
        """
        return self.named_item(name)

    def add(self, element: Node, before: Node | int | None = None) -> None:
        """Insert *element* into the select at a requested position.

        *before* may be ``None`` (append), an integer option index, or an
        existing option node reference.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> a = doc.create_element("option")
        >>> b = doc.create_element("option")
        >>> sel.options.add(a)
        >>> sel.options.add(b, 0)
        >>> sel.options[0] is b
        True
        """
        if before is None:
            self._select.append_child(element)
            return

        if isinstance(before, int):
            ref = self.item(before)
            if ref is None:
                self._select.append_child(element)
            else:
                ref_parent = ref.parent_node
                if ref_parent is None:
                    self._select.append_child(element)
                else:
                    ref_parent.insert_before(element, ref)
            return

        ref_parent = before.parent_node
        if ref_parent is None:
            self._select.append_child(element)
        else:
            ref_parent.insert_before(element, before)

    def remove(self, index: int) -> None:
        """Remove option at *index* if present.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> _ = sel.append_child(doc.create_element("option"))
        >>> sel.options.length
        1
        >>> sel.options.remove(0)
        >>> sel.options.length
        0
        """
        option = self.item(index)
        if option is None:
            return
        parent = option.parent_node
        if parent is not None:
            parent.remove_child(option)

    @property
    def selected_index(self) -> int:
        """0-based index of first selected option, or ``-1``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> a = doc.create_element("option")
        >>> b = doc.create_element("option")
        >>> b.set_attribute("selected", "")
        >>> _ = sel.append_child(a)
        >>> _ = sel.append_child(b)
        >>> sel.options.selected_index
        1
        """
        for idx, option in enumerate(self._options()):
            if option.has_attribute("selected"):
                return idx
        return -1

    @property
    def selectedIndex(self) -> int:
        """Alias for :attr:`selected_index` (Web IDL casing).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sel = doc.create_element("select")
        >>> sel.options.selectedIndex
        -1
        """
        return self.selected_index

    def __repr__(self) -> str:
        return f"HTMLOptionsCollection({self._options()!r})"


class NamedNodeMap:
    """An ordered map of Attr objects keyed by attribute name.

    Supports ``len()``, iteration (yields Attr objects), integer index
    access, and string key access.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> el.set_attribute("id", "main")
    >>> len(el.attributes)
    1
    >>> el.attributes["id"].value
    'main'
    """

    __slots__ = ("_data",)

    def __init__(self) -> None:
        self._data: OrderedDict[str, object] = OrderedDict()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[object]:
        return iter(self._data.values())

    def __getitem__(self, key: int | str) -> object:
        if isinstance(key, int):
            try:
                return list(self._data.values())[key]
            except IndexError:
                raise IndexError(f"NamedNodeMap index {key} out of range")
        return self._data[key]

    def __contains__(self, name: str) -> bool:  # type: ignore[override]
        return name in self._data

    def get_named_item(self, name: str) -> object | None:
        """Return the Attr with the given name, or ``None`` if absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "box")
        >>> el.attributes.get_named_item("class").value
        'box'
        >>> el.attributes.get_named_item("missing") is None
        True
        """
        return self._data.get(name)

    def set_named_item(self, attr: object) -> object | None:
        """Set *attr*, returning the displaced Attr (or ``None``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("id", "x")
        >>> el.attributes.get_named_item("id").value
        'x'
        """
        from aspose_html.dom._attr import Attr  # local import to avoid cycle
        assert isinstance(attr, Attr)
        old = self._data.get(attr.name)
        self._data[attr.name] = attr
        return old if old is not attr else None

    def remove_named_item(self, name: str) -> object:
        """Remove and return the Attr with *name*.

        Raises ``NotFoundError`` if the attribute is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-x", "1")
        >>> attr = el.attributes.remove_named_item("data-x")
        >>> attr.value
        '1'
        """
        if name not in self._data:
            raise NotFoundError(f"No attribute named {name!r}")
        return self._data.pop(name)

    def __repr__(self) -> str:
        items = ", ".join(f"{k}={v!r}" for k, v in self._data.items())  # type: ignore[union-attr]
        return f"NamedNodeMap({{{items}}})"
