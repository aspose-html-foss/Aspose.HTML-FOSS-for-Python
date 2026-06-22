"""ActiveFormattingList — §13.2.4.3 active formatting elements list.

The list maintains formatting elements between marker sentinels.
The "reconstruct" algorithm walks back from the end to create and
insert copies of any formatting elements not currently open.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from aspose_html.dom import Element


class _Marker:
    """A formatting list marker sentinel (not an Element)."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "<MARKER>"


# Module-level singleton — the spec says there is one kind of marker
MARKER = _Marker()

# Type alias
ActiveFormattingEntry = Union["Element", _Marker]


class ActiveFormattingList:
    """The list of active formatting elements as defined in §13.2.4.3.

    Supports push, clear-to-last-marker, and the "reconstruct" algorithm.
    The list is ordered: index 0 is the oldest entry.

    Examples
    --------
    >>> from aspose_html.tree._active_formatting import ActiveFormattingList, MARKER
    >>> lst = ActiveFormattingList()
    >>> lst.push_marker()
    >>> lst.is_marker(lst[-1])
    True
    """

    __slots__ = ("_list",)

    def __init__(self) -> None:
        self._list: list[ActiveFormattingEntry] = []

    def push(self, element: Element) -> None:
        """Append element to the end.

        If the same element (by local_name + attributes) already appears
        three or more times since the last marker, replace the oldest
        duplicate per §13.2.4.3 step 2 (the "Noah's Ark" clause).
        """
        # Count duplicates since last marker
        duplicates = []
        for entry in reversed(self._list):
            if isinstance(entry, _Marker):
                break
            # Compare by local_name and attributes
            if (entry._local_name == element._local_name  # type: ignore[union-attr]
                    and _same_attributes(entry, element)):  # type: ignore[arg-type]
                duplicates.append(entry)
        if len(duplicates) >= 3:
            # Remove the oldest duplicate (last in duplicates list, since we iterated in reverse)
            oldest = duplicates[-1]
            self._list.remove(oldest)
        self._list.append(element)

    def push_marker(self) -> None:
        """Append a marker to the end."""
        self._list.append(MARKER)

    def clear_to_last_marker(self) -> None:
        """Remove entries back to and including the last marker."""
        while self._list:
            entry = self._list.pop()
            if isinstance(entry, _Marker):
                return

    def remove(self, element: Element) -> None:
        """Remove element if present. No-op otherwise."""
        try:
            self._list.remove(element)
        except ValueError:
            pass

    def replace(self, old: Element, new: Element) -> None:
        """Replace old with new at the same position."""
        idx = self._list.index(old)
        self._list[idx] = new

    def is_marker(self, entry: ActiveFormattingEntry) -> bool:
        """True if entry is the MARKER sentinel."""
        return isinstance(entry, _Marker)

    def contains(self, element: Element) -> bool:
        """True if element is in the list (not a marker)."""
        return element in self._list

    def __len__(self) -> int:
        return len(self._list)

    def __getitem__(self, idx: int) -> ActiveFormattingEntry:
        return self._list[idx]

    def __iter__(self):
        return iter(self._list)

    def reconstruct(self, tree_builder: object) -> None:
        """Reconstruct the active formatting elements per §13.2.6.4.1.

        Creates and inserts cloned elements for each non-marker entry
        after the last marker (or from the start if no marker) that is
        not already on the open elements stack.
        """
        # §13.2.6.4.1 steps
        # Step 1: If list is empty, return.
        if not self._list:
            return

        # Step 2: If the last entry is a marker or is on open elements, return.
        last = self._list[-1]
        if self.is_marker(last) or tree_builder._open_elements.contains_node(last):  # type: ignore[union-attr]
            return

        # Step 3: Let entry be the last element in the list.
        # Walk back to find the first entry that is a marker or is on the stack.
        entry_idx = len(self._list) - 1
        while entry_idx > 0:
            entry_idx -= 1
            entry = self._list[entry_idx]
            if self.is_marker(entry) or tree_builder._open_elements.contains_node(entry):  # type: ignore[union-attr]
                entry_idx += 1  # advance past marker/open to first not-found entry
                break

        # Reopen entries from entry_idx to end
        while entry_idx < len(self._list):
            entry = self._list[entry_idx]
            # Clone the formatting element
            clone = tree_builder._clone_element(entry)  # type: ignore[union-attr]
            # Insert the clone at the appropriate location
            tree_builder._insert_element(clone)  # type: ignore[union-attr]
            # Replace entry with clone
            self._list[entry_idx] = clone
            entry_idx += 1

    def __repr__(self) -> str:
        return f"ActiveFormattingList({self._list!r})"


def _same_attributes(a: Element, b: Element) -> bool:
    """True if both elements have the same set of attribute names and values."""
    attrs_a = {attr.name: attr.value for attr in a._attributes}  # type: ignore[union-attr]
    attrs_b = {attr.name: attr.value for attr in b._attributes}  # type: ignore[union-attr]
    return attrs_a == attrs_b
