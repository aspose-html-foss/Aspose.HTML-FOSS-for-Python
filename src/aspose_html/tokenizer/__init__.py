"""WHATWG HTML Tokeniser public API.

This package implements the HTML tokenisation algorithm defined in
§13.2.5 of the WHATWG HTML Living Standard.  It is the second stage
of the parsing pipeline, consuming decoded Unicode text from the encoding
detection module and producing a stream of typed tokens for the tree
constructor (BACK-3).

Public surface
--------------
- :class:`Tokenizer` — the state machine
- :class:`TokenizerState` — all ~80 WHATWG states
- :class:`DoctypeToken`
- :class:`StartTagToken`
- :class:`EndTagToken`
- :class:`CommentToken`
- :class:`CharacterToken`
- :class:`EofToken`
- :data:`AnyToken` — union type alias for use in type hints

See Also
--------
ADR-002-html-tokeniser.md : architectural decisions for this module
"""
from aspose_html.tokenizer._tokens import (
    DoctypeToken,
    StartTagToken,
    EndTagToken,
    CommentToken,
    CharacterToken,
    EofToken,
    AnyToken,
)
from aspose_html.tokenizer._states import TokenizerState
from aspose_html.tokenizer._tokenizer import Tokenizer

__all__ = [
    "DoctypeToken",
    "StartTagToken",
    "EndTagToken",
    "CommentToken",
    "CharacterToken",
    "EofToken",
    "AnyToken",
    "TokenizerState",
    "Tokenizer",
]
