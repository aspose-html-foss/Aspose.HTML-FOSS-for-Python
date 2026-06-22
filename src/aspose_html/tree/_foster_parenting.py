"""Foster parenting location — §13.2.6.1.

When foster parenting is active, nodes that would normally be inserted
into a table, tbody, tfoot, thead, or tr element are instead inserted
immediately before the nearest ancestor table element, or appended to
the document if no table is in scope.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom import Document, Node
    from aspose_html.tree._open_elements import StackOfOpenElements


def get_foster_parent_location(
    open_elements: StackOfOpenElements,
    document: Document,
) -> tuple[Node, Node | None]:
    """Return the foster parent insertion location per §13.2.6.1.

    Returns a (parent, before_node) pair. The caller inserts the node
    using parent.insert_before(node, before_node) (or append_child if
    before_node is None).

    Parameters
    ----------
    open_elements : StackOfOpenElements
        The current stack of open elements.
    document : Document
        The document root (used as fallback parent if no table found).

    Returns
    -------
    tuple[Node, Node | None]
        (parent_node, reference_node) where reference_node may be None
        meaning append to parent.
    """
    # Find the last table element on the stack
    last_table = None
    last_table_idx = -1
    for i in range(len(open_elements._stack) - 1, -1, -1):
        el = open_elements._stack[i]
        if el._local_name == "table":
            last_table = el
            last_table_idx = i
            break

    if last_table is None:
        # §13.2.6.1 step 3: no table found — foster into the first element on stack
        # (which should be the html element)
        if open_elements._stack:
            return open_elements._stack[0], None
        return document, None  # type: ignore[return-value]

    # §13.2.6.1 step 4: if the last table has a parent, insert before the table
    if last_table._parent is not None:
        return last_table._parent, last_table  # type: ignore[return-value]

    # §13.2.6.1 step 5: table has no parent — insert into element immediately
    # above the last table on the stack
    if last_table_idx > 0:
        return open_elements._stack[last_table_idx - 1], None  # type: ignore[return-value]

    return document, None  # type: ignore[return-value]
