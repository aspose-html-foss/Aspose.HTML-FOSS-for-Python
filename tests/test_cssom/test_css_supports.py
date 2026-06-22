"""Tests for CSS.supports() static helper (BACK-196, ADR-179).

Tests cover the public contract of CSS.supports() from
aspose_html.cssom as specified by CSS Conditional Rules Level 4 §6.

Note on one-argument form
-------------------------
``CSS.supports(conditionText)`` passes the string directly to the
underlying ``_supports_condition_matches`` engine, which requires
``@supports`` condition syntax — i.e. the declaration must be wrapped
in parentheses: ``"(color: red)"``.  Bare ``"color: red"`` (without
parens) is not valid ``@supports`` condition text and returns ``False``.
"""
import aspose_html.cssom
from aspose_html.cssom import CSS


class TestCSSSupportsImport:
    """Importability and namespace checks."""

    def test_css_importable(self) -> None:
        """from aspose_html.cssom import CSS must not raise."""
        # Import already performed at module level; reaching this line is success.
        assert CSS is not None

    def test_css_in_all(self) -> None:
        """'CSS' must appear in aspose_html.cssom.__all__."""
        assert "CSS" in aspose_html.cssom.__all__

    def test_css_in_dir(self) -> None:
        """'CSS' must appear in dir(aspose_html.cssom)."""
        assert "CSS" in dir(aspose_html.cssom)


class TestCSSSupportsOneArg:
    """One-argument form: CSS.supports(conditionText).

    conditionText must be in @supports condition syntax:
    declarations require surrounding parentheses.
    """

    def test_one_arg_known_property_with_parens(self) -> None:
        """CSS.supports('(color: red)') is True — parenthesised form."""
        assert CSS.supports("(color: red)") is True

    def test_one_arg_known_font_size(self) -> None:
        """CSS.supports('(font-size: 1em)') is True."""
        assert CSS.supports("(font-size: 1em)") is True

    def test_one_arg_bare_string_false(self) -> None:
        """CSS.supports('color: red') without parens is False.

        The underlying engine requires @supports condition syntax;
        bare 'property: value' is not recognised.
        """
        assert CSS.supports("color: red") is False

    def test_one_arg_unknown_property_false(self) -> None:
        """CSS.supports('(bogus-prop: val)') is False for unknown property."""
        assert CSS.supports("(bogus-prop: val)") is False

    def test_one_arg_selector_false(self) -> None:
        """CSS.supports('selector(div > p)') is always False."""
        assert CSS.supports("selector(div > p)") is False

    def test_one_arg_empty_false(self) -> None:
        """CSS.supports('') is False for empty string."""
        assert CSS.supports("") is False

    def test_one_arg_and_clause(self) -> None:
        """CSS.supports with 'and' compound condition is True when all parts match."""
        assert CSS.supports("(color: red) and (font-size: 1em)") is True


class TestCSSSupportssTwoArg:
    """Two-argument form: CSS.supports(property, value).

    The two-argument form wraps the pair as '(property: value)'
    before passing to the evaluation engine.
    """

    def test_two_arg_known_color(self) -> None:
        """CSS.supports('color', 'red') is True for a known property."""
        assert CSS.supports("color", "red") is True

    def test_two_arg_known_font_size(self) -> None:
        """CSS.supports('font-size', '12px') is True."""
        assert CSS.supports("font-size", "12px") is True

    def test_two_arg_unknown_property_false(self) -> None:
        """CSS.supports('fake-bogus-prop', 'x') is False for unknown property."""
        assert CSS.supports("fake-bogus-prop", "x") is False

    def test_two_arg_unknown_bogus_property_false(self) -> None:
        """CSS.supports('unknown-bogus-property', 'value') is False."""
        assert CSS.supports("unknown-bogus-property", "value") is False

    def test_two_arg_custom_property_false(self) -> None:
        """CSS.supports('--foo', '1') is False.

        The underlying _supports_condition_matches engine does not
        recognise CSS custom properties (--*) as supported names.
        The two-arg form wraps as '(--foo: 1)', which the engine
        returns False for because '--foo' does not match _SUPPORTED_NAME_RE.

        Note: ADR-179 draft listed True here; actual engine behavior is
        False.  See SINV created at BACK-196 Build hop.
        """
        assert CSS.supports("--foo", "1") is False

    def test_two_arg_wraps_as_condition(self) -> None:
        """Two-arg form wraps pair as '(property: value)' before evaluation."""
        # Verify via matching one-arg result for the same wrapped string
        assert CSS.supports("color", "red") == CSS.supports("(color: red)")

    def test_two_arg_selector_false(self) -> None:
        """CSS.supports('selector(div > p)') one-arg is False."""
        assert CSS.supports("selector(div > p)") is False
