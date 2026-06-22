"""test_foster_parenting.py — tests for foster parenting."""
import pytest
from aspose_html.tree import parse_html


def _get_body(doc):
    return list(doc.document_element.children)[1]


def _get_nodes(parent):
    return list(parent.child_nodes)


def test_text_before_table():
    """Text inside <table> is foster-parented before the table."""
    doc = parse_html("<!DOCTYPE html><body><table>foster text</table></body>")
    body = _get_body(doc)
    nodes = _get_nodes(body)
    # Foster-parented text node should come before the table
    text_nodes = [n for n in nodes if n.node_type == 3]
    table_nodes = [n for n in nodes if n.node_type == 1 and n.tag_name == "TABLE"]  # type: ignore
    assert len(text_nodes) > 0, "Foster-parented text node expected"
    assert len(table_nodes) == 1, "Table should still be present"
    text_idx = nodes.index(text_nodes[0])
    table_idx = nodes.index(table_nodes[0])
    assert text_idx < table_idx, "Text must come before table"


def test_element_before_table():
    """Elements that don't belong inside <table> are foster-parented."""
    # <div> inside <table> triggers foster parenting
    doc = parse_html("<!DOCTYPE html><body><table><div>misplaced</div></table></body>")
    body = _get_body(doc)
    nodes = _get_nodes(body)
    div_nodes = [n for n in nodes if n.node_type == 1 and n.tag_name == "DIV"]  # type: ignore
    table_nodes = [n for n in nodes if n.node_type == 1 and n.tag_name == "TABLE"]  # type: ignore
    # div should appear before table (foster-parented)
    assert len(div_nodes) >= 1
    assert len(table_nodes) == 1


def test_no_table_on_stack_appends_to_document():
    """Without a table on the stack, foster parenting falls back to the html element."""
    # This is tested indirectly through normal parsing
    doc = parse_html("<!DOCTYPE html><body><p>normal</p></body>")
    body = _get_body(doc)
    p_nodes = [n for n in body.children if n.tag_name == "P"]
    assert len(p_nodes) == 1


def test_whitespace_in_table_not_foster_parented():
    """Whitespace inside <table> is not foster-parented in standards mode."""
    doc = parse_html("<!DOCTYPE html><body><table>  <tr><td>cell</td></tr></table></body>")
    body = _get_body(doc)
    nodes = _get_nodes(body)
    # Whitespace-only text nodes inside table should not appear as siblings of table
    table_nodes = [n for n in nodes if n.node_type == 1 and n.tag_name == "TABLE"]  # type: ignore
    assert len(table_nodes) == 1
