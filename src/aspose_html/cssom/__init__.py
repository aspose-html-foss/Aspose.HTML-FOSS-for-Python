"""Public CSSOM rule-object baseline (Track 14 / BACK-81, extended BACK-164).

Examples
--------
>>> from aspose_html.cssom import CSSStyleSheet
>>> sheet = CSSStyleSheet()
>>> sheet.replace_sync("p { color: red }")
>>> sheet.css_rules[0].css_text
'p { color: red }'
"""

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
    CSSRuleList,
    CSSStyleRule,
    CSSSupportsRule,
)
from ._stylesheet import CSSStyleSheet


class CSS:
    """Namespace class for CSS static utilities (CSS Conditional Rules §6).

    No instance state.  All methods are ``@staticmethod``.

    In the **two-argument form** the pair is wrapped as ``"(property: value)"``
    before evaluation, so the property name alone is sufficient:

    >>> CSS.supports("color", "red")
    True
    >>> CSS.supports("font-size", "1em")
    True
    >>> CSS.supports("unknown-bogus-property", "value")
    False
    >>> CSS.supports("selector(div)")
    False
    """

    @staticmethod
    def supports(property_or_condition: str, value: str | None = None) -> bool:
        """Return ``True`` when the CSS feature described by the arguments is supported.

        Two call forms (CSS Conditional Rules §6):

        - ``CSS.supports(conditionText)`` — evaluates *conditionText* as a
          ``@supports`` condition string directly.  The string must already be
          in ``@supports`` condition syntax, e.g. ``"(color: red)"``.
        - ``CSS.supports(property, value)`` — wraps the pair as
          ``"({property}: {value})"`` before evaluating.

        The evaluation uses the same conservative feature-detection logic as
        the ``@supports`` cascade rule in :mod:`aspose_html.dom._cascade`.

        Parameters
        ----------
        property_or_condition:
            Either a ``@supports`` condition string (one-argument form) or a
            CSS property name (two-argument form).
        value:
            CSS property value; only valid in the two-argument form.

        Returns
        -------
        bool
            ``True`` when the condition or property/value pair is recognised
            as supported.

        Examples
        --------
        >>> CSS.supports("color", "red")
        True
        >>> CSS.supports("(color: red)")
        True
        >>> CSS.supports("font-size", "12px")
        True
        >>> CSS.supports("fake-property", "red")
        False
        >>> CSS.supports("selector(div > p)")
        False
        """
        from aspose_html.dom._cascade import _supports_condition_matches
        if value is not None:
            condition = f"({property_or_condition}: {value})"
        else:
            condition = property_or_condition
        return _supports_condition_matches(condition)


__all__ = [
    "CSS",
    "CSSRule",
    "CSSStyleRule",
    "CSSMediaRule",
    "CSSRuleList",
    "CSSKeyframesRule",
    "CSSKeyframeRule",
    "CSSFontFaceRule",
    "CSSSupportsRule",
    "CSSImportRule",
    "CSSLayerBlockRule",
    "CSSLayerStatementRule",
    "CSSNamespaceRule",
    "CSSCounterStyleRule",
    "CSSPageRule",
    "CSSPropertyRule",
    "CSSStyleSheet",
]
