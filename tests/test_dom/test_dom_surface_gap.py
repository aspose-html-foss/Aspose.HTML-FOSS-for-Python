"""Tests for : DOM surface gap closure.

Covers all 11 acceptance criteria from  / :
  - Node.is_connected (AC-1 through AC-4)
  - Document.cookie (AC-5, AC-6)
  - Document.hidden (AC-7)
  - Document.visibility_state (AC-8)
  - Document.has_focus() (AC-9)
  - pytest --doctest-modules passes (AC-10, AC-11)
"""
import pytest

from aspose_html.dom import Document
from aspose_html.dom._exceptions import NotSupportedError


# ---------------------------------------------------------------------------
# Group A — Node.is_connected
# ---------------------------------------------------------------------------

class TestNodeIsConnected:
    """AC-1 through AC-4 and related cases."""

    def test_freshly_created_element_is_not_connected(self):
        """AC-1: a freshly created element has no parent — not connected."""
        doc = Document()
        el = doc.create_element("div")
        assert el.is_connected is False

    def test_appended_element_is_connected(self):
        """AC-2: after append_child, the element is connected."""
        doc = Document()
        el = doc.create_element("div")
        doc.append_child(el)
        assert el.is_connected is True

    def test_element_removed_from_document_is_not_connected(self):
        """Removing an element restores is_connected to False."""
        doc = Document()
        el = doc.create_element("p")
        doc.append_child(el)
        assert el.is_connected is True
        doc.remove_child(el)
        assert el.is_connected is False

    def test_node_in_document_fragment_is_not_connected(self):
        """AC-3: a node appended only to a DocumentFragment is not connected."""
        doc = Document()
        frag = doc.create_document_fragment()
        el = doc.create_element("span")
        frag.append_child(el)
        assert el.is_connected is False

    def test_document_fragment_itself_is_not_connected(self):
        """AC-3: a DocumentFragment itself is not connected (root is not Document)."""
        doc = Document()
        frag = doc.create_document_fragment()
        assert frag.is_connected is False

    def test_document_itself_is_connected(self):
        """AC-4: a Document object returns is_connected == True."""
        doc = Document()
        assert doc.is_connected is True

    def test_deeply_nested_element_in_document_is_connected(self):
        """A deeply nested element whose ancestor chain reaches a Document is connected."""
        doc = Document()
        outer = doc.create_element("div")
        inner = doc.create_element("span")
        leaf = doc.create_element("b")
        doc.append_child(outer)
        outer.append_child(inner)
        inner.append_child(leaf)
        assert leaf.is_connected is True

    def test_detached_subtree_is_not_connected(self):
        """A subtree not appended to a document is not connected, even if multi-level."""
        doc = Document()
        outer = doc.create_element("div")
        inner = doc.create_element("span")
        outer.append_child(inner)
        # Neither node is in the document
        assert outer.is_connected is False
        assert inner.is_connected is False

    def test_text_node_in_document_is_connected(self):
        """is_connected works for non-Element node types (Text)."""
        doc = Document()
        el = doc.create_element("p")
        doc.append_child(el)
        t = doc.create_text_node("hello")
        el.append_child(t)
        assert t.is_connected is True

    def test_text_node_detached_is_not_connected(self):
        """A detached Text node is not connected."""
        doc = Document()
        t = doc.create_text_node("hello")
        assert t.is_connected is False

    def test_comment_node_in_document_is_connected(self):
        """is_connected works for Comment nodes."""
        doc = Document()
        c = doc.create_comment("note")
        doc.append_child(c)
        assert c.is_connected is True


# ---------------------------------------------------------------------------
# Group B — Document.cookie
# ---------------------------------------------------------------------------

class TestDocumentCookie:
    """AC-5 and AC-6."""

    def test_cookie_getter_returns_empty_string(self):
        """AC-5: doc.cookie returns '' (empty string)."""
        doc = Document()
        assert doc.cookie == ""

    def test_cookie_setter_raises_not_supported_error(self):
        """AC-6: doc.cookie = '...' raises NotSupportedError."""
        doc = Document()
        with pytest.raises(NotSupportedError) as exc_info:
            doc.cookie = "foo=bar"
        assert "headless mode" in str(exc_info.value)

    def test_cookie_setter_error_message(self):
        """The error message matches the documented behavior."""
        doc = Document()
        with pytest.raises(NotSupportedError) as exc_info:
            doc.cookie = "session=abc"
        assert str(exc_info.value) == "Document.cookie is not supported in headless mode"


# ---------------------------------------------------------------------------
# Group C — Document.hidden / visibility_state
# ---------------------------------------------------------------------------

class TestDocumentVisibility:
    """AC-7 and AC-8."""

    def test_hidden_is_false(self):
        """AC-7: doc.hidden is False."""
        doc = Document()
        assert doc.hidden is False

    def test_visibility_state_is_visible(self):
        """AC-8: doc.visibility_state is 'visible'."""
        doc = Document()
        assert doc.visibility_state == "visible"


# ---------------------------------------------------------------------------
# Group D — Document.has_focus()
# ---------------------------------------------------------------------------

class TestDocumentHasFocus:
    """AC-9."""

    def test_has_focus_returns_false(self):
        """AC-9: doc.has_focus() returns False."""
        doc = Document()
        assert doc.has_focus() is False

    def test_has_focus_is_callable(self):
        """has_focus is a method (not a property) per WHATWG HTML §7.3.1."""
        doc = Document()
        # Accessing doc.has_focus should give a callable, not a bool
        assert callable(doc.has_focus)

    def test_has_focus_return_type(self):
        """has_focus() returns exactly bool False, not a truthy/falsy non-bool."""
        doc = Document()
        result = doc.has_focus()
        assert result is False
        assert isinstance(result, bool)
