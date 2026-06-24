"""HTML serialisation — WHATWG HTML Living Standard §13.3.

Converts a DOM node tree back to its HTML string representation.

Public API
----------
serialise(node)   -> str  — serialise a node and its descendants
inner_html(node)  -> str  — serialise only children (no outer tag)
outer_html(node)  -> str  — alias for serialise(); consistent with .outerHTML

: Void elements must never emit closing tags.
: Text escapes &, \\u00a0, <, >; attribute values escape &, \\u00a0, ".
: Round-trip property — serialise(HTMLDocument.parse(html)) re-parses to
         structurally equivalent DOM.

Examples
--------
>>> from aspose_html.dom import Document
>>> from aspose_html.serialiser import serialise
>>> doc = Document()
>>> el = doc.create_element("p")
>>> doc.append_child(el)  # doctest: +ELLIPSIS
<...>
>>> serialise(el)
'<p></p>'
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom import Node


# WHATWG HTML Living Standard §13.3
VOID_ELEMENTS: frozenset[str] = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

# WHATWG HTML Living Standard §13.3 — raw text elements
# (script, style content is not escaped)
RAW_TEXT_ELEMENTS: frozenset[str] = frozenset({
    "script", "style",
})

_HTML_NS = "http://www.w3.org/1999/xhtml"
_SVG_NS = "http://www.w3.org/2000/svg"
_MATHML_NS = "http://www.w3.org/1998/Math/MathML"


def _escape_text(s: str) -> str:
    """Escape text content per WHATWG HTML Living Standard §13.3.

    Replaces (in order, to avoid double-escaping):
      & → &amp;, \\u00a0 → &nbsp;, < → &lt;, > → &gt;
    """
    # & must be replaced first — 
    s = s.replace("&", "&amp;")
    s = s.replace("\u00a0", "&nbsp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def _escape_attr(s: str) -> str:
    """Escape an attribute value per WHATWG HTML Living Standard §13.3.

    Replaces (in order, to avoid double-escaping):
      & → &amp;, \\u00a0 → &nbsp;, " → &quot;
    """
    # & must be replaced first — 
    s = s.replace("&", "&amp;")
    s = s.replace("\u00a0", "&nbsp;")
    s = s.replace('"', "&quot;")
    return s


def _serialise_node(node: "Node", buf: list[str]) -> None:
    """Append the serialisation of *node* and its descendants to *buf*.

    Implements WHATWG HTML Living Standard §13.3 fragment serialisation
    algorithm. Dispatches on ``node.node_type``.
    """
    # Lazy import — defensive pattern per  and html_document.py convention
    from aspose_html.dom._node_type import NodeType  # noqa: PLC0415

    nt = node.node_type

    if nt == NodeType.ELEMENT_NODE:
        # Determine tag name for output per WHATWG §13.3.4.
        # HTML, SVG, MathML namespaces: use local_name (no prefix).
        # Unknown namespace with a prefix: use prefix:local_name.
        # Unknown namespace without prefix: use local_name.
        ns = node.namespace_uri  # type: ignore[attr-defined]
        local = node.local_name  # type: ignore[attr-defined]
        prefix = getattr(node, "prefix", None)  # type: ignore[attr-defined]

        if ns in (_HTML_NS, _SVG_NS, _MATHML_NS) or ns is None:
            # WHATWG §13.3.4: HTML/SVG/MathML namespaces use local_name only.
            tag = local
        else:
            # Unknown namespace: use qualified name when prefix is set.
            tag = f"{prefix}:{local}" if prefix else local

        buf.append("<")
        buf.append(tag)

        # Emit attributes in insertion order —  (order preserved)
        for attr in node.attributes:  # type: ignore[attr-defined]
            buf.append(" ")
            buf.append(attr.name)
            buf.append('="')
            buf.append(_escape_attr(str(attr.value)))
            buf.append('"')

        buf.append(">")

        # : void elements in HTML namespace (or no namespace) must not
        # emit children or a closing tag.
        if tag in VOID_ELEMENTS and (ns == _HTML_NS or ns is None):
            return

        # <template> serialises its _template_content fragment, not child_nodes.
        # See  and : _template_content is the documented internal
        # slot for template content (no public property in  v1.0).
        if tag == "template" and ns == _HTML_NS:
            tc = getattr(node, "_template_content", None)  # See 
            if tc is not None:
                for child in tc.child_nodes:
                    _serialise_node(child, buf)
        else:
            for child in node.child_nodes:
                _serialise_node(child, buf)

        buf.append("</")
        buf.append(tag)
        buf.append(">")

    elif nt == NodeType.TEXT_NODE:
        # Raw text elements (script, style) are not escaped — §13.3
        parent = node.parent_node
        if (
            parent is not None
            and parent.node_type == NodeType.ELEMENT_NODE
            and parent.local_name in RAW_TEXT_ELEMENTS  # type: ignore[attr-defined]
        ):
            buf.append(node.data)  # type: ignore[attr-defined]
        else:
            buf.append(_escape_text(node.data))  # type: ignore[attr-defined]

    elif nt == NodeType.CDATA_SECTION_NODE:
        # In HTML serialisation CDATASection is treated as Text (§13.3).
        buf.append(_escape_text(node.data))  # type: ignore[attr-defined]

    elif nt == NodeType.PROCESSING_INSTRUCTION_NODE:
        buf.append("<?")
        buf.append(node.target)  # type: ignore[attr-defined]
        buf.append(" ")
        buf.append(node.data)  # type: ignore[attr-defined]
        buf.append("?>")

    elif nt == NodeType.COMMENT_NODE:
        buf.append("<!--")
        buf.append(node.data)  # type: ignore[attr-defined]
        buf.append("-->")

    elif nt == NodeType.DOCUMENT_NODE:
        # Serialise all children in document order.
        for child in node.child_nodes:
            _serialise_node(child, buf)

    elif nt == NodeType.DOCUMENT_TYPE_NODE:
        s = "<!DOCTYPE " + node.name  # type: ignore[attr-defined]
        pub = node.public_id  # type: ignore[attr-defined]
        sys = node.system_id  # type: ignore[attr-defined]
        if pub:
            s += ' PUBLIC "' + pub + '"'
            if sys:
                s += ' "' + sys + '"'
        elif sys:
            s += ' SYSTEM "' + sys + '"'
        s += ">"
        buf.append(s)

    elif nt == NodeType.DOCUMENT_FRAGMENT_NODE:
        # Serialise all children in order (same as DOCUMENT_NODE).
        for child in node.child_nodes:
            _serialise_node(child, buf)

    # else: unknown node type — skip silently (future-proofing)


def serialise(node: "Node") -> str:
    """Serialise a DOM node to its HTML string representation.

    Implements the WHATWG HTML Living Standard §13.3 fragment
    serialisation algorithm.  When *node* is a ``Document``, the
    full document including the doctype is serialised.  When *node*
    is an ``Element``, the element and all its descendants are
    serialised (``outerHTML`` equivalent).  When *node* is a
    ``DocumentFragment``, the children are serialised without a
    wrapping tag (``innerHTML`` equivalent).

    Parameters
    ----------
    node : Node
        Any DOM node.  Supported types: ``Document``,
        ``DocumentFragment``, ``Element``, ``Text``, ``Comment``,
        ``CDATASection``, ``ProcessingInstruction``, ``DocumentType``.
        Unknown node types are silently skipped.

    Returns
    -------
    str
        The HTML serialisation of *node*.

    Raises
    ------
    TypeError
        If *node* is not a ``Node`` instance.

    Examples
    --------
    Serialise an element:

    >>> from aspose_html.dom import Document
    >>> from aspose_html.serialiser import serialise
    >>> doc = Document()
    >>> p = doc.create_element("p")
    >>> p.set_attribute("class", "intro")
    >>> t = doc.create_text_node("Hello")
    >>> p.append_child(t)  # doctest: +ELLIPSIS
    <...>
    >>> serialise(p)
    '<p class="intro">Hello</p>'

    Serialise a void element:

    >>> br = doc.create_element("br")
    >>> serialise(br)
    '<br>'

    Serialise a text node with characters that require escaping:

    >>> t2 = doc.create_text_node("a < b & c > d")
    >>> serialise(t2)
    'a &lt; b &amp; c &gt; d'

    Serialise an SVG element — local name only, per WHATWG §13.3.4:

    >>> svg_ns = "http://www.w3.org/2000/svg"
    >>> circle = doc.create_element_ns(svg_ns, "svg:circle")
    >>> serialise(circle)
    '<circle></circle>'
    """
    from aspose_html.dom._node import Node as _Node  # noqa: PLC0415

    if not isinstance(node, _Node):
        raise TypeError(
            f"serialise() expects a Node, got {type(node).__name__}"
        )
    buf: list[str] = []
    _serialise_node(node, buf)
    return "".join(buf)


def inner_html(node: "Node") -> str:
    """Return the serialisation of all children of *node*.

    Equivalent to the DOM ``innerHTML`` getter.  For an ``Element``,
    this is the serialised children without the element's own open/
    close tags.  For a ``Document`` or ``DocumentFragment``, this
    is the serialisation of all children.

    Parameters
    ----------
    node : Node
        A ``Document``, ``DocumentFragment``, or ``Element`` node.

    Returns
    -------
    str
        The ``innerHTML`` equivalent — children serialised, no
        wrapping tag.

    Raises
    ------
    TypeError
        If *node* is not a ``Node`` instance.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> from aspose_html.serialiser import inner_html
    >>> doc = Document()
    >>> div = doc.create_element("div")
    >>> span = doc.create_element("span")
    >>> div.append_child(span)  # doctest: +ELLIPSIS
    <...>
    >>> inner_html(div)
    '<span></span>'
    """
    from aspose_html.dom._node import Node as _Node  # noqa: PLC0415

    if not isinstance(node, _Node):
        raise TypeError(
            f"inner_html() expects a Node, got {type(node).__name__}"
        )
    buf: list[str] = []
    for child in node.child_nodes:
        _serialise_node(child, buf)
    return "".join(buf)


def outer_html(node: "Node") -> str:
    """Return the serialisation of *node* including its own tag.

    Equivalent to the DOM ``outerHTML`` getter.  Identical to
    ``serialise(node)`` for ``Element`` nodes.  For ``Document``
    and ``DocumentFragment`` nodes, delegates to ``serialise``.

    Parameters
    ----------
    node : Node
        Any DOM node.

    Returns
    -------
    str
        The ``outerHTML`` equivalent.

    Raises
    ------
    TypeError
        If *node* is not a ``Node`` instance.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> from aspose_html.serialiser import outer_html
    >>> doc = Document()
    >>> el = doc.create_element("section")
    >>> el.set_attribute("id", "main")
    >>> t = doc.create_text_node("body text")
    >>> el.append_child(t)  # doctest: +ELLIPSIS
    <...>
    >>> outer_html(el)
    '<section id="main">body text</section>'
    """
    return serialise(node)
