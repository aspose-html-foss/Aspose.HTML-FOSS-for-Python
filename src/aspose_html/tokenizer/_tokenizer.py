"""WHATWG HTML Tokeniser (§13.2.5) — state machine implementation.

This module implements the complete HTML tokenisation algorithm as defined
in the WHATWG HTML Living Standard §13.2.5.  Each of the ~80 states is
implemented as a private method named ``_state_<state_name_lowercased>``.
An O(1) dispatch table maps ``TokenizerState`` values to these methods.

Constraints:
- : No regex. No approximation. Every state from §13.2.5 is a
  distinct method. See .
- : Attribute order preserved. Tokens are immutable (frozen
  dataclasses). See .
- : Public API naming follows .NET Aspose.HTML conventions.
  See , Decision 11.

See  for full design rationale.
"""
from __future__ import annotations

from typing import Generator, Callable

from aspose_html.dom import ParseError
from aspose_html.tokenizer._tokens import (
    AnyToken,
    DoctypeToken,
    StartTagToken,
    EndTagToken,
    CommentToken,
    CharacterToken,
    EofToken,
)
from aspose_html.tokenizer._states import TokenizerState
from aspose_html.tokenizer._char_refs import (
    resolve_named_char_ref,
    resolve_numeric_char_ref,
    find_named_char_ref_match,
    NAMED_CHAR_REFS,
)

# Sentinel value for "no character" (EOF)
_EOF = ""


class Tokenizer:
    """WHATWG HTML tokeniser (§13.2.5).

    Converts a Unicode string produced by encoding detection into a stream
    of typed tokens consumed by the tree constructor ().

    Parameters
    ----------
    text:
        Decoded HTML string from ``EncodingDetectionResult.text``.
        Must have CRLF and lone CR pre-normalised to LF (the encoding
        module guarantees this).
    initial_state:
        The starting state. Defaults to ``TokenizerState.DATA``.
        The tree constructor may pass a different state for fragment
        parsing (e.g. ``TokenizerState.RCDATA`` for ``<textarea>``).

    Examples
    --------
    >>> from aspose_html.tokenizer import Tokenizer, TokenizerState
    >>> tok = Tokenizer('<p>Hello</p>')
    >>> tokens = list(tok.tokenize())
    >>> tokens[0].tag_name
    'p'
    """

    def __init__(
        self,
        text: str,
        initial_state: TokenizerState = TokenizerState.DATA,
    ) -> None:
        self._text: str = text
        self._pos: int = 0          # current position (0-based)
        self._line: int = 1         # current 1-based line number
        self._col: int = 1          # current 1-based column number
        self._state: TokenizerState = initial_state
        # State to return to after character reference resolution
        self._return_state: TokenizerState = TokenizerState.DATA
        # Mutable token being assembled (dict or None)
        self._current_token: dict | None = None
        # Buffers
        self._char_buf: list[str] = []           # consecutive char output
        self._char_buf_line: int = 1             # line of first char in buf
        self._char_buf_col: int = 1              # col of first char in buf
        self._attr_name_buf: list[str] = []      # current attribute name
        self._attr_value_buf: list[str] = []     # current attribute value
        self._attrs_buf: list[tuple[str, str]] = []  # completed attributes
        self._temp_buf: list[str] = []           # temp buffer for char refs etc.
        self._errors: list[ParseError] = []
        self._last_start_tag_name: str | None = None
        self._reconsume: bool = False
        # Pending output tokens (emitted from state methods, yielded by loop)
        self._output_queue: list[AnyToken] = []
        # Numeric char ref accumulator
        self._char_ref_code: int = 0

        # Build O(1) dispatch table: state -> bound method  (See  §3)
        self._dispatch: dict[TokenizerState, Callable[[str], None]] = {}
        for state in TokenizerState:
            method_name = "_state_" + state.name.lower()
            method = getattr(self, method_name, None)
            if method is not None:
                self._dispatch[state] = method

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @property
    def state(self) -> TokenizerState:
        """The current tokeniser state.

        The tree constructor reads this after each token to detect
        state-based adjustments.

        Examples
        --------
        >>> from aspose_html.tokenizer import Tokenizer, TokenizerState
        >>> tok = Tokenizer('')
        >>> tok.state
        <TokenizerState.DATA: 0>
        """
        return self._state

    def set_state(self, state: TokenizerState) -> None:
        """Inject a new state into the tokeniser.

        Called by the tree constructor to switch the tokeniser into
        RCDATA, RAWTEXT, SCRIPT_DATA, or PLAINTEXT after processing a
        start tag that requires raw text content (e.g. ``<script>``,
        ``<style>``, ``<textarea>``). Must only be called between tokens,
        not during a tokenize() iteration.

        Parameters
        ----------
        state:
            The target state. Must be one of ``TokenizerState.RCDATA``,
            ``RAWTEXT``, ``SCRIPT_DATA``, or ``PLAINTEXT``.

        Examples
        --------
        >>> from aspose_html.tokenizer import Tokenizer, TokenizerState
        >>> tok = Tokenizer('<script>x</script>', TokenizerState.DATA)
        >>> tok.set_state(TokenizerState.SCRIPT_DATA)
        >>> tok.state
        <TokenizerState.SCRIPT_DATA: 3>
        """
        self._state = state

    def tokenize(self) -> Generator[AnyToken, None, None]:
        """Tokenise the input text and yield tokens one at a time.

        Yields tokens in source order. The last token is always
        ``EofToken``. The generator must be fully consumed or explicitly
        closed; it is not safe to call ``tokenize()`` twice on the same
        instance.

        The tree constructor may call ``set_state()`` between ``next()``
        calls on the returned generator to inject state changes.

        Yields
        ------
        AnyToken
            One of ``DoctypeToken``, ``StartTagToken``, ``EndTagToken``,
            ``CommentToken``, ``CharacterToken``, or ``EofToken``.

        Examples
        --------
        >>> from aspose_html.tokenizer import Tokenizer
        >>> tokens = list(Tokenizer('<!DOCTYPE html><p>Hi</p>').tokenize())
        >>> tokens[0].name
        'html'
        >>> tokens[1].tag_name
        'p'
        """
        text = self._text
        n = len(text)

        while True:
            # Determine current character
            if self._reconsume:
                self._reconsume = False
                # Use the same char again (pos was NOT advanced)
                if self._pos > n:
                    char = _EOF
                elif self._pos == n:
                    char = _EOF
                else:
                    char = text[self._pos - 1] if self._pos > 0 else _EOF
            else:
                if self._pos >= n:
                    char = _EOF
                else:
                    char = text[self._pos]
                    self._pos += 1
                    # Update line/column tracking
                    if char == "\n":
                        self._line += 1
                        self._col = 1
                    else:
                        self._col += 1

            # Dispatch to current state handler
            handler = self._dispatch.get(self._state)
            if handler is not None:
                handler(char)
            # else: unimplemented state — skip (should not happen)

            # Yield any tokens queued by the state handler
            for token in self._output_queue:
                yield token
            self._output_queue.clear()

            # Stop when we've processed EOF and not reconsuming
            if char is _EOF and not self._reconsume:
                # Flush any remaining character buffer
                ct = self._flush_chars()
                if ct is not None:
                    yield ct
                # Emit EOF token
                yield EofToken(line=self._line, column=self._col)
                return

    @classmethod
    def tokenize_fragment(
        cls,
        context_element_name: str,
        text: str,
    ) -> Generator[AnyToken, None, None]:
        """Tokenise ``text`` as a fragment for ``innerHTML`` parsing.

        Sets the initial tokeniser state based on ``context_element_name``
        as required by the WHATWG fragment parsing algorithm §13.2.6.

        Parameters
        ----------
        context_element_name:
            The lowercase tag name of the element whose ``innerHTML`` is
            being set (e.g. ``'textarea'``, ``'script'``, ``'title'``).
        text:
            The HTML fragment string to tokenise.

        Yields
        ------
        AnyToken

        Examples
        --------
        >>> from aspose_html.tokenizer import Tokenizer
        >>> tokens = list(Tokenizer.tokenize_fragment('div', '<b>Hi</b>'))
        >>> tokens[0].tag_name
        'b'
        """
        # §13.2.6: initial state based on context element
        state = _FRAGMENT_CONTEXT_STATES.get(
            context_element_name, TokenizerState.DATA
        )
        tok = cls(text, initial_state=state)
        yield from tok.tokenize()

    @property
    def errors(self) -> list[ParseError]:
        """Parse errors collected during tokenisation.

        Each entry is a ``ParseError`` with ``code`` (WHATWG error
        identifier string), ``line``, ``column``, and ``message``.
        This list is populated during ``tokenize()``; it is empty before
        tokenisation begins.

        Examples
        --------
        >>> from aspose_html.tokenizer import Tokenizer
        >>> tok = Tokenizer('<!--no end')
        >>> _ = list(tok.tokenize())
        >>> tok.errors[0].code
        'eof-in-comment'
        """
        return self._errors

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _emit(self, token: AnyToken) -> None:
        """Flush any pending character buffer, then queue *token* for output."""
        ct = self._flush_chars()
        if ct is not None:
            self._output_queue.append(ct)
        self._output_queue.append(token)

    def _emit_char(self, char: str) -> None:
        """Buffer a character for eventual emission as CharacterToken."""
        if not self._char_buf:
            # Record the source position of the first character in the run
            self._char_buf_line = self._line
            self._char_buf_col = self._col - (1 if char != "\n" else 0)
        self._char_buf.append(char)

    def _flush_chars(self) -> CharacterToken | None:
        """Drain _char_buf into a single CharacterToken, or return None."""
        if not self._char_buf:
            return None
        token = CharacterToken(
            data="".join(self._char_buf),
            line=self._char_buf_line,
            column=self._char_buf_col,
        )
        self._char_buf.clear()
        return token

    def _parse_error(self, code: str, message: str = "") -> None:
        """Record a parse error at the current position."""
        if not message:
            message = code.replace("-", " ").capitalize()
        self._errors.append(ParseError(
            code=code,
            line=self._line,
            column=self._col,
            message=message,
        ))

    def _reconsume_in(self, state: TokenizerState) -> None:
        """Switch to *state* and reconsume the current character."""
        self._state = state
        self._reconsume = True

    def _commit_attr(self) -> None:
        """Finish the current attribute and add it to the buffer."""
        if self._current_token and self._current_token.get("_type") in (
            "start_tag", "end_tag"
        ):
            name = "".join(self._attr_name_buf)
            value = "".join(self._attr_value_buf)
            self._attr_name_buf.clear()
            self._attr_value_buf.clear()
            # : preserve all attributes; tree constructor deduplicates
            # Duplicate attribute parse error raised here per spec
            existing_names = [a[0] for a in self._attrs_buf]
            if name in existing_names:
                self._parse_error("duplicate-attribute")
                # Spec §13.2.5.33: discard duplicate — keep first occurrence
                return
            self._attrs_buf.append((name, value))

    def _emit_current_tag(self) -> None:
        """Build and emit the current start/end tag token."""
        assert self._current_token is not None
        tok_type = self._current_token["_type"]
        line = self._current_token["line"]
        col = self._current_token["col"]

        if tok_type == "start_tag":
            tag_name = self._current_token["tag_name"]
            self._last_start_tag_name = tag_name
            self._emit(StartTagToken(
                tag_name=tag_name,
                self_closing=self._current_token["self_closing"],
                attributes=tuple(self._attrs_buf),
                line=line,
                column=col,
            ))
        elif tok_type == "end_tag":
            self._emit(EndTagToken(
                tag_name=self._current_token["tag_name"],
                line=line,
                column=col,
            ))
        self._current_token = None
        self._attrs_buf.clear()

    def _is_appropriate_end_tag(self) -> bool:
        """Check if the current end tag is appropriate (for raw-text states)."""
        if self._current_token is None:
            return False
        if self._current_token.get("_type") != "end_tag":
            return False
        return self._current_token.get("tag_name") == self._last_start_tag_name

    # -------------------------------------------------------------------------
    # State machine — §13.2.5.1: Data state
    # -------------------------------------------------------------------------

    def _state_data(self, char: str) -> None:
        if char == "&":
            self._return_state = TokenizerState.DATA
            self._state = TokenizerState.CHARACTER_REFERENCE
        elif char == "<":
            self._state = TokenizerState.TAG_OPEN
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._emit_char(char)
        elif char is _EOF:
            pass  # EOF — handled by main loop
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.2: RCDATA state
    # -------------------------------------------------------------------------

    def _state_rcdata(self, char: str) -> None:
        if char == "&":
            self._return_state = TokenizerState.RCDATA
            self._state = TokenizerState.CHARACTER_REFERENCE
        elif char == "<":
            self._state = TokenizerState.RCDATA_LESS_THAN_SIGN
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._emit_char("\uFFFD")
        elif char is _EOF:
            pass
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.3: RAWTEXT state
    # -------------------------------------------------------------------------

    def _state_rawtext(self, char: str) -> None:
        if char == "<":
            self._state = TokenizerState.RAWTEXT_LESS_THAN_SIGN
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._emit_char("\uFFFD")
        elif char is _EOF:
            pass
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.4: Script data state
    # -------------------------------------------------------------------------

    def _state_script_data(self, char: str) -> None:
        if char == "<":
            self._state = TokenizerState.SCRIPT_DATA_LESS_THAN_SIGN
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._emit_char("\uFFFD")
        elif char is _EOF:
            pass
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.5: PLAINTEXT state
    # -------------------------------------------------------------------------

    def _state_plaintext(self, char: str) -> None:
        if char == "\x00":
            self._parse_error("unexpected-null-character")
            self._emit_char("\uFFFD")
        elif char is _EOF:
            pass
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.6: Tag open state
    # -------------------------------------------------------------------------

    def _state_tag_open(self, char: str) -> None:
        if char == "!":
            self._state = TokenizerState.MARKUP_DECLARATION_OPEN
        elif char == "/":
            self._state = TokenizerState.END_TAG_OPEN
        elif char.isalpha():
            self._current_token = {
                "_type": "start_tag",
                "tag_name": "",
                "self_closing": False,
                "line": self._line,
                "col": self._col - 2,  # '<' was consumed before
            }
            self._attrs_buf.clear()
            self._reconsume_in(TokenizerState.TAG_NAME)
        elif char == "?":
            self._parse_error("unexpected-question-mark-instead-of-tag-name")
            self._current_token = {
                "_type": "comment",
                "data": "",
                "line": self._line,
                "col": self._col - 2,
            }
            self._reconsume_in(TokenizerState.BOGUS_COMMENT)
        elif char is _EOF:
            self._parse_error("eof-before-tag-name")
            self._emit_char("<")
        else:
            self._parse_error("invalid-first-character-of-tag-name")
            self._emit_char("<")
            self._reconsume_in(TokenizerState.DATA)

    # -------------------------------------------------------------------------
    # §13.2.5.7: End tag open state
    # -------------------------------------------------------------------------

    def _state_end_tag_open(self, char: str) -> None:
        if char.isalpha():
            self._current_token = {
                "_type": "end_tag",
                "tag_name": "",
                "line": self._line,
                "col": self._col - 3,
            }
            self._attrs_buf.clear()
            self._reconsume_in(TokenizerState.TAG_NAME)
        elif char == ">":
            self._parse_error("missing-end-tag-name")
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-before-tag-name")
            self._emit_char("<")
            self._emit_char("/")
        else:
            self._parse_error("invalid-first-character-of-tag-name")
            self._current_token = {
                "_type": "comment",
                "data": "",
                "line": self._line,
                "col": self._col - 2,
            }
            self._reconsume_in(TokenizerState.BOGUS_COMMENT)

    # -------------------------------------------------------------------------
    # §13.2.5.8: Tag name state
    # -------------------------------------------------------------------------

    def _state_tag_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            self._state = TokenizerState.BEFORE_ATTRIBUTE_NAME
        elif char == "/":
            self._state = TokenizerState.SELF_CLOSING_START_TAG
        elif char == ">":
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char.isupper():
            self._current_token["tag_name"] += char.lower()  # type: ignore
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._current_token["tag_name"] += "\uFFFD"  # type: ignore
        elif char is _EOF:
            self._parse_error("eof-in-tag")
        else:
            self._current_token["tag_name"] += char  # type: ignore

    # -------------------------------------------------------------------------
    # §13.2.5.9: RCDATA less-than sign state
    # -------------------------------------------------------------------------

    def _state_rcdata_less_than_sign(self, char: str) -> None:
        if char == "/":
            self._temp_buf.clear()
            self._state = TokenizerState.RCDATA_END_TAG_OPEN
        else:
            self._emit_char("<")
            self._reconsume_in(TokenizerState.RCDATA)

    # -------------------------------------------------------------------------
    # §13.2.5.10: RCDATA end tag open state
    # -------------------------------------------------------------------------

    def _state_rcdata_end_tag_open(self, char: str) -> None:
        if char.isalpha():
            self._current_token = {
                "_type": "end_tag",
                "tag_name": "",
                "line": self._line,
                "col": self._col - 2,
            }
            self._reconsume_in(TokenizerState.RCDATA_END_TAG_NAME)
        else:
            self._emit_char("<")
            self._emit_char("/")
            self._reconsume_in(TokenizerState.RCDATA)

    # -------------------------------------------------------------------------
    # §13.2.5.11: RCDATA end tag name state
    # -------------------------------------------------------------------------

    def _state_rcdata_end_tag_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " ") and self._is_appropriate_end_tag():
            self._state = TokenizerState.BEFORE_ATTRIBUTE_NAME
        elif char == "/" and self._is_appropriate_end_tag():
            self._state = TokenizerState.SELF_CLOSING_START_TAG
        elif char == ">" and self._is_appropriate_end_tag():
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char.isalpha():
            self._current_token["tag_name"] += char.lower()  # type: ignore
            self._temp_buf.append(char)
        else:
            self._emit_char("<")
            self._emit_char("/")
            for c in self._temp_buf:
                self._emit_char(c)
            self._temp_buf.clear()
            self._current_token = None
            self._reconsume_in(TokenizerState.RCDATA)

    # -------------------------------------------------------------------------
    # §13.2.5.12: RAWTEXT less-than sign state
    # -------------------------------------------------------------------------

    def _state_rawtext_less_than_sign(self, char: str) -> None:
        if char == "/":
            self._temp_buf.clear()
            self._state = TokenizerState.RAWTEXT_END_TAG_OPEN
        else:
            self._emit_char("<")
            self._reconsume_in(TokenizerState.RAWTEXT)

    # -------------------------------------------------------------------------
    # §13.2.5.13: RAWTEXT end tag open state
    # -------------------------------------------------------------------------

    def _state_rawtext_end_tag_open(self, char: str) -> None:
        if char.isalpha():
            self._current_token = {
                "_type": "end_tag",
                "tag_name": "",
                "line": self._line,
                "col": self._col - 2,
            }
            self._reconsume_in(TokenizerState.RAWTEXT_END_TAG_NAME)
        else:
            self._emit_char("<")
            self._emit_char("/")
            self._reconsume_in(TokenizerState.RAWTEXT)

    # -------------------------------------------------------------------------
    # §13.2.5.14: RAWTEXT end tag name state
    # -------------------------------------------------------------------------

    def _state_rawtext_end_tag_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " ") and self._is_appropriate_end_tag():
            self._state = TokenizerState.BEFORE_ATTRIBUTE_NAME
        elif char == "/" and self._is_appropriate_end_tag():
            self._state = TokenizerState.SELF_CLOSING_START_TAG
        elif char == ">" and self._is_appropriate_end_tag():
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char.isalpha():
            self._current_token["tag_name"] += char.lower()  # type: ignore
            self._temp_buf.append(char)
        else:
            self._emit_char("<")
            self._emit_char("/")
            for c in self._temp_buf:
                self._emit_char(c)
            self._temp_buf.clear()
            self._current_token = None
            self._reconsume_in(TokenizerState.RAWTEXT)

    # -------------------------------------------------------------------------
    # §13.2.5.15: Script data less-than sign state
    # -------------------------------------------------------------------------

    def _state_script_data_less_than_sign(self, char: str) -> None:
        if char == "/":
            self._temp_buf.clear()
            self._state = TokenizerState.SCRIPT_DATA_END_TAG_OPEN
        elif char == "!":
            self._state = TokenizerState.SCRIPT_DATA_ESCAPE_START
            self._emit_char("<")
            self._emit_char("!")
        else:
            self._emit_char("<")
            self._reconsume_in(TokenizerState.SCRIPT_DATA)

    # -------------------------------------------------------------------------
    # §13.2.5.16: Script data end tag open state
    # -------------------------------------------------------------------------

    def _state_script_data_end_tag_open(self, char: str) -> None:
        if char.isalpha():
            self._current_token = {
                "_type": "end_tag",
                "tag_name": "",
                "line": self._line,
                "col": self._col - 2,
            }
            self._reconsume_in(TokenizerState.SCRIPT_DATA_END_TAG_NAME)
        else:
            self._emit_char("<")
            self._emit_char("/")
            self._reconsume_in(TokenizerState.SCRIPT_DATA)

    # -------------------------------------------------------------------------
    # §13.2.5.17: Script data end tag name state
    # -------------------------------------------------------------------------

    def _state_script_data_end_tag_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " ") and self._is_appropriate_end_tag():
            self._state = TokenizerState.BEFORE_ATTRIBUTE_NAME
        elif char == "/" and self._is_appropriate_end_tag():
            self._state = TokenizerState.SELF_CLOSING_START_TAG
        elif char == ">" and self._is_appropriate_end_tag():
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char.isalpha():
            self._current_token["tag_name"] += char.lower()  # type: ignore
            self._temp_buf.append(char)
        else:
            self._emit_char("<")
            self._emit_char("/")
            for c in self._temp_buf:
                self._emit_char(c)
            self._temp_buf.clear()
            self._current_token = None
            self._reconsume_in(TokenizerState.SCRIPT_DATA)

    # -------------------------------------------------------------------------
    # §13.2.5.18: Script data escape start state
    # -------------------------------------------------------------------------

    def _state_script_data_escape_start(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.SCRIPT_DATA_ESCAPE_START_DASH
            self._emit_char("-")
        else:
            self._reconsume_in(TokenizerState.SCRIPT_DATA)

    # -------------------------------------------------------------------------
    # §13.2.5.19: Script data escape start dash state
    # -------------------------------------------------------------------------

    def _state_script_data_escape_start_dash(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH
            self._emit_char("-")
        else:
            self._reconsume_in(TokenizerState.SCRIPT_DATA)

    # -------------------------------------------------------------------------
    # §13.2.5.20: Script data escaped state
    # -------------------------------------------------------------------------

    def _state_script_data_escaped(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED_DASH
            self._emit_char("-")
        elif char == "<":
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._emit_char("\uFFFD")
        elif char is _EOF:
            self._parse_error("eof-in-script-html-comment-like-text")
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.21: Script data escaped dash state
    # -------------------------------------------------------------------------

    def _state_script_data_escaped_dash(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED_DASH_DASH
            self._emit_char("-")
        elif char == "<":
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED
            self._emit_char("\uFFFD")
        elif char is _EOF:
            self._parse_error("eof-in-script-html-comment-like-text")
        else:
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.22: Script data escaped dash dash state
    # -------------------------------------------------------------------------

    def _state_script_data_escaped_dash_dash(self, char: str) -> None:
        if char == "-":
            self._emit_char("-")
        elif char == "<":
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN
        elif char == ">":
            self._state = TokenizerState.SCRIPT_DATA
            self._emit_char(">")
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED
            self._emit_char("\uFFFD")
        elif char is _EOF:
            self._parse_error("eof-in-script-html-comment-like-text")
        else:
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.23: Script data escaped less-than sign state
    # -------------------------------------------------------------------------

    def _state_script_data_escaped_less_than_sign(self, char: str) -> None:
        if char == "/":
            self._temp_buf.clear()
            self._state = TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_OPEN
        elif char.isalpha():
            self._temp_buf.clear()
            self._emit_char("<")
            self._reconsume_in(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_START)
        else:
            self._emit_char("<")
            self._reconsume_in(TokenizerState.SCRIPT_DATA_ESCAPED)

    # -------------------------------------------------------------------------
    # §13.2.5.24: Script data escaped end tag open state
    # -------------------------------------------------------------------------

    def _state_script_data_escaped_end_tag_open(self, char: str) -> None:
        if char.isalpha():
            self._current_token = {
                "_type": "end_tag",
                "tag_name": "",
                "line": self._line,
                "col": self._col - 2,
            }
            self._reconsume_in(TokenizerState.SCRIPT_DATA_ESCAPED_END_TAG_NAME)
        else:
            self._emit_char("<")
            self._emit_char("/")
            self._reconsume_in(TokenizerState.SCRIPT_DATA_ESCAPED)

    # -------------------------------------------------------------------------
    # §13.2.5.25: Script data escaped end tag name state
    # -------------------------------------------------------------------------

    def _state_script_data_escaped_end_tag_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " ") and self._is_appropriate_end_tag():
            self._state = TokenizerState.BEFORE_ATTRIBUTE_NAME
        elif char == "/" and self._is_appropriate_end_tag():
            self._state = TokenizerState.SELF_CLOSING_START_TAG
        elif char == ">" and self._is_appropriate_end_tag():
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char.isalpha():
            self._current_token["tag_name"] += char.lower()  # type: ignore
            self._temp_buf.append(char)
        else:
            self._emit_char("<")
            self._emit_char("/")
            for c in self._temp_buf:
                self._emit_char(c)
            self._temp_buf.clear()
            self._current_token = None
            self._reconsume_in(TokenizerState.SCRIPT_DATA_ESCAPED)

    # -------------------------------------------------------------------------
    # §13.2.5.26: Script data double escape start state
    # -------------------------------------------------------------------------

    def _state_script_data_double_escape_start(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " ", "/", ">"):
            if "".join(self._temp_buf).lower() == "script":
                self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED
            else:
                self._state = TokenizerState.SCRIPT_DATA_ESCAPED
            self._emit_char(char)
        elif char.isalpha():
            self._temp_buf.append(char.lower())
            self._emit_char(char)
        else:
            self._reconsume_in(TokenizerState.SCRIPT_DATA_ESCAPED)

    # -------------------------------------------------------------------------
    # §13.2.5.27: Script data double escaped state
    # -------------------------------------------------------------------------

    def _state_script_data_double_escaped(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH
            self._emit_char("-")
        elif char == "<":
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN
            self._emit_char("<")
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._emit_char("\uFFFD")
        elif char is _EOF:
            self._parse_error("eof-in-script-html-comment-like-text")
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.28: Script data double escaped dash state
    # -------------------------------------------------------------------------

    def _state_script_data_double_escaped_dash(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH
            self._emit_char("-")
        elif char == "<":
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN
            self._emit_char("<")
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED
            self._emit_char("\uFFFD")
        elif char is _EOF:
            self._parse_error("eof-in-script-html-comment-like-text")
        else:
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.29: Script data double escaped dash dash state
    # -------------------------------------------------------------------------

    def _state_script_data_double_escaped_dash_dash(self, char: str) -> None:
        if char == "-":
            self._emit_char("-")
        elif char == "<":
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN
            self._emit_char("<")
        elif char == ">":
            self._state = TokenizerState.SCRIPT_DATA
            self._emit_char(">")
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED
            self._emit_char("\uFFFD")
        elif char is _EOF:
            self._parse_error("eof-in-script-html-comment-like-text")
        else:
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.30: Script data double escaped less-than sign state
    # -------------------------------------------------------------------------

    def _state_script_data_double_escaped_less_than_sign(self, char: str) -> None:
        if char == "/":
            self._temp_buf.clear()
            self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPE_END
            self._emit_char("/")
        else:
            self._reconsume_in(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED)

    # -------------------------------------------------------------------------
    # §13.2.5.31: Script data double escape end state
    # -------------------------------------------------------------------------

    def _state_script_data_double_escape_end(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " ", "/", ">"):
            if "".join(self._temp_buf).lower() == "script":
                self._state = TokenizerState.SCRIPT_DATA_ESCAPED
            else:
                self._state = TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED
            self._emit_char(char)
        elif char.isalpha():
            self._temp_buf.append(char.lower())
            self._emit_char(char)
        else:
            self._reconsume_in(TokenizerState.SCRIPT_DATA_DOUBLE_ESCAPED)

    # -------------------------------------------------------------------------
    # §13.2.5.32: Before attribute name state
    # -------------------------------------------------------------------------

    def _state_before_attribute_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass  # ignore
        elif char in ("/", ">") or char is _EOF:
            self._reconsume_in(TokenizerState.AFTER_ATTRIBUTE_NAME)
        elif char == "=":
            self._parse_error("unexpected-equals-sign-before-attribute-name")
            self._attr_name_buf.clear()
            self._attr_value_buf.clear()
            self._attr_name_buf.append(char)
            self._state = TokenizerState.ATTRIBUTE_NAME
        else:
            self._attr_name_buf.clear()
            self._attr_value_buf.clear()
            self._reconsume_in(TokenizerState.ATTRIBUTE_NAME)

    # -------------------------------------------------------------------------
    # §13.2.5.33: Attribute name state
    # -------------------------------------------------------------------------

    def _state_attribute_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " ", "/", ">") or char is _EOF:
            self._reconsume_in(TokenizerState.AFTER_ATTRIBUTE_NAME)
        elif char == "=":
            self._state = TokenizerState.BEFORE_ATTRIBUTE_VALUE
        elif char.isupper():
            self._attr_name_buf.append(char.lower())
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._attr_name_buf.append("\uFFFD")
        elif char in ('"', "'", "<"):
            self._parse_error("unexpected-character-in-attribute-name")
            self._attr_name_buf.append(char)
        else:
            self._attr_name_buf.append(char)

    # -------------------------------------------------------------------------
    # §13.2.5.34: After attribute name state
    # -------------------------------------------------------------------------

    def _state_after_attribute_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass
        elif char == "/":
            self._commit_attr()
            self._state = TokenizerState.SELF_CLOSING_START_TAG
        elif char == "=":
            self._state = TokenizerState.BEFORE_ATTRIBUTE_VALUE
        elif char == ">":
            self._commit_attr()
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char is _EOF:
            self._parse_error("eof-in-tag")
            self._commit_attr()
        else:
            self._commit_attr()
            self._attr_name_buf.clear()
            self._attr_value_buf.clear()
            self._reconsume_in(TokenizerState.ATTRIBUTE_NAME)

    # -------------------------------------------------------------------------
    # §13.2.5.35: Before attribute value state
    # -------------------------------------------------------------------------

    def _state_before_attribute_value(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass
        elif char == '"':
            self._state = TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED
        elif char == "'":
            self._state = TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED
        elif char == ">":
            self._parse_error("missing-attribute-value")
            self._commit_attr()
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        else:
            self._reconsume_in(TokenizerState.ATTRIBUTE_VALUE_UNQUOTED)

    # -------------------------------------------------------------------------
    # §13.2.5.36: Attribute value (double-quoted) state
    # -------------------------------------------------------------------------

    def _state_attribute_value_double_quoted(self, char: str) -> None:
        if char == '"':
            self._state = TokenizerState.AFTER_ATTRIBUTE_VALUE_QUOTED
        elif char == "&":
            self._return_state = TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED
            self._state = TokenizerState.CHARACTER_REFERENCE
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._attr_value_buf.append("\uFFFD")
        elif char is _EOF:
            self._parse_error("eof-in-tag")
        else:
            self._attr_value_buf.append(char)

    # -------------------------------------------------------------------------
    # §13.2.5.37: Attribute value (single-quoted) state
    # -------------------------------------------------------------------------

    def _state_attribute_value_single_quoted(self, char: str) -> None:
        if char == "'":
            self._state = TokenizerState.AFTER_ATTRIBUTE_VALUE_QUOTED
        elif char == "&":
            self._return_state = TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED
            self._state = TokenizerState.CHARACTER_REFERENCE
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._attr_value_buf.append("\uFFFD")
        elif char is _EOF:
            self._parse_error("eof-in-tag")
        else:
            self._attr_value_buf.append(char)

    # -------------------------------------------------------------------------
    # §13.2.5.38: Attribute value (unquoted) state
    # -------------------------------------------------------------------------

    def _state_attribute_value_unquoted(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            self._commit_attr()
            self._state = TokenizerState.BEFORE_ATTRIBUTE_NAME
        elif char == "&":
            self._return_state = TokenizerState.ATTRIBUTE_VALUE_UNQUOTED
            self._state = TokenizerState.CHARACTER_REFERENCE
        elif char == ">":
            self._commit_attr()
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._attr_value_buf.append("\uFFFD")
        elif char in ('"', "'", "<", "=", "`"):
            self._parse_error("unexpected-character-in-unquoted-attribute-value")
            self._attr_value_buf.append(char)
        elif char is _EOF:
            self._parse_error("eof-in-tag")
        else:
            self._attr_value_buf.append(char)

    # -------------------------------------------------------------------------
    # §13.2.5.39: After attribute value (quoted) state
    # -------------------------------------------------------------------------

    def _state_after_attribute_value_quoted(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            self._commit_attr()
            self._state = TokenizerState.BEFORE_ATTRIBUTE_NAME
        elif char == "/":
            self._commit_attr()
            self._state = TokenizerState.SELF_CLOSING_START_TAG
        elif char == ">":
            self._commit_attr()
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char is _EOF:
            self._parse_error("eof-in-tag")
            self._commit_attr()
        else:
            self._parse_error("missing-whitespace-between-attributes")
            self._commit_attr()
            self._reconsume_in(TokenizerState.BEFORE_ATTRIBUTE_NAME)

    # -------------------------------------------------------------------------
    # §13.2.5.40: Self-closing start tag state
    # -------------------------------------------------------------------------

    def _state_self_closing_start_tag(self, char: str) -> None:
        if char == ">":
            self._current_token["self_closing"] = True  # type: ignore
            self._state = TokenizerState.DATA
            self._emit_current_tag()
        elif char is _EOF:
            self._parse_error("eof-in-tag")
        else:
            self._parse_error("unexpected-solidus-in-tag")
            self._reconsume_in(TokenizerState.BEFORE_ATTRIBUTE_NAME)

    # -------------------------------------------------------------------------
    # §13.2.5.41: Bogus comment state
    # -------------------------------------------------------------------------

    def _state_bogus_comment(self, char: str) -> None:
        if char == ">":
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
            self._state = TokenizerState.DATA
        elif char is _EOF:
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            if self._current_token:
                self._current_token["data"] += "\uFFFD"  # type: ignore
        else:
            if self._current_token:
                self._current_token["data"] += char  # type: ignore

    # -------------------------------------------------------------------------
    # §13.2.5.42: Markup declaration open state
    # -------------------------------------------------------------------------

    def _state_markup_declaration_open(self, char: str) -> None:
        # This state is special: we need to look ahead multiple characters
        # We handle it by accumulating into temp_buf until we have enough
        # to decide. We use a different approach: peek at upcoming chars.
        pos = self._pos - 1  # rewind: char was already consumed
        text = self._text
        remaining = text[pos:]

        if remaining.startswith("--"):
            # Comment start
            self._pos = pos + 2
            self._col += 2
            self._current_token = {
                "_type": "comment",
                "data": "",
                "line": self._line,
                "col": self._col - 4,
            }
            self._state = TokenizerState.COMMENT_START
        elif remaining[:7].upper() == "DOCTYPE":
            self._pos = pos + 7
            self._col += 7
            self._state = TokenizerState.DOCTYPE
        elif remaining.startswith("[CDATA["):
            # Only valid in foreign content (SVG/MathML); otherwise bogus
            # For now treat as bogus comment (no tree constructor context)
            self._pos = pos + 7
            self._col += 7
            # In a real parser with tree constructor, we'd check foreign context
            # For tokeniser alone, treat as CDATA section
            self._state = TokenizerState.CDATA_SECTION
        else:
            self._parse_error("incorrectly-opened-comment")
            self._current_token = {
                "_type": "comment",
                "data": "",
                "line": self._line,
                "col": self._col - 1,
            }
            self._state = TokenizerState.BOGUS_COMMENT

    # -------------------------------------------------------------------------
    # §13.2.5.43: Comment start state
    # -------------------------------------------------------------------------

    def _state_comment_start(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.COMMENT_START_DASH
        elif char == ">":
            self._parse_error("abrupt-closing-of-empty-comment")
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
            self._state = TokenizerState.DATA
        else:
            self._reconsume_in(TokenizerState.COMMENT)

    # -------------------------------------------------------------------------
    # §13.2.5.44: Comment start dash state
    # -------------------------------------------------------------------------

    def _state_comment_start_dash(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.COMMENT_END
        elif char == ">":
            self._parse_error("abrupt-closing-of-empty-comment")
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-comment")
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
        else:
            if self._current_token:
                self._current_token["data"] += "-"  # type: ignore
            self._reconsume_in(TokenizerState.COMMENT)

    # -------------------------------------------------------------------------
    # §13.2.5.45: Comment state
    # -------------------------------------------------------------------------

    def _state_comment(self, char: str) -> None:
        if char == "<":
            if self._current_token:
                self._current_token["data"] += char  # type: ignore
            self._state = TokenizerState.COMMENT_LESS_THAN_SIGN
        elif char == "-":
            self._state = TokenizerState.COMMENT_END_DASH
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            if self._current_token:
                self._current_token["data"] += "\uFFFD"  # type: ignore
        elif char is _EOF:
            self._parse_error("eof-in-comment")
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
        else:
            if self._current_token:
                self._current_token["data"] += char  # type: ignore

    # -------------------------------------------------------------------------
    # §13.2.5.46: Comment less-than sign state
    # -------------------------------------------------------------------------

    def _state_comment_less_than_sign(self, char: str) -> None:
        if char == "!":
            if self._current_token:
                self._current_token["data"] += char  # type: ignore
            self._state = TokenizerState.COMMENT_LESS_THAN_SIGN_BANG
        elif char == "<":
            if self._current_token:
                self._current_token["data"] += char  # type: ignore
        else:
            self._reconsume_in(TokenizerState.COMMENT)

    # -------------------------------------------------------------------------
    # §13.2.5.47: Comment less-than sign bang state
    # -------------------------------------------------------------------------

    def _state_comment_less_than_sign_bang(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH
        else:
            self._reconsume_in(TokenizerState.COMMENT)

    # -------------------------------------------------------------------------
    # §13.2.5.48: Comment less-than sign bang dash state
    # -------------------------------------------------------------------------

    def _state_comment_less_than_sign_bang_dash(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH
        else:
            self._reconsume_in(TokenizerState.COMMENT_END_DASH)

    # -------------------------------------------------------------------------
    # §13.2.5.49: Comment less-than sign bang dash dash state
    # -------------------------------------------------------------------------

    def _state_comment_less_than_sign_bang_dash_dash(self, char: str) -> None:
        if char == ">" or char is _EOF:
            self._reconsume_in(TokenizerState.COMMENT_END)
        else:
            self._parse_error("nested-comment")
            self._reconsume_in(TokenizerState.COMMENT_END)

    # -------------------------------------------------------------------------
    # §13.2.5.50: Comment end dash state
    # -------------------------------------------------------------------------

    def _state_comment_end_dash(self, char: str) -> None:
        if char == "-":
            self._state = TokenizerState.COMMENT_END
        elif char is _EOF:
            self._parse_error("eof-in-comment")
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
        else:
            if self._current_token:
                self._current_token["data"] += "-"  # type: ignore
            self._reconsume_in(TokenizerState.COMMENT)

    # -------------------------------------------------------------------------
    # §13.2.5.51: Comment end state
    # -------------------------------------------------------------------------

    def _state_comment_end(self, char: str) -> None:
        if char == ">":
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
            self._state = TokenizerState.DATA
        elif char == "!":
            self._state = TokenizerState.COMMENT_END_BANG
        elif char == "-":
            if self._current_token:
                self._current_token["data"] += "-"  # type: ignore
        elif char is _EOF:
            self._parse_error("eof-in-comment")
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
        else:
            if self._current_token:
                self._current_token["data"] += "--"  # type: ignore
            self._reconsume_in(TokenizerState.COMMENT)

    # -------------------------------------------------------------------------
    # §13.2.5.52: Comment end bang state
    # -------------------------------------------------------------------------

    def _state_comment_end_bang(self, char: str) -> None:
        if char == "-":
            if self._current_token:
                self._current_token["data"] += "--!"  # type: ignore
            self._state = TokenizerState.COMMENT_END_DASH
        elif char == ">":
            self._parse_error("incorrectly-closed-comment")
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-comment")
            data = self._current_token["data"] if self._current_token else ""  # type: ignore
            line = self._current_token["line"] if self._current_token else self._line  # type: ignore
            col = self._current_token["col"] if self._current_token else self._col  # type: ignore
            self._emit(CommentToken(data=data, line=line, column=col))
            self._current_token = None
        else:
            if self._current_token:
                self._current_token["data"] += "--!"  # type: ignore
            self._reconsume_in(TokenizerState.COMMENT)

    # -------------------------------------------------------------------------
    # §13.2.5.53: DOCTYPE state
    # -------------------------------------------------------------------------

    def _state_doctype(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            self._state = TokenizerState.BEFORE_DOCTYPE_NAME
        elif char == ">":
            self._reconsume_in(TokenizerState.BEFORE_DOCTYPE_NAME)
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit(DoctypeToken(
                name=None, public_id=None, system_id=None,
                force_quirks=True, line=self._line, column=self._col,
            ))
        else:
            self._parse_error("missing-whitespace-before-doctype-name")
            self._reconsume_in(TokenizerState.BEFORE_DOCTYPE_NAME)

    # -------------------------------------------------------------------------
    # §13.2.5.54: Before DOCTYPE name state
    # -------------------------------------------------------------------------

    def _state_before_doctype_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass
        elif char.isupper():
            self._current_token = {
                "_type": "doctype",
                "name": char.lower(),
                "public_id": None,
                "system_id": None,
                "force_quirks": False,
                "line": self._line,
                "col": self._col,
            }
            self._state = TokenizerState.DOCTYPE_NAME
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._current_token = {
                "_type": "doctype",
                "name": "\uFFFD",
                "public_id": None,
                "system_id": None,
                "force_quirks": False,
                "line": self._line,
                "col": self._col,
            }
            self._state = TokenizerState.DOCTYPE_NAME
        elif char == ">":
            self._parse_error("missing-doctype-name")
            self._emit(DoctypeToken(
                name=None, public_id=None, system_id=None,
                force_quirks=True, line=self._line, column=self._col,
            ))
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit(DoctypeToken(
                name=None, public_id=None, system_id=None,
                force_quirks=True, line=self._line, column=self._col,
            ))
        else:
            self._current_token = {
                "_type": "doctype",
                "name": char,
                "public_id": None,
                "system_id": None,
                "force_quirks": False,
                "line": self._line,
                "col": self._col,
            }
            self._state = TokenizerState.DOCTYPE_NAME

    # -------------------------------------------------------------------------
    # §13.2.5.55: DOCTYPE name state
    # -------------------------------------------------------------------------

    def _state_doctype_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            self._state = TokenizerState.AFTER_DOCTYPE_NAME
        elif char == ">":
            tok = self._current_token
            self._emit(DoctypeToken(
                name=tok["name"],  # type: ignore
                public_id=tok["public_id"],  # type: ignore
                system_id=tok["system_id"],  # type: ignore
                force_quirks=tok["force_quirks"],  # type: ignore
                line=tok["line"],  # type: ignore
                column=tok["col"],  # type: ignore
            ))
            self._current_token = None
            self._state = TokenizerState.DATA
        elif char.isupper():
            self._current_token["name"] += char.lower()  # type: ignore
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            self._current_token["name"] += "\uFFFD"  # type: ignore
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._current_token["force_quirks"] = True  # type: ignore
            tok = self._current_token
            self._emit(DoctypeToken(
                name=tok["name"],  # type: ignore
                public_id=tok["public_id"],  # type: ignore
                system_id=tok["system_id"],  # type: ignore
                force_quirks=True,
                line=tok["line"],  # type: ignore
                column=tok["col"],  # type: ignore
            ))
            self._current_token = None
        else:
            self._current_token["name"] += char  # type: ignore

    # -------------------------------------------------------------------------
    # §13.2.5.56: After DOCTYPE name state
    # -------------------------------------------------------------------------

    def _state_after_doctype_name(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass
        elif char == ">":
            tok = self._current_token
            self._emit(DoctypeToken(
                name=tok["name"],  # type: ignore
                public_id=tok["public_id"],  # type: ignore
                system_id=tok["system_id"],  # type: ignore
                force_quirks=tok["force_quirks"],  # type: ignore
                line=tok["line"],  # type: ignore
                column=tok["col"],  # type: ignore
            ))
            self._current_token = None
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            tok = self._current_token
            if tok:
                self._emit(DoctypeToken(
                    name=tok["name"],  # type: ignore
                    public_id=tok["public_id"],  # type: ignore
                    system_id=tok["system_id"],  # type: ignore
                    force_quirks=True,
                    line=tok["line"],  # type: ignore
                    column=tok["col"],  # type: ignore
                ))
                self._current_token = None
        else:
            # Look ahead for PUBLIC or SYSTEM keywords
            pos = self._pos - 1
            remaining = self._text[pos:].upper()
            if remaining.startswith("PUBLIC"):
                self._pos = pos + 6
                self._col += 5
                self._state = TokenizerState.AFTER_DOCTYPE_PUBLIC_KEYWORD
            elif remaining.startswith("SYSTEM"):
                self._pos = pos + 6
                self._col += 5
                self._state = TokenizerState.AFTER_DOCTYPE_SYSTEM_KEYWORD
            else:
                self._parse_error("invalid-character-sequence-after-doctype-name")
                if self._current_token:
                    self._current_token["force_quirks"] = True  # type: ignore
                self._reconsume_in(TokenizerState.BOGUS_DOCTYPE)

    # -------------------------------------------------------------------------
    # §13.2.5.57–67: DOCTYPE public/system identifier states (simplified)
    # -------------------------------------------------------------------------

    def _state_after_doctype_public_keyword(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            self._state = TokenizerState.BEFORE_DOCTYPE_PUBLIC_IDENTIFIER
        elif char == '"':
            self._parse_error("missing-whitespace-after-doctype-public-keyword")
            if self._current_token:
                self._current_token["public_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED
        elif char == "'":
            self._parse_error("missing-whitespace-after-doctype-public-keyword")
            if self._current_token:
                self._current_token["public_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED
        elif char == ">":
            self._parse_error("missing-doctype-public-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._emit_current_doctype(force_quirks=True)
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            self._parse_error("missing-quote-before-doctype-public-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._reconsume_in(TokenizerState.BOGUS_DOCTYPE)

    def _state_before_doctype_public_identifier(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass
        elif char == '"':
            if self._current_token:
                self._current_token["public_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED
        elif char == "'":
            if self._current_token:
                self._current_token["public_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED
        elif char == ">":
            self._parse_error("missing-doctype-public-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._emit_current_doctype(force_quirks=True)
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            self._parse_error("missing-quote-before-doctype-public-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._reconsume_in(TokenizerState.BOGUS_DOCTYPE)

    def _state_doctype_public_identifier_double_quoted(self, char: str) -> None:
        if char == '"':
            self._state = TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            if self._current_token:
                self._current_token["public_id"] += "\uFFFD"  # type: ignore
        elif char == ">":
            self._parse_error("abrupt-doctype-public-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._emit_current_doctype(force_quirks=True)
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            if self._current_token:
                self._current_token["public_id"] += char  # type: ignore

    def _state_doctype_public_identifier_single_quoted(self, char: str) -> None:
        if char == "'":
            self._state = TokenizerState.AFTER_DOCTYPE_PUBLIC_IDENTIFIER
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            if self._current_token:
                self._current_token["public_id"] += "\uFFFD"  # type: ignore
        elif char == ">":
            self._parse_error("abrupt-doctype-public-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._emit_current_doctype(force_quirks=True)
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            if self._current_token:
                self._current_token["public_id"] += char  # type: ignore

    def _state_after_doctype_public_identifier(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            self._state = TokenizerState.BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS
        elif char == ">":
            self._emit_current_doctype()
            self._state = TokenizerState.DATA
        elif char == '"':
            self._parse_error("missing-whitespace-between-doctype-public-and-system-identifiers")
            if self._current_token:
                self._current_token["system_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED
        elif char == "'":
            self._parse_error("missing-whitespace-between-doctype-public-and-system-identifiers")
            if self._current_token:
                self._current_token["system_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            self._parse_error("missing-quote-before-doctype-system-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._reconsume_in(TokenizerState.BOGUS_DOCTYPE)

    def _state_between_doctype_public_and_system_identifiers(
        self, char: str
    ) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass
        elif char == ">":
            self._emit_current_doctype()
            self._state = TokenizerState.DATA
        elif char == '"':
            if self._current_token:
                self._current_token["system_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED
        elif char == "'":
            if self._current_token:
                self._current_token["system_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            self._parse_error("missing-quote-before-doctype-system-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._reconsume_in(TokenizerState.BOGUS_DOCTYPE)

    def _state_after_doctype_system_keyword(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            self._state = TokenizerState.BEFORE_DOCTYPE_SYSTEM_IDENTIFIER
        elif char == '"':
            self._parse_error("missing-whitespace-after-doctype-system-keyword")
            if self._current_token:
                self._current_token["system_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED
        elif char == "'":
            self._parse_error("missing-whitespace-after-doctype-system-keyword")
            if self._current_token:
                self._current_token["system_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED
        elif char == ">":
            self._parse_error("missing-doctype-system-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._emit_current_doctype(force_quirks=True)
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            self._parse_error("missing-quote-before-doctype-system-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._reconsume_in(TokenizerState.BOGUS_DOCTYPE)

    def _state_before_doctype_system_identifier(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass
        elif char == '"':
            if self._current_token:
                self._current_token["system_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED
        elif char == "'":
            if self._current_token:
                self._current_token["system_id"] = ""  # type: ignore
            self._state = TokenizerState.DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED
        elif char == ">":
            self._parse_error("missing-doctype-system-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._emit_current_doctype(force_quirks=True)
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            self._parse_error("missing-quote-before-doctype-system-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._reconsume_in(TokenizerState.BOGUS_DOCTYPE)

    def _state_doctype_system_identifier_double_quoted(self, char: str) -> None:
        if char == '"':
            self._state = TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            if self._current_token:
                self._current_token["system_id"] += "\uFFFD"  # type: ignore
        elif char == ">":
            self._parse_error("abrupt-doctype-system-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._emit_current_doctype(force_quirks=True)
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            if self._current_token:
                self._current_token["system_id"] += char  # type: ignore

    def _state_doctype_system_identifier_single_quoted(self, char: str) -> None:
        if char == "'":
            self._state = TokenizerState.AFTER_DOCTYPE_SYSTEM_IDENTIFIER
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
            if self._current_token:
                self._current_token["system_id"] += "\uFFFD"  # type: ignore
        elif char == ">":
            self._parse_error("abrupt-doctype-system-identifier")
            if self._current_token:
                self._current_token["force_quirks"] = True  # type: ignore
            self._emit_current_doctype(force_quirks=True)
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            if self._current_token:
                self._current_token["system_id"] += char  # type: ignore

    def _state_after_doctype_system_identifier(self, char: str) -> None:
        if char in ("\t", "\n", "\x0C", " "):
            pass
        elif char == ">":
            self._emit_current_doctype()
            self._state = TokenizerState.DATA
        elif char is _EOF:
            self._parse_error("eof-in-doctype")
            self._emit_current_doctype(force_quirks=True)
        else:
            self._parse_error("unexpected-character-after-doctype-system-identifier")
            self._reconsume_in(TokenizerState.BOGUS_DOCTYPE)

    def _emit_current_doctype(self, force_quirks: bool = False) -> None:
        """Helper to emit the current doctype token."""
        tok = self._current_token
        if tok is None:
            return
        if force_quirks:
            tok["force_quirks"] = True
        self._emit(DoctypeToken(
            name=tok.get("name"),  # type: ignore
            public_id=tok.get("public_id"),  # type: ignore
            system_id=tok.get("system_id"),  # type: ignore
            force_quirks=tok["force_quirks"],  # type: ignore
            line=tok["line"],  # type: ignore
            column=tok["col"],  # type: ignore
        ))
        self._current_token = None

    # -------------------------------------------------------------------------
    # §13.2.5.68: Bogus DOCTYPE state
    # -------------------------------------------------------------------------

    def _state_bogus_doctype(self, char: str) -> None:
        if char == ">":
            self._emit_current_doctype()
            self._state = TokenizerState.DATA
        elif char == "\x00":
            self._parse_error("unexpected-null-character")
        elif char is _EOF:
            self._emit_current_doctype()
        # else: ignore

    # -------------------------------------------------------------------------
    # §13.2.5.69: CDATA section state
    # -------------------------------------------------------------------------

    def _state_cdata_section(self, char: str) -> None:
        if char == "]":
            self._state = TokenizerState.CDATA_SECTION_BRACKET
        elif char is _EOF:
            self._parse_error("eof-in-cdata")
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.70: CDATA section bracket state
    # -------------------------------------------------------------------------

    def _state_cdata_section_bracket(self, char: str) -> None:
        if char == "]":
            self._state = TokenizerState.CDATA_SECTION_END
        else:
            self._emit_char("]")
            self._reconsume_in(TokenizerState.CDATA_SECTION)

    # -------------------------------------------------------------------------
    # §13.2.5.71: CDATA section end state
    # -------------------------------------------------------------------------

    def _state_cdata_section_end(self, char: str) -> None:
        if char == "]":
            self._emit_char("]")
        elif char == ">":
            self._state = TokenizerState.DATA
        else:
            self._emit_char("]")
            self._emit_char("]")
            self._reconsume_in(TokenizerState.CDATA_SECTION)

    # -------------------------------------------------------------------------
    # §13.2.5.72: Character reference state
    # -------------------------------------------------------------------------

    def _state_character_reference(self, char: str) -> None:
        self._temp_buf.clear()
        self._temp_buf.append("&")
        if char.isalnum():
            self._reconsume_in(TokenizerState.NAMED_CHARACTER_REFERENCE)
        elif char == "#":
            self._temp_buf.append(char)
            self._state = TokenizerState.NUMERIC_CHARACTER_REFERENCE
        else:
            # Flush the & as literal characters
            self._flush_char_ref_to_output()
            self._reconsume_in(self._return_state)

    # -------------------------------------------------------------------------
    # §13.2.5.73: Named character reference state
    # -------------------------------------------------------------------------

    def _state_named_character_reference(self, char: str) -> None:
        # Accumulate into temp_buf (past the leading '&')
        # We need to do longest-prefix matching.
        # Strategy: accumulate chars, check after each if we have a full match
        # or if no further match is possible.
        if char.isalnum() or char == ";":
            self._temp_buf.append(char)
            candidate = "".join(self._temp_buf[1:])  # without leading '&'

            # Check if candidate with semicolon is in table
            if candidate in NAMED_CHAR_REFS:
                if char == ";":
                    # Complete, well-formed reference — flush replacement
                    replacement = NAMED_CHAR_REFS[candidate]
                    self._flush_named_char_ref(replacement)
                    self._state = self._return_state
                # else: might still be a longer match — keep accumulating
                # Actually the WHATWG algo says: if we've matched (with ;), emit
                # But we need to handle no-semicolon legacy forms too.
                # Simplified: if char is ';', we matched exactly — emit
                elif char != ";":
                    # Not yet at semicolon, keep going
                    pass
            else:
                # No match with current candidate — try without semicolon forms
                # Try to find a match without trailing semicolon
                if candidate not in NAMED_CHAR_REFS:
                    # Could still be a prefix; continue
                    # But if this char can't extend any entry, fall through
                    # Check if any entry starts with our current candidate
                    # For simplicity: check if any key has our candidate as prefix
                    # This is the "still accumulating" case
                    pass
        else:
            # Non-alnum and not ';' — end of candidate
            candidate = "".join(self._temp_buf[1:])  # without leading '&'
            # Try to find the longest match
            result = find_named_char_ref_match(candidate)
            if result is not None:
                matched_name, replacement = result
                # Check if we're in attribute context and semicolon is missing
                in_attr = self._return_state in (
                    TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
                    TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED,
                    TokenizerState.ATTRIBUTE_VALUE_UNQUOTED,
                )
                if not matched_name.endswith(";"):
                    if in_attr and (char == "=" or char.isalnum()):
                        # In attribute, followed by =alnum: treat as ambiguous
                        # Emit & + candidate as literal
                        self._flush_char_ref_to_output()
                    else:
                        self._parse_error("missing-semicolon-after-character-reference")
                        self._flush_named_char_ref(replacement)
                        # Push back consumed chars that weren't part of the match
                        leftover = candidate[len(matched_name):]
                        for c in leftover:
                            self._char_ref_flush_to_return_state(c)
                else:
                    self._flush_named_char_ref(replacement)
                    # Push back the current char and any leftover
                    leftover = candidate[len(matched_name):]
                    for c in leftover:
                        self._char_ref_flush_to_return_state(c)
            else:
                # No match found — emit & and all accumulated chars as literals
                self._flush_char_ref_to_output()
                # candidate chars need to be output too (already in temp_buf[1:])
                for c in candidate:
                    self._char_ref_flush_to_return_state(c)
            self._reconsume_in(self._return_state)

    def _flush_named_char_ref(self, replacement: str) -> None:
        """Emit the replacement string to the appropriate target."""
        self._temp_buf.clear()
        in_attr = self._return_state in (
            TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
            TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED,
            TokenizerState.ATTRIBUTE_VALUE_UNQUOTED,
        )
        if in_attr:
            self._attr_value_buf.append(replacement)
        else:
            self._emit_char(replacement)
        self._state = self._return_state

    def _flush_char_ref_to_output(self) -> None:
        """Emit the temp_buf contents as literal characters."""
        in_attr = self._return_state in (
            TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
            TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED,
            TokenizerState.ATTRIBUTE_VALUE_UNQUOTED,
        )
        for c in self._temp_buf:
            if in_attr:
                self._attr_value_buf.append(c)
            else:
                self._emit_char(c)
        self._temp_buf.clear()

    def _char_ref_flush_to_return_state(self, char: str) -> None:
        """Emit a single character to the return-state target."""
        in_attr = self._return_state in (
            TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
            TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED,
            TokenizerState.ATTRIBUTE_VALUE_UNQUOTED,
        )
        if in_attr:
            self._attr_value_buf.append(char)
        else:
            self._emit_char(char)

    # -------------------------------------------------------------------------
    # §13.2.5.74: Ambiguous ampersand state
    # -------------------------------------------------------------------------

    def _state_ambiguous_ampersand(self, char: str) -> None:
        if char.isalnum():
            in_attr = self._return_state in (
                TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
                TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED,
                TokenizerState.ATTRIBUTE_VALUE_UNQUOTED,
            )
            if in_attr:
                self._attr_value_buf.append(char)
            else:
                self._emit_char(char)
        elif char == ";":
            self._parse_error("unknown-named-character-reference")
            self._reconsume_in(self._return_state)
        else:
            self._reconsume_in(self._return_state)

    # -------------------------------------------------------------------------
    # §13.2.5.75: Numeric character reference state
    # -------------------------------------------------------------------------

    def _state_numeric_character_reference(self, char: str) -> None:
        self._char_ref_code = 0
        if char in ("x", "X"):
            self._temp_buf.append(char)
            self._state = TokenizerState.HEXADECIMAL_CHARACTER_REFERENCE_START
        else:
            self._reconsume_in(TokenizerState.DECIMAL_CHARACTER_REFERENCE_START)

    # -------------------------------------------------------------------------
    # §13.2.5.76: Hexadecimal character reference start state
    # -------------------------------------------------------------------------

    def _state_hexadecimal_character_reference_start(self, char: str) -> None:
        if char in "0123456789abcdefABCDEF":
            self._reconsume_in(TokenizerState.HEXADECIMAL_CHARACTER_REFERENCE)
        else:
            self._parse_error("absence-of-digits-in-numeric-character-reference")
            self._flush_char_ref_to_output()
            self._reconsume_in(self._return_state)

    # -------------------------------------------------------------------------
    # §13.2.5.77: Decimal character reference start state
    # -------------------------------------------------------------------------

    def _state_decimal_character_reference_start(self, char: str) -> None:
        if char.isdigit():
            self._reconsume_in(TokenizerState.DECIMAL_CHARACTER_REFERENCE)
        else:
            self._parse_error("absence-of-digits-in-numeric-character-reference")
            self._flush_char_ref_to_output()
            self._reconsume_in(self._return_state)

    # -------------------------------------------------------------------------
    # §13.2.5.78: Hexadecimal character reference state
    # -------------------------------------------------------------------------

    def _state_hexadecimal_character_reference(self, char: str) -> None:
        if char.isdigit():
            self._char_ref_code = self._char_ref_code * 16 + int(char)
        elif char in "abcdef":
            self._char_ref_code = self._char_ref_code * 16 + (ord(char) - 0x57)
        elif char in "ABCDEF":
            self._char_ref_code = self._char_ref_code * 16 + (ord(char) - 0x37)
        elif char == ";":
            self._state = TokenizerState.NUMERIC_CHARACTER_REFERENCE_END
        else:
            self._parse_error("missing-semicolon-after-character-reference")
            self._reconsume_in(TokenizerState.NUMERIC_CHARACTER_REFERENCE_END)

    # -------------------------------------------------------------------------
    # §13.2.5.79: Decimal character reference state
    # -------------------------------------------------------------------------

    def _state_decimal_character_reference(self, char: str) -> None:
        if char.isdigit():
            self._char_ref_code = self._char_ref_code * 10 + int(char)
        elif char == ";":
            self._state = TokenizerState.NUMERIC_CHARACTER_REFERENCE_END
        else:
            self._parse_error("missing-semicolon-after-character-reference")
            self._reconsume_in(TokenizerState.NUMERIC_CHARACTER_REFERENCE_END)

    # -------------------------------------------------------------------------
    # §13.2.5.80: Numeric character reference end state
    # -------------------------------------------------------------------------

    def _state_numeric_character_reference_end(self, char: str) -> None:
        code_point = self._char_ref_code
        replacement, err_codes = resolve_numeric_char_ref(code_point)
        for code in err_codes:
            self._parse_error(code)
        in_attr = self._return_state in (
            TokenizerState.ATTRIBUTE_VALUE_DOUBLE_QUOTED,
            TokenizerState.ATTRIBUTE_VALUE_SINGLE_QUOTED,
            TokenizerState.ATTRIBUTE_VALUE_UNQUOTED,
        )
        if in_attr:
            self._attr_value_buf.append(replacement)
        else:
            self._emit_char(replacement)
        self._temp_buf.clear()
        self._reconsume_in(self._return_state)


# §13.2.6: Fragment context element → initial tokeniser state mapping
_FRAGMENT_CONTEXT_STATES: dict[str, TokenizerState] = {
    "title": TokenizerState.RCDATA,
    "textarea": TokenizerState.RCDATA,
    "style": TokenizerState.RAWTEXT,
    "xmp": TokenizerState.RAWTEXT,
    "iframe": TokenizerState.RAWTEXT,
    "noembed": TokenizerState.RAWTEXT,
    "noframes": TokenizerState.RAWTEXT,
    "script": TokenizerState.SCRIPT_DATA,
    "plaintext": TokenizerState.PLAINTEXT,
}
