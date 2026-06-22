"""aspose_html.tree — WHATWG HTML tree construction (§13.2.6).

Consumes token stream from aspose_html.tokenizer and builds a Document
tree using aspose_html.dom node types.

Public API
----------
- :func:`parse_html` — parse an HTML string into a Document.
- :func:`parse_fragment` — parse an HTML fragment (innerHTML-style).
- :class:`TreeBuilder` — the tree construction state machine (for testing).

See Also
--------
ADR-003-tree-construction.md : architectural decisions for this module.
"""
from aspose_html.tree._builder import TreeBuilder
from aspose_html.tree._parse import parse_html, parse_fragment

__all__ = ["TreeBuilder", "parse_html", "parse_fragment"]
