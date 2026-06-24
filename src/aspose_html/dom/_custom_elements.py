"""Custom Elements registry (autonomous custom elements only).

Examples
--------
>>> from aspose_html.dom import Document, HTMLElement
>>> doc = Document()
>>> reg = doc.default_view.custom_elements
>>> class MyTag(HTMLElement):
...     __slots__ = ()
>>> reg.define("my-tag", MyTag, observed_attributes=("data-x",))
>>> isinstance(doc.create_element("my-tag"), MyTag)
True
"""
from __future__ import annotations

import dataclasses
import logging
import re
from typing import TYPE_CHECKING

from aspose_html.dom._exceptions import NotSupportedError
from aspose_html.dom._node_type import NodeType

if TYPE_CHECKING:
    from aspose_html.dom._document import Document
    from aspose_html.dom._element import Element
    from aspose_html.dom._html_element import HTMLElement
    from aspose_html.dom._node import Node


_LOGGER = logging.getLogger("aspose_html.custom_elements")
_NAME_RE = re.compile(r"^[a-z][a-z0-9._\-]*-[a-z0-9._\-]*$")
_RESERVED_NAMES: frozenset[str] = frozenset({
    "annotation-xml", "color-profile", "font-face", "font-face-src",
    "font-face-uri", "font-face-format", "font-face-name", "missing-glyph",
})


def _validate_custom_element_name(name: str) -> None:
    if not isinstance(name, str):
        raise TypeError(f"name must be str, got {type(name).__name__}")
    if not _NAME_RE.match(name):
        raise SyntaxError(f"Invalid custom element name {name!r}")
    if name in _RESERVED_NAMES:
        raise SyntaxError(f"Custom element name {name!r} is reserved")


def _is_connected(element: "Element") -> bool:
    node: Node | None = element
    while node is not None:
        if node._node_type == NodeType.DOCUMENT_NODE:
            return True
        node = node._parent
    return False


def _check_slot_compatibility(constructor: type) -> None:
    """Best-effort guard for __class__ reassignment slot compatibility.

    Raises TypeError when the constructor defines non-empty __slots__.
    """
    slots = getattr(constructor, "__slots__", ())
    if isinstance(slots, str):
        slots = (slots,)
    if tuple(slots):
        raise TypeError(
            "custom element constructor must declare empty __slots__ for "
            "upgrade compatibility"
        )


@dataclasses.dataclass(slots=True)
class _Definition:
    name: str
    constructor: type
    observed_attributes: tuple[str, ...]


class CustomElementRegistry:
    __slots__ = ("_document", "_definitions", "_constructors")

    def __init__(self, document: "Document") -> None:
        self._document = document
        self._definitions: dict[str, _Definition] = {}
        self._constructors: dict[type, str] = {}

    def define(self, name: str, constructor: type, *, observed_attributes: tuple[str, ...] = ()) -> None:
        _validate_custom_element_name(name)
        if name in self._definitions:
            raise NotSupportedError(f"name already defined: {name!r}")
        if constructor in self._constructors:
            raise NotSupportedError(f"constructor already registered as {self._constructors[constructor]!r}")
        from aspose_html.dom._html_element import HTMLElement  # noqa: PLC0415
        if not isinstance(constructor, type) or not issubclass(constructor, HTMLElement):
            raise TypeError("constructor must be a subclass of HTMLElement")
        _check_slot_compatibility(constructor)
        constructor.__custom_element_observed__ = frozenset(observed_attributes)
        self._definitions[name] = _Definition(name, constructor, tuple(observed_attributes))
        self._constructors[constructor] = name
        self._drain_upgrade_queue(name)

    def get(self, name: str) -> "type[HTMLElement] | None":
        definition = self._definitions.get(name)
        return None if definition is None else definition.constructor

    def get_name(self, constructor: type) -> str | None:
        return self._constructors.get(constructor)

    def upgrade(self, root: "Node") -> None:
        stack: list[Node] = [root]
        while stack:
            node = stack.pop(0)
            if node._node_type == NodeType.ELEMENT_NODE:
                definition = self._definitions.get(node._local_name)
                if definition is not None:
                    self._upgrade_element(node, definition)
            stack[0:0] = list(node._children)

    def when_defined(self, name: str) -> str | None:
        return name if name in self._definitions else None

    def _is_observed(self, element: "Element", attr_name: str) -> bool:
        observed = getattr(type(element), "__custom_element_observed__", None)
        return observed is not None and attr_name in observed

    def _fire_attribute_changed(self, element: "Element", attr_name: str, old: str | None, new: str | None) -> None:
        callback = getattr(element, "attribute_changed_callback", None)
        if callback is None:
            return
        try:
            callback(attr_name, old, new)
        except Exception:
            _LOGGER.exception("attribute_changed_callback failed")

    def _fire_connected(self, element: "Element") -> None:
        if type(element) not in self._constructors:
            return
        callback = getattr(element, "connected_callback", None)
        if callback is None:
            return
        try:
            callback()
        except Exception:
            _LOGGER.exception("connected_callback failed")

    def _fire_disconnected(self, element: "Element") -> None:
        if type(element) not in self._constructors:
            return
        callback = getattr(element, "disconnected_callback", None)
        if callback is None:
            return
        try:
            callback()
        except Exception:
            _LOGGER.exception("disconnected_callback failed")

    def _fire_adopted(self, element: "Element", old_doc: "Document | None", new_doc: "Document") -> None:
        if type(element) not in self._constructors:
            return
        callback = getattr(element, "adopted_callback", None)
        if callback is None:
            return
        try:
            callback(old_doc, new_doc)
        except Exception:
            _LOGGER.exception("adopted_callback failed")

    def _upgrade_element(self, element: "Element", definition: _Definition) -> None:
        if isinstance(element, definition.constructor):
            return
        element.__class__ = definition.constructor
        for attr_name in definition.observed_attributes:
            value = element.get_attribute(attr_name)
            if value is not None:
                self._fire_attribute_changed(element, attr_name, None, value)
        if _is_connected(element):
            self._fire_connected(element)

    def _drain_upgrade_queue(self, name: str) -> None:
        doc = self._document
        definition = self._definitions.get(name)
        if doc is None or definition is None:
            return
        kept = []
        for element in doc._upgrade_queue_snapshot():
            if element._local_name == name:
                self._upgrade_element(element, definition)
                continue
            kept.append(element)
        doc._replace_upgrade_queue(kept)
