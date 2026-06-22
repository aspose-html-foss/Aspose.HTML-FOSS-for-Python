"""Embedded content element classes.

Contains ``HTMLImageElement``, ``HTMLIFrameElement``, ``HTMLEmbedElement``,
``HTMLObjectElement``, ``HTMLCanvasElement``, ``HTMLParamElement``.

See ADR-304 for the split rationale.
"""
from __future__ import annotations

import re

from aspose_html.dom._html_element import HTMLElement
from aspose_html.dom._validation import ValidityState, _ConstraintValidationMixin
from aspose_html.dom.html._form_elements import _get_form_owner


# ---------------------------------------------------------------------------
# HTMLImageElement
# ---------------------------------------------------------------------------

class HTMLImageElement(HTMLElement):
    """HTML ``<img>`` image element.

    Reflects ``src``, ``alt``, ``width``, ``height``, ``srcset``, ``sizes``,
    ``loading``, ``decoding``, ``cross_origin``, ``use_map``, ``is_map`` IDL
    attributes, and the headless stubs ``complete``, ``natural_width``,
    ``natural_height`` (always ``False``/``0``).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> img = doc.create_element("img")
    >>> isinstance(img, HTMLImageElement)
    True
    >>> img.src
    ''
    >>> img.width
    0
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def src(self) -> str:
        """The ``src`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.src
        ''
        >>> img.src = "photo.jpg"
        >>> img.src
        'photo.jpg'
        """
        return self.get_attribute("src") or ""

    @src.setter
    def src(self, value: str) -> None:
        self.set_attribute("src", value)

    @property
    def alt(self) -> str:
        """The ``alt`` attribute value, or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.alt
        ''
        >>> img.alt = "A photo"
        >>> img.alt
        'A photo'
        """
        return self.get_attribute("alt") or ""

    @alt.setter
    def alt(self, value: str) -> None:
        self.set_attribute("alt", value)

    @property
    def width(self) -> int:
        """The ``width`` attribute as an integer (default ``0``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.width
        0
        >>> img.width = 320
        >>> img.width
        320
        """
        try:
            return int(self.get_attribute("width") or 0)
        except ValueError:
            return 0

    @width.setter
    def width(self, value: int) -> None:
        self.set_attribute("width", str(value))

    @property
    def height(self) -> int:
        """The ``height`` attribute as an integer (default ``0``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.height
        0
        >>> img.height = 240
        >>> img.height
        240
        """
        try:
            return int(self.get_attribute("height") or 0)
        except ValueError:
            return 0

    @height.setter
    def height(self, value: int) -> None:
        self.set_attribute("height", str(value))

    @property
    def srcset(self) -> str:
        """The ``srcset`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.srcset
        ''
        >>> img.srcset = "img@2x.png 2x"
        >>> img.srcset
        'img@2x.png 2x'
        """
        return self.get_attribute("srcset") or ""

    @srcset.setter
    def srcset(self, value: str) -> None:
        self.set_attribute("srcset", value)

    @property
    def sizes(self) -> str:
        """The ``sizes`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.sizes
        ''
        >>> img.sizes = "(max-width: 600px) 480px, 800px"
        >>> img.sizes
        '(max-width: 600px) 480px, 800px'
        """
        return self.get_attribute("sizes") or ""

    @sizes.setter
    def sizes(self, value: str) -> None:
        self.set_attribute("sizes", value)

    @property
    def loading(self) -> str:
        """The ``loading`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.loading
        ''
        >>> img.loading = "lazy"
        >>> img.loading
        'lazy'
        """
        return self.get_attribute("loading") or ""

    @loading.setter
    def loading(self, value: str) -> None:
        self.set_attribute("loading", value)

    @property
    def decoding(self) -> str:
        """The ``decoding`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.decoding
        ''
        >>> img.decoding = "async"
        >>> img.decoding
        'async'
        """
        return self.get_attribute("decoding") or ""

    @decoding.setter
    def decoding(self, value: str) -> None:
        self.set_attribute("decoding", value)

    @property
    def cross_origin(self) -> str | None:
        """The ``crossorigin`` attribute value, or ``None`` when absent.

        ``None`` means no CORS request (WHATWG §2.6.4).  The empty string
        ``""`` is never returned — absent attribute → ``None``.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.cross_origin is None
        True
        >>> img.cross_origin = "anonymous"
        >>> img.cross_origin
        'anonymous'
        >>> img.cross_origin = None
        >>> img.cross_origin is None
        True
        """
        return self.get_attribute("crossorigin")

    @cross_origin.setter
    def cross_origin(self, value: str | None) -> None:
        if value is None:
            self.remove_attribute("crossorigin")
        else:
            self.set_attribute("crossorigin", value)

    @property
    def use_map(self) -> str:
        """The ``usemap`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.use_map
        ''
        >>> img.use_map = "#mymap"
        >>> img.use_map
        '#mymap'
        """
        return self.get_attribute("usemap") or ""

    @use_map.setter
    def use_map(self, value: str) -> None:
        self.set_attribute("usemap", value)

    @property
    def is_map(self) -> bool:
        """Whether the ``ismap`` boolean attribute is present.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.is_map
        False
        >>> img.is_map = True
        >>> img.is_map
        True
        >>> img.is_map = False
        >>> img.is_map
        False
        """
        return self.has_attribute("ismap")

    @is_map.setter
    def is_map(self, value: bool) -> None:
        if value:
            self.set_attribute("ismap", "")
        else:
            self.remove_attribute("ismap")

    @property
    def complete(self) -> bool:
        """Always ``False`` in headless mode (no network fetch).

        WHATWG §4.8.3.2: an image is "completely available" only when
        its source has been fully fetched and decoded — neither applies
        in headless mode.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.complete
        False
        """
        return False

    @property
    def natural_width(self) -> int:
        """Always ``0`` in headless mode (no layout engine).

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.natural_width
        0
        """
        return 0

    @property
    def natural_height(self) -> int:
        """Always ``0`` in headless mode (no layout engine).

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.natural_height
        0
        """
        return 0

    @property
    def current_src(self) -> str:
        """Current selected source URL (headless: reflects ``src`` attribute).

        WHATWG HTML §4.8.4.1: in headless mode the current request is the
        ``src`` content attribute value.

        >>> from aspose_html.dom import Document
        >>> img = Document().create_element("img")
        >>> img.current_src
        ''
        >>> img.src = "photo.jpg"
        >>> img.current_src
        'photo.jpg'
        """
        return self.get_attribute("src") or ""

    @property
    def referrer_policy(self) -> str:
        """Reflect the ``referrerpolicy`` attribute; default ``''``.

        >>> from aspose_html.dom import Document
        >>> img = Document().create_element("img")
        >>> img.referrer_policy
        ''
        >>> img.referrer_policy = "no-referrer"
        >>> img.referrer_policy
        'no-referrer'
        """
        return self.get_attribute("referrerpolicy") or ""

    @referrer_policy.setter
    def referrer_policy(self, value: str) -> None:
        self.set_attribute("referrerpolicy", value)

    @property
    def fetch_priority(self) -> str:
        """Reflect the ``fetchpriority`` attribute; default ``''``.

        >>> from aspose_html.dom import Document
        >>> img = Document().create_element("img")
        >>> img.fetch_priority
        ''
        >>> img.fetch_priority = "high"
        >>> img.fetch_priority
        'high'
        """
        return self.get_attribute("fetchpriority") or ""

    @fetch_priority.setter
    def fetch_priority(self, value: str) -> None:
        self.set_attribute("fetchpriority", value)

    @property
    def x(self) -> int:
        """Horizontal layout position stub — always ``0`` in headless mode.

        CSSOM View §7.2: ``x`` reflects the element's left border-box edge
        relative to the viewport. No layout engine is available in headless mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.x
        0
        """
        return 0

    @property
    def y(self) -> int:
        """Vertical layout position stub — always ``0`` in headless mode.

        CSSOM View §7.2: ``y`` reflects the element's top border-box edge
        relative to the viewport. No layout engine is available in headless mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> img = doc.create_element("img")
        >>> img.y
        0
        """
        return 0

    def decode(self) -> None:
        """Decode the image (not supported in headless mode).

        WHATWG HTML §4.8.3.6: returns a Promise in browsers; raises
        ``NotImplementedError`` in headless mode because no image decoding
        pipeline is available.

        Raises:
            NotImplementedError: always — headless mode has no image pipeline.

        >>> from aspose_html.dom import Document
        >>> img = Document().create_element("img")
        >>> try:
        ...     img.decode()
        ... except NotImplementedError:
        ...     print("not supported")
        not supported
        """
        raise NotImplementedError(
            "HTMLImageElement.decode() is not supported in headless mode."
        )


# ---------------------------------------------------------------------------
# Embedding elements — SPEC-049 / ADR-053
# ---------------------------------------------------------------------------

class HTMLIFrameElement(HTMLElement):
    """HTML ``<iframe>`` element.

    Reflects ``src``, ``name``, ``allow``, ``sandbox`` as string properties;
    ``width`` and ``height`` as integer properties (default ``0``).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("iframe")
    >>> isinstance(el, HTMLIFrameElement)
    True
    """

    __slots__ = ()

    @property
    def src(self) -> str:
        """The ``src`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.src
        ''
        """
        return self.get_attribute("src") or ""

    @src.setter
    def src(self, value: str) -> None:
        self.set_attribute("src", value)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("iframe").name
        ''
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def allow(self) -> str:
        """The ``allow`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("iframe").allow
        ''
        """
        return self.get_attribute("allow") or ""

    @allow.setter
    def allow(self, value: str) -> None:
        self.set_attribute("allow", value)

    @property
    def sandbox(self) -> str:
        """The ``sandbox`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("iframe").sandbox
        ''
        """
        return self.get_attribute("sandbox") or ""

    @sandbox.setter
    def sandbox(self, value: str) -> None:
        self.set_attribute("sandbox", value)

    @property
    def width(self) -> int:
        """The ``width`` attribute as integer (default ``0``).

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("iframe").width
        0
        """
        try:
            return int(self.get_attribute("width") or 0)
        except ValueError:
            return 0

    @width.setter
    def width(self, value: int) -> None:
        self.set_attribute("width", str(value))

    @property
    def height(self) -> int:
        """The ``height`` attribute as integer (default ``0``).

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("iframe").height
        0
        """
        try:
            return int(self.get_attribute("height") or 0)
        except ValueError:
            return 0

    @height.setter
    def height(self, value: int) -> None:
        self.set_attribute("height", str(value))

    @property
    def content_document(self) -> object | None:
        """The embedded document, or ``None`` in headless mode.

        Track 58 ownership boundary: ``HTMLIFrameElement`` does not create
        embedded document objects itself. Resolution is delegated to the
        owning ``BrowsingContext`` when available.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.content_document is None
        True
        """
        doc = self.owner_document
        if doc is None:
            return None
        view = doc.default_view
        if view is None:
            return None
        ctx = getattr(view, "_browsing_context", None)
        if ctx is None:
            return None
        return ctx.iframe_content_document_for(self)

    @property
    def content_window(self) -> object | None:
        """The embedded browsing-context window, or ``None`` in headless mode.

        Track 58 ownership boundary: ``HTMLIFrameElement`` does not create
        embedded window objects itself. Resolution is delegated to the owning
        ``BrowsingContext`` when available.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.content_window is None
        True
        """
        doc = self.owner_document
        if doc is None:
            return None
        view = doc.default_view
        if view is None:
            return None
        ctx = getattr(view, "_browsing_context", None)
        if ctx is None:
            return None
        return ctx.iframe_content_window_for(self)

    @property
    def srcdoc(self) -> str:
        """The ``srcdoc`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.srcdoc
        ''
        >>> el.srcdoc = '<p>hello</p>'
        >>> el.srcdoc
        '<p>hello</p>'
        """
        return self.get_attribute("srcdoc") or ""

    @srcdoc.setter
    def srcdoc(self, value: str) -> None:
        self.set_attribute("srcdoc", value)

    @property
    def referrer_policy(self) -> str:
        """The ``referrerpolicy`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.referrer_policy
        ''
        >>> el.referrer_policy = 'no-referrer'
        >>> el.referrer_policy
        'no-referrer'
        """
        return self.get_attribute("referrerpolicy") or ""

    @referrer_policy.setter
    def referrer_policy(self, value: str) -> None:
        self.set_attribute("referrerpolicy", value)

    @property
    def loading(self) -> str:
        """Reflect the ``loading`` content attribute; empty string when absent (WHATWG HTML §4.8.5).

        Valid values are ``"eager"`` and ``"lazy"``; unrecognised values return as-is.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('iframe')
        >>> el.loading
        ''
        >>> el.set_attribute('loading', 'lazy'); el.loading
        'lazy'
        """
        return self.get_attribute("loading") or ""

    @loading.setter
    def loading(self, value: str) -> None:
        self.set_attribute("loading", value)

    @property
    def allow_fullscreen(self) -> bool:
        """Whether the ``allowfullscreen`` boolean attribute is present (WHATWG HTML §4.8.5).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('iframe')
        >>> el.allow_fullscreen
        False
        >>> el.set_attribute('allowfullscreen', ''); el.allow_fullscreen
        True
        """
        return self.has_attribute("allowfullscreen")

    @allow_fullscreen.setter
    def allow_fullscreen(self, value: bool) -> None:
        if value:
            self.set_attribute("allowfullscreen", "")
        else:
            self.remove_attribute("allowfullscreen")

    def get_svg_document(self):
        """Return ``None`` — no embedded SVG document in headless mode.

        WHATWG HTML §4.8.5: returns the active document if it is an SVG document.
        In headless mode there is no embedded browsing context.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.get_svg_document() is None
        True
        """
        return None

    @property
    def align(self) -> str:
        """Reflects obsolete ``align`` content attribute (WHATWG HTML §4.8.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.align
        ''
        >>> el.set_attribute("align", "center")
        >>> el.align
        'center'
        """
        return self.get_attribute("align") or ""

    @align.setter
    def align(self, value: str) -> None:
        self.set_attribute("align", value)

    @property
    def scrolling(self) -> str:
        """Reflects obsolete ``scrolling`` content attribute (WHATWG HTML §4.8.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.scrolling
        ''
        >>> el.set_attribute("scrolling", "no")
        >>> el.scrolling
        'no'
        """
        return self.get_attribute("scrolling") or ""

    @scrolling.setter
    def scrolling(self, value: str) -> None:
        self.set_attribute("scrolling", value)

    @property
    def frame_border(self) -> str:
        """Reflects obsolete ``frameborder`` content attribute (WHATWG HTML §4.8.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.frame_border
        ''
        >>> el.set_attribute("frameborder", "0")
        >>> el.frame_border
        '0'
        """
        return self.get_attribute("frameborder") or ""

    @frame_border.setter
    def frame_border(self, value: str) -> None:
        self.set_attribute("frameborder", value)

    @property
    def long_desc(self) -> str:
        """Reflects obsolete ``longdesc`` content attribute (WHATWG HTML §4.8.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.long_desc
        ''
        >>> el.set_attribute("longdesc", "desc.html")
        >>> el.long_desc
        'desc.html'
        """
        return self.get_attribute("longdesc") or ""

    @long_desc.setter
    def long_desc(self, value: str) -> None:
        self.set_attribute("longdesc", value)

    @property
    def margin_height(self) -> str:
        """Reflects obsolete ``marginheight`` content attribute (WHATWG HTML §4.8.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.margin_height
        ''
        >>> el.set_attribute("marginheight", "10")
        >>> el.margin_height
        '10'
        """
        return self.get_attribute("marginheight") or ""

    @margin_height.setter
    def margin_height(self, value: str) -> None:
        self.set_attribute("marginheight", value)

    @property
    def margin_width(self) -> str:
        """Reflects obsolete ``marginwidth`` content attribute (WHATWG HTML §4.8.5).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("iframe")
        >>> el.margin_width
        ''
        >>> el.set_attribute("marginwidth", "5")
        >>> el.margin_width
        '5'
        """
        return self.get_attribute("marginwidth") or ""

    @margin_width.setter
    def margin_width(self, value: str) -> None:
        self.set_attribute("marginwidth", value)


class HTMLEmbedElement(HTMLElement):
    """HTML ``<embed>`` element.

    Reflects ``src`` and ``type`` string properties; ``width`` and ``height``
    as integer properties (default ``0``).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("embed")
    >>> isinstance(el, HTMLEmbedElement)
    True
    """

    __slots__ = ()

    @property
    def src(self) -> str:
        """The ``src`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("embed").src
        ''
        """
        return self.get_attribute("src") or ""

    @src.setter
    def src(self, value: str) -> None:
        self.set_attribute("src", value)

    @property
    def type(self) -> str:
        """The ``type`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("embed").type
        ''
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def type_(self) -> str:
        """Reflects the ``type`` content attribute (WHATWG HTML §4.8.6).

        IDL snake_case alias for :attr:`type`, following the ``type_``
        convention used across form/media elements to avoid shadowing the
        Python built-in ``type``. Returns an empty string when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("embed")
        >>> el.type_
        ''
        >>> el.set_attribute("type", "application/pdf")
        >>> el.type_
        'application/pdf'
        """
        return self.get_attribute("type") or ""

    def get_svg_document(self):
        """Returns ``None`` in headless mode (WHATWG HTML §4.8.6).

        In a rendering context this would return the embedded SVG document
        if the embedded content is an SVG document; in headless mode the
        embedded content document is inaccessible.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("embed")
        >>> el.get_svg_document() is None
        True
        """
        return None

    @property
    def align(self) -> str:
        """The ``align`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("embed")
        >>> el.align
        ''
        >>> el.align = "middle"
        >>> el.get_attribute("align")
        'middle'
        """
        return self.get_attribute("align") or ""

    @align.setter
    def align(self, value: str) -> None:
        self.set_attribute("align", value)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("embed")
        >>> el.name
        ''
        >>> el.name = "plugin"
        >>> el.get_attribute("name")
        'plugin'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def width(self) -> int:
        """The ``width`` attribute as integer (default ``0``).

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("embed").width
        0
        """
        try:
            return int(self.get_attribute("width") or 0)
        except ValueError:
            return 0

    @width.setter
    def width(self, value: int) -> None:
        self.set_attribute("width", str(value))

    @property
    def height(self) -> int:
        """The ``height`` attribute as integer (default ``0``).

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("embed").height
        0
        """
        try:
            return int(self.get_attribute("height") or 0)
        except ValueError:
            return 0

    @height.setter
    def height(self, value: int) -> None:
        self.set_attribute("height", str(value))



class HTMLObjectElement(_ConstraintValidationMixin, HTMLElement):
    """HTML ``<object>`` element.

    Reflects ``data``, ``type``, ``name`` string properties; ``width`` and
    ``height`` as integer properties (default ``0``).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("object")
    >>> isinstance(el, HTMLObjectElement)
    True
    """

    __slots__ = ("_custom_validity_message",)

    @property
    def data(self) -> str:
        """The ``data`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("object").data
        ''
        """
        return self.get_attribute("data") or ""

    @data.setter
    def data(self, value: str) -> None:
        self.set_attribute("data", value)

    @property
    def use_map(self) -> str:
        """The ``usemap`` attribute value, or ``''`` when absent (WHATWG HTML §4.8.7).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('object')
        >>> el.use_map
        ''
        >>> el.set_attribute('usemap', '#mymap'); el.use_map
        '#mymap'
        """
        return self.get_attribute("usemap") or ""

    @use_map.setter
    def use_map(self, value: str) -> None:
        self.set_attribute("usemap", value)

    # -- Constraint validation (WHATWG HTML §4.8.7, via _ConstraintValidationMixin) ---

    @property
    def will_validate(self) -> bool:
        """Always ``False`` — ``<object>`` is not a candidate for constraint validation.

        Per WHATWG HTML §4.8.7: ``<object>`` is listed but not validatable.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().create_element('object').will_validate
        False
        """
        return False

    def _compute_validity_state(self) -> ValidityState:
        return ValidityState()

    @property
    def type(self) -> str:
        """The ``type`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("object").type
        ''
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("object").name
        ''
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def code(self) -> str:
        """The ``code`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.code
        ''
        >>> el.code = "Applet.class"
        >>> el.code
        'Applet.class'
        """
        return self.get_attribute("code") or ""

    @code.setter
    def code(self, value: str) -> None:
        self.set_attribute("code", value)

    @property
    def code_base(self) -> str:
        """The ``codebase`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.code_base
        ''
        >>> el.code_base = "https://example.com/base/"
        >>> el.get_attribute("codebase")
        'https://example.com/base/'
        """
        return self.get_attribute("codebase") or ""

    @code_base.setter
    def code_base(self, value: str) -> None:
        self.set_attribute("codebase", value)

    @property
    def code_type(self) -> str:
        """The ``codetype`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.code_type
        ''
        >>> el.code_type = "application/java"
        >>> el.get_attribute("codetype")
        'application/java'
        """
        return self.get_attribute("codetype") or ""

    @code_type.setter
    def code_type(self, value: str) -> None:
        self.set_attribute("codetype", value)

    @property
    def declare(self) -> bool:
        """Whether the boolean ``declare`` attribute is present.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.declare
        False
        >>> el.declare = True
        >>> el.has_attribute("declare")
        True
        """
        return self.has_attribute("declare")

    @declare.setter
    def declare(self, value: bool) -> None:
        if value:
            self.set_attribute("declare", "")
        else:
            self.remove_attribute("declare")

    @property
    def archive(self) -> str:
        """The ``archive`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.archive
        ''
        >>> el.archive = "app.jar"
        >>> el.archive
        'app.jar'
        """
        return self.get_attribute("archive") or ""

    @archive.setter
    def archive(self, value: str) -> None:
        self.set_attribute("archive", value)

    @property
    def standby(self) -> str:
        """The ``standby`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.standby
        ''
        >>> el.standby = "Loading…"
        >>> el.get_attribute("standby")
        'Loading…'
        """
        return self.get_attribute("standby") or ""

    @standby.setter
    def standby(self, value: str) -> None:
        self.set_attribute("standby", value)

    @property
    def width(self) -> int:
        """The ``width`` attribute as integer (default ``0``).

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("object").width
        0
        """
        try:
            return int(self.get_attribute("width") or 0)
        except ValueError:
            return 0

    @width.setter
    def width(self, value: int) -> None:
        self.set_attribute("width", str(value))

    @property
    def height(self) -> int:
        """The ``height`` attribute as integer (default ``0``).

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("object").height
        0
        """
        try:
            return int(self.get_attribute("height") or 0)
        except ValueError:
            return 0

    @height.setter
    def height(self, value: int) -> None:
        self.set_attribute("height", str(value))

    @property
    def form(self) -> "HTMLElement | None":
        """Nearest ancestor ``<form>`` element, or ``None``.

        Uses the same simplified form-owner lookup as other
        form-associated controls in this module.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<form id="f"><object id="o"></object></form>')
        >>> obj = doc.get_element_by_id("o")
        >>> obj.form is doc.get_element_by_id("f")
        True
        >>> from aspose_html.dom import Document
        >>> Document().create_element("object").form is None
        True
        """
        return _get_form_owner(self)

    @property
    def content_document(self) -> object | None:
        """The embedded document, or ``None`` in headless mode.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.content_document is None
        True
        """
        return None

    @property
    def content_window(self) -> object | None:
        """The embedded browsing-context window, or ``None`` in headless mode.

        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.content_window is None
        True
        """
        return None

    def get_svg_document(self):
        """Returns ``None`` in headless mode.

        WHATWG HTML §4.8.7 — the embedded document is inaccessible
        without a rendering context.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> el = Document().create_element("object")
        >>> el.get_svg_document() is None
        True
        """
        return None


class HTMLCanvasElement(HTMLElement):
    """HTML ``<canvas>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLCanvasElement
    >>> el = Document().create_element("canvas")
    >>> isinstance(el, HTMLCanvasElement)
    True
    >>> el.width, el.height
    (300, 150)
    """

    __slots__ = ()

    @property
    def width(self) -> int:
        """Canvas width in CSS pixels (default ``300``).

        >>> from aspose_html.dom import Document
        >>> canvas = Document().create_element("canvas")
        >>> canvas.width
        300
        >>> canvas.width = 640
        >>> canvas.width
        640
        """
        try:
            return int(self.get_attribute("width") or "300")
        except ValueError:
            return 300

    @width.setter
    def width(self, value: int) -> None:
        self.set_attribute("width", str(int(value)))

    @property
    def height(self) -> int:
        """Canvas height in CSS pixels (default ``150``).

        >>> from aspose_html.dom import Document
        >>> canvas = Document().create_element("canvas")
        >>> canvas.height
        150
        >>> canvas.height = 360
        >>> canvas.height
        360
        """
        try:
            return int(self.get_attribute("height") or "150")
        except ValueError:
            return 150

    @height.setter
    def height(self, value: int) -> None:
        self.set_attribute("height", str(int(value)))

    def get_context(self, context_id: str, options: object = None) -> None:
        """Return rendering context — always ``None`` (server-side stub).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> canvas = Document().create_element("canvas")
        >>> canvas.get_context("2d") is None
        True
        """
        return None

    def to_data_url(self, type: str = "image/png", quality: object = None) -> str:
        """Serialize canvas as a data URL (headless stub, returns ``'data:,'``).

        WHATWG HTML §4.12.5.3: in headless mode there is no pixel buffer to
        serialize, so the minimal data URL is returned.

        >>> from aspose_html.dom import Document
        >>> Document().create_element("canvas").to_data_url()
        'data:,'
        """
        return "data:,"

    def to_blob(
        self,
        callback: object,
        type: str = "image/png",
        quality: object = None,
    ) -> None:
        """Invoke ``callback`` with ``None`` (headless no-op).

        WHATWG HTML §4.12.5.5: the callback receives a ``Blob`` object;
        in headless mode there is no pixel data, so the callback is called
        with ``None``.

        >>> from aspose_html.dom import Document
        >>> results = []
        >>> Document().create_element("canvas").to_blob(results.append)
        >>> results
        [None]
        """
        callback(None)

    def transfer_control_to_offscreen(self) -> None:
        """Transfer canvas control to an OffscreenCanvas (not supported).

        WHATWG HTML §4.12.5.4: raises ``NotSupportedError`` because
        OffscreenCanvas is out of scope in headless mode.

        Raises:
            NotSupportedError: always — OffscreenCanvas is not available.

        >>> from aspose_html.dom import Document
        >>> canvas = Document().create_element("canvas")
        >>> try:
        ...     canvas.transfer_control_to_offscreen()
        ... except Exception as e:
        ...     print(type(e).__name__)
        NotSupportedError
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "OffscreenCanvas is not supported in headless mode."
        )


class HTMLParamElement(HTMLElement):
    """HTML ``<param>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLParamElement
    >>> el = Document().create_element("param")
    >>> isinstance(el, HTMLParamElement)
    True
    >>> el.name = "autoplay"
    >>> el.name
    'autoplay'
    """

    __slots__ = ()

    @property
    def name(self) -> str:
        """The ``name`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> param = Document().create_element("param")
        >>> param.name
        ''
        >>> param.name = "quality"
        >>> param.name
        'quality'
        """
        return self.get_attribute("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def value(self) -> str:
        """The ``value`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> param = Document().create_element("param")
        >>> param.value
        ''
        >>> param.value = "high"
        >>> param.value
        'high'
        """
        return self.get_attribute("value") or ""

    @value.setter
    def value(self, value: str) -> None:
        self.set_attribute("value", value)

    @property
    def type(self) -> str:
        """The ``type`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> param = Document().create_element("param")
        >>> param.type
        ''
        >>> param.type = "text/plain"
        >>> param.type
        'text/plain'
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def value_type(self) -> str:
        """The ``valuetype`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> param = Document().create_element("param")
        >>> param.value_type
        ''
        >>> param.value_type = "ref"
        >>> param.get_attribute("valuetype")
        'ref'
        """
        return self.get_attribute("valuetype") or ""

    @value_type.setter
    def value_type(self, value: str) -> None:
        self.set_attribute("valuetype", value)



