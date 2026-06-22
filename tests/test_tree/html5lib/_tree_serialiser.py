from __future__ import annotations

import json

from aspose_html.dom import Comment, Document, DocumentFragment, DocumentType, Element, NodeType


_SVG_NS = "http://www.w3.org/2000/svg"
_MATHML_NS = "http://www.w3.org/1998/Math/MathML"


def serialise_tree(document: Document) -> str:
    """Serialise a Document into html5lib compact tree format."""
    out: list[str] = []
    for child in document.child_nodes:
        _serialise_node(child, depth=0, out=out)
    return "\n".join(out)


def serialise_fragment(root: DocumentFragment) -> str:
    """Serialise a DocumentFragment in html5lib compact format."""
    out: list[str] = []
    for child in root.child_nodes:
        _serialise_node(child, depth=0, out=out)
    return "\n".join(out)


def _line(depth: int, payload: str) -> str:
    return f"| {'  ' * depth}{payload}"


def _element_name(el: Element) -> str:
    if el.namespace_uri == _SVG_NS:
        return f"svg {el.local_name}"
    if el.namespace_uri == _MATHML_NS:
        return f"math {el.local_name}"
    return el.local_name


def _serialise_node(node, depth: int, out: list[str]) -> None:
    if node.node_type == NodeType.DOCUMENT_TYPE_NODE and isinstance(node, DocumentType):
        out.append(_line(depth, f"<!DOCTYPE {node.name}>"))
        return

    if node.node_type == NodeType.ELEMENT_NODE and isinstance(node, Element):
        out.append(_line(depth, f"<{_element_name(node)}>"))
        for attr in node.attributes:
            out.append(_line(depth + 1, f'{attr.name}={json.dumps(attr.value, ensure_ascii=False)}'))
        if node.local_name == "template" and hasattr(node, "content"):
            out.append(_line(depth + 1, "content"))
            content = node.content
            for child in content.child_nodes:
                _serialise_node(child, depth + 2, out)
        for child in node.child_nodes:
            _serialise_node(child, depth + 1, out)
        return

    if node.node_type == NodeType.TEXT_NODE:
        out.append(_line(depth, json.dumps(node.node_value or "", ensure_ascii=False)))
        return

    if node.node_type == NodeType.COMMENT_NODE and isinstance(node, Comment):
        out.append(_line(depth, f"<!-- {node.data} -->"))
        return
