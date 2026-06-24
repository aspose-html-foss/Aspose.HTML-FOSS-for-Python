"""Public entry-point functions for the WHATWG HTML parser.

parse_html() and parse_fragment() are the primary user-facing API for
converting HTML strings to DOM trees.

: API names follow Aspose.HTML .NET naming conventions.
: Type hints and runnable docstring examples on all public functions.
"""
from __future__ import annotations

from aspose_html.dom import Document, Element, DocumentFragment
from aspose_html.tokenizer import Tokenizer
from aspose_html.tree._builder import TreeBuilder


def parse_html(
    html: str,
    *,
    base_url: str | None = None,
) -> Document:
    """Parse an HTML string and return a Document tree.

    Implements the WHATWG HTML Living Standard parsing algorithm,
    running the tokenizer and tree construction stages in sequence.

    Parameters
    ----------
    html : str
        The HTML source text. Must already be a decoded Unicode string.
        For raw bytes, use aspose_html.encoding.detect_encoding first.
    base_url : str | None
        The document base URL. Currently recorded on the Document but
        not used for URL resolution in v1.0. Defaults to None.

    Returns
    -------
    Document
        The fully constructed DOM Document tree. The document's
        parse_errors attribute contains any tokenizer and tree
        construction errors encountered.

    Raises
    ------
    TypeError
        If *html* is not a str.

    Examples
    --------
    >>> from aspose_html.tree import parse_html
    >>> doc = parse_html('<p>Hello, world!</p>')
    >>> doc.document_element.tag_name
    'HTML'
    >>> list(doc.document_element.children)[1].tag_name
    'BODY'
    """
    if not isinstance(html, str):
        raise TypeError(f"parse_html() expects a str, got {type(html).__name__}")

    tokenizer = Tokenizer(html)
    document = Document()
    if base_url is not None:
        document._url = base_url
    builder = TreeBuilder(tokenizer, document, fragment_context=None)
    builder.run()
    return document


def parse_fragment(
    html: str,
    context_element: Element | None = None,
    *,
    base_url: str | None = None,
) -> DocumentFragment:
    """Parse an HTML fragment in the context of a given element.

    Implements the fragment parsing algorithm from §13.2.8, used for
    innerHTML-style assignments.

    Parameters
    ----------
    html : str
        The HTML fragment source text.
    context_element : Element | None
        The element that provides context for parsing. Its tag_name
        determines the initial insertion mode (e.g., 'body' starts
        in IN_BODY, 'table' starts in IN_TABLE). If None, defaults
        to a <body> context.
    base_url : str | None
        The base URL. Defaults to None.

    Returns
    -------
    DocumentFragment
        A DocumentFragment containing the parsed nodes.

    Raises
    ------
    TypeError
        If *html* is not a str.

    Examples
    --------
    >>> from aspose_html.tree import parse_html, parse_fragment
    >>> doc = parse_html('<body></body>')
    >>> body = list(doc.document_element.children)[1]
    >>> frag = parse_fragment('<p>Hello</p>', body)
    >>> list(frag.child_nodes)[0].tag_name
    'P'
    """
    if not isinstance(html, str):
        raise TypeError(f"parse_fragment() expects a str, got {type(html).__name__}")

    # §13.2.8: Create a new Document node; set its compat mode to the context
    # element's node document's compat mode.
    document = Document()

    # Create a context element if not provided (default to <body>)
    if context_element is None:
        ctx = document.create_element("body")
    else:
        ctx = context_element

    tokenizer = Tokenizer(html)
    builder = TreeBuilder(tokenizer, document, fragment_context=ctx)
    builder.run()

    # §13.2.8 step 14: return the child nodes of the root html element
    # as a DocumentFragment. The html element was created in TreeBuilder
    # and all parsed nodes are direct children of it.
    frag = document.create_document_fragment()
    html_el = document.document_element
    if html_el is not None:
        for child in list(html_el.child_nodes):
            html_el.remove_child(child)
            frag.append_child(child)
    return frag
