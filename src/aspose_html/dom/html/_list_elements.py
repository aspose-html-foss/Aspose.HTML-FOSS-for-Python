"""List element classes.

Contains ``HTMLUListElement``, ``HTMLOListElement``,
``HTMLLIElement``, ``HTMLDListElement``.

See  for the split rationale.
"""
from __future__ import annotations

from aspose_html.dom._html_element import HTMLElement


# ---------------------------------------------------------------------------
# HTML list subclasses  ( / )
# ---------------------------------------------------------------------------

class HTMLUListElement(HTMLElement):
    """HTML ``<ul>`` unordered list element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLUListElement
    >>> doc = Document()
    >>> ul = doc.create_element("ul")
    >>> isinstance(ul, HTMLUListElement)
    True
    """

    __slots__ = ()



class HTMLOListElement(HTMLElement):
    """HTML ``<ol>`` ordered list element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLOListElement
    >>> doc = Document()
    >>> ol = doc.create_element("ol")
    >>> isinstance(ol, HTMLOListElement)
    True
    >>> ol.start
    1
    """

    __slots__ = ()

    @property
    def reversed(self) -> bool:
        """Boolean IDL attribute reflecting ``'reversed'``."""
        return self.has_attribute("reversed")

    @reversed.setter
    def reversed(self, value: bool) -> None:
        if value:
            self.set_attribute("reversed", "")
        else:
            self.remove_attribute("reversed")

    @property
    def start(self) -> int:
        """Integer IDL attribute reflecting ``'start'``. Default ``1``."""
        try:
            return int(self.get_attribute("start") or 1)
        except ValueError:
            return 1

    @start.setter
    def start(self, value: int) -> None:
        self.set_attribute("start", str(value))

    @property
    def type_(self) -> str:
        """String IDL attribute reflecting ``'type'``. Maps to HTML ``type`` attribute."""
        return self.get_attribute("type") or ""

    @type_.setter
    def type_(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def type(self) -> str:
        """Reflect the ``type`` content attribute (WHATWG HTML §4.4.5).

        Returns the list numbering style (``'1'``, ``'A'``, ``'a'``, ``'I'``,
        ``'i'``), or ``''`` when absent.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); ol = doc.create_element('ol')
        >>> ol.type
        ''
        >>> ol.set_attribute('type', 'A'); ol.type
        'A'
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def compact(self) -> bool:
        """Whether the boolean ``compact`` attribute is present (WHATWG HTML §4.4.5).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); ol = doc.create_element('ol')
        >>> ol.compact
        False
        >>> ol.set_attribute('compact', ''); ol.compact
        True
        """
        return self.has_attribute("compact")

    @compact.setter
    def compact(self, value: bool) -> None:
        if value:
            self.set_attribute("compact", "")
        else:
            self.remove_attribute("compact")


class HTMLLIElement(HTMLElement):
    """HTML ``<li>`` list item element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLLIElement
    >>> doc = Document()
    >>> li = doc.create_element("li")
    >>> isinstance(li, HTMLLIElement)
    True
    >>> li.value
    0
    """

    __slots__ = ()

    @property
    def value(self) -> int:
        """Integer IDL attribute reflecting ``'value'``. Default ``0``."""
        try:
            return int(self.get_attribute("value") or 0)
        except ValueError:
            return 0

    @value.setter
    def value(self, v: int) -> None:
        self.set_attribute("value", str(v))

    @property
    def type_(self) -> str:
        """String IDL attribute reflecting ``'type'``."""
        return self.get_attribute("type") or ""

    @type_.setter
    def type_(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def type(self) -> str:
        """Reflect the ``type`` content attribute (WHATWG HTML §4.4.8).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> doc = Document(); el = doc.create_element('li')
        >>> el.type
        ''
        >>> el.set_attribute('type', 'A'); el.type
        'A'
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)



class HTMLDListElement(HTMLElement):
    """HTML ``<dl>`` definition list element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLDListElement
    >>> doc = Document()
    >>> dl = doc.create_element("dl")
    >>> isinstance(dl, HTMLDListElement)
    True
    """

    __slots__ = ()


# ---------------------------------------------------------------------------
# HTMLTextAreaElement  ( / )
# ---------------------------------------------------------------------------


