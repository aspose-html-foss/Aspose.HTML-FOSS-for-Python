"""HTMLDocument — top-level public entry point for HTML parsing.

This module exposes :class:`HTMLDocument`, the primary user-facing class for
converting HTML strings or byte sequences into a WHATWG-compliant DOM tree.

See Also
--------
ADR-005-html-parse-api.md : architectural decisions for this module.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom import Document, DocumentFragment, Element


class HTMLDocument:
    """Top-level entry point for parsing HTML into a Document tree.

    Wraps the full WHATWG HTML parsing pipeline:
    encoding detection → tokenization → tree construction → DOM.

    Use the :meth:`parse` classmethod to create a Document from an HTML
    string or byte sequence.

    This class follows the Aspose.HTML .NET naming convention (INV-001).
    It is not intended to be instantiated directly.

    Examples
    --------
    >>> from aspose_html.html_document import HTMLDocument
    >>> doc = HTMLDocument.parse('<p>Hello</p>')
    >>> doc.document_element.tag_name
    'HTML'
    """

    @classmethod
    def parse(
        cls,
        html: str | bytes,
        *,
        encoding: str | None = None,
        base_url: str | None = None,
    ) -> "Document":
        """Parse HTML and return a Document tree.

        Parameters
        ----------
        html : str | bytes
            The HTML source. If ``bytes``, encoding is detected automatically
            using the WHATWG encoding sniff sequence (BOM → override → prescan
            → UTF-8 default). If ``str``, the string is parsed directly.
        encoding : str | None
            Optional encoding override (WHATWG label, e.g. ``"utf-8"``,
            ``"latin1"``). Accepted only when *html* is ``bytes``. When
            *html* is a ``str``, this parameter must be ``None``; passing a
            non-None value raises ``TypeError``.
        base_url : str | None
            The document base URL. Stored on the ``Document`` but not used
            for URL resolution in v1.0. Defaults to ``None``.

        Returns
        -------
        Document
            The fully constructed DOM Document tree.
            ``document.parse_errors`` contains any parse errors.

        Raises
        ------
        TypeError
            If *html* is neither ``str`` nor ``bytes``.
        TypeError
            If *html* is a ``str`` and *encoding* is not ``None``.
        ValueError
            If *encoding* is not a recognised WHATWG encoding label.
        UnsupportedEncodingError
            If the detected or specified encoding has no Python codec.

        Examples
        --------
        Parse from a string:

        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.parse('<!DOCTYPE html><html><body><p>Hi</p></body></html>')
        >>> doc.document_element.tag_name
        'HTML'
        >>> list(doc.document_element.children)[1].tag_name
        'BODY'

        Parse from bytes (encoding detected automatically):

        >>> doc = HTMLDocument.parse(b'<p>caf\\xc3\\xa9</p>')
        >>> doc.document_element.tag_name
        'HTML'

        Parse from bytes with an explicit encoding override:

        >>> doc = HTMLDocument.parse(b'<p>hello</p>', encoding='utf-8')
        >>> doc.document_element.tag_name
        'HTML'
        """
        # Step 1: type guard
        if not isinstance(html, (str, bytes)):
            raise TypeError(
                f"parse() expects str or bytes, got {type(html).__name__}"
            )

        # Step 2: encoding parameter is only meaningful for bytes input
        if isinstance(html, str) and encoding is not None:
            raise TypeError(
                "encoding parameter is only valid when html is bytes; "
                "got str with encoding override"
            )

        # Step 3: if bytes, run WHATWG encoding detection pipeline (INV-004)
        # Lazy import preserves the dependency direction at module-load time.
        # See ADR-005 § Implementation Logic.
        detected_encoding: str | None = None
        if isinstance(html, bytes):
            from aspose_html.encoding import detect_encoding  # noqa: PLC0415
            result = detect_encoding(html, override_encoding=encoding)
            text = result.text
            detected_encoding = result.encoding
        else:
            text = html

        # Step 4: delegate to tree construction (INV-002 — no lossy transform)
        from aspose_html.tree import parse_html  # noqa: PLC0415
        doc = parse_html(text, base_url=base_url)
        if detected_encoding is not None:
            doc._character_set = detected_encoding
        return doc

    @classmethod
    def parse_fragment(
        cls,
        html: str | bytes,
        context_element: "Element | None" = None,
        *,
        encoding: str | None = None,
    ) -> "DocumentFragment":
        """Parse an HTML fragment and return a DocumentFragment.

        Implements the WHATWG fragment parsing algorithm (§13.2.8), used for
        innerHTML-style assignments.

        Parameters
        ----------
        html : str | bytes
            The HTML fragment source. If ``bytes``, encoding is detected
            automatically using the WHATWG encoding sniff sequence.
        context_element : Element | None
            The element that provides parsing context. Its tag_name determines
            the initial insertion mode (e.g., ``"body"`` starts in IN_BODY,
            ``"table"`` starts in IN_TABLE). If ``None``, defaults to a
            ``<body>`` context.
        encoding : str | None
            Optional encoding override. Accepted only when *html* is ``bytes``.
            When *html* is a ``str``, this must be ``None``; a non-None value
            raises ``TypeError``.

        Returns
        -------
        DocumentFragment
            A DocumentFragment containing the parsed nodes.

        Raises
        ------
        TypeError
            If *html* is neither ``str`` nor ``bytes``.
        TypeError
            If *html* is a ``str`` and *encoding* is not ``None``.
        ValueError
            If *encoding* is not a recognised WHATWG encoding label.
        UnsupportedEncodingError
            If the detected or specified encoding has no Python codec.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> frag = HTMLDocument.parse_fragment('<p>Hello</p>')
        >>> list(frag.child_nodes)[0].tag_name
        'P'
        """
        # Step 1: type guard
        if not isinstance(html, (str, bytes)):
            raise TypeError(
                f"parse_fragment() expects str or bytes, got {type(html).__name__}"
            )

        # Step 2: encoding parameter is only meaningful for bytes input
        if isinstance(html, str) and encoding is not None:
            raise TypeError(
                "encoding parameter is only valid when html is bytes; "
                "got str with encoding override"
            )

        # Step 3: bytes path — run WHATWG encoding detection pipeline (INV-004)
        if isinstance(html, bytes):
            from aspose_html.encoding import detect_encoding  # noqa: PLC0415
            result = detect_encoding(html, override_encoding=encoding)
            text = result.text
        else:
            text = html

        # Step 4: delegate to fragment parsing (INV-002)
        from aspose_html.tree import parse_fragment  # noqa: PLC0415
        return parse_fragment(text, context_element)

    @classmethod
    def load(
        cls,
        path: "str | pathlib.Path",
    ) -> "Document":
        """Load an HTML document from a file path and return a Document tree.

        Reads the file as raw bytes, runs the full WHATWG encoding detection
        pipeline (BOM sniff → prescan → UTF-8 default), then parses the
        decoded HTML. Equivalent to calling ``HTMLDocument.parse(open(path,
        'rb').read())``.

        Parameters
        ----------
        path : str | pathlib.Path
            Path to the HTML file. Relative paths are resolved against the
            current working directory.

        Returns
        -------
        Document
            The fully constructed DOM Document tree.
            ``document.parse_errors`` contains any parse errors.

        Raises
        ------
        FileNotFoundError
            If *path* does not refer to an existing file. Propagated directly
            from ``pathlib.Path.read_bytes()``.
        ValueError
            If the encoding declared in the file is not a recognised WHATWG
            encoding label. Propagated from the encoding pipeline.
        UnsupportedEncodingError
            If the detected encoding has no Python codec. Propagated from the
            encoding pipeline.

        Examples
        --------
        >>> import pathlib, tempfile
        >>> with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='wb') as f:
        ...     _ = f.write(b'<!DOCTYPE html><html><body><p>Hi</p></body></html>')
        ...     tmp = f.name
        >>> from aspose_html.html_document import HTMLDocument
        >>> doc = HTMLDocument.load(tmp)
        >>> doc.document_element.tag_name
        'HTML'
        >>> import os; os.unlink(tmp)
        """
        import pathlib  # noqa: PLC0415
        from aspose_html.encoding import detect_encoding  # noqa: PLC0415
        from aspose_html.tree import parse_html  # noqa: PLC0415

        data: bytes = pathlib.Path(path).read_bytes()
        result = detect_encoding(data)
        return parse_html(result.text)
