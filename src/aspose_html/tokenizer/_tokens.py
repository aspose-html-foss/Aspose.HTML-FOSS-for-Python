"""Token dataclasses for the WHATWG HTML tokeniser.

All six token types defined in §13.2.5 are frozen dataclasses. They are
immutable after construction, carry source position (line/column), and
are the sole data exchanged between the tokeniser and the tree constructor.

See ADR-002 for the rationale behind frozen dataclasses and the
tuple-of-tuples attribute representation.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DoctypeToken:
    """A DOCTYPE token emitted by the WHATWG tokeniser.

    Attributes
    ----------
    name:
        The DOCTYPE name, lowercased. ``None`` if missing.
    public_id:
        The public identifier string. ``None`` if missing.
    system_id:
        The system identifier string. ``None`` if missing.
    force_quirks:
        If True, the tree constructor must set quirks mode.
    line:
        1-based source line number where this token starts.
    column:
        1-based source column number where this token starts.

    Examples
    --------
    >>> DoctypeToken(name='html', public_id=None, system_id=None,
    ...              force_quirks=False, line=1, column=1)
    DoctypeToken(name='html', public_id=None, system_id=None, force_quirks=False, line=1, column=1)
    """

    name: str | None
    public_id: str | None
    system_id: str | None
    force_quirks: bool
    line: int
    column: int


@dataclass(frozen=True)
class StartTagToken:
    """A start tag token, e.g. ``<div class="x">``.

    Attributes
    ----------
    tag_name:
        The lowercase tag name (e.g. ``'div'``).
    self_closing:
        True if the tag has a trailing ``/>``.
    attributes:
        Ordered sequence of ``(name, value)`` string pairs. Order
        is preserved exactly as encountered in the source. Duplicate
        attribute names are possible; the tree constructor handles
        deduplication per spec.
    line:
        1-based source line number.
    column:
        1-based source column number.

    Examples
    --------
    >>> StartTagToken(tag_name='div', self_closing=False,
    ...     attributes=(('class', 'foo'), ('id', 'bar')),
    ...     line=1, column=1)
    StartTagToken(tag_name='div', self_closing=False, attributes=(('class', 'foo'), ('id', 'bar')), line=1, column=1)
    """

    tag_name: str
    self_closing: bool
    # INV-002: attribute order preserved exactly; tuple-of-tuples is immutable
    attributes: tuple[tuple[str, str], ...]
    line: int
    column: int


@dataclass(frozen=True)
class EndTagToken:
    """An end tag token, e.g. ``</div>``.

    Attributes
    ----------
    tag_name:
        The lowercase tag name.
    line:
        1-based source line number.
    column:
        1-based source column number.

    Examples
    --------
    >>> EndTagToken(tag_name='div', line=1, column=6)
    EndTagToken(tag_name='div', line=1, column=6)
    """

    tag_name: str
    line: int
    column: int


@dataclass(frozen=True)
class CommentToken:
    """A comment token, e.g. ``<!-- text -->``.

    Attributes
    ----------
    data:
        The comment content, not including the ``<!--`` and ``-->``
        delimiters.
    line:
        1-based source line number.
    column:
        1-based source column number.

    Examples
    --------
    >>> CommentToken(data=' text ', line=1, column=1)
    CommentToken(data=' text ', line=1, column=1)
    """

    data: str
    line: int
    column: int


@dataclass(frozen=True)
class CharacterToken:
    """A character token carrying one or more Unicode characters.

    The WHATWG spec emits one character at a time in many states.
    The tokeniser buffers consecutive characters and emits them as
    a single CharacterToken for efficiency (see ADR-002, Decision 4).

    Attributes
    ----------
    data:
        One or more Unicode characters (buffered for efficiency).
    line:
        1-based source line number of the first character.
    column:
        1-based source column number of the first character.

    Examples
    --------
    >>> CharacterToken(data='Hello', line=1, column=1)
    CharacterToken(data='Hello', line=1, column=1)
    """

    data: str
    line: int
    column: int


@dataclass(frozen=True)
class EofToken:
    """An end-of-file token. Always the last token in a stream.

    Attributes
    ----------
    line:
        1-based source line number of the EOF position.
    column:
        1-based source column number of the EOF position.

    Examples
    --------
    >>> EofToken(line=1, column=14)
    EofToken(line=1, column=14)
    """

    line: int
    column: int


# INV-001: type alias name matches .NET AnyToken convention
AnyToken = (
    DoctypeToken
    | StartTagToken
    | EndTagToken
    | CommentToken
    | CharacterToken
    | EofToken
)
