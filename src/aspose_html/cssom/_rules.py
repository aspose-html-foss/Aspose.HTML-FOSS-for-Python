"""CSSOM rule objects for stylesheet inspection (BACK-81, BACK-164)."""
from __future__ import annotations

from urllib.parse import urlsplit
from typing import TYPE_CHECKING, Callable, Iterator

from aspose_html.dom import IndexSizeError
from aspose_html.url import URL, URLParseError

from ._declarations import CSSDeclarationBlock

if TYPE_CHECKING:
    from ._stylesheet import CSSStyleSheet


class CSSRule:
    """Base class for CSSOM rules.

    Examples
    --------
    >>> rule = CSSStyleRule("p", CSSDeclarationBlock.parse("color: red"))
    >>> rule.type == CSSRule.STYLE_RULE
    True
    >>> CSSRule.IMPORT_RULE
    3
    >>> CSSRule.SUPPORTS_RULE
    12
    >>> CSSRule.UNKNOWN_RULE
    0
    >>> CSSRule.LAYER_BLOCK_RULE
    17
    >>> CSSRule.COUNTER_STYLE_RULE
    11
    """

    # Rule type constants — CSSOM §5.4 Table 1
    UNKNOWN_RULE: int = 0        # ADD — CSSOM §5.4
    STYLE_RULE: int = 1
    CHARSET_RULE: int = 2       # Obsolete but IDL-specified
    IMPORT_RULE: int = 3
    MEDIA_RULE: int = 4
    FONT_FACE_RULE: int = 5
    PAGE_RULE: int = 6
    KEYFRAMES_RULE: int = 7
    KEYFRAME_RULE: int = 8
    NAMESPACE_RULE: int = 10
    COUNTER_STYLE_RULE: int = 11  # CSSOM §5.4; corrected from 20
    SUPPORTS_RULE: int = 12
    FONT_FEATURE_VALUES_RULE: int = 14  # ADD — CSSOM §5.4 Track 91
    LAYER_BLOCK_RULE: int = 17   # ADD — CSS Cascade 5 / CSSOM-Extensions §2.1
    LAYER_STATEMENT_RULE: int = 1001  # ADD — CSS Cascade 5 / CSSOM-Extensions §2.1 Track 91

    __slots__ = ("parent_style_sheet", "parent_rule")

    def __init__(self) -> None:
        self.parent_style_sheet: CSSStyleSheet | None = None
        self.parent_rule: CSSRule | None = None

    @property
    def type(self) -> int:
        raise NotImplementedError

    @property
    def css_text(self) -> str:
        raise NotImplementedError


class CSSRuleList:
    """Ordered, live CSS rule collection.

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text("p { color: red }")
    >>> rules = sheet.css_rules
    >>> rules.length
    1
    >>> rules.item(0).css_text
    'p { color: red }'
    """

    __slots__ = ("_provider",)

    def __init__(self, provider: Callable[[], list[CSSRule]]) -> None:
        self._provider = provider

    @property
    def length(self) -> int:
        """Number of rules in the live collection."""
        return len(self._provider())

    def item(self, index: int) -> "CSSRule | None":
        """Return the rule at *index*, or ``None`` if out of range (CSSOM §6.5).

        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("div { color: red; }")
        >>> rl = sheet.css_rules
        >>> rl.item(0).selector_text
        'div'
        >>> rl.item(99) is None
        True
        """
        rules = self._provider()
        if 0 <= index < len(rules):
            return rules[index]
        return None

    def __len__(self) -> int:
        return len(self._provider())

    def __iter__(self) -> Iterator[CSSRule]:
        return iter(tuple(self._provider()))

    def __getitem__(self, index: int) -> CSSRule:
        return self._provider()[index]


class CSSStyleRule(CSSRule):
    """Style rule (``selector { declarations }``).

    Examples
    --------
    >>> rule = CSSStyleRule("div.foo", CSSDeclarationBlock.parse("color: red"))
    >>> rule.css_text
    'div.foo { color: red }'
    >>> rule.selector_text
    'div.foo'
    """

    __slots__ = ("_selector_text", "style")

    def __init__(self, selector_text: str, style: CSSDeclarationBlock) -> None:
        super().__init__()
        self._selector_text = selector_text
        self.style = style
        self.style._parent_rule = self

    @property
    def selector_text(self) -> str:
        """The serialized selector string for this rule (CSSOM §6.6).

        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("div.foo { color: red; }")
        >>> sheet.css_rules[0].selector_text
        'div.foo'
        """
        return self._selector_text

    @property
    def type(self) -> int:
        return CSSRule.STYLE_RULE

    @property
    def css_text(self) -> str:
        return f"{self.selector_text} {{ {self.style.css_text} }}"


class CSSMediaRule(CSSRule):
    """Media rule scaffold for nested style rules.

    Examples
    --------
    >>> media = CSSMediaRule("screen")
    >>> media.insert_rule("p { color: red }")
    0
    >>> media.css_text
    '@media screen { p { color: red } }'
    """

    __slots__ = ("media_text", "_rules", "css_rules")

    def __init__(self, media_text: str) -> None:
        super().__init__()
        self.media_text = media_text
        self._rules: list[CSSRule] = []
        self.css_rules = CSSRuleList(lambda: self._rules)

    @property
    def type(self) -> int:
        return CSSRule.MEDIA_RULE

    @property
    def condition_text(self) -> str:
        """The media condition as a string (CSSOM §6.8.1 alias for ``media_text``).

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@media (max-width: 600px) { p { color: red } }')
        >>> sheet.css_rules[0].condition_text
        '(max-width: 600px)'
        """
        return self.media_text

    @property
    def css_text(self) -> str:
        inner = " ".join(rule.css_text for rule in self._rules)
        return f"@media {self.media_text} {{ {inner} }}"

    def insert_rule(self, rule_text: str, index: int | None = None) -> int:
        """Insert a nested style rule and return its index."""
        from ._parser import parse_rule_text  # local import to avoid cycle

        rule = parse_rule_text(rule_text, allow_media=False)
        if not isinstance(rule, CSSStyleRule):
            raise SyntaxError("Invalid CSS rule syntax: expected style rule")
        insert_index = len(self._rules) if index is None else index
        if insert_index < 0 or insert_index > len(self._rules):
            raise IndexSizeError("rule index out of range")
        rule.parent_rule = self
        rule.parent_style_sheet = self.parent_style_sheet
        self._rules.insert(insert_index, rule)
        return insert_index

    def delete_rule(self, index: int) -> None:
        """Delete a nested rule at *index*."""
        if index < 0 or index >= len(self._rules):
            raise IndexSizeError("rule index out of range")
        del self._rules[index]


class CSSKeyframesRule(CSSRule):
    """A ``@keyframes`` rule containing animation keyframe descriptors (CSSOM Animations §7).

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text(
    ...     "@keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
    ... )
    >>> rule = sheet.css_rules[0]
    >>> isinstance(rule, CSSKeyframesRule)
    True
    >>> rule.name
    'slide'
    >>> rule.type == CSSRule.KEYFRAMES_RULE
    True
    >>> rule.css_rules.length
    2
    """

    __slots__ = ("name", "_frames", "css_rules")

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name: str = name
        self._frames: list[CSSKeyframeRule] = []
        self.css_rules: CSSRuleList = CSSRuleList(lambda: self._frames)  # type: ignore[assignment]

    @property
    def type(self) -> int:
        """Rule type constant — always :attr:`CSSRule.KEYFRAMES_RULE` (7)."""
        return CSSRule.KEYFRAMES_RULE

    @property
    def css_text(self) -> str:
        """Serialise the rule to CSS text.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text(
        ...     "@keyframes fade { from { opacity: 0 } to { opacity: 1 } }"
        ... )
        >>> "@keyframes fade" in sheet.css_rules[0].css_text
        True
        """
        inner = " ".join(frame.css_text for frame in self._frames)
        return f"@keyframes {self.name} {{ {inner} }}"

    def append_rule(self, rule_text: str) -> None:
        """Parse *rule_text* as a single keyframe and append it to this rule (CSSOM §6.6).

        If *rule_text* cannot be parsed as a valid keyframe declaration, the call
        is silently ignored (forgiving parser policy).

        Parameters
        ----------
        rule_text:
            A complete keyframe snippet, e.g. ``"from { opacity: 0 }"``.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@keyframes s { from { opacity: 0 } }')
        >>> kr = sheet.css_rules[0]
        >>> kr.append_rule('to { opacity: 1 }')
        >>> len(kr.css_rules)
        2
        """
        from ._parser import parse_stylesheet  # local import to avoid cycle

        wrapper = f"@keyframes __append__ {{ {rule_text} }}"
        parsed = parse_stylesheet(wrapper)
        if not parsed or not isinstance(parsed[0], CSSKeyframesRule):
            return
        new_frames: list[CSSKeyframeRule] = parsed[0]._frames
        if not new_frames:
            return
        frame = new_frames[0]
        frame.parent_rule = self
        frame.parent_style_sheet = self.parent_style_sheet
        self._frames.append(frame)

    def find_rule(self, key_text: str) -> "CSSKeyframeRule | None":
        """Return the last keyframe whose ``key_text`` matches *key_text*, or ``None`` (CSSOM §6.6).

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@keyframes s { from { opacity: 0 } to { opacity: 1 } }')
        >>> kr = sheet.css_rules[0]
        >>> kr.find_rule('from').key_text
        'from'
        >>> kr.find_rule('missing') is None
        True
        """
        result: CSSKeyframeRule | None = None
        for kf in self._frames:
            if kf.key_text == key_text:
                result = kf
        return result

    def delete_rule(self, key_text: str) -> None:
        """Remove the last keyframe whose ``key_text`` matches *key_text* (CSSOM §6.6).

        If no matching keyframe is found, the call is silently ignored.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@keyframes s { from { opacity: 0 } }')
        >>> kr = sheet.css_rules[0]
        >>> kr.delete_rule('from')
        >>> len(kr.css_rules)
        0
        >>> kr.delete_rule('missing')  # no-op
        """
        for i in range(len(self._frames) - 1, -1, -1):
            if self._frames[i].key_text == key_text:
                del self._frames[i]
                break


class CSSKeyframeRule(CSSRule):
    """A single keyframe descriptor within a ``@keyframes`` rule (CSSOM Animations §7).

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text(
    ...     "@keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
    ... )
    >>> frame = sheet.css_rules[0].css_rules[0]
    >>> isinstance(frame, CSSKeyframeRule)
    True
    >>> frame.key_text
    'from'
    >>> frame.type == CSSRule.KEYFRAME_RULE
    True
    """

    __slots__ = ("key_text", "style")

    def __init__(self, key_text: str, style: CSSDeclarationBlock) -> None:
        super().__init__()
        self.key_text: str = key_text
        self.style: CSSDeclarationBlock = style

    @property
    def type(self) -> int:
        """Rule type constant — always :attr:`CSSRule.KEYFRAME_RULE` (8)."""
        return CSSRule.KEYFRAME_RULE

    @property
    def css_text(self) -> str:
        """Serialise this keyframe descriptor to CSS text.

        Examples
        --------
        >>> from aspose_html.cssom._declarations import CSSDeclarationBlock
        >>> frame = CSSKeyframeRule("from", CSSDeclarationBlock.parse("opacity: 0"))
        >>> frame.css_text
        'from { opacity: 0 }'
        """
        return f"{self.key_text} {{ {self.style.css_text} }}"


class CSSFontFaceRule(CSSRule):
    """A ``@font-face`` rule holding font descriptor declarations (CSS Fonts §4.4).

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text(
    ...     "@font-face { font-family: MyFont; src: url(f.woff2); }"
    ... )
    >>> rule = sheet.css_rules[0]
    >>> isinstance(rule, CSSFontFaceRule)
    True
    >>> rule.type == CSSRule.FONT_FACE_RULE
    True
    >>> rule.style.get_property_value("font-family")
    'MyFont'
    """

    __slots__ = ("style",)

    def __init__(self, style: CSSDeclarationBlock) -> None:
        super().__init__()
        self.style: CSSDeclarationBlock = style

    @property
    def type(self) -> int:
        """Rule type constant — always :attr:`CSSRule.FONT_FACE_RULE` (5)."""
        return CSSRule.FONT_FACE_RULE

    @property
    def css_text(self) -> str:
        """Serialise the rule to CSS text.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text(
        ...     "@font-face { font-family: MyFont; src: url(f.woff2); }"
        ... )
        >>> "@font-face" in sheet.css_rules[0].css_text
        True
        """
        return f"@font-face {{ {self.style.css_text} }}"


class CSSSupportsRule(CSSRule):
    """A ``@supports`` rule with a condition and nested style rules (CSS Conditional Rules §2).

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text(
    ...     "@supports (display: grid) { div { color: red } }"
    ... )
    >>> rule = sheet.css_rules[0]
    >>> isinstance(rule, CSSSupportsRule)
    True
    >>> rule.condition_text
    '(display: grid)'
    >>> rule.type == CSSRule.SUPPORTS_RULE
    True
    >>> rule.css_rules.length
    1
    """

    __slots__ = ("condition_text", "_rules", "css_rules")

    def __init__(self, condition_text: str) -> None:
        super().__init__()
        self.condition_text: str = condition_text
        self._rules: list[CSSRule] = []
        self.css_rules: CSSRuleList = CSSRuleList(lambda: self._rules)

    @property
    def type(self) -> int:
        """Rule type constant — always :attr:`CSSRule.SUPPORTS_RULE` (12)."""
        return CSSRule.SUPPORTS_RULE

    @property
    def css_text(self) -> str:
        """Serialise the rule to CSS text.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text(
        ...     "@supports (display: grid) { div { color: red } }"
        ... )
        >>> "@supports (display: grid)" in sheet.css_rules[0].css_text
        True
        """
        inner = " ".join(rule.css_text for rule in self._rules)
        return f"@supports {self.condition_text} {{ {inner} }}"

    def insert_rule(self, rule_text: str, index: int = 0) -> int:
        """Insert a CSS rule into the nested rule list (CSSOM §6.7).

        Parameters
        ----------
        rule_text:
            The full text of the rule to parse and insert.
        index:
            Position at which to insert the rule (default ``0``).

        Returns
        -------
        int
            The index at which the rule was inserted.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@supports (display: flex) { p { color: red } }')
        >>> sr = sheet.css_rules[0]
        >>> sr.insert_rule('div { margin: 0 }', 0)
        0
        >>> len(sr.css_rules)
        2
        """
        from ._parser import parse_rule_text  # local import to avoid cycle

        rule = parse_rule_text(rule_text, allow_media=False)
        if not isinstance(rule, CSSStyleRule):
            raise SyntaxError("Invalid CSS rule syntax: expected style rule")
        if index < 0 or index > len(self._rules):
            raise IndexSizeError("rule index out of range")
        rule.parent_rule = self
        rule.parent_style_sheet = self.parent_style_sheet
        self._rules.insert(index, rule)
        return index

    def delete_rule(self, index: int) -> None:
        """Remove the rule at *index* from the nested rule list (CSSOM §6.7).

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@supports (display: flex) { p { color: red } }')
        >>> sr = sheet.css_rules[0]
        >>> sr.delete_rule(0)
        >>> len(sr.css_rules)
        0
        """
        if index < 0 or index >= len(self._rules):
            raise IndexSizeError("rule index out of range")
        del self._rules[index]


class CSSImportRule(CSSRule):
    """An ``@import`` statement rule (CSSOM §6.7).

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text('@import "reset.css"')
    >>> rule = sheet.css_rules[0]
    >>> isinstance(rule, CSSImportRule)
    True
    >>> rule.href
    'reset.css'
    >>> rule.media
    ''
    >>> rule.type == CSSRule.IMPORT_RULE
    True
    """

    __slots__ = ("href", "media")

    def __init__(self, href: str, media: str = "") -> None:
        super().__init__()
        self.href: str = href
        self.media: str = media

    @property
    def type(self) -> int:
        """Rule type constant — always :attr:`CSSRule.IMPORT_RULE` (3)."""
        return CSSRule.IMPORT_RULE

    @property
    def resolved_href(self) -> str:
        """Resolve :attr:`href` against the parent stylesheet base URL.

        Returns
        -------
        str
            - Absolute ``href`` values are returned unchanged.
            - Relative ``href`` values resolve against ``parent_style_sheet._base_url``
              when that base is present and parseable.
            - If base context is missing/invalid or parsing fails, the raw
              :attr:`href` value is returned unchanged.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@import "styles/reset.css"', href='https://example.com/assets/site.css')
        >>> sheet.css_rules[0].resolved_href
        'https://example.com/assets/styles/reset.css'
        >>> sheet2 = CSSStyleSheet.from_text('@import "styles/reset.css"')
        >>> sheet2.css_rules[0].resolved_href
        'styles/reset.css'
        """
        if urlsplit(self.href).scheme:
            return self.href

        sheet = self.parent_style_sheet
        base_url = getattr(sheet, "_base_url", None) if sheet is not None else None
        if not base_url or not URL.can_parse(base_url):
            return self.href

        try:
            return URL(self.href, base=base_url).href
        except URLParseError:
            return self.href

    @property
    def css_text(self) -> str:
        """Serialise the rule to CSS text.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@import "reset.css"')
        >>> sheet.css_rules[0].css_text
        '@import "reset.css"'
        >>> sheet2 = CSSStyleSheet.from_text('@import "reset.css" screen')
        >>> sheet2.css_rules[0].css_text
        '@import "reset.css" screen'
        """
        if self.media:
            return f'@import "{self.href}" {self.media}'
        return f'@import "{self.href}"'


class CSSLayerBlockRule(CSSRule):
    """A CSS ``@layer`` block rule assigning child rules to a named cascade layer.

    The rule maps directly to the CSSOM Cascading and Layering draft
    ``CSSLayerBlockRule`` interface.  Full layer-order-aware priority is
    deferred to a future track; child rules participate in cascade using
    source order (CSS Cascade 5 §6.4 semantics are not yet implemented).

    Examples
    --------
    >>> from aspose_html.cssom import CSSLayerBlockRule
    >>> rule = CSSLayerBlockRule("base")
    >>> rule.name
    'base'
    >>> rule.type == CSSLayerBlockRule.LAYER_BLOCK_RULE
    True
    >>> rule.css_text
    '@layer base {  }'
    """

    LAYER_BLOCK_RULE: int = 1000

    __slots__ = ("name", "_rules", "css_rules")

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name: str = name
        self._rules: list[CSSRule] = []
        self.css_rules: CSSRuleList = CSSRuleList(lambda: self._rules)

    @property
    def type(self) -> int:
        """Return the CSSOM rule type constant (``LAYER_BLOCK_RULE = 1000``).

        Examples
        --------
        >>> from aspose_html.cssom import CSSLayerBlockRule
        >>> rule = CSSLayerBlockRule("theme")
        >>> rule.type
        1000
        """
        return CSSLayerBlockRule.LAYER_BLOCK_RULE

    @property
    def css_text(self) -> str:
        """Serialise the rule to CSS text.

        Examples
        --------
        >>> from aspose_html.cssom._parser import parse_stylesheet
        >>> rules = parse_stylesheet("@layer base { p { color: red } }")
        >>> rules[0].css_text
        '@layer base { p { color: red } }'
        """
        inner = " ".join(r.css_text for r in self._rules)
        name_part = f" {self.name}" if self.name else ""
        return f"@layer{name_part} {{ {inner} }}"

    def insert_rule(self, rule_text: str, index: int = 0) -> int:
        """Insert a CSS rule into the nested rule list (CSSOM §6.7).

        Parameters
        ----------
        rule_text:
            The full text of the rule to parse and insert.
        index:
            Position at which to insert the rule (default ``0``).

        Returns
        -------
        int
            The index at which the rule was inserted.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@layer utilities { p { color: red } }')
        >>> lr = sheet.css_rules[0]
        >>> lr.insert_rule('div { margin: 0 }', 0)
        0
        >>> len(lr.css_rules)
        2
        """
        from ._parser import parse_rule_text  # local import to avoid cycle

        rule = parse_rule_text(rule_text, allow_media=False)
        if not isinstance(rule, CSSStyleRule):
            raise SyntaxError("Invalid CSS rule syntax: expected style rule")
        if index < 0 or index > len(self._rules):
            raise IndexSizeError("rule index out of range")
        rule.parent_rule = self
        rule.parent_style_sheet = self.parent_style_sheet
        self._rules.insert(index, rule)
        return index

    def delete_rule(self, index: int) -> None:
        """Remove the rule at *index* from the nested rule list (CSSOM §6.7).

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text('@layer utilities { p { color: red } }')
        >>> lr = sheet.css_rules[0]
        >>> lr.delete_rule(0)
        >>> len(lr.css_rules)
        0
        """
        if index < 0 or index >= len(self._rules):
            raise IndexSizeError("rule index out of range")
        del self._rules[index]


class CSSLayerStatementRule(CSSRule):
    """A CSS ``@layer`` statement rule declaring cascade layer order.

    The rule maps directly to the CSSOM Cascading and Layering draft
    ``CSSLayerStatementRule`` interface.  A statement rule ends with ``;``
    and contains only a comma-separated list of layer names — no block body.

    Examples
    --------
    >>> from aspose_html.cssom import CSSLayerStatementRule
    >>> rule = CSSLayerStatementRule(["base", "layout", "utilities"])
    >>> rule.name_list
    ['base', 'layout', 'utilities']
    >>> rule.type == CSSLayerStatementRule.LAYER_STATEMENT_RULE
    True
    >>> rule.css_text
    '@layer base, layout, utilities;'
    """

    LAYER_STATEMENT_RULE: int = 1001

    __slots__ = ("name_list",)

    def __init__(self, name_list: list[str]) -> None:
        super().__init__()
        self.name_list: list[str] = list(name_list)

    @property
    def type(self) -> int:
        """Return the CSSOM rule type constant (``LAYER_STATEMENT_RULE = 1001``).

        Examples
        --------
        >>> from aspose_html.cssom import CSSLayerStatementRule
        >>> rule = CSSLayerStatementRule(["reset", "base"])
        >>> rule.type
        1001
        """
        return CSSLayerStatementRule.LAYER_STATEMENT_RULE

    @property
    def css_text(self) -> str:
        """Serialise the rule to CSS text.

        Examples
        --------
        >>> from aspose_html.cssom._parser import parse_stylesheet
        >>> rules = parse_stylesheet("@layer base, layout;")
        >>> rules[0].css_text
        '@layer base, layout;'
        """
        return f"@layer {', '.join(self.name_list)};"


class CSSNamespaceRule(CSSRule):
    """A ``@namespace`` rule (CSSOM §6.6, type 10).

    Records a namespace URI and optional prefix for use in namespace-qualified
    selectors.  This implementation is an object-model stub — it does not affect
    cascade or selector matching.

    Examples
    --------
    >>> from aspose_html.cssom._stylesheet import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text(
    ...     '@namespace "http://www.w3.org/1999/xhtml";'
    ... )
    >>> rule = sheet.css_rules[0]
    >>> isinstance(rule, CSSNamespaceRule)
    True
    >>> rule.namespace_uri
    'http://www.w3.org/1999/xhtml'
    >>> rule.prefix is None
    True
    >>> rule.css_type
    10
    """

    __slots__ = ("_namespace_uri", "_prefix")

    def __init__(self, namespace_uri: str, prefix: str | None = None) -> None:
        super().__init__()
        self._namespace_uri = namespace_uri
        self._prefix = prefix

    @property
    def css_type(self) -> int:
        """Rule type constant — always :attr:`CSSRule.NAMESPACE_RULE` (10).

        >>> from aspose_html.cssom._rules import CSSNamespaceRule
        >>> CSSNamespaceRule("http://www.w3.org/2000/svg", "svg").css_type
        10
        """
        return CSSRule.NAMESPACE_RULE

    @property
    def type(self) -> int:
        """Legacy alias for :attr:`css_type` (CSSOM §6.6 ``type`` property)."""
        return self.css_type

    @property
    def namespace_uri(self) -> str:
        """The namespace URI string.

        >>> from aspose_html.cssom._rules import CSSNamespaceRule
        >>> CSSNamespaceRule("http://www.w3.org/2000/svg").namespace_uri
        'http://www.w3.org/2000/svg'
        """
        return self._namespace_uri

    @property
    def prefix(self) -> str | None:
        """The namespace prefix, or ``None`` for a default namespace declaration.

        >>> from aspose_html.cssom._rules import CSSNamespaceRule
        >>> CSSNamespaceRule("http://www.w3.org/2000/svg", "svg").prefix
        'svg'
        >>> CSSNamespaceRule("http://www.w3.org/2000/svg").prefix is None
        True
        """
        return self._prefix

    @property
    def css_text(self) -> str:
        """Reconstructed ``@namespace`` declaration string.

        >>> from aspose_html.cssom._rules import CSSNamespaceRule
        >>> CSSNamespaceRule("http://www.w3.org/1999/xhtml").css_text
        '@namespace "http://www.w3.org/1999/xhtml";'
        >>> CSSNamespaceRule("http://www.w3.org/2000/svg", "svg").css_text
        '@namespace svg "http://www.w3.org/2000/svg";'
        """
        if self._prefix:
            return f'@namespace {self._prefix} "{self._namespace_uri}";'
        return f'@namespace "{self._namespace_uri}";'


class CSSPageRule(CSSRule):
    """CSS ``@page`` rule (CSSOM §6.4).

    Represents a ``@page`` at-rule, which specifies styles for printed pages.
    The rule holds an optional page selector string (e.g. ``:first``, ``:left``,
    a named page like ``cover``) and a declaration block for page-margin and
    page-break properties.

    Examples
    --------
    >>> from aspose_html.cssom._declarations import CSSDeclarationBlock
    >>> from aspose_html.cssom._rules import CSSPageRule
    >>> rule = CSSPageRule("", CSSDeclarationBlock.parse("margin: 1cm"))
    >>> rule.type
    6
    >>> rule.selector_text
    ''
    >>> rule.style.get_property_value("margin")
    '1cm'
    >>> rule.css_text
    '@page { margin: 1cm }'
    """

    PAGE_RULE: int = 6

    __slots__ = ("_selector_text", "_style")

    def __init__(self, selector_text: str, style: "CSSDeclarationBlock") -> None:
        super().__init__()
        self._selector_text: str = selector_text
        self._style: CSSDeclarationBlock = style

    @property
    def type(self) -> int:
        """Return PAGE_RULE (6).

        Examples
        --------
        >>> from aspose_html.cssom._declarations import CSSDeclarationBlock
        >>> from aspose_html.cssom._rules import CSSPageRule
        >>> rule = CSSPageRule("", CSSDeclarationBlock.parse("margin: 1cm"))
        >>> rule.type
        6
        """
        return CSSRule.PAGE_RULE

    @property
    def selector_text(self) -> str:
        """The page selector string (``''`` for bare ``@page``).

        Examples
        --------
        >>> from aspose_html.cssom._declarations import CSSDeclarationBlock
        >>> from aspose_html.cssom._rules import CSSPageRule
        >>> rule = CSSPageRule(":first", CSSDeclarationBlock.parse("margin: 2cm"))
        >>> rule.selector_text
        ':first'
        """
        return self._selector_text

    @property
    def style(self) -> "CSSDeclarationBlock":
        """The declaration block for the ``@page`` rule.

        Examples
        --------
        >>> from aspose_html.cssom._declarations import CSSDeclarationBlock
        >>> from aspose_html.cssom._rules import CSSPageRule
        >>> rule = CSSPageRule("", CSSDeclarationBlock.parse("margin: 1cm"))
        >>> rule.style.get_property_value("margin")
        '1cm'
        """
        return self._style

    @property
    def css_text(self) -> str:
        """Reconstructed ``@page`` rule text.

        Examples
        --------
        >>> from aspose_html.cssom._declarations import CSSDeclarationBlock
        >>> from aspose_html.cssom._rules import CSSPageRule
        >>> rule = CSSPageRule("", CSSDeclarationBlock.parse("margin: 1cm"))
        >>> rule.css_text
        '@page { margin: 1cm }'
        >>> CSSPageRule(":first", CSSDeclarationBlock.parse("margin: 2cm")).css_text
        '@page :first { margin: 2cm }'
        """
        if self._selector_text:
            return f"@page {self._selector_text} {{ {self._style.css_text} }}"
        return f"@page {{ {self._style.css_text} }}"


class CSSPropertyRule(CSSRule):
    """CSS ``@property`` rule stub (CSS Properties and Values API §3).

    Represents a ``@property`` at-rule declaring a custom CSS property with a
    type syntax, inheritance behaviour, and initial value. This implementation
    is a headless structural stub: the rule appears in ``css_rules`` so that
    stylesheet enumeration tools can discover it, but no runtime registration
    or typed-CSSOM integration is performed.

    Examples
    --------
    >>> from aspose_html.cssom import CSSPropertyRule
    >>> rule = CSSPropertyRule("--color", '"<color>"', "false", "red")
    >>> rule.type
    16
    >>> rule.name
    '--color'
    >>> rule.syntax
    '"<color>"'
    >>> rule.inherits
    'false'
    >>> rule.initial_value
    'red'
    >>> '@property --color' in rule.css_text
    True
    """

    PROPERTY_RULE: int = 16

    __slots__ = ("_name", "_syntax", "_inherits", "_initial_value")

    def __init__(
        self, name: str, syntax: str, inherits: str, initial_value: str
    ) -> None:
        super().__init__()
        self._name: str = name
        self._syntax: str = syntax
        self._inherits: str = inherits
        self._initial_value: str = initial_value

    @property
    def type(self) -> int:
        """Return PROPERTY_RULE (16).

        Examples
        --------
        >>> from aspose_html.cssom import CSSPropertyRule
        >>> rule = CSSPropertyRule("--x", '"<color>"', "false", "red")
        >>> rule.type
        16
        """
        return 16

    @property
    def name(self) -> str:
        """The custom property name (e.g. ``'--color'``).

        Examples
        --------
        >>> from aspose_html.cssom import CSSPropertyRule
        >>> rule = CSSPropertyRule("--color", '"<color>"', "false", "red")
        >>> rule.name
        '--color'
        """
        return self._name

    @property
    def syntax(self) -> str:
        """The syntax descriptor string.

        Examples
        --------
        >>> from aspose_html.cssom import CSSPropertyRule
        >>> rule = CSSPropertyRule("--color", '"<color>"', "false", "red")
        >>> rule.syntax
        '"<color>"'
        """
        return self._syntax

    @property
    def inherits(self) -> str:
        """``'true'`` or ``'false'`` (string, not bool).

        Examples
        --------
        >>> from aspose_html.cssom import CSSPropertyRule
        >>> rule = CSSPropertyRule("--color", '"<color>"', "false", "red")
        >>> rule.inherits
        'false'
        """
        return self._inherits

    @property
    def initial_value(self) -> str:
        """The initial-value descriptor string.

        Examples
        --------
        >>> from aspose_html.cssom import CSSPropertyRule
        >>> rule = CSSPropertyRule("--color", '"<color>"', "false", "red")
        >>> rule.initial_value
        'red'
        """
        return self._initial_value

    @property
    def css_text(self) -> str:
        """Reconstructed ``@property`` rule text.

        Examples
        --------
        >>> from aspose_html.cssom import CSSPropertyRule
        >>> rule = CSSPropertyRule("--color", '"<color>"', "false", "red")
        >>> '@property --color' in rule.css_text
        True
        """
        parts = []
        if self._syntax:
            parts.append(f"syntax: {self._syntax}")
        if self._inherits:
            parts.append(f"inherits: {self._inherits}")
        if self._initial_value:
            parts.append(f"initial-value: {self._initial_value}")
        body = "; ".join(parts)
        if body:
            body += ";"
        return f"@property {self._name} {{ {body} }}"


class CSSCounterStyleRule(CSSRule):
    """A ``@counter-style`` rule (CSS Counter Styles Level 3 §3, CSSOM §5.4 type 11).

    Holds the counter style name and its descriptor declarations.  This
    implementation is an object-model stub — it does not affect list-style
    rendering or cascade computation.

    Examples
    --------
    >>> from aspose_html.cssom._stylesheet import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text(
    ...     '@counter-style thumbs { system: cyclic; symbols: "A"; suffix: " "; }'
    ... )
    >>> rule = sheet.css_rules[0]
    >>> isinstance(rule, CSSCounterStyleRule)
    True
    >>> rule.name
    'thumbs'
    >>> rule.css_type
    11
    """

    __slots__ = ("_name", "_body_text")

    def __init__(self, name: str, body_text: str = "") -> None:
        super().__init__()
        self._name = name
        self._body_text = body_text  # raw descriptor text; not cascade-participating

    @property
    def css_type(self) -> int:
        """Rule type constant — always :attr:`CSSRule.COUNTER_STYLE_RULE` (11).

        >>> from aspose_html.cssom._rules import CSSCounterStyleRule
        >>> CSSCounterStyleRule("lower-greek").css_type
        11
        """
        return CSSRule.COUNTER_STYLE_RULE

    @property
    def type(self) -> int:
        """Legacy alias for :attr:`css_type` (CSSOM §6.6 ``type`` property)."""
        return self.css_type

    @property
    def name(self) -> str:
        """The counter style name from the ``@counter-style`` declaration.

        >>> from aspose_html.cssom._rules import CSSCounterStyleRule
        >>> CSSCounterStyleRule("lower-greek").name
        'lower-greek'
        """
        return self._name

    @property
    def style(self) -> str:
        """The rule body descriptor text (raw string, not cascade-participating).

        >>> from aspose_html.cssom._rules import CSSCounterStyleRule
        >>> CSSCounterStyleRule("thumbs", "system: cyclic").style
        'system: cyclic'
        """
        return self._body_text

    @property
    def css_text(self) -> str:
        """Reconstructed ``@counter-style`` declaration string.

        >>> from aspose_html.cssom._rules import CSSCounterStyleRule
        >>> r = CSSCounterStyleRule("thumbs", "system: cyclic")
        >>> "@counter-style thumbs" in r.css_text
        True
        """
        if self._body_text:
            return f"@counter-style {self._name} {{ {self._body_text} }}"
        return f"@counter-style {self._name} {{}}"
