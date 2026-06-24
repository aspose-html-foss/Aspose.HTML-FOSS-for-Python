"""Inline CSS style declaration — WHATWG CSS Object Model §4.1 (simplified).

Provides a live, dict-like view of an element's ``style`` attribute.
Only inline styles are supported; computed styles are out of scope for v1.0.

See .
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from aspose_html.dom._element import Element


class CSSStyleDeclaration:
    """A live view of an element's inline style attribute.

    Reads and writes the owning element's 'style' attribute directly.
    Changes to the element's 'style' attribute from outside (e.g. via
    set_attribute('style', ...)) are immediately visible through this object
    because it re-parses the attribute on every access.

    Parameters
    ----------
    owner_element:
        The DOM element whose ``style`` attribute backs this object.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> el.style["color"] = "red"
    >>> el.get_attribute("style")
    'color: red'
    """

    __slots__ = ("_owner",)

    def __init__(self, owner_element: "Element") -> None:
        object.__setattr__(self, "_owner", owner_element)

    # ------------------------------------------------------------------
    # Internal helpers — type annotations required; no doctests ( exempt)
    # ------------------------------------------------------------------

    def _parse(self) -> dict[str, tuple[str, bool]]:
        """Parse the owner element's style attribute into a property dict.

        Returns an ordered mapping of lowercased property names to
        ``(value, is_important)`` tuples.  Called on every read operation —
        no caching (live-view contract).
        """
        raw: str = self._owner.get_attribute("style") or ""
        result: dict[str, tuple[str, bool]] = {}
        for token in raw.split(";"):
            token = token.strip()
            if not token:
                continue
            parts = token.split(":", 1)
            if len(parts) < 2:
                # Malformed declaration (no colon) — skip silently ()
                continue
            name = parts[0].strip().lower()
            value = parts[1].strip()
            if not name:
                continue
            is_important = False
            if value.lower().endswith("!important"):
                value = value[: -len("!important")].strip()
                is_important = True
            result[name] = (value, is_important)
        return result

    def _serialise(self, styles: dict[str, tuple[str, bool]]) -> str:
        """Serialise a property dict back to an inline style string.

        Returns ``""`` for an empty dict.
        """
        if not styles:
            return ""
        parts = []
        for k, (v, important) in styles.items():
            parts.append(f"{k}: {v} !important" if important else f"{k}: {v}")
        return "; ".join(parts)

    # ------------------------------------------------------------------
    # Public dict-protocol methods
    # ------------------------------------------------------------------

    def __getitem__(self, property_name: str) -> str:
        """Return the value of the named CSS property, or ``''`` if not set.

        Parameters
        ----------
        property_name:
            CSS property name (case-insensitive; normalised to lowercase).

        Returns
        -------
        str
            The property value, or ``''`` if the property is absent.
            Never raises ``KeyError``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("style", "color: red")
        >>> el.style["color"]
        'red'
        >>> el.style["font-size"]
        ''
        """
        result = self._parse().get(property_name.lower().strip())
        return result[0] if result is not None else ""

    def __setitem__(self, property_name: str, value: str) -> None:
        """Set the named CSS property to *value*.

        Writes back to the element's ``style`` attribute immediately.

        Parameters
        ----------
        property_name:
            CSS property name (normalised to lowercase on write).
        value:
            CSS value string. No validation is performed.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style["color"] = "blue"
        >>> el.get_attribute("style")
        'color: blue'
        """
        styles = self._parse()
        name = property_name.lower().strip()
        if name:
            styles[name] = (value, False)
        self._owner.set_attribute("style", self._serialise(styles))

    def __delitem__(self, property_name: str) -> None:
        """Remove the named CSS property from the inline style.

        No-op if the property is not present. When the last property is
        removed, the ``style`` attribute is removed from the element entirely.

        Parameters
        ----------
        property_name:
            CSS property name (case-insensitive).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style["color"] = "blue"
        >>> del el.style["color"]
        >>> el.style["color"]
        ''
        """
        styles = self._parse()
        styles.pop(property_name.lower(), None)  # no-op if absent ()
        result = self._serialise(styles)
        if result == "":
            self._owner.remove_attribute("style")
        else:
            self._owner.set_attribute("style", result)

    def __contains__(self, property_name: object) -> bool:
        """Return ``True`` if the named property is present in the inline style.

        Parameters
        ----------
        property_name:
            CSS property name to check. Accepts ``object`` to satisfy the
            ``__contains__`` protocol.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style["margin"] = "0"
        >>> "margin" in el.style
        True
        >>> "padding" in el.style
        False
        """
        return property_name in self._parse()

    def __len__(self) -> int:
        """Return the number of properties in the inline style.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> len(el.style)
        0
        >>> el.style["color"] = "red"
        >>> len(el.style)
        1
        """
        return len(self._parse())

    def __iter__(self) -> Iterator[str]:
        """Iterate over property names in declaration order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("style", "color: red; font-size: 12px")
        >>> list(el.style)
        ['color', 'font-size']
        """
        return iter(self._parse())

    def __repr__(self) -> str:
        return f"CSSStyleDeclaration({self._parse()!r})"

    # ------------------------------------------------------------------
    # CSSOM-compatible named methods (snake_cased per )
    # ------------------------------------------------------------------

    @property
    def css_text(self) -> str:
        """The full inline style string (raw attribute value).

        Setting this property replaces the entire ``style`` attribute.
        Setting to an empty or whitespace-only string removes the attribute.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style.css_text = "color: red; margin: 0"
        >>> el.style.css_text
        'color: red; margin: 0'
        """
        return self._owner.get_attribute("style") or ""

    @css_text.setter
    def css_text(self, value: str) -> None:
        if value.strip() == "":
            self._owner.remove_attribute("style")
        else:
            self._owner.set_attribute("style", value)

    @property
    def length(self) -> int:
        """The number of CSS properties in the declaration block.

        Per CSSOM §6.1: returns the number of CSS declarations.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style.length
        0
        >>> el.style["color"] = "red"
        >>> el.style["margin"] = "4px"
        >>> el.style.length
        2
        """
        return len(self._parse())

    def item(self, index: int) -> str:
        """Return the CSS property name at *index*, or ``''`` if out of range.

        Per CSSOM §6.1: returns the property name at the given 0-based index
        in declaration order, or ``''`` when *index* is out of range.

        Parameters
        ----------
        index:
            0-based position in the declaration block.

        Returns
        -------
        str
            The property name (e.g. ``'color'``) or ``''``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style["color"] = "red"
        >>> el.style.item(0)
        'color'
        >>> el.style.item(99)
        ''
        >>> el.style.item(-1)
        ''
        """
        props = list(self._parse().keys())
        return props[index] if 0 <= index < len(props) else ""

    def get_property_value(self, property_name: str) -> str:
        """Return the value of the named property, or ``''`` if not set.

        Equivalent to ``self[property_name]``.

        Parameters
        ----------
        property_name:
            CSS property name (case-insensitive).

        Returns
        -------
        str
            The property value or ``''``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style["color"] = "green"
        >>> el.style.get_property_value("color")
        'green'
        """
        return self[property_name]

    def get_property_priority(self, property_name: str) -> str:
        """Return ``"important"`` if *property_name* carries ``!important``, else ``""``.

        Parameters
        ----------
        property_name:
            CSS property name (case-insensitive).

        Returns
        -------
        str
            ``"important"`` or ``""``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style.set_property("color", "red", "important")
        >>> el.style.get_property_priority("color")
        'important'
        >>> el.style.get_property_priority("background-color")
        ''
        """
        result = self._parse().get(property_name.lower().strip())
        if result is None:
            return ""
        return "important" if result[1] else ""

    def set_property(self, property_name: str, value: str, priority: str = "") -> None:
        """Set the named property to *value*, optionally with ``!important`` priority.

        Parameters
        ----------
        property_name:
            CSS property name.
        value:
            CSS value string.
        priority:
            ``"important"`` to mark the declaration as ``!important``,
            or ``""`` (default) for normal priority.  Any other value is
            treated as ``""`` (matches browser behaviour — no error raised).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style.set_property("color", "red")
        >>> el.style["color"]
        'red'
        >>> el.style.set_property("margin", "0", "important")
        >>> el.style.get_property_priority("margin")
        'important'
        >>> el.get_attribute("style")
        'color: red; margin: 0 !important'
        """
        styles = self._parse()
        name = property_name.lower().strip()
        is_important = priority.strip().lower() == "important"
        if name:
            styles[name] = (value.strip(), is_important)
        self._owner.set_attribute("style", self._serialise(styles))

    def set_property_priority(self, property_name: str, priority: str) -> None:
        """Set the priority for an existing inline property (CSSOM §6.1).

        If *property_name* is not present in the inline style, the call is
        silently ignored. *priority* must be ``''`` (normal) or
        ``'important'``; other values are accepted without error (no
        validation is performed — matches browser behaviour).

        Parameters
        ----------
        property_name:
            CSS property name (case-insensitive).
        priority:
            ``'important'`` to mark the declaration as ``!important``, or
            ``''`` to clear the priority flag.

        Examples
        --------
        >>> import aspose_html
        >>> doc = aspose_html.HTMLDocument.parse('<p style="color: red">hi</p>')
        >>> p = doc.query_selector('p')
        >>> p.style.set_property_priority('color', 'important')
        >>> p.style.get_property_priority('color')
        'important'
        >>> p.style.set_property_priority('margin', 'important')  # absent — no-op
        """
        name = property_name.lower().strip()
        parsed = self._parse()
        if name not in parsed:
            return
        value, _ = parsed[name]
        parsed[name] = (value, priority.strip().lower() == "important")
        self._owner.set_attribute("style", self._serialise(parsed))

    def remove_property(self, property_name: str) -> str:
        """Remove the named property and return its previous value (or ``''``).

        Parameters
        ----------
        property_name:
            CSS property name to remove.

        Returns
        -------
        str
            The previous value of the property, or ``''`` if it was absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style["color"] = "red"
        >>> el.style.remove_property("color")
        'red'
        >>> el.style["color"]
        ''
        """
        old = self[property_name]
        del self[property_name]
        return old

    @property
    def parent_rule(self) -> None:
        """Always ``None`` — inline styles have no parent rule (CSSOM §6.1).

        Per CSSOM §6.1 the ``parentRule`` attribute of an inline style
        declaration is always ``null``.  This property exists for IDL
        conformance.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.style.parent_rule is None
        True
        """
        return None
