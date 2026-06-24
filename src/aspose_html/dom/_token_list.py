"""DOMTokenList — a live, mutable set of space-separated tokens backed by an element attribute.

Implements the WHATWG DOMTokenList interface (https://dom.spec.whatwg.org/#domtokenlist)
for the ``class`` attribute. Designed as a leaf module: no runtime imports from aspose_html.
Element is imported under TYPE_CHECKING only to avoid circular imports. See .
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterator

if TYPE_CHECKING:
    from aspose_html.dom._element import Element


def _validate_token(token: str) -> None:
    """Raise ValueError if *token* is empty or contains ASCII whitespace.

    Called before any mutation or read-validation in DOMTokenList. Per WHATWG
    DOMTokenList spec, both empty tokens and tokens with whitespace are invalid.
    """
    if not token:
        raise ValueError("token must not be empty")
    for ch in token:
        if ch in " \t\n\f\r":
            raise ValueError("token must not contain whitespace")


class DOMTokenList:
    """A live, mutable set of space-separated tokens backed by an element attribute.

    Implements the WHATWG DOMTokenList interface for the ``class`` attribute.
    Every operation reads from the backing attribute; mutations write back
    immediately via ``set_attribute`` / ``remove_attribute``.

    No token data is cached inside this object — ``_tokens()`` re-reads the
    attribute on every call. This preserves the live-view contract: external
    mutations via ``set_attribute("class", ...)`` are immediately visible.
    See  and .

    Parameters
    ----------
    owner_element:
        The element whose attribute backs this list.
    attr_name:
        The attribute name to read and write. Always ``"class"`` for
        ``element.class_list``; present for future extensibility (e.g. ``rel``).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> el.set_attribute("class", "foo bar")
    >>> el.class_list.contains("foo")
    True
    >>> el.class_list.add("baz")
    >>> el.get_attribute("class")
    'foo bar baz'
    >>> "active" in el.class_list
    False
    >>> el.class_list.add("active")
    >>> "active" in el.class_list
    True
    """

    __slots__ = ("_owner", "_attr")

    def __init__(self, owner_element: "Element", attr_name: str = "class") -> None:
        """Initialise the list by storing owner and attribute name only.

        Does not read or parse the attribute at construction time.

        Examples
        --------
        >>> from aspose_html.dom import Document, DOMTokenList
        >>> doc = Document()
        >>> el = doc.create_element("span")
        >>> isinstance(el.class_list, DOMTokenList)
        True
        """
        self._owner: "Element" = owner_element
        self._attr: str = attr_name

    # ------------------------------------------------------------------
    # Internal helper — type annotations required; no doctest required
    # ------------------------------------------------------------------

    def _tokens(self) -> list[str]:
        """Read the backing attribute and return its tokens as a list.

        Uses str.split() with no argument to split on any ASCII whitespace and
        discard empty strings — matching the WHATWG ordered set parser for
        space-separated tokens. See .
        """
        raw = self._owner.get_attribute(self._attr) or ""
        return raw.split()

    # ------------------------------------------------------------------
    # value property
    # ------------------------------------------------------------------

    @property
    def value(self) -> str:
        """The raw attribute value string, or ``''`` if the attribute is absent.

        Setting this property replaces the entire attribute value.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.class_list.value
        ''
        >>> el.class_list.value = "a b c"
        >>> el.class_list.value
        'a b c'
        """
        return self._owner.get_attribute(self._attr) or ""

    @value.setter
    def value(self, new_value: str) -> None:
        self._owner.set_attribute(self._attr, new_value)

    # ------------------------------------------------------------------
    # Public read operations
    # ------------------------------------------------------------------

    def contains(self, token: str) -> bool:
        """Return ``True`` if *token* is present in the token list.

        Validates *token* (raises ``ValueError`` for empty or whitespace-containing
        tokens) per WHATWG spec, then checks membership. : matches
        WHATWG DOMTokenList.contains().

        Parameters
        ----------
        token:
            The token to search for.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "foo bar")
        >>> el.class_list.contains("foo")
        True
        >>> el.class_list.contains("baz")
        False
        """
        _validate_token(token)
        return token in self._tokens()

    def values(self) -> Iterator[str]:
        """Return an iterator over the tokens in attribute order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "a b c")
        >>> list(el.class_list.values())
        ['a', 'b', 'c']
        """
        return iter(self._tokens())

    def item(self, index: int) -> str | None:
        """Return the token at *index*, or ``None`` if *index* is out of bounds.

        Implements WHATWG DOMTokenList.item(index). Returns ``None`` for any
        index outside ``[0, len(self))``, including negative indices. Does not
        raise ``IndexError`` — out-of-bounds access always returns ``None``.

        Note: ``__getitem__`` raises ``IndexError`` for out-of-range indices
        (Python convention). ``item()`` returns ``None`` instead (WHATWG
        convention). Both behaviours are correct in their respective contexts.

        Parameters
        ----------
        index:
            Zero-based position. Negative values always return ``None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "foo bar baz")
        >>> el.class_list.item(0)
        'foo'
        >>> el.class_list.item(2)
        'baz'
        >>> el.class_list.item(3) is None
        True
        >>> el.class_list.item(-1) is None
        True
        """
        # : read-only accessor; no validation; reads live attribute via _tokens()
        tokens = self._tokens()
        if 0 <= index < len(tokens):
            return tokens[index]
        return None

    # ------------------------------------------------------------------
    # Mutating operations
    # ------------------------------------------------------------------

    def add(self, *tokens: str) -> None:
        """Add one or more tokens. Already-present tokens are silently ignored.

        Validates each token before any mutation. When tokens are added, writes
        the updated value back via ``set_attribute``. If called with no arguments,
        the attribute is not touched. : mutation immediately visible through
        the attribute. See .

        Parameters
        ----------
        *tokens:
            Tokens to add. Each must be non-empty and contain no whitespace.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.class_list.add("foo")
        >>> el.class_list.add("foo")
        >>> el.get_attribute("class")
        'foo'
        >>> el.class_list.add("bar")
        >>> el.get_attribute("class")
        'foo bar'
        """
        for token in tokens:
            _validate_token(token)
        if not tokens:
            return
        current = self._tokens()
        seen: set[str] = set(current)
        for token in tokens:
            if token not in seen:
                current.append(token)
                seen.add(token)
        self._owner.set_attribute(self._attr, " ".join(current))

    def remove(self, *tokens: str) -> None:
        """Remove one or more tokens. Tokens not present are silently ignored.

        Validates each token before any mutation. When all tokens are removed,
        calls ``remove_attribute`` so the attribute is absent entirely (not set
        to ``""``). : mutation immediately visible. See .

        Parameters
        ----------
        *tokens:
            Tokens to remove. Each must be non-empty and contain no whitespace.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "a b c")
        >>> el.class_list.remove("b", "absent")
        >>> el.get_attribute("class")
        'a c'
        >>> el.class_list.remove("a", "c")
        >>> el.get_attribute("class") is None
        True
        """
        for token in tokens:
            _validate_token(token)
        if not tokens:
            return
        to_remove: set[str] = set(tokens)
        current = [t for t in self._tokens() if t not in to_remove]
        if current:
            self._owner.set_attribute(self._attr, " ".join(current))
        else:
            self._owner.remove_attribute(self._attr)

    def toggle(self, token: str, force: bool | None = None) -> bool:
        """Add or remove *token*, returning its new presence state.

        If *force* is ``None``: adds when absent (returns ``True``), removes
        when present (returns ``False``).
        If *force* is ``True``: always adds (returns ``True``).
        If *force* is ``False``: always removes (returns ``False``).

        Parameters
        ----------
        token:
            The token to toggle. Must be non-empty and contain no whitespace.
        force:
            Optional override — see above.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.class_list.toggle("active")
        True
        >>> el.class_list.toggle("active")
        False
        >>> el.class_list.toggle("active", force=True)
        True
        >>> el.class_list.toggle("active", force=False)
        False
        """
        _validate_token(token)
        present = token in self._tokens()
        if force is None:
            if present:
                self.remove(token)
                return False
            else:
                self.add(token)
                return True
        if force:
            self.add(token)
            return True
        # force is False
        self.remove(token)
        return False

    def replace(self, old_token: str, new_token: str) -> bool:
        """Replace *old_token* with *new_token* in-place.

        Returns ``True`` if *old_token* was present and replaced; ``False``
        if *old_token* was absent (attribute unchanged). If *new_token* is
        already present at a different position, that duplicate is removed —
        the position of *old_token* is kept. : mutation immediately
        visible. See .

        Parameters
        ----------
        old_token:
            Token to look for and replace.
        new_token:
            Token to substitute in.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "old extra")
        >>> el.class_list.replace("old", "new")
        True
        >>> el.get_attribute("class")
        'new extra'
        >>> el.class_list.replace("absent", "x")
        False
        """
        _validate_token(old_token)
        _validate_token(new_token)
        current = self._tokens()
        if old_token not in current:
            return False
        result: list[str] = []
        replaced = False
        for t in current:
            if t == old_token and not replaced:
                result.append(new_token)
                replaced = True
            elif t == new_token:
                # Skip duplicate of the replacement token —  deduplication rule
                pass
            else:
                result.append(t)
        self._owner.set_attribute(self._attr, " ".join(result))
        return True

    # ------------------------------------------------------------------
    # WHATWG DOM §7.1 IDL tail — length, entries, keys, for_each, supports
    # ------------------------------------------------------------------

    @property
    def length(self) -> int:
        """The number of tokens in the list (read-only).

        Equivalent to ``len(self)``. Provided for WHATWG IDL compatibility
        with the DOM ``DOMTokenList.length`` attribute. See  / .

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.class_list.length
        0
        >>> el.set_attribute("class", "a b c")
        >>> el.class_list.length
        3
        """
        return len(self._tokens())

    def entries(self) -> Iterator[tuple[int, str]]:
        """Return an iterator of ``(index, token)`` pairs, in attribute order.

        Mirrors the WHATWG ``DOMTokenList.entries()`` iterator. Each yielded
        tuple is ``(int, str)`` where the integer is the zero-based position
        of the token in the list.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "a b c")
        >>> list(el.class_list.entries())
        [(0, 'a'), (1, 'b'), (2, 'c')]
        """
        return enumerate(self._tokens())

    def keys(self) -> Iterator[int]:
        """Return an iterator of integer indices ``0, 1, …, len-1``.

        Mirrors the WHATWG ``DOMTokenList.keys()`` iterator. The iteration
        order matches the token order in the backing attribute value.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "x y z")
        >>> list(el.class_list.keys())
        [0, 1, 2]
        """
        return iter(range(len(self._tokens())))

    def for_each(
        self, callback: Callable[["str", int, "DOMTokenList"], None]
    ) -> None:
        """Call *callback* once for each token in attribute order.

        Mirrors the WHATWG ``DOMTokenList.forEach()`` method. The callback
        receives three arguments: ``(token, index, tokenlist)``.

        Parameters
        ----------
        callback:
            Callable with signature ``(token: str, index: int,
            list: DOMTokenList) -> None``.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "p q")
        >>> seen = []
        >>> el.class_list.for_each(lambda tok, idx, _: seen.append((idx, tok)))
        >>> seen
        [(0, 'p'), (1, 'q')]
        """
        for index, token in enumerate(self._tokens()):
            callback(token, index, self)

    def supports(self, token: str) -> bool:
        """Raise ``TypeError`` — no supported-tokens list exists for the class attribute.

        Per WHATWG DOM §7.1.8, ``DOMTokenList.supports(token)`` is only
        applicable to token lists that have an *associated supported-tokens
        list*. The ``class`` attribute has none, so this method always raises
        ``TypeError`` regardless of the value of *token*.

        The return-type annotation is ``bool`` to match the IDL signature;
        the body never returns normally.

        Parameters
        ----------
        token:
            The token whose support status is queried.

        Raises
        ------
        TypeError:
            Always — ``class`` has no associated supported-tokens list.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> try:
        ...     el.class_list.supports("foo")
        ... except TypeError as exc:
        ...     print("TypeError raised")
        TypeError raised
        """
        raise TypeError(
            "DOMTokenList.supports() is not applicable to the class attribute "
            "(no associated supported-tokens list)."
        )

    # ------------------------------------------------------------------
    # Python sequence protocol
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of tokens in the list.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> len(el.class_list)
        0
        >>> el.set_attribute("class", "a b")
        >>> len(el.class_list)
        2
        """
        return len(self._tokens())

    def __iter__(self) -> Iterator[str]:
        """Iterate over tokens in attribute order.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "x y")
        >>> list(el.class_list)
        ['x', 'y']
        """
        return iter(self._tokens())

    def __contains__(self, item: object) -> bool:
        """Return ``True`` if *item* is present in the token list.

        Does not validate *item* — containment testing follows Python convention
        and returns ``False`` for non-string items rather than raising. Use
        ``contains()`` when validation is required (per WHATWG spec).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "foo")
        >>> "foo" in el.class_list
        True
        >>> "bar" in el.class_list
        False
        """
        return item in self._tokens()

    def __getitem__(self, index: int) -> str:
        """Return the token at *index* (supports negative indices).

        Raises ``IndexError`` for out-of-range indices (standard list behaviour).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> el.set_attribute("class", "foo bar")
        >>> el.class_list[0]
        'foo'
        >>> el.class_list[-1]
        'bar'
        """
        return self._tokens()[index]

    def __repr__(self) -> str:
        return f"DOMTokenList({self._tokens()!r})"
