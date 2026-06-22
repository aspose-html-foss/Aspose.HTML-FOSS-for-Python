"""Anchor and hyperlink element classes.

Contains ``HTMLAnchorElement``, ``HTMLAreaElement``, ``HTMLMapElement`` and
the URL-resolution helpers used by those elements.

See ADR-304 for the split rationale.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin

from aspose_html.dom._html_element import HTMLElement
from aspose_html.url import URL, URLParseError


def _get_base_url(document: "Document") -> URL:
    """Return base URL for hyperlink resolution.

    Delegates to ``Document.base_uri`` so callers share the same
    `<base href>`/fallback semantics.
    """
    return URL(document.base_uri)


def _resolve_anchor_href(element: "HTMLAnchorElement") -> "URL | None":
    """Parse the element's href as a URL, returning None on failure.

    Used by URL decomposition properties (protocol, host, pathname, etc.).
    Does not affect the href getter or its urljoin fallback path.
    See ADR-152.
    """
    raw = element.get_attribute("href") or ""
    if not raw:
        return None
    doc = element.owner_document
    try:
        if doc is not None:
            return URL(raw, base=_get_base_url(doc))
        return URL(raw)
    except (URLParseError, Exception):  # noqa: BLE001
        return None


def _resolve_area_href(element: "HTMLAreaElement") -> "URL | None":
    """Parse ``HTMLAreaElement.href`` as URL, mirroring area href fallback."""
    raw = element.get_attribute("href") or ""
    if not raw:
        return None

    doc = element.owner_document
    if doc is None:
        try:
            return URL(raw)
        except (URLParseError, Exception):  # noqa: BLE001
            return None

    try:
        resolved = URL(raw, base=_get_base_url(doc)).href
    except URLParseError:
        resolved = urljoin(doc.url, raw)

    try:
        return URL(resolved)
    except (URLParseError, Exception):  # noqa: BLE001
        return None



# ---------------------------------------------------------------------------
# HTMLAnchorElement
# ---------------------------------------------------------------------------

class HTMLAnchorElement(HTMLElement):
    """HTML ``<a>`` anchor element.

    Reflects the ``href`` and ``target`` IDL attributes.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("a")
    >>> isinstance(el, HTMLAnchorElement)
    True
    >>> el.href
    ''
    >>> el.href = "https://example.com"
    >>> el.href
    'https://example.com'
    """

    __slots__ = ("_rel_list_cache",)

    @property
    def href(self) -> str:
        """Resolved ``href`` URL, or ``''`` when attribute is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.href
        ''
        >>> a.href = "/path"
        >>> a.href
        '/path'
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc2 = HTMLDocument.parse("<a href='page'></a>", base_url="https://example.com/root/")
        >>> doc2.query_selector("a").href
        'https://example.com/root/page'
        >>> a.href = "https://example.com"
        >>> a.href
        'https://example.com'
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
    def target(self) -> str:
        """The ``target`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.target
        ''
        >>> a.target = "_blank"
        >>> a.target
        '_blank'
        """
        return self.get_attribute("target") or ""

    @target.setter
    def target(self, value: str) -> None:
        self.set_attribute("target", value)

    # -- Link-metadata attribute reflections (INV-001, INV-003) --------------

    @property
    def rel(self) -> str:
        """The ``rel`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.rel
        ''
        >>> a.rel = "nofollow"
        >>> a.rel
        'nofollow'
        """
        return self.get_attribute("rel") or ""

    @rel.setter
    def rel(self, value: str) -> None:
        self.set_attribute("rel", value)

    @property
    def download(self) -> str:
        """The ``download`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.download
        ''
        >>> a.download = "file.pdf"
        >>> a.download
        'file.pdf'
        """
        return self.get_attribute("download") or ""

    @download.setter
    def download(self, value: str) -> None:
        self.set_attribute("download", value)

    @property
    def hreflang(self) -> str:
        """The ``hreflang`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.hreflang
        ''
        >>> a.hreflang = "en"
        >>> a.hreflang
        'en'
        """
        return self.get_attribute("hreflang") or ""

    @hreflang.setter
    def hreflang(self, value: str) -> None:
        self.set_attribute("hreflang", value)

    @property
    def type(self) -> str:
        """The ``type`` attribute value, or ``''`` when absent.

        Note: defaults to ``''`` for ``<a>`` (not ``'text'`` — that default
        applies only to ``<input>`` per WHATWG HTML §4.10.18).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.type
        ''
        >>> a.type = "text/html"
        >>> a.type
        'text/html'
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def text(self) -> str:
        """The text content of the anchor, or ``''`` when empty.

        Equivalent to ``textContent`` per WHATWG HTML §4.6.1.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.text
        ''
        >>> a.text = "Click me"
        >>> a.text
        'Click me'
        """
        return self.text_content or ""

    @text.setter
    def text(self, value: str) -> None:
        self.text_content = value

    # -- IDL tail properties (ADR-294) ----------------------------------------

    @property
    def rel_list(self) -> "DOMTokenList":
        """``DOMTokenList`` backed by the ``rel`` attribute (WHATWG HTML §4.6.3).

        The same instance is returned on every access.

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMTokenList
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> isinstance(a.rel_list, DOMTokenList)
        True
        >>> a.rel_list is a.rel_list
        True
        >>> a.rel_list.add("nofollow")
        >>> a.rel
        'nofollow'
        """
        cached = getattr(self, "_rel_list_cache", None)
        if cached is None:
            from aspose_html.dom._token_list import DOMTokenList  # noqa: PLC0415
            cached = DOMTokenList(self, "rel")
            object.__setattr__(self, "_rel_list_cache", cached)
        return cached

    @property
    def referrer_policy(self) -> str:
        """The ``referrerpolicy`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.6.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.referrer_policy
        ''
        >>> a.referrer_policy = "no-referrer"
        >>> a.referrer_policy
        'no-referrer'
        """
        return self.get_attribute("referrerpolicy") or ""

    @referrer_policy.setter
    def referrer_policy(self, value: str) -> None:
        self.set_attribute("referrerpolicy", value)

    @property
    def ping(self) -> str:
        """The ``ping`` attribute value, or ``''`` when absent.

        Per WHATWG HTML §4.6.3.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.ping
        ''
        >>> a.ping = "https://example.com/ping"
        >>> a.ping
        'https://example.com/ping'
        """
        return self.get_attribute("ping") or ""

    @ping.setter
    def ping(self, value: str) -> None:
        self.set_attribute("ping", value)

    # -- URL decomposition properties (read-only, INV-001, INV-003) ----------
    # All delegate to _resolve_anchor_href(); return "" (or "null" for origin)
    # when href is absent or unparseable. See ADR-152.

    @property
    def protocol(self) -> str:
        """URL scheme followed by ``':'``, or ``''`` when href is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.protocol
        ''
        >>> a.href = "https://example.com/path"
        >>> a.protocol
        'https:'
        """
        u = _resolve_anchor_href(self)
        return u.protocol if u is not None else ""

    @property
    def username(self) -> str:
        """Username from the URL userinfo, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.username
        ''
        >>> a.href = "https://user:pass@example.com/"
        >>> a.username
        'user'
        """
        u = _resolve_anchor_href(self)
        return u.username if u is not None else ""

    @property
    def password(self) -> str:
        """Password from the URL userinfo, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.password
        ''
        >>> a.href = "https://user:pass@example.com/"
        >>> a.password
        'pass'
        """
        u = _resolve_anchor_href(self)
        return u.password if u is not None else ""

    @property
    def host(self) -> str:
        """Hostname and port (``'host:port'``), or ``''`` when href is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.host
        ''
        >>> a.href = "https://example.com:8080/path"
        >>> a.host
        'example.com:8080'
        """
        u = _resolve_anchor_href(self)
        return u.host if u is not None else ""

    @property
    def hostname(self) -> str:
        """Domain name from the resolved href, or ``''`` when href is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.hostname
        ''
        >>> a.href = "https://example.com/path"
        >>> a.hostname
        'example.com'
        """
        u = _resolve_anchor_href(self)
        return u.hostname if u is not None else ""

    @property
    def port(self) -> str:
        """Port number as a string, or ``''`` when absent or default.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.port
        ''
        >>> a.href = "https://example.com:8080/path"
        >>> a.port
        '8080'
        """
        u = _resolve_anchor_href(self)
        return u.port if u is not None else ""

    @property
    def pathname(self) -> str:
        """URL path component, or ``''`` when href is absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.pathname
        ''
        >>> a.href = "https://example.com/some/path"
        >>> a.pathname
        '/some/path'
        """
        u = _resolve_anchor_href(self)
        return u.pathname if u is not None else ""

    @property
    def search(self) -> str:
        """Query string including leading ``'?'``, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.search
        ''
        >>> a.href = "https://example.com/path?q=1"
        >>> a.search
        '?q=1'
        """
        u = _resolve_anchor_href(self)
        return u.search if u is not None else ""

    @property
    def hash(self) -> str:
        """Fragment including leading ``'#'``, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.hash
        ''
        >>> a.href = "https://example.com/path#section"
        >>> a.hash
        '#section'
        """
        u = _resolve_anchor_href(self)
        return u.hash if u is not None else ""

    @property
    def origin(self) -> str:
        """Scheme + host origin, or ``'null'`` for opaque or absent href.

        Returns ``'null'`` when href is absent, unparseable, or the scheme
        is not HTTP/HTTPS/FTP/WS/WSS (per WHATWG URL standard).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> a = doc.create_element("a")
        >>> a.origin
        'null'
        >>> a.href = "https://example.com/"
        >>> a.origin
        'https://example.com'
        """
        u = _resolve_anchor_href(self)
        return u.origin if u is not None else "null"



# ---------------------------------------------------------------------------
# Semantic / inline elements — SPEC-049 / ADR-053
# ---------------------------------------------------------------------------

class HTMLAreaElement(HTMLElement):
    """HTML ``<area>`` image-map hyperlink area.

    ``href`` resolves against document base URL via ``_get_base_url()``.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("area")
    >>> isinstance(el, HTMLAreaElement)
    True
    """

    __slots__ = ("_rel_list_cache",)

    @property
    def href(self) -> str:
        """Resolved ``href`` URL, or ``''`` when attribute is absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("area").href
        ''
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
    def target(self) -> str:
        """The ``target`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("area").target
        ''
        """
        return self.get_attribute("target") or ""

    @target.setter
    def target(self, value: str) -> None:
        self.set_attribute("target", value)

    @property
    def alt(self) -> str:
        """The ``alt`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("area").alt
        ''
        """
        return self.get_attribute("alt") or ""

    @alt.setter
    def alt(self, value: str) -> None:
        self.set_attribute("alt", value)

    @property
    def coords(self) -> str:
        """The ``coords`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("area").coords
        ''
        """
        return self.get_attribute("coords") or ""

    @coords.setter
    def coords(self, value: str) -> None:
        self.set_attribute("coords", value)

    @property
    def shape(self) -> str:
        """The ``shape`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("area").shape
        ''
        """
        return self.get_attribute("shape") or ""

    @shape.setter
    def shape(self, value: str) -> None:
        self.set_attribute("shape", value)

    @property
    def rel(self) -> str:
        """The ``rel`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("area").rel
        ''
        """
        return self.get_attribute("rel") or ""

    @rel.setter
    def rel(self, value: str) -> None:
        self.set_attribute("rel", value)

    @property
    def protocol(self) -> str:
        """Resolved URL scheme followed by ``':'``, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.protocol
        ''
        >>> area.href = "https://example.com/path"
        >>> area.protocol
        'https:'
        """
        u = _resolve_area_href(self)
        return u.protocol if u is not None else ""

    @property
    def host(self) -> str:
        """Resolved ``'host:port'``, or ``''`` when href is absent.

        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.href = "https://example.com:8443/path"
        >>> area.host
        'example.com:8443'
        """
        u = _resolve_area_href(self)
        return u.host if u is not None else ""

    @property
    def host_name(self) -> str:
        """Resolved hostname, or ``''`` when href is absent.

        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.href = "https://example.com/path"
        >>> area.host_name
        'example.com'
        """
        u = _resolve_area_href(self)
        return u.hostname if u is not None else ""

    @property
    def port(self) -> str:
        """Resolved port string, or ``''`` when absent/default.

        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.href = "https://example.com:8443/path"
        >>> area.port
        '8443'
        """
        u = _resolve_area_href(self)
        return u.port if u is not None else ""

    @property
    def path_name(self) -> str:
        """Resolved URL pathname, or ``''`` when href is absent.

        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.href = "https://example.com/docs/page.html"
        >>> area.path_name
        '/docs/page.html'
        """
        u = _resolve_area_href(self)
        return u.pathname if u is not None else ""

    @property
    def search(self) -> str:
        """Resolved query string including ``'?'``, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.href = "https://example.com/path?q=1"
        >>> area.search
        '?q=1'
        """
        u = _resolve_area_href(self)
        return u.search if u is not None else ""

    @property
    def hash(self) -> str:
        """Resolved fragment including ``'#'``, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.href = "https://example.com/path#spot"
        >>> area.hash
        '#spot'
        """
        u = _resolve_area_href(self)
        return u.hash if u is not None else ""

    @property
    def origin(self) -> str:
        """Resolved URL origin, or ``''`` when href is absent/unparseable.

        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.origin
        ''
        >>> area.href = "https://example.com/path"
        >>> area.origin
        'https://example.com'
        """
        u = _resolve_area_href(self)
        return u.origin if u is not None else ""

    # -- IDL tail additions (Track 110, ADR-309) --------------------------------

    @property
    def download(self) -> str:
        """The ``download`` attribute value, or ``''`` when absent (WHATWG HTML §4.8.2).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.download
        ''
        >>> area.download = "file.pdf"
        >>> area.download
        'file.pdf'
        """
        return self.get_attribute("download") or ""

    @download.setter
    def download(self, value: str) -> None:
        self.set_attribute("download", value)

    @property
    def rel_list(self) -> "DOMTokenList":
        """``DOMTokenList`` backed by the ``rel`` attribute (WHATWG HTML §4.8.2).

        The same instance is returned on every access.

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMTokenList
        >>> doc = Document()
        >>> area = doc.create_element("area")
        >>> isinstance(area.rel_list, DOMTokenList)
        True
        >>> area.rel_list is area.rel_list
        True
        >>> area.rel_list.add("nofollow")
        >>> area.rel
        'nofollow'
        """
        cached = getattr(self, "_rel_list_cache", None)
        if cached is None:
            from aspose_html.dom._token_list import DOMTokenList  # noqa: PLC0415
            cached = DOMTokenList(self, "rel")
            object.__setattr__(self, "_rel_list_cache", cached)
        return cached

    @property
    def referrer_policy(self) -> str:
        """The ``referrerpolicy`` attribute value, or ``''`` when absent (WHATWG HTML §4.8.2).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.referrer_policy
        ''
        >>> area.referrer_policy = "no-referrer"
        >>> area.referrer_policy
        'no-referrer'
        """
        return self.get_attribute("referrerpolicy") or ""

    @referrer_policy.setter
    def referrer_policy(self, value: str) -> None:
        self.set_attribute("referrerpolicy", value)

    @property
    def ping(self) -> str:
        """The ``ping`` attribute value, or ``''`` when absent (WHATWG HTML §4.8.2).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.ping
        ''
        >>> area.ping = "https://example.com/ping"
        >>> area.ping
        'https://example.com/ping'
        """
        return self.get_attribute("ping") or ""

    @ping.setter
    def ping(self, value: str) -> None:
        self.set_attribute("ping", value)

    @property
    def hostname(self) -> str:
        """Domain name from the resolved href, or ``''`` when href is absent (WHATWG HTML §4.8.2).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.hostname
        ''
        >>> area.href = "https://example.com/path"
        >>> area.hostname
        'example.com'
        """
        u = _resolve_area_href(self)
        return u.hostname if u is not None else ""

    @property
    def pathname(self) -> str:
        """URL path component, or ``''`` when href is absent (WHATWG HTML §4.8.2).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> area = Document().create_element("area")
        >>> area.pathname
        ''
        >>> area.href = "https://example.com/path"
        >>> area.pathname
        '/path'
        """
        u = _resolve_area_href(self)
        return u.pathname if u is not None else ""


class HTMLMapElement(HTMLElement):
    """HTML ``<map>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("map"), HTMLMapElement)
    True
    """

    __slots__ = ()

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("map").name
        ''
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def areas(self) -> "HTMLCollection":
        """Live collection of descendant ``<area>`` elements.

        The returned collection is live and re-evaluates against the map
        subtree on each access, so append/remove mutations are reflected
        immediately.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> map_el = doc.create_element("map")
        >>> len(map_el.areas)
        0
        >>> map_el.append_child(doc.create_element("area"))
        <Element 'AREA'>
        >>> len(map_el.areas)
        1
        """
        from aspose_html.dom._collections import _SubtreeHTMLCollection  # noqa: PLC0415

        return _SubtreeHTMLCollection(
            self,
            lambda node: isinstance(node, HTMLAreaElement),
        )



