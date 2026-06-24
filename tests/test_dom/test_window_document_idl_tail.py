"""Tests for :  — Window IDL tail and Document IDL stubs.

Covers  /  acceptance criteria AC-1 through AC-17:
  AC-1  to AC-11: Window.self, window, closed, top, parent, opener, screen_x/y,
                  scroll, scroll_to, scroll_by.
  AC-11 to AC-15: Document.design_mode, dir, current_script.
  AC-16:          All new members have runnable doctest examples (verified by
                  pytest --doctest-modules separately).
  AC-17:          This file contains >= 16 tests; 0 new failures in full suite.
"""

from aspose_html.dom._document import Document


# ---------------------------------------------------------------------------
# Window — self-reference aliases (WHATWG HTML §11.1.1)
# ---------------------------------------------------------------------------

def test_window_self_is_self():
    """AC-1: w.self is the same Window instance."""
    w = Document().default_view
    assert w.self is w


def test_window_window_is_self():
    """AC-2: w.window is the same Window instance."""
    w = Document().default_view
    assert w.window is w


# ---------------------------------------------------------------------------
# Window — browsing-context state (WHATWG HTML §11.1.2–3)
# ---------------------------------------------------------------------------

def test_window_closed_false_before_close():
    """AC-3: closed is False on a freshly created window."""
    w = Document().default_view
    assert w.closed is False


def test_window_closed_true_after_close():
    """Bonus: close() sets closed to True (exercises close() interaction)."""
    w = Document().default_view
    w.close()
    assert w.closed is True


def test_window_top_is_self():
    """AC-4: top returns self in non-framed headless mode."""
    w = Document().default_view
    assert w.top is w


def test_window_parent_is_self():
    """AC-5: parent returns self in non-framed headless mode."""
    w = Document().default_view
    assert w.parent is w


def test_window_opener_is_none():
    """AC-6: opener is None in headless mode (no opener window)."""
    w = Document().default_view
    assert w.opener is None


# ---------------------------------------------------------------------------
# Window — screen geometry stubs (CSSOM View §9.2)
# ---------------------------------------------------------------------------

def test_window_screen_x_is_zero():
    """AC-7 (part 1): screen_x returns 0."""
    w = Document().default_view
    assert w.screen_x == 0


def test_window_screen_y_is_zero():
    """AC-7 (part 2): screen_y returns 0."""
    w = Document().default_view
    assert w.screen_y == 0


# ---------------------------------------------------------------------------
# Window — viewport scroll methods (CSSOM View §5.5)
# ---------------------------------------------------------------------------

def test_window_scroll_noop():
    """AC-8: scroll(x, y) returns None without error."""
    w = Document().default_view
    assert w.scroll(0, 0) is None


def test_window_scroll_with_options():
    """scroll() silently accepts ScrollOptions keyword arguments."""
    w = Document().default_view
    assert w.scroll(0, 0, behavior="smooth") is None


def test_window_scroll_to_noop():
    """AC-9: scroll_to(x, y) returns None without error."""
    w = Document().default_view
    assert w.scroll_to(0, 0) is None


def test_window_scroll_to_with_options():
    """scroll_to() silently accepts ScrollOptions keyword arguments."""
    w = Document().default_view
    assert w.scroll_to(0, 0, behavior="instant") is None


def test_window_scroll_by_noop():
    """AC-10: scroll_by(x, y) returns None without error."""
    w = Document().default_view
    assert w.scroll_by(0, 0) is None


def test_window_scroll_by_with_options():
    """scroll_by() silently accepts ScrollOptions keyword arguments."""
    w = Document().default_view
    assert w.scroll_by(10, 20, behavior="auto") is None


# ---------------------------------------------------------------------------
# Document — metadata stubs (WHATWG HTML §7.6.4, §3.3.2, §8.1.3.4)
# ---------------------------------------------------------------------------

def test_document_design_mode_default():
    """AC-11: design_mode getter returns 'off'."""
    doc = Document()
    assert doc.design_mode == "off"


def test_document_design_mode_setter_noop():
    """AC-12: setting design_mode = 'on' is a no-op; still returns 'off'."""
    doc = Document()
    doc.design_mode = "on"
    assert doc.design_mode == "off"


def test_document_design_mode_setter_accepts_off():
    """design_mode setter accepts 'off' without error."""
    doc = Document()
    doc.design_mode = "off"
    assert doc.design_mode == "off"


def test_document_dir_default():
    """AC-13: dir getter returns empty string."""
    doc = Document()
    assert doc.dir == ""


def test_document_dir_setter_noop():
    """AC-14: setting dir = 'rtl' is a no-op; still returns ''."""
    doc = Document()
    doc.dir = "rtl"
    assert doc.dir == ""


def test_document_dir_setter_accepts_ltr():
    """dir setter accepts 'ltr' without error."""
    doc = Document()
    doc.dir = "ltr"
    assert doc.dir == ""


def test_document_current_script_none():
    """AC-15: current_script returns None."""
    doc = Document()
    assert doc.current_script is None


# ---------------------------------------------------------------------------
# Attribute error checks — new members are accessible (regression guard)
# ---------------------------------------------------------------------------

def test_window_members_accessible():
    """All 11 new Window members are accessible without AttributeError."""
    w = Document().default_view
    # Properties
    _ = w.self
    _ = w.window
    _ = w.closed
    _ = w.top
    _ = w.parent
    _ = w.opener
    _ = w.screen_x
    _ = w.screen_y
    # Methods — call to ensure accessible
    w.scroll(0, 0)
    w.scroll_to(0, 0)
    w.scroll_by(0, 0)


def test_document_members_accessible():
    """All 3 new Document members are accessible without AttributeError."""
    doc = Document()
    _ = doc.design_mode
    _ = doc.dir
    _ = doc.current_script
