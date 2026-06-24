"""DOM Parsing/Serialization interfaces: DOMParser and XMLSerializer.

Implements the programmatic APIs defined by WHATWG HTML §11.3.1 and
W3C DOM Parsing and Serialization.
"""
from __future__ import annotations

from aspose_html.dom._exceptions import NotSupportedError
from aspose_html.html_document import HTMLDocument
from aspose_html.serialiser import serialise

if False:  # pragma: no cover
    from aspose_html.dom import Document, Node


class DOMParser:
    """Parse markup strings into DOM documents.

    Currently only ``text/html`` parsing is supported.

    Examples
    --------
    >>> parser = DOMParser()
    >>> doc = parser.parse_from_string("<p>hello</p>", "text/html")
    >>> doc.body.first_element_child.tag_name
    'P'
    """

    def parse_from_string(self, string: str, type: str) -> "Document":
        """Parse *string* using the supplied MIME *type*.

        Parameters
        ----------
        string:
            Input markup.
        type:
            MIME type hint. Supported: ``"text/html"``.

        Returns
        -------
        Document
            Parsed DOM document.

        Raises
        ------
        NotSupportedError
            If *type* is an XML MIME type or any unsupported type.
        """
        if type == "text/html":
            return HTMLDocument.parse(string)

        if type in {
            "application/xml",
            "text/xml",
            "application/xhtml+xml",
            "image/svg+xml",
        }:
            raise NotSupportedError(
                "DOMParser XML parsing is not supported in this build"
            )

        raise NotSupportedError(
            f"Unsupported DOMParser type {type!r}; only 'text/html' is supported"
        )


class XMLSerializer:
    """Serialise DOM nodes to strings.

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> p = doc.create_element("p")
    >>> p.append_child(doc.create_text_node("ok"))  # doctest: +ELLIPSIS
    <...>
    >>> XMLSerializer().serialize_to_string(p)
    '<p>ok</p>'
    """

    def serialize_to_string(self, root: "Node") -> str:
        """Return the serialised string form of *root*.

        Parameters
        ----------
        root:
            The root node to serialise.

        Returns
        -------
        str
            Serialised markup/text for the given node.
        """
        return serialise(root)
