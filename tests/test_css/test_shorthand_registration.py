"""Tests for CSS shorthand registration gap fix — Track 98, ADR-297.

Verifies that the 19 CSS shorthand names that were present in
``_SHORTHAND_EXPANSIONS`` but absent from ``_KNOWN_PROPERTIES`` /
``_INITIAL_VALUE_BASELINE`` now return ``True`` from ``CSS.supports()``.

Covers:
- Physical border-side shorthands: border, border-top/right/bottom/left
- CSS Logical Properties axis shorthands: margin-inline/block,
  padding-inline/block, inset-inline/block
- CSS Logical Properties border shorthands: border-block/inline and
  their start/end variants
- Scroll-box shorthands: scroll-margin, scroll-padding
- Regression guard: no previously-True property becomes False
- Regression guard: shorthand expansion still returns correct longhands
"""
from __future__ import annotations

from aspose_html.cssom import CSS
from aspose_html.dom._cascade_shorthands import _expand_shorthand_value


# ---------------------------------------------------------------------------
# Physical border-side shorthands (AC-1 through AC-5)
# ---------------------------------------------------------------------------


def test_css_supports_border_shorthand() -> None:
    """CSS.supports('border', ...) returns True (AC-1)."""
    assert CSS.supports("border", "1px solid red") is True


def test_css_supports_border_top() -> None:
    """CSS.supports('border-top', ...) returns True (AC-2)."""
    assert CSS.supports("border-top", "2px dashed blue") is True


def test_css_supports_border_right() -> None:
    """CSS.supports('border-right', ...) returns True (AC-3)."""
    assert CSS.supports("border-right", "1px") is True


def test_css_supports_border_bottom() -> None:
    """CSS.supports('border-bottom', ...) returns True (AC-4)."""
    assert CSS.supports("border-bottom", "0") is True


def test_css_supports_border_left() -> None:
    """CSS.supports('border-left', ...) returns True (AC-5)."""
    assert CSS.supports("border-left", "thick") is True


# ---------------------------------------------------------------------------
# CSS Logical Properties axis shorthands (AC-6 through AC-11)
# ---------------------------------------------------------------------------


def test_css_supports_margin_inline() -> None:
    """CSS.supports('margin-inline', ...) returns True (AC-6)."""
    assert CSS.supports("margin-inline", "10px") is True


def test_css_supports_margin_block() -> None:
    """CSS.supports('margin-block', ...) returns True (AC-7)."""
    assert CSS.supports("margin-block", "5px 15px") is True


def test_css_supports_padding_inline() -> None:
    """CSS.supports('padding-inline', ...) returns True (AC-8)."""
    assert CSS.supports("padding-inline", "0") is True


def test_css_supports_padding_block() -> None:
    """CSS.supports('padding-block', ...) returns True (AC-9)."""
    assert CSS.supports("padding-block", "4px") is True


def test_css_supports_inset_inline() -> None:
    """CSS.supports('inset-inline', ...) returns True (AC-10)."""
    assert CSS.supports("inset-inline", "auto") is True


def test_css_supports_inset_block() -> None:
    """CSS.supports('inset-block', ...) returns True (AC-11)."""
    assert CSS.supports("inset-block", "0") is True


# ---------------------------------------------------------------------------
# CSS Logical Properties border shorthands (AC-12 through AC-17)
# ---------------------------------------------------------------------------


def test_css_supports_border_block() -> None:
    """CSS.supports('border-block', ...) returns True (AC-12)."""
    assert CSS.supports("border-block", "1px solid blue") is True


def test_css_supports_border_inline() -> None:
    """CSS.supports('border-inline', ...) returns True (AC-13)."""
    assert CSS.supports("border-inline", "2px dashed") is True


def test_css_supports_border_block_start() -> None:
    """CSS.supports('border-block-start', ...) returns True (AC-14)."""
    assert CSS.supports("border-block-start", "1px solid") is True


def test_css_supports_border_block_end() -> None:
    """CSS.supports('border-block-end', ...) returns True (AC-15)."""
    assert CSS.supports("border-block-end", "0") is True


def test_css_supports_border_inline_start() -> None:
    """CSS.supports('border-inline-start', ...) returns True (AC-16)."""
    assert CSS.supports("border-inline-start", "thin") is True


def test_css_supports_border_inline_end() -> None:
    """CSS.supports('border-inline-end', ...) returns True (AC-17)."""
    assert CSS.supports("border-inline-end", "medium") is True


# ---------------------------------------------------------------------------
# Scroll-box shorthands (AC-18 through AC-19)
# ---------------------------------------------------------------------------


def test_css_supports_scroll_margin() -> None:
    """CSS.supports('scroll-margin', ...) returns True (AC-18)."""
    assert CSS.supports("scroll-margin", "8px") is True


def test_css_supports_scroll_padding() -> None:
    """CSS.supports('scroll-padding', ...) returns True (AC-19)."""
    assert CSS.supports("scroll-padding", "4px 8px") is True


# ---------------------------------------------------------------------------
# Regression guard: no previously-True property becomes False (AC-20 partial)
# ---------------------------------------------------------------------------


def test_css_supports_existing_not_broken() -> None:
    """Pre-existing True properties must remain True — no regression (AC-20)."""
    assert CSS.supports("margin", "10px") is True
    assert CSS.supports("padding", "5px") is True
    assert CSS.supports("border-width", "1px") is True
    assert CSS.supports("border-color", "red") is True
    assert CSS.supports("inset", "0") is True
    # Inherited properties that were already True
    assert CSS.supports("color", "red") is True
    assert CSS.supports("font-size", "16px") is True


# ---------------------------------------------------------------------------
# Regression guard: shorthand expansion still works correctly (AC-21)
# ---------------------------------------------------------------------------


def test_shorthand_expansion_still_works() -> None:
    """_expand_shorthand_value still returns correct longhands after registration fix."""
    result = _expand_shorthand_value("margin-inline", "10px")
    assert result == {"margin-inline-start": "10px", "margin-inline-end": "10px"}


def test_shorthand_expansion_padding_block() -> None:
    """_expand_shorthand_value for padding-block: two tokens expand to start/end."""
    result = _expand_shorthand_value("padding-block", "4px 8px")
    assert result == {"padding-block-start": "4px", "padding-block-end": "8px"}


def test_shorthand_expansion_border_top() -> None:
    """_expand_shorthand_value for border-top: three WSC tokens expand to width/style/color."""
    result = _expand_shorthand_value("border-top", "1px solid red")
    assert result is not None
    assert result.get("border-top-width") == "1px"
    assert result.get("border-top-style") == "solid"
    assert result.get("border-top-color") == "red"


def test_shorthand_expansion_scroll_margin_single() -> None:
    """_expand_shorthand_value for scroll-margin: single value broadcasts to all four."""
    result = _expand_shorthand_value("scroll-margin", "8px")
    assert result is not None
    assert result.get("scroll-margin-top") == "8px"
    assert result.get("scroll-margin-right") == "8px"
    assert result.get("scroll-margin-bottom") == "8px"
    assert result.get("scroll-margin-left") == "8px"
