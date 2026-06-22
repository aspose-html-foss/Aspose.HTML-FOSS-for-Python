"""ProcessingInstruction node."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.dom._character_data import CharacterData
from aspose_html.dom._node_type import NodeType

if TYPE_CHECKING:
    from aspose_html.dom._document import Document


class ProcessingInstruction(CharacterData):
    """A processing instruction node (e.g. ``<?xml version="1.0"?>``).

    ``node_name`` returns ``target``; ``node_value`` and ``data`` both
    return the PI data.

    Examples
    --------
    >>> from aspose_html.dom import ProcessingInstruction
    >>> pi = ProcessingInstruction("xml", 'version="1.0"')
    >>> pi.target
    'xml'
    >>> pi.data
    'version="1.0"'
    >>> pi.node_name
    'xml'
    >>> pi.node_type
    7
    """

    __slots__ = ("_target",)

    def __init__(
        self,
        target: str,
        data: str = "",
        owner_document: Document | None = None,
    ) -> None:
        super().__init__(NodeType.PROCESSING_INSTRUCTION_NODE, data, owner_document)
        self._target: str = target

    @property
    def node_name(self) -> str:
        """The processing instruction target.

        Examples
        --------
        >>> from aspose_html.dom import ProcessingInstruction
        >>> pi = ProcessingInstruction("xml", "")
        >>> pi.node_name
        'xml'
        """
        return self._target

    @property
    def target(self) -> str:
        """The PI target string.

        Examples
        --------
        >>> from aspose_html.dom import ProcessingInstruction
        >>> pi = ProcessingInstruction("php", "echo 42;")
        >>> pi.target
        'php'
        """
        return self._target

    def _clone_self(self) -> ProcessingInstruction:
        return ProcessingInstruction(self._target, self._data, self._owner_document)

    def __repr__(self) -> str:
        return f"<ProcessingInstruction target={self._target!r}>"

    __str__ = __repr__
