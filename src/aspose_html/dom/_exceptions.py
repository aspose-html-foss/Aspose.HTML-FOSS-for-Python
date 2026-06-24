"""DOM exception hierarchy — WHATWG DOM Standard."""
from __future__ import annotations


class DOMException(Exception):
    """Base for all DOM exceptions.

    Attributes
    ----------
    code:
        Numeric DOM exception code.
    message:
        Human-readable description.

    Examples
    --------
    >>> e = DOMException("test error")
    >>> isinstance(e, Exception)
    True
    """

    code: int = 0

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class IndexSizeError(DOMException):
    """Raised when an index or size is out of range.

    Examples
    --------
    >>> e = IndexSizeError("offset out of range")
    >>> e.code
    1
    """

    code: int = 1


class HierarchyRequestError(DOMException):
    """Raised when the tree hierarchy is violated.

    Examples
    --------
    >>> e = HierarchyRequestError("invalid insertion")
    >>> e.code
    3
    """

    code: int = 3


class WrongDocumentError(DOMException):
    """Raised when a node belongs to a different document.

    Examples
    --------
    >>> e = WrongDocumentError("wrong doc")
    >>> e.code
    4
    """

    code: int = 4


class InvalidCharacterError(DOMException):
    """Raised when an invalid character is used.

    Examples
    --------
    >>> e = InvalidCharacterError("bad char")
    >>> e.code
    5
    """

    code: int = 5


class NoModificationAllowedError(DOMException):
    """Raised when a node cannot be modified in its current context.

    Examples
    --------
    >>> e = NoModificationAllowedError("cannot modify")
    >>> e.code
    7
    """

    code: int = 7


class NotFoundError(DOMException):
    """Raised when a node is not found in the expected location.

    Examples
    --------
    >>> e = NotFoundError("node not found")
    >>> e.code
    8
    """

    code: int = 8


class NotSupportedError(DOMException):
    """Raised when an operation is not supported.

    Examples
    --------
    >>> e = NotSupportedError("not supported")
    >>> e.code
    9
    """

    code: int = 9


class InUseAttributeError(DOMException):
    """Raised when an Attr is already in use by another element.

    Corresponds to WHATWG DOM IN_USE_ATTRIBUTE_ERR (legacy code 10).

    Examples
    --------
    >>> e = InUseAttributeError("attr already in use")
    >>> e.code
    10
    """

    code: int = 10


class InvalidStateError(DOMException):
    """Raised when an operation is performed in an invalid state.

    Corresponds to WHATWG DOM InvalidStateError (no legacy numeric code).
    Used by Range methods when a boundary node has no parent.

    Examples
    --------
    >>> e = InvalidStateError("node has no parent")
    >>> isinstance(e, DOMException)
    True
    """

    code: int = 0


class SecurityError(DOMException):
    """Raised when an operation is blocked for security reasons."""

    code: int = 18


class SyntaxError(DOMException):
    """Raised when a string does not match the expected pattern or grammar.

    Corresponds to WHATWG DOM ``SyntaxError`` (legacy code 12).  Used by
    ``Element.insert_adjacent_html`` and ``Element.insert_adjacent_text``
    when the *position* argument is not one of the four recognised values.

    Examples
    --------
    >>> e = SyntaxError("Invalid position")
    >>> e.code
    12
    """

    code: int = 12
