"""Read-only DOM proxy objects for the QuickJS bridge.

All proxy callbacks are pure Python callables registered via
``quickjs.Context.add_callable``.  They are invoked from JavaScript
functions that are built inside the QuickJS runtime by
:meth:`_DocumentProxy.install_globals`.

Most proxy methods are read-only.  The sole write-through is
:meth:`_DocumentProxy.set_attribute`, which is called from JS
``el.setAttribute(name, value)`` and mutates the Python DOM.
All other write paths silently no-op or fall back to empty strings.

The module-level ``_ELEMENT_REGISTRY`` maps ``id(element)`` to the
live Python :class:`~aspose_html.dom.Element`.  It is populated each
time :meth:`_ElementProxy.to_js_data` is called and allows
``window.getComputedStyle`` to recover the Python element from the
integer ``__py_id__`` key embedded in the JS element object.

Note: DOM node classes use ``__slots__`` without ``__weakref__``, so
all proxy classes hold strong references to DOM objects.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aspose_html.dom._element import Element
    from aspose_html.dom._document import Document


# ---------------------------------------------------------------------------
# Module-level element registry
# ---------------------------------------------------------------------------

#: Maps ``id(element)`` → element for getComputedStyle round-trips.
#: Strong references — elements stay alive as long as the document tree
#: holds them, which covers the entire ``JSContext`` lifetime.
_ELEMENT_REGISTRY: dict[int, "Element"] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _element_to_json(element: "Element") -> str:
    """Serialise *element* to a JSON string suitable for ``JSON.parse`` in JS.

    Registers the element in :data:`_ELEMENT_REGISTRY` so that
    ``getComputedStyle`` can recover it via ``__py_id__``.

    Parameters
    ----------
    element : Element
        A live DOM element.

    Returns
    -------
    str
        JSON-encoded dict with keys: ``tagName``, ``id``, ``className``,
        ``textContent``, ``__py_id__``.
    """
    py_id = id(element)
    _ELEMENT_REGISTRY[py_id] = element
    return json.dumps(
        {
            "tagName": element._tag_name,
            "id": element.get_attribute("id") or "",
            "className": element.get_attribute("class") or "",
            "textContent": (element.text_content or ""),
            "__py_id__": py_id,
        }
    )


# ---------------------------------------------------------------------------
# _ElementProxy
# ---------------------------------------------------------------------------

class _ElementProxy:
    """Read-only JS proxy for a DOM :class:`~aspose_html.dom.Element`.

    Wraps a single element.  Use :meth:`to_js_data` to obtain a JSON
    string ready for ``JSON.parse`` on the JS side.

    Parameters
    ----------
    element : Element
        The DOM element to proxy.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> el.set_attribute("id", "box")
    >>> proxy = _ElementProxy(el)
    >>> import json
    >>> data = json.loads(proxy.to_js_data())
    >>> data["tagName"]
    'DIV'
    >>> data["id"]
    'box'
    """

    __slots__ = ("_el",)

    def __init__(self, element: "Element") -> None:
        # Strong reference — DOM uses __slots__ without __weakref__
        self._el: "Element" = element

    def to_js_data(self) -> str:
        """Return a JSON string representation of the element for the JS side.

        Returns
        -------
        str
            JSON object with ``tagName``, ``id``, ``className``,
            ``textContent``, and ``__py_id__``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("span")
        >>> proxy = _ElementProxy(el)
        >>> import json
        >>> json.loads(proxy.to_js_data())["tagName"]
        'SPAN'
        """
        return _element_to_json(self._el)


# ---------------------------------------------------------------------------
# _ComputedStyleProxy
# ---------------------------------------------------------------------------

class _ComputedStyleProxy:
    """Read-only JS proxy for a computed style declaration.

    Wraps the result of :meth:`~aspose_html.dom.Element.get_computed_style`
    and exposes ``getPropertyValue`` for the JS side.

    Parameters
    ----------
    computed : ComputedStyleDeclaration
        The resolved style object from the cascade resolver.

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> doc.append_child(el)
    <Element 'DIV'>
    >>> sheet = CSSStyleSheet()
    >>> sheet.replace_sync("div { color: green }")
    >>> doc.attach_style_sheet(sheet)
    >>> computed = el.get_computed_style()
    >>> proxy = _ComputedStyleProxy(computed)
    >>> proxy.get_property_value("color")
    'green'
    """

    __slots__ = ("_computed",)

    def __init__(self, computed: Any) -> None:
        self._computed = computed

    def get_property_value(self, name: str) -> str:
        """Return the computed value for CSS property *name*.

        Parameters
        ----------
        name : str
            A CSS property name, e.g. ``"color"``.

        Returns
        -------
        str
            The resolved value, or ``""`` if not set.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> doc.append_child(el)
        <Element 'P'>
        >>> sheet = CSSStyleSheet()
        >>> sheet.replace_sync("p { font-size: 14px }")
        >>> doc.attach_style_sheet(sheet)
        >>> proxy = _ComputedStyleProxy(el.get_computed_style())
        >>> proxy.get_property_value("font-size")
        '14px'
        """
        return self._computed.get_property_value(str(name))


# ---------------------------------------------------------------------------
# _DocumentProxy
# ---------------------------------------------------------------------------

class _DocumentProxy:
    """JS proxy for a :class:`~aspose_html.dom.Document`.

    Exposes ``querySelector``, ``querySelectorAll``, ``getElementById``,
    ``getElementsByTagName``, ``getComputedStyle``, and ``set_attribute``
    as Python callables that can be registered with
    ``quickjs.Context.add_callable``.  All methods except
    :meth:`set_attribute` are read-only; ``set_attribute`` routes JS
    ``el.setAttribute(name, value)`` calls into the Python DOM.

    Parameters
    ----------
    document : Document
        The live document to proxy.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> doc.append_child(el)
    <Element 'DIV'>
    >>> proxy = _DocumentProxy(doc)
    >>> import json
    >>> result = proxy.query_selector("div")
    >>> json.loads(result)["tagName"]
    'DIV'
    """

    __slots__ = ("_document",)

    def __init__(self, document: "Document") -> None:
        # Strong reference — DOM uses __slots__ without __weakref__
        self._document: "Document" = document

    def query_selector(self, sel: Any) -> "str | None":
        """Return JSON element data for the first element matching *sel*, or ``None``.

        Parameters
        ----------
        sel : str
            A CSS selector string.

        Returns
        -------
        str or None
            JSON-encoded element dict, or ``None`` if no match.
        """
        from aspose_html.css import select  # noqa: PLC0415
        results = select(self._document, str(sel), first_only=True)
        if not results:
            return None
        return _element_to_json(results[0])

    def query_selector_all(self, sel: Any) -> str:
        """Return JSON array of element data for all elements matching *sel*.

        Parameters
        ----------
        sel : str
            A CSS selector string.

        Returns
        -------
        str
            JSON-encoded array of element dicts.
        """
        from aspose_html.css import select  # noqa: PLC0415
        results = select(self._document, str(sel))
        return json.dumps([json.loads(_element_to_json(el)) for el in results])

    def get_element_by_id(self, id_val: Any) -> "str | None":
        """Return JSON element data for the element with *id_val*, or ``None``.

        Parameters
        ----------
        id_val : str
            The element's id attribute value.

        Returns
        -------
        str or None
            JSON-encoded element dict, or ``None`` if not found.
        """
        from aspose_html.css import select  # noqa: PLC0415
        id_str = str(id_val) if id_val is not None else ""
        if not id_str:
            return None
        results = select(self._document, f"#{id_str}", first_only=True)
        if not results:
            return None
        return _element_to_json(results[0])

    def get_elements_by_tag_name(self, tag: Any) -> str:
        """Return JSON array of element data for all elements with *tag*.

        Parameters
        ----------
        tag : str
            A tag name (case-insensitive).

        Returns
        -------
        str
            JSON-encoded array of element dicts.
        """
        tag_str = str(tag).lower() if tag is not None else ""
        results: list[Element] = []
        _collect_by_tag(self._document, tag_str, results)
        return json.dumps([json.loads(_element_to_json(el)) for el in results])

    def get_attribute(self, py_id: Any, name: Any) -> "str | None":
        """Return attribute *name* for the element identified by *py_id*.

        Parameters
        ----------
        py_id : int
            The ``__py_id__`` of the element as registered in
            :data:`_ELEMENT_REGISTRY`.
        name : str
            Attribute name.

        Returns
        -------
        str or None
            The attribute value, or ``None`` if not found.
        """
        if py_id is None:
            return None
        el = _ELEMENT_REGISTRY.get(int(py_id))
        if el is None:
            return None
        return el.get_attribute(str(name))

    def has_attribute(self, py_id: Any, name: Any) -> bool:
        """Return whether element *py_id* has attribute *name*.

        Parameters
        ----------
        py_id : int
            The ``__py_id__`` registered in :data:`_ELEMENT_REGISTRY`.
        name : str
            Attribute name.

        Returns
        -------
        bool
        """
        if py_id is None:
            return False
        el = _ELEMENT_REGISTRY.get(int(py_id))
        if el is None:
            return False
        return el.has_attribute(str(name))

    def get_computed_style(self, py_id: Any, _pseudo: Any = None) -> str:
        """Return JSON computed style data for the element identified by *py_id*.

        Parameters
        ----------
        py_id : int
            The ``__py_id__`` from the JS element object.
        _pseudo : str or None
            Pseudo-element (ignored — not supported in current cascade).

        Returns
        -------
        str
            JSON-encoded dict mapping property names to values.
        """
        if py_id is None:
            return json.dumps({})
        el = _ELEMENT_REGISTRY.get(int(py_id))
        if el is None:
            return json.dumps({})
        computed = el.get_computed_style()
        # Export all known properties the cascade resolves
        _KNOWN_PROPS = (
            "color", "font-family", "font-size", "font-style",
            "font-weight", "line-height", "background-color",
            "text-align", "text-decoration", "display",
            "visibility", "opacity",
        )
        style_data = {
            p: computed.get_property_value(p)
            for p in _KNOWN_PROPS
        }
        return json.dumps(style_data)

    def set_attribute(self, py_id: Any, name: Any, value: Any) -> None:
        """Write *value* to attribute *name* on the element identified by *py_id*.

        Called from JS ``el.setAttribute(name, value)``.  Validates *name*
        as a non-empty string before calling
        :meth:`~aspose_html.dom.Element.set_attribute` to prevent prototype
        pollution.

        Parameters
        ----------
        py_id : int
            The ``__py_id__`` of the element in :data:`_ELEMENT_REGISTRY`.
        name : str
            Attribute name.  Silently ignored if empty or non-string.
        value : str
            Attribute value coerced to ``str``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> proxy = _DocumentProxy(doc)
        >>> _ = proxy.query_selector("div")  # registers el in _ELEMENT_REGISTRY
        >>> proxy.set_attribute(id(el), "class", "active")
        >>> el.get_attribute("class")
        'active'
        """
        if py_id is None:
            return
        el = _ELEMENT_REGISTRY.get(int(py_id))
        if el is None:
            return
        name_str = str(name) if name is not None else ""
        if not name_str:
            return
        el.set_attribute(name_str, str(value) if value is not None else "")


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _collect_by_tag(node: Any, tag: str, out: list) -> None:
    """Recursively collect child elements whose local_name matches *tag*."""
    from aspose_html.dom._element import Element  # noqa: PLC0415
    for child in node.child_nodes:
        if isinstance(child, Element):
            if tag == "*" or child._local_name == tag:
                out.append(child)
            _collect_by_tag(child, tag, out)
