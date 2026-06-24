"""MutationObserver API and internal mutation signal dispatcher.

Synchronous delivery is a deliberate v1.0 simplification (no event loop).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable
import weakref

from aspose_html.dom._exceptions import InvalidStateError

if TYPE_CHECKING:
    from aspose_html.dom._node import Node


@dataclass(frozen=True)
class MutationRecord:
    """One DOM mutation notification record.

    Examples
    --------
    >>> from aspose_html.dom import Document, MutationObserver
    >>> doc = Document()
    >>> root = doc.create_element("div")
    >>> _ = doc.append_child(root)
    >>> out = []
    >>> obs = MutationObserver(lambda recs, o: out.extend(recs))
    >>> obs.observe(root, child_list=True)
    >>> child = doc.create_element("span")
    >>> _ = root.append_child(child)
    >>> out[0].type
    'childList'
    """

    type: str
    target: "Node"
    added_nodes: tuple["Node", ...]
    removed_nodes: tuple["Node", ...]
    previous_sibling: "Node | None"
    next_sibling: "Node | None"
    attribute_name: str | None
    attribute_namespace: str | None
    old_value: str | None


@dataclass
class _ObserverRegistration:
    target: "Node"
    child_list: bool
    attributes: bool
    character_data: bool
    subtree: bool
    attribute_filter: frozenset[str] | None
    attribute_old_value: bool
    character_data_old_value: bool


class MutationObserver:
    """Observe DOM mutations on a target node.

    Examples
    --------
    >>> from aspose_html.dom import Document, MutationObserver
    >>> doc = Document()
    >>> root = doc.create_element("div")
    >>> _ = doc.append_child(root)
    >>> calls = []
    >>> observer = MutationObserver(lambda records, obs: calls.append(len(records)))
    >>> observer.observe(root, child_list=True)
    >>> root.append_child(doc.create_element("p"))
    <Element 'P'>
    >>> calls
    [1]
    """

    __slots__ = ("_callback", "_registrations", "_pending_records", "__weakref__")

    def __init__(
        self,
        callback: Callable[[list[MutationRecord], "MutationObserver"], None],
    ) -> None:
        """Create an observer with a mutation callback.

        Examples
        --------
        >>> from aspose_html.dom import MutationObserver
        >>> observer = MutationObserver(lambda records, obs: None)
        >>> observer.take_records()
        []
        """
        self._callback = callback
        self._registrations: list[_ObserverRegistration] = []
        self._pending_records: list[MutationRecord] = []

    def observe(
        self,
        target: "Node",
        *,
        child_list: bool = False,
        attributes: bool = False,
        character_data: bool = False,
        subtree: bool = False,
        attribute_filter: list[str] | None = None,
        attribute_old_value: bool = False,
        character_data_old_value: bool = False,
    ) -> None:
        """Start observing *target* with the given options.

        Raises
        ------
        InvalidStateError
            If *target* is detached and has no owner document.

        Examples
        --------
        >>> from aspose_html.dom import Document, MutationObserver
        >>> doc = Document()
        >>> root = doc.create_element("div")
        >>> doc.append_child(root)
        <Element 'DIV'>
        >>> seen = []
        >>> observer = MutationObserver(lambda records, obs: seen.extend(records))
        >>> observer.observe(root, child_list=True)
        >>> root.append_child(doc.create_element("span"))
        <Element 'SPAN'>
        >>> seen[0].type
        'childList'
        """
        doc = target.owner_document
        if doc is None:
            raise InvalidStateError("Cannot observe detached node without owner document.")

        # Replace registration on same target.
        self._registrations = [r for r in self._registrations if r.target is not target]
        self._registrations.append(
            _ObserverRegistration(
                target=target,
                child_list=child_list,
                attributes=attributes,
                character_data=character_data,
                subtree=subtree,
                attribute_filter=frozenset(attribute_filter) if attribute_filter is not None else None,
                attribute_old_value=attribute_old_value,
                character_data_old_value=character_data_old_value,
            )
        )
        doc._mutation_signal.register(self)

    def disconnect(self) -> None:
        """Stop all active observations and clear queued records.

        Examples
        --------
        >>> from aspose_html.dom import Document, MutationObserver
        >>> doc = Document()
        >>> root = doc.create_element("div")
        >>> doc.append_child(root)
        <Element 'DIV'>
        >>> seen = []
        >>> observer = MutationObserver(lambda records, obs: seen.extend(records))
        >>> observer.observe(root, child_list=True)
        >>> observer.disconnect()
        >>> root.append_child(doc.create_element("span"))
        <Element 'SPAN'>
        >>> seen
        []
        """
        docs: set[object] = set()
        for reg in self._registrations:
            doc = reg.target.owner_document
            if doc is not None and doc not in docs:
                docs.add(doc)
                doc._mutation_signal.unregister(self)
        self._registrations.clear()
        self._pending_records.clear()

    def take_records(self) -> list[MutationRecord]:
        """Return queued records and clear the internal queue.

        Examples
        --------
        >>> from aspose_html.dom import Document, MutationObserver
        >>> doc = Document()
        >>> root = doc.create_element("div")
        >>> doc.append_child(root)
        <Element 'DIV'>
        >>> observer = MutationObserver(lambda records, obs: None)
        >>> observer.take_records()
        []
        """
        records = list(self._pending_records)
        self._pending_records.clear()
        return records


class _MutationSignal:
    """Per-document dispatcher for MutationObserver callbacks."""

    __slots__ = ("_observers", "_ranges")

    def __init__(self) -> None:
        self._observers: list[weakref.ref[MutationObserver]] = []
        self._ranges: weakref.WeakSet[object] = weakref.WeakSet()

    def register(self, observer: MutationObserver) -> None:
        """Register an observer weakly for this document."""
        for ref in self._observers:
            if ref() is observer:
                return
        self._observers.append(weakref.ref(observer))

    def unregister(self, observer: MutationObserver) -> None:
        """Unregister an observer if present."""
        live: list[weakref.ref[MutationObserver]] = []
        for ref in self._observers:
            ob = ref()
            if ob is None:
                continue
            if ob is observer:
                continue
            live.append(ref)
        self._observers = live

    def notify_child_list(
        self,
        target: "Node",
        added: tuple["Node", ...],
        removed: tuple["Node", ...],
        previous_sibling: "Node | None",
        next_sibling: "Node | None",
    ) -> None:
        """Notify observers about child-list mutation."""
        self._notify_ranges_child_list(target, added, removed, previous_sibling, next_sibling)
        deliveries: list[MutationObserver] = []
        for observer, reg in self._iter_matching(target):
            if not reg.child_list:
                continue
            observer._pending_records.append(
                MutationRecord(
                    type="childList",
                    target=target,
                    added_nodes=added,
                    removed_nodes=removed,
                    previous_sibling=previous_sibling,
                    next_sibling=next_sibling,
                    attribute_name=None,
                    attribute_namespace=None,
                    old_value=None,
                )
            )
            if observer not in deliveries:
                deliveries.append(observer)
        self._deliver(deliveries)

    def notify_attribute(
        self,
        target: "Node",
        attr_name: str,
        attr_namespace: "str | None",
        old_value: "str | None",
    ) -> None:
        """Notify observers about attribute mutation."""
        deliveries: list[MutationObserver] = []
        for observer, reg in self._iter_matching(target):
            if not reg.attributes:
                continue
            if reg.attribute_filter is not None and attr_name not in reg.attribute_filter:
                continue
            observer._pending_records.append(
                MutationRecord(
                    type="attributes",
                    target=target,
                    added_nodes=(),
                    removed_nodes=(),
                    previous_sibling=None,
                    next_sibling=None,
                    attribute_name=attr_name,
                    attribute_namespace=attr_namespace,
                    old_value=old_value if reg.attribute_old_value else None,
                )
            )
            if observer not in deliveries:
                deliveries.append(observer)
        self._deliver(deliveries)

    def notify_character_data(self, target: "Node", old_value: "str | None") -> None:
        """Notify observers about character data mutation."""
        self._notify_ranges_character_data(target)
        deliveries: list[MutationObserver] = []
        for observer, reg in self._iter_matching(target):
            if not reg.character_data:
                continue
            observer._pending_records.append(
                MutationRecord(
                    type="characterData",
                    target=target,
                    added_nodes=(),
                    removed_nodes=(),
                    previous_sibling=None,
                    next_sibling=None,
                    attribute_name=None,
                    attribute_namespace=None,
                    old_value=old_value if reg.character_data_old_value else None,
                )
            )
            if observer not in deliveries:
                deliveries.append(observer)
        self._deliver(deliveries)

    def _iter_matching(self, target: "Node") -> list[tuple[MutationObserver, _ObserverRegistration]]:
        live_refs: list[weakref.ref[MutationObserver]] = []
        matches: list[tuple[MutationObserver, _ObserverRegistration]] = []
        for ref in self._observers:
            observer = ref()
            if observer is None:
                continue
            live_refs.append(ref)
            for reg in observer._registrations:
                if reg.target is target:
                    matches.append((observer, reg))
                    continue
                if reg.subtree and self._is_descendant_or_self(target, reg.target):
                    matches.append((observer, reg))
        self._observers = live_refs
        return matches

    @staticmethod
    def _is_descendant_or_self(node: "Node", ancestor: "Node") -> bool:
        cur: Node | None = node
        while cur is not None:
            if cur is ancestor:
                return True
            cur = cur.parent_node
        return False

    @staticmethod
    def _owner_document_for(target: "Node") -> object | None:
        doc = target.owner_document
        if doc is not None:
            return doc
        if target.node_type == 9:
            return target
        return None

    def _notify_ranges_child_list(
        self,
        target: "Node",
        added: tuple["Node", ...],
        removed: tuple["Node", ...],
        previous_sibling: "Node | None",
        next_sibling: "Node | None",
    ) -> None:
        doc = self._owner_document_for(target)
        ranges = getattr(doc, "_ranges", None) if doc is not None else None
        if not ranges:
            return
        for range_obj in tuple(ranges):
            range_obj._handle_child_list_mutation(  # noqa: SLF001
                target,
                added,
                removed,
                previous_sibling,
                next_sibling,
            )

    def _notify_ranges_character_data(self, target: "Node") -> None:
        doc = self._owner_document_for(target)
        ranges = getattr(doc, "_ranges", None) if doc is not None else None
        if not ranges:
            return
        for range_obj in tuple(ranges):
            range_obj._handle_character_data_mutation(target)  # noqa: SLF001

    @staticmethod
    def _deliver(deliveries: list[MutationObserver]) -> None:
        for observer in deliveries:
            if not observer._pending_records:
                continue
            records = list(observer._pending_records)
            observer._callback(records, observer)
            observer._pending_records.clear()
