"""TreeBuilder — WHATWG HTML tree construction algorithm (§13.2.6).

This module implements the complete tree construction state machine.
Each of the 23 WHATWG insertion modes is implemented as a private method
named ``_process_<mode_value>(token)``. A dispatch dict maps each mode to
its method.

Constraints:
- INV-002: No structural shortcuts. The spec algorithm drives every insertion.
- INV-004: All 23 insertion modes are present as distinct methods.
- INV-005: Only DOM factory methods and tree mutation methods are used.
  Never construct node objects directly.
- ADR-002 protocol: set_state() is called AFTER receiving a StartTagToken
  and BEFORE the next next() call on the generator.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from aspose_html.tokenizer import (
    Tokenizer,
    TokenizerState,
    DoctypeToken,
    StartTagToken,
    EndTagToken,
    CommentToken,
    CharacterToken,
    EofToken,
    AnyToken,
)
from aspose_html.dom import (
    Document,
    Element,
    DocumentType,
    ParseError,
    NodeType,
)
from aspose_html.tree._insertion_modes import InsertionMode
from aspose_html.tree._open_elements import StackOfOpenElements
from aspose_html.tree._active_formatting import ActiveFormattingList
from aspose_html.tree._template import TemplateInsertionModeStack
from aspose_html.tree._foster_parenting import get_foster_parent_location
from aspose_html.tree._doctype_switch import determine_quirks_mode
from aspose_html.tree._foreign_content import (
    SVG_NAMESPACE, MATHML_NAMESPACE, HTML_NAMESPACE,
    adjust_svg_attributes, adjust_mathml_attributes,
)

# Raw-text element tag names — tree builder switches tokenizer state after
# processing start tags for these elements (ADR-002 protocol).
_RAWTEXT_ELEMENTS: frozenset[str] = frozenset({
    "style", "xmp", "iframe", "noembed", "noframes", "noscript",
})
_RCDATA_ELEMENTS: frozenset[str] = frozenset({"title", "textarea"})
_SCRIPT_DATA_ELEMENTS: frozenset[str] = frozenset({"script"})
_PLAINTEXT_ELEMENTS: frozenset[str] = frozenset({"plaintext"})

# Void elements — self-closing by definition
_VOID_ELEMENTS: frozenset[str] = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

# Elements that imply end tags for <p> closure
_P_IMPLIED_END_TAGS: frozenset[str] = frozenset({
    "address", "article", "aside", "blockquote", "center", "details",
    "dialog", "dir", "div", "dl", "fieldset", "figcaption", "figure",
    "footer", "header", "hgroup", "hr", "main", "menu", "nav",
    "ol", "p", "pre", "section", "summary", "table", "ul",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "form", "li",  # these close <p> too
})

# Formatting element tag names
_FORMATTING_ELEMENTS: frozenset[str] = frozenset({
    "a", "b", "big", "code", "em", "font", "i", "nobr",
    "s", "small", "strike", "strong", "tt", "u",
})

# Implied end tags elements
_IMPLIED_END_TAGS: frozenset[str] = frozenset({
    "dd", "dt", "li", "optgroup", "option",
    "p", "rb", "rp", "rt", "rtc",
})

# Table-related elements
_TABLE_BODY_ELEMENTS: frozenset[str] = frozenset({"tbody", "tfoot", "thead"})
_TABLE_CELL_ELEMENTS: frozenset[str] = frozenset({"td", "th"})


def run_navigation_html_parser(html: str, document: Document) -> None:
    """Run HTML tree-construction into an existing Document for navigation.

    Internal Track-56 adapter hook used by Window's navigation pipeline.
    This keeps parser entry deterministic and centralized instead of
    ad-hoc direct parser construction in navigation code.
    """
    if not isinstance(html, str):
        raise TypeError(f"run_navigation_html_parser() expects str html, got {type(html).__name__}")
    tokenizer = Tokenizer(html)
    builder = TreeBuilder(tokenizer, document, fragment_context=None)
    builder.run()


class TreeBuilder:
    """Drives the WHATWG tree construction algorithm.

    The tree builder consumes tokens from a Tokenizer and builds a Document
    tree. It manages the insertion mode state machine, the stack of open
    elements, the list of active formatting elements, foster parenting, and
    the adoption agency algorithm.

    Not intended for direct user construction; prefer parse_html() or
    parse_fragment() from aspose_html.tree.

    Parameters
    ----------
    tokenizer : Tokenizer
        A Tokenizer instance ready to yield tokens.
    document : Document
        The Document node to build into. Must be a freshly created Document
        with no children.
    fragment_context : Element | None
        If set, the builder runs in fragment parsing mode (innerHTML-style).
        The element is used to determine the initial insertion mode.

    Examples
    --------
    >>> from aspose_html.tokenizer import Tokenizer
    >>> from aspose_html.dom import Document
    >>> from aspose_html.tree import TreeBuilder
    >>> tok = Tokenizer('<p>hello</p>')
    >>> doc = Document()
    >>> builder = TreeBuilder(tok, doc, fragment_context=None)
    >>> builder.run()
    >>> doc.document_element.tag_name
    'HTML'
    """

    __slots__ = (
        "_tokenizer",
        "_document",
        "_fragment_context",
        "_mode",
        "_original_mode",
        "_open_elements",
        "_active_formatting",
        "_template_modes",
        "_head_element",
        "_form_element",
        "_frameset_ok",
        "_foster_parenting",
        "_pending_table_chars",
        "_dispatch",
        "_errors",
        "_in_foreign_content",
    )

    def __init__(
        self,
        tokenizer: Tokenizer,
        document: Document,
        fragment_context: Element | None = None,
    ) -> None:
        self._tokenizer: Tokenizer = tokenizer
        self._document: Document = document
        self._fragment_context: Element | None = fragment_context
        self._mode: InsertionMode = InsertionMode.INITIAL
        self._original_mode: InsertionMode = InsertionMode.INITIAL
        self._open_elements: StackOfOpenElements = StackOfOpenElements()
        self._active_formatting: ActiveFormattingList = ActiveFormattingList()
        self._template_modes: TemplateInsertionModeStack = TemplateInsertionModeStack()
        self._head_element: Element | None = None
        self._form_element: Element | None = None
        self._frameset_ok: bool = True
        self._foster_parenting: bool = False
        self._pending_table_chars: list[str] = []
        self._errors: list[ParseError] = []
        self._in_foreign_content: bool = False

        # Build dispatch table
        self._dispatch: dict[InsertionMode, Callable[[AnyToken], None]] = {
            InsertionMode.INITIAL: self._process_initial,
            InsertionMode.BEFORE_HTML: self._process_before_html,
            InsertionMode.BEFORE_HEAD: self._process_before_head,
            InsertionMode.IN_HEAD: self._process_in_head,
            InsertionMode.IN_HEAD_NOSCRIPT: self._process_in_head_noscript,
            InsertionMode.AFTER_HEAD: self._process_after_head,
            InsertionMode.IN_BODY: self._process_in_body,
            InsertionMode.TEXT: self._process_text,
            InsertionMode.IN_TABLE: self._process_in_table,
            InsertionMode.IN_TABLE_TEXT: self._process_in_table_text,
            InsertionMode.IN_CAPTION: self._process_in_caption,
            InsertionMode.IN_COLUMN_GROUP: self._process_in_column_group,
            InsertionMode.IN_TABLE_BODY: self._process_in_table_body,
            InsertionMode.IN_ROW: self._process_in_row,
            InsertionMode.IN_CELL: self._process_in_cell,
            InsertionMode.IN_SELECT: self._process_in_select,
            InsertionMode.IN_SELECT_IN_TABLE: self._process_in_select_in_table,
            InsertionMode.IN_TEMPLATE: self._process_in_template,
            InsertionMode.AFTER_BODY: self._process_after_body,
            InsertionMode.IN_FRAMESET: self._process_in_frameset,
            InsertionMode.AFTER_FRAMESET: self._process_after_frameset,
            InsertionMode.AFTER_AFTER_BODY: self._process_after_after_body,
            InsertionMode.AFTER_AFTER_FRAMESET: self._process_after_after_frameset,
        }

        # Fragment parsing initialization (§13.2.8 steps 5-7, 10)
        if fragment_context is not None:
            # Step 5-6: Create root html element and append to document
            html_el = document.create_element("html")
            document.append_child(html_el)
            # Step 7: Push onto open elements stack
            self._open_elements.push(html_el)
            # Step 10: Reset the insertion mode based on context element
            self._reset_insertion_mode_appropriately()

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run(self) -> None:
        """Execute the tree construction algorithm until EofToken.

        Drives the tokenizer generator, processes each token through
        the current insertion mode, and builds the document in-place.

        Returns
        -------
        None
            The document passed to __init__ is mutated in place.
        """
        gen = self._tokenizer.tokenize()
        for token in gen:
            self._process_token(token)
            if isinstance(token, EofToken):
                break

        # Collect tokenizer errors into the document
        for err in self._tokenizer.errors:
            self._document.parse_errors.append(err)
        # Collect tree builder errors
        self._document.parse_errors.extend(self._errors)

    # -------------------------------------------------------------------------
    # Internal: token dispatch
    # -------------------------------------------------------------------------

    def _process_token(self, token: AnyToken) -> None:
        """Route a token through the current insertion mode handler."""
        # Foreign content check: if current node is in a foreign namespace
        # and token is not EOF, consider foreign content routing.
        # Simplified: just dispatch to current mode.
        handler = self._dispatch.get(self._mode)
        if handler is not None:
            handler(token)

    # -------------------------------------------------------------------------
    # Mode: INITIAL
    # -------------------------------------------------------------------------

    def _process_initial(self, token: AnyToken) -> None:
        """§13.2.6.4.1 — initial insertion mode."""
        match token:
            case CharacterToken():
                # Ignore whitespace
                if token.data.strip():
                    self._add_parse_error("unexpected-char-in-initial-mode", token)
                    self._document.compat_mode = "BackCompat"
                    self._mode = InsertionMode.BEFORE_HTML
                    self._dispatch[self._mode](token)
            case CommentToken():
                self._document.append_child(
                    self._document.create_comment(token.data)
                )
            case DoctypeToken():
                self._process_doctype(token)
            case _:
                # EOF or tags — switch to BEFORE_HTML and reprocess
                if not isinstance(token, EofToken):
                    self._add_parse_error("expected-doctype-but-got-chars", token)
                self._document.compat_mode = "BackCompat"
                self._mode = InsertionMode.BEFORE_HTML
                self._dispatch[self._mode](token)

    def _process_doctype(self, token: DoctypeToken) -> None:
        """Process a DOCTYPE token in INITIAL mode."""
        name = token.name or ""
        pub = token.public_id or ""
        sys = token.system_id or ""
        dt = DocumentType(name, pub, sys, self._document)
        self._document.append_child(dt)
        mode = determine_quirks_mode(token)
        self._document.compat_mode = mode
        self._mode = InsertionMode.BEFORE_HTML

    # -------------------------------------------------------------------------
    # Mode: BEFORE_HTML
    # -------------------------------------------------------------------------

    def _process_before_html(self, token: AnyToken) -> None:
        """§13.2.6.4.2 — before html insertion mode."""
        match token:
            case DoctypeToken():
                # Parse error, ignore
                self._add_parse_error("doctype-in-before-html", token)
            case CommentToken():
                self._document.append_child(
                    self._document.create_comment(token.data)
                )
            case CharacterToken():
                if not token.data.strip():
                    return  # Ignore whitespace
                self._add_parse_error("unexpected-char-before-html", token)
                html_el = self._create_html_element()
                self._document.append_child(html_el)
                self._open_elements.push(html_el)
                self._mode = InsertionMode.BEFORE_HEAD
                self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name == "html":
                html_el = self._create_element_for_token(token, HTML_NAMESPACE)
                self._document.append_child(html_el)
                self._open_elements.push(html_el)
                self._mode = InsertionMode.BEFORE_HEAD
            case EndTagToken() if token.tag_name not in ("head", "body", "html", "br"):
                self._add_parse_error("end-tag-before-html", token)
            case _:
                # Create html element implicitly
                html_el = self._create_html_element()
                self._document.append_child(html_el)
                self._open_elements.push(html_el)
                self._mode = InsertionMode.BEFORE_HEAD
                if not isinstance(token, EofToken):
                    self._dispatch[self._mode](token)

    def _create_html_element(self) -> Element:
        """Create an <html> element owned by self._document."""
        return self._document.create_element("html")

    # -------------------------------------------------------------------------
    # Mode: BEFORE_HEAD
    # -------------------------------------------------------------------------

    def _process_before_head(self, token: AnyToken) -> None:
        """§13.2.6.4.3 — before head insertion mode."""
        match token:
            case CharacterToken():
                if not token.data.strip():
                    return
                # Implicit <head>
                self._insert_implicit_head()
                self._dispatch[self._mode](token)
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-in-before-head", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case StartTagToken() if token.tag_name == "head":
                head = self._insert_element_for_token(token)
                self._head_element = head
                self._mode = InsertionMode.IN_HEAD
            case EndTagToken() if token.tag_name not in ("head", "body", "html", "br"):
                self._add_parse_error("end-tag-before-head", token)
            case _:
                self._insert_implicit_head()
                self._dispatch[self._mode](token)

    def _insert_implicit_head(self) -> None:
        """Insert an implicit <head> element and switch to IN_HEAD."""
        head = self._document.create_element("head")
        self._insert_element(head)
        self._head_element = head
        self._mode = InsertionMode.IN_HEAD

    # -------------------------------------------------------------------------
    # Mode: IN_HEAD
    # -------------------------------------------------------------------------

    def _process_in_head(self, token: AnyToken) -> None:
        """§13.2.6.4.4 — in head insertion mode."""
        match token:
            case CharacterToken():
                if not token.data.strip():
                    self._insert_character(token.data)
                    return
                self._pop_head_and_switch(token)
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-in-head", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case StartTagToken() if token.tag_name in ("base", "basefont", "bgsound", "link"):
                self._insert_element_for_token(token)
                self._open_elements.pop()
            case StartTagToken() if token.tag_name == "meta":
                self._insert_element_for_token(token)
                self._open_elements.pop()
            case StartTagToken() if token.tag_name == "title":
                self._parse_raw_text_or_rcdata(token, TokenizerState.RCDATA)
            case StartTagToken() if token.tag_name in ("noscript",):
                # We don't execute scripts, so treat as IN_HEAD_NOSCRIPT or raw text
                self._insert_element_for_token(token)
                self._mode = InsertionMode.IN_HEAD_NOSCRIPT
            case StartTagToken() if token.tag_name in ("noframes", "style"):
                self._parse_raw_text_or_rcdata(token, TokenizerState.RAWTEXT)
            case StartTagToken() if token.tag_name == "script":
                self._parse_raw_text_or_rcdata(token, TokenizerState.SCRIPT_DATA)
            case StartTagToken() if token.tag_name == "template":
                self._process_template_start(token)
            case StartTagToken() if token.tag_name == "head":
                self._add_parse_error("duplicate-head", token)
            case EndTagToken() if token.tag_name == "head":
                self._open_elements.pop()
                self._mode = InsertionMode.AFTER_HEAD
            case EndTagToken() if token.tag_name == "template":
                self._process_template_end(token)
            case EndTagToken() if token.tag_name not in ("body", "html", "br"):
                self._add_parse_error("end-tag-in-head", token)
            case _:
                self._pop_head_and_switch(token)

    def _pop_head_and_switch(self, token: AnyToken) -> None:
        """Pop <head> and switch to AFTER_HEAD, reprocessing the token."""
        self._open_elements.pop()
        self._mode = InsertionMode.AFTER_HEAD
        self._dispatch[self._mode](token)

    def _parse_raw_text_or_rcdata(
        self, token: StartTagToken, state: TokenizerState
    ) -> None:
        """Generic raw text / RCDATA parsing entry point."""
        el = self._insert_element_for_token(token)
        # ADR-002 protocol: set_state BEFORE next next() call
        self._tokenizer.set_state(state)
        self._original_mode = self._mode
        self._mode = InsertionMode.TEXT

    # -------------------------------------------------------------------------
    # Mode: IN_HEAD_NOSCRIPT
    # -------------------------------------------------------------------------

    def _process_in_head_noscript(self, token: AnyToken) -> None:
        """§13.2.6.4.5 — in head noscript insertion mode."""
        match token:
            case DoctypeToken():
                self._add_parse_error("doctype-in-head-noscript", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case EndTagToken() if token.tag_name == "noscript":
                self._open_elements.pop()
                self._mode = InsertionMode.IN_HEAD
            case CharacterToken():
                if not token.data.strip():
                    self._process_in_head(token)
                    return
                self._add_parse_error("char-in-head-noscript", token)
                self._open_elements.pop()
                self._mode = InsertionMode.IN_HEAD
                self._dispatch[self._mode](token)
            case CommentToken():
                self._process_in_head(token)
            case StartTagToken() if token.tag_name in ("basefont", "bgsound", "link", "meta", "noframes", "style"):
                self._process_in_head(token)
            case StartTagToken() if token.tag_name in ("head", "noscript"):
                self._add_parse_error("bad-tag-in-head-noscript", token)
            case EndTagToken() if token.tag_name not in ("br",):
                self._add_parse_error("end-tag-in-head-noscript", token)
            case _:
                self._add_parse_error("unexpected-in-head-noscript", token)
                self._open_elements.pop()
                self._mode = InsertionMode.IN_HEAD
                self._dispatch[self._mode](token)

    # -------------------------------------------------------------------------
    # Mode: AFTER_HEAD
    # -------------------------------------------------------------------------

    def _process_after_head(self, token: AnyToken) -> None:
        """§13.2.6.4.6 — after head insertion mode."""
        match token:
            case CharacterToken():
                if not token.data.strip():
                    self._insert_character(token.data)
                    return
                self._insert_implicit_body(token)
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-after-head", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case StartTagToken() if token.tag_name == "body":
                self._insert_element_for_token(token)
                self._frameset_ok = False
                self._mode = InsertionMode.IN_BODY
            case StartTagToken() if token.tag_name == "frameset":
                self._insert_element_for_token(token)
                self._mode = InsertionMode.IN_FRAMESET
            case StartTagToken() if token.tag_name in (
                "base", "basefont", "bgsound", "link", "meta",
                "noframes", "script", "style", "template", "title",
            ):
                self._add_parse_error("element-after-head", token)
                # Re-open head and process
                if self._head_element is not None:
                    self._open_elements.push(self._head_element)
                self._process_in_head(token)
                if (self._head_element is not None
                        and self._open_elements.contains_node(self._head_element)):
                    self._open_elements.pop_until_node(self._head_element)
            case EndTagToken() if token.tag_name == "template":
                self._process_in_head(token)
            case EndTagToken() if token.tag_name not in ("body", "html", "br"):
                self._add_parse_error("end-tag-after-head", token)
            case _:
                self._insert_implicit_body(token)

    def _insert_implicit_body(self, token: AnyToken) -> None:
        """Insert an implicit <body> element and switch to IN_BODY."""
        body = self._document.create_element("body")
        self._insert_element(body)
        self._mode = InsertionMode.IN_BODY
        self._dispatch[self._mode](token)

    # -------------------------------------------------------------------------
    # Mode: IN_BODY
    # -------------------------------------------------------------------------

    def _process_in_body(self, token: AnyToken) -> None:  # noqa: C901 (complexity OK — spec is long)
        """§13.2.6.4.7 — in body insertion mode."""
        match token:
            case CharacterToken() if token.data == "\x00":
                self._add_parse_error("null-character-in-body", token)
            case CharacterToken():
                self._active_formatting.reconstruct(self)
                self._insert_character(token.data)
                if token.data.strip():
                    self._frameset_ok = False
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-in-body", token)
            case StartTagToken() if token.tag_name == "html":
                self._add_parse_error("html-start-tag-in-body", token)
                # Merge attributes into the existing html element
                html_el = self._open_elements.bottom
                if html_el is not None:
                    self._merge_attributes(html_el, token)
            case StartTagToken() if token.tag_name in (
                "base", "basefont", "bgsound", "link", "meta",
                "noframes", "script", "style", "template", "title",
            ):
                self._process_in_head(token)
            case EndTagToken() if token.tag_name == "template":
                self._process_in_head(token)
            case StartTagToken() if token.tag_name == "body":
                self._add_parse_error("body-start-tag-in-body", token)
                if len(self._open_elements) < 2:
                    return
                body = self._open_elements._stack[1]
                if body._local_name != "body":
                    return
                self._frameset_ok = False
                self._merge_attributes(body, token)
            case StartTagToken() if token.tag_name == "frameset":
                self._add_parse_error("frameset-in-body", token)
                if not self._frameset_ok:
                    return
                # Remove body from parent
                if len(self._open_elements) >= 2:
                    body = self._open_elements._stack[1]
                    if body._parent is not None:
                        body._parent.remove_child(body)
                while len(self._open_elements) > 1:
                    self._open_elements.pop()
                self._insert_element_for_token(token)
                self._mode = InsertionMode.IN_FRAMESET
            case EofToken():
                if self._template_modes.current is not None:
                    self._process_in_template(token)
                    return
                # Check for open elements that should not be open at EOF
                # (generate parse errors for them, then stop)
            case EndTagToken() if token.tag_name == "body":
                if not self._open_elements.has_in_scope("body"):
                    self._add_parse_error("body-end-tag-without-body", token)
                    return
                self._mode = InsertionMode.AFTER_BODY
            case EndTagToken() if token.tag_name == "html":
                if not self._open_elements.has_in_scope("body"):
                    self._add_parse_error("html-end-without-body", token)
                    return
                self._mode = InsertionMode.AFTER_BODY
                self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name in (
                "address", "article", "aside", "blockquote", "center",
                "details", "dialog", "dir", "div", "dl", "fieldset",
                "figcaption", "figure", "footer", "header", "hgroup",
                "main", "menu", "nav", "ol", "p", "section", "summary", "ul",
            ):
                self._close_p_if_in_button_scope()
                self._insert_element_for_token(token)
            case StartTagToken() if token.tag_name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self._close_p_if_in_button_scope()
                if self._open_elements.current and self._open_elements.current._local_name in (
                    "h1", "h2", "h3", "h4", "h5", "h6"
                ):
                    self._add_parse_error("heading-in-heading", token)
                    self._open_elements.pop()
                self._insert_element_for_token(token)
            case StartTagToken() if token.tag_name in ("pre", "listing"):
                self._close_p_if_in_button_scope()
                self._insert_element_for_token(token)
                self._frameset_ok = False
            case StartTagToken() if token.tag_name == "form":
                self._close_p_if_in_button_scope()
                if self._form_element is not None and "template" not in self._open_elements:
                    self._add_parse_error("nested-form", token)
                    return
                form = self._insert_element_for_token(token)
                if "template" not in self._open_elements:
                    self._form_element = form
            case StartTagToken() if token.tag_name == "li":
                self._process_li_start(token)
            case StartTagToken() if token.tag_name in ("dd", "dt"):
                self._process_dd_dt_start(token)
            case StartTagToken() if token.tag_name == "plaintext":
                self._close_p_if_in_button_scope()
                self._insert_element_for_token(token)
                # ADR-002 protocol: set PLAINTEXT state before next next()
                self._tokenizer.set_state(TokenizerState.PLAINTEXT)
            case StartTagToken() if token.tag_name == "button":
                if self._open_elements.has_in_scope("button"):
                    self._add_parse_error("nested-button", token)
                    self._generate_implied_end_tags()
                    self._open_elements.pop_until("button")
                self._active_formatting.reconstruct(self)
                self._insert_element_for_token(token)
                self._frameset_ok = False
            case EndTagToken() if token.tag_name in (
                "address", "article", "aside", "blockquote", "button",
                "center", "details", "dialog", "dir", "div", "dl",
                "fieldset", "figcaption", "figure", "footer", "header",
                "hgroup", "listing", "main", "menu", "nav", "ol",
                "pre", "section", "summary", "ul",
            ):
                if not self._open_elements.has_in_scope(token.tag_name):
                    self._add_parse_error("end-tag-without-start", token)
                    return
                self._generate_implied_end_tags()
                if self._open_elements.current and self._open_elements.current._local_name != token.tag_name:
                    self._add_parse_error("unexpected-end-tag", token)
                self._open_elements.pop_until(token.tag_name)
            case EndTagToken() if token.tag_name == "form":
                if "template" not in self._open_elements:
                    form_el = self._form_element
                    self._form_element = None
                    if form_el is None or not self._open_elements.has_in_scope("form"):
                        self._add_parse_error("form-end-no-form", token)
                        return
                    self._generate_implied_end_tags()
                    if self._open_elements.current is not form_el:
                        self._add_parse_error("form-end-not-current", token)
                    self._open_elements.pop_until_node(form_el)
                else:
                    if not self._open_elements.has_in_scope("form"):
                        self._add_parse_error("form-end-no-form", token)
                        return
                    self._generate_implied_end_tags()
                    self._open_elements.pop_until("form")
            case EndTagToken() if token.tag_name == "p":
                if not self._open_elements.has_in_button_scope("p"):
                    self._add_parse_error("p-end-without-p", token)
                    self._insert_element_for_tag("p")  # §13.2.6.4.7: create implied <p>
                self._close_p_element()
            case EndTagToken() if token.tag_name == "li":
                if not self._open_elements.has_in_list_item_scope("li"):
                    self._add_parse_error("li-end-without-li", token)
                    return
                self._generate_implied_end_tags(exclude="li")
                self._open_elements.pop_until("li")
            case EndTagToken() if token.tag_name in ("dd", "dt"):
                if not self._open_elements.has_in_scope(token.tag_name):
                    self._add_parse_error("dd-dt-end-without-start", token)
                    return
                self._generate_implied_end_tags(exclude=token.tag_name)
                self._open_elements.pop_until(token.tag_name)
            case EndTagToken() if token.tag_name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                if not any(
                    self._open_elements.has_in_scope(h)
                    for h in ("h1", "h2", "h3", "h4", "h5", "h6")
                ):
                    self._add_parse_error("heading-end-without-start", token)
                    return
                self._generate_implied_end_tags()
                self._open_elements.pop_until("h1", "h2", "h3", "h4", "h5", "h6")
            case StartTagToken() if token.tag_name == "a":
                # Check for <a> in active formatting — if so, run AAA
                existing_a = None
                for entry in reversed(list(self._active_formatting)):
                    if self._active_formatting.is_marker(entry):
                        break
                    if entry._local_name == "a":  # type: ignore[union-attr]
                        existing_a = entry
                        break
                if existing_a is not None:
                    self._add_parse_error("nested-a", token)
                    from aspose_html.tree._adoption_agency import run_adoption_agency_algorithm
                    run_adoption_agency_algorithm(self, token)
                    self._active_formatting.remove(existing_a)
                    if self._open_elements.contains_node(existing_a):
                        self._open_elements.pop_until_node(existing_a)
                self._active_formatting.reconstruct(self)
                el = self._insert_element_for_token(token)
                self._active_formatting.push(el)
            case StartTagToken() if token.tag_name in _FORMATTING_ELEMENTS:
                self._active_formatting.reconstruct(self)
                el = self._insert_element_for_token(token)
                self._active_formatting.push(el)
            case StartTagToken() if token.tag_name == "nobr":
                self._active_formatting.reconstruct(self)
                if self._open_elements.has_in_scope("nobr"):
                    self._add_parse_error("nested-nobr", token)
                    from aspose_html.tree._adoption_agency import run_adoption_agency_algorithm
                    run_adoption_agency_algorithm(self, token)
                    self._active_formatting.reconstruct(self)
                el = self._insert_element_for_token(token)
                self._active_formatting.push(el)
            case EndTagToken() if token.tag_name in _FORMATTING_ELEMENTS | frozenset({"a"}):
                from aspose_html.tree._adoption_agency import run_adoption_agency_algorithm
                run_adoption_agency_algorithm(self, token)
            case StartTagToken() if token.tag_name in ("applet", "marquee", "object"):
                self._active_formatting.reconstruct(self)
                self._insert_element_for_token(token)
                self._active_formatting.push_marker()
                self._frameset_ok = False
            case EndTagToken() if token.tag_name in ("applet", "marquee", "object"):
                if not self._open_elements.has_in_scope(token.tag_name):
                    self._add_parse_error("end-tag-without-start", token)
                    return
                self._generate_implied_end_tags()
                self._open_elements.pop_until(token.tag_name)
                self._active_formatting.clear_to_last_marker()
            case StartTagToken() if token.tag_name == "table":
                if (self._document.compat_mode != "BackCompat"
                        and self._open_elements.has_in_button_scope("p")):
                    self._close_p_element()
                self._insert_element_for_token(token)
                self._frameset_ok = False
                self._mode = InsertionMode.IN_TABLE
            case StartTagToken() if token.tag_name in ("area", "br", "embed", "img", "keygen", "wbr"):
                self._active_formatting.reconstruct(self)
                self._insert_element_for_token(token)
                self._open_elements.pop()
                self._frameset_ok = False
            case StartTagToken() if token.tag_name == "input":
                self._active_formatting.reconstruct(self)
                self._insert_element_for_token(token)
                self._open_elements.pop()
                # Check if it's a hidden input
                ty = None
                for name, val in token.attributes:
                    if name == "type":
                        ty = val
                        break
                if ty is None or ty.lower() != "hidden":
                    self._frameset_ok = False
            case StartTagToken() if token.tag_name in ("param", "source", "track"):
                self._insert_element_for_token(token)
                self._open_elements.pop()
            case StartTagToken() if token.tag_name == "hr":
                self._close_p_if_in_button_scope()
                self._insert_element_for_token(token)
                self._open_elements.pop()
                self._frameset_ok = False
            case StartTagToken() if token.tag_name == "image":
                self._add_parse_error("image-tag", token)
                # Treat as <img>
                from aspose_html.tokenizer._tokens import StartTagToken as ST
                img_token = ST(
                    tag_name="img",
                    self_closing=token.self_closing,
                    attributes=token.attributes,
                    line=token.line,
                    column=token.column,
                )
                self._dispatch[self._mode](img_token)
            case StartTagToken() if token.tag_name == "textarea":
                self._insert_element_for_token(token)
                # ADR-002 protocol: RCDATA before next token
                self._tokenizer.set_state(TokenizerState.RCDATA)
                self._original_mode = self._mode
                self._mode = InsertionMode.TEXT
                self._frameset_ok = False
            case StartTagToken() if token.tag_name == "xmp":
                self._close_p_if_in_button_scope()
                self._active_formatting.reconstruct(self)
                self._frameset_ok = False
                self._parse_raw_text_or_rcdata(token, TokenizerState.RAWTEXT)
            case StartTagToken() if token.tag_name == "iframe":
                self._frameset_ok = False
                self._parse_raw_text_or_rcdata(token, TokenizerState.RAWTEXT)
            case StartTagToken() if token.tag_name == "noembed":
                self._parse_raw_text_or_rcdata(token, TokenizerState.RAWTEXT)
            case StartTagToken() if token.tag_name == "select":
                self._active_formatting.reconstruct(self)
                self._insert_element_for_token(token)
                self._frameset_ok = False
                if self._mode in (
                    InsertionMode.IN_TABLE,
                    InsertionMode.IN_CAPTION,
                    InsertionMode.IN_TABLE_BODY,
                    InsertionMode.IN_ROW,
                    InsertionMode.IN_CELL,
                ):
                    self._mode = InsertionMode.IN_SELECT_IN_TABLE
                else:
                    self._mode = InsertionMode.IN_SELECT
            case StartTagToken() if token.tag_name in ("optgroup", "option"):
                if self._open_elements.current and self._open_elements.current._local_name == "option":
                    self._open_elements.pop()
                self._active_formatting.reconstruct(self)
                self._insert_element_for_token(token)
            case StartTagToken() if token.tag_name in ("rb", "rtc"):
                if self._open_elements.has_in_scope("ruby"):
                    self._generate_implied_end_tags()
                self._insert_element_for_token(token)
            case StartTagToken() if token.tag_name in ("rp", "rt"):
                if self._open_elements.has_in_scope("ruby"):
                    self._generate_implied_end_tags(exclude="rtc")
                    if self._open_elements.current and self._open_elements.current._local_name not in ("rtc", "ruby"):
                        self._add_parse_error("rp-rt-nesting", token)
                self._insert_element_for_token(token)
            case StartTagToken() if token.tag_name == "math":
                self._active_formatting.reconstruct(self)
                self._insert_foreign_element(token, MATHML_NAMESPACE, adjust_mathml_attributes)
            case StartTagToken() if token.tag_name == "svg":
                self._active_formatting.reconstruct(self)
                self._insert_foreign_element(token, SVG_NAMESPACE, adjust_svg_attributes)
            case StartTagToken() if token.tag_name in _VOID_ELEMENTS:
                self._active_formatting.reconstruct(self)
                self._insert_element_for_token(token)
                self._open_elements.pop()
            case StartTagToken() if token.tag_name == "caption":
                self._add_parse_error("caption-in-body", token)
            case StartTagToken() if token.tag_name in ("col", "colgroup", "frame", "head",
                                                        "tbody", "td", "tfoot", "th", "thead", "tr"):
                self._add_parse_error("table-element-in-body", token)
            case StartTagToken():
                self._active_formatting.reconstruct(self)
                self._insert_element_for_token(token)
            case EndTagToken() if token.tag_name == "br":
                self._add_parse_error("br-end-tag", token)
                # Treat as <br>
                from aspose_html.tokenizer._tokens import StartTagToken as ST
                br_token = ST(
                    tag_name="br",
                    self_closing=False,
                    attributes=(),
                    line=token.line,
                    column=token.column,
                )
                self._dispatch[self._mode](br_token)
            case EndTagToken():
                self._any_other_end_tag(token)
            case EofToken():
                pass  # End processing

    # -------------------------------------------------------------------------
    # Mode: TEXT
    # -------------------------------------------------------------------------

    def _process_text(self, token: AnyToken) -> None:
        """§13.2.6.4.8 — text insertion mode."""
        match token:
            case CharacterToken():
                self._insert_character(token.data)
            case EofToken():
                self._add_parse_error("eof-in-text", token)
                self._open_elements.pop()
                self._mode = self._original_mode
                self._dispatch[self._mode](token)
            case EndTagToken():
                self._open_elements.pop()
                self._mode = self._original_mode

    # -------------------------------------------------------------------------
    # Mode: IN_TABLE
    # -------------------------------------------------------------------------

    def _process_in_table(self, token: AnyToken) -> None:
        """§13.2.6.4.9 — in table insertion mode."""
        match token:
            case CharacterToken():
                # Table text — collect for later
                current = self._open_elements.current
                if current and current._local_name in ("table", "tbody", "tfoot", "thead", "tr"):
                    self._pending_table_chars.append(token.data)
                    self._original_mode = self._mode
                    self._mode = InsertionMode.IN_TABLE_TEXT
                else:
                    self._table_foster_character(token)
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-in-table", token)
            case StartTagToken() if token.tag_name == "caption":
                self._clear_stack_to_table_context()
                self._active_formatting.push_marker()
                self._insert_element_for_token(token)
                self._mode = InsertionMode.IN_CAPTION
            case StartTagToken() if token.tag_name == "colgroup":
                self._clear_stack_to_table_context()
                self._insert_element_for_token(token)
                self._mode = InsertionMode.IN_COLUMN_GROUP
            case StartTagToken() if token.tag_name == "col":
                self._clear_stack_to_table_context()
                col_group = self._document.create_element("colgroup")
                self._insert_element(col_group)
                self._mode = InsertionMode.IN_COLUMN_GROUP
                self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name in _TABLE_BODY_ELEMENTS:
                self._clear_stack_to_table_context()
                self._insert_element_for_token(token)
                self._mode = InsertionMode.IN_TABLE_BODY
            case StartTagToken() if token.tag_name in ("td", "th", "tr"):
                self._clear_stack_to_table_context()
                tbody = self._document.create_element("tbody")
                self._insert_element(tbody)
                self._mode = InsertionMode.IN_TABLE_BODY
                self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name == "table":
                self._add_parse_error("nested-table", token)
                if not self._open_elements.has_in_table_scope("table"):
                    return
                self._open_elements.pop_until("table")
                self._reset_insertion_mode_appropriately()
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name == "table":
                if not self._open_elements.has_in_table_scope("table"):
                    self._add_parse_error("table-end-without-table", token)
                    return
                self._open_elements.pop_until("table")
                self._reset_insertion_mode_appropriately()
            case EndTagToken() if token.tag_name in (
                "body", "caption", "col", "colgroup", "html",
                "tbody", "td", "tfoot", "th", "thead", "tr",
            ):
                self._add_parse_error("end-tag-in-table", token)
            case StartTagToken() if token.tag_name in ("style", "script", "template"):
                self._process_in_head(token)
            case EndTagToken() if token.tag_name == "template":
                self._process_in_head(token)
            case StartTagToken() if token.tag_name == "input":
                ty = None
                for name, val in token.attributes:
                    if name == "type":
                        ty = val
                        break
                if ty and ty.lower() == "hidden":
                    self._add_parse_error("hidden-input-in-table", token)
                    el = self._insert_element_for_token(token)
                    self._open_elements.pop()
                else:
                    self._table_foster_character(token)
            case StartTagToken() if token.tag_name == "form":
                self._add_parse_error("form-in-table", token)
                if self._form_element is not None or "template" in self._open_elements:
                    return
                form = self._insert_element_for_token(token)
                self._form_element = form
                self._open_elements.pop()
            case EofToken():
                self._process_in_body(token)
            case _:
                self._add_parse_error("unexpected-in-table", token)
                self._foster_parenting = True
                self._process_in_body(token)
                self._foster_parenting = False

    def _table_foster_character(self, token: AnyToken) -> None:
        """Foster a token through IN_BODY with foster parenting active."""
        self._add_parse_error("foster-parenting", token)
        self._foster_parenting = True
        self._process_in_body(token)
        self._foster_parenting = False

    # -------------------------------------------------------------------------
    # Mode: IN_TABLE_TEXT
    # -------------------------------------------------------------------------

    def _process_in_table_text(self, token: AnyToken) -> None:
        """§13.2.6.4.10 — in table text insertion mode."""
        match token:
            case CharacterToken() if token.data == "\x00":
                # Parse error: drop null characters in table text mode
                self._add_parse_error("null-character-in-table-text", token)
            case CharacterToken():
                self._pending_table_chars.append(token.data)
            case _:
                # Flush pending chars
                text = "".join(self._pending_table_chars)
                self._pending_table_chars = []
                if text.strip():
                    # Foster parent non-whitespace
                    self._foster_parenting = True
                    self._active_formatting.reconstruct(self)
                    self._insert_character(text)
                    self._foster_parenting = False
                elif text:
                    self._insert_character(text)
                self._mode = self._original_mode
                self._dispatch[self._mode](token)

    # -------------------------------------------------------------------------
    # Mode: IN_CAPTION
    # -------------------------------------------------------------------------

    def _process_in_caption(self, token: AnyToken) -> None:
        """§13.2.6.4.11 — in caption insertion mode."""
        match token:
            case EndTagToken() if token.tag_name == "caption":
                if not self._open_elements.has_in_table_scope("caption"):
                    self._add_parse_error("caption-end-without-start", token)
                    return
                self._generate_implied_end_tags()
                self._open_elements.pop_until("caption")
                self._active_formatting.clear_to_last_marker()
                self._mode = InsertionMode.IN_TABLE
            case StartTagToken() if token.tag_name in (
                "table", "caption", "col", "colgroup", "tbody", "td", "tfoot",
                "th", "thead", "tr",
            ):
                if not self._open_elements.has_in_table_scope("caption"):
                    self._add_parse_error("table-tag-before-caption-end", token)
                    return
                self._generate_implied_end_tags()
                self._open_elements.pop_until("caption")
                self._active_formatting.clear_to_last_marker()
                self._mode = InsertionMode.IN_TABLE
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name == "table":
                if not self._open_elements.has_in_table_scope("caption"):
                    self._add_parse_error("table-end-before-caption-end", token)
                    return
                self._generate_implied_end_tags()
                self._open_elements.pop_until("caption")
                self._active_formatting.clear_to_last_marker()
                self._mode = InsertionMode.IN_TABLE
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name in (
                "body", "col", "colgroup", "html", "tbody", "td",
                "tfoot", "th", "thead", "tr",
            ):
                self._add_parse_error("end-tag-in-caption", token)
            case _:
                self._process_in_body(token)

    # -------------------------------------------------------------------------
    # Mode: IN_COLUMN_GROUP
    # -------------------------------------------------------------------------

    def _process_in_column_group(self, token: AnyToken) -> None:
        """§13.2.6.4.12 — in column group insertion mode."""
        match token:
            case CharacterToken():
                if not token.data.strip():
                    self._insert_character(token.data)
                    return
                self._close_colgroup_and_reprocess(token)
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-in-colgroup", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case StartTagToken() if token.tag_name == "col":
                self._insert_element_for_token(token)
                self._open_elements.pop()
            case EndTagToken() if token.tag_name == "colgroup":
                if self._open_elements.current and self._open_elements.current._local_name != "colgroup":
                    self._add_parse_error("colgroup-end-wrong", token)
                    return
                self._open_elements.pop()
                self._mode = InsertionMode.IN_TABLE
            case EndTagToken() if token.tag_name == "col":
                self._add_parse_error("col-end-tag", token)
            case StartTagToken() if token.tag_name == "template":
                self._process_in_head(token)
            case EndTagToken() if token.tag_name == "template":
                self._process_in_head(token)
            case EofToken():
                self._process_in_body(token)
            case _:
                self._close_colgroup_and_reprocess(token)

    def _close_colgroup_and_reprocess(self, token: AnyToken) -> None:
        if self._open_elements.current and self._open_elements.current._local_name != "colgroup":
            self._add_parse_error("implicit-colgroup-end", token)
            return
        self._open_elements.pop()
        self._mode = InsertionMode.IN_TABLE
        self._dispatch[self._mode](token)

    # -------------------------------------------------------------------------
    # Mode: IN_TABLE_BODY
    # -------------------------------------------------------------------------

    def _process_in_table_body(self, token: AnyToken) -> None:
        """§13.2.6.4.13 — in table body insertion mode."""
        match token:
            case StartTagToken() if token.tag_name == "tr":
                self._clear_stack_to_table_body_context()
                self._insert_element_for_token(token)
                self._mode = InsertionMode.IN_ROW
            case StartTagToken() if token.tag_name in ("td", "th"):
                self._add_parse_error("cell-in-table-body", token)
                self._clear_stack_to_table_body_context()
                tr = self._document.create_element("tr")
                self._insert_element(tr)
                self._mode = InsertionMode.IN_ROW
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name in _TABLE_BODY_ELEMENTS:
                if not self._open_elements.has_in_table_scope(token.tag_name):
                    self._add_parse_error("table-body-end-without-start", token)
                    return
                self._clear_stack_to_table_body_context()
                self._open_elements.pop()
                self._mode = InsertionMode.IN_TABLE
            case StartTagToken() if token.tag_name in (
                "caption", "col", "colgroup", "tbody", "tfoot", "thead",
            ):
                # Check if any table body is in scope
                in_scope = any(
                    self._open_elements.has_in_table_scope(t)
                    for t in ("tbody", "thead", "tfoot")
                )
                if not in_scope:
                    self._add_parse_error("table-struct-outside-body", token)
                    return
                self._clear_stack_to_table_body_context()
                self._open_elements.pop()
                self._mode = InsertionMode.IN_TABLE
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name == "table":
                in_scope = any(
                    self._open_elements.has_in_table_scope(t)
                    for t in ("tbody", "thead", "tfoot")
                )
                if not in_scope:
                    self._add_parse_error("table-end-no-tbody", token)
                    return
                self._clear_stack_to_table_body_context()
                self._open_elements.pop()
                self._mode = InsertionMode.IN_TABLE
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name in (
                "body", "caption", "col", "colgroup", "html", "td", "th", "tr",
            ):
                self._add_parse_error("end-tag-in-table-body", token)
            case _:
                self._process_in_table(token)

    # -------------------------------------------------------------------------
    # Mode: IN_ROW
    # -------------------------------------------------------------------------

    def _process_in_row(self, token: AnyToken) -> None:
        """§13.2.6.4.14 — in row insertion mode."""
        match token:
            case StartTagToken() if token.tag_name in ("td", "th"):
                self._clear_stack_to_table_row_context()
                self._insert_element_for_token(token)
                self._active_formatting.push_marker()
                self._mode = InsertionMode.IN_CELL
            case EndTagToken() if token.tag_name == "tr":
                if not self._open_elements.has_in_table_scope("tr"):
                    self._add_parse_error("tr-end-without-tr", token)
                    return
                self._clear_stack_to_table_row_context()
                self._open_elements.pop()  # pop the tr
                self._mode = InsertionMode.IN_TABLE_BODY
            case StartTagToken() if token.tag_name in (
                "caption", "col", "colgroup", "tbody", "tfoot", "thead",
            ):
                if not self._open_elements.has_in_table_scope("tr"):
                    self._add_parse_error("struct-before-tr-end", token)
                    return
                self._clear_stack_to_table_row_context()
                self._open_elements.pop()  # pop the tr
                self._mode = InsertionMode.IN_TABLE_BODY
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name == "table":
                if not self._open_elements.has_in_table_scope("tr"):
                    self._add_parse_error("table-end-before-tr-end", token)
                    return
                self._clear_stack_to_table_row_context()
                self._open_elements.pop()  # pop the tr
                self._mode = InsertionMode.IN_TABLE_BODY
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name in _TABLE_BODY_ELEMENTS:
                if not (
                    self._open_elements.has_in_table_scope(token.tag_name)
                    or self._open_elements.has_in_table_scope("tr")
                ):
                    self._add_parse_error("tbody-end-before-tr-end", token)
                    return
                self._clear_stack_to_table_row_context()
                self._open_elements.pop()  # pop the tr
                self._mode = InsertionMode.IN_TABLE_BODY
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name in (
                "body", "caption", "col", "colgroup", "html", "td", "th",
            ):
                self._add_parse_error("end-tag-in-row", token)
            case _:
                self._process_in_table(token)

    # -------------------------------------------------------------------------
    # Mode: IN_CELL
    # -------------------------------------------------------------------------

    def _process_in_cell(self, token: AnyToken) -> None:
        """§13.2.6.4.15 — in cell insertion mode."""
        match token:
            case EndTagToken() if token.tag_name in ("td", "th"):
                if not self._open_elements.has_in_table_scope(token.tag_name):
                    self._add_parse_error("cell-end-without-start", token)
                    return
                self._generate_implied_end_tags()
                self._open_elements.pop_until(token.tag_name)
                self._active_formatting.clear_to_last_marker()
                self._mode = InsertionMode.IN_ROW
            case StartTagToken() if token.tag_name in (
                "caption", "col", "colgroup", "tbody", "td", "tfoot",
                "th", "thead", "tr",
            ):
                if not (
                    self._open_elements.has_in_table_scope("td")
                    or self._open_elements.has_in_table_scope("th")
                ):
                    self._add_parse_error("struct-before-cell-end", token)
                    return
                self._close_cell(token)
            case EndTagToken() if token.tag_name == "table":
                if not (
                    self._open_elements.has_in_table_scope("td")
                    or self._open_elements.has_in_table_scope("th")
                ):
                    self._add_parse_error("table-end-before-cell-end", token)
                    return
                self._close_cell(token)
            case EndTagToken() if token.tag_name in _TABLE_BODY_ELEMENTS | frozenset({"tr"}):
                if not self._open_elements.has_in_table_scope(token.tag_name):
                    self._add_parse_error("table-struct-end-before-cell-end", token)
                    return
                self._close_cell(token)
            case EndTagToken() if token.tag_name in (
                "body", "caption", "col", "colgroup", "html",
            ):
                self._add_parse_error("end-tag-in-cell", token)
            case _:
                self._process_in_body(token)

    def _close_cell(self, token: AnyToken) -> None:
        """Close the current table cell."""
        if self._open_elements.has_in_table_scope("td"):
            self._generate_implied_end_tags()
            self._open_elements.pop_until("td")
        else:
            self._generate_implied_end_tags()
            self._open_elements.pop_until("th")
        self._active_formatting.clear_to_last_marker()
        self._mode = InsertionMode.IN_ROW
        self._dispatch[self._mode](token)

    # -------------------------------------------------------------------------
    # Mode: IN_SELECT
    # -------------------------------------------------------------------------

    def _process_in_select(self, token: AnyToken) -> None:
        """§13.2.6.4.16 — in select insertion mode."""
        match token:
            case CharacterToken() if token.data == "\x00":
                self._add_parse_error("null-in-select", token)
            case CharacterToken():
                self._insert_character(token.data)
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-in-select", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case StartTagToken() if token.tag_name == "option":
                if self._open_elements.current and self._open_elements.current._local_name == "option":
                    self._open_elements.pop()
                self._insert_element_for_token(token)
            case StartTagToken() if token.tag_name == "optgroup":
                if self._open_elements.current and self._open_elements.current._local_name == "option":
                    self._open_elements.pop()
                if self._open_elements.current and self._open_elements.current._local_name == "optgroup":
                    self._open_elements.pop()
                self._insert_element_for_token(token)
            case EndTagToken() if token.tag_name == "optgroup":
                if (self._open_elements.current
                        and self._open_elements.current._local_name == "option"):
                    prev = None
                    if len(self._open_elements._stack) >= 2:
                        prev = self._open_elements._stack[-2]
                    if prev and prev._local_name == "optgroup":
                        self._open_elements.pop()
                if (self._open_elements.current
                        and self._open_elements.current._local_name == "optgroup"):
                    self._open_elements.pop()
                else:
                    self._add_parse_error("optgroup-end-without-start", token)
            case EndTagToken() if token.tag_name == "option":
                if self._open_elements.current and self._open_elements.current._local_name == "option":
                    self._open_elements.pop()
                else:
                    self._add_parse_error("option-end-without-start", token)
            case EndTagToken() if token.tag_name == "select":
                if not self._open_elements.has_in_select_scope("select"):
                    self._add_parse_error("select-end-no-select", token)
                    return
                self._open_elements.pop_until("select")
                self._reset_insertion_mode_appropriately()
            case StartTagToken() if token.tag_name == "select":
                self._add_parse_error("nested-select", token)
                if not self._open_elements.has_in_select_scope("select"):
                    return
                self._open_elements.pop_until("select")
                self._reset_insertion_mode_appropriately()
            case StartTagToken() if token.tag_name in ("input", "keygen", "textarea"):
                self._add_parse_error("input-in-select", token)
                if not self._open_elements.has_in_select_scope("select"):
                    return
                self._open_elements.pop_until("select")
                self._reset_insertion_mode_appropriately()
                self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name in ("script", "template"):
                self._process_in_head(token)
            case EndTagToken() if token.tag_name == "template":
                self._process_in_head(token)
            case EofToken():
                self._process_in_body(token)
            case _:
                self._add_parse_error("unexpected-in-select", token)

    # -------------------------------------------------------------------------
    # Mode: IN_SELECT_IN_TABLE
    # -------------------------------------------------------------------------

    def _process_in_select_in_table(self, token: AnyToken) -> None:
        """§13.2.6.4.17 — in select in table insertion mode."""
        match token:
            case StartTagToken() if token.tag_name in (
                "caption", "table", "tbody", "tfoot", "thead", "tr", "td", "th",
            ):
                self._add_parse_error("table-element-in-select-in-table", token)
                self._open_elements.pop_until("select")
                self._reset_insertion_mode_appropriately()
                self._dispatch[self._mode](token)
            case EndTagToken() if token.tag_name in (
                "caption", "table", "tbody", "tfoot", "thead", "tr", "td", "th",
            ):
                self._add_parse_error("table-end-in-select-in-table", token)
                if not self._open_elements.has_in_table_scope(token.tag_name):
                    return
                self._open_elements.pop_until("select")
                self._reset_insertion_mode_appropriately()
                self._dispatch[self._mode](token)
            case _:
                self._process_in_select(token)

    # -------------------------------------------------------------------------
    # Mode: IN_TEMPLATE
    # -------------------------------------------------------------------------

    def _process_in_template(self, token: AnyToken) -> None:
        """§13.2.6.4.18 — in template insertion mode."""
        match token:
            case CharacterToken() | CommentToken() | DoctypeToken():
                self._process_in_body(token)
            case StartTagToken() if token.tag_name in (
                "base", "basefont", "bgsound", "link", "meta",
                "noframes", "script", "style", "template", "title",
            ):
                self._process_in_head(token)
            case EndTagToken() if token.tag_name == "template":
                self._process_in_head(token)
            case StartTagToken() if token.tag_name in (
                "caption", "colgroup", "tbody", "tfoot", "thead",
            ):
                self._template_modes.pop()
                self._template_modes.push(InsertionMode.IN_TABLE)
                self._mode = InsertionMode.IN_TABLE
                self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name == "col":
                self._template_modes.pop()
                self._template_modes.push(InsertionMode.IN_COLUMN_GROUP)
                self._mode = InsertionMode.IN_COLUMN_GROUP
                self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name == "tr":
                self._template_modes.pop()
                self._template_modes.push(InsertionMode.IN_TABLE_BODY)
                self._mode = InsertionMode.IN_TABLE_BODY
                self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name in ("td", "th"):
                self._template_modes.pop()
                self._template_modes.push(InsertionMode.IN_ROW)
                self._mode = InsertionMode.IN_ROW
                self._dispatch[self._mode](token)
            case StartTagToken():
                self._template_modes.pop()
                self._template_modes.push(InsertionMode.IN_BODY)
                self._mode = InsertionMode.IN_BODY
                self._dispatch[self._mode](token)
            case EndTagToken():
                self._add_parse_error("unexpected-end-tag-in-template", token)
            case EofToken():
                if "template" not in self._open_elements:
                    # Stop parsing
                    return
                self._add_parse_error("eof-in-template", token)
                self._open_elements.pop_until("template")
                self._active_formatting.clear_to_last_marker()
                self._template_modes.pop()
                self._reset_insertion_mode_appropriately()
                self._dispatch[self._mode](token)

    def _process_template_start(self, token: StartTagToken) -> None:
        """Handle <template> start tag in IN_HEAD mode."""
        el = self._insert_element_for_token(token)
        self._active_formatting.push_marker()
        self._frameset_ok = False
        self._mode = InsertionMode.IN_TEMPLATE
        self._template_modes.push(InsertionMode.IN_TEMPLATE)
        # Create the template's content fragment
        content = self._document.create_document_fragment()
        el._template_content = content

    def _process_template_end(self, token: EndTagToken) -> None:
        """Handle </template> end tag."""
        if "template" not in self._open_elements:
            self._add_parse_error("template-end-without-start", token)
            return
        self._generate_implied_end_tags()
        if self._open_elements.current and self._open_elements.current._local_name != "template":
            self._add_parse_error("template-end-while-open", token)
        self._open_elements.pop_until("template")
        self._active_formatting.clear_to_last_marker()
        self._template_modes.pop()
        self._reset_insertion_mode_appropriately()

    # -------------------------------------------------------------------------
    # Mode: AFTER_BODY
    # -------------------------------------------------------------------------

    def _process_after_body(self, token: AnyToken) -> None:
        """§13.2.6.4.19 — after body insertion mode."""
        match token:
            case CharacterToken():
                if not token.data.strip():
                    self._process_in_body(token)
                    return
                self._add_parse_error("char-after-body", token)
                self._mode = InsertionMode.IN_BODY
                self._dispatch[self._mode](token)
            case CommentToken():
                # Insert comment as child of <html>
                html_el = self._open_elements.bottom
                if html_el is not None:
                    html_el.append_child(self._document.create_comment(token.data))
                else:
                    self._document.append_child(self._document.create_comment(token.data))
            case DoctypeToken():
                self._add_parse_error("doctype-after-body", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case EndTagToken() if token.tag_name == "html":
                if self._fragment_context is not None:
                    self._add_parse_error("html-end-in-fragment", token)
                    return
                self._mode = InsertionMode.AFTER_AFTER_BODY
            case EofToken():
                pass  # Stop parsing
            case _:
                self._add_parse_error("unexpected-after-body", token)
                self._mode = InsertionMode.IN_BODY
                self._dispatch[self._mode](token)

    # -------------------------------------------------------------------------
    # Mode: IN_FRAMESET
    # -------------------------------------------------------------------------

    def _process_in_frameset(self, token: AnyToken) -> None:
        """§13.2.6.4.20 — in frameset insertion mode."""
        match token:
            case CharacterToken():
                if not token.data.strip():
                    self._insert_character(token.data)
                    return
                self._add_parse_error("char-in-frameset", token)
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-in-frameset", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case StartTagToken() if token.tag_name == "frameset":
                self._insert_element_for_token(token)
            case EndTagToken() if token.tag_name == "frameset":
                if self._open_elements.current and self._open_elements.current._local_name == "html":
                    self._add_parse_error("frameset-end-html-only", token)
                    return
                self._open_elements.pop()
                if (self._fragment_context is None
                        and (self._open_elements.current is None
                             or self._open_elements.current._local_name != "frameset")):
                    self._mode = InsertionMode.AFTER_FRAMESET
            case StartTagToken() if token.tag_name == "frame":
                self._insert_element_for_token(token)
                self._open_elements.pop()
            case StartTagToken() if token.tag_name == "noframes":
                self._process_in_head(token)
            case EofToken():
                if self._open_elements.current and self._open_elements.current._local_name != "html":
                    self._add_parse_error("eof-in-frameset", token)
            case _:
                self._add_parse_error("unexpected-in-frameset", token)

    # -------------------------------------------------------------------------
    # Mode: AFTER_FRAMESET
    # -------------------------------------------------------------------------

    def _process_after_frameset(self, token: AnyToken) -> None:
        """§13.2.6.4.21 — after frameset insertion mode."""
        match token:
            case CharacterToken():
                if not token.data.strip():
                    self._insert_character(token.data)
                    return
                self._add_parse_error("char-after-frameset", token)
            case CommentToken():
                self._insert_comment(token)
            case DoctypeToken():
                self._add_parse_error("doctype-after-frameset", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case EndTagToken() if token.tag_name == "html":
                self._mode = InsertionMode.AFTER_AFTER_FRAMESET
            case StartTagToken() if token.tag_name == "noframes":
                self._process_in_head(token)
            case EofToken():
                pass
            case _:
                self._add_parse_error("unexpected-after-frameset", token)

    # -------------------------------------------------------------------------
    # Mode: AFTER_AFTER_BODY
    # -------------------------------------------------------------------------

    def _process_after_after_body(self, token: AnyToken) -> None:
        """§13.2.6.4.22 — after after body insertion mode."""
        match token:
            case CommentToken():
                self._document.append_child(
                    self._document.create_comment(token.data)
                )
            case DoctypeToken():
                self._add_parse_error("doctype-after-after-body", token)
                self._mode = InsertionMode.IN_BODY
                self._dispatch[self._mode](token)
            case CharacterToken():
                if not token.data.strip():
                    self._process_in_body(token)
                else:
                    self._add_parse_error("char-after-after-body", token)
                    self._mode = InsertionMode.IN_BODY
                    self._dispatch[self._mode](token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case EofToken():
                pass
            case _:
                self._add_parse_error("unexpected-after-after-body", token)
                self._mode = InsertionMode.IN_BODY
                self._dispatch[self._mode](token)

    # -------------------------------------------------------------------------
    # Mode: AFTER_AFTER_FRAMESET
    # -------------------------------------------------------------------------

    def _process_after_after_frameset(self, token: AnyToken) -> None:
        """§13.2.6.4.23 — after after frameset insertion mode."""
        match token:
            case CommentToken():
                self._document.append_child(
                    self._document.create_comment(token.data)
                )
            case DoctypeToken():
                self._process_in_body(token)
            case CharacterToken():
                if not token.data.strip():
                    self._process_in_body(token)
                    return
                self._add_parse_error("char-after-after-frameset", token)
            case StartTagToken() if token.tag_name == "html":
                self._process_in_body(token)
            case StartTagToken() if token.tag_name == "noframes":
                self._process_in_head(token)
            case EofToken():
                pass
            case _:
                self._add_parse_error("unexpected-after-after-frameset", token)

    # -------------------------------------------------------------------------
    # Insertion helpers
    # -------------------------------------------------------------------------

    def _get_adjusted_insertion_location(
        self,
        override_target: Element | None = None,
    ) -> tuple[object, object]:
        """Return (parent, before_node) for the next insertion.

        When foster parenting is active, delegates to get_foster_parent_location.
        Otherwise returns (current_node, None) — append to current.
        """
        if self._foster_parenting:
            # §13.2.6.1 — foster parenting
            return get_foster_parent_location(self._open_elements, self._document)

        target = override_target or self._open_elements.current

        # §13.2.6.1 — if target is a template, insert into its content fragment
        if target is not None and target._local_name == "template":
            content = getattr(target, "_template_content", None)
            if content is not None:
                return content, None

        return target or self._document, None

    def _insert_element(self, element: Element) -> Element:
        """Insert element at the adjusted insertion location and push onto stack."""
        parent, before = self._get_adjusted_insertion_location()
        if before is not None:
            parent.insert_before(element, before)
        else:
            parent.append_child(element)
        self._open_elements.push(element)
        return element

    def _insert_element_for_token(self, token: StartTagToken) -> Element:
        """Create and insert an element for a start tag token."""
        el = self._create_element_for_token(token, HTML_NAMESPACE)
        return self._insert_element(el)

    def _insert_element_for_tag(self, tag_name: str) -> Element:
        """Create and insert an element for a plain tag name."""
        el = self._document.create_element(tag_name)
        return self._insert_element(el)

    def _insert_foreign_element(
        self,
        token: StartTagToken,
        namespace_uri: str,
        attr_adjuster: object = None,
    ) -> Element:
        """Create and insert a foreign-namespace element."""
        # INV-005: use factory method, never the Element constructor directly
        # See ADR-003 §INV-005 satisfaction clause
        local_name = token.tag_name
        el = self._document.create_element_ns(namespace_uri, local_name)  # ADR-023
        # Apply attribute adjustments
        attrs = token.attributes
        if attr_adjuster is not None:
            adjusted_attrs = attr_adjuster(attrs)
        else:
            adjusted_attrs = list(attrs)
        for name, value in adjusted_attrs:
            el.set_attribute(name, value)
        return self._insert_element(el)

    def _create_element_for_token(
        self, token: StartTagToken, namespace_uri: str
    ) -> Element:
        """Create an Element for a StartTagToken without inserting it."""
        el = self._document.create_element(token.tag_name)
        # Apply attributes (deduplication: first occurrence wins)
        seen: set[str] = set()
        for name, value in token.attributes:
            if name not in seen:
                el.set_attribute(name, value)
                seen.add(name)
        return el

    def _clone_element(self, element: Element) -> Element:
        """Create a shallow clone of element (same tag, same attributes, no children)."""
        clone = self._document.create_element(element._local_name)
        for attr in element._attributes:
            clone.set_attribute(attr.name, attr.value)  # type: ignore[union-attr]
        return clone

    def _insert_character(self, data: str) -> None:
        """Insert character data at the current insertion location.

        If the previous sibling is a Text node, append to it (merge).
        Otherwise create a new Text node.
        """
        parent, before = self._get_adjusted_insertion_location()
        # Find where to insert in parent's children
        if before is not None:
            children = parent._children
            idx = children.index(before)
            if idx > 0:
                prev = children[idx - 1]
                if prev._node_type == NodeType.TEXT_NODE:
                    prev._data += data  # type: ignore[union-attr]
                    return
            # Insert a new text node before 'before'
            text_node = self._document.create_text_node(data)
            parent.insert_before(text_node, before)
        else:
            children = parent._children
            if children and children[-1]._node_type == NodeType.TEXT_NODE:
                children[-1]._data += data  # type: ignore[union-attr]
                return
            text_node = self._document.create_text_node(data)
            parent.append_child(text_node)

    def _insert_comment(self, token: CommentToken) -> None:
        """Insert a comment node at the adjusted insertion location."""
        comment = self._document.create_comment(token.data)
        parent, before = self._get_adjusted_insertion_location()
        if before is not None:
            parent.insert_before(comment, before)
        else:
            parent.append_child(comment)

    # -------------------------------------------------------------------------
    # Open elements helpers
    # -------------------------------------------------------------------------

    def _generate_implied_end_tags(self, exclude: str | None = None) -> None:
        """Pop elements that have implied end tags."""
        while self._open_elements._stack:
            top = self._open_elements.current
            if top is None:
                break
            if top._local_name == exclude:
                break
            if top._local_name in _IMPLIED_END_TAGS:
                self._open_elements.pop()
            else:
                break

    def _close_p_if_in_button_scope(self) -> None:
        """Close a <p> element if one is in button scope."""
        if self._open_elements.has_in_button_scope("p"):
            self._close_p_element()

    def _close_p_element(self) -> None:
        """Close the current <p> element."""
        self._generate_implied_end_tags(exclude="p")
        if self._open_elements.current and self._open_elements.current._local_name != "p":
            self._add_parse_error("implicit-close-p", None)
        self._open_elements.pop_until("p")

    def _process_li_start(self, token: StartTagToken) -> None:
        """Process <li> start tag — §13.2.6.4.7."""
        self._frameset_ok = False
        for el in reversed(self._open_elements._stack):
            if el._local_name == "li":
                self._generate_implied_end_tags(exclude="li")
                self._open_elements.pop_until("li")
                break
            if (el._local_name not in _IMPLIED_END_TAGS
                    and el._local_name in _SPECIAL_ELEMENTS_FOR_LI):
                break
        self._close_p_if_in_button_scope()
        self._insert_element_for_token(token)

    def _process_dd_dt_start(self, token: StartTagToken) -> None:
        """Process <dd>/<dt> start tag."""
        self._frameset_ok = False
        for el in reversed(self._open_elements._stack):
            if el._local_name in ("dd", "dt"):
                self._generate_implied_end_tags(exclude=el._local_name)
                self._open_elements.pop_until(el._local_name)
                break
            if (el._local_name not in _IMPLIED_END_TAGS
                    and el._local_name in _SPECIAL_ELEMENTS_FOR_LI):
                break
        self._close_p_if_in_button_scope()
        self._insert_element_for_token(token)

    def _any_other_end_tag(self, token: EndTagToken) -> None:
        """Handle end tags not matched by specific rules."""
        for i in range(len(self._open_elements._stack) - 1, -1, -1):
            node = self._open_elements._stack[i]
            if node._local_name == token.tag_name:
                self._generate_implied_end_tags(exclude=token.tag_name)
                if self._open_elements.current and self._open_elements.current is not node:
                    self._add_parse_error("unexpected-end-tag", token)
                self._open_elements.pop_until_node(node)
                return
            # If we hit a special element, stop
            from aspose_html.tree._adoption_agency import _SPECIAL_ELEMENTS
            if node._local_name in _SPECIAL_ELEMENTS:
                self._add_parse_error("end-tag-without-start-in-body", token)
                return

    def _merge_attributes(self, element: Element, token: StartTagToken) -> None:
        """Add attributes from token to element if not already present."""
        for name, value in token.attributes:
            if not element.has_attribute(name):
                element.set_attribute(name, value)

    # -------------------------------------------------------------------------
    # Stack clearing helpers — §13.2.6.3
    # -------------------------------------------------------------------------

    _TABLE_CONTEXT_ELEMENTS: frozenset[str] = frozenset({
        "table", "template", "html",
    })
    _TABLE_BODY_CONTEXT_ELEMENTS: frozenset[str] = frozenset({
        "tbody", "tfoot", "thead", "template", "html",
    })
    _TABLE_ROW_CONTEXT_ELEMENTS: frozenset[str] = frozenset({
        "tr", "template", "html",
    })

    def _clear_stack_to_table_context(self) -> None:
        """Pop elements until the current node is table, template, or html."""
        while self._open_elements._stack:
            top = self._open_elements.current
            if top is None:
                break
            if top._local_name in self._TABLE_CONTEXT_ELEMENTS:
                break
            self._open_elements.pop()

    def _clear_stack_to_table_body_context(self) -> None:
        """Pop elements until the current node is tbody, tfoot, thead, template, or html."""
        while self._open_elements._stack:
            top = self._open_elements.current
            if top is None:
                break
            if top._local_name in self._TABLE_BODY_CONTEXT_ELEMENTS:
                break
            self._open_elements.pop()

    def _clear_stack_to_table_row_context(self) -> None:
        """Pop elements until the current node is tr, template, or html."""
        while self._open_elements._stack:
            top = self._open_elements.current
            if top is None:
                break
            if top._local_name in self._TABLE_ROW_CONTEXT_ELEMENTS:
                break
            self._open_elements.pop()

    # -------------------------------------------------------------------------
    # Insertion mode reset
    # -------------------------------------------------------------------------

    def _reset_insertion_mode_appropriately(self) -> None:
        """§13.2.4.1 — reset the insertion mode appropriately."""
        last = False
        node_list = list(self._open_elements._stack)
        for node in reversed(node_list):
            if node is node_list[0]:
                last = True
                if self._fragment_context is not None:
                    node = self._fragment_context  # type: ignore[assignment]
            tag = node._local_name
            if tag == "select":
                for ancestor in reversed(node_list[:node_list.index(node)]):
                    if ancestor._local_name == "template":
                        self._mode = InsertionMode.IN_SELECT
                        return
                    if ancestor._local_name == "table":
                        self._mode = InsertionMode.IN_SELECT_IN_TABLE
                        return
                self._mode = InsertionMode.IN_SELECT
                return
            if tag in ("td", "th") and not last:
                self._mode = InsertionMode.IN_CELL
                return
            if tag == "tr":
                self._mode = InsertionMode.IN_ROW
                return
            if tag in ("tbody", "thead", "tfoot"):
                self._mode = InsertionMode.IN_TABLE_BODY
                return
            if tag == "caption":
                self._mode = InsertionMode.IN_CAPTION
                return
            if tag == "colgroup":
                self._mode = InsertionMode.IN_COLUMN_GROUP
                return
            if tag == "table":
                self._mode = InsertionMode.IN_TABLE
                return
            if tag == "template":
                mode = self._template_modes.current
                if mode is not None:
                    self._mode = mode
                return
            if tag == "head" and not last:
                self._mode = InsertionMode.IN_HEAD
                return
            if tag == "body":
                self._mode = InsertionMode.IN_BODY
                return
            if tag == "frameset":
                self._mode = InsertionMode.IN_FRAMESET
                return
            if tag == "html":
                if self._head_element is None:
                    self._mode = InsertionMode.BEFORE_HEAD
                else:
                    self._mode = InsertionMode.AFTER_HEAD
                return
        self._mode = InsertionMode.IN_BODY

    # -------------------------------------------------------------------------
    # Error helpers
    # -------------------------------------------------------------------------

    def _add_parse_error(
        self,
        code: str,
        token: AnyToken | None,
        message: str = "",
    ) -> None:
        """Record a tree-construction parse error."""
        line = getattr(token, "line", 0) if token is not None else 0
        col = getattr(token, "column", 0) if token is not None else 0
        err = ParseError(code=code, line=line, column=col, message=message or code)
        self._errors.append(err)


# Special elements set for <li>/<dd>/<dt> processing (excludes table-related)
_SPECIAL_ELEMENTS_FOR_LI: frozenset[str] = frozenset({
    "address", "div", "p",
    "applet", "area", "article", "aside", "base", "basefont",
    "bgsound", "blockquote", "body", "br", "button", "caption", "center",
    "col", "colgroup", "dd", "details", "dir",
    "dl", "dt", "embed", "fieldset", "figcaption", "figure",
    "footer", "form", "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6",
    "head", "header", "hgroup", "hr", "html", "iframe", "img", "input",
    "isindex", "link", "listing", "main", "marquee", "menu",
    "meta", "nav", "noembed", "noframes", "noscript", "object", "ol",
    "param", "plaintext", "pre", "script", "section", "select",
    "source", "style", "summary", "table", "tbody", "td", "template",
    "textarea", "tfoot", "th", "thead", "title", "tr", "track", "ul",
    "wbr", "xmp",
})
