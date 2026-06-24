"""CSSStyleSheet baseline implementation."""
from __future__ import annotations

from aspose_html.dom import IndexSizeError

from ._parser import parse_rule_text, parse_stylesheet
from ._rules import CSSMediaRule, CSSRule, CSSRuleList


class CSSStyleSheet:
    """Minimal CSSOM stylesheet object (CSSOM §6.4).

    Examples
    --------
    >>> sheet = CSSStyleSheet()
    >>> sheet.replace_sync("p { color: red; margin: 0 }")
    >>> sheet.css_rules.length
    1
    >>> sheet.css_rules[0].css_text
    'p { color: red; margin: 0 }'
    >>> sheet2 = CSSStyleSheet.from_text("div { color: blue }", title="theme", href="/a.css", media="screen")
    >>> sheet2.title
    'theme'
    >>> sheet2.href
    '/a.css'
    >>> sheet2.media
    'screen'
    >>> sheet2.disabled
    False
    >>> sheet2.owner_rule is None
    True
    """

    __slots__ = (
        "_rules",
        "css_rules",
        "owner_node",
        "_href",
        "_base_url",
        "_title",
        "_disabled",
        "_owner_rule",
        "_media",
        "_parent_style_sheet",
        "_owner_document_ref",  # M7.1 adopted/attached back-reference — /
    )

    def __init__(self) -> None:
        self._rules: list[CSSRule] = []
        self.css_rules = CSSRuleList(lambda: self._rules)
        self.owner_node: object | None = None
        self._href: str | None = None
        self._base_url: str | None = None
        self._title: str = ""
        self._disabled: bool = False
        self._owner_rule: CSSRule | None = None
        self._media: str = ""
        self._parent_style_sheet: "CSSStyleSheet | None" = None
        # Set when this sheet is adopted/attached to a Document so the
        # mutation methods can invalidate that document's layout style cache
        # (M7.1). None for unattached / construction-time sheets.
        self._owner_document_ref: object | None = None

    # ------------------------------------------------------------------
    # CSSOM §6.4 metadata properties
    # ------------------------------------------------------------------

    @property
    def href(self) -> str | None:
        """URL of this stylesheet, or ``None`` for inline sheets (CSSOM §6.4).

        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red; }")
        >>> sheet.href is None
        True
        >>> sheet2 = CSSStyleSheet.from_text("p { color: red; }", href="/a.css")
        >>> sheet2.href
        '/a.css'
        """
        return self._href

    @href.setter
    def href(self, value: str | None) -> None:
        self._href = value

    @property
    def title(self) -> str:
        """The title of this stylesheet (CSSOM §6.4).

        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red; }", title="theme")
        >>> sheet.title
        'theme'
        """
        return self._title

    @property
    def disabled(self) -> bool:
        """Whether this stylesheet is disabled (CSSOM §6.4). Always ``False``.

        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red; }")
        >>> sheet.disabled
        False
        """
        return self._disabled

    @property
    def owner_rule(self) -> CSSRule | None:
        """The ``@import`` rule that owns this sheet, or ``None`` (CSSOM §6.4).

        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red; }")
        >>> sheet.owner_rule is None
        True
        """
        return self._owner_rule

    @property
    def media(self) -> str:
        """The media query string for this stylesheet (CSSOM §6.4).

        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red; }")
        >>> sheet.media
        ''
        >>> sheet2 = CSSStyleSheet.from_text("p { color: red; }", media="screen")
        >>> sheet2.media
        'screen'
        """
        return self._media

    @property
    def parent_style_sheet(self) -> "CSSStyleSheet | None":
        """The stylesheet that imported this one via ``@import``, or ``None`` (CSSOM §7.2.1).

        For top-level stylesheets this is always ``None``.  Non-None values
        are set by future ``@import``-linking logic.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red }")
        >>> sheet.parent_style_sheet is None
        True
        """
        return self._parent_style_sheet

    @property
    def rules(self) -> "CSSRuleList":
        """Legacy alias for ``css_rules`` (CSSOM §7.2.1 historical).

        Returns the same live :class:`CSSRuleList` object as :attr:`css_rules`.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red }")
        >>> sheet.rules is sheet.css_rules
        True
        """
        return self.css_rules

    def add_rule(self, selector: str, style: str, index: int = -1) -> int:
        """Insert a new rule (legacy Netscape/IE form) — delegates to ``insert_rule``.

        Constructs the text ``"{selector} {{ {style} }}"`` and calls
        :meth:`insert_rule`.  When *index* is ``-1`` (the default), the rule
        is appended at the end of the list.

        Returns ``-1`` per the CSSOM historical specification.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red }")
        >>> sheet.add_rule("div", "margin: 0")
        -1
        >>> len(sheet.css_rules)
        2
        """
        rule_text = f"{selector} {{ {style} }}"
        insert_index = len(self._rules) if index == -1 else index
        self.insert_rule(rule_text, insert_index)
        return -1

    def remove_rule(self, index: int = 0) -> None:
        """Remove the rule at *index* (legacy Netscape/IE form) — delegates to ``delete_rule``.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red }")
        >>> sheet.remove_rule(0)
        >>> len(sheet.css_rules)
        0
        """
        self.delete_rule(index)

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_text(
        cls,
        css_text: str,
        *,
        title: str = "",
        href: str | None = None,
        media: str = "",
    ) -> "CSSStyleSheet":
        """Create a ``CSSStyleSheet`` from a CSS text string.

        Parameters
        ----------
        css_text:
            The CSS source to parse.
        title:
            Optional stylesheet title (CSSOM §6.4 ``title`` attribute).
        href:
            Optional URL of the stylesheet (CSSOM §6.4 ``href`` attribute).
        media:
            Optional media query string (CSSOM §6.4 ``media`` attribute).

        Returns
        -------
        CSSStyleSheet

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("div { color: red; }", title="T", href="/s.css", media="all")
        >>> sheet.css_rules.length
        1
        >>> sheet.title
        'T'
        >>> sheet.href
        '/s.css'
        >>> sheet.media
        'all'
        """
        instance = cls()
        instance.replace_sync(css_text)
        instance._title = title
        instance._href = href
        instance._base_url = href
        instance._media = media
        return instance

    # ------------------------------------------------------------------
    # Mutation API
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # M7.1 layout style-cache invalidation (/)
    # ------------------------------------------------------------------

    def _set_owner_document(self, document: object | None) -> None:
        """Record (or clear) the owning Document for cache invalidation.

        Set by ``Document.attach_style_sheet`` / ``adopted_style_sheets`` on
        adoption and cleared on detach. Internal — not part of the CSSOM
        surface.
        """
        self._owner_document_ref = document

    def _owning_document(self) -> object | None:
        """Resolve the Document whose layout cache this sheet feeds, or ``None``.

        An adopted/attached sheet carries a direct back-reference
        (``_owner_document_ref``); a ``<style>``/``<link>`` sheet is reached
        through its ``owner_node`` element's ``owner_document``. Returns
        ``None`` for an unattached sheet (e.g. during construction), in which
        case no invalidation occurs.
        """
        doc = self._owner_document_ref
        if doc is not None:
            return doc
        owner_node = self.owner_node
        if owner_node is not None:
            return getattr(owner_node, "owner_document", None)
        return None

    def _invalidate_owner_document_style(self) -> None:
        """Bump the owning document's style epoch when this sheet mutates.

        Silent no-op when the sheet is not attached/adopted to a document
        (AC-11/AC-12 — detached sheets never bump).
        """
        doc = self._owning_document()
        if doc is not None:
            doc._bump_style_epoch()

    def replace_sync(self, css_text: str) -> None:
        """Replace stylesheet contents from CSS text."""
        parsed = parse_stylesheet(css_text)
        self._rules = parsed
        self.css_rules = CSSRuleList(lambda: self._rules)
        self._wire_parent_links()
        self._invalidate_owner_document_style()  # AC-11

    def insert_rule(self, rule_text: str, index: int | None = None) -> int:
        """Parse *rule_text* and insert it at *index* in :attr:`css_rules`.

        Parameters
        ----------
        rule_text : str
            A CSS rule string, e.g. ``"p { color: red }"``.
        index : int or None
            Position at which to insert.  ``None`` or an omitted index
            appends the rule (index = length).  Must be in range
            ``[0, length]`` (inclusive); raises
            :class:`~aspose_html.dom.IndexSizeError` otherwise.

        Returns
        -------
        int
            The index at which the rule was inserted.

        Raises
        ------
        IndexSizeError
            If *index* is negative or greater than the current rule count.
        SyntaxError
            If *rule_text* cannot be parsed as a valid CSS rule.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red }")
        >>> sheet.insert_rule("div { margin: 0 }")
        1
        >>> sheet.css_rules.length
        2
        >>> sheet.insert_rule("span { color: blue }", 0)
        0
        >>> sheet.css_rules[0].selector_text
        'span'
        """
        rule = parse_rule_text(rule_text, allow_media=True)
        insert_index = len(self._rules) if index is None else index
        if not (0 <= insert_index <= len(self._rules)):
            raise IndexSizeError("rule index out of range")
        rule.parent_style_sheet = self
        rule.parent_rule = None
        self._rules.insert(insert_index, rule)
        self._invalidate_owner_document_style()  # AC-12
        return insert_index

    def delete_rule(self, index: int) -> None:
        """Remove the rule at *index* from :attr:`css_rules`.

        Parameters
        ----------
        index : int
            Zero-based position to remove.  Must be in range
            ``[0, length - 1]``; raises
            :class:`~aspose_html.dom.IndexSizeError` otherwise.

        Raises
        ------
        IndexSizeError
            If *index* is out of range.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red } div { margin: 0 }")
        >>> sheet.css_rules.length
        2
        >>> sheet.delete_rule(0)
        >>> sheet.css_rules.length
        1
        """
        if not (0 <= index < len(self._rules)):
            raise IndexSizeError("rule index out of range")
        rule = self._rules.pop(index)
        rule.parent_style_sheet = None
        self._invalidate_owner_document_style()  # AC-12

    @property
    def css_text(self) -> str:
        """Serialise the stylesheet to a CSS text string (CSSOM §6.6).

        Returns all rules joined by newlines via their individual
        :attr:`~aspose_html.cssom.CSSRule.css_text` properties.  The value
        is always consistent with the live :attr:`css_rules` list — no
        cached text is stored.

        Examples
        --------
        >>> from aspose_html.cssom import CSSStyleSheet
        >>> sheet = CSSStyleSheet.from_text("p { color: red; }")
        >>> "p {" in sheet.css_text
        True
        >>> sheet2 = CSSStyleSheet.from_text(
        ...     "@keyframes slide { from { opacity: 0 } to { opacity: 1 } }"
        ... )
        >>> "@keyframes slide" in sheet2.css_text
        True
        """
        return "\n".join(rule.css_text for rule in self._rules)

    def _wire_parent_links(self) -> None:
        for rule in self._rules:
            rule.parent_style_sheet = self
            rule.parent_rule = None
            if isinstance(rule, CSSMediaRule):
                for child in rule.css_rules:
                    child.parent_rule = rule
                    child.parent_style_sheet = self
