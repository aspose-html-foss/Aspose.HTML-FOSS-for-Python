"""Document metadata element classes.

Contains ``HTMLScriptElement``, ``HTMLLinkElement``, ``HTMLMetaElement``,
``HTMLTitleElement``, ``HTMLStyleElement``, ``HTMLBaseElement``.

See  for the split rationale.
"""
from __future__ import annotations

from urllib.parse import urljoin

from aspose_html.dom._html_element import HTMLElement
from aspose_html.dom.html._anchor_elements import _get_base_url
from aspose_html.url import URL, URLParseError


# ---------------------------------------------------------------------------
# HTMLScriptElement
# ---------------------------------------------------------------------------

class HTMLScriptElement(HTMLElement):
    """HTML ``<script>`` element.

    Reflects ``src``, ``type``, ``async_`` (maps to the ``async`` HTML
    attribute — ``async`` is a Python keyword), and ``defer`` IDL attributes.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> script = doc.create_element("script")
    >>> isinstance(script, HTMLScriptElement)
    True
    >>> script.async_
    False
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def src(self) -> str:
        """The ``src`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.src
        ''
        >>> script.src = "app.js"
        >>> script.src
        'app.js'
        """
        return self.get_attribute("src") or ""

    @src.setter
    def src(self, value: str) -> None:
        self.set_attribute("src", value)

    @property
    def type(self) -> str:
        """The ``type`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.type
        ''
        >>> script.type = "module"
        >>> script.type
        'module'
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def async_(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``async`` attribute.

        Named ``async_`` because ``async`` is a Python reserved keyword.
        Setting to ``True`` creates the attribute with an empty string value
        (WHATWG boolean attribute rule); setting to ``False`` removes it.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.async_
        False
        >>> script.async_ = True
        >>> script.async_
        True
        >>> script.async_ = False
        >>> script.async_
        False
        """
        return self.has_attribute("async")

    @async_.setter
    def async_(self, value: bool) -> None:
        if value:
            self.set_attribute("async", "")
        else:
            self.remove_attribute("async")

    @property
    def defer(self) -> bool:
        """Boolean presence attribute ``defer``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.defer
        False
        >>> script.defer = True
        >>> script.defer
        True
        """
        return self.has_attribute("defer")

    @defer.setter
    def defer(self, value: bool) -> None:
        if value:
            self.set_attribute("defer", "")
        else:
            self.remove_attribute("defer")

    @property
    def text(self) -> str:
        """Concatenated text content of all descendant Text nodes.

        WHATWG HTML §4.12.1 — equivalent to reading ``text_content`` on the
        element; returns ``""`` when the element has no text children.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.text
        ''
        >>> _ = script.append_child(doc.create_text_node("var x = 1;"))
        >>> script.text
        'var x = 1;'
        """
        return self.text_content or ""

    @text.setter
    def text(self, value: str) -> None:
        """Replace all children with a single Text node containing *value*.

        Does NOT evaluate the script content.  Setting to ``""`` removes all
        children without appending a new node.

        If the element is detached (no owner document), a standalone
        ``Text`` node is created without an owner document (no error raised).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.text = "console.log(1);"
        >>> script.text
        'console.log(1);'
        >>> script.text = "var y = 2;"
        >>> script.text
        'var y = 2;'
        """
        while self.first_child is not None:
            self.remove_child(self.first_child)
        if value:
            doc = self._owner_document
            if doc is not None:
                self.append_child(doc.create_text_node(value))
            else:
                from aspose_html.dom._character_data import Text  # noqa: PLC0415
                self.append_child(Text(value))

    @property
    def integrity(self) -> str:
        """The ``integrity`` attribute value (SRI), or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.integrity
        ''
        >>> script.integrity = "sha384-abc123"
        >>> script.integrity
        'sha384-abc123'
        """
        return self.get_attribute("integrity") or ""

    @integrity.setter
    def integrity(self, value: str) -> None:
        self.set_attribute("integrity", value)

    @property
    def cross_origin(self) -> "str | None":
        """The ``crossorigin`` attribute value, or ``None`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.cross_origin is None
        True
        >>> script.cross_origin = "anonymous"
        >>> script.cross_origin
        'anonymous'
        >>> script.cross_origin = None
        >>> script.cross_origin is None
        True
        """
        return self.get_attribute("crossorigin")

    @cross_origin.setter
    def cross_origin(self, value: "str | None") -> None:
        if value is None:
            self.remove_attribute("crossorigin")
        else:
            self.set_attribute("crossorigin", value)

    @property
    def referrer_policy(self) -> str:
        """The ``referrerpolicy`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.referrer_policy
        ''
        >>> script.referrer_policy = "no-referrer"
        >>> script.referrer_policy
        'no-referrer'
        """
        return self.get_attribute("referrerpolicy") or ""

    @referrer_policy.setter
    def referrer_policy(self, value: str) -> None:
        self.set_attribute("referrerpolicy", value)

    @property
    def no_module(self) -> bool:
        """Reflect the ``nomodule`` boolean attribute (WHATWG HTML §4.12.1).

        Returns ``True`` when the ``nomodule`` attribute is present (regardless
        of value); ``False`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('script')
        >>> el.no_module
        False
        >>> el.set_attribute('nomodule', '')
        >>> el.no_module
        True
        """
        return self.has_attribute("nomodule")

    @no_module.setter
    def no_module(self, value: bool) -> None:
        if value:
            self.set_attribute("nomodule", "")
        else:
            self.remove_attribute("nomodule")

    @property
    def blocking(self) -> str:
        """Reflect the ``blocking`` content attribute; empty string when absent (WHATWG HTML §4.12.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('script')
        >>> el.blocking
        ''
        """
        return self.get_attribute("blocking") or ""

    @blocking.setter
    def blocking(self, value: str) -> None:
        self.set_attribute("blocking", value)

    @property
    def fetch_priority(self) -> str:
        """Reflect the ``fetchpriority`` content attribute; empty string when absent (WHATWG HTML §4.12.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('script')
        >>> el.fetch_priority
        ''
        """
        return self.get_attribute("fetchpriority") or ""

    @fetch_priority.setter
    def fetch_priority(self, value: str) -> None:
        self.set_attribute("fetchpriority", value)

    @property
    def charset(self) -> str:
        """Reflects obsolete ``charset`` content attribute (WHATWG HTML §4.12.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.charset
        ''
        >>> script.set_attribute("charset", "utf-8")
        >>> script.charset
        'utf-8'
        """
        return self.get_attribute("charset") or ""

    @charset.setter
    def charset(self, value: str) -> None:
        self.set_attribute("charset", value)

    @property
    def event(self) -> str:
        """Reflects obsolete ``event`` content attribute (WHATWG HTML §4.12.1).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.event
        ''
        >>> script.set_attribute("event", "onclick")
        >>> script.event
        'onclick'
        """
        return self.get_attribute("event") or ""

    @event.setter
    def event(self, value: str) -> None:
        self.set_attribute("event", value)

    @property
    def html_for(self) -> str:
        """Reflects obsolete ``for`` content attribute (WHATWG HTML §4.12.1).

        Named ``html_for`` because ``for`` is a Python reserved keyword.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> script = doc.create_element("script")
        >>> script.html_for
        ''
        >>> script.set_attribute("for", "myElement")
        >>> script.html_for
        'myElement'
        """
        return self.get_attribute("for") or ""

    @html_for.setter
    def html_for(self, value: str) -> None:
        self.set_attribute("for", value)


# ---------------------------------------------------------------------------
# HTMLLinkElement
# ---------------------------------------------------------------------------

class HTMLLinkElement(HTMLElement):
    """HTML ``<link>`` element.

    Reflects ``href``, ``rel``, and ``type`` IDL attributes.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> link = doc.create_element("link")
    >>> isinstance(link, HTMLLinkElement)
    True
    >>> link.rel
    ''
    """

    __slots__ = (
        "_custom_validity_message",
        "_sheet_cache",
        "_sheet_cache_href",
        "_sheet_cache_rel",
        "_rel_list_cache",
        "_sizes_cache",
    )

    @property
    def href(self) -> str:
        """Resolved ``href`` URL, or ``''`` when attribute is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.href
        ''
        >>> link.href = "style.css"
        >>> link.href
        'style.css'
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc2 = HTMLDocument.parse("<link href='style.css'>", base_url="https://example.com/assets/")
        >>> doc2.query_selector("link").href
        'https://example.com/assets/style.css'
        """
        raw = self.get_attribute("href") or ""
        if raw == "":
            return ""
        doc = self.owner_document
        if doc is None:
            return raw
        try:
            return URL(raw, base=_get_base_url(doc)).href
        except URLParseError:
            return urljoin(doc.url, raw)

    @href.setter
    def href(self, value: str) -> None:
        self.set_attribute("href", value)

    @property
    def rel(self) -> str:
        """The ``rel`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.rel
        ''
        >>> link.rel = "stylesheet"
        >>> link.rel
        'stylesheet'
        """
        return self.get_attribute("rel") or ""

    @rel.setter
    def rel(self, value: str) -> None:
        self.set_attribute("rel", value)

    @property
    def type(self) -> str:
        """The ``type`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.type
        ''
        >>> link.type = "text/css"
        >>> link.type
        'text/css'
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def sheet(self) -> CSSStyleSheet | None:
        """Stylesheet object for ``rel=stylesheet`` links, else ``None``.

         does not fetch or parse external CSS. Returned sheet has empty
        ``css_rules`` and metadata only.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.sheet is None
        True
        >>> link.rel = "StyleSheet preload"
        >>> link.href = "a.css"
        >>> sheet = link.sheet
        >>> sheet is not None
        True
        >>> sheet.owner_node is link
        True
        >>> sheet.href
        'a.css'
        """
        rel_value = self.rel
        rel_tokens = [token.casefold() for token in rel_value.split() if token]
        if "stylesheet" not in rel_tokens:
            return None
        href_value = self.href or self.get_attribute("href") or None
        cache = getattr(self, "_sheet_cache", None)
        cached_href = getattr(self, "_sheet_cache_href", None)
        cached_rel = getattr(self, "_sheet_cache_rel", None)
        if cache is not None and cached_href == href_value and cached_rel == rel_value:
            return cache
        from aspose_html.cssom import CSSStyleSheet  # noqa: PLC0415
        sheet = CSSStyleSheet()
        sheet.owner_node = self
        sheet.href = href_value
        self._sheet_cache = sheet
        self._sheet_cache_href = href_value
        self._sheet_cache_rel = rel_value
        return sheet

    # -- IDL tail properties () ----------------------------------------

    @property
    def cross_origin(self) -> "str | None":
        """The ``crossorigin`` attribute value, or ``None`` when absent.

        Per WHATWG HTML §4.2.4 (nullable DOMString).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.cross_origin is None
        True
        >>> link.cross_origin = "anonymous"
        >>> link.cross_origin
        'anonymous'
        """
        return self.get_attribute("crossorigin")

    @cross_origin.setter
    def cross_origin(self, value: "str | None") -> None:
        if value is None:
            self.remove_attribute("crossorigin")
        else:
            self.set_attribute("crossorigin", value)

    @property
    def integrity(self) -> str:
        """The ``integrity`` subresource-integrity attribute, or ``''`` when absent.

        Per WHATWG HTML §4.2.4.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.integrity
        ''
        >>> link.integrity = "sha384-abc"
        >>> link.integrity
        'sha384-abc'
        """
        return self.get_attribute("integrity") or ""

    @integrity.setter
    def integrity(self, value: str) -> None:
        self.set_attribute("integrity", value)

    @property
    def referrer_policy(self) -> str:
        """The ``referrerpolicy`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.2.4.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.referrer_policy
        ''
        >>> link.referrer_policy = "no-referrer"
        >>> link.referrer_policy
        'no-referrer'
        """
        return self.get_attribute("referrerpolicy") or ""

    @referrer_policy.setter
    def referrer_policy(self, value: str) -> None:
        self.set_attribute("referrerpolicy", value)

    @property
    def as_(self) -> str:
        """The ``as`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.2.4. Named ``as_`` to avoid conflict with the
        Python ``as`` keyword.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.as_
        ''
        >>> link.as_ = "script"
        >>> link.as_
        'script'
        """
        return self.get_attribute("as") or ""

    @as_.setter
    def as_(self, value: str) -> None:
        self.set_attribute("as", value)

    @property
    def sizes(self) -> "DOMTokenList":
        """``DOMTokenList`` backed by the ``sizes`` attribute (WHATWG HTML §4.2.4).

        The same instance is returned on every access.

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMTokenList
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> isinstance(link.sizes, DOMTokenList)
        True
        >>> link.sizes is link.sizes
        True
        >>> link.sizes.add("any")
        >>> link.get_attribute("sizes")
        'any'
        """
        cached = getattr(self, "_sizes_cache", None)
        if cached is None:
            from aspose_html.dom._token_list import DOMTokenList  # noqa: PLC0415
            cached = DOMTokenList(self, "sizes")
            object.__setattr__(self, "_sizes_cache", cached)
        return cached

    @property
    def rel_list(self) -> "DOMTokenList":
        """``DOMTokenList`` backed by the ``rel`` attribute (WHATWG HTML §4.2.4).

        The same instance is returned on every access.

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMTokenList
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> isinstance(link.rel_list, DOMTokenList)
        True
        >>> link.rel_list is link.rel_list
        True
        >>> link.rel_list.add("stylesheet")
        >>> link.rel
        'stylesheet'
        """
        cached = getattr(self, "_rel_list_cache", None)
        if cached is None:
            from aspose_html.dom._token_list import DOMTokenList  # noqa: PLC0415
            cached = DOMTokenList(self, "rel")
            object.__setattr__(self, "_rel_list_cache", cached)
        return cached

    @property
    def disabled(self) -> bool:
        """Boolean presence attribute reflecting the HTML ``disabled`` attribute.

        Per WHATWG HTML §4.2.4.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.disabled
        False
        >>> link.disabled = True
        >>> link.disabled
        True
        >>> link.disabled = False
        >>> link.disabled
        False
        """
        return self.has_attribute("disabled")

    @disabled.setter
    def disabled(self, value: bool) -> None:
        if value:
            self.set_attribute("disabled", "")
        else:
            self.remove_attribute("disabled")

    @property
    def hreflang(self) -> str:
        """The ``hreflang`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.2.4.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.hreflang
        ''
        >>> link.hreflang = "en"
        >>> link.hreflang
        'en'
        """
        return self.get_attribute("hreflang") or ""

    @hreflang.setter
    def hreflang(self, value: str) -> None:
        self.set_attribute("hreflang", value)

    @property
    def media(self) -> str:
        """The ``media`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.2.4.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.media
        ''
        >>> link.media = "screen"
        >>> link.media
        'screen'
        """
        return self.get_attribute("media") or ""

    @media.setter
    def media(self, value: str) -> None:
        self.set_attribute("media", value)

    @property
    def charset(self) -> str:
        """The ``charset`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.2.4 (obsolete but still reflected).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.charset
        ''
        >>> link.charset = "utf-8"
        >>> link.charset
        'utf-8'
        """
        return self.get_attribute("charset") or ""

    @charset.setter
    def charset(self, value: str) -> None:
        self.set_attribute("charset", value)

    @property
    def image_srcset(self) -> str:
        """Reflects ``imagesrcset`` attribute (WHATWG HTML §4.2.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.image_srcset
        ''
        >>> link.set_attribute("imagesrcset", "img-2x.png 2x")
        >>> link.image_srcset
        'img-2x.png 2x'
        """
        return self.get_attribute("imagesrcset") or ""

    @image_srcset.setter
    def image_srcset(self, value: str) -> None:
        self.set_attribute("imagesrcset", value)

    @property
    def image_sizes(self) -> str:
        """Reflects ``imagesizes`` attribute (WHATWG HTML §4.2.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.image_sizes
        ''
        >>> link.set_attribute("imagesizes", "(max-width: 600px) 100vw")
        >>> link.image_sizes
        '(max-width: 600px) 100vw'
        """
        return self.get_attribute("imagesizes") or ""

    @image_sizes.setter
    def image_sizes(self, value: str) -> None:
        self.set_attribute("imagesizes", value)

    @property
    def blocking(self) -> str:
        """Reflects ``blocking`` attribute; returns ``''`` (headless stub) (WHATWG HTML §4.2.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.blocking
        ''
        """
        return self.get_attribute("blocking") or ""

    @blocking.setter
    def blocking(self, value: str) -> None:
        self.set_attribute("blocking", value)

    @property
    def fetch_priority(self) -> str:
        """Reflects ``fetchpriority`` attribute; default ``'auto'`` (WHATWG HTML §4.2.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.fetch_priority
        'auto'
        >>> link.set_attribute("fetchpriority", "high")
        >>> link.fetch_priority
        'high'
        """
        return self.get_attribute("fetchpriority") or "auto"

    @fetch_priority.setter
    def fetch_priority(self, value: str) -> None:
        self.set_attribute("fetchpriority", value)

    @property
    def rev(self) -> str:
        """Reflects obsolete ``rev`` content attribute (WHATWG HTML §4.2.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.rev
        ''
        >>> link.set_attribute("rev", "made")
        >>> link.rev
        'made'
        """
        return self.get_attribute("rev") or ""

    @rev.setter
    def rev(self, value: str) -> None:
        self.set_attribute("rev", value)

    @property
    def target(self) -> str:
        """Reflects obsolete ``target`` content attribute (WHATWG HTML §4.2.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> link = doc.create_element("link")
        >>> link.target
        ''
        >>> link.set_attribute("target", "_blank")
        >>> link.target
        '_blank'
        """
        return self.get_attribute("target") or ""

    @target.setter
    def target(self, value: str) -> None:
        self.set_attribute("target", value)


# ---------------------------------------------------------------------------
# HTMLMetaElement
# ---------------------------------------------------------------------------

class HTMLMetaElement(HTMLElement):
    """HTML ``<meta>`` element.

    Reflects ``name``, ``content``, and ``http_equiv`` IDL attributes.
    Note: ``http_equiv`` maps to the HTML attribute ``http-equiv`` (hyphen
    in the attribute name, underscore in the Python property name).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> meta = doc.create_element("meta")
    >>> isinstance(meta, HTMLMetaElement)
    True
    >>> meta.http_equiv
    ''
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meta = doc.create_element("meta")
        >>> meta.name
        ''
        >>> meta.name = "description"
        >>> meta.name
        'description'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def content(self) -> str:
        """The ``content`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meta = doc.create_element("meta")
        >>> meta.content
        ''
        >>> meta.content = "A description"
        >>> meta.content
        'A description'
        """
        return self.get_attribute("content") or ""

    @content.setter
    def content(self, value: str) -> None:
        self.set_attribute("content", value)

    @property
    def http_equiv(self) -> str:
        """The HTML ``http-equiv`` attribute value, or ``''`` when absent.

        The Python property name uses an underscore (``http_equiv``) because
        Python identifiers cannot contain hyphens.  The underlying HTML
        attribute name is ``http-equiv`` (with a hyphen).  # 

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meta = doc.create_element("meta")
        >>> meta.http_equiv
        ''
        >>> meta.http_equiv = "refresh"
        >>> meta.http_equiv
        'refresh'
        >>> meta.get_attribute("http-equiv")
        'refresh'
        """
        # Attribute name is "http-equiv" with a hyphen — not "http_equiv". # 
        return self.get_attribute("http-equiv") or ""

    @http_equiv.setter
    def http_equiv(self, value: str) -> None:
        self.set_attribute("http-equiv", value)

    @property
    def charset(self) -> str:
        """Reflect the ``charset`` content attribute (WHATWG HTML §4.2.5).

        Returns ``''`` when the attribute is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('meta')
        >>> el.charset
        ''
        >>> el.set_attribute('charset', 'utf-8')
        >>> el.charset
        'utf-8'
        """
        return self.get_attribute("charset") or ""

    @charset.setter
    def charset(self, value: str) -> None:
        self.set_attribute("charset", value)

    @property
    def scheme(self) -> str:
        """Reflects obsolete ``scheme`` content attribute (WHATWG HTML §4.2.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meta = doc.create_element("meta")
        >>> meta.scheme
        ''
        >>> meta.set_attribute("scheme", "ISBN")
        >>> meta.scheme
        'ISBN'
        """
        return self.get_attribute("scheme") or ""

    @scheme.setter
    def scheme(self, value: str) -> None:
        self.set_attribute("scheme", value)

    @property
    def media(self) -> str:
        """Reflects ``media`` content attribute (WHATWG HTML §4.2.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> meta = doc.create_element("meta")
        >>> meta.media
        ''
        >>> meta.set_attribute("media", "screen")
        >>> meta.media
        'screen'
        """
        return self.get_attribute("media") or ""

    @media.setter
    def media(self, value: str) -> None:
        self.set_attribute("media", value)


# ---------------------------------------------------------------------------
# HTMLTitleElement
# ---------------------------------------------------------------------------

class HTMLTitleElement(HTMLElement):
    """HTML ``<title>`` element.

    The ``text`` property reads and writes the element's first ``Text`` child
    node directly — it is NOT an attribute reflection.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> title = doc.create_element("title")
    >>> isinstance(title, HTMLTitleElement)
    True
    >>> title.text
    ''
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def text(self) -> str:
        """The text content of the ``<title>`` element.

        Reads the ``data`` of the first ``Text`` child node; returns ``''``
        if no text child exists.

        Setting replaces all children with a single new ``Text`` node.
        Raises ``NotSupportedError`` if the element has no owner document.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> title = doc.create_element("title")
        >>> title.text
        ''
        >>> doc.append_child(title)
        <Element 'TITLE'>
        >>> title.text = "My Page"
        >>> title.text
        'My Page'
        """
        from aspose_html.dom._node_type import NodeType  # noqa: PLC0415
        child = self.first_child
        if child is not None and child._node_type == NodeType.TEXT_NODE:
            return child.data  # type: ignore[attr-defined]
        return ""

    @text.setter
    def text(self, value: str) -> None:
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        # Remove all existing children.
        for child in list(self._children):
            self.remove_child(child)
        if value:
            doc = self._owner_document
            if doc is None:
                raise NotSupportedError(
                    "Cannot set HTMLTitleElement.text on a detached element "
                    "(no owner document). Append the element to a document first."
                )
            self.append_child(doc.create_text_node(value))


# ---------------------------------------------------------------------------
# HTMLButtonElement
# ---------------------------------------------------------------------------


class HTMLStyleElement(HTMLElement):
    """HTML ``<style>`` element.

    Reflects IDL attributes: ``media`` and ``type``.
    """

    __slots__ = ("_sheet_cache", "_sheet_cache_text")

    @property
    def media(self) -> str:
        """The ``media`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> style = doc.create_element("style")
        >>> style.media
        ''
        >>> style.media = "screen"
        >>> style.media
        'screen'
        """
        return self.get_attribute("media") or ""

    @media.setter
    def media(self, value: str) -> None:
        self.set_attribute("media", value)

    @property
    def type(self) -> str:
        """The ``type`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> style = doc.create_element("style")
        >>> style.type
        ''
        >>> style.type = "text/css"
        >>> style.type
        'text/css'
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def sheet(self) -> CSSStyleSheet | None:
        """Stylesheet parsed from this element's text content.

        Parses the concatenated text content as CSS and returns a
        ``CSSStyleSheet``.  The result is cached on the text value and
        re-parsed only when the text changes.  Returns an empty (zero-rule)
        sheet when ``text_content`` is empty.

        The returned sheet's ``owner_node`` is set to ``self`` and is
        included in ``owner_document.style_sheets`` automatically via
        ``Document._collect_style_sheets()``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> style = doc.create_element("style")
        >>> style.text_content = "p { color: red }"
        >>> style.sheet.css_rules[0].css_text
        'p { color: red }'
        >>> style.sheet.owner_node is style
        True
        """
        text_value = self.text_content or ""
        cache = getattr(self, "_sheet_cache", None)
        cached_text = getattr(self, "_sheet_cache_text", None)
        if cache is not None and cached_text == text_value:
            return cache
        from aspose_html.cssom import CSSStyleSheet  # noqa: PLC0415
        sheet = CSSStyleSheet()
        sheet.replace_sync(text_value)
        sheet.owner_node = self
        self._sheet_cache = sheet
        self._sheet_cache_text = text_value
        return sheet

    @property
    def disabled(self) -> bool:
        """Disabled state of the associated ``CSSStyleSheet``, or ``False`` if no sheet.

        Per WHATWG HTML §4.2.4 / CSSOM §6.2: reflects the sheet's ``disabled``
        flag.  Setting ``True`` disables the sheet; ``False`` re-enables it.
        When no sheet is attached the getter returns ``False`` and the setter
        is a no-op.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element('style')
        >>> el.disabled
        False
        """
        sheet = getattr(self, "sheet", None)
        if sheet is None:
            return False
        return bool(sheet.disabled)

    @disabled.setter
    def disabled(self, value: bool) -> None:
        sheet = getattr(self, "sheet", None)
        if sheet is not None:
            sheet.disabled = bool(value)

    @property
    def blocking(self) -> str:
        """Reflects ``blocking`` attribute; returns ``''`` (headless stub) (WHATWG HTML §4.2.6).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> style = doc.create_element("style")
        >>> style.blocking
        ''
        """
        return self.get_attribute("blocking") or ""

    @blocking.setter
    def blocking(self, value: str) -> None:
        self.set_attribute("blocking", value)


class HTMLBaseElement(HTMLElement):
    """HTML ``<base>`` element.

    Reflects IDL attributes: ``href`` (raw reflection) and ``target``.
    """

    __slots__ = ()

    @property
    def href(self) -> str:
        """The raw ``href`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> base = doc.create_element("base")
        >>> base.href
        ''
        >>> base.href = "/assets/"
        >>> base.href
        '/assets/'
        """
        return self.get_attribute("href") or ""

    @href.setter
    def href(self, value: str) -> None:
        self.set_attribute("href", value)

    @property
    def target(self) -> str:
        """The ``target`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> base = doc.create_element("base")
        >>> base.target
        ''
        >>> base.target = "_blank"
        >>> base.target
        '_blank'
        """
        return self.get_attribute("target") or ""

    @target.setter
    def target(self, value: str) -> None:
        self.set_attribute("target", value)



