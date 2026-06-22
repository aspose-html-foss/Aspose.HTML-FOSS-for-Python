"""Document and ParseError — the root of the DOM tree."""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from aspose_html.dom._node import Node, _adopt
from aspose_html.dom._node_type import NodeType
from aspose_html.dom._exceptions import HierarchyRequestError, InvalidCharacterError, NotSupportedError
from aspose_html.dom._collections import (
    HTMLCollection,
    NodeList,
    _StaticNodeList,
    _SubtreeHTMLCollection,
)

if TYPE_CHECKING:
    from typing import Callable
    from aspose_html.cssom import CSSStyleSheet
    from aspose_html.dom._character_data import CDATASection
    from aspose_html.dom._element import Element
    from aspose_html.dom._style_sheets import StyleSheetList
    from aspose_html.dom._traversal import TreeWalker, NodeIterator
    from aspose_html.dom._range import Range
    from aspose_html.dom._selection import Selection
    from aspose_html.dom._implementation import DOMImplementation
    from aspose_html.dom._event import Event
    from aspose_html.layout import ComputedStyle


_HTML_NS = "http://www.w3.org/1999/xhtml"


def _collect_elements_by_ns(
    node: "Node",
    namespace: "str | None",
    local_name_lower: str,
    out: list,
) -> None:
    """Recursive depth-first collector for get_elements_by_tag_name_ns.

    Not part of the public API. Per WHATWG DOM §4.5.
    """
    from aspose_html.dom._element import Element  # noqa: PLC0415
    for child in getattr(node, "_children", ()):
        if isinstance(child, Element):
            ns_match = namespace == "*" or child._namespace_uri == namespace
            ln_match = local_name_lower == "*" or (
                child._local_name or ""
            ).lower() == local_name_lower
            if ns_match and ln_match:
                out.append(child)
        _collect_elements_by_ns(child, namespace, local_name_lower, out)


def _coerce_nodes(
    nodes: "tuple[Node | str, ...]",
    owner_document: "Document | None",
) -> "list[Node]":
    """Convert a mixed tuple of Node and str into a list of Node objects.

    Strings are converted to Text nodes via *owner_document*.create_text_node().
    Used by the ParentNode mixin methods (ADR-028).
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


# Populated by aspose_html.dom.html (BACK-16) on first create_element() call.
# Keyed by lowercase tag name; values are HTMLElement subclasses.
_ELEMENT_REGISTRY: dict[str, type] = {}
_registry_loaded: bool = False

# BACK-68/BACK-70: keep per-Document runtime state without widening
# Document.__slots__ (validated by tests as a public compatibility contract).
_DEFAULT_VIEW_BY_DOC_ID: dict[int, object] = {}
_IMPLEMENTATION_BY_DOC_ID: dict[int, object] = {}
_UPGRADE_QUEUE_BY_DOC_ID: dict[int, list["Element"]] = {}
_ATTACHED_STYLE_SHEETS_BY_DOC_ID: dict[int, list["CSSStyleSheet"]] = {}
_ADOPTED_STYLE_SHEETS_BY_DOC_ID: dict[int, list["CSSStyleSheet"]] = {}
_DOM_CONFIG_BY_DOC_ID: dict[int, "DOMConfiguration"] = {}
_READY_STATE_BY_DOC_ID: dict[int, str] = {}


def _try_load_html_registry() -> None:
    """Attempt to import the HTML element registry (BACK-16).

    Sets ``_registry_loaded`` to True after the first attempt (success or
    failure) so that the import is only tried once per process.
    """
    global _registry_loaded
    _registry_loaded = True
    try:
        import aspose_html.dom.html as _html_pkg  # noqa: PLC0415
        _html_pkg.register(_ELEMENT_REGISTRY)
    except ImportError:
        pass  # BACK-16 not yet installed — graceful degradation


@dataclasses.dataclass
class ParseError:
    """A parse error recorded during tree construction.

    Examples
    --------
    >>> e = ParseError(code="eof-in-comment", line=1, column=5, message="unexpected EOF")
    >>> e.code
    'eof-in-comment'
    """

    code: str
    line: int
    column: int
    message: str


class DOMConfiguration:
    """Baseline DOMConfiguration compatibility surface.

    This object stores a minimal, deterministic parameter map for legacy
    document-level normalization configuration.

    Examples
    --------
    >>> cfg = DOMConfiguration()
    >>> cfg.can_set_parameter("comments", True)
    True
    >>> cfg.set_parameter("comments", False)
    >>> cfg.get_parameter("comments")
    False
    """

    __slots__ = ("_parameters",)

    _SUPPORTED_DEFAULTS = {
        "comments": True,
        "namespaces": True,
        "well-formed": True,
    }

    def __init__(self) -> None:
        self._parameters: dict[str, bool] = dict(self._SUPPORTED_DEFAULTS)

    def can_set_parameter(self, name: str, value: object) -> bool:
        """Return whether *name* can be set to *value*.

        Parameters are case-insensitive and currently support only boolean
        values for the baseline set.
        """
        return name.lower() in self._SUPPORTED_DEFAULTS and isinstance(value, bool)

    def set_parameter(self, name: str, value: object) -> None:
        """Set a baseline parameter.

        Raises
        ------
        NotSupportedError
            If *name* is unsupported or *value* is not a bool.
        """
        normalized = name.lower()
        if normalized not in self._SUPPORTED_DEFAULTS or not isinstance(value, bool):
            raise NotSupportedError(
                f"Unsupported DOMConfiguration parameter assignment: {name!r}."
            )
        self._parameters[normalized] = value

    def get_parameter(self, name: str) -> bool:
        """Return the current value for a baseline parameter.

        Raises
        ------
        NotSupportedError
            If *name* is unsupported.
        """
        normalized = name.lower()
        if normalized not in self._SUPPORTED_DEFAULTS:
            raise NotSupportedError(
                f"Unsupported DOMConfiguration parameter lookup: {name!r}."
            )
        return self._parameters[normalized]


class _DocumentTimeline:
    """Minimal DocumentTimeline stub (Web Animations API §6.2).

    A read-only timeline attached to every :class:`Document`.  In headless
    mode the timeline is always paused at ``0.0`` — no animation engine is
    running.

    Examples
    --------
    >>> from aspose_html.dom._document import _DocumentTimeline
    >>> tl = _DocumentTimeline()
    >>> tl.current_time
    0.0
    """

    __slots__ = ()

    @property
    def current_time(self) -> float:
        """Current time in milliseconds; always ``0.0`` in headless mode.

        Examples
        --------
        >>> from aspose_html.dom._document import _DocumentTimeline
        >>> _DocumentTimeline().current_time
        0.0
        """
        return 0.0

    def __repr__(self) -> str:
        return "DocumentTimeline(current_time=0.0)"


class _AllCollection:
    """Lazy all-elements-in-tree-order collection (WHATWG HTML §legacy).

    Iterates all Element descendants of the document in tree order.
    Supports ``__len__``, ``__iter__``, and integer ``__getitem__``.
    Named access (``doc.all["id"]``) is not supported in this stub.

    Examples
    --------
    >>> from aspose_html import HTMLDocument
    >>> doc = HTMLDocument.parse('<html><body><p>Hi</p></body></html>')
    >>> ac = doc.all
    >>> len(ac) > 0
    True
    """

    __slots__ = ("_doc",)

    def __init__(self, doc: "Document") -> None:
        self._doc = doc

    def _elements(self) -> list:
        """Collect all Element nodes in tree order."""
        from aspose_html.dom._element import Element  # noqa: PLC0415
        result: list = []
        stack = list(reversed(getattr(self._doc, "_children", [])))
        while stack:
            node = stack.pop()
            if isinstance(node, Element):
                result.append(node)
            stack.extend(reversed(getattr(node, "_children", [])))
        return result

    def __len__(self) -> int:
        return len(self._elements())

    def __iter__(self):
        return iter(self._elements())

    def __getitem__(self, index: int):
        return self._elements()[index]


class Document(Node):
    """The root of a DOM tree.

    ``Document()`` creates an empty, standards-mode document.  Use the
    factory methods (``create_element``, ``create_text_node``, etc.) to
    create child nodes.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> doc.node_type
    9
    >>> doc.compat_mode
    'CSS1Compat'
    """

    __slots__ = (
        "_compat_mode",
        "_parse_errors",
        "_id_map",
        "_url",
        "_mutation_signal",
        "_selection",
        "_character_set",   # WHATWG DOM §3.1
        "_style_epoch",     # M7.1 layout style cache generation — SPEC-168/ADR-315
        "_style_cache",     # M7.1 dict[int, ComputedStyle] keyed by id(element)
    )

    def __init__(self) -> None:
        super().__init__(NodeType.DOCUMENT_NODE, owner_document=None)
        from aspose_html.dom._mutation_observer import _MutationSignal  # noqa: PLC0415

        self._compat_mode: str = "CSS1Compat"
        self._parse_errors: list[ParseError] = []
        self._id_map: dict[str, Element] = {}
        self._url: str = "about:blank"
        self._mutation_signal: _MutationSignal = _MutationSignal()
        from aspose_html.dom._selection import Selection  # noqa: PLC0415

        self._selection: Selection = Selection(self)
        self._character_set: str = "UTF-8"
        # M7.1 layout style cache (SPEC-168/ADR-315): a monotonic epoch and a
        # per-document ComputedStyle cache keyed by id(element). The cache lives
        # on the Document instance — never at module scope (INV-010).
        self._style_epoch: int = 0
        self._style_cache: dict[int, "ComputedStyle"] = {}
        _READY_STATE_BY_DOC_ID[id(self)] = "complete"

    # ------------------------------------------------------------------
    # Internal navigation lifecycle helpers (Track 56 contract)
    # ------------------------------------------------------------------

    def _navigation_prepare_replacement(self) -> None:
        """Enter deterministic pre-parse state for document replacement.

        Internal helper used by Window lifecycle hooks.
        """
        _READY_STATE_BY_DOC_ID[id(self)] = "loading"

    def _navigation_mark_parser_started(self) -> None:
        """Mark the document as parser-interactive during lifecycle progression."""
        _READY_STATE_BY_DOC_ID[id(self)] = "interactive"

    def _navigation_mark_complete(self) -> None:
        """Mark lifecycle completion for the active document."""
        _READY_STATE_BY_DOC_ID[id(self)] = "complete"

    def __del__(self) -> None:
        doc_id = id(self)
        _DEFAULT_VIEW_BY_DOC_ID.pop(doc_id, None)
        _IMPLEMENTATION_BY_DOC_ID.pop(doc_id, None)
        _UPGRADE_QUEUE_BY_DOC_ID.pop(doc_id, None)
        _ATTACHED_STYLE_SHEETS_BY_DOC_ID.pop(doc_id, None)
        _ADOPTED_STYLE_SHEETS_BY_DOC_ID.pop(doc_id, None)
        _DOM_CONFIG_BY_DOC_ID.pop(doc_id, None)
        _READY_STATE_BY_DOC_ID.pop(doc_id, None)

    def _bump_style_epoch(self) -> None:
        """Invalidate the layout style cache (M7.1 — SPEC-168/ADR-315).

        Increments ``_style_epoch`` by 1 and clears the per-document
        ``ComputedStyle`` cache. Called by the DOM mutation hooks (attribute,
        inline style, stylesheet, and tree changes) so the next
        ``computed_style`` read misses and produces a fresh snapshot carrying
        the new epoch. Internal — not on the public CSSOM surface (INV-001).
        """
        self._style_epoch += 1
        self._style_cache.clear()

    def _get_cached_default_view(self):
        return _DEFAULT_VIEW_BY_DOC_ID.get(id(self))

    def _enqueue_for_upgrade(self, element: "Element") -> None:
        doc_id = id(self)
        queue = _UPGRADE_QUEUE_BY_DOC_ID.get(doc_id)
        if queue is None:
            queue = []
            _UPGRADE_QUEUE_BY_DOC_ID[doc_id] = queue
        queue.append(element)

    def _upgrade_queue_snapshot(self) -> list["Element"]:
        return list(_UPGRADE_QUEUE_BY_DOC_ID.get(id(self), ()))

    def _replace_upgrade_queue(self, queue: list["Element"]) -> None:
        doc_id = id(self)
        if queue:
            _UPGRADE_QUEUE_BY_DOC_ID[doc_id] = queue
            return
        _UPGRADE_QUEUE_BY_DOC_ID.pop(doc_id, None)

    def _attached_style_sheets(self) -> list["CSSStyleSheet"]:
        return _ATTACHED_STYLE_SHEETS_BY_DOC_ID.setdefault(id(self), [])

    def _adopted_style_sheets(self) -> list["CSSStyleSheet"]:
        return _ADOPTED_STYLE_SHEETS_BY_DOC_ID.setdefault(id(self), [])

    @property
    def default_view(self):
        """Per-Document Window object (lazy, cached)."""
        doc_id = id(self)
        view = _DEFAULT_VIEW_BY_DOC_ID.get(doc_id)
        if view is None:
            from aspose_html.dom._window import Window  # noqa: PLC0415
            view = Window(self)
            _DEFAULT_VIEW_BY_DOC_ID[doc_id] = view
        return view

    @property
    def location(self):
        """Return the associated Window's Location object, or ``None``.

        WHATWG HTML §9.2.7: the ``location`` attribute returns the ``Location``
        object of the browsing context.  In headless mode a ``Document`` is
        detached unless it was created by a ``Window``; the backing attribute
        is ``_owner_window``.  When no ``_owner_window`` is set (all bare
        ``Document()`` instances), ``None`` is returned.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().location is None
        True
        """
        w = getattr(self, "_owner_window", None)
        if w is not None:
            return w.location
        return None

    @property
    def implementation(self) -> "DOMImplementation":
        """Per-Document DOMImplementation object (lazy, cached).

        Repeated access returns the same object for this document.

        Examples
        --------
        >>> from aspose_html.dom import DOMImplementation, Document
        >>> doc = Document()
        >>> isinstance(doc.implementation, DOMImplementation)
        True
        >>> doc.implementation is doc.implementation
        True
        >>> Document().implementation is doc.implementation
        False
        """
        doc_id = id(self)
        implementation = _IMPLEMENTATION_BY_DOC_ID.get(doc_id)
        if implementation is None:
            from aspose_html.dom._implementation import DOMImplementation  # noqa: PLC0415

            implementation = DOMImplementation(self)
            _IMPLEMENTATION_BY_DOC_ID[doc_id] = implementation
        return implementation

    @property
    def dom_config(self) -> DOMConfiguration:
        """Per-Document DOMConfiguration object (lazy, cached).

        Repeated access returns the same configuration object for this
        document instance.

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMConfiguration
        >>> doc = Document()
        >>> isinstance(doc.dom_config, DOMConfiguration)
        True
        >>> doc.dom_config is doc.dom_config
        True
        >>> Document().dom_config is doc.dom_config
        False
        >>> cfg = doc.dom_config
        >>> cfg.get_parameter("comments")
        True
        >>> cfg.set_parameter("comments", False)
        >>> cfg.get_parameter("comments")
        False
        """
        doc_id = id(self)
        config = _DOM_CONFIG_BY_DOC_ID.get(doc_id)
        if config is None:
            config = DOMConfiguration()
            _DOM_CONFIG_BY_DOC_ID[doc_id] = config
        return config

    def normalize_document(self) -> None:
        """Normalize this document using existing ``Node.normalize`` semantics.

        This normalizes the full document subtree in place, merging adjacent
        text nodes and removing empty text nodes where applicable.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> root = doc.create_element("div")
        >>> doc.append_child(root)
        <Element 'DIV'>
        >>> root.append_child(doc.create_text_node("a"))
        <Text data='a'>
        >>> root.append_child(doc.create_text_node("b"))
        <Text data='b'>
        >>> len(root.child_nodes)
        2
        >>> doc.normalize_document()
        >>> len(root.child_nodes)
        1
        >>> root.first_child.data
        'ab'
        >>> doc.normalize_document()  # idempotent repeat call
        >>> root.first_child.data
        'ab'
        """
        self.normalize()

    @property
    def _ranges(self):
        """Internal weak set of live ranges, stored on the mutation signal."""
        return self._mutation_signal._ranges

    def _register_range(self, range_obj: "Range") -> None:
        """Register a live range weakly for internal mutation updates."""
        self._mutation_signal._ranges.add(range_obj)

    def _unregister_range(self, range_obj: "Range") -> None:
        """Remove a live range from internal mutation updates if present."""
        self._mutation_signal._ranges.discard(range_obj)

    @property
    def url(self) -> str:
        """Document URL (WHATWG ``Document.URL``), default ``"about:blank"``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().url
        'about:blank'
        """
        return self._url

    @property
    def document_uri(self) -> str:
        """The document's URL as a string (WHATWG DOM §4.5 ``documentURI``).

        Always returns the same value as :attr:`url`. Provided as a
        DOM-standard alias for code that uses the ``documentURI`` property
        name. Both properties read from the same internal slot (``_url``),
        so they remain identical under any mutation.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.document_uri == doc.url
        True
        >>> doc.document_uri
        'about:blank'
        """
        return self._url

    @property
    def base_uri(self) -> str:
        """Resolved base URL for this document (WHATWG DOM ``Node.baseURI``).

        The getter scans ``<base href>`` elements in document tree order and
        returns the first parseable candidate resolved against :attr:`url`.
        If no parseable ``href`` exists, it falls back to :attr:`url`.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.base_uri == doc.url
        True

        >>> html = doc.create_element("html")
        >>> head = doc.create_element("head")
        >>> base = doc.create_element("base")
        >>> base.set_attribute("href", "assets/")
        >>> _ = head.append_child(base)
        >>> _ = html.append_child(head)
        >>> _ = doc.append_child(html)
        >>> doc._url = "https://example.com/root/page.html"
        >>> doc.base_uri
        'https://example.com/root/assets/'
        """
        from aspose_html.url import URL  # noqa: PLC0415

        stack: list[Node] = [self]
        while stack:
            current = stack.pop()
            if current._node_type == NodeType.ELEMENT_NODE:
                namespace_uri = getattr(current, "namespace_uri", None)
                local_name = getattr(current, "local_name", "")
                if namespace_uri == _HTML_NS and local_name == "base":
                    href = current.get_attribute("href")  # type: ignore[attr-defined]
                    if href and URL.can_parse(href, base=self.url):
                        try:
                            return URL(href, base=self.url).href
                        except Exception:
                            pass

            for child in reversed(current._children):
                stack.append(child)

        return self.url

    @property
    def referrer(self) -> str:
        """Referring document URL (WHATWG HTML Standard §document).

        Always ``""`` in a server-side parse context (no HTTP request chain).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().referrer
        ''
        """
        return ""

    @property
    def domain(self) -> str:
        """Hostname component of the document URL (WHATWG HTML Standard §document).

        Returns the ``hostname`` of the document's :attr:`url` when it is a
        parseable absolute URL; returns ``""`` otherwise (``"about:blank"``,
        empty string, or unparseable URL).

        The setter is intentionally absent — the ``document.domain`` security
        setter is out of scope for server-side use.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().domain
        ''
        """
        try:
            from aspose_html.url import URL  # noqa: PLC0415
            return URL(self._url).hostname
        except Exception:
            return ""

    @property
    def last_modified(self) -> str:
        """Last-modified timestamp string (WHATWG HTML Standard §document).

        Always ``""`` — no file-system or HTTP Last-Modified header is
        available in a server-side parse context.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().last_modified
        ''
        """
        return ""

    @property
    def cookie(self) -> str:
        """Read-only cookie string stub — always returns ``""`` (WHATWG HTML §8.11.1).

        A setter is provided but always raises :class:`NotSupportedError` because
        headless document processing does not support cookie storage.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.cookie
        ''
        """
        return ""

    @cookie.setter
    def cookie(self, value: str) -> None:
        """Raise :class:`NotSupportedError` — cookie storage is not supported.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> doc = Document()
        >>> try:
        ...     doc.cookie = "foo=bar"
        ... except NotSupportedError as exc:
        ...     print(str(exc))
        Document.cookie is not supported in headless mode
        """
        raise NotSupportedError("Document.cookie is not supported in headless mode")

    @property
    def hidden(self) -> bool:
        """Whether the document is hidden — always ``False`` in headless mode.

        Per Page Visibility Level 2 §5. A headless document is never visually
        hidden; it has no rendering surface.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().hidden
        False
        """
        return False

    @property
    def visibility_state(self) -> str:
        """Document visibility state — always ``"visible"`` in headless mode.

        Per Page Visibility Level 2 §5.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().visibility_state
        'visible'
        """
        return "visible"

    def has_focus(self) -> bool:
        """Return whether the document has focus — always ``False`` in headless mode.

        Per WHATWG HTML §7.3.1. No focus management is performed in headless
        document processing.

        Returns
        -------
        bool
            Always ``False``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().has_focus()
        False
        """
        return False

    @property
    def design_mode(self) -> str:
        """Whether the document is in design mode (WHATWG HTML §7.6.4).

        Returns ``"off"`` in headless mode. Full edit-mode activation is not
        supported in static document processing; the getter always reflects
        the headless default. The setter accepts ``"on"`` or ``"off"`` and
        is a no-op — setting design mode does not change document behaviour.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.design_mode
        'off'
        >>> doc.design_mode = 'on'
        >>> doc.design_mode
        'off'
        """
        return "off"

    @design_mode.setter
    def design_mode(self, value: str) -> None:
        """Set design mode — no-op in headless mode (WHATWG HTML §7.6.4)."""

    @property
    def dir(self) -> str:
        """Document text direction (WHATWG HTML §3.3.2).

        Returns ``""`` in headless mode (no forced text direction). The
        setter accepts ``"ltr"``, ``"rtl"``, ``"auto"``, or ``""`` and is a
        no-op — RTL-aware frameworks may write this attribute; the getter
        always returns ``""`` because headless processing applies no forced
        directionality.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.dir
        ''
        >>> doc.dir = 'rtl'
        >>> doc.dir
        ''
        """
        return ""

    @dir.setter
    def dir(self, value: str) -> None:
        """Set document text direction — no-op in headless mode (WHATWG HTML §3.3.2)."""

    @property
    def current_script(self) -> None:
        """The currently executing script element (WHATWG HTML §8.1.3.4).

        Returns ``None`` in headless mode — no script is being parsed or
        executed. Code that reads this property to determine the currently
        executing ``<script>`` element for dynamic base-URL derivation
        receives ``None`` and can skip the optimisation.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().current_script is None
        True
        """
        return None

    def open(self, type: str = "text/html", replace: str = "") -> "Document":
        """Open the document for writing (WHATWG HTML §7.7).

        Not supported in static document processing mode.

        Parameters
        ----------
        type : str
            MIME type for the new document stream.  Ignored.
        replace : str
            If ``"replace"``, the history entry is replaced.  Ignored.

        Returns
        -------
        Document
            This method never returns normally.

        Raises
        ------
        NotSupportedError
            Always.  Dynamic document opening is not supported in headless
            document processing mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> doc = Document()
        >>> try:
        ...     doc.open()
        ... except NotSupportedError as exc:
        ...     print(str(exc))
        Document.open() is not supported in static document processing mode
        """
        self.default_view._document_dynamic_markup_intent("open")
        raise NotSupportedError(
            "Document.open() is not supported in static document processing mode"
        )

    def close(self) -> None:
        """Close the document after writing (WHATWG HTML §7.7).

        Not supported in static document processing mode.

        Raises
        ------
        NotSupportedError
            Always.  Dynamic document close is not supported in headless
            document processing mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> doc = Document()
        >>> try:
        ...     doc.close()
        ... except NotSupportedError as exc:
        ...     print(str(exc))
        Document.close() is not supported in static document processing mode
        """
        self.default_view._document_dynamic_markup_intent("close")
        raise NotSupportedError(
            "Document.close() is not supported in static document processing mode"
        )

    def write(self, *text: str) -> None:
        """Write a string to the document stream (WHATWG HTML §7.7).

        Not supported.  Use :meth:`~aspose_html.html_document.HTMLDocument.parse`
        to create documents from HTML source.

        Parameters
        ----------
        *text : str
            One or more strings to write.  Ignored.

        Raises
        ------
        NotSupportedError
            Always.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> doc = Document()
        >>> try:
        ...     doc.write("<p>hello</p>")
        ... except NotSupportedError as exc:
        ...     print(str(exc))
        Document.write() is not supported; use HTMLDocument.parse() to create documents
        """
        self.default_view._document_dynamic_markup_intent("write")
        raise NotSupportedError(
            "Document.write() is not supported; use HTMLDocument.parse() to create documents"
        )

    def writeln(self, *text: str) -> None:
        """Write a string followed by a newline (WHATWG HTML §7.7).

        Not supported.  Use :meth:`~aspose_html.html_document.HTMLDocument.parse`
        to create documents from HTML source.

        Parameters
        ----------
        *text : str
            One or more strings to write.  Ignored.

        Raises
        ------
        NotSupportedError
            Always.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> doc = Document()
        >>> try:
        ...     doc.writeln("<p>hello</p>")
        ... except NotSupportedError as exc:
        ...     print(str(exc))
        Document.write() is not supported; use HTMLDocument.parse() to create documents
        """
        self.default_view._document_dynamic_markup_intent("writeln")
        raise NotSupportedError(
            "Document.write() is not supported; use HTMLDocument.parse() to create documents"
        )

    @property
    def character_set(self) -> str:
        """Character encoding used during parsing (WHATWG DOM §3.1).

        Returns the encoding label that was detected or set when the document
        was parsed.  For documents not created by :meth:`HTMLDocument.parse`,
        the default value is ``"UTF-8"``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().character_set
        'UTF-8'
        """
        return self._character_set

    @property
    def charset(self) -> str:
        """Alias for :attr:`character_set` (HTML Standard name).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.charset == doc.character_set
        True
        """
        return self._character_set

    @property
    def input_encoding(self) -> str:
        """Alias for :attr:`character_set` (WHATWG DOM compatibility name).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.input_encoding == doc.character_set
        True
        """
        return self._character_set

    @property
    def content_type(self) -> str:
        """Document MIME type; always ``"text/html"`` for HTML documents.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().content_type
        'text/html'
        """
        return "text/html"

    @property
    def style_sheets(self) -> "StyleSheetList":
        """Live document stylesheet list.

        Order is deterministic:
        1. Programmatic/adopted sheets from ``adopted_style_sheets``.
        2. ``<style>`` and ``<link rel='stylesheet'>`` sheets in document order.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sheet = CSSStyleSheet()
        >>> doc.attach_style_sheet(sheet)
        >>> doc.style_sheets.length
        1
        >>> doc.style_sheets.item(0) is sheet
        True
        """
        from aspose_html.dom._style_sheets import StyleSheetList  # noqa: PLC0415
        return StyleSheetList(self._collect_style_sheets)

    @property
    def adopted_style_sheets(self) -> list["CSSStyleSheet"]:
        """Document-level constructable stylesheet adoption list.

        Getter returns a shallow copy so callers cannot mutate internal state
        without using assignment.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.adopted_style_sheets
        []
        >>> first = CSSStyleSheet()
        >>> second = CSSStyleSheet()
        >>> doc.adopted_style_sheets = [first, second]
        >>> [sheet is first for sheet in doc.adopted_style_sheets]
        [True, False]
        >>> doc.adopted_style_sheets[1] is second
        True
        """
        return list(self._adopted_style_sheets())

    @adopted_style_sheets.setter
    def adopted_style_sheets(self, sheets: "list[CSSStyleSheet] | tuple[CSSStyleSheet, ...]") -> None:
        """Replace document-adopted stylesheets atomically.

        Raises
        ------
        TypeError
            If *sheets* is not a list/tuple of ``CSSStyleSheet`` objects.
        """
        from aspose_html.cssom import CSSStyleSheet  # noqa: PLC0415

        if not isinstance(sheets, (list, tuple)):
            raise TypeError("adopted_style_sheets must be a list or tuple of CSSStyleSheet")
        validated: list[CSSStyleSheet] = []
        for sheet in sheets:
            if not isinstance(sheet, CSSStyleSheet):
                raise TypeError("adopted_style_sheets entries must be CSSStyleSheet instances")
            validated.append(sheet)
        # Drop the back-reference on sheets no longer adopted (M7.1).
        for previous in self._adopted_style_sheets():
            if previous not in validated:
                previous._set_owner_document(None)
        for sheet in validated:
            sheet._set_owner_document(self)
        _ADOPTED_STYLE_SHEETS_BY_DOC_ID[id(self)] = validated
        # One epoch bump per assignment regardless of sheet count (AC-10).
        self._bump_style_epoch()

    def attach_style_sheet(self, sheet: "CSSStyleSheet") -> None:
        """Attach a stylesheet to this document.

        Duplicate attachment by object identity is ignored.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sheet = CSSStyleSheet()
        >>> doc.attach_style_sheet(sheet)
        >>> doc.attach_style_sheet(sheet)
        >>> doc.style_sheets.length
        1
        """
        adopted_sheets = self._adopted_style_sheets()
        for adopted in adopted_sheets:
            if adopted is sheet:
                return
        sheet.owner_node = None
        sheet._set_owner_document(self)  # M7.1 back-reference for cache invalidation
        adopted_sheets.append(sheet)
        self._bump_style_epoch()  # AC-8

    def detach_style_sheet(self, sheet: "CSSStyleSheet") -> None:
        """Detach a previously attached stylesheet.

        Missing sheets are ignored.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> sheet = CSSStyleSheet()
        >>> doc.detach_style_sheet(sheet)
        >>> doc.style_sheets.length
        0
        """
        remaining = [
            adopted for adopted in self._adopted_style_sheets() if adopted is not sheet
        ]
        removed = len(remaining) != len(self._adopted_style_sheets())
        _ADOPTED_STYLE_SHEETS_BY_DOC_ID[id(self)] = remaining
        if removed:
            sheet._set_owner_document(None)  # M7.1 drop back-reference
        self._bump_style_epoch()  # AC-9 (bumps once per call)

    def _collect_style_sheets(self) -> list["CSSStyleSheet"]:
        sheets = list(self._adopted_style_sheets())
        stack = list(self._children)
        while stack:
            node = stack.pop(0)
            sheet = getattr(node, "sheet", None)
            if sheet is not None:
                sheets.append(sheet)
            stack[0:0] = list(node._children)
        return sheets

    # ------------------------------------------------------------------
    # Node interface
    # ------------------------------------------------------------------

    @property
    def node_name(self) -> str:
        """``'#document'``

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().node_name
        '#document'
        """
        return "#document"

    # ------------------------------------------------------------------
    # Document properties
    # ------------------------------------------------------------------

    @property
    def document_element(self) -> Element | None:
        """The root Element child, or ``None`` if not yet set.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.document_element is None
        True
        >>> el = doc.create_element("html")
        >>> doc.append_child(el)
        <Element 'HTML'>
        >>> doc.document_element is el
        True
        """
        for child in self._children:
            if child._node_type == NodeType.ELEMENT_NODE:
                return child  # type: ignore[return-value]
        return None

    @property
    def document_type(self) -> DocumentType | None:
        """The DocumentType child, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document, DocumentType
        >>> doc = Document()
        >>> doc.document_type is None
        True
        """
        for child in self._children:
            if child._node_type == NodeType.DOCUMENT_TYPE_NODE:
                return child  # type: ignore[return-value]
        return None

    @property
    def compat_mode(self) -> str:
        """``'BackCompat'`` (quirks) or ``'CSS1Compat'`` (no-quirks).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().compat_mode
        'CSS1Compat'
        """
        return self._compat_mode

    @compat_mode.setter
    def compat_mode(self, value: str) -> None:
        """Set by the tree constructor only.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.compat_mode = "BackCompat"
        >>> doc.compat_mode
        'BackCompat'
        """
        self._compat_mode = value

    @property
    def ready_state(self) -> str:
        """Document loading state.

        Per WHATWG HTML §7.7.1, browsers cycle through ``'loading'``,
        ``'interactive'``, and ``'complete'``. In this library, direct
        document creation/parsing returns fully constructed documents, so
        the default value is ``'complete'``. Internal navigation lifecycle
        helpers may temporarily expose ``'loading'``/``'interactive'`` while
        replacement/parsing hooks execute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().ready_state
        'complete'
        """
        return _READY_STATE_BY_DOC_ID.get(id(self), "complete")

    @property
    def parse_errors(self) -> list[ParseError]:
        """Parse errors from the last parse operation.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().parse_errors
        []
        """
        return self._parse_errors

    @property
    def head(self) -> Element | None:
        """The ``<head>`` element child of ``document_element``, or ``None``.

        Returns the first child ``Element`` of ``document_element`` whose
        ``local_name`` is ``"head"`` (case-insensitive), or ``None`` if
        ``document_element`` is ``None`` or has no ``<head>`` child.

        This property never mutates the document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.head is None
        True
        >>> html = doc.create_element("html")
        >>> head = doc.create_element("head")
        >>> doc.append_child(html)
        <Element 'HTML'>
        >>> html.append_child(head)
        <Element 'HEAD'>
        >>> doc.head is head
        True
        """
        de = self.document_element
        if de is None:
            return None
        for child in de._children:
            if (
                child._node_type == NodeType.ELEMENT_NODE
                and child._local_name.lower() == "head"  # INV-005: case-insensitive per WHATWG
            ):
                return child  # type: ignore[return-value]
        return None

    @property
    def body(self) -> Element | None:
        """The ``<body>`` element child of ``document_element``, or ``None``.

        Returns the first child ``Element`` of ``document_element`` whose
        ``local_name`` is ``"body"`` (case-insensitive), or ``None`` if
        ``document_element`` is ``None`` or has no ``<body>`` child.

        This property never mutates the document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.body is None
        True
        >>> html = doc.create_element("html")
        >>> body = doc.create_element("body")
        >>> doc.append_child(html)
        <Element 'HTML'>
        >>> html.append_child(body)
        <Element 'BODY'>
        >>> doc.body is body
        True
        """
        de = self.document_element
        if de is None:
            return None
        for child in de._children:
            if (
                child._node_type == NodeType.ELEMENT_NODE
                and child._local_name.lower() == "body"  # INV-005: case-insensitive per WHATWG
            ):
                return child  # type: ignore[return-value]
        return None

    @property
    def forms(self) -> "HTMLCollection":
        """Live collection of all ``<form>`` elements in the document.

        Rescans the document subtree on every access (live semantics per
        WHATWG HTML §3.1.1).

        Returns
        -------
        HTMLCollection
            Every ``<form>`` element in document order.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse("<html><body><form></form></body></html>")
        >>> len(doc.forms)
        1
        >>> _ = doc.body.append_child(doc.create_element("form"))
        >>> len(doc.forms)
        2
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(  # type: ignore[return-value]
            self,
            lambda el: getattr(el, "_tag_name", None) == "FORM",
        )

    @property
    def images(self) -> "HTMLCollection":
        """Live collection of all ``<img>`` elements in the document.

        Rescans the document subtree on every access (live semantics per
        WHATWG HTML §3.1.1).

        Returns
        -------
        HTMLCollection
            Every ``<img>`` element in document order.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<html><body><img src="a.png"/></body></html>')
        >>> len(doc.images)
        1
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(  # type: ignore[return-value]
            self,
            lambda el: getattr(el, "_tag_name", None) == "IMG",
        )

    @property
    def links(self) -> "HTMLCollection":
        """Live collection of ``<a href>`` and ``<area href>`` elements.

        Only elements that carry an ``href`` attribute are included — bare
        ``<a>`` tags without ``href`` are excluded. ``<area>`` elements with
        ``href`` are included (WHATWG HTML §3.1.1).

        Rescans the document subtree on every access (live semantics).

        Returns
        -------
        HTMLCollection
            Every ``<a href>`` and ``<area href>`` element in document order.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<html><body><a href="#">link</a></body></html>')
        >>> len(doc.links)
        1
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(  # type: ignore[return-value]
            self,
            lambda el: getattr(el, "_tag_name", None) in ("A", "AREA")
            and el.has_attribute("href"),
        )

    @property
    def scripts(self) -> "HTMLCollection":
        """Live collection of all ``<script>`` elements in the document.

        Rescans the document subtree on every access (live semantics per
        WHATWG HTML §3.1.1).

        Returns
        -------
        HTMLCollection
            Every ``<script>`` element in document order.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<html><head><script></script></head></html>')
        >>> len(doc.scripts)
        1
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(  # type: ignore[return-value]
            self,
            lambda el: getattr(el, "_tag_name", None) == "SCRIPT",
        )

    @property
    def embeds(self) -> "HTMLCollection":
        """Live collection of all ``<embed>`` descendants.

        Analogous to :attr:`scripts` and :attr:`images`. Re-evaluated on
        each access (live collection semantics per WHATWG HTML §3.1.1).

        Returns
        -------
        HTMLCollection
            Every ``<embed>`` element in document order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> len(Document().embeds)
        0
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<html><body><embed src="a.swf"></body></html>')
        >>> len(doc.embeds)
        1
        >>> doc.embeds[0].tag_name
        'EMBED'
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(  # type: ignore[return-value]
            self,
            lambda el: getattr(el, "_tag_name", None) == "EMBED",
        )

    @property
    def applets(self) -> "HTMLCollection":
        """Live collection of all ``<applet>`` descendants.

        ``<applet>`` is obsolete; the WHATWG HTML parser never emits
        applet nodes. This collection is always empty.

        Returns
        -------
        HTMLCollection
            Every ``<applet>`` element in document order (always empty in
            practice).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> len(Document().applets)
        0
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(  # type: ignore[return-value]
            self,
            lambda el: getattr(el, "_tag_name", None) == "APPLET",
        )

    @property
    def anchors(self) -> "HTMLCollection":
        """Live collection of ``<a name=...>`` elements (legacy named anchors).

        Only ``<a>`` elements that carry a ``name`` attribute are included.
        Elements that have ``href`` but no ``name`` are excluded. This matches
        the legacy ``document.anchors`` semantics in WHATWG HTML §3.1.1.

        Rescans the document subtree on every access (live semantics).

        Returns
        -------
        HTMLCollection
            Every ``<a name=...>`` element in document order.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<html><body><a name="top">top</a></body></html>')
        >>> len(doc.anchors)
        1
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415
        return _SubtreeHTMLCollection(  # type: ignore[return-value]
            self,
            lambda el: getattr(el, "_tag_name", None) == "A"
            and el.has_attribute("name"),
        )

    @property
    def title(self) -> str:
        """The text content of the first ``<title>`` element in ``<head>``.

        Returns the ``text_content`` of the first child ``Element`` of
        ``head`` whose ``local_name`` is ``"title"`` (case-insensitive).
        Returns ``""`` if ``head`` is ``None``, or if ``head`` has no
        ``<title>`` child.

        This property never mutates the document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.title
        ''
        >>> html = doc.create_element("html")
        >>> head = doc.create_element("head")
        >>> title_el = doc.create_element("title")
        >>> title_el.text_content = "Hello"
        >>> doc.append_child(html)
        <Element 'HTML'>
        >>> html.append_child(head)
        <Element 'HEAD'>
        >>> head.append_child(title_el)
        <Element 'TITLE'>
        >>> doc.title
        'Hello'
        """
        head = self.head
        if head is None:
            return ""
        for child in head._children:
            if (
                child._node_type == NodeType.ELEMENT_NODE
                and child._local_name.lower() == "title"
            ):
                return child.text_content or ""  # type: ignore[union-attr]
        return ""

    @title.setter
    def title(self, value: str) -> None:
        """Set the text content of the first ``<title>`` element in ``<head>``.

        If ``head`` is ``None``, this is a no-op (graceful degradation for
        documents without a ``<head>`` element).

        If a ``<title>`` element already exists as a child of ``head``, its
        ``text_content`` is replaced with *value*.

        If no ``<title>`` element exists, one is created via
        ``create_element("title")``, its ``text_content`` is set to *value*,
        and it is appended to ``head``.

        Parameters
        ----------
        value : str
            The new title string.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> html = doc.create_element("html")
        >>> head = doc.create_element("head")
        >>> doc.append_child(html)
        <Element 'HTML'>
        >>> html.append_child(head)
        <Element 'HEAD'>
        >>> doc.title = "My Page"
        >>> doc.title
        'My Page'
        >>> doc.title = "Updated"
        >>> doc.title
        'Updated'
        """
        head = self.head
        if head is None:
            # See ADR-017: no-op when <head> absent — matches WHATWG graceful degradation
            return
        for child in head._children:
            if (
                child._node_type == NodeType.ELEMENT_NODE
                and child._local_name.lower() == "title"
            ):
                child.text_content = value  # type: ignore[union-attr]
                return
        new_title = self.create_element("title")
        new_title.text_content = value
        head.append_child(new_title)

    def save(
        self,
        path: "str | pathlib.Path",
        encoding: str = "utf-8",
    ) -> None:
        """Serialise the document and write it to a file.

        Calls ``serialise(self)`` (WHATWG §13.3 fragment serialisation) to
        produce the HTML string, then writes it to *path*. If the document
        has no ``DocumentType`` child node (i.e. was created programmatically
        without a doctype), the output is prefixed with
        ``"<!DOCTYPE html>\\n"`` before writing, ensuring the saved file is
        always a valid HTML5 document. When a ``DocumentType`` child is
        present, ``serialise()`` already emits the doctype — it is not
        doubled.

        Parameters
        ----------
        path : str | pathlib.Path
            Destination file path. The file is created or overwritten. Parent
            directory must already exist.
        encoding : str
            Any codec name accepted by Python's built-in ``open()`` (e.g.
            ``"utf-8"``, ``"utf-8-sig"``, ``"latin-1"``). Defaults to
            ``"utf-8"``.

        Returns
        -------
        None

        Raises
        ------
        OSError
            If the file cannot be written (permission denied, directory
            missing, etc.). Propagated from ``pathlib.Path.write_text()``.
        LookupError
            If *encoding* is not a recognised codec name. Propagated from
            ``open()``.

        Examples
        --------
        >>> import pathlib, tempfile
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<!DOCTYPE html><html><body><p>Hi</p></body></html>')
        >>> with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        ...     tmp = f.name
        >>> doc.save(tmp)
        >>> content = pathlib.Path(tmp).read_text(encoding='utf-8')
        >>> content.startswith('<!DOCTYPE html>')
        True
        >>> import os; os.unlink(tmp)
        """
        import pathlib  # noqa: PLC0415
        from aspose_html.serialiser import serialise  # noqa: PLC0415

        # serialise() already emits <!DOCTYPE ...> when the document has a
        # DocumentType child (WHATWG §13.3). Prepend the HTML5 declaration
        # only when no DocumentType node is present, so the saved file is
        # always a valid HTML5 document.  See ADR-025.
        has_doctype = any(
            child.node_type == NodeType.DOCUMENT_TYPE_NODE
            for child in self.child_nodes
        )

        html_text: str = serialise(self)
        if not has_doctype:
            output = "<!DOCTYPE html>\n" + html_text
        else:
            output = html_text

        pathlib.Path(path).write_text(output, encoding=encoding)

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    def create_element(self, tag_name: str) -> "HTMLElement":
        """Create an HTMLElement owned by this document.

        For HTML-namespace documents, *tag_name* is lowercased and the returned
        element is an instance of ``HTMLElement`` (or a registered subclass for
        known tag names populated by BACK-16).

        Parameters
        ----------
        tag_name : str
            The tag name. Case-insensitive; stored lowercase as ``local_name``.

        Returns
        -------
        HTMLElement
            An element in the HTML namespace, owned by this document.

        Examples
        --------
        >>> from aspose_html.dom import Document, HTMLElement, Element
        >>> doc = Document()
        >>> el = doc.create_element("DIV")
        >>> el.local_name
        'div'
        >>> el.tag_name
        'DIV'
        >>> el.owner_document is doc
        True
        >>> isinstance(el, HTMLElement)
        True
        >>> isinstance(el, Element)
        True
        """
        from aspose_html.dom._html_element import HTMLElement  # lazy — avoids circular import

        global _registry_loaded
        if not _registry_loaded:
            _try_load_html_registry()

        local_name = tag_name.lower()
        win = self._get_cached_default_view()
        if win is not None and win._custom_elements is not None:
            custom_cls = win._custom_elements.get(local_name)
            if custom_cls is not None:
                return custom_cls(local_name, namespace_uri=_HTML_NS, prefix=None, owner_document=self)
        cls = _ELEMENT_REGISTRY.get(local_name, HTMLElement)
        element = cls(
            local_name,
            namespace_uri=_HTML_NS,
            prefix=None,
            owner_document=self,
        )
        if "-" in local_name and (win is None or win._custom_elements is None or win._custom_elements.get(local_name) is None):
            self._enqueue_for_upgrade(element)
        return element

    def create_element_ns(self, namespace_uri: str, qualified_name: str) -> Element:
        """Create an Element in a specific namespace, owned by this document.

        This follows the WHATWG DOM §5.3.3 parameter order:
        *namespace_uri* first, *qualified_name* second.

        Unlike :meth:`create_element`, *qualified_name* is NOT lowercased —
        callers must supply the canonical local name for the target namespace
        (e.g. ``"svg"`` for SVG, ``"math"`` for MathML).

        Parameters
        ----------
        namespace_uri : str
            The namespace URI for the new element, e.g.
            ``"http://www.w3.org/2000/svg"`` or
            ``"http://www.w3.org/1998/Math/MathML"``.
        qualified_name : str
            The qualified name (or local name) for the new element.
            If it contains a colon (e.g. ``"svg:path"``), the part before
            the first colon is treated as the namespace prefix and the
            part after as the local name (WHATWG DOM §4.6).

        Returns
        -------
        Element
            A new Element with *namespace_uri*, *prefix*, and *local_name*
            set correctly, owned by this document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element_ns("http://www.w3.org/2000/svg", "svg")
        >>> el.local_name
        'svg'
        >>> el.prefix is None
        True
        >>> el.namespace_uri
        'http://www.w3.org/2000/svg'
        >>> el.owner_document is doc
        True

        Qualified names split into prefix and local name:

        >>> svg_ns = "http://www.w3.org/2000/svg"
        >>> path = doc.create_element_ns(svg_ns, "svg:path")
        >>> path.prefix
        'svg'
        >>> path.local_name
        'path'
        >>> path.tag_name
        'svg:path'

        Deprecated calling convention (tag first) emits DeprecationWarning:

        >>> import warnings
        >>> with warnings.catch_warnings(record=True) as w:
        ...     warnings.simplefilter("always")
        ...     el2 = doc.create_element_ns("svg", "http://www.w3.org/2000/svg")
        ...     assert len(w) == 1
        ...     assert issubclass(w[0].category, DeprecationWarning)
        ...     assert "argument order has changed" in str(w[0].message)
        >>> el2.local_name
        'svg'
        >>> el2.namespace_uri
        'http://www.w3.org/2000/svg'
        """
        import warnings

        from aspose_html.dom._element import Element

        # Detect old calling convention: first arg is a tag name (no slash),
        # second arg looks like a URI (contains ":/").
        # See ADR-023 for heuristic rationale.
        if "/" not in namespace_uri and ":/" in qualified_name:
            warnings.warn(
                "create_element_ns() argument order has changed: "
                "use create_element_ns(namespace_uri, qualified_name). "
                "The old order create_element_ns(tag, namespace_uri) is deprecated "
                "and will be removed in a future version.",
                DeprecationWarning,
                stacklevel=2,
            )
            namespace_uri, qualified_name = qualified_name, namespace_uri

        # WHATWG DOM §4.6: split qualified name on first ':' to obtain prefix
        # and local name.  Unqualified names (no colon) have prefix=None.
        if ":" in qualified_name:
            prefix, local_name = qualified_name.split(":", 1)
        else:
            prefix, local_name = None, qualified_name

        return Element(
            local_name,
            namespace_uri=namespace_uri,
            prefix=prefix,
            owner_document=self,
        )

    def create_text_node(self, data: str) -> Text:
        """Create a Text node with the given character data.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> t = doc.create_text_node("hello")
        >>> t.data
        'hello'
        """
        from aspose_html.dom._character_data import Text

        return Text(data, owner_document=self)

    def create_comment(self, data: str) -> Comment:
        """Create a Comment node with the given character data.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> c = doc.create_comment("a note")
        >>> c.data
        'a note'
        """
        from aspose_html.dom._character_data import Comment

        return Comment(data, owner_document=self)

    def create_cdata_section(self, data: str) -> "CDATASection":
        """Create a CDATASection node owned by this document.

        Implements WHATWG DOM §5.2.

        Parameters
        ----------
        data : str
            Character data for the CDATA section.

        Returns
        -------
        CDATASection
            New node with ``node_type == NodeType.CDATA_SECTION_NODE``
            and ``owner_document is self``.

        Raises
        ------
        InvalidCharacterError
            If *data* contains the sequence ``']]>'``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> cds = doc.create_cdata_section("some data")
        >>> cds.data
        'some data'
        >>> cds.owner_document is doc
        True
        >>> cds.node_type
        4
        """
        if "]]>" in data:
            raise InvalidCharacterError(
                "CDATASection data must not contain ']]>'."
            )
        from aspose_html.dom._character_data import CDATASection  # noqa: PLC0415

        return CDATASection(data, owner_document=self)

    def create_document_fragment(self) -> DocumentFragment:
        """Create an empty DocumentFragment owned by this document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> frag = doc.create_document_fragment()
        >>> frag.node_type
        11
        """
        from aspose_html.dom._document_fragment import DocumentFragment

        return DocumentFragment(owner_document=self)

    def create_event(self, interface: str) -> "Event":
        """Create a legacy event object for *interface*.

        Supported interfaces (case-insensitive): ``"Event"``, ``"Events"``,
        ``"CustomEvent"``, ``"UIEvent"``, ``"MouseEvent"``, ``"MouseEvents"``,
        ``"KeyboardEvent"``, ``"FocusEvent"``, ``"InputEvent"``, and
        ``"ErrorEvent"``.

        Examples
        --------
        >>> from aspose_html.dom import CustomEvent, Document, Event
        >>> from aspose_html.dom import UIEvent, MouseEvent, KeyboardEvent
        >>> from aspose_html.dom import FocusEvent, InputEvent, ErrorEvent
        >>> doc = Document()
        >>> isinstance(doc.create_event("Event"), Event)
        True
        >>> isinstance(doc.create_event("CustomEvent"), CustomEvent)
        True
        >>> isinstance(doc.create_event("UIEvent"), UIEvent)
        True
        >>> isinstance(doc.create_event("MouseEvent"), MouseEvent)
        True
        >>> isinstance(doc.create_event("KeyboardEvent"), KeyboardEvent)
        True
        >>> isinstance(doc.create_event("FocusEvent"), FocusEvent)
        True
        >>> isinstance(doc.create_event("InputEvent"), InputEvent)
        True
        >>> isinstance(doc.create_event("ErrorEvent"), ErrorEvent)
        True
        """
        from aspose_html.dom._event import (  # noqa: PLC0415
            CustomEvent,
            ErrorEvent,
            Event,
            FocusEvent,
            InputEvent,
            KeyboardEvent,
            MouseEvent,
            UIEvent,
        )

        normalized = interface.strip().lower()
        if normalized in {"event", "events", "htmlevents"}:
            return Event("")
        if normalized == "customevent":
            return CustomEvent("")
        if normalized == "uievent":
            return UIEvent("")
        if normalized in {"mouseevent", "mouseevents"}:
            return MouseEvent("")
        if normalized == "keyboardevent":
            return KeyboardEvent("")
        if normalized == "focusevent":
            return FocusEvent("")
        if normalized == "inputevent":
            return InputEvent("")
        if normalized == "errorevent":
            return ErrorEvent("")
        raise NotSupportedError(
            f"Event interface {interface!r} is not supported by create_event()."
        )

    def create_range(self) -> "Range":
        """Create a new Range collapsed at this document.

        The returned range has both boundary points at ``(self, 0)``.

        Returns
        -------
        Range
            A collapsed range anchored to this document.

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
        from aspose_html.dom._range import Range  # noqa: PLC0415  # See ADR-044: lazy import to avoid circular dependency
        return Range(self)

    def get_selection(self) -> "Selection":
        """Return this document's singleton selection object.

        The same :class:`~aspose_html.dom.Selection` instance is returned on
        every call.

        Returns
        -------
        Selection
            This document-scoped selection singleton.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> s1 = doc.get_selection()
        >>> s2 = doc.get_selection()
        >>> s1 is s2
        True
        """
        return self._selection

    def create_processing_instruction(
        self, target: str, data: str
    ) -> "ProcessingInstruction":
        """Create a ProcessingInstruction node owned by this document.

        Implements WHATWG DOM §5.2.

        Validation (raises ``InvalidCharacterError``):
        - *target* must not contain ``':'`` (simplified XML Name check for v1).
        - *data* must not contain the sequence ``'?>'``.

        Parameters
        ----------
        target : str
            The PI target string.  Must be a valid XML Name without a colon.
        data : str
            The PI data string.  Must not contain ``'?>'``.

        Returns
        -------
        ProcessingInstruction
            A new node with ``target``, ``data``, and ``owner_document == self``.

        Raises
        ------
        InvalidCharacterError
            If *target* contains ``':'`` or *data* contains ``'?>'``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> pi = doc.create_processing_instruction("xml-stylesheet", 'href="a.css"')
        >>> pi.target
        'xml-stylesheet'
        >>> pi.data
        'href="a.css"'
        >>> pi.owner_document is doc
        True
        """
        # NFR-1: lazy import to avoid circular dependency — See ADR-034
        from aspose_html.dom._processing_instruction import ProcessingInstruction  # noqa: PLC0415

        if ":" in target:
            raise InvalidCharacterError(
                f"ProcessingInstruction target {target!r} must not contain ':'."
            )
        if "?>" in data:
            raise InvalidCharacterError(
                "ProcessingInstruction data must not contain '?>'."
            )
        return ProcessingInstruction(target, data, owner_document=self)

    def create_attribute(self, local_name: str) -> "Attr":
        """Create a non-namespaced ``Attr`` owned by this document.

        Parameters
        ----------
        local_name : str
            Attribute local name for the null namespace.

        Returns
        -------
        Attr
            An unattached attribute node with null namespace semantics.

        Raises
        ------
        InvalidCharacterError
            If *local_name* is empty, contains whitespace, or contains ``':'``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> attr = doc.create_attribute("data-id")
        >>> attr.name
        'data-id'
        >>> attr.namespace_uri is None
        True
        >>> attr.owner_element is None
        True
        >>> attr.owner_document is doc
        True
        """
        from aspose_html.dom._attr import Attr  # noqa: PLC0415

        if local_name == "":
            raise InvalidCharacterError("Attribute local_name must not be empty.")
        if any(ch.isspace() for ch in local_name):
            raise InvalidCharacterError("Attribute local_name must not contain whitespace.")
        if ":" in local_name:
            raise InvalidCharacterError("Attribute local_name must not contain ':'.")

        return Attr(
            local_name,
            "",
            owner_element=None,
            owner_document=self,
            namespace_uri=None,
            local_name_ns=local_name,
        )

    def create_attribute_ns(
        self,
        namespace_uri: str | None,
        qualified_name: str,
    ) -> "Attr":
        """Create a new namespaced ``Attr`` owned by this document.

        The returned ``Attr`` is not attached to any element; pass it to
        :meth:`~aspose_html.dom.Element.set_attribute_node` or use
        :meth:`~aspose_html.dom.Element.set_attribute_ns` directly.

        Parameters
        ----------
        namespace_uri : str or None
            The namespace URI, or ``None`` for the null namespace.
        qualified_name : str
            The qualified attribute name, e.g. ``"xlink:href"``.

        Returns
        -------
        Attr
            An unattached namespaced attribute node owned by this document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> attr = doc.create_attribute_ns("http://www.w3.org/1999/xlink", "xlink:href")
        >>> attr.namespace_uri
        'http://www.w3.org/1999/xlink'
        >>> attr.local_name
        'href'
        >>> attr.name
        'xlink:href'
        >>> attr.value
        ''
        >>> attr.owner_element is None
        True
        """
        from aspose_html.dom._attr import Attr  # noqa: PLC0415

        local_name = qualified_name.split(":", 1)[1] if ":" in qualified_name else qualified_name
        return Attr(
            qualified_name,
            "",
            owner_element=None,
            owner_document=self,
            namespace_uri=namespace_uri,
            local_name_ns=local_name,
        )

    # ------------------------------------------------------------------
    # Traversal factory methods  # See ADR-043
    # ------------------------------------------------------------------

    def create_tree_walker(
        self,
        root: "Node",
        what_to_show: int = 0xFFFFFFFF,
        node_filter: "Callable[[Node], int] | None" = None,
    ) -> "TreeWalker":
        """Create a TreeWalker for filtered cursor-style DOM traversal.

        Per WHATWG DOM §6.3.

        Parameters
        ----------
        root : Node
            The root of the traversal.  ``current_node`` starts at *root*.
        what_to_show : int
            Bitmask of ``NodeFilter.SHOW_*`` constants. Default: ``SHOW_ALL``.
        node_filter : callable or None
            A callable accepting a ``Node`` and returning
            ``NodeFilter.FILTER_ACCEPT``, ``FILTER_REJECT``, or
            ``FILTER_SKIP``.  ``None`` means accept all.

        Returns
        -------
        TreeWalker

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> walker = doc.create_tree_walker(el, NodeFilter.SHOW_ELEMENT)
        >>> walker.current_node is el
        True
        """
        from aspose_html.dom._traversal import TreeWalker  # noqa: PLC0415  lazy import — avoid circular
        return TreeWalker(root, what_to_show, node_filter)

    def create_node_iterator(
        self,
        root: "Node",
        what_to_show: int = 0xFFFFFFFF,
        node_filter: "Callable[[Node], int] | None" = None,
    ) -> "NodeIterator":
        """Create a NodeIterator for flat filtered DOM traversal.

        Per WHATWG DOM §6.2.

        Parameters
        ----------
        root : Node
            The root of the iteration.
        what_to_show : int
            Bitmask of ``NodeFilter.SHOW_*`` constants. Default: ``SHOW_ALL``.
        node_filter : callable or None
            Callable returning ``FILTER_ACCEPT``, ``FILTER_REJECT``, or
            ``FILTER_SKIP``.

        Returns
        -------
        NodeIterator

        Examples
        --------
        >>> from aspose_html.dom import Document, NodeFilter
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> it = doc.create_node_iterator(el, NodeFilter.SHOW_TEXT)
        >>> it.reference_node is el
        True
        """
        from aspose_html.dom._traversal import NodeIterator  # noqa: PLC0415  lazy import — avoid circular
        return NodeIterator(root, what_to_show, node_filter)

    # ------------------------------------------------------------------
    # Cross-document node operations  # See ADR-026
    # ------------------------------------------------------------------

    def adopt_node(self, node: Node) -> Node:
        """Adopt *node* into this document, moving it from its current tree.

        Per WHATWG DOM §5.3.8:

        1. Raises ``NotSupportedError`` if *node* is a ``Document``.
        2. If *node* has a parent, removes it from its parent via
           ``parent.remove_child(node)``.
        3. Recursively sets ``_owner_document`` on *node* and all its
           descendants to ``self``.
        4. Returns *node*.

        After ``adopt_node``, the node can be appended to this document
        without raising ``WrongDocumentError``.

        Parameters
        ----------
        node : Node
            The node to adopt. Must not be a ``Document``.

        Returns
        -------
        Node
            The same *node* object, now owned by this document.

        Raises
        ------
        NotSupportedError
            If *node* is a ``Document``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> src = Document()
        >>> dst = Document()
        >>> el = src.create_element("div")
        >>> src.append_child(el)
        <Element 'DIV'>
        >>> adopted = dst.adopt_node(el)
        >>> adopted is el
        True
        >>> el.owner_document is dst
        True
        >>> el.parent_node is None
        True
        """
        # INV-005: WHATWG DOM §5.3.8 — Document nodes cannot be adopted.
        if node._node_type == NodeType.DOCUMENT_NODE:
            raise NotSupportedError("Adopting a Document node is not supported.")
        old_doc = node._owner_document
        if node._parent is not None:
            node._parent.remove_child(node)
        # INV-005: _adopt() recursively repoints _owner_document (ADR-026).
        _adopt(node, self)
        if old_doc is not None and old_doc is not self:
            new_win = self._get_cached_default_view()
            if new_win is not None and new_win._custom_elements is not None:
                stack = [node]
                while stack:
                    n = stack.pop(0)
                    if n._node_type == NodeType.ELEMENT_NODE:
                        new_win._custom_elements._fire_adopted(n, old_doc, self)
                    stack[0:0] = list(n._children)
        return node

    def import_node(self, node: Node, deep: bool = False) -> Node:
        """Return a clone of *node* owned by this document.

        Per WHATWG DOM §5.3.6:

        1. Raises ``NotSupportedError`` if *node* is a ``Document``.
        2. Clones *node* via ``node.clone_node(deep)``.
        3. Adopts the clone into this document via ``self.adopt_node(clone)``.
        4. Returns the adopted clone.

        The original tree is not modified. The returned node has no parent.

        Parameters
        ----------
        node : Node
            The node to import. Must not be a ``Document``.
        deep : bool, optional
            If ``True``, recursively clone the entire subtree. Defaults to
            ``False``.

        Returns
        -------
        Node
            A new node (and optionally subtree) owned by this document,
            not yet inserted anywhere.

        Raises
        ------
        NotSupportedError
            If *node* is a ``Document``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> src = Document()
        >>> dst = Document()
        >>> el = src.create_element("p")
        >>> src.append_child(el)
        <Element 'P'>
        >>> clone = dst.import_node(el, deep=False)
        >>> clone is el
        False
        >>> clone.owner_document is dst
        True
        >>> el.parent_node is not None
        True
        """
        # INV-005: WHATWG DOM §5.3.6 — check before clone_node to avoid
        # wasting work on a doomed operation (ADR-026).
        if node._node_type == NodeType.DOCUMENT_NODE:
            raise NotSupportedError("Importing a Document node is not supported.")
        clone = node.clone_node(deep)
        # adopt_node recursively repoints _owner_document; clone has no parent
        # so the parent-removal step inside adopt_node is a no-op.
        return self.adopt_node(clone)

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def get_element_by_id(self, id: str) -> Element | None:
        """Return the first element with attribute ``id`` matching *id*.

        Uses an ``O(1)`` internal map maintained by ``_register_id`` /
        ``_unregister_id``.  Returns ``None`` if no match.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("id", "main")
        >>> doc.append_child(el)
        <Element 'DIV' id='main'>
        >>> doc.get_element_by_id("main") is el
        True
        >>> doc.get_element_by_id("nope") is None
        True
        """
        return self._id_map.get(id)

    def get_elements_by_tag_name(self, name: str) -> HTMLCollection:
        """Return all descendant elements with the given tag name.

        ``'*'`` matches all elements.  The comparison is case-insensitive.

        Returns a live collection that re-scans the subtree on access.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> doc.append_child(el)
        <Element 'P'>
        >>> len(doc.get_elements_by_tag_name("p"))
        1
        >>> len(doc.get_elements_by_tag_name("*"))
        1
        """
        if name == "*":
            filter_fn = lambda el: True  # noqa: E731
        else:
            name_lower = name.lower()
            filter_fn = lambda el: el._local_name == name_lower  # type: ignore[union-attr] # noqa: E731
        return _SubtreeHTMLCollection(self, filter_fn)  # type: ignore[return-value]

    def get_elements_by_class_name(self, names: str) -> HTMLCollection:
        """Return all descendant elements with all of the given class names.

        *names* is a space-separated string of class tokens.

        Returns a live collection that re-scans the subtree on access.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "a b")
        >>> doc.append_child(el)
        <Element 'DIV' class='a b'>
        >>> len(doc.get_elements_by_class_name("a"))
        1
        >>> len(doc.get_elements_by_class_name("a b"))
        1
        >>> len(doc.get_elements_by_class_name("c"))
        0
        """
        class_set = set(names.split())

        def filter_fn(el: Element) -> bool:
            return class_set.issubset(set(el.class_list))  # type: ignore[attr-defined]

        return _SubtreeHTMLCollection(self, filter_fn)  # type: ignore[return-value]

    def get_elements_by_name(self, name: str) -> NodeList:
        """Return all descendant elements whose ``name`` attribute equals *name*.

        The comparison is case-sensitive per WHATWG HTML §3.2.8.  All element
        types are included (not just form controls).  The returned
        ``_SubtreeHTMLCollection`` re-scans the subtree on every access, so it
        reflects DOM mutations immediately (live semantics).

        An empty ``_SubtreeHTMLCollection`` is returned when no elements match.
        The result is always a collection object, never a plain list.

        Parameters
        ----------
        name : str
            The exact value of the ``name`` attribute to match.  Case-sensitive.

        Returns
        -------
        NodeList
            A live collection of all matching elements in document order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> inp.set_attribute("name", "q")
        >>> _ = doc.append_child(inp)
        >>> coll = doc.get_elements_by_name("q")
        >>> len(coll)
        1
        >>> coll[0] is inp
        True
        >>> len(doc.get_elements_by_name("missing"))
        0
        """
        # INV-005: WHATWG HTML §3.2.8 — live collection, case-sensitive name match.
        return _SubtreeHTMLCollection(  # type: ignore[return-value]
            self,
            lambda el: el.get_attribute("name") == name,  # type: ignore[union-attr]
        )

    @property
    def compatible_mode(self) -> str:
        """Quirks-mode indicator (WHATWG HTML §3.2.1).

        Returns ``'CSS1Compat'`` for standards-mode documents and
        ``'BackCompat'`` for quirks-mode documents. All documents produced
        by this library are in standards mode (the parser always sets
        a ``<!DOCTYPE html>`` baseline).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().compatible_mode
        'CSS1Compat'
        """
        return "CSS1Compat"

    @property
    def strict_error_checking(self) -> bool:
        """Always ``True`` in headless mode (DOM3 Core §1.1.1).

        DOM3 Core §1.1.1 defines ``strictErrorChecking`` as a flag that, when
        ``False``, allows implementations to skip certain validation checks.
        This headless implementation always validates, so the flag is always
        ``True``. The setter is present for DOM3 Core compliance but is a no-op.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().strict_error_checking
        True
        """
        return True

    @strict_error_checking.setter
    def strict_error_checking(self, value: bool) -> None:
        """No-op — strict error checking is always enabled in headless mode.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document()
        >>> doc.strict_error_checking = False  # must not raise
        >>> doc.strict_error_checking
        True
        """

    def get_elements_by_tag_name_ns(
        self, namespace: "str | None", local_name: str
    ) -> list:
        """Return all descendant elements matching namespace and local name.

        Per WHATWG DOM §4.5. ``'*'`` for either argument matches all values.
        For HTML-namespace elements the local name comparison is
        case-insensitive.

        Parameters
        ----------
        namespace:
            Namespace URI to match, or ``'*'`` for any namespace, or
            ``None`` for the null namespace.
        local_name:
            Local name to match, or ``'*'`` for any local name.

        Returns
        -------
        list
            All matching descendant elements in tree order.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document()
        >>> p = doc.create_element("p")
        >>> _ = doc.append_child(p)
        >>> results = doc.get_elements_by_tag_name_ns('*', 'p')
        >>> len(results)
        1
        >>> results[0] is p
        True
        >>> doc.get_elements_by_tag_name_ns('*', '*') == [p]
        True
        """
        results: list = []
        _collect_elements_by_ns(self, namespace, local_name.lower(), results)
        return results

    # ------------------------------------------------------------------
    # ParentNode mixin (WHATWG DOM §4.2.6)
    # ------------------------------------------------------------------

    def prepend(self, *nodes: "Node | str") -> None:
        """Insert *nodes* before the first child of this document.

        Strings are converted to Text nodes via ``self.create_text_node()``.
        No-op if *nodes* is empty.

        Per WHATWG DOM §4.2.6 ParentNode.prepend().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("html")
        >>> doc.prepend(el)
        >>> doc.first_child is el
        True
        """
        if not nodes:
            return
        coerced = _coerce_nodes(nodes, self)
        first = self.first_child
        for node in coerced:
            self.insert_before(node, first)

    def append(self, *nodes: "Node | str") -> None:
        """Append *nodes* as the last children of this document.

        Strings are converted to Text nodes via ``self.create_text_node()``.
        No-op if *nodes* is empty.

        Per WHATWG DOM §4.2.6 ParentNode.append().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("html")
        >>> doc.append(el)
        >>> doc.last_child is el
        True
        """
        if not nodes:
            return
        coerced = _coerce_nodes(nodes, self)
        for node in coerced:
            self.append_child(node)

    def replace_children(self, *nodes: "Node | str") -> None:
        """Remove all children of this document, then append *nodes*.

        Strings are converted to Text nodes via ``self.create_text_node()``.
        Calling with no arguments removes all children.

        Per WHATWG DOM §4.2.6 ParentNode.replaceChildren().

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("html")
        >>> _ = doc.append_child(el)
        >>> doc.replace_children()
        >>> len(doc.child_nodes)
        0
        """
        for child in list(self._children):
            self.remove_child(child)
        coerced = _coerce_nodes(nodes, self)
        for node in coerced:
            self.append_child(node)

    def query_selector(self, selector: str) -> Element | None:
        """Return the first element matching the CSS selector, or ``None``.

        Delegates to ``aspose_html.css.select`` (lazy import, available
        after BACK-7/BACK-8 are implemented).

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> doc.query_selector("p")  # doctest: +SKIP
        """
        from aspose_html.css import select  # lazy import
        results = select(self, selector, first_only=True)
        return results[0] if results else None

    def query_selector_all(self, selector: str) -> NodeList:
        """Return a static NodeList of all elements matching the CSS selector.

        Examples
        --------
        >>> from aspose_html.dom import Document  # doctest: +SKIP
        >>> doc = Document()  # doctest: +SKIP
        >>> doc.query_selector_all("p")  # doctest: +SKIP
        """
        from aspose_html.css import select  # lazy import
        results = select(self, selector, first_only=False)
        return _StaticNodeList(results)

    # ------------------------------------------------------------------
    # ParentNode element-child properties (WHATWG DOM §4.2.6)
    # ------------------------------------------------------------------

    @property
    def first_element_child(self) -> "Element | None":
        """First direct child that is an Element, or ``None``.

        WHATWG DOM §4.2.6 ParentNode mixin — same semantics as on
        ``Element``, applied to the Document's direct children.

        For a standard HTML document this returns the ``<html>`` root element.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse("<html><body></body></html>")
        >>> doc.first_element_child.tag_name
        'HTML'
        """
        for child in self._children:
            if child._node_type == NodeType.ELEMENT_NODE:
                return child  # type: ignore[return-value]
        return None

    @property
    def last_element_child(self) -> "Element | None":
        """Last direct child that is an Element, or ``None``.

        WHATWG DOM §4.2.6 ParentNode mixin — same semantics as on
        ``Element``, applied to the Document's direct children.

        For a standard HTML document this returns the ``<html>`` root element
        (the only element child at the document level).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse("<html><body></body></html>")
        >>> doc.last_element_child.tag_name
        'HTML'
        """
        result = None
        for child in self._children:
            if child._node_type == NodeType.ELEMENT_NODE:
                result = child
        return result  # type: ignore[return-value]

    @property
    def child_element_count(self) -> int:
        """Number of direct children that are Element nodes.

        WHATWG DOM §4.2.6 ParentNode mixin.

        For a standard HTML document this is ``1`` (the ``<html>`` root).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse("<html><body></body></html>")
        >>> doc.child_element_count
        1
        """
        return sum(
            1 for child in self._children
            if child._node_type == NodeType.ELEMENT_NODE
        )

    @property
    def active_element(self) -> "Element | None":
        """The currently focused element, always ``None`` in headless mode.

        WHATWG HTML §7.10.3 — there is no focus model in headless mode.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse("<html><body><input></body></html>")
        >>> doc.active_element is None
        True
        """
        return None

    def get_animations(self) -> list[object]:
        """Return document-level animations (headless stub: always ``[]``).

        This runtime does not implement a rendering/animation pipeline, so
        there are never active animations to report.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.get_animations()
        []
        """
        return []

    # ------------------------------------------------------------------
    # Track 102 — Document IDL tail (BACK-323 / ADR-301)
    # ------------------------------------------------------------------

    @property
    def full_screen_enabled(self) -> bool:
        """Always ``False`` — no display in headless mode (Fullscreen API §7).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().full_screen_enabled
        False
        """
        return False

    @property
    def fullscreen_element(self) -> None:
        """Always ``None`` — no fullscreen element in headless mode (Fullscreen API §7).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().fullscreen_element is None
        True
        """
        return None

    @property
    def pointer_lock_element(self) -> None:
        """Always ``None`` — no pointer lock in headless mode (Pointer Lock API §4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().pointer_lock_element is None
        True
        """
        return None

    def element_from_point(self, x: float, y: float) -> None:
        """Always ``None`` — headless has no layout engine for hit testing (CSSOM View §11.6).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().element_from_point(0, 0) is None
        True
        """
        return None

    def elements_from_point(self, x: float, y: float) -> list:
        """Always ``[]`` — headless has no layout engine for hit testing (CSSOM View §11.6).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().elements_from_point(0, 0)
        []
        """
        return []

    def exec_command(self, command_id: str, show_ui: bool = False,
                     value: str = "") -> bool:
        """Always ``False`` — legacy editing command; no pipeline in headless (WHATWG HTML §8.6.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().exec_command('bold')
        False
        """
        return False

    def query_command_enabled(self, command_id: str) -> bool:
        """Always ``False`` — no editing pipeline in headless (WHATWG HTML §8.6.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().query_command_enabled('bold')
        False
        """
        return False

    @property
    def timeline(self) -> "_DocumentTimeline":
        """Document timeline stub; ``current_time`` is always ``0.0`` (Web Animations API §6.2).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().timeline.current_time
        0.0
        """
        return _DocumentTimeline()

    def has_storage_access(self) -> bool:
        """Always ``True`` — headless origin is treated as same-origin (Storage Access API).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().has_storage_access()
        True
        """
        return True

    def request_storage_access(self) -> None:
        """No-op stub — headless always has storage access; no async grant needed (Storage Access API).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().request_storage_access() is None
        True
        """

    @property
    def all(self) -> "_AllCollection":
        """All elements in tree order (WHATWG HTML §legacy document layout interface).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse('<html><body><p>Hi</p></body></html>')
        >>> len(doc.all) > 0
        True
        """
        return _AllCollection(self)

    @property
    def plugins(self) -> "HTMLCollection":
        """Alias for :attr:`embeds` per WHATWG HTML §4.1 legacy interface.

        Returns the same live ``<embed>`` element collection as :attr:`embeds`.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse('<html><body></body></html>')
        >>> len(doc.plugins) == len(doc.embeds)
        True
        """
        return self.embeds

    @property
    def children(self) -> "HTMLCollection":
        """Direct element children of the document (WHATWG DOM §4.2.6 ParentNode).

        For a standard HTML document, returns an HTMLCollection containing
        the single ``<html>`` element.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse('<html><body></body></html>')
        >>> len(doc.children) == 1
        True
        >>> doc.children[0].tag_name
        'HTML'
        """
        kids = [c for c in self._children if c._node_type == NodeType.ELEMENT_NODE]
        return HTMLCollection(kids)

    # ------------------------------------------------------------------
    # Track 112 — Document IDL tail (BACK-333 / ADR-311)
    # ------------------------------------------------------------------

    @property
    def origin(self) -> str:
        """Opaque origin string — always ``'null'`` in headless mode (WHATWG DOM §4.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().origin
        'null'
        """
        return "null"

    @property
    def fg_color(self) -> str:
        """Reflects obsolete ``fgColor`` document-level attribute via ``<body>`` ``text`` attribute.

        Per WHATWG HTML §15.3.1. Returns ``''`` when no ``<body>`` element exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.fg_color
        ''
        """
        body = self.body
        return (body.get_attribute("text") or "") if body is not None else ""

    @fg_color.setter
    def fg_color(self, value: str) -> None:
        body = self.body
        if body is not None:
            body.set_attribute("text", value)

    @property
    def bg_color(self) -> str:
        """Reflects obsolete ``bgColor`` document-level attribute via ``<body>`` ``bgcolor`` attribute.

        Per WHATWG HTML §15.3.1. Returns ``''`` when no ``<body>`` element exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.bg_color
        ''
        """
        body = self.body
        return (body.get_attribute("bgcolor") or "") if body is not None else ""

    @bg_color.setter
    def bg_color(self, value: str) -> None:
        body = self.body
        if body is not None:
            body.set_attribute("bgcolor", value)

    @property
    def link_color(self) -> str:
        """Reflects obsolete ``linkColor`` document-level attribute via ``<body>`` ``link`` attribute.

        Per WHATWG HTML §15.3.1. Returns ``''`` when no ``<body>`` element exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.link_color
        ''
        """
        body = self.body
        return (body.get_attribute("link") or "") if body is not None else ""

    @link_color.setter
    def link_color(self, value: str) -> None:
        body = self.body
        if body is not None:
            body.set_attribute("link", value)

    @property
    def v_link_color(self) -> str:
        """Reflects obsolete ``vlinkColor`` document-level attribute via ``<body>`` ``vlink`` attribute.

        Per WHATWG HTML §15.3.1. Returns ``''`` when no ``<body>`` element exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.v_link_color
        ''
        """
        body = self.body
        return (body.get_attribute("vlink") or "") if body is not None else ""

    @v_link_color.setter
    def v_link_color(self, value: str) -> None:
        body = self.body
        if body is not None:
            body.set_attribute("vlink", value)

    @property
    def a_link_color(self) -> str:
        """Reflects obsolete ``alinkColor`` document-level attribute via ``<body>`` ``alink`` attribute.

        Per WHATWG HTML §15.3.1. Returns ``''`` when no ``<body>`` element exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.a_link_color
        ''
        """
        body = self.body
        return (body.get_attribute("alink") or "") if body is not None else ""

    @a_link_color.setter
    def a_link_color(self, value: str) -> None:
        body = self.body
        if body is not None:
            body.set_attribute("alink", value)

    # ------------------------------------------------------------------
    # Internal ID map helpers (called by Node mutation methods)
    # ------------------------------------------------------------------

    def _register_id(self, element: Element, id_value: str) -> None:
        """Register *element* under *id_value* in the internal id map.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc._register_id(el, "main")
        >>> doc.get_element_by_id("main") is el
        True
        """
        self._id_map[id_value] = element

    def _unregister_id(self, element: Element) -> None:
        """Remove *element*'s id from the map if it is currently registered.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("id", "x")
        >>> doc._register_id(el, "x")
        >>> doc._unregister_id(el)
        >>> doc.get_element_by_id("x") is None
        True
        """
        id_val = element.get_attribute("id")  # type: ignore[attr-defined]
        if id_val and self._id_map.get(id_val) is element:
            del self._id_map[id_val]

    def _walk_register_ids(self, node: Node) -> None:
        """Recursively register id attributes for *node* and its descendants."""
        if node._node_type == NodeType.ELEMENT_NODE:
            id_val = node.get_attribute("id")  # type: ignore[attr-defined]
            if id_val:
                self._id_map[id_val] = node  # type: ignore[assignment]
        for child in node._children:
            self._walk_register_ids(child)

    def _walk_unregister_ids(self, node: Node) -> None:
        """Recursively unregister id attributes for *node* and its descendants."""
        if node._node_type == NodeType.ELEMENT_NODE:
            id_val = node.get_attribute("id")  # type: ignore[attr-defined]
            if id_val and self._id_map.get(id_val) is node:
                del self._id_map[id_val]
        for child in node._children:
            self._walk_unregister_ids(child)

    # ------------------------------------------------------------------
    # Hierarchy validation
    # ------------------------------------------------------------------

    def _validate_insertion(
        self, node: Node, replacing: Node | None = None
    ) -> None:
        super()._validate_insertion(node, replacing)
        nt = node._node_type

        if nt == NodeType.ELEMENT_NODE:
            existing = self.document_element
            if existing is not None and existing is not replacing:
                raise HierarchyRequestError(
                    "Document can only have one Element child."
                )
        elif nt == NodeType.DOCUMENT_TYPE_NODE:
            existing_dt = self.document_type
            if existing_dt is not None and existing_dt is not replacing:
                raise HierarchyRequestError(
                    "Document can only have one DocumentType child."
                )
        elif nt == NodeType.DOCUMENT_FRAGMENT_NODE:
            # Validate that the fragment's children would not violate rules.
            frag_elements = [
                c for c in node._children if c._node_type == NodeType.ELEMENT_NODE
            ]
            frag_doctypes = [
                c for c in node._children if c._node_type == NodeType.DOCUMENT_TYPE_NODE
            ]
            if len(frag_elements) > 1:
                raise HierarchyRequestError(
                    "Fragment contains more than one Element."
                )
            if len(frag_doctypes) > 1:
                raise HierarchyRequestError(
                    "Fragment contains more than one DocumentType."
                )
            if frag_elements and self.document_element is not None:
                raise HierarchyRequestError(
                    "Document already has an Element child."
                )
            if frag_doctypes and self.document_type is not None:
                raise HierarchyRequestError(
                    "Document already has a DocumentType child."
                )
            # Also check for invalid node types in the fragment.
            for c in node._children:
                ct = c._node_type
                if ct not in (
                    NodeType.ELEMENT_NODE,
                    NodeType.DOCUMENT_TYPE_NODE,
                    NodeType.COMMENT_NODE,
                    NodeType.PROCESSING_INSTRUCTION_NODE,
                ):
                    raise HierarchyRequestError(
                        f"Document cannot contain node type {ct} from fragment."
                    )
        elif nt not in (
            NodeType.COMMENT_NODE,
            NodeType.PROCESSING_INSTRUCTION_NODE,
        ):
            raise HierarchyRequestError(
                f"Document cannot contain node type {nt}."
            )

    # ------------------------------------------------------------------
    # Track 114 — Document IDL tail (BACK-335 / ADR-313)
    # ------------------------------------------------------------------

    @property
    def fonts(self):
        """Always ``None`` in headless mode.

        WHATWG HTML §8.6 — the document's ``FontFaceSet``. No font loading
        pipeline is available in headless execution.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().fonts is None
        True
        """
        return None

    @property
    def picture_in_picture_enabled(self) -> bool:
        """Always ``False`` in headless mode.

        Picture-in-Picture API — no video rendering context available.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().picture_in_picture_enabled
        False
        """
        return False

    @property
    def picture_in_picture_element(self):
        """Always ``None`` in headless mode.

        Picture-in-Picture API — no video rendering context available.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().picture_in_picture_element is None
        True
        """
        return None

    @property
    def prerendering(self) -> bool:
        """Always ``False`` in headless mode.

        WHATWG HTML §7.6 — True only when the document is being prerendered.
        Headless execution is never a prerender context.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().prerendering
        False
        """
        return False

    # ------------------------------------------------------------------
    # Clone
    # ------------------------------------------------------------------

    def _clone_self(self) -> Document:
        clone = Document()
        clone._compat_mode = self._compat_mode
        return clone

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"<Document compat_mode={self._compat_mode!r}>"

    __str__ = __repr__


# Alias types for use in type annotations without circular imports.
from aspose_html.dom._character_data import Text, Comment  # noqa: E402
from aspose_html.dom._document_type import DocumentType  # noqa: E402
from aspose_html.dom._document_fragment import DocumentFragment  # noqa: E402
