"""Tests for VisualViewport class and Window.visual_viewport (BACK-296 / ADR-274)."""
import pytest

from aspose_html.dom import Document, VisualViewport
from aspose_html.dom._window import VisualViewport as _VisualViewport


def _window():
    return Document().default_view


def test_visual_viewport_type():
    """window.visual_viewport returns a VisualViewport instance."""
    vv = _window().visual_viewport
    assert isinstance(vv, VisualViewport)


def test_visual_viewport_is_singleton():
    """window.visual_viewport returns the same object on repeated access."""
    w = _window()
    assert w.visual_viewport is w.visual_viewport


def test_visual_viewport_scale():
    assert _window().visual_viewport.scale == 1.0


def test_visual_viewport_width():
    assert _window().visual_viewport.width == 0


def test_visual_viewport_height():
    assert _window().visual_viewport.height == 0


def test_visual_viewport_offset_left():
    assert _window().visual_viewport.offset_left == 0.0


def test_visual_viewport_offset_top():
    assert _window().visual_viewport.offset_top == 0.0


def test_visual_viewport_page_left():
    assert _window().visual_viewport.page_left == 0.0


def test_visual_viewport_page_top():
    assert _window().visual_viewport.page_top == 0.0


def test_visual_viewport_importable_from_dom():
    """from aspose_html.dom import VisualViewport must succeed."""
    from aspose_html.dom import VisualViewport as VV  # noqa: PLC0415
    assert VV is _VisualViewport
