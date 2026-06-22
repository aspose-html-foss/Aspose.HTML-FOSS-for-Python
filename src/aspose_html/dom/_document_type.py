"""DocumentType node."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.dom._node import Node
from aspose_html.dom._node_type import NodeType
from aspose_html.dom._exceptions import HierarchyRequestError

if TYPE_CHECKING:
    from aspose_html.dom._document import Document


class DocumentType(Node):
    """A document type declaration node (``<!DOCTYPE html>``).

    DocumentType nodes may not have children.

    Examples
    --------
    >>> from aspose_html.dom import DocumentType
    >>> dt = DocumentType("html")
    >>> dt.name
    'html'
    >>> dt.node_type
    10
    """

    __slots__ = ("_name", "_public_id", "_system_id")

    def __init__(
        self,
        name: str,
        public_id: str = "",
        system_id: str = "",
        owner_document: Document | None = None,
    ) -> None:
        super().__init__(NodeType.DOCUMENT_TYPE_NODE, owner_document)
        self._name: str = name
        self._public_id: str = public_id
        self._system_id: str = system_id

    @property
    def node_name(self) -> str:
        """The document type name.

        Examples
        --------
        >>> from aspose_html.dom import DocumentType
        >>> DocumentType("html").node_name
        'html'
        """
        return self._name

    @property
    def name(self) -> str:
        """The document type name (e.g. ``'html'``).

        Examples
        --------
        >>> from aspose_html.dom import DocumentType
        >>> DocumentType("html").name
        'html'
        """
        return self._name

    @property
    def public_id(self) -> str:
        """The public identifier string, or ``''``.

        Examples
        --------
        >>> from aspose_html.dom import DocumentType
        >>> DocumentType("html").public_id
        ''
        """
        return self._public_id

    @property
    def system_id(self) -> str:
        """The system identifier string, or ``''``.

        Examples
        --------
        >>> from aspose_html.dom import DocumentType
        >>> DocumentType("html").system_id
        ''
        """
        return self._system_id

    def _validate_insertion(
        self, node: Node, replacing: Node | None = None
    ) -> None:
        raise HierarchyRequestError("DocumentType nodes cannot have children.")

    def _clone_self(self) -> DocumentType:
        return DocumentType(
            self._name, self._public_id, self._system_id, self._owner_document
        )

    def __repr__(self) -> str:
        return f"<DocumentType {self._name!r}>"

    __str__ = __repr__
