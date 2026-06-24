"""NodeType integer constants — WHATWG DOM Standard node type values."""
from __future__ import annotations


class NodeType:
    """Integer constants for the ``node_type`` property of DOM nodes.

    Constants 5 (EntityReference) and 6 (Entity) are deprecated in DOM4
    and are not exposed.

    Examples
    --------
    >>> NodeType.ELEMENT_NODE
    1
    >>> NodeType.DOCUMENT_NODE
    9
    """

    ELEMENT_NODE: int = 1
    ATTRIBUTE_NODE: int = 2
    TEXT_NODE: int = 3
    CDATA_SECTION_NODE: int = 4
    PROCESSING_INSTRUCTION_NODE: int = 7
    COMMENT_NODE: int = 8
    DOCUMENT_NODE: int = 9
    DOCUMENT_TYPE_NODE: int = 10
    DOCUMENT_FRAGMENT_NODE: int = 11
