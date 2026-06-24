"""CSS Selector Level 3 recursive-descent parser.

Parses a CSS selector string and produces a SelectorList AST.

Internal to aspose_html.css — not part of the public API.
The only public name here (frozen for select() in __init__.py) is parse().

Design: hand-written tokeniser + recursive-descent parser. See  §5.
No third-party dependencies. No regex for tokenisation (LL(1) approach).
"""
from __future__ import annotations

import dataclasses
import re as _re
from enum import Enum
from typing import Optional

from ._ast import (
    Combinator,
    AttributeOperator,
    UniversalSelector,
    TypeSelector,
    ClassSelector,
    IDSelector,
    AttributeSelector,
    NthArgument,
    PseudoClassSelector,
    SimpleSelector,
    CompoundSelector,
    ComplexSelector,
    SelectorList,
    HasPseudoClass,
    IsPseudoClass,
    WherePseudoClass,
    ComplexNotPseudoClass,
    NthFilteredChildPseudoClass,
)
from ._errors import syntax_error


# ── Internal token types ───────────────────────────────────────────────────────

class _TokenType(Enum):
    IDENT      = "IDENT"       # identifier: letters, digits, -, _ and non-ASCII
    HASH       = "HASH"        # #ident
    DOT        = "DOT"         # .
    STAR       = "STAR"        # *
    LBRACKET   = "LBRACKET"    # [
    RBRACKET   = "RBRACKET"    # ]
    LPAREN     = "LPAREN"      # (
    RPAREN     = "RPAREN"      # )
    COLON      = "COLON"       # :
    COMMA      = "COMMA"       # ,
    GT         = "GT"          # >
    PLUS       = "PLUS"        # +
    TILDE      = "TILDE"       # ~
    WHITESPACE = "WHITESPACE"  # one or more whitespace characters
    STRING     = "STRING"      # 'quoted' or "quoted"
    ATTR_OP    = "ATTR_OP"     # ~=, |=, ^=, $=, *=, =
    INVALID    = "INVALID"     # unexpected character; produces SyntaxError in parser
    EOF        = "EOF"


@dataclasses.dataclass
class _Token:
    type: _TokenType
    value: str
    position: int  # byte offset in original string, for error messages


# ── Tokeniser ─────────────────────────────────────────────────────────────────

_WHITESPACE_CHARS = frozenset(" \t\r\n\f")

# CSS identifier start characters (ASCII subset; non-ASCII handled separately)
_IDENT_START_ASCII = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
)
# Identifier continuation characters (ASCII subset)
_IDENT_CONT_ASCII = _IDENT_START_ASCII | frozenset("0123456789-")


def _is_ident_start(ch: str) -> bool:
    """True if ch can begin a CSS identifier."""
    if ch in _IDENT_START_ASCII:
        return True
    # Non-ASCII (code point >= 0x80) is valid per CSS spec
    return ord(ch) >= 0x80


def _is_ident_char(ch: str) -> bool:
    """True if ch can continue a CSS identifier."""
    if ch in _IDENT_CONT_ASCII:
        return True
    return ord(ch) >= 0x80


class _Tokeniser:
    """Tokenises a CSS selector string into a sequence of _Token objects."""

    def __init__(self, text: str) -> None:
        self._text = text
        self._pos = 0
        self._tokens: list[_Token] = []
        self._built = False

    def tokenise(self) -> list[_Token]:
        """Return the full token list including a trailing EOF token."""
        if self._built:
            return self._tokens
        self._built = True
        text = self._text
        length = len(text)
        pos = 0

        while pos < length:
            start = pos
            ch = text[pos]

            # Whitespace
            if ch in _WHITESPACE_CHARS:
                while pos < length and text[pos] in _WHITESPACE_CHARS:
                    pos += 1
                self._tokens.append(_Token(_TokenType.WHITESPACE, text[start:pos], start))
                continue

            # Single-character structural tokens
            if ch == ".":
                self._tokens.append(_Token(_TokenType.DOT, ".", pos))
                pos += 1
                continue
            if ch == "*":
                if pos + 1 < length and text[pos + 1] == "=":
                    self._tokens.append(_Token(_TokenType.ATTR_OP, "*=", pos))
                    pos += 2
                else:
                    self._tokens.append(_Token(_TokenType.STAR, "*", pos))
                    pos += 1
                continue
            if ch == "[":
                self._tokens.append(_Token(_TokenType.LBRACKET, "[", pos))
                pos += 1
                continue
            if ch == "]":
                self._tokens.append(_Token(_TokenType.RBRACKET, "]", pos))
                pos += 1
                continue
            if ch == "(":
                self._tokens.append(_Token(_TokenType.LPAREN, "(", pos))
                pos += 1
                continue
            if ch == ")":
                self._tokens.append(_Token(_TokenType.RPAREN, ")", pos))
                pos += 1
                continue
            if ch == ":":
                self._tokens.append(_Token(_TokenType.COLON, ":", pos))
                pos += 1
                continue
            if ch == ",":
                self._tokens.append(_Token(_TokenType.COMMA, ",", pos))
                pos += 1
                continue
            if ch == ">":
                self._tokens.append(_Token(_TokenType.GT, ">", pos))
                pos += 1
                continue
            if ch == "+":
                self._tokens.append(_Token(_TokenType.PLUS, "+", pos))
                pos += 1
                continue
            if ch == "~":
                # Could be ~= attribute operator or ~ general sibling combinator
                if pos + 1 < length and text[pos + 1] == "=":
                    self._tokens.append(_Token(_TokenType.ATTR_OP, "~=", pos))
                    pos += 2
                else:
                    self._tokens.append(_Token(_TokenType.TILDE, "~", pos))
                    pos += 1
                continue
            if ch == "|":
                if pos + 1 < length and text[pos + 1] == "=":
                    self._tokens.append(_Token(_TokenType.ATTR_OP, "|=", pos))
                    pos += 2
                else:
                    self._tokens.append(_Token(_TokenType.INVALID, ch, pos))
                    pos += 1
                continue
            if ch == "^":
                if pos + 1 < length and text[pos + 1] == "=":
                    self._tokens.append(_Token(_TokenType.ATTR_OP, "^=", pos))
                    pos += 2
                else:
                    self._tokens.append(_Token(_TokenType.INVALID, ch, pos))
                    pos += 1
                continue
            if ch == "$":
                if pos + 1 < length and text[pos + 1] == "=":
                    self._tokens.append(_Token(_TokenType.ATTR_OP, "$=", pos))
                    pos += 2
                else:
                    self._tokens.append(_Token(_TokenType.INVALID, ch, pos))
                    pos += 1
                continue
            if ch == "=":
                self._tokens.append(_Token(_TokenType.ATTR_OP, "=", pos))
                pos += 1
                continue

            # Hash (#ident)
            # Emit INVALID instead of raising when # is not followed by a valid
            # identifier — this allows forgiving mode in :is()/:where() to skip
            # the invalid selector rather than aborting the whole parse.
            if ch == "#":
                pos += 1
                if pos >= length or not (_is_ident_start(text[pos]) or text[pos] == "-" or text[pos].isdigit()):
                    self._tokens.append(_Token(_TokenType.INVALID, "#", start))
                    continue
                id_start = pos
                # ID values can include any ident chars or digits after #
                while pos < length and (_is_ident_char(text[pos]) or text[pos] == "-"):
                    pos += 1
                if pos == id_start:
                    self._tokens.append(_Token(_TokenType.INVALID, "#", start))
                    continue
                self._tokens.append(_Token(_TokenType.HASH, text[id_start:pos], start))
                continue

            # String literals (quoted)
            if ch in ('"', "'"):
                quote = ch
                pos += 1
                buf: list[str] = []
                while pos < length:
                    c = text[pos]
                    if c == quote:
                        pos += 1
                        break
                    if c == "\\":
                        pos += 1
                        if pos >= length:
                            raise syntax_error("unterminated escape in string", start)
                        buf.append(text[pos])
                        pos += 1
                    else:
                        buf.append(c)
                        pos += 1
                else:
                    raise syntax_error("unterminated string literal", start)
                self._tokens.append(_Token(_TokenType.STRING, "".join(buf), start))
                continue

            # Identifier (may start with - only if followed by ident-start or -)
            if _is_ident_start(ch) or (
                ch == "-" and pos + 1 < length and (
                    _is_ident_start(text[pos + 1]) or text[pos + 1] == "-"
                )
            ):
                while pos < length and (_is_ident_char(text[pos]) or text[pos] == "-"):
                    pos += 1
                self._tokens.append(_Token(_TokenType.IDENT, text[start:pos], start))
                continue

            # Digits (for An+B number tokens when they appear standalone)
            if ch.isdigit():
                while pos < length and text[pos].isdigit():
                    pos += 1
                self._tokens.append(_Token(_TokenType.IDENT, text[start:pos], start))
                continue

            # Emit INVALID token — parser raises SyntaxError when it sees it.
            # This allows forgiving mode to skip invalid individual selectors
            # even when unexpected characters appear in the input.
            self._tokens.append(_Token(_TokenType.INVALID, ch, pos))
            pos += 1

        self._tokens.append(_Token(_TokenType.EOF, "", length))
        return self._tokens


# ── Parser ────────────────────────────────────────────────────────────────────

# Pseudo-classes that are in-scope (no argument)
_PSEUDO_NO_ARG = frozenset({
    "root", "empty",
    "first-child", "last-child", "only-child",
    "first-of-type", "last-of-type", "only-of-type",
    "scope",
    "link", "visited", "any-link",
    # Valid stateful/user-action pseudo-classes in headless mode: parsed as
    # regular pseudo-classes and deterministically evaluate to no-match.
    "hover", "focus", "active", "focus-visible",
    #  / : parser accepts these and matcher applies
    # deterministic form-control semantics.
    "enabled", "disabled",
    #  / : parser accepts :checked and matcher applies
    # deterministic checked/selected-state semantics.
    "checked",
    #  / : parser accepts :target and matcher applies
    # deterministic fragment-target semantics.
    "target",
    #  / : form constraint-validation and UI-state pseudo-classes.
    "valid", "invalid",
    "required", "optional",
    "placeholder-shown",
    "default",
    "indeterminate",
    "read-only", "read-write",
    "blank",
    #  / : focus-within is valid syntax but deterministically
    # no-match in headless mode (no focus propagation model).
    "focus-within",
})

# Functional pseudo-classes that take An+B arguments
_PSEUDO_NTH = frozenset({
    "nth-child", "nth-last-child", "nth-of-type", "nth-last-of-type",
})

# Pseudo-elements (single-colon legacy forms) — raise NotImplementedError
_PSEUDO_ELEMENTS_SINGLE_COLON = frozenset({
    "before", "after", "first-line", "first-letter",
})

# Out-of-scope dynamic pseudo-classes — raise NotImplementedError.
# NOTE: "is", "where", and "has" have been REMOVED from this set — they are
# now implemented as Level 4 pseudo-classes in _parse_pseudo_class(). See .
# All previously out-of-scope dynamic pseudo-classes have been migrated to
# either _PSEUDO_NO_ARG (no-match headless semantics) or full implementation.
_PSEUDO_DYNAMIC_OOS: frozenset[str] = frozenset()

_PSEUDO_ELEMENT_NOT_IMPLEMENTED_PREFIX = "Pseudo-elements are not implemented:"


class _SelectorParser:
    """Hand-written recursive-descent parser for CSS Selectors Level 3.

    See  §5 for the grammar and method list.
    """

    def __init__(self, tokens: list[_Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # ── Token navigation ──────────────────────────────────────────────────────

    def _peek(self) -> _Token:
        """Look ahead one token without consuming it."""
        return self._tokens[self._pos]

    def _consume(self) -> _Token:
        """Advance past the current token and return it."""
        tok = self._tokens[self._pos]
        if tok.type != _TokenType.EOF:
            self._pos += 1
        return tok

    def _expect(self, token_type: _TokenType) -> _Token:
        """Consume the next token; raise SyntaxError if it does not match."""
        tok = self._peek()
        if tok.type != token_type:
            raise syntax_error(
                f"expected {token_type.value!r} but got {tok.value!r}",
                tok.position,
            )
        return self._consume()

    def _skip_whitespace(self) -> None:
        """Consume any WHITESPACE token at the current position."""
        if self._peek().type == _TokenType.WHITESPACE:
            self._consume()

    # ── Top-level entry points ─────────────────────────────────────────────────

    def _parse_selector_list(self, *, forgiving: bool = False) -> SelectorList:
        """selector_list = complex_selector (',' complex_selector)*

        Stops at EOF or RPAREN (the caller is responsible for consuming the
        closing parenthesis when this is called from inside a functional
        pseudo-class such as :not(), :is(), :where(), or :has()).
        """
        self._skip_whitespace()

        selectors: list[ComplexSelector] = []
        errors: list[Exception] = []

        # Terminator tokens: the list ends at EOF or the closing ')' of the
        # enclosing functional pseudo-class.
        _STOP_TYPES = (_TokenType.EOF, _TokenType.RPAREN)

        # Each iteration: skip optional whitespace, then parse one complex selector.
        # On first iteration there is no preceding comma to consume.
        first = True
        while True:
            if not first:
                # Expect a comma separator between selectors
                self._skip_whitespace()
                tok = self._peek()
                if tok.type in _STOP_TYPES:
                    break
                if tok.type != _TokenType.COMMA:
                    raise syntax_error(
                        f"unexpected token {tok.value!r} after selector",
                        tok.position,
                    )
                self._consume()  # consume comma
                self._skip_whitespace()
                # Even in forgiving contexts (:is/:where), duplicate commas
                # and trailing commas are invalid selector-list syntax.
                peek_after_comma = self._peek()
                if peek_after_comma.type in (_TokenType.COMMA, *_STOP_TYPES):
                    raise syntax_error(
                        "invalid selector list: empty entry in comma-separated list",
                        peek_after_comma.position,
                    )
            else:
                first = False

            if self._peek().type in _STOP_TYPES:
                # trailing comma — treat as syntax error
                raise syntax_error("selector string ends with a trailing comma")

            # Save position so we can rewind on forgiving parse failure
            saved_pos = self._pos
            try:
                selectors.append(self._parse_complex_selector())
            except SyntaxError as exc:
                if not forgiving:
                    raise
                errors.append(exc)
                # Rewind and skip to the next comma (or EOF) so the next
                # iteration can continue from there.
                self._pos = saved_pos
                self._skip_to_next_comma()

        if not selectors:
            # All entries failed — even forgiving mode raises SyntaxError
            first_err = errors[0] if errors else syntax_error("empty selector")
            raise first_err

        return SelectorList(selectors=tuple(selectors))

    def _skip_to_next_comma(self) -> None:
        """Skip tokens until the next comma (exclusive), RPAREN at depth 0, or EOF.

        Stops at RPAREN with depth==0 without consuming it so the enclosing
        functional pseudo-class (e.g. :is()) can consume the closing ')'.
        This is needed for forgiving parsing inside :is() and :where() — after
        a bad alternative is dropped, the cursor must leave the ')' intact for
        the caller.  See .
        """
        depth = 0
        while True:
            tok = self._peek()
            if tok.type == _TokenType.EOF:
                break
            if tok.type == _TokenType.RPAREN:
                if depth > 0:
                    depth -= 1
                    self._consume()
                else:
                    # Stop here — leave the closing ')' for the caller
                    break
            elif tok.type == _TokenType.LPAREN:
                depth += 1
                self._consume()
            elif tok.type == _TokenType.COMMA and depth == 0:
                # Leave the comma for the outer loop to handle (it was already
                # consumed before calling this method, so we need to step back)
                # Actually: outer loop already consumed the comma. We advance
                # past comma here so outer loop hits the next entry or EOF.
                # But: the outer loop's while True re-reads from current pos.
                # We want to leave cursor just AFTER the bad entry but BEFORE
                # the next comma. Since we consume commas in the outer loop,
                # we must NOT consume this comma here.
                break
            else:
                self._consume()

    def _parse_complex_selector(self) -> ComplexSelector:
        """complex_selector = compound_selector (combinator compound_selector)*"""
        first = self._parse_compound_selector()
        parts: list[tuple[Combinator | None, CompoundSelector]] = [
            (None, first)
        ]

        while True:
            combinator = self._parse_combinator()
            if combinator is None:
                break
            right = self._parse_compound_selector()
            parts.append((combinator, right))

        return ComplexSelector(parts=tuple(parts))

    def _parse_combinator(self) -> Optional[Combinator]:
        """Try to parse a combinator. Returns None if no combinator follows.

        Combinators: ' ' (descendant), '>' (child), '+' (adjacent), '~' (sibling).
        Whitespace is significant: a space between compounds is a DESCENDANT
        combinator, unless followed by >, +, or ~.
        """
        tok = self._peek()

        # Explicit combinators (may be surrounded by optional whitespace)
        if tok.type == _TokenType.GT:
            self._consume()
            self._skip_whitespace()
            # Verify there is something after the combinator
            if self._peek().type == _TokenType.EOF:
                raise syntax_error("selector ends with combinator '>'", tok.position)
            return Combinator.CHILD

        if tok.type == _TokenType.PLUS:
            self._consume()
            self._skip_whitespace()
            if self._peek().type == _TokenType.EOF:
                raise syntax_error("selector ends with combinator '+'", tok.position)
            return Combinator.ADJACENT

        if tok.type == _TokenType.TILDE:
            self._consume()
            self._skip_whitespace()
            if self._peek().type == _TokenType.EOF:
                raise syntax_error("selector ends with combinator '~'", tok.position)
            return Combinator.SIBLING

        # Whitespace — could be DESCENDANT combinator or just trailing whitespace
        if tok.type == _TokenType.WHITESPACE:
            ws_tok = self._consume()
            next_tok = self._peek()

            # If followed by explicit combinator, consume whitespace and let
            # the next iteration handle the explicit combinator
            if next_tok.type == _TokenType.GT:
                self._consume()
                self._skip_whitespace()
                if self._peek().type == _TokenType.EOF:
                    raise syntax_error("selector ends with combinator '>'", next_tok.position)
                return Combinator.CHILD
            if next_tok.type == _TokenType.PLUS:
                self._consume()
                self._skip_whitespace()
                if self._peek().type == _TokenType.EOF:
                    raise syntax_error("selector ends with combinator '+'", next_tok.position)
                return Combinator.ADJACENT
            if next_tok.type == _TokenType.TILDE:
                self._consume()
                self._skip_whitespace()
                if self._peek().type == _TokenType.EOF:
                    raise syntax_error("selector ends with combinator '~'", next_tok.position)
                return Combinator.SIBLING

            # Followed by EOF or COMMA — this was trailing whitespace, not a combinator
            if next_tok.type in (_TokenType.EOF, _TokenType.COMMA):
                return None

            # Otherwise it's a DESCENDANT combinator
            return Combinator.DESCENDANT

        return None

    def _parse_compound_selector(self) -> CompoundSelector:
        """compound_selector = simple_selector+

        At most one TypeSelector or UniversalSelector, which must be first.
        """
        simple_selectors: list[SimpleSelector] = []

        tok = self._peek()

        # Reject INVALID tokens immediately with a clear SyntaxError
        if tok.type == _TokenType.INVALID:
            raise syntax_error(
                f"unexpected character {tok.value!r}",
                tok.position,
            )

        # Optionally start with type selector or universal selector
        if tok.type == _TokenType.STAR:
            self._consume()
            simple_selectors.append(UniversalSelector())
        elif tok.type == _TokenType.IDENT:
            # Type selector — : lowercased at parse time for HTML mode
            self._consume()
            simple_selectors.append(TypeSelector(tag_name=tok.value.lower()))

        # Parse additional simple selectors (class, id, attribute, pseudo)
        # Note: double-colon (::) pseudo-elements are handled inside _parse_pseudo_class
        while True:
            tok = self._peek()
            if tok.type == _TokenType.INVALID:
                raise syntax_error(
                    f"unexpected character {tok.value!r}",
                    tok.position,
                )
            elif tok.type == _TokenType.DOT:
                simple_selectors.append(self._parse_class_selector())
            elif tok.type == _TokenType.HASH:
                simple_selectors.append(self._parse_id_selector())
            elif tok.type == _TokenType.LBRACKET:
                simple_selectors.append(self._parse_attribute_selector())
            elif tok.type == _TokenType.COLON:
                simple_selectors.append(self._parse_pseudo_class())
            else:
                break

        if not simple_selectors:
            tok = self._peek()
            raise syntax_error(
                f"expected a selector but got {tok.value!r}",
                tok.position,
            )

        return CompoundSelector(simple_selectors=tuple(simple_selectors))

    # ── Simple selector parsers ───────────────────────────────────────────────

    def _parse_class_selector(self) -> ClassSelector:
        """.classname"""
        self._expect(_TokenType.DOT)
        tok = self._peek()
        if tok.type != _TokenType.IDENT:
            raise syntax_error(
                f"expected class name after '.' but got {tok.value!r}",
                tok.position,
            )
        self._consume()
        return ClassSelector(class_name=tok.value)

    def _parse_id_selector(self) -> IDSelector:
        """#idname — the HASH token already strips the '#'."""
        tok = self._expect(_TokenType.HASH)
        return IDSelector(id_value=tok.value)

    def _parse_attribute_selector(self) -> AttributeSelector:
        """[attr], [attr=val], [attr~=val], [attr|=val], [attr^=val], [attr$=val], [attr*=val]
        Optional 'i' flag for case-insensitive value match.
        """
        self._expect(_TokenType.LBRACKET)
        self._skip_whitespace()

        # Attribute name
        name_tok = self._peek()
        if name_tok.type != _TokenType.IDENT:
            raise syntax_error(
                f"expected attribute name but got {name_tok.value!r}",
                name_tok.position,
            )
        self._consume()
        attr_name = name_tok.value.lower()  # attribute names case-insensitive in HTML mode

        self._skip_whitespace()
        tok = self._peek()

        # Check for operator
        if tok.type == _TokenType.RBRACKET:
            self._consume()
            return AttributeSelector(
                attr_name=attr_name,
                operator=AttributeOperator.EXISTS,
                value=None,
            )

        if tok.type != _TokenType.ATTR_OP:
            raise syntax_error(
                f"expected attribute operator or ']' but got {tok.value!r}",
                tok.position,
            )
        op_tok = self._consume()
        op_str = op_tok.value
        op_map = {
            "=":  AttributeOperator.EQUALS,
            "~=": AttributeOperator.WORD,
            "|=": AttributeOperator.DASHMATCH,
            "^=": AttributeOperator.PREFIX,
            "$=": AttributeOperator.SUFFIX,
            "*=": AttributeOperator.SUBSTRING,
        }
        if op_str not in op_map:
            raise syntax_error(f"unknown attribute operator {op_str!r}", op_tok.position)
        operator = op_map[op_str]

        self._skip_whitespace()
        val_tok = self._peek()
        if val_tok.type == _TokenType.STRING:
            self._consume()
            value = val_tok.value
        elif val_tok.type == _TokenType.IDENT:
            self._consume()
            value = val_tok.value
        else:
            raise syntax_error(
                f"expected attribute value but got {val_tok.value!r}",
                val_tok.position,
            )

        self._skip_whitespace()

        # Optional case-insensitive flag
        case_insensitive = False
        flag_tok = self._peek()
        if flag_tok.type == _TokenType.IDENT and flag_tok.value.lower() == "i":
            self._consume()
            case_insensitive = True
            self._skip_whitespace()

        self._expect(_TokenType.RBRACKET)
        return AttributeSelector(
            attr_name=attr_name,
            operator=operator,
            value=value,
            case_insensitive=case_insensitive,
        )

    def _parse_pseudo_class(
        self,
    ) -> "PseudoClassSelector | HasPseudoClass | IsPseudoClass | WherePseudoClass | ComplexNotPseudoClass":
        """Parse a pseudo-class or pseudo-element starting at ':'.

        Single colon: pseudo-class (or legacy pseudo-element form).
        Double colon: pseudo-element (always NotImplementedError).

        Handles Level 3 pseudo-classes plus the Level 4 additions
        :has(), :is(), :where(), and complex :not() ().
        """
        colon_tok = self._expect(_TokenType.COLON)

        # Double colon — pseudo-element
        if self._peek().type == _TokenType.COLON:
            self._consume()
            name_tok = self._peek()
            name = name_tok.value if name_tok.type == _TokenType.IDENT else "?"
            if name_tok.type == _TokenType.IDENT:
                self._consume()
            raise NotImplementedError(
                f"{_PSEUDO_ELEMENT_NOT_IMPLEMENTED_PREFIX} ::{name}"
            )

        name_tok = self._peek()
        if name_tok.type != _TokenType.IDENT:
            raise syntax_error(
                f"expected pseudo-class name after ':' but got {name_tok.value!r}",
                name_tok.position,
            )
        self._consume()
        name = name_tok.value.lower()

        # Single-colon legacy pseudo-element forms
        if name in _PSEUDO_ELEMENTS_SINGLE_COLON:
            raise NotImplementedError(
                f"{_PSEUDO_ELEMENT_NOT_IMPLEMENTED_PREFIX} :{name}"
            )

        # Out-of-scope dynamic pseudo-classes (Level 4 names removed — handled below)
        if name in _PSEUDO_DYNAMIC_OOS:
            raise NotImplementedError(
                f"Pseudo-class :{name} is not implemented (out of scope for Level 3)"
            )

        # Non-functional pseudo-classes (no argument)
        if name in _PSEUDO_NO_ARG:
            return PseudoClassSelector(name=name, argument=None)

        # Functional pseudo-classes require a LPAREN next
        if self._peek().type != _TokenType.LPAREN:
            raise syntax_error(
                f"pseudo-class :{name} is not supported (unrecognised pseudo-class)",
                name_tok.position,
            )
        self._expect(_TokenType.LPAREN)

        if name in _PSEUDO_NTH:
            argument = self._parse_nth_argument_from_tokens(pseudo_name=name)
            self._expect(_TokenType.RPAREN)
            if isinstance(argument, NthFilteredChildPseudoClass):
                # Return the NthFilteredChildPseudoClass directly — it IS the
                # node for this compound slot (not wrapped in PseudoClassSelector).
                return argument  # type: ignore[return-value]
            return PseudoClassSelector(name=name, argument=argument)

        # ── Level 4: :not(selector-list) — non-forgiving ─────────────────────
        # See . All :not() forms now produce ComplexNotPseudoClass.
        # The Level-3 PseudoClassSelector(name="not") path is kept in the
        # matcher for backward-compatibility with cached ASTs only.
        if name == "not":
            self._skip_whitespace()
            # : :not() uses non-forgiving parsing (Level 4 §4.5)
            sl = self._parse_selector_list(forgiving=False)
            self._skip_whitespace()
            self._expect(_TokenType.RPAREN)
            #  / : W3C Selectors Level 4 §4.5 forbids nested :not().
            # After parsing, walk the argument selector list and raise SyntaxError
            # if any CompoundSelector contains a ComplexNotPseudoClass or a legacy
            # PseudoClassSelector(name="not").  This guard runs only for :not();
            # :is() and :where() may freely contain :not() in their arguments.
            for complex_sel in sl.selectors:
                for _combinator, compound in complex_sel.parts:
                    for simple in compound.simple_selectors:
                        if isinstance(simple, ComplexNotPseudoClass) or (
                            isinstance(simple, PseudoClassSelector)
                            and simple.name == "not"
                        ):
                            raise SyntaxError(
                                "Nested :not() is invalid per CSS Selectors Level 4 §4.5"
                            )
            return ComplexNotPseudoClass(selector_list=sl)

        # ── Level 4: :is(selector-list) — forgiving ──────────────────────────
        # : forgiving parsing silently drops invalid selectors (Level 4 §4.4)
        if name == "is":
            self._skip_whitespace()
            sl = self._parse_selector_list(forgiving=True)
            self._skip_whitespace()
            self._expect(_TokenType.RPAREN)
            return IsPseudoClass(selector_list=sl)

        # ── Level 4: :where(selector-list) — forgiving ───────────────────────
        # : same forgiving parsing as :is(); zero specificity (Level 4 §4.7)
        if name == "where":
            self._skip_whitespace()
            sl = self._parse_selector_list(forgiving=True)
            self._skip_whitespace()
            self._expect(_TokenType.RPAREN)
            return WherePseudoClass(selector_list=sl)

        # ── Level 4: :has(relative-selector-list) ────────────────────────────
        # : non-forgiving; relative selectors may begin with a combinator
        if name == "has":
            self._skip_whitespace()
            relative_selectors = self._parse_relative_selector_list()
            self._skip_whitespace()
            self._expect(_TokenType.RPAREN)
            return HasPseudoClass(relative_selectors=tuple(relative_selectors))

        if name == "lang":
            self._skip_whitespace()
            lang_tok = self._peek()
            if lang_tok.type not in (_TokenType.IDENT, _TokenType.STRING):
                raise syntax_error(
                    f"expected language range in :lang() but got {lang_tok.value!r}",
                    lang_tok.position,
                )
            self._consume()
            lang_value = lang_tok.value
            self._skip_whitespace()
            self._expect(_TokenType.RPAREN)
            return PseudoClassSelector(name="lang", argument=lang_value)

        # Unknown functional pseudo-class — not supported
        raise syntax_error(
            f"unsupported pseudo-class :{name}()",
            name_tok.position,
        )

    def _parse_relative_selector_list(
        self,
    ) -> list[tuple["Combinator | None", SelectorList]]:
        """Parse a relative selector list for :has().

        A relative selector list is a comma-separated sequence of relative
        selectors. Each relative selector may optionally begin with a leading
        combinator (``>``, ``~``, or ``+``). The absence of an explicit leading
        combinator implies a descendant relationship.

        Returns a list of ``(leading_combinator, inner_selector_list)`` pairs.
        Raises ``SyntaxError`` if the list is empty or any entry is invalid
        (non-forgiving per Level 4 §4.6 and §3.3). See .
        """
        result: list[tuple[Combinator | None, SelectorList]] = []
        first = True

        while True:
            self._skip_whitespace()

            # Handle comma separator (skip on first iteration)
            if not first:
                tok = self._peek()
                if tok.type == _TokenType.EOF or tok.type == _TokenType.RPAREN:
                    break
                if tok.type != _TokenType.COMMA:
                    break
                self._consume()  # consume comma
                self._skip_whitespace()
            else:
                first = False

            # Check for end of list before trying to parse an entry
            if self._peek().type in (_TokenType.EOF, _TokenType.RPAREN):
                break

            # Optional leading combinator
            leading_combinator: Combinator | None = None
            peek = self._peek()
            if peek.type == _TokenType.GT:
                self._consume()
                leading_combinator = Combinator.CHILD
                self._skip_whitespace()
            elif peek.type == _TokenType.PLUS:
                self._consume()
                leading_combinator = Combinator.ADJACENT
                self._skip_whitespace()
            elif peek.type == _TokenType.TILDE:
                self._consume()
                leading_combinator = Combinator.SIBLING
                self._skip_whitespace()

            # Parse one complex selector and wrap in a SelectorList
            complex_sel = self._parse_complex_selector()
            inner_sl = SelectorList(selectors=(complex_sel,))
            result.append((leading_combinator, inner_sl))

        if not result:
            raise syntax_error("empty :has() argument list")

        return result

    def _parse_not_argument(self) -> SimpleSelector:
        """Legacy Level-3 :not() argument parser — no longer used by the parser.

        Kept as dead code so existing external callers are not broken.
        The parser now produces ComplexNotPseudoClass for all :not() forms.
        See .
        """
        # Legacy Level-3 only — no longer used by parser ()
        tok = self._peek()

        if tok.type == _TokenType.STAR:
            self._consume()
            return UniversalSelector()

        if tok.type == _TokenType.IDENT:
            self._consume()
            self._skip_whitespace()
            if self._peek().type == _TokenType.COMMA:
                raise syntax_error(
                    ":not() with a selector list is not supported (Level 4, out of scope)",
                    tok.position,
                )
            return TypeSelector(tag_name=tok.value.lower())

        if tok.type == _TokenType.DOT:
            return self._parse_class_selector()

        if tok.type == _TokenType.HASH:
            return self._parse_id_selector()

        if tok.type == _TokenType.LBRACKET:
            return self._parse_attribute_selector()

        if tok.type == _TokenType.COLON:
            return self._parse_pseudo_class()  # type: ignore[return-value]

        raise syntax_error(
            f"expected a simple selector inside :not() but got {tok.value!r}",
            tok.position,
        )

    def _parse_nth_argument_from_tokens(
        self, *, pseudo_name: str = "nth-child"
    ) -> "NthArgument | NthFilteredChildPseudoClass":
        """Parse An+B [of <selector-list>] from tokens.

        Called after LPAREN has been consumed by the caller.

        Parameters
        ----------
        pseudo_name : str
            The pseudo-class name being parsed (``"nth-child"`` or
            ``"nth-last-child"`` for filtered-child semantics;
            ``"nth-of-type"`` or ``"nth-last-of-type"`` for the plain path).
            Used to set the ``reverse`` flag on ``NthFilteredChildPseudoClass``.

        Returns
        -------
        NthArgument
            When no ``of`` keyword is present (plain An+B), or when
            ``pseudo_name`` is ``nth-of-type`` / ``nth-last-of-type``.
        NthFilteredChildPseudoClass
            When ``of <selector-list>`` is present and ``pseudo_name`` is
            ``nth-child`` or ``nth-last-child``.

        Raises
        ------
        SyntaxError
            For empty argument, missing An+B before ``of``, or invalid
            selector list after ``of``.
        """
        # Collect tokens up to the matching RPAREN, reconstructing the original
        # text faithfully.  HASH tokens store only the identifier value (without
        # the '#' prefix) because the tokeniser strips it; we must re-add '#'.
        parts: list[str] = []
        while self._peek().type not in (_TokenType.RPAREN, _TokenType.EOF):
            tok = self._consume()
            if tok.type == _TokenType.HASH:
                parts.append("#" + tok.value)
            else:
                parts.append(tok.value)
        raw = "".join(parts).strip()
        if not raw:
            raise syntax_error("empty :nth-child() argument")

        # Detect "of <selector-list>" suffix only for nth-child / nth-last-child.
        # nth-of-type and nth-last-of-type do NOT support the "of S" extension
        # per CSS Selectors Level 4 — they are type-scoped by definition.
        if pseudo_name in ("nth-child", "nth-last-child"):
            halves = _re.split(r"\s+of\s+", raw, maxsplit=1, flags=_re.IGNORECASE)
            if len(halves) == 2:
                anb_raw, selector_raw = halves
                if not anb_raw.strip():
                    raise SyntaxError(
                        "missing An+B before 'of' in :nth-child()"
                    )
                if not selector_raw.strip():
                    raise SyntaxError(
                        "missing selector after 'of' in :nth-child()"
                    )
                nth_arg = _parse_nth_argument(anb_raw)
                selector_list = _parse_selector_list_from_str(
                    selector_raw, forgiving=False
                )
                return NthFilteredChildPseudoClass(
                    nth=nth_arg,
                    filter=selector_list,
                    reverse=(pseudo_name == "nth-last-child"),
                )

        # Plain An+B path (no "of" keyword, or nth-of-type / nth-last-of-type)
        return _parse_nth_argument(raw)

def _parse_selector_list_from_str(text: str, *, forgiving: bool = False) -> SelectorList:
    """Parse a selector list from a plain string.

    Creates a fresh ``_SelectorParser`` from ``text`` and calls
    ``_parse_selector_list()``. Re-raises ``SyntaxError`` from the inner
    parser as-is.

    Used to parse the ``of <selector-list>`` suffix inside
    ``:nth-child(An+B of S)`` without complicating the outer token stream.

    Parameters
    ----------
    text : str
        The raw selector text (everything after ``of ``).
    forgiving : bool, optional
        Whether to use forgiving parsing (default False — per CSS §8.3 the
        ``of S`` clause uses non-forgiving semantics).

    Returns
    -------
    SelectorList
        The parsed selector list.
    """
    tokens = _Tokeniser(text).tokenise()
    inner_parser = _SelectorParser(tokens)
    return inner_parser._parse_selector_list(forgiving=forgiving)


def _parse_nth_argument(raw: str) -> NthArgument:
    """Parse An+B micro-syntax from a raw string.

    Handles: even, odd, integer, An, An+B, An-B, -n+B, n forms.
    See  §10 and CSS Syntax §8.3 An+B microsyntax.

    Raises SyntaxError for invalid strings.
    """
    s = raw.strip().lower()

    if s == "even":
        return NthArgument(a=2, b=0)
    if s == "odd":
        return NthArgument(a=2, b=1)

    # Normalise spaces around + and - (CSS allows whitespace in An+B)
    # e.g. "2n + 1" -> "2n+1", "2n - 1" -> "2n-1"
    import re as _re
    s = _re.sub(r"\s*\+\s*", "+", s)
    s = _re.sub(r"\s*-\s*", "-", s)

    # Pure integer: e.g. "3", "-3"
    if _re.fullmatch(r"-?\d+", s):
        return NthArgument(a=0, b=int(s))

    # Forms with 'n':
    # n, -n, An, An+B, An-B, -n+B, -n-B
    m = _re.fullmatch(
        r"(?P<a>-?\d*|-?)n(?P<sign>[+-]?)(?P<b>\d*)",
        s,
    )
    if not m:
        raise SyntaxError(f"Invalid An+B expression: {raw!r}")

    a_str = m.group("a")
    sign = m.group("sign")
    b_str = m.group("b")

    # Parse coefficient of n
    if a_str == "" or a_str == "+":
        a = 1
    elif a_str == "-":
        a = -1
    else:
        a = int(a_str)

    # Parse B offset
    if b_str == "":
        b = 0
    else:
        b = int(b_str)
        if sign == "-":
            b = -b

    return NthArgument(a=a, b=b)


# ── Public parse function ──────────────────────────────────────────────────────

def parse(selector_str: str, *, forgiving: bool = False) -> SelectorList:
    """Parse selector_str into a SelectorList AST.

    Parameters
    ----------
    selector_str : str
        A CSS selector string (Level 3 subset).
    forgiving : bool, optional
        When True, individual invalid comma-separated selectors are silently
        skipped rather than failing the whole parse. If all entries fail,
        SyntaxError is still raised. Default False.

    Returns
    -------
    SelectorList
        The parsed selector AST.

    Raises
    ------
    SyntaxError
        If the selector string is completely invalid (no valid selector can
        be recovered) or if forgiving=False and any selector is invalid.
    NotImplementedError
        If the selector string uses syntactically valid but unimplemented
        constructs (pseudo-elements and out-of-scope dynamic pseudo-classes,
        such as :checked).

    Notes
    -----
    This function is internal. Users call aspose_html.css.select() which
    calls parse() internally.
    """
    if not selector_str or not selector_str.strip():
        raise SyntaxError("Invalid CSS selector: selector string is empty")

    tokens = _Tokeniser(selector_str).tokenise()
    parser = _SelectorParser(tokens)
    return parser._parse_selector_list(forgiving=forgiving)
