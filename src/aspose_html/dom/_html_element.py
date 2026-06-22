"""HTMLElement — base class for all HTML-namespace DOM elements.

All elements in the HTML namespace (http://www.w3.org/1999/xhtml) that are
created by ``Document.create_element()`` are instances of ``HTMLElement`` or
one of its subclasses.

``HTMLElement`` adds no instance attributes; ``__slots__ = ()`` explicitly
opts in to the slots protocol without introducing a ``__dict__``.

INV-001: Class name ``HTMLElement`` matches the .NET Aspose.HTML class name.
"""
from __future__ import annotations

import re

from aspose_html.dom._element import Element

_CONTENT_EDITABLE_VALID = frozenset({"true", "false", "inherit", "plaintext-only"})


class HTMLElement(Element):
    """Base class for all HTML-namespace element types.

    All elements in the HTML namespace (http://www.w3.org/1999/xhtml) that
    are created by ``Document.create_element()`` are instances of
    ``HTMLElement`` or one of its subclasses.

    ``HTMLElement`` adds no new instance attributes; ``__slots__ = ()``
    explicitly opts in to the slots protocol without introducing a
    ``__dict__``.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLElement, Element
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> isinstance(el, HTMLElement)
    True
    >>> isinstance(el, Element)
    True
    """

    # INV-001: no rename permitted — HTMLElement matches Aspose.HTML .NET API.
    # No new instance attributes in v1.0 — foundation for BACK-16 subclasses.
    __slots__ = ()

    # ------------------------------------------------------------------
    # Clone — resolves SINV-001
    # ------------------------------------------------------------------

    def _clone_self(self) -> "HTMLElement":
        """Clone this element, preserving its concrete subclass.  # See ADR-012

        Dispatches through ``owner_document.create_element()`` so that the
        result is the correct registered subclass (e.g. ``HTMLAnchorElement``
        rather than a plain ``Element``).  Attributes are then copied from
        the original using namespace-aware dispatch (BACK-48 / ADR-041):
        namespaced attributes are copied via ``set_attribute_ns()`` to preserve
        ``_namespace_uri`` and ``_local_name_ns``; plain attributes via
        ``set_attribute()``.  This fixes the SINV-002 defect where all
        attributes were routed through ``set_attribute()``, silently discarding
        namespace metadata and causing ``get_attribute_ns()`` to return ``None``
        on the clone.

        For detached elements (no owner document) falls back to direct
        construction via ``type(self)(...)`` so that the concrete subclass
        is still preserved.  # INV-005: clone must preserve subclass identity

        Lazy-initialised slots (``_class_list``, ``_style_declaration``,
        ``_dataset``) and ``_event_listeners`` are **not** copied — they are
        reset to ``None`` by the element constructor and recreated independently
        on first access on the clone.

        Not part of the public API.  Called by ``Node.clone_node()``.
        """
        doc = self._owner_document
        if doc is not None:
            # Use the registry — correct subclass is returned automatically.
            # See ADR-012 (SINV-001 resolution).
            clone = doc.create_element(self._local_name)
        else:
            # Detached element — fall back to direct construction so that the
            # concrete subclass is preserved without a document reference.
            clone = type(self)(
                self._local_name,
                namespace_uri=self._namespace_uri,
                prefix=self._prefix,
                owner_document=None,
            )
        for attr in self._attributes:
            # INV-005: preserve namespace context per WHATWG DOM §4.5 clone algorithm.
            # set_attribute() would create a plain (non-namespaced) Attr, losing
            # _namespace_uri and _local_name_ns for namespaced attributes (SINV-002).
            if attr._namespace_uri is not None:
                clone.set_attribute_ns(attr._namespace_uri, attr.name, attr.value)  # type: ignore[union-attr]
            else:
                clone.set_attribute(attr.name, attr.value)  # type: ignore[union-attr]
        return clone  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Global reflected attribute properties (BACK-34, ADR-030)
    # ------------------------------------------------------------------

    @property
    def hidden(self) -> bool:
        """Whether the element is hidden (reflects the ``hidden`` boolean attribute).

        A hidden element is not rendered. Setting to ``True`` adds the ``hidden``
        attribute with an empty value; setting to ``False`` removes it (WHATWG
        boolean attribute pattern).  # INV-005: boolean attribute pattern

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.hidden
        False
        >>> el.hidden = True
        >>> el.get_attribute("hidden")
        ''
        >>> el.hidden = False
        >>> el.has_attribute("hidden")
        False
        """
        return self.has_attribute("hidden")

    @hidden.setter
    def hidden(self, value: bool) -> None:
        # INV-005: boolean attribute — True sets attribute to "", False removes it
        if value:
            self.set_attribute("hidden", "")
        else:
            self.remove_attribute("hidden")

    @property
    def title(self) -> str:
        """The tooltip title of this element (reflects the ``title`` attribute).

        Returns the value of the ``title`` attribute, or ``''`` if absent.
        This is the advisory tooltip title, distinct from ``Document.title``
        (which reflects the ``<title>`` element text content).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("abbr")
        >>> el.title
        ''
        >>> el.title = "World Health Organization"
        >>> el.get_attribute("title")
        'World Health Organization'
        """
        return self.get_attribute("title") or ""

    @title.setter
    def title(self, value: str) -> None:
        self.set_attribute("title", value)

    @property
    def lang(self) -> str:
        """The language of the element's content (reflects the ``lang`` attribute).

        Returns the value of the ``lang`` attribute, or ``''`` if absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("p")
        >>> el.lang
        ''
        >>> el.lang = "fr"
        >>> el.get_attribute("lang")
        'fr'
        """
        return self.get_attribute("lang") or ""

    @lang.setter
    def lang(self, value: str) -> None:
        self.set_attribute("lang", value)

    @property
    def tab_index(self) -> int:
        """The tab order index of this element (reflects the ``tabindex`` attribute).

        Returns the integer value of the ``tabindex`` attribute, or ``0`` if the
        attribute is absent (WHATWG HTML §6.6.5 default for sequential focus
        navigation).  # INV-001: snake_case tab_index corresponds to IDL tabIndex

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("button")
        >>> el.tab_index
        0
        >>> el.tab_index = 3
        >>> el.get_attribute("tabindex")
        '3'
        """
        raw = self.get_attribute("tabindex")
        if raw is None:
            return 0
        try:
            return int(raw)
        except ValueError:
            return 0

    @tab_index.setter
    def tab_index(self, value: int) -> None:
        self.set_attribute("tabindex", str(value))

    @property
    def access_key(self) -> str:
        """The keyboard shortcut key for this element (reflects the ``accesskey``
        attribute).

        Returns the value of the ``accesskey`` attribute, or ``''`` if absent.
        # INV-001: snake_case access_key corresponds to IDL accessKey

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("a")
        >>> el.access_key
        ''
        >>> el.access_key = "k"
        >>> el.get_attribute("accesskey")
        'k'
        """
        return self.get_attribute("accesskey") or ""

    @access_key.setter
    def access_key(self, value: str) -> None:
        self.set_attribute("accesskey", value)

    @property
    def content_editable(self) -> str:
        """Reflects the ``contenteditable`` attribute (WHATWG HTML §6.6).

        Returns ``"inherit"`` when the attribute is absent.
        Valid IDL values are ``"true"``, ``"false"``, ``"inherit"``, and
        ``"plaintext-only"``. Setting an invalid value raises
        :exc:`aspose_html.dom.SyntaxError`.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.content_editable
        'inherit'
        >>> el.content_editable = "true"
        >>> el.get_attribute("contenteditable")
        'true'
        """
        val = self.get_attribute("contenteditable")
        return val if val is not None else "inherit"

    @content_editable.setter
    def content_editable(self, value: str) -> None:
        if value not in _CONTENT_EDITABLE_VALID:
            from aspose_html.dom._exceptions import SyntaxError as _SyntaxError  # noqa: PLC0415
            raise _SyntaxError(
                f"Invalid contenteditable value {value!r}; must be one of "
                f"{sorted(_CONTENT_EDITABLE_VALID)}"
            )
        self.set_attribute("contenteditable", value)

    @property
    def is_content_editable(self) -> bool:
        """Whether this element is currently editable (WHATWG HTML §6.6).

        Returns ``True`` iff the element's own ``contenteditable`` attribute is
        ``"true"``. Ancestor-inherited editability is out of scope.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.is_content_editable
        False
        >>> el.content_editable = "true"
        >>> el.is_content_editable
        True
        """
        return self.get_attribute("contenteditable") == "true"

    @property
    def dir(self) -> str:
        """Text directionality of the element (reflects the ``dir`` attribute).

        Returns the value of the ``dir`` attribute, or ``''`` when absent.
        Valid hint values are ``"ltr"``, ``"rtl"``, ``"auto"``, and ``""``,
        but no validation is applied on set.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("p")
        >>> el.dir
        ''
        >>> el.dir = "rtl"
        >>> el.get_attribute("dir")
        'rtl'
        """
        return self.get_attribute("dir") or ""

    @dir.setter
    def dir(self, value: str) -> None:
        self.set_attribute("dir", value)

    @property
    def draggable(self) -> bool:
        """Whether the element is draggable (reflects the ``draggable`` attribute).

        Returns ``True`` when the attribute value is exactly ``"true"``,
        ``False`` otherwise (including when the attribute is absent).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("img")
        >>> el.draggable
        False
        >>> el.draggable = True
        >>> el.get_attribute("draggable")
        'true'
        """
        return self.get_attribute("draggable") == "true"

    @draggable.setter
    def draggable(self, value: bool) -> None:
        self.set_attribute("draggable", "true" if value else "false")

    @property
    def spell_check(self) -> bool:
        """Whether spellchecking is enabled (reflects the ``spellcheck`` attribute).

        Returns ``False`` only when the attribute value is exactly ``"false"``.
        The default (attribute absent) is ``True`` per WHATWG HTML §6.8.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("textarea")
        >>> el.spell_check
        True
        >>> el.spell_check = False
        >>> el.get_attribute("spellcheck")
        'false'
        """
        val = self.get_attribute("spellcheck")
        return val != "false"

    @spell_check.setter
    def spell_check(self, value: bool) -> None:
        self.set_attribute("spellcheck", "true" if value else "false")

    @property
    def spellcheck(self) -> bool:
        """Whether spellchecking is enabled (reflects the ``spellcheck`` attribute).

        Alias for :attr:`spell_check` — the WHATWG IDL name.

        Returns ``False`` only when the attribute value is exactly ``"false"``;
        the default (absent) is ``True`` per WHATWG HTML §6.8.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.spellcheck
        True
        >>> el.spellcheck = False
        >>> el.get_attribute("spellcheck")
        'false'
        """
        val = self.get_attribute("spellcheck")
        return val != "false"

    @spellcheck.setter
    def spellcheck(self, value: bool) -> None:
        self.set_attribute("spellcheck", "true" if value else "false")

    @property
    def autocapitalize(self) -> str:
        """Auto-capitalisation hint (reflects the ``autocapitalize`` attribute).

        Returns the attribute value, or ``''`` when absent.
        Per WHATWG HTML §6.8.6. Valid hint values are ``"none"``, ``"sentences"``,
        ``"words"``, ``"characters"`` — no validation applied.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("input")
        >>> el.autocapitalize
        ''
        >>> el.autocapitalize = "sentences"
        >>> el.get_attribute("autocapitalize")
        'sentences'
        """
        return self.get_attribute("autocapitalize") or ""

    @autocapitalize.setter
    def autocapitalize(self, value: str) -> None:
        self.set_attribute("autocapitalize", value)

    @property
    def nonce(self) -> str:
        """Cryptographic nonce for CSP (reflects the ``nonce`` attribute).

        Returns the attribute value, or ``''`` when absent.
        Per WHATWG HTML §4.2.5.3 (nonce for Content Security Policy).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("script")
        >>> el.nonce
        ''
        >>> el.nonce = "EDNnf03nceIOfn39fn3e9h3sdfa"
        >>> el.nonce
        'EDNnf03nceIOfn39fn3e9h3sdfa'
        """
        return self.get_attribute("nonce") or ""

    @nonce.setter
    def nonce(self, value: str) -> None:
        self.set_attribute("nonce", value)

    @property
    def autofocus(self) -> bool:
        """Whether this element should receive focus on page load.

        Reflects the ``autofocus`` boolean attribute per WHATWG HTML §6.6.8.
        Returns ``True`` when the attribute is present (any value), ``False``
        when absent. Coexists with same-named properties on
        ``HTMLInputElement`` and ``HTMLButtonElement`` which override via MRO.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.autofocus
        False
        >>> el.autofocus = True
        >>> el.has_attribute("autofocus")
        True
        """
        return self.has_attribute("autofocus")

    @autofocus.setter
    def autofocus(self, value: bool) -> None:
        if value:
            self.set_attribute("autofocus", "")
        else:
            self.remove_attribute("autofocus")

    @property
    def access_key_label(self) -> str:
        """System-assigned access key label (headless stub: always ``''``).

        Per WHATWG HTML §6.6.2. In a headless environment there is no system
        shortcut assignment, so this returns an empty string unconditionally.
        This property is read-only; no setter is provided.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().create_element("button").access_key_label
        ''
        """
        return ""

    @property
    def input_mode(self) -> str:
        """Virtual keyboard input mode hint (reflects the ``inputmode`` attribute).

        Returns the attribute value, or ``''`` when absent.
        Per WHATWG HTML §6.8.6. Valid values: ``"none"``, ``"text"``, ``"tel"``,
        ``"url"``, ``"email"``, ``"numeric"``, ``"decimal"``, ``"search"``.
        Note: the HTML attribute name is ``inputmode`` (no underscore);
        the Python name is ``input_mode`` per snake_case convention.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("input")
        >>> el.input_mode
        ''
        >>> el.input_mode = "numeric"
        >>> el.get_attribute("inputmode")
        'numeric'
        """
        return self.get_attribute("inputmode") or ""

    @input_mode.setter
    def input_mode(self, value: str) -> None:
        self.set_attribute("inputmode", value)

    @property
    def enter_key_hint(self) -> str:
        """Enter-key action label hint (reflects the ``enterkeyhint`` attribute).

        Returns the attribute value, or ``''`` when absent.
        Per WHATWG HTML §6.8.6. Valid values: ``"enter"``, ``"done"``, ``"go"``,
        ``"next"``, ``"previous"``, ``"search"``, ``"send"``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("input")
        >>> el.enter_key_hint
        ''
        >>> el.enter_key_hint = "search"
        >>> el.get_attribute("enterkeyhint")
        'search'
        """
        return self.get_attribute("enterkeyhint") or ""

    @enter_key_hint.setter
    def enter_key_hint(self, value: str) -> None:
        self.set_attribute("enterkeyhint", value)

    @property
    def translate(self) -> bool:
        """Whether translation is enabled for this element (WHATWG HTML §6.1.2).

        Returns ``False`` when the ``translate`` attribute value is ``"no"``
        (case-insensitive). Returns ``True`` when absent or value is ``"yes"``
        (case-insensitive) or any other value.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("p")
        >>> el.translate
        True
        >>> el.translate = False
        >>> el.get_attribute("translate")
        'no'
        """
        val = self.get_attribute("translate")
        if val is None:
            return True
        return val.lower() != "no"

    @translate.setter
    def translate(self, value: bool) -> None:
        self.set_attribute("translate", "yes" if value else "no")

    # ------------------------------------------------------------------
    # inner_text / outer_text — BACK-137, ADR-120
    # Simplified WHATWG HTML §3.2.7 non-rendering semantics.
    # ------------------------------------------------------------------

    @property
    def inner_text(self) -> str:
        """Rendered text content — whitespace-collapsed ``text_content``.

        In a non-rendering server-side context this returns the same string
        as ``text_content`` but with consecutive whitespace collapsed to a
        single space and leading/trailing whitespace stripped.

        Per WHATWG HTML §3.2.7 — simplified for non-rendering environments.
        INV-001: ``inner_text`` is the snake_case form of ``.NET InnerText``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> div.inner_html = "<p>Hello   world</p><p>  end  </p>"
        >>> div.inner_text
        'Hello world end'
        """
        raw = self.text_content or ""
        return re.sub(r"\s+", " ", raw).strip()

    @inner_text.setter
    def inner_text(self, value: str) -> None:
        """Replace element children with a single Text node.

        Removes all current children using DOM mutation primitives, then
        appends a new Text node for *value* (omitted when empty).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> div = doc.create_element("div")
        >>> _ = doc.append_child(div)
        >>> div.inner_text = "hello"
        >>> div.inner_html
        'hello'
        """
        # Remove all children using DOM mutation primitives (INV-005).
        while self._children:
            self.remove_child(self._children[0])
        if value:
            doc = self._owner_document
            if doc is not None:
                self.append_child(doc.create_text_node(value))
            else:
                from aspose_html.dom._character_data import Text  # noqa: PLC0415
                self.append_child(Text(value))

    @property
    def outer_text(self) -> str:
        """Same as ``inner_text`` (getter mirrors inner_text per HTML Standard §3.2.7).

        INV-001: ``outer_text`` is the snake_case form of ``.NET OuterText``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> span = doc.create_element("span")
        >>> span.inner_text = "hi"
        >>> span.outer_text
        'hi'
        """
        return self.inner_text

    @outer_text.setter
    def outer_text(self, value: str) -> None:
        """Replace this element in its parent tree with a Text node.

        Raises :exc:`~aspose_html.dom.NoModificationAllowedError` (code 7)
        if the element has no parent node.

        Examples
        --------
        >>> from aspose_html.dom import Document, NoModificationAllowedError
        >>> doc = Document()
        >>> parent = doc.create_element("div")
        >>> span = doc.create_element("span")
        >>> _ = doc.append_child(parent)
        >>> _ = parent.append_child(span)
        >>> span.outer_text = "replaced"
        >>> parent.inner_html
        'replaced'
        """
        if self._parent is None:
            from aspose_html.dom._exceptions import NoModificationAllowedError  # noqa: PLC0415
            raise NoModificationAllowedError(
                "Cannot set outer_text on a detached element (no parent node)."
            )
        doc = self._owner_document
        if doc is not None:
            text_node = doc.create_text_node(value)
        else:
            from aspose_html.dom._character_data import Text  # noqa: PLC0415
            text_node = Text(value)
        self.replace_with(text_node)

    # ------------------------------------------------------------------
    # Interaction methods — BACK-138, ADR-121, SPEC-078 Group F
    # ------------------------------------------------------------------

    def click(self) -> None:
        """Dispatch a synthetic click event on this element.

        Fires a bubbling, cancelable ``'click'`` :class:`~aspose_html.dom.Event`
        using the existing ``dispatch_event`` infrastructure.  In a server-side
        context no default browser action (navigation, form submission) occurs.

        INV-001: corresponds to ``.NET HTMLElement.Click()``.
        INV-005: uses ``dispatch_event`` — no direct DOM-tree mutation.

        Examples
        --------
        >>> from aspose_html.dom import Document, Event
        >>> doc = Document()
        >>> btn = doc.create_element("button")
        >>> _ = doc.append_child(btn)
        >>> clicked = []
        >>> btn.add_event_listener("click", lambda e: clicked.append(True))
        >>> btn.click()
        >>> len(clicked)
        1
        """
        from aspose_html.dom._event import Event  # noqa: PLC0415 — avoid module-level cycle
        evt = Event("click", bubbles=True, cancelable=True)
        self.dispatch_event(evt)

    def focus(self, options: "dict | None" = None) -> None:
        """Dispatch a non-bubbling ``'focus'`` event on this element.

        The *options* dict is accepted for API compatibility but ignored in
        this server-side stub — no focus-management infrastructure exists.

        INV-001: corresponds to ``.NET HTMLElement.Focus()``.
        INV-005: uses ``dispatch_event`` — no direct DOM-tree mutation.

        Parameters
        ----------
        options:
            Optional focus-options dict (e.g. ``{"preventScroll": True}``).
            Accepted but not acted upon.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> _ = doc.append_child(inp)
        >>> fired = []
        >>> inp.add_event_listener("focus", lambda e: fired.append(e.type))
        >>> inp.focus()
        >>> fired
        ['focus']
        """
        from aspose_html.dom._event import Event  # noqa: PLC0415
        evt = Event("focus", bubbles=False, cancelable=False)
        self.dispatch_event(evt)

    def blur(self) -> None:
        """Dispatch a non-bubbling ``'blur'`` event on this element.

        INV-001: corresponds to ``.NET HTMLElement.Blur()``.
        INV-005: uses ``dispatch_event`` — no direct DOM-tree mutation.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> inp = doc.create_element("input")
        >>> _ = doc.append_child(inp)
        >>> fired = []
        >>> inp.add_event_listener("blur", lambda e: fired.append(e.type))
        >>> inp.blur()
        >>> fired
        ['blur']
        """
        from aspose_html.dom._event import Event  # noqa: PLC0415
        evt = Event("blur", bubbles=False, cancelable=False)
        self.dispatch_event(evt)

    # ------------------------------------------------------------------
    # Popover API stubs (WHATWG HTML §6.12.2)
    # ------------------------------------------------------------------

    def show_popover(self) -> None:
        """Show this element as a popover (no-op in headless mode).

        Per WHATWG HTML §6.12.2. Popovers are a rendering-surface concept;
        in a headless environment this method is a no-op for API compatibility.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.show_popover()
        """

    def hide_popover(self) -> None:
        """Hide this element's popover (no-op in headless mode).

        Per WHATWG HTML §6.12.2. Counterpart to :meth:`show_popover`.
        In a headless environment this method is a no-op for API compatibility.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.hide_popover()
        """

    def toggle_popover(self, force: "bool | None" = None) -> bool:
        """Toggle this element's popover state (no-op, always returns ``False``).

        Per WHATWG HTML §6.12.2. In a headless environment no popover is ever
        shown, so this method is a no-op returning ``False`` regardless of the
        optional *force* argument.

        Parameters
        ----------
        force:
            If provided, hints whether to force-show (``True``) or force-hide
            (``False``). Ignored in headless mode.

        Returns
        -------
        bool
            Always ``False`` in headless mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.toggle_popover()
        False
        >>> el.toggle_popover(force=True)
        False
        """
        return False

    # ------------------------------------------------------------------
    # Track 114 — popover attribute reflection (BACK-335 / ADR-313)
    # ------------------------------------------------------------------

    @property
    def popover(self):
        """Reflects the ``popover`` content attribute (WHATWG HTML §6.12).

        Returns ``None`` when the attribute is absent; otherwise the
        attribute value string (e.g. ``"auto"``, ``"manual"``, ``"hint"``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("div")
        >>> el.popover is None
        True
        >>> el.set_attribute("popover", "auto")
        >>> el.popover
        'auto'
        >>> el.popover = "manual"
        >>> el.get_attribute("popover")
        'manual'
        >>> el.popover = None
        >>> el.has_attribute("popover")
        False
        """
        return self.get_attribute("popover")

    @popover.setter
    def popover(self, value: "str | None") -> None:
        if value is None:
            self.remove_attribute("popover")
        else:
            self.set_attribute("popover", value)
