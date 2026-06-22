"""Tests for Element geometry stubs — DOMRect, DOMRectList, and the
CSSOM View geometry properties/methods on Element (ADR-123 / SPEC-080).
"""
import pytest

from aspose_html.dom import Document, DOMRect, DOMRectList
from aspose_html.dom._geometry import DOMRect as _DOMRect, DOMRectList as _DOMRectList


# ---------------------------------------------------------------------------
# DOMRect
# ---------------------------------------------------------------------------


def test_domrect_zero_default():
    r = DOMRect()
    assert r.x == 0.0
    assert r.y == 0.0
    assert r.width == 0.0
    assert r.height == 0.0


def test_domrect_computed_properties():
    r = DOMRect(x=10.0, y=20.0, width=100.0, height=50.0)
    assert r.left == 10.0
    assert r.right == 110.0
    assert r.top == 20.0
    assert r.bottom == 70.0


def test_domrect_negative_width():
    """CSSOM View §7.1: left = min(x, x+width), right = max(x, x+width)."""
    r = DOMRect(x=10.0, width=-5.0)
    assert r.left == 5.0
    assert r.right == 10.0


def test_domrect_negative_height():
    """CSSOM View §7.1: top = min(y, y+height), bottom = max(y, y+height)."""
    r = DOMRect(y=20.0, height=-50.0)
    assert r.top == -30.0
    assert r.bottom == 20.0


def test_domrect_zero_computed_properties():
    r = DOMRect()
    assert r.top == 0.0
    assert r.right == 0.0
    assert r.bottom == 0.0
    assert r.left == 0.0


def test_domrect_mutable_attributes():
    r = DOMRect(x=1.0, y=2.0, width=3.0, height=4.0)
    r.x = 5.0
    r.width = 10.0
    assert r.right == 15.0


def test_domrect_repr():
    r = DOMRect(x=1.0, y=2.0, width=3.0, height=4.0)
    assert "DOMRect" in repr(r)


# ---------------------------------------------------------------------------
# DOMRectList
# ---------------------------------------------------------------------------


def test_domrectlist_empty():
    rl = DOMRectList([])
    assert len(rl) == 0
    assert rl.item(0) is None
    assert list(rl) == []


def test_domrectlist_item_and_length():
    r1, r2 = DOMRect(), DOMRect()
    rl = DOMRectList([r1, r2])
    assert len(rl) == 2
    assert rl.item(0) is r1
    assert rl.item(1) is r2
    assert rl.item(5) is None


def test_domrectlist_iter():
    r1, r2 = DOMRect(1.0), DOMRect(2.0)
    rl = DOMRectList([r1, r2])
    assert list(rl) == [r1, r2]


def test_domrectlist_getitem():
    r = DOMRect(3.0)
    rl = DOMRectList([r])
    assert rl[0] is r


def test_domrectlist_getitem_out_of_range():
    rl = DOMRectList([])
    with pytest.raises(IndexError):
        _ = rl[0]


def test_domrectlist_item_returns_none_not_raises():
    """item() must return None for out-of-range — not raise IndexError."""
    rl = DOMRectList([DOMRect()])
    assert rl.item(99) is None


def test_domrectlist_repr():
    rl = DOMRectList([DOMRect()])
    assert "DOMRectList" in repr(rl)


# ---------------------------------------------------------------------------
# Element geometry methods
# ---------------------------------------------------------------------------


def test_get_bounding_client_rect_returns_zero_domrect():
    doc = Document()
    el = doc.create_element("div")
    r = el.get_bounding_client_rect()
    assert isinstance(r, DOMRect)
    assert r.x == 0.0
    assert r.y == 0.0
    assert r.width == 0.0
    assert r.height == 0.0


def test_get_bounding_client_rect_returns_new_instance_each_call():
    doc = Document()
    el = doc.create_element("div")
    r1 = el.get_bounding_client_rect()
    r2 = el.get_bounding_client_rect()
    assert r1 is not r2


def test_get_client_rects_returns_empty_domrectlist():
    doc = Document()
    el = doc.create_element("div")
    rl = el.get_client_rects()
    assert isinstance(rl, DOMRectList)
    assert len(rl) == 0


# ---------------------------------------------------------------------------
# Element geometry properties — all return 0
# ---------------------------------------------------------------------------


def test_scroll_client_offset_return_zero():
    doc = Document()
    el = doc.create_element("div")
    for attr in (
        "scroll_width",
        "scroll_height",
        "client_width",
        "client_height",
        "offset_width",
        "offset_height",
        "offset_top",
        "offset_left",
        "scroll_top",
        "scroll_left",
    ):
        assert getattr(el, attr) == 0, f"{attr} should be 0"


def test_scroll_top_setter_is_noop():
    doc = Document()
    el = doc.create_element("div")
    el.scroll_top = 100  # must not raise
    assert el.scroll_top == 0


def test_scroll_left_setter_is_noop():
    doc = Document()
    el = doc.create_element("div")
    el.scroll_left = 200  # must not raise
    assert el.scroll_left == 0


def test_scroll_top_setter_accepts_negative():
    doc = Document()
    el = doc.create_element("div")
    el.scroll_top = -50  # must not raise
    assert el.scroll_top == 0


# ---------------------------------------------------------------------------
# CSSOM View §5 gap-closure stubs — offset_parent, client_top, client_left
# (ADR-164 / BACK-181)
# ---------------------------------------------------------------------------


def test_offset_parent_is_none():
    doc = Document()
    el = doc.create_element("div")
    assert el.offset_parent is None


def test_client_top_is_zero():
    doc = Document()
    el = doc.create_element("div")
    assert el.client_top == 0


def test_client_left_is_zero():
    doc = Document()
    el = doc.create_element("div")
    assert el.client_left == 0


def test_geometry_properties_are_int():
    doc = Document()
    el = doc.create_element("div")
    assert isinstance(el.client_top, int)
    assert isinstance(el.client_left, int)


# ---------------------------------------------------------------------------
# Public API export
# ---------------------------------------------------------------------------


def test_domrect_importable_from_dom():
    from aspose_html.dom import DOMRect as DR, DOMRectList as DRL  # noqa: PLC0415
    assert DR is _DOMRect
    assert DRL is _DOMRectList


def test_domrect_in_all():
    import aspose_html.dom as dom  # noqa: PLC0415
    assert "DOMRect" in dom.__all__
    assert "DOMRectList" in dom.__all__
