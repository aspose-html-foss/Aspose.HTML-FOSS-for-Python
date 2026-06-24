"""DOMStringMap — live dict-like view of an element's ``data-*`` attributes.

Implements the WHATWG HTML Living Standard §2.6.8 ``DOMStringMap`` interface.
Designed as a leaf module: no runtime imports from ``aspose_html``.
``Element`` is imported under ``TYPE_CHECKING`` only to avoid circular imports.
See .
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from aspose_html.dom._element import Element

_DATA_PREFIX = "data-"


def _attr_name(key: str) -> str:
    """Convert a camelCase dataset key to a ``data-*`` attribute name.

    Algorithm (WHATWG §2.6.8):

    1. Prepend ``data-``.
    2. For each uppercase letter in *key*, replace with ``-`` + lowercase.

    Examples: ``"foo"`` → ``"data-foo"``, ``"fooBar"`` → ``"data-foo-bar"``,
    ``"xmlLang"`` → ``"data-xml-lang"``.
    """
    return _DATA_PREFIX + re.sub(r"([A-Z])", lambda m: "-" + m.group(1).lower(), key)


def _key_from_attr(attr_name: str) -> str:
    """Convert a ``data-*`` attribute name to a camelCase dataset key.

    Algorithm (WHATWG §2.6.8):

    1. Strip the ``data-`` prefix.
    2. Replace each ``-X`` sequence (hyphen followed by an ASCII letter)
       with the uppercase form of the letter.

    Examples: ``"data-foo"`` → ``"foo"``, ``"data-foo-bar"`` → ``"fooBar"``,
    ``"data-xml-lang"`` → ``"xmlLang"``.
    """
    # Strip "data-" prefix — See  for WHATWG §2.6.8 algorithm.
    name = attr_name[len(_DATA_PREFIX):]
    # Replace "-x" (hyphen + lowercase letter) with uppercase letter
    return re.sub(r"-([a-z])", lambda m: m.group(1).upper(), name)


class DOMStringMap:
    """A live dict-like view of an element's ``data-*`` custom attributes.

    Reads from and writes to the owning element's attribute map directly on
    every operation. Changes to ``data-*`` attributes via ``set_attribute``
    are immediately visible through this object because it re-reads attributes
    on every call.

    Key mapping follows WHATWG HTML Living Standard §2.6.8:

    - Attribute ``data-foo-bar`` → key ``"fooBar"``
    - Key ``"fooBar"`` → attribute ``"data-foo-bar"``

    No attribute data is stored inside this object — all reads and writes pass
    through the element's ``NamedNodeMap`` ( live-view contract).

    Parameters
    ----------
    owner_element:
        The DOM element whose ``data-*`` attributes back this object.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> el.set_attribute("data-my-name", "Alice")
    >>> el.dataset["myName"]
    'Alice'
    >>> el.dataset["myName"] = "Bob"
    >>> el.get_attribute("data-my-name")
    'Bob'
    """

    __slots__ = ("_owner",)

    def __init__(self, owner_element: "Element") -> None:
        """Store the owning element. No attribute reads occur here.

        Parameters
        ----------
        owner_element:
            The element whose ``data-*`` attributes back this map.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> from aspose_html.dom._dataset import DOMStringMap
        >>> ds = DOMStringMap(el)
        >>> ds._owner is el
        True
        """
        self._owner = owner_element

    # ------------------------------------------------------------------
    # Dict protocol — public API
    # ------------------------------------------------------------------

    def __getitem__(self, key: str) -> str:
        """Return the value of the ``data-*`` attribute for *key*.

        Raises ``KeyError`` if the attribute is absent (unlike
        ``CSSStyleDeclaration.__getitem__``, which returns ``""``).

        Parameters
        ----------
        key:
            camelCase dataset key, e.g. ``"fooBar"`` for ``data-foo-bar``.

        Returns
        -------
        str
            The attribute value.

        Raises
        ------
        KeyError
            If no ``data-*`` attribute matching *key* exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-foo", "bar")
        >>> el.dataset["foo"]
        'bar'
        >>> el.dataset["absent"]  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        KeyError: 'absent'
        """
        attr = _attr_name(key)
        value = self._owner.get_attribute(attr)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: str) -> None:
        """Set the ``data-*`` attribute for *key* to *value*.

        Creates the attribute if it does not exist; updates it if it does.

        Parameters
        ----------
        key:
            camelCase dataset key, e.g. ``"myName"`` for ``data-my-name``.
        value:
            String value to set.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.dataset["myName"] = "Alice"
        >>> el.get_attribute("data-my-name")
        'Alice'
        """
        self._owner.set_attribute(_attr_name(key), value)

    def __delitem__(self, key: str) -> None:
        """Remove the ``data-*`` attribute for *key*.

        Raises ``KeyError`` if the attribute is absent (AC-5 from ).

        Parameters
        ----------
        key:
            camelCase dataset key.

        Raises
        ------
        KeyError
            If no ``data-*`` attribute matching *key* exists.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-foo", "1")
        >>> del el.dataset["foo"]
        >>> el.has_attribute("data-foo")
        False
        >>> del el.dataset["missing"]  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        KeyError: 'missing'
        """
        attr = _attr_name(key)
        if self._owner.get_attribute(attr) is None:
            raise KeyError(key)
        self._owner.remove_attribute(attr)

    def __contains__(self, key: object) -> bool:
        """Return ``True`` if *key* corresponds to an existing ``data-*`` attribute.

        Returns ``False`` for non-string keys without raising. Never raises.

        Parameters
        ----------
        key:
            Accepts ``object`` to satisfy the Python ``__contains__`` protocol.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-foo", "1")
        >>> "foo" in el.dataset
        True
        >>> "bar" in el.dataset
        False
        >>> 42 in el.dataset
        False
        """
        if not isinstance(key, str):
            return False
        return self._owner.has_attribute(_attr_name(key))

    def __iter__(self) -> Iterator[str]:
        """Iterate over all dataset keys in attribute insertion order.

        Yields camelCase keys for every ``data-*`` attribute on the element.
        Non-``data-*`` attributes (``id``, ``class``, ``style``, etc.) are
        skipped ( live-view contract).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-foo", "1")
        >>> el.set_attribute("data-bar", "2")
        >>> list(el.dataset)
        ['foo', 'bar']
        """
        for attr in self._owner.attributes:
            if attr.name.startswith(_DATA_PREFIX):  # type: ignore[union-attr]
                yield _key_from_attr(attr.name)  # type: ignore[union-attr]

    def __len__(self) -> int:
        """Return the number of ``data-*`` attributes on the element.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> len(el.dataset)
        0
        >>> el.set_attribute("data-a", "1")
        >>> el.set_attribute("data-b", "2")
        >>> len(el.dataset)
        2
        """
        return sum(
            1
            for attr in self._owner.attributes
            if attr.name.startswith(_DATA_PREFIX)  # type: ignore[union-attr]
        )

    def __repr__(self) -> str:
        return f"DOMStringMap({dict(self.items())!r})"

    # ------------------------------------------------------------------
    # Convenience dict-like methods
    # ------------------------------------------------------------------

    def get(self, key: str, default: str = "") -> str:
        """Return the value for *key*, or *default* if absent.

        Never raises. Returns *default* (``""`` by default) when the
        attribute is absent. Correctly handles empty-string attribute values:
        an attribute present with value ``""`` is returned as ``""``, not as
        *default*.

        Parameters
        ----------
        key:
            camelCase dataset key.
        default:
            Value to return when the attribute is absent.

        Returns
        -------
        str
            The attribute value or *default*.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-foo", "bar")
        >>> el.dataset.get("foo")
        'bar'
        >>> el.dataset.get("absent")
        ''
        >>> el.dataset.get("absent", "default")
        'default'
        """
        attr = _attr_name(key)
        value = self._owner.get_attribute(attr)
        return value if value is not None else default

    def keys(self) -> Iterator[str]:
        """Return an iterator over all dataset keys in insertion order.

        Equivalent to ``iter(self)``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-foo", "1")
        >>> el.set_attribute("data-bar-baz", "2")
        >>> list(el.dataset.keys())
        ['foo', 'barBaz']
        """
        return iter(self)

    def values(self) -> Iterator[str]:
        """Return an iterator over all dataset values in key insertion order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-x", "hello")
        >>> list(el.dataset.values())
        ['hello']
        """
        for key in self:
            yield self._owner.get_attribute(_attr_name(key))  # type: ignore[misc]

    def items(self) -> Iterator[tuple[str, str]]:
        """Return an iterator of ``(key, value)`` pairs in insertion order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("data-foo", "1")
        >>> list(el.dataset.items())
        [('foo', '1')]
        """
        for key in self:
            yield (key, self._owner.get_attribute(_attr_name(key)))  # type: ignore[misc]
