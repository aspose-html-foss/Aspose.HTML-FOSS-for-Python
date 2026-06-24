"""Minimal stylesheet parser for CSSOM baseline."""
from __future__ import annotations

import re

from aspose_html.css._parser import parse as parse_selector

from ._declarations import CSSDeclarationBlock
from ._rules import (
    CSSCounterStyleRule,
    CSSFontFaceRule,
    CSSImportRule,
    CSSKeyframeRule,
    CSSKeyframesRule,
    CSSLayerBlockRule,
    CSSLayerStatementRule,
    CSSMediaRule,
    CSSNamespaceRule,
    CSSPageRule,
    CSSPropertyRule,
    CSSRule,
    CSSStyleRule,
    CSSSupportsRule,
)

# At-rule keywords that are known to this parser and handled in parse_stylesheet.
# Unknown at-rules are silently skipped per CSSOM error-recovery rules.
_KNOWN_AT_RULES = frozenset(
    {
        "@media",
        "@keyframes",
        "@-webkit-keyframes",
        "@font-face",
        "@supports",
        "@charset",
        "@import",
        "@layer",
        "@namespace",
        "@counter-style",
        "@page",
        "@property",
    }
)

# Pattern: @import "url" optional_media ;
_IMPORT_QUOTED_RE = re.compile(
    r"""@import\s+(?:"([^"]+)"|'([^']+)'|url\(\s*(?:"([^"]+)"|'([^']+)'|([^)\s]+))\s*\))"""
    r"""\s*([^;]*?)\s*;""",
    re.IGNORECASE,
)

# Pattern: @keyframes <name>  (with optional vendor prefix)
_KEYFRAMES_NAME_RE = re.compile(
    r"@(?:-webkit-)?keyframes\s+(.+)$", re.IGNORECASE
)

# Pattern: @supports <condition>
_SUPPORTS_CONDITION_RE = re.compile(
    r"@supports\s+(.+)$", re.IGNORECASE
)

# Pattern: @layer <name>  (empty name allowed for anonymous layers)
_LAYER_BLOCK_NAME_RE = re.compile(
    r"@layer\s*(.*?)$", re.IGNORECASE
)


def _skip_ws(text: str, pos: int) -> int:
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos


def _read_block(text: str, block_start: int) -> tuple[str, int]:
    depth = 0
    i = block_start
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[block_start + 1 : i], i + 1
        i += 1
    raise SyntaxError("Invalid CSS rule syntax: unmatched braces")


def _validate_selector(selector_text: str) -> None:
    try:
        parse_selector(selector_text, forgiving=False)
    except SyntaxError as exc:
        raise SyntaxError(f"Invalid selector in style rule: {selector_text}") from exc


def _parse_keyframes_rule(header: str, body: str) -> CSSKeyframesRule:
    """Parse a ``@keyframes`` header and block body into a :class:`CSSKeyframesRule`.

    Parameters
    ----------
    header:
        The text before ``{``, e.g. ``"@keyframes slide"``.
    body:
        The text inside the braces.

    Returns
    -------
    CSSKeyframesRule
    """
    m = _KEYFRAMES_NAME_RE.match(header)
    if m is None:
        raise SyntaxError(f"Invalid @keyframes header: {header!r}")
    name = m.group(1).strip()
    rule = CSSKeyframesRule(name)

    # Parse keyframe blocks inside the body.
    # Each block is: <key_text> { <declarations> }
    pos = 0
    text = body
    while True:
        pos = _skip_ws(text, pos)
        if pos >= len(text):
            break
        brace_index = text.find("{", pos)
        if brace_index == -1:
            break
        key_text = text[pos:brace_index].strip()
        if not key_text:
            raise SyntaxError("Invalid @keyframes body: missing keyframe selector")
        decl_body, end_pos = _read_block(text, brace_index)
        style = CSSDeclarationBlock.parse(decl_body)
        frame = CSSKeyframeRule(key_text, style)
        frame.parent_rule = rule
        rule._frames.append(frame)
        pos = end_pos
    return rule


def _parse_font_face_rule(body: str) -> CSSFontFaceRule:
    """Parse a ``@font-face`` block body into a :class:`CSSFontFaceRule`.

    Parameters
    ----------
    body:
        The text inside the ``@font-face { ... }`` braces.

    Returns
    -------
    CSSFontFaceRule
    """
    return CSSFontFaceRule(CSSDeclarationBlock.parse(body))


def _parse_supports_rule(
    header: str, body: str, allow_media: bool
) -> CSSSupportsRule:
    """Parse a ``@supports`` header and block body into a :class:`CSSSupportsRule`.

    Parameters
    ----------
    header:
        The text before ``{``, e.g. ``"@supports (display: grid)"``.
    body:
        The text inside the braces (treated as a nested stylesheet).
    allow_media:
        Propagated to the nested stylesheet parser.

    Returns
    -------
    CSSSupportsRule
    """
    m = _SUPPORTS_CONDITION_RE.match(header)
    if m is None:
        raise SyntaxError(f"Invalid @supports header: {header!r}")
    condition_text = m.group(1).strip()
    rule = CSSSupportsRule(condition_text)
    children = parse_stylesheet(body, allow_media=allow_media)
    for child in children:
        child.parent_rule = rule
        rule._rules.append(child)
    return rule


def _parse_layer_block_rule(
    header: str, body: str, allow_media: bool
) -> CSSLayerBlockRule:
    """Parse a ``@layer`` block-form header and body into a :class:`CSSLayerBlockRule`.

    Parameters
    ----------
    header:
        The text before ``{``, e.g. ``"@layer base"`` or ``"@layer"``.
    body:
        The text inside the braces (treated as a nested stylesheet).
    allow_media:
        Propagated to the nested stylesheet parser.

    Returns
    -------
    CSSLayerBlockRule
    """
    m = _LAYER_BLOCK_NAME_RE.match(header)
    name = m.group(1).strip() if m else ""
    rule = CSSLayerBlockRule(name)
    children = parse_stylesheet(body, allow_media=allow_media)
    for child in children:
        child.parent_rule = rule
        rule._rules.append(child)
    return rule


def _parse_layer_statement_rule(
    text: str, pos: int
) -> tuple[CSSLayerStatementRule | None, int]:
    """Parse a ``@layer`` statement-form rule starting at *pos*.

    The statement ends at the first ``;``.  Returns ``(None, new_pos)`` if
    the statement cannot be parsed (empty name list after stripping).

    Parameters
    ----------
    text:
        Full stylesheet text.
    pos:
        Position of the ``@layer`` keyword.

    Returns
    -------
    tuple[CSSLayerStatementRule | None, int]
        The parsed rule (or ``None`` on unparseable input) and the position
        immediately after the terminating ``;``.
    """
    semi = text.find(";", pos)
    if semi == -1:
        return None, len(text)
    statement = text[pos:semi]
    # Strip "@layer" prefix
    body = re.sub(r"^@layer\s*", "", statement, flags=re.IGNORECASE).strip()
    if not body:
        return None, semi + 1
    name_list = [n.strip() for n in body.split(",") if n.strip()]
    if not name_list:
        return None, semi + 1
    return CSSLayerStatementRule(name_list), semi + 1


_NAMESPACE_URI_RE = re.compile(
    r'(?:url\((["\']?)([^)]+)\1\)|"([^"]+)"|\'([^\']+)\')\s*$'
)


def _parse_namespace_rule(stmt: str) -> "CSSNamespaceRule | None":
    """Parse a statement-form ``@namespace`` declaration.

    Handles the two forms:

    - ``@namespace "uri";``               → prefix=None
    - ``@namespace prefix "uri";``        → prefix=prefix-token

    Returns ``None`` if the statement cannot be parsed.

    Parameters
    ----------
    stmt:
        The text of the rule including the ``@namespace`` token, *without*
        the trailing ``;``.

    Returns
    -------
    CSSNamespaceRule | None
    """
    body = stmt[len("@namespace"):].strip()
    if not body:
        return None
    m = _NAMESPACE_URI_RE.search(body)
    if not m:
        return None
    # url(...) form: group(2) holds the URI; quoted forms: group(3) or group(4)
    uri = m.group(2) or m.group(3) or m.group(4) or ""
    if not uri:
        return None
    prefix_part = body[:m.start()].strip() or None
    return CSSNamespaceRule(uri, prefix_part if prefix_part else None)


def _parse_counter_style_rule(header: str, body: str) -> CSSCounterStyleRule:
    """Parse a block-form ``@counter-style`` rule.

    Parameters
    ----------
    header:
        The text before ``{``, e.g. ``"@counter-style thumbs"``.
    body:
        The text inside the ``{ ... }`` block.

    Returns
    -------
    CSSCounterStyleRule
    """
    name_part = header[len("@counter-style"):].strip()
    name = name_part or "anonymous"
    return CSSCounterStyleRule(name, body.strip())


def _parse_page_rule(header: str, body: str) -> CSSPageRule:
    """Parse an ``@page`` header and block body into a :class:`CSSPageRule`.

    Parameters
    ----------
    header:
        The text before ``{``, e.g. ``"@page"`` or ``"@page :first"``.
    body:
        The text inside the ``{ ... }`` block (page declarations).

    Returns
    -------
    CSSPageRule

    Examples
    --------
    >>> rule = _parse_page_rule("@page", "margin: 1cm")
    >>> rule.selector_text
    ''
    >>> rule.style.get_property_value("margin")
    '1cm'
    >>> _parse_page_rule("@page :first", "margin-top: 2cm").selector_text
    ':first'
    """
    selector_text = header[len("@page"):].strip()
    style = CSSDeclarationBlock.parse(body)
    return CSSPageRule(selector_text, style)


def _parse_property_rule(header: str, body: str) -> CSSPropertyRule:
    """Parse an ``@property`` header and block body into a :class:`CSSPropertyRule`.

    Parameters
    ----------
    header:
        The text before ``{``, e.g. ``"@property --color"``.
    body:
        The text inside the ``{ ... }`` block (descriptor declarations).

    Returns
    -------
    CSSPropertyRule

    Examples
    --------
    >>> rule = _parse_property_rule(
    ...     "@property --color",
    ...     'syntax: "<color>"; inherits: false; initial-value: red',
    ... )
    >>> rule.name
    '--color'
    >>> rule.inherits
    'false'
    >>> rule.initial_value
    'red'
    """
    name = header[len("@property"):].strip()
    descriptors: dict[str, str] = {}
    for part in body.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            key, _, val = part.partition(":")
            descriptors[key.strip().lower()] = val.strip()
    syntax = descriptors.get("syntax", "")
    inherits = descriptors.get("inherits", "")
    initial_value = descriptors.get("initial-value", "")
    return CSSPropertyRule(name, syntax, inherits, initial_value)


def _parse_import_statement(
    text: str, pos: int
) -> tuple[CSSImportRule | None, int]:
    """Parse an ``@import`` statement starting at *pos*.

    The import statement ends at the first ``;`` found.  If the URL cannot
    be extracted the function returns ``(None, new_pos)`` and the caller
    skips the statement.

    Parameters
    ----------
    text:
        Full stylesheet text.
    pos:
        Position of the ``@import`` keyword.

    Returns
    -------
    tuple[CSSImportRule | None, int]
        The parsed rule (or ``None`` on unparseable input) and the position
        immediately after the terminating ``;``.
    """
    semi = text.find(";", pos)
    if semi == -1:
        # No semicolon — try to parse the rest of the line/text as an import.
        statement = text[pos:].rstrip() + ";"
        new_pos = len(text)
    else:
        statement = text[pos : semi + 1]
        new_pos = semi + 1

    m = _IMPORT_QUOTED_RE.match(statement)
    if m is None:
        return None, new_pos

    # Groups 1-5 are the URL from different syntaxes; group 6 is optional media
    href = m.group(1) or m.group(2) or m.group(3) or m.group(4) or m.group(5) or ""
    media = (m.group(6) or "").strip()
    if not href:
        return None, new_pos
    return CSSImportRule(href, media), new_pos


def parse_rule_text(rule_text: str, *, allow_media: bool) -> CSSRule:
    """Parse a single CSS rule string into a rule object.

    This function is used by :meth:`CSSStyleSheet.insert_rule` and
    :class:`CSSMediaRule`.  It only accepts ``@media`` and style rules;
    other at-rules raise :exc:`SyntaxError` so that ``insert_rule`` callers
    receive a clear error (CSSOM §6.4).

    Parameters
    ----------
    rule_text:
        A complete CSS rule string.
    allow_media:
        Whether ``@media`` rules are accepted.

    Returns
    -------
    CSSRule

    Raises
    ------
    SyntaxError
        For invalid or unsupported rule syntax.

    Examples
    --------
    >>> rule = parse_rule_text("p { color: red }", allow_media=False)
    >>> rule.css_text
    'p { color: red }'
    >>> parse_rule_text("@media screen { p { color: red } }", allow_media=True).type
    4
    """
    text = rule_text.strip()
    brace_index = text.find("{")
    if brace_index <= 0:
        raise SyntaxError("Invalid CSS rule syntax: missing '{'")
    header = text[:brace_index].strip()
    body, end_pos = _read_block(text, brace_index)
    if text[end_pos:].strip():
        raise SyntaxError("Invalid CSS rule syntax: trailing tokens")

    if header.startswith("@"):
        lheader = header.lower()
        if not lheader.startswith("@media"):
            raise SyntaxError(f"Unsupported at-rule: {header}")
        if not allow_media:
            raise SyntaxError("Invalid CSS rule syntax: nested at-rule not supported")
        media_text = header[6:].strip()
        media_rule = CSSMediaRule(media_text)
        children = parse_stylesheet(body, allow_media=False)
        for child in children:
            if isinstance(child, CSSMediaRule):
                raise SyntaxError(
                    "Invalid CSS rule syntax: nested at-rule not supported"
                )
            child.parent_rule = media_rule
            media_rule._rules.append(child)
        return media_rule

    _validate_selector(header)
    return CSSStyleRule(header, CSSDeclarationBlock.parse(body))


def parse_stylesheet(css_text: str, *, allow_media: bool = True) -> list[CSSRule]:
    """Parse stylesheet text into a list of CSSOM rule objects.

    Unknown at-rules (``@charset``, vendor-prefixed, etc.) are silently
    skipped per CSSOM error-recovery rules.  Known at-rule types
    (``@media``, ``@keyframes``, ``@font-face``, ``@supports``,
    ``@import``, ``@layer``, ``@namespace``, ``@counter-style``) are
    parsed into typed rule objects.

    Parameters
    ----------
    css_text:
        Full CSS stylesheet text.
    allow_media:
        Whether ``@media`` rules are accepted (``False`` for nested contexts).

    Returns
    -------
    list[CSSRule]

    Examples
    --------
    >>> rules = parse_stylesheet("p { color: red } div { margin: 0 }")
    >>> len(rules)
    2
    >>> rules[0].css_text
    'p { color: red }'
    """
    rules: list[CSSRule] = []
    pos = 0
    text = css_text
    while True:
        pos = _skip_ws(text, pos)
        if pos >= len(text):
            break

        # Peek at the current token to detect statement at-rules (no block)
        rest = text[pos:]
        rest_lower = rest.lstrip().lower()

        if rest_lower.startswith("@import"):
            rule, pos = _parse_import_statement(text, pos)
            if rule is not None:
                rules.append(rule)
            continue

        if rest_lower.startswith("@charset"):
            semi = text.find(";", pos)
            if semi == -1:
                break
            pos = semi + 1
            continue

        # @namespace — statement at-rule: @namespace [prefix] "uri" ;
        if rest_lower.startswith("@namespace"):
            semi = text.find(";", pos)
            if semi == -1:
                break
            stmt = text[pos:semi].strip()
            rule = _parse_namespace_rule(stmt)
            if rule is not None:
                rules.append(rule)
            pos = semi + 1
            continue

        # @layer — can be statement form (ends in ';') or block form (has '{')
        if rest_lower.startswith("@layer"):
            # Determine which form: find the earlier of ';' and '{'
            semi_pos = text.find(";", pos)
            brace_pos = text.find("{", pos)
            if semi_pos != -1 and (brace_pos == -1 or semi_pos < brace_pos):
                # Statement form
                rule, pos = _parse_layer_statement_rule(text, pos)
                if rule is not None:
                    rules.append(rule)
                continue
            # Fall through to block-form processing below

        # All remaining rules require a block — find the opening brace.
        brace_index = text.find("{", pos)
        if brace_index == -1:
            # No more blocks; ignore trailing text
            break

        header = text[pos:brace_index].strip()

        # Check for unknown at-rules before reading the block body.
        if header.startswith("@"):
            lh = header.lower()
            if not any(lh.startswith(kw) for kw in _KNOWN_AT_RULES):
                # Unknown at-rule — could be a statement rule ending in ';' that
                # was embedded in the header text (e.g. '@namespace url(...); p').
                # Check whether a ';' appears before the '{' we found.
                semi_before_brace = text.find(";", pos, brace_index)
                if semi_before_brace != -1:
                    # Statement-style unknown at-rule: skip up to ';'.
                    pos = semi_before_brace + 1
                else:
                    # Block-style unknown at-rule: skip the block.
                    _, end_pos = _read_block(text, brace_index)
                    pos = end_pos
                continue

            # Read the block body for the known at-rule.
            body, end_pos = _read_block(text, brace_index)

            if lh.startswith("@media"):
                # Existing CSSMediaRule path
                snippet = text[pos:end_pos]
                rule_obj = parse_rule_text(snippet, allow_media=allow_media)
                rules.append(rule_obj)
            elif lh.startswith("@keyframes") or lh.startswith(
                "@-webkit-keyframes"
            ):
                rule_obj = _parse_keyframes_rule(header, body)
                rules.append(rule_obj)
            elif lh.startswith("@font-face"):
                rule_obj = _parse_font_face_rule(body)
                rules.append(rule_obj)
            elif lh.startswith("@supports"):
                rule_obj = _parse_supports_rule(header, body, allow_media)
                rules.append(rule_obj)
            elif lh.startswith("@layer"):
                rule_obj = _parse_layer_block_rule(header, body, allow_media)
                rules.append(rule_obj)
            elif lh.startswith("@counter-style"):
                rule_obj = _parse_counter_style_rule(header, body)
                rules.append(rule_obj)
            elif lh.startswith("@page"):
                rule_obj = _parse_page_rule(header, body)
                rules.append(rule_obj)
            elif lh.startswith("@property"):
                rule_obj = _parse_property_rule(header, body)
                rules.append(rule_obj)
            # @charset with block is unusual; skip it (already handled above
            # for the statement form)
            pos = end_pos
            continue

        # Regular style rule
        body, end_pos = _read_block(text, brace_index)
        snippet = text[pos:end_pos]
        rule_obj = parse_rule_text(snippet, allow_media=allow_media)
        rules.append(rule_obj)
        pos = end_pos
    return rules
