"""EventTarget — base class for objects that can receive DOM events.

Per WHATWG DOM §2.9. This module is a leaf — no runtime imports from other
aspose_html subpackages at module load time. _node.py imports from here (not
the reverse) to prevent circular imports.
"""
from __future__ import annotations

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from aspose_html.dom._event import Event


class EventTarget:
    """Base class for objects that can receive DOM events.

    Per WHATWG DOM §2.9, every ``Node`` is an ``EventTarget``.
    ``EventTarget`` can also be used standalone.

    Examples
    --------
    >>> from aspose_html.dom import EventTarget, Event
    >>> et = EventTarget()
    >>> log = []
    >>> et.add_event_listener("ping", lambda e: log.append(e.type))
    >>> et.dispatch_event(Event("ping"))
    True
    >>> log
    ['ping']
    """

    __slots__ = ("_event_listeners",)

    def __init__(self) -> None:
        # Lazily initialised to None. The dict is created only when
        # add_event_listener is first called, so nodes that never register
        # a listener pay no dict allocation cost. See ADR-040.
        # Value type changed from list[Callable] to list[tuple[Callable, bool]]
        # where the bool is the once_flag. See ADR-173.
        self._event_listeners: dict[tuple[str, bool], list[tuple[Callable, bool]]] | None = None

    def add_event_listener(
        self,
        type: str,
        listener: Callable,
        *,
        capture: bool = False,
        once: bool = False,
    ) -> None:
        """Register *listener* for events of *type*.

        Registering the same ``(type, listener, capture)`` triple twice is
        idempotent — only one copy is stored. The ``once`` flag is **not**
        part of the identity key (WHATWG DOM §2.9.4 step 5): the first
        registration wins.

        Parameters
        ----------
        type : str
            Event type string (e.g. ``"click"``).
        listener : Callable
            Callable accepting a single ``Event`` argument.
        capture : bool
            If ``True``, the listener fires during the capture phase.
        once : bool
            If ``True``, the listener is automatically removed after it fires
            for the first time.

        Raises
        ------
        TypeError
            If *listener* is not callable.

        Examples
        --------
        >>> from aspose_html.dom import Document, Event
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> calls = []
        >>> el.add_event_listener("click", lambda e: calls.append(1))
        >>> el.dispatch_event(Event("click"))
        True
        >>> calls
        [1]

        A listener registered with ``once=True`` fires exactly once:

        >>> from aspose_html.dom import EventTarget, Event
        >>> et = EventTarget()
        >>> fired = []
        >>> et.add_event_listener("foo", lambda e: fired.append(1), once=True)
        >>> _ = et.dispatch_event(Event("foo"))
        >>> _ = et.dispatch_event(Event("foo"))
        >>> fired
        [1]
        """
        if not callable(listener):
            raise TypeError(f"listener must be callable, got {type(listener).__name__!r}")

        if self._event_listeners is None:
            self._event_listeners = {}
        key = (type, capture)
        bucket = self._event_listeners.setdefault(key, [])
        # INV-005: idempotent registration per WHATWG DOM §2.9.4 step 5.
        # Identity is (type, capture, listener callable) — once flag is excluded.
        if not any(fn is listener for fn, _once in bucket):
            bucket.append((listener, once))

    def remove_event_listener(
        self,
        type: str,
        listener: Callable,
        *,
        capture: bool = False,
    ) -> None:
        """Deregister a previously-registered listener.

        No-op if the listener was not registered.

        Parameters
        ----------
        type : str
            Event type string.
        listener : Callable
            The exact callable object that was passed to ``add_event_listener``.
        capture : bool
            Must match the ``capture`` value used during registration.

        Examples
        --------
        >>> from aspose_html.dom import Document, Event
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> fn = lambda e: None
        >>> el.add_event_listener("click", fn)
        >>> el.remove_event_listener("click", fn)
        >>> el.dispatch_event(Event("click"))
        True
        """
        if self._event_listeners is None:
            return
        key = (type, capture)
        bucket = self._event_listeners.get(key)
        if bucket:
            for i, (fn, _once) in enumerate(bucket):
                if fn is listener:
                    del bucket[i]
                    break

    def dispatch_event(self, event: "Event") -> bool:
        """Dispatch *event* through the ancestor tree.

        Returns ``True`` if ``preventDefault()`` was **not** called, or
        ``False`` if it was (event was cancelled).

        Implements WHATWG DOM §2.9.6 dispatch algorithm:
        capture phase (top-down ancestors) → at-target → bubble phase
        (bottom-up ancestors, only if event.bubbles).

        Parameters
        ----------
        event : Event
            The event object to dispatch. Must not already be in dispatch.

        Raises
        ------
        ValueError
            If *event* is already being dispatched.

        Examples
        --------
        >>> from aspose_html.dom import Document, Event
        >>> doc = Document()
        >>> el = doc.create_element("div")
        >>> doc.append_child(el)
        <Element 'DIV'>
        >>> doc_calls = []
        >>> el_calls = []
        >>> doc.add_event_listener("click", lambda e: doc_calls.append(1), capture=True)
        >>> el.add_event_listener("click", lambda e: el_calls.append(1))
        >>> result = el.dispatch_event(Event("click", bubbles=True))
        >>> el_calls
        [1]
        >>> doc_calls
        [1]
        >>> result
        True
        """
        from aspose_html.dom._event import Event as _Event  # avoid cycle at module load

        # Step 1 — Re-dispatch guard per WHATWG DOM §2.9.6.
        if event._dispatch:
            raise ValueError("event is already being dispatched")
        event._dispatch = True

        # Step 2 — Set target.
        event._target = self

        # Step 3 — Build ancestor chain.
        # ancestors[0] is immediate parent; ancestors[-1] is root.
        ancestors: list[EventTarget] = []
        current = getattr(self, "_parent", None)
        while current is not None:
            ancestors.append(current)
            current = getattr(current, "_parent", None)

        capture_chain = list(reversed(ancestors))  # top-down (root first)
        bubble_chain = ancestors                   # bottom-up

        # Step 4 — Capture phase.
        event._event_phase = _Event.CAPTURING_PHASE
        for node in capture_chain:
            event._current_target = node
            node._invoke_listeners(event, capture=True)
            if event._stop_propagation_flag:
                break

        # Step 5 — At-target phase (both capture and bubble listeners).
        # WHATWG §2.9.6: stop_propagation() only halts traversal between nodes
        # in the ancestor chain — the target itself always fires unconditionally.
        event._event_phase = _Event.AT_TARGET
        event._current_target = self
        self._invoke_listeners(event, capture=True)
        if not event._stop_immediate_propagation_flag:
            self._invoke_listeners(event, capture=False)

        # Step 6 — Bubble phase (only if event.bubbles and not stopped).
        if event._bubbles and not event._stop_propagation_flag:
            event._event_phase = _Event.BUBBLING_PHASE
            for node in bubble_chain:
                event._current_target = node
                node._invoke_listeners(event, capture=False)
                if event._stop_propagation_flag:
                    break

        # Step 7 — Reset.
        event._event_phase = _Event.NONE
        event._current_target = None
        event._dispatch = False

        # Step 8 — Return.
        return not event._default_prevented

    def _invoke_listeners(self, event: "Event", *, capture: bool) -> None:
        """Invoke listeners for *event.type* in the given phase.

        Takes a snapshot of the bucket before iterating so that listeners
        added during dispatch are not invoked for the current event
        (WHATWG DOM §2.9.6 snapshot semantics).

        Parameters
        ----------
        event : Event
            The event being dispatched.
        capture : bool
            ``True`` to invoke capture-phase listeners; ``False`` for bubble.
        """
        if self._event_listeners is None:
            return
        key = (event._type, capture)
        bucket = self._event_listeners.get(key)
        if not bucket:
            return
        # Snapshot before iterating — see ADR-040 §Snapshot semantics.
        # Snapshot entries are (listener_callable, once_flag) pairs.
        for listener_fn, once_flag in list(bucket):
            if event._stop_immediate_propagation_flag:
                break
            try:
                listener_fn(event)
            except Exception:
                # INV-005 / ADR-040: exceptions in listeners must NOT halt
                # dispatch. WHATWG "report the exception" → suppress in a
                # library context without a browser error-reporting hook.
                pass
            if once_flag:
                # ADR-173: auto-remove once listeners after first invocation.
                # The bucket is the live list; the snapshot ensures this removal
                # does not affect the current dispatch iteration.
                try:
                    bucket.remove((listener_fn, True))
                except ValueError:
                    pass  # already removed by a concurrent remove_event_listener
