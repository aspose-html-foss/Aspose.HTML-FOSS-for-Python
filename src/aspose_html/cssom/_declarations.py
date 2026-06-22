"""CSS declaration block helpers for CSSOM rule bodies.

This baseline parser/serializer is intentionally minimal for BACK-81.
Extended in BACK-307 (Track 86) to add CSSOM §6.1 IDL completeness:
length, item, parent_rule, get_property_priority, set_property_priority.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from ._rules import CSSRule


class CSSDeclarationBlock:
    """A small CSSStyleDeclaration-compatible declaration container.

    Internal storage uses ``dict[str, tuple[str, str]]`` mapping property
    names to ``(value, priority)`` pairs where priority is ``''`` or
    ``'important'``.

    Examples
    --------
    >>> decl = CSSDeclarationBlock()
    >>> decl.set_property("color", "red")
    >>> decl.css_text
    'color: red'
    """

    __slots__ = ("_properties", "_parent_rule")

    def __init__(self, properties: dict[str, str] | None = None) -> None:
        # Accept legacy dict[str, str] input and normalise to tuple format.
        self._properties: dict[str, tuple[str, str]] = {
            k: (v, "") for k, v in (properties or {}).items()
        }
        self._parent_rule: "CSSRule | None" = None

    @classmethod
    def parse(cls, text: str) -> "CSSDeclarationBlock":
        """Parse a ``name:value`` declaration list.

        Examples
        --------
        >>> b = CSSDeclarationBlock.parse("color: red; font-weight: bold")
        >>> b.get_property_value("color")
        'red'
        >>> b.get_property_value("font-weight")
        'bold'
        """
        properties: dict[str, str] = {}
        for token in text.split(";"):
            token = token.strip()
            if not token:
                continue
            name_value = token.split(":", 1)
            if len(name_value) != 2:
                continue
            name = name_value[0].strip().lower()
            value = name_value[1].strip()
            if name:
                properties[name] = value
        return cls(properties)

    # ------------------------------------------------------------------
    # CSSOM §6.1 IDL properties
    # ------------------------------------------------------------------

    @property
    def length(self) -> int:
        """Number of CSS property declarations in this block (CSSOM §6.1).

        Examples
        --------
        >>> b = CSSDeclarationBlock.parse("color: red; font-weight: bold")
        >>> b.length
        2
        """
        return len(self._properties)

    def item(self, index: int) -> str:
        """Return the property name at *index*, or ``''`` if out of range (CSSOM §6.1).

        Examples
        --------
        >>> b = CSSDeclarationBlock.parse("color: red; margin: 0")
        >>> b.item(0)
        'color'
        >>> b.item(99)
        ''
        >>> b.item(-1)
        ''
        """
        keys = list(self._properties.keys())
        if 0 <= index < len(keys):
            return keys[index]
        return ""

    @property
    def parent_rule(self) -> "CSSRule | None":
        """The CSSRule that owns this declaration block, or ``None`` (CSSOM §6.1).

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red }")
        >>> sheet.css_rules[0].style.parent_rule is sheet.css_rules[0]
        True
        """
        return self._parent_rule

    def get_property_priority(self, property_name: str) -> str:
        """Return ``'important'`` if the property is declared ``!important``, else ``''``.

        Examples
        --------
        >>> b = CSSDeclarationBlock()
        >>> b.set_property("color", "red")
        >>> b.set_property_priority("color", "important")
        >>> b.get_property_priority("color")
        'important'
        >>> b.get_property_priority("margin")
        ''
        """
        return self._properties.get(property_name.lower(), ("", ""))[1]

    def set_property_priority(self, property_name: str, priority: str) -> None:
        """Set the priority (``''`` or ``'important'``) for an existing property.

        If *property_name* is not present, the call is silently ignored.

        Examples
        --------
        >>> b = CSSDeclarationBlock()
        >>> b.set_property("color", "red")
        >>> b.set_property_priority("color", "important")
        >>> b.css_text
        'color: red !important'
        """
        name = property_name.lower()
        if name in self._properties:
            value = self._properties[name][0]
            self._properties[name] = (value, priority)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @property
    def css_text(self) -> str:
        """Canonical declaration serialization.

        Examples
        --------
        >>> decl = CSSDeclarationBlock.parse("color: red; margin: 0")
        >>> decl.css_text
        'color: red; margin: 0'
        """
        parts = []
        for name, (value, priority) in self._properties.items():
            if priority == "important":
                parts.append(f"{name}: {value} !important")
            else:
                parts.append(f"{name}: {value}")
        return "; ".join(parts)

    @css_text.setter
    def css_text(self, value: str) -> None:
        parsed = self.parse(value)
        self._properties = parsed._properties

    # ------------------------------------------------------------------
    # CSSOM-compatible named methods
    # ------------------------------------------------------------------

    def get_property_value(self, property_name: str) -> str:
        """Return the property value or ``''`` when absent.

        Examples
        --------
        >>> b = CSSDeclarationBlock.parse("color: red")
        >>> b.get_property_value("color")
        'red'
        >>> b.get_property_value("margin")
        ''
        """
        return self._properties.get(property_name.lower(), ("", ""))[0]

    def set_property(self, property_name: str, value: str) -> None:
        """Set a property value (normal priority).

        Examples
        --------
        >>> b = CSSDeclarationBlock()
        >>> b.set_property("color", "blue")
        >>> b.get_property_value("color")
        'blue'
        """
        self._properties[property_name.lower()] = (value, "")

    def remove_property(self, property_name: str) -> str:
        """Remove and return a property's previous value, if present.

        Examples
        --------
        >>> b = CSSDeclarationBlock.parse("color: red")
        >>> b.remove_property("color")
        'red'
        >>> b.remove_property("margin")
        ''
        """
        return self._properties.pop(property_name.lower(), ("", ""))[0]

    # ------------------------------------------------------------------
    # Python collection protocol
    # ------------------------------------------------------------------

    def __getitem__(self, property_name: str) -> str:
        return self.get_property_value(property_name)

    def __setitem__(self, property_name: str, value: str) -> None:
        self.set_property(property_name, value)

    def __delitem__(self, property_name: str) -> None:
        self.remove_property(property_name)

    def __iter__(self) -> Iterator[str]:
        return iter(self._properties)

    def __len__(self) -> int:
        return len(self._properties)
