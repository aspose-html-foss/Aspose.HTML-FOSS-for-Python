"""Tests for token dataclasses — ADR-002 AC-1 through AC-4.

Tests that all 6 token types can be constructed, that field values are
accessible, and that frozen instances reject mutation.
"""
from __future__ import annotations

import pytest
from dataclasses import FrozenInstanceError

from aspose_html.tokenizer import (
    DoctypeToken,
    StartTagToken,
    EndTagToken,
    CommentToken,
    CharacterToken,
    EofToken,
)


def test_doctype_token_fields() -> None:
    tok = DoctypeToken(
        name="html",
        public_id=None,
        system_id=None,
        force_quirks=False,
        line=1,
        column=1,
    )
    assert tok.name == "html"
    assert tok.public_id is None
    assert tok.system_id is None
    assert tok.force_quirks is False
    assert tok.line == 1
    assert tok.column == 1


def test_start_tag_token_fields() -> None:
    tok = StartTagToken(
        tag_name="div",
        self_closing=False,
        attributes=(("class", "foo"), ("id", "bar")),
        line=1,
        column=1,
    )
    assert tok.tag_name == "div"
    assert tok.self_closing is False
    assert tok.attributes == (("class", "foo"), ("id", "bar"))
    assert tok.line == 1
    assert tok.column == 1


def test_end_tag_token_fields() -> None:
    tok = EndTagToken(tag_name="span", line=2, column=5)
    assert tok.tag_name == "span"
    assert tok.line == 2
    assert tok.column == 5


def test_comment_token_fields() -> None:
    tok = CommentToken(data=" hello world ", line=3, column=1)
    assert tok.data == " hello world "
    assert tok.line == 3
    assert tok.column == 1


def test_character_token_fields() -> None:
    tok = CharacterToken(data="Hello", line=1, column=1)
    assert tok.data == "Hello"
    assert tok.line == 1
    assert tok.column == 1


def test_eof_token_fields() -> None:
    tok = EofToken(line=10, column=3)
    assert tok.line == 10
    assert tok.column == 3


def test_tokens_are_frozen() -> None:
    """INV-002: tokens must be immutable after construction."""
    doctype = DoctypeToken(
        name="html", public_id=None, system_id=None,
        force_quirks=False, line=1, column=1,
    )
    start = StartTagToken(
        tag_name="p", self_closing=False,
        attributes=(), line=1, column=1,
    )
    end = EndTagToken(tag_name="p", line=1, column=4)
    comment = CommentToken(data="x", line=1, column=1)
    char = CharacterToken(data="a", line=1, column=1)
    eof = EofToken(line=1, column=2)

    for tok in (doctype, start, end, comment, char, eof):
        with pytest.raises(FrozenInstanceError):
            tok.__setattr__(  # type: ignore[call-arg]
                list(tok.__dataclass_fields__)[0], "mutated"
            )
