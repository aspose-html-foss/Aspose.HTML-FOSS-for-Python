"""Text and flow element classes.

Contains ``HTMLDivElement``, ``HTMLSpanElement``, ``HTMLParagraphElement``,
``HTMLHeadingElement``, ``HTMLQuoteElement``, ``HTMLTimeElement``,
``HTMLDataElement``, ``HTMLUnknownElement``.

See  for the split rationale.
"""
from __future__ import annotations

from aspose_html.dom._html_element import HTMLElement


# ---------------------------------------------------------------------------
# HTMLDivElement  ( / )
# ---------------------------------------------------------------------------

class HTMLDivElement(HTMLElement):
    """HTML ``<div>`` block container element.

    No IDL-reflected attributes beyond those inherited from ``HTMLElement``.
    This class exists for correct ``isinstance`` dispatch.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLDivElement
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> isinstance(el, HTMLDivElement)
    True
    """

    __slots__ = ()


# ---------------------------------------------------------------------------
# HTMLSpanElement  ( / )
# ---------------------------------------------------------------------------

class HTMLSpanElement(HTMLElement):
    """HTML ``<span>`` inline container element.

    No IDL-reflected attributes beyond those inherited from ``HTMLElement``.
    This class exists for correct ``isinstance`` dispatch.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLSpanElement
    >>> doc = Document()
    >>> el = doc.create_element("span")
    >>> isinstance(el, HTMLSpanElement)
    True
    """

    __slots__ = ()


# ---------------------------------------------------------------------------
# HTMLParagraphElement  ( / )
# ---------------------------------------------------------------------------

class HTMLParagraphElement(HTMLElement):
    """HTML ``<p>`` paragraph element.

    No IDL-reflected attributes beyond those inherited from ``HTMLElement``.
    This class exists for correct ``isinstance`` dispatch.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLParagraphElement
    >>> doc = Document()
    >>> el = doc.create_element("p")
    >>> isinstance(el, HTMLParagraphElement)
    True
    """

    __slots__ = ()


# ---------------------------------------------------------------------------
# HTMLHeadingElement  ( / )
# ---------------------------------------------------------------------------

class HTMLHeadingElement(HTMLElement):
    """HTML heading element — covers ``<h1>`` through ``<h6>``.

    All six heading tag names map to this single class.  The actual tag name
    (``"h1"`` … ``"h6"``) is preserved on the element as usual via
    ``element.tag_name`` / ``element.local_name``.

    No IDL-reflected attributes beyond those inherited from ``HTMLElement``.
    This class exists for correct ``isinstance`` dispatch.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLHeadingElement
    >>> doc = Document()
    >>> h1 = doc.create_element("h1")
    >>> isinstance(h1, HTMLHeadingElement)
    True
    >>> h6 = doc.create_element("h6")
    >>> isinstance(h6, HTMLHeadingElement)
    True
    """

    __slots__ = ()

# ---------------------------------------------------------------------------
# HTMLTableElement and table-related subclasses  ( / )
# ---------------------------------------------------------------------------


class HTMLTimeElement(HTMLElement):
    """HTML ``<time>`` element.

    Reflects the HTML ``datetime`` attribute as ``date_time``.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("time"), HTMLTimeElement)
    True
    """

    __slots__ = ()

    @property
    def date_time(self) -> str:
        """The ``datetime`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("time").date_time
        ''
        """
        return self.get_attribute("datetime") or ""

    @date_time.setter
    def date_time(self, value: str) -> None:
        self.set_attribute("datetime", value)



class HTMLDataElement(HTMLElement):
    """HTML ``<data>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("data"), HTMLDataElement)
    True
    """

    __slots__ = ()

    @property
    def value(self) -> str:
        """The ``value`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("data").value
        ''
        """
        return self.get_attribute("value") or ""

    @value.setter
    def value(self, value: str) -> None:
        self.set_attribute("value", value)



class HTMLQuoteElement(HTMLElement):
    """HTML ``<blockquote>``/``<q>`` quote element.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("blockquote"), HTMLQuoteElement)
    True
    """

    __slots__ = ()

    @property
    def cite(self) -> str:
        """The ``cite`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc.create_element("q").cite
        ''
        """
        return self.get_attribute("cite") or ""

    @cite.setter
    def cite(self, value: str) -> None:
        self.set_attribute("cite", value)



class HTMLUnknownElement(HTMLElement):
    """HTML unknown element interface (export-only, not registry-dispatched).

    Examples
    --------
    >>> from aspose_html.dom import HTMLUnknownElement
    >>> issubclass(HTMLUnknownElement, HTMLElement)
    True
    """

    __slots__ = ()


# ---------------------------------------------------------------------------
# HTMLSummaryElement  ( / )
# ---------------------------------------------------------------------------


