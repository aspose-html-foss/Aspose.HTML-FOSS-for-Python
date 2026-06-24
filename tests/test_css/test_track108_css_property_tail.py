"""Tests for  CSS property tail — , .

Covers CSS Transforms Level 2 individual-transform longhands,
CSS Text Level 4 text-wrap family, CSS Compositing, CSS Fragmentation,
CSS Images Level 4, CSS Cascade Level 4 ``all`` sentinel,
CSS Text Decoration Level 4, and CSS Container Queries Level 1
(container-type / container-name / container shorthand).

AC map (see ):
  AC-1  — CSS.supports("rotate", "45deg") is True
  AC-2  — CSS.supports("scale", "0.5") is True
  AC-3  — CSS.supports("translate", "10px") is True
  AC-4  — CSS.supports("line-break", "strict") is True
  AC-5  — CSS.supports("text-wrap", "balance") is True
  AC-6  — CSS.supports("text-wrap-mode", "nowrap") is True
  AC-7  — CSS.supports("text-wrap-style", "stable") is True
  AC-8  — CSS.supports("background-blend-mode", "multiply") is True
  AC-9  — CSS.supports("box-decoration-break", "clone") is True
  AC-10 — CSS.supports("image-orientation", "from-image") is True
  AC-11 — CSS.supports("all", "unset") is True
  AC-12 — CSS.supports("text-underline-offset", "0.1em") is True
  AC-13 — CSS.supports("container-type", "inline-size") is True
  AC-14 — CSS.supports("container-name", "sidebar") is True
  AC-15 — container shorthand "sidebar / inline-size" → name+type correct
  AC-16 — container shorthand "main" → name "main", type defaults to "normal"
  AC-17 — len(_INITIAL_VALUE_BASELINE) == 368
"""
from __future__ import annotations

import pytest

from aspose_html.cssom import CSS
from aspose_html.dom import Document
from aspose_html.dom._cascade_data import _INITIAL_VALUE_BASELINE


def _make_element_with_inline(prop: str, value: str) -> object:
    """Create a <div> with *prop* set as inline style and return it."""
    doc = Document()
    el = doc.create_element("div")
    doc.append_child(el)
    el.style[prop] = value
    return el


# ---------------------------------------------------------------------------
# AC-1 / AC-2 / AC-3
# ---------------------------------------------------------------------------

def test_css_supports_individual_transforms() -> None:
    """CSS.supports returns True for all CSS Transforms Level 2 individual longhands."""
    assert CSS.supports("rotate", "45deg")
    assert CSS.supports("scale", "0.5")
    assert CSS.supports("translate", "10px")


# ---------------------------------------------------------------------------
# AC-4 / AC-5 / AC-6 / AC-7
# ---------------------------------------------------------------------------

def test_css_supports_text_wrap_family() -> None:
    """CSS.supports returns True for all CSS Text Level 4 text-wrap longhands."""
    assert CSS.supports("line-break", "strict")
    assert CSS.supports("text-wrap", "balance")
    assert CSS.supports("text-wrap-mode", "nowrap")
    assert CSS.supports("text-wrap-style", "stable")


# ---------------------------------------------------------------------------
# AC-8 / AC-9 / AC-10 / AC-11 / AC-12
# ---------------------------------------------------------------------------

def test_css_supports_misc_modern() -> None:
    """CSS.supports returns True for misc modern CSS properties (compositing, fragmentation, etc.)."""
    assert CSS.supports("background-blend-mode", "multiply")
    assert CSS.supports("box-decoration-break", "clone")
    assert CSS.supports("image-orientation", "from-image")
    assert CSS.supports("all", "unset")
    assert CSS.supports("text-underline-offset", "0.1em")


# ---------------------------------------------------------------------------
# AC-13 / AC-14 + container shorthand CSS.supports
# ---------------------------------------------------------------------------

def test_css_supports_container_queries() -> None:
    """CSS.supports returns True for all Container Queries Level 1 properties."""
    assert CSS.supports("container-type", "inline-size")
    assert CSS.supports("container-name", "sidebar")
    assert CSS.supports("container", "sidebar / inline-size")


# ---------------------------------------------------------------------------
# AC-15
# ---------------------------------------------------------------------------

def test_container_shorthand_expansion() -> None:
    """container shorthand 'sidebar / inline-size' → container-name and container-type."""
    el = _make_element_with_inline("container", "sidebar / inline-size")
    style = el.get_computed_style()
    assert style.get_property_value("container-name") == "sidebar"
    assert style.get_property_value("container-type") == "inline-size"


# ---------------------------------------------------------------------------
# AC-16
# ---------------------------------------------------------------------------

def test_container_shorthand_name_only() -> None:
    """container shorthand 'main' (no slash) → name='main', type defaults to 'normal'."""
    el = _make_element_with_inline("container", "main")
    style = el.get_computed_style()
    assert style.get_property_value("container-name") == "main"
    assert style.get_property_value("container-type") == "normal"


# ---------------------------------------------------------------------------
# AC-17
# ---------------------------------------------------------------------------

def test_initial_value_baseline_count() -> None:
    """_INITIAL_VALUE_BASELINE must have exactly 416 entries after ."""
    assert len(_INITIAL_VALUE_BASELINE) == 416
