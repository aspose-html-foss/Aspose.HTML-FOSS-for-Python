"""DOMImplementation — legacy DOM feature probing surface."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.dom._exceptions import InvalidCharacterError, WrongDocumentError
from aspose_html.dom._node import _adopt

if TYPE_CHECKING:
    from aspose_html.dom._document import Document
    from aspose_html.dom._document_type import DocumentType


def _validate_doctype_name(qualified_name: str) -> None:
    if qualified_name == "":
        raise InvalidCharacterError("DocumentType name must not be empty.")
    if any(ch.isspace() for ch in qualified_name):
        raise InvalidCharacterError("DocumentType name must not contain whitespace.")


class DOMImplementation:
    """Legacy DOMImplementation compatibility surface.

    Provides deterministic, side-effect free feature-probe behavior.
    """

    __slots__ = ("_document",)

    def __init__(self, document: object | None = None) -> None:
        self._document = document

    def has_feature(self, feature: str, version: str | None = None) -> bool:
        """Return legacy feature-probe compatibility status.

        Legacy compatibility alias for DOM Level 3 Core ``hasFeature`` and
        Aspose.HTML .NET ``DOMImplementation.HasFeature(string, string)``.

        Examples
        --------
        >>> from aspose_html.dom import DOMImplementation
        >>> impl = DOMImplementation()
        >>> impl.has_feature("Core")
        True
        >>> impl.has_feature("XML", "3.0")
        True
        >>> impl.has_feature("Unknown", "1.0")
        False
        """
        normalized_feature = feature.strip().lower()
        normalized_version = "" if version is None else version.strip()

        if normalized_feature not in {"core", "xml", "html", "xhtml"}:
            return False
        if normalized_version in {"", "1.0", "2.0", "3.0"}:
            return True
        return False

    def create_document_type(
        self,
        qualified_name: str,
        public_id: str,
        system_id: str,
    ) -> "DocumentType":
        """Create a DocumentType node with baseline validation semantics.

        Examples
        --------
        >>> from aspose_html.dom import DOMImplementation
        >>> impl = DOMImplementation()
        >>> dt = impl.create_document_type("html", "", "")
        >>> dt.name
        'html'
        >>> dt.public_id
        ''
        >>> dt.system_id
        ''
        """
        from aspose_html.dom._document_type import DocumentType

        _validate_doctype_name(qualified_name)
        return DocumentType(qualified_name, public_id, system_id)

    def create_document(
        self,
        namespace: str | None,
        qualified_name: str,
        doctype: "DocumentType | None",
    ) -> "Document":
        """Create a Document with optional doctype and root baseline wiring.

        Examples
        --------
        >>> from aspose_html.dom import DOMImplementation
        >>> impl = DOMImplementation()
        >>> dt = impl.create_document_type("html", "", "")
        >>> doc = impl.create_document("http://www.w3.org/1999/xhtml", "html", dt)
        >>> doc.document_type is dt
        True
        >>> doc.document_element.tag_name
        'HTML'
        """
        from aspose_html.dom._document import Document

        doc = Document()

        if doctype is not None:
            if doctype.owner_document is not None and doctype.owner_document is not doc:
                raise WrongDocumentError(
                    "DocumentType belongs to a different document."
                )
            _adopt(doctype, doc)
            doc.append_child(doctype)

        if qualified_name != "":
            if namespace is None:
                root = doc.create_element(qualified_name)
            else:
                root = doc.create_element_ns(namespace, qualified_name)
            doc.append_child(root)

        return doc

    def get_feature(self, feature: str, version: str | None = None) -> object | None:
        """Return this implementation for supported probes, else ``None``.

        Legacy compatibility alias for DOM Level 3 Core ``getFeature`` and
        Aspose.HTML .NET ``DOMImplementation.GetFeature(string, string)``.

        Examples
        --------
        >>> from aspose_html.dom import DOMImplementation
        >>> impl = DOMImplementation()
        >>> impl.get_feature("Core") is impl
        True
        >>> impl.has_feature("XML", "3.0")
        True
        >>> impl.get_feature("XML", "3.0") is impl
        True
        >>> impl.get_feature("Unknown", "1.0") is None
        True
        """
        if self.has_feature(feature, version):
            return self
        return None

    def create_html_document(self, title: str | None = None) -> "Document":
        """Create a detached HTML Document with html/head/body structure.

        Examples
        --------
        >>> from aspose_html.dom import DOMImplementation
        >>> impl = DOMImplementation()
        >>> doc = impl.create_html_document()
        >>> doc.document_element is not None
        True
        >>> doc.document_element.tag_name
        'HTML'
        >>> doc.head is not None and doc.body is not None
        True
        >>> doc.title
        ''
        >>> untitled = impl.create_html_document("")
        >>> untitled.title
        ''
        >>> titled = impl.create_html_document("Hello")
        >>> titled.title
        'Hello'
        """
        from aspose_html.dom._document import Document

        doc = Document()
        html = doc.create_element("html")
        head = doc.create_element("head")
        body = doc.create_element("body")

        doc.append_child(html)
        html.append_child(head)
        html.append_child(body)

        if title:
            title_el = doc.create_element("title")
            title_el.text_content = title
            head.append_child(title_el)

        return doc
