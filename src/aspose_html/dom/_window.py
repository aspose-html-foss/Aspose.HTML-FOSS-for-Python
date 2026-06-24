"""Window, Navigator, Location, Console — per-Document stubs.

Support / stub classes are defined in :mod:`aspose_html.dom._window_stubs`
().  This module re-exports all of them so that existing import
paths such as ``from aspose_html.dom._window import Navigator`` continue
to work unchanged.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from aspose_html.dom._browsing_context import BrowsingContext
from aspose_html.dom._event_target import EventTarget
from aspose_html.dom._exceptions import InvalidCharacterError
from aspose_html.dom._structured_clone import (
    clone_or_raise_data_clone_error,
    transfer_or_raise_data_clone_error,
)
from aspose_html.dom._window_event_loop import WindowEventLoop
from aspose_html.dom._window_stubs import (  # noqa: F401
    _UnhandledRejectionReport,
    set_default_user_agent,
    MediaQueryList,
    Navigator,
    Location,
    Storage,
    VisualViewport,
    Screen,
    Console,
    IntersectionObserverEntry,
    IntersectionObserver,
    ResizeObserverEntry,
    ResizeObserver,
    MessagePort,
    MessageChannel,
    BroadcastChannel,
    DataCloneError,
    SubtleCrypto,
    Crypto,
    PerformanceEntry,
    PerformanceTiming,
    Performance,
    BarProp,
    _External,
)

if TYPE_CHECKING:
    from aspose_html.dom._document import Document
    from aspose_html.dom._element import Element
    from aspose_html.dom._cascade import ComputedStyleDeclaration
    from aspose_html.dom._selection import Selection


class Window(EventTarget):
    """Per-document window object with EventTarget behavior.

    >>> from aspose_html.dom import Document, Event
    >>> doc = Document()
    >>> win = doc.default_view
    >>> seen = []
    >>> win.add_event_listener("ping", lambda evt: seen.append(evt.type))
    >>> win.dispatch_event(Event("ping"))
    True
    >>> seen
    ['ping']
    """
    __slots__ = (
        "_browsing_context", "_document", "_navigator", "_location", "_console", "_history", "_custom_elements",
        "_local_storage", "_session_storage", "_screen", "_visual_viewport", "_idle_callbacks", "_next_idle_callback_id",
        "_event_loop", "_crypto", "_performance", "_closed", "onunhandledrejection",
        "_name", "_status",
    )

    def __init__(self, document: "Document") -> None:
        super().__init__()
        self._browsing_context = BrowsingContext(document)
        self._document = document
        self._navigator = Navigator()
        self._location = Location(self)
        self._console = Console()
        self._history = None
        self._custom_elements = None
        self._local_storage: Storage | None = None
        self._session_storage: Storage | None = None
        self._screen: Screen | None = None
        self._visual_viewport: VisualViewport | None = None
        self._idle_callbacks: dict[int, tuple[Callable[..., object], object | None]] = {}
        self._next_idle_callback_id: int = 0
        self._event_loop = WindowEventLoop()
        self._event_loop.register_task_source("navigation")
        self._event_loop.register_task_source("runtime-error")
        self._crypto: Crypto | None = None
        self._performance: Performance | None = None
        self._closed: bool = False
        self.onunhandledrejection: Callable[[object], object] | None = None
        self._name: str = ""
        self._status: str = ""

    @property
    def _active_timers(self) -> dict[int, tuple[Callable[..., object], tuple[object, ...], bool]]:
        return self._event_loop._active_timers

    @property
    def _timer_task_queue(self):
        return self._event_loop._timer_task_queue

    @property
    def _next_timer_id(self) -> int:
        return self._event_loop._next_timer_id
    @property
    def _navigation_lifecycle_state(self) -> str:
        return self._browsing_context.lifecycle_state

    @_navigation_lifecycle_state.setter
    def _navigation_lifecycle_state(self, value: str) -> None:
        self._browsing_context._lifecycle_state = value

    @property
    def _navigation_cleanup_marks(self) -> list[str]:
        return self._browsing_context.cleanup_marks

    @_navigation_cleanup_marks.setter
    def _navigation_cleanup_marks(self, value: list[str]) -> None:
        self._browsing_context._cleanup_marks = value

    @property
    def _navigation_epoch(self) -> int:
        return self._browsing_context.navigation_epoch

    # ------------------------------------------------------------------
    # Internal navigation lifecycle contract hooks ()
    # ------------------------------------------------------------------

    def _navigation_begin(self) -> bool:
        """Transition lifecycle ``idle|cancelled|completed -> navigating``.

        Returns ``True`` when a new navigation cycle was accepted.
        Returns ``False`` when the current state forbids beginning another
        cycle (e.g., while replacing document or parsing).
        """
        if self._navigation_lifecycle_state not in {"idle", "cancelled", "completed"}:
            return False
        return self._browsing_context.begin_navigation()

    def _navigation_cancel(self) -> None:
        """Cancel active navigation work and return to ``idle`` deterministically."""
        token = self._browsing_context.active_navigation_token
        if token is not None:
            self._event_loop.cancel(token)
        if not self._browsing_context.cancel_navigation():
            return
        self._event_loop.schedule(
            "navigation",
            "navigation-cancel",
            token=None,
            callback=self._clear_navigation_scheduled_work,
        )
        self._event_loop.schedule(
            "navigation",
            "navigation-cancel",
            token=None,
            callback=self._browsing_context.current_document._navigation_mark_complete,
        )
        self._event_loop.drain()

    def _navigation_accept_response(self) -> None:
        """Transition ``navigating -> replacing_document`` and perform cleanup."""
        token = self._browsing_context.active_navigation_token
        self._event_loop.schedule("navigation", "navigation-start", token=token, callback=self._browsing_context.accept_response)
        self._event_loop.schedule("navigation", "navigation-start", token=token, callback=self._clear_navigation_scheduled_work)
        self._event_loop.schedule(
            "navigation",
            "navigation-start",
            token=token,
            callback=self._browsing_context.current_document._navigation_prepare_replacement,
        )
        self._event_loop.schedule(
            "navigation",
            "navigation-start",
            token=token,
            callback=lambda: self._navigation_cleanup_marks.append("replace_ready"),
        )
        self._event_loop.drain()

    def _navigation_attach_document(self, document: "Document") -> None:
        """Attach/initialize the replacement document for current navigation."""
        token = self._browsing_context.active_navigation_token

        def _attach() -> None:
            self._browsing_context.attach_document(document)
            self._document = document

        self._event_loop.schedule("navigation", "document-attach", token=token, callback=_attach)
        self._event_loop.schedule(
            "navigation",
            "document-attach",
            token=token,
            callback=lambda: self._browsing_context.current_document._navigation_prepare_replacement(),
        )
        self._event_loop.drain()

    def _navigation_mark_parsing(self) -> None:
        """Transition ``replacing_document -> parsing`` after cleanup completes."""
        token = self._browsing_context.active_navigation_token
        self._event_loop.schedule("navigation", "navigation-start", token=token, callback=self._browsing_context.mark_parsing)
        self._event_loop.schedule(
            "navigation",
            "navigation-start",
            token=token,
            callback=self._browsing_context.current_document._navigation_mark_parser_started,
        )
        self._event_loop.drain()

    def _navigation_complete(self) -> None:
        """Transition ``parsing -> completed`` and finalize readyState."""
        token = self._browsing_context.active_navigation_token
        self._event_loop.schedule("navigation", "navigation-complete", token=token, callback=self._browsing_context.mark_complete)
        self._event_loop.schedule(
            "navigation",
            "navigation-complete",
            token=token,
            callback=self._browsing_context.current_document._navigation_mark_complete,
        )
        self._event_loop.drain()

    def _clear_navigation_scheduled_work(self) -> None:
        """Clear timer/idle scheduled work as lifecycle cleanup obligation."""
        self._event_loop.clear_timer_work()
        self._idle_callbacks.clear()
        self._navigation_cleanup_marks.append("scheduled_work_cleared")

    def _navigation_schedule_parser(
        self,
        parser_job: "Callable[[], None]",
        *,
        scheduler_hook: "Callable[[Callable[[], None]], None] | None" = None,
    ) -> None:
        """Schedule parser work through a single approved hook."""
        if self._navigation_lifecycle_state != "replacing_document":
            raise RuntimeError("parser scheduling requires replacing_document state")
        self._navigation_cleanup_marks.append("parser_schedule_requested")
        if scheduler_hook is None:
            scheduler_hook = lambda job: job()
        scheduler_hook(parser_job)

    def _navigation_process_response(
        self,
        *,
        response_kind: str,
        html_source: str = "",
        scheduler_hook: "Callable[[Callable[[], None]], None] | None" = None,
        parser_hook: "Callable[[str, Document], None] | None" = None,
    ) -> "Document":
        """Execute deterministic replacement + branch-specific completion path.

        response_kind:
            ``"html"`` for parser path; any other value follows media-like path.
        """
        if not self._navigation_begin():
            raise RuntimeError("navigation already active")

        self._navigation_accept_response()
        from aspose_html.dom._document import Document as _Document  # noqa: PLC0415
        replacement = _Document()
        self._navigation_attach_document(replacement)

        if response_kind.lower() != "html":
            self._navigation_cleanup_marks.append("media_like_branch")
            self._browsing_context.current_document._navigation_mark_complete()
            self._browsing_context.complete_non_html()
            return self._browsing_context.current_document

        self._navigation_cleanup_marks.append("html_branch")
        if parser_hook is None:
            from aspose_html.tree._builder import run_navigation_html_parser  # noqa: PLC0415

            parser_hook = run_navigation_html_parser

        def _run_parser() -> None:
            self._navigation_mark_parsing()
            parser_hook(html_source, self._document)
            self._navigation_complete()

        self._navigation_schedule_parser(_run_parser, scheduler_hook=scheduler_hook)
        return self._document

    def _document_dynamic_markup_intent(self, operation: str) -> None:
        """Route Document dynamic-markup lifecycle intent via BrowsingContext.

        Internal  boundary seam: Document.open/write/writeln/close must
        not own lifecycle transitions directly.
        """
        self._browsing_context.record_dynamic_markup_intent(operation)

    @property
    def document(self) -> "Document":
        return self._browsing_context.current_document

    @property
    def navigator(self) -> Navigator:
        return self._navigator

    @property
    def location(self) -> Location:
        return self._location

    @property
    def console(self) -> Console:
        return self._console

    @property
    def history(self) -> "History":
        """Per-window History singleton."""
        if self._history is None:
            from aspose_html.dom._history import History  # noqa: PLC0415
            self._history = History(self)
        return self._history

    @property
    def custom_elements(self) -> "CustomElementRegistry":
        """Per-window CustomElementRegistry singleton."""
        if self._custom_elements is None:
            from aspose_html.dom._custom_elements import CustomElementRegistry  # noqa: PLC0415
            self._custom_elements = CustomElementRegistry(self._document)
        return self._custom_elements

    @property
    def local_storage(self) -> Storage:
        """Per-Window in-memory key-value store (``localStorage`` stub).

        Returns the same :class:`Storage` instance on every access for this
        window.  The store is transient — data is lost when the object is
        garbage-collected.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ls = doc.default_view.local_storage
        >>> ls.set_item("theme", "dark")
        >>> doc.default_view.local_storage.get_item("theme")
        'dark'
        >>> doc.default_view.local_storage is doc.default_view.local_storage
        True
        """
        if self._local_storage is None:
            self._local_storage = Storage()
        return self._local_storage

    @property
    def session_storage(self) -> Storage:
        """Per-Window in-memory key-value store (``sessionStorage`` stub).

        Returns the same :class:`Storage` instance on every access for this
        window.  The store is independent from :attr:`local_storage`.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> ss = doc.default_view.session_storage
        >>> ss.set_item("token", "abc")
        >>> doc.default_view.session_storage.get_item("token")
        'abc'
        >>> doc.default_view.session_storage is doc.default_view.session_storage
        True
        """
        if self._session_storage is None:
            self._session_storage = Storage()
        return self._session_storage

    # ------------------------------------------------------------------
    # Internal microtask/Promise boundary seam ()
    # ------------------------------------------------------------------

    def _schedule_microtask_checkpoint(
        self,
        callback: "Callable[[], None]",
        *,
        token: object | None = None,
    ) -> None:
        """Queue a microtask-checkpoint intent via :class:`WindowEventLoop`.

        This is an internal contract seam only. It does **not** implement
        Promise execution or a standalone microtask queue in ``Window``.
        """
        self._event_loop.schedule_microtask_checkpoint(callback, token=token)

    # ------------------------------------------------------------------
    # Public queueMicrotask (WHATWG HTML §8.4 /  / )
    # ------------------------------------------------------------------

    def queue_microtask(self, callback: "Callable[[], None]") -> None:
        """Schedule *callback* as a microtask via the WindowEventLoop seam.

        Per WHATWG HTML §8.4. In this headless runtime, microtask callbacks
        are registered with the :class:`WindowEventLoop` scheduling seam and
        are **not** dispatched synchronously — actual callback invocation is
        deferred to a future track that implements real microtask checkpoint
        processing.

        Parameters
        ----------
        callback:
            A zero-argument callable to be enqueued. Must be callable; no
            explicit type guard is applied — a non-callable raises
            :exc:`TypeError` at Python level when the event loop attempts to
            invoke it.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> from aspose_html.dom._window import Window
        >>> doc = Document()
        >>> w = Window(doc)
        >>> w.queue_microtask(lambda: None)  # deterministic no-op
        >>> result = []
        >>> w.queue_microtask(lambda: result.append(1))
        >>> result  # not yet invoked — deferred to event loop
        []
        """
        self._event_loop.schedule_microtask_checkpoint(callback, token=None)

    def _queue_unhandled_rejection(self, reason: object) -> None:
        """Queue bounded unhandled-rejection reporting through event loop.

        The notification is never surfaced synchronously from the caller
        stack. Delivery is deferred to the event-loop boundary and is a
        deterministic no-op when the window is closed or no callable handler
        is installed.
        """
        if self._closed:
            return
        payload = _UnhandledRejectionReport(reason=reason)
        self._event_loop.schedule(
            "runtime-error",
            "unhandled-rejection",
            callback=lambda: self._dispatch_unhandled_rejection(payload),
        )

    def _dispatch_unhandled_rejection(self, payload: _UnhandledRejectionReport) -> None:
        if self._closed:
            return
        handler = self.onunhandledrejection
        if not callable(handler):
            return
        handler(payload)

    # ------------------------------------------------------------------
    # Structured clone (WHATWG HTML §2.7.5 /  / )
    # ------------------------------------------------------------------

    def structured_clone(
        self,
        value: object,
        *,
        transfer: list | None = None,
    ) -> object:
        """Return a structured-clone-compatible deep copy of ``value``.

        Per WHATWG HTML §2.7.5.  *transfer* is a keyword-only sequence of
        objects to be "transferred".  In this headless single-runtime context,
        transfer is not supported; any non-empty *transfer* list raises
        :class:`DataCloneError` for each item that is a recognized WHATWG
        transferable type.  Non-transferable items in the transfer list are
        cloned normally (plain-value transfer is a no-op copy per WHATWG §2.7.4).

        Raises :class:`DataCloneError` when *value* (or any item in *transfer*)
        cannot be structured-cloned per WHATWG HTML §2.7 policy.

        Parameters
        ----------
        value:
            The object to clone. Must be serializable by :func:`copy.deepcopy`.
        transfer:
            Optional keyword-only list of transferable objects.  When ``None``
            or ``[]``, behavior is identical to calling without *transfer*.
            When non-empty, each item is validated via the transferable-type
            policy registry and raises :class:`DataCloneError` for recognized
            WHATWG transferable types.

        Returns
        -------
        object
            A deep copy of *value*.

        Raises
        ------
        DataCloneError
            When *value* cannot be deep-copied (e.g. lambdas, generators), or
            when any item in *transfer* is a recognized WHATWG transferable type
            that cannot be transferred in a headless context.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> from aspose_html.dom._window import Window
        >>> doc = Document()
        >>> w = Window(doc)
        >>> w.structured_clone({"key": [1, 2, 3]})
        {'key': [1, 2, 3]}
        >>> w.structured_clone(42, transfer=[])
        42
        """
        if transfer:
            for item in transfer:
                transfer_or_raise_data_clone_error(item, is_in_transfer_list=True)
        return clone_or_raise_data_clone_error(value)

    # ------------------------------------------------------------------
    # Screen and viewport stubs ( Group E / )
    # ------------------------------------------------------------------

    @property
    def screen(self) -> "Screen":
        """Browser screen geometry (stub — all dimensions are zero).

        Returns the same :class:`Screen` instance on every access for this
        window.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.screen.color_depth
        24
        >>> w.screen is w.screen
        True
        """
        if self._screen is None:
            self._screen = Screen()
        return self._screen

    @property
    def visual_viewport(self) -> "VisualViewport":
        """CSSOM View visual viewport (stub — all dimensions are zero in headless mode).

        Returns a cached :class:`VisualViewport` singleton.  Always the same
        object for the lifetime of this ``Window`` instance.

        Examples
        --------
        >>> from aspose_html.html_document import HTMLDocument
        >>> w = HTMLDocument.parse('<p>x</p>').default_view
        >>> w.visual_viewport is w.visual_viewport
        True
        >>> w.visual_viewport.height
        0
        """
        if self._visual_viewport is None:
            self._visual_viewport = VisualViewport()
        return self._visual_viewport

    @property
    def inner_width(self) -> int:
        """Viewport inner width in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.inner_width
        0
        """
        return 0

    @property
    def inner_height(self) -> int:
        """Viewport inner height in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.inner_height
        0
        """
        return 0

    @property
    def outer_width(self) -> int:
        """Window outer width in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.outer_width
        0
        """
        return 0

    @property
    def outer_height(self) -> int:
        """Window outer height in CSS pixels (stub: 0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.outer_height
        0
        """
        return 0

    @property
    def scroll_x(self) -> float:
        """Horizontal scroll offset in CSS pixels (stub: 0.0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.scroll_x
        0.0
        """
        return 0.0

    @property
    def scroll_y(self) -> float:
        """Vertical scroll offset in CSS pixels (stub: 0.0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.scroll_y
        0.0
        """
        return 0.0

    @property
    def page_x_offset(self) -> float:
        """Alias for :attr:`scroll_x` (stub: 0.0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.page_x_offset == w.scroll_x
        True
        """
        return self.scroll_x

    @property
    def page_y_offset(self) -> float:
        """Alias for :attr:`scroll_y` (stub: 0.0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.page_y_offset == w.scroll_y
        True
        """
        return self.scroll_y

    @property
    def device_pixel_ratio(self) -> float:
        """Device pixel ratio (stub: 1.0).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.device_pixel_ratio
        1.0
        """
        return 1.0

    # ------------------------------------------------------------------
    # Browsing-context hierarchy and self-reference (WHATWG HTML §11.1)
    # ------------------------------------------------------------------

    @property
    def self(self) -> "Window":
        """Self-reference alias for the Window object (WHATWG HTML §11.1.1).

        Returns the Window instance itself. Equivalent to writing ``window``
        in a browser global scope. This alias is used by code that guards
        global-scope access via ``window.self``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.self is w
        True
        """
        return self

    @property
    def window(self) -> "Window":
        """Self-reference alias; same object as :attr:`self` (WHATWG HTML §11.1.1).

        Returns the Window instance itself. Both ``window.self`` and
        ``window.window`` are identical per the WHATWG HTML spec.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.window is w
        True
        """
        return self

    @property
    def closed(self) -> bool:
        """Whether the window has been closed (WHATWG HTML §11.1.2).

        Returns ``False`` until :meth:`close` is called, after which it
        returns ``True``. Reads the existing ``_closed`` slot set by
        :meth:`close`.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.closed
        False
        >>> w.close()
        >>> w.closed
        True
        """
        return self._closed

    @property
    def top(self) -> "Window":
        """Top-most window in the browsing-context chain (WHATWG HTML §11.1.3).

        In headless non-framed mode there is no parent frame, so this window
        is its own top. Returns ``self``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.top is w
        True
        """
        return self

    @property
    def parent(self) -> "Window":
        """Parent window in the browsing-context chain (WHATWG HTML §11.1.3).

        In headless non-framed mode there is no parent frame, so this window
        is its own parent. Returns ``self``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.parent is w
        True
        """
        return self

    @property
    def opener(self) -> None:
        """The window that opened this one (WHATWG HTML §11.1.3).

        Always ``None`` in headless mode — there is no opener window when a
        document is created programmatically.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.opener is None
        True
        """
        return None

    @property
    def screen_x(self) -> int:
        """Window left-edge position on the screen in CSS pixels (stub: 0).

        Per CSSOM View §9.2. In headless mode the window has no screen
        position; returns ``0`` for API parity.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.screen_x
        0
        """
        return 0

    @property
    def screen_y(self) -> int:
        """Window top-edge position on the screen in CSS pixels (stub: 0).

        Per CSSOM View §9.2. In headless mode the window has no screen
        position; returns ``0`` for API parity.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.screen_y
        0
        """
        return 0

    @property
    def screen_left(self) -> int:
        """Alias for :attr:`screen_x` (CSSOM View §9.2).

        ``screenLeft`` and ``screenX`` return the same value per the spec —
        the left-edge position of the window on the screen. Always ``0``
        in headless mode.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.screen_left
        0
        """
        return self.screen_x

    @property
    def screen_top(self) -> int:
        """Alias for :attr:`screen_y` (CSSOM View §9.2).

        ``screenTop`` and ``screenY`` return the same value per the spec —
        the top-edge position of the window on the screen. Always ``0``
        in headless mode.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.screen_top
        0
        """
        return self.screen_y

    @property
    def name(self) -> str:
        """Browsing-context name (WHATWG HTML §7.1.2).

        Returns the stored name string. Default is ``''``. Frameworks use
        this to identify named frames or windows.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.name
        ''
        >>> w.name = "sidebar"
        >>> w.name
        'sidebar'
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = str(value)

    @property
    def status(self) -> str:
        """Legacy status bar text (WHATWG HTML §11.1.1).

        The status bar is not rendered in headless mode; this property is
        provided for API compatibility only. Getter returns the stored string;
        setter stores it without effect on any real status bar.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.status
        ''
        >>> w.status = "Loading..."
        >>> w.status
        'Loading...'
        """
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = str(value)

    def print(self) -> None:
        """Request a print dialog (no-op in headless mode).

        Per WHATWG HTML §11.3.2. In a headless environment no print dialog
        is available; this method is a no-op for API compatibility.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.print()  # no-op, no exception
        """

    def stop(self) -> None:
        """Stop loading the current document (no-op in headless mode).

        Per WHATWG HTML §11.1.1. In a headless environment document loading
        is synchronous and already complete; this is a no-op.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.stop()  # no-op, no exception
        """

    def scroll(self, x: float = 0, y: float = 0, **options: object) -> None:
        """Scroll the viewport to an absolute position — no-op in headless mode.

        Per CSSOM View §5.5. Accepts the positional ``(x, y)`` form as well
        as the ``ScrollOptions`` dict keyword form (passed via ``**options``).
        In headless mode there is no rendered viewport; the call is silently
        ignored.

        Parameters
        ----------
        x:
            Target horizontal scroll offset in CSS pixels. Ignored.
        y:
            Target vertical scroll offset in CSS pixels. Ignored.
        **options:
            Optional ``ScrollOptions`` dict fields (``behavior``, ``left``,
            ``top``). Accepted for API compatibility; ignored.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.scroll(0, 0) is None
        True
        """

    def scroll_to(self, x: float = 0, y: float = 0, **options: object) -> None:
        """Scroll the viewport to an absolute position — no-op in headless mode.

        Per CSSOM View §5.5. ``scroll_to`` and ``scroll`` are synonyms in
        the WHATWG spec. Both forms are accepted and both are no-ops here.

        Parameters
        ----------
        x:
            Target horizontal scroll offset in CSS pixels. Ignored.
        y:
            Target vertical scroll offset in CSS pixels. Ignored.
        **options:
            Optional ``ScrollOptions`` dict fields. Accepted; ignored.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.scroll_to(0, 0) is None
        True
        """

    def scroll_by(self, x: float = 0, y: float = 0, **options: object) -> None:
        """Scroll the viewport by a relative delta — no-op in headless mode.

        Per CSSOM View §5.5. Offsets the current scroll position by ``(x, y)``
        in a browser; in headless mode there is no viewport so the call is
        silently ignored.

        Parameters
        ----------
        x:
            Horizontal delta in CSS pixels. Ignored.
        y:
            Vertical delta in CSS pixels. Ignored.
        **options:
            Optional ``ScrollOptions`` dict fields. Accepted; ignored.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.scroll_by(0, 0) is None
        True
        """

    # ------------------------------------------------------------------
    # Timer/task queue model ( foundational subset)
    # Delays are accepted for API parity but ignored by this headless scheduler.
    # Callbacks run only when _dispatch_timer_macrotasks(...) is called.
    # ------------------------------------------------------------------

    def set_timeout(
        self,
        callback: "Callable[..., object]",
        delay: int = 0,
        *args: object,
    ) -> int:
        """Queue a one-shot timer callback and return its handle.

        In this headless runtime, timer callbacks are queued as pending macro-tasks
        and execute deterministically only when internal dispatch is triggered.

        Parameters
        ----------
        callback:
            Any callable; ignored.
        delay:
            Delay in milliseconds; ignored.
        *args:
            Extra arguments forwarded to *callback* by browsers; ignored.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> handle = w.set_timeout(lambda: None, 1000)
        >>> isinstance(handle, int) and handle > 0
        True
        """
        return self._event_loop.schedule_timer(callback, args, repeating=False)

    def clear_timeout(self, id: int | None = None) -> None:  # noqa: A002
        """Cancel a pending one-shot timer (idempotent for unknown handles).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> handle = w.set_timeout(lambda: None, 1)
        >>> w.clear_timeout(handle)
        >>> w.clear_timeout(handle)  # repeated cancellation is allowed
        """
        if id is None:
            return
        self._event_loop.cancel_timer(id)

    def set_interval(
        self,
        callback: "Callable[..., object]",
        delay: int = 0,
        *args: object,
    ) -> int:
        """Queue a repeating timer callback and return its handle.

        In this headless runtime, interval callbacks run only when internal
        macro-task dispatch is triggered.

        Parameters
        ----------
        callback:
            Any callable; ignored.
        delay:
            Interval in milliseconds; ignored.
        *args:
            Extra arguments forwarded to *callback* by browsers; ignored.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> handle = w.set_interval(lambda: None, 500)
        >>> isinstance(handle, int) and handle > 0
        True
        """
        return self._event_loop.schedule_timer(callback, args, repeating=True)

    def clear_interval(self, id: int | None = None) -> None:  # noqa: A002
        """Cancel a pending interval timer (idempotent for unknown handles).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> handle = w.set_interval(lambda: None, 1)
        >>> w.clear_interval(handle)
        >>> w.clear_interval(99_999)  # unknown id is ignored
        """
        if id is None:
            return
        self._event_loop.cancel_timer(id)

    def _dispatch_timer_macrotasks(self, max_tasks: int | None = None) -> int:
        """Run queued timer callbacks in deterministic FIFO order.

        This internal helper is the Track-54 macro-task dispatch contract used by
        tests/integration. It processes pending timer handles from a FIFO queue,
        skips canceled handles, and re-queues active intervals after execution.
        """
        return self._event_loop.dispatch_timer_tasks(max_tasks)

    def request_animation_frame(
        self, callback: "Callable[[float], object]"
    ) -> int:
        """Request an animation frame callback (no-op stub; returns 0).

        The callback is **never** called — there is no rendering pipeline
        in a server-side context.  The returned handle is always ``0``.

        Parameters
        ----------
        callback:
            Any callable accepting a single ``float`` timestamp; ignored.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.request_animation_frame(lambda t: None)
        0
        """
        return 0

    def cancel_animation_frame(self, id: int | None = None) -> None:  # noqa: A002
        """Cancel an animation frame request (no-op stub).

        Always a no-op regardless of the *id* value.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.cancel_animation_frame(0)
        """

    def request_idle_callback(
        self,
        callback: "Callable[..., object]",
        options: object | None = None,
    ) -> int:
        """Queue an idle callback request and return a deterministic integer id.

        In headless mode there is no scheduler/event loop, so the callback is
        stored for API-shape compatibility only and is never auto-invoked.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> seen = []
        >>> idle_id = w.request_idle_callback(lambda deadline=None: seen.append(deadline))
        >>> isinstance(idle_id, int)
        True
        >>> seen
        []
        """
        idle_id = self._next_idle_callback_id
        self._next_idle_callback_id += 1
        self._idle_callbacks[idle_id] = (callback, options)
        return idle_id

    def cancel_idle_callback(self, id: int | None = None) -> None:  # noqa: A002
        """Cancel a pending idle callback request (idempotent no-op for unknown ids).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> idle_id = w.request_idle_callback(lambda *_: None)
        >>> w.cancel_idle_callback(idle_id)
        >>> w.cancel_idle_callback(idle_id)  # idempotent
        >>> w.cancel_idle_callback(10_000)   # unknown id is ignored
        """
        if id is None:
            return
        self._idle_callbacks.pop(id, None)

    # ------------------------------------------------------------------
    # Browsing-context command stubs ( / )
    # ------------------------------------------------------------------

    def open(
        self,
        url: str = "",
        target: str = "_blank",
        features: str = "",
    ) -> None:
        """No-op browsing-context command stub per WHATWG HTML §8.8.2.

        In browsers, ``window.open(...)`` may create or target another
        browsing context and can return a Window proxy. In this headless
        runtime, browsing-context creation/navigation is out of scope,
        so this method is a deterministic no-op and always returns
        ``None``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.open() is None
        True
        >>> w.open("https://example.com", "_self", "noopener") is None
        True
        """
        return None

    def close(self) -> None:
        """No-op browsing-context command stub per WHATWG HTML §8.8.1.

        In a browser this closes the current top-level browsing context.
        In this headless runtime there is nothing to close, so the method
        is a deterministic no-op returning ``None``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.close() is None
        True
        """
        self._closed = True
        return None

    def focus(self) -> None:
        """No-op browsing-context command stub.

        Browsers may give focus to this window. In this headless runtime
        focus management is not modeled, so this method is a deterministic
        no-op returning ``None``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.focus() is None
        True
        """
        return None

    def blur(self) -> None:
        """No-op browsing-context command stub.

        Browsers may remove focus from this window. In this headless
        runtime focus state is not modeled, so this method is a
        deterministic no-op returning ``None``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.blur() is None
        True
        """
        return None

    # ------------------------------------------------------------------
    # Dialog stubs ( Group E / )
    # ------------------------------------------------------------------

    def alert(self, message: str = "") -> None:
        """No-op dialog stub per WHATWG HTML §8.5.1.

        In a browser this displays a modal alert dialog. In this
        headless library it does nothing and returns ``None``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.alert("Hello") is None
        True
        >>> w.alert() is None
        True
        """

    def confirm(self, message: str = "") -> bool:
        """No-op dialog stub per WHATWG HTML §8.5.1.

        Always returns ``False`` — no user interaction is possible
        in a headless server-side context.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.confirm("Are you sure?")
        False
        >>> w.confirm()
        False
        """
        return False

    def prompt(self, message: str = "", default: str = "") -> str | None:
        """No-op dialog stub per WHATWG HTML §8.5.1.

        Always returns ``None`` — no user interaction is possible
        in a headless server-side context.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.prompt("Enter name") is None
        True
        >>> w.prompt() is None
        True
        """
        return None

    # ------------------------------------------------------------------
    # CSSOM View stubs ( Group E / )
    # ------------------------------------------------------------------

    def get_computed_style(
        self,
        element: "Element",
        pseudo_elt: str | None = None,
    ) -> "ComputedStyleDeclaration":
        """Return the computed style for *element*.

        Delegates to the existing cascade pipeline
        (``element.get_computed_style()``). The ``pseudo_elt``
        argument is accepted for API compatibility but ignored —
        pseudo-element computed styles are not supported.

        Per CSSOM View Module §4.1.

        Parameters
        ----------
        element:
            The DOM element whose computed style to return.
        pseudo_elt:
            Optional pseudo-element selector (e.g. ``'::before'``).
            Accepted but ignored in this implementation.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> doc = HTMLDocument.parse(
        ...     '<style>p { color: red; }</style><p id="x">hi</p>'
        ... )
        >>> el = doc.get_element_by_id("x")
        >>> cs = doc.default_view.get_computed_style(el)
        >>> cs.get_property_value("color")
        'red'
        """
        return element.get_computed_style()

    def match_media(self, query: str) -> "MediaQueryList":
        """Return a :class:`MediaQueryList` for *query*.

        :attr:`~MediaQueryList.matches` reflects the current baseline
        media environment (see
        :data:`~aspose_html.dom._cascade._MEDIA_BASELINE_ENV`).
        By default the environment is ``screen`` +
        ``prefers-color-scheme: light``.

        Per CSSOM View Module §4.3.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.match_media("screen").matches
        True
        >>> w.match_media("print").matches
        False
        >>> w.match_media("screen").media
        'screen'
        """
        return MediaQueryList(query)

    @property
    def IntersectionObserver(self) -> type[IntersectionObserver]:
        """Constructor reference for :class:`IntersectionObserver`.

        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.IntersectionObserver is IntersectionObserver
        True
        """
        return IntersectionObserver

    @property
    def ResizeObserver(self) -> type[ResizeObserver]:
        """Constructor reference for :class:`ResizeObserver`.

        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.ResizeObserver is ResizeObserver
        True
        """
        return ResizeObserver

    @property
    def MessagePort(self) -> type[MessagePort]:
        """Constructor reference for :class:`MessagePort`.

        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.MessagePort is MessagePort
        True
        """
        return MessagePort

    @property
    def MessageChannel(self) -> type[MessageChannel]:
        """Constructor reference for :class:`MessageChannel`.

        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.MessageChannel is MessageChannel
        True
        """
        return MessageChannel

    @property
    def BroadcastChannel(self) -> type[BroadcastChannel]:
        """Constructor reference for :class:`BroadcastChannel`.

        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.BroadcastChannel is BroadcastChannel
        True
        """
        return BroadcastChannel

    # ------------------------------------------------------------------
    # Crypto (W3C Web Cryptography API §10.1 /  / )
    # ------------------------------------------------------------------

    @property
    def crypto(self) -> "Crypto":
        """Return the per-window :class:`Crypto` object stub.

        Per W3C Web Crypto API §10.1.  The same instance is returned on
        every access (cached in ``_crypto`` slot).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> from aspose_html.dom._window import Window
        >>> doc = Document()
        >>> w = Window(doc)
        >>> w.crypto is w.crypto
        True
        """
        if self._crypto is None:
            self._crypto = Crypto()
        return self._crypto

    @property
    def Crypto(self) -> type["Crypto"]:
        """Constructor reference for :class:`Crypto`.

        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.Crypto is Crypto
        True
        """
        return Crypto

    # ------------------------------------------------------------------
    # Performance (W3C HR Time Level 2 /  / )
    # ------------------------------------------------------------------

    @property
    def performance(self) -> "Performance":
        """Return the per-window :class:`Performance` object.

        Per W3C HR Time Level 2 §5.  The same instance is returned on every
        access (cached in ``_performance`` slot).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> from aspose_html.dom._window import Window
        >>> doc = Document()
        >>> w = Window(doc)
        >>> w.performance is w.performance
        True
        >>> isinstance(w.performance.now(), float)
        True
        """
        if self._performance is None:
            self._performance = Performance()
        return self._performance

    @property
    def Performance(self) -> type["Performance"]:
        """Constructor reference for :class:`Performance`.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.Performance is Performance
        True
        """
        return Performance

    def get_selection(self) -> "Selection":
        """Return the :class:`~aspose_html.dom.Selection` for this window's document.

        Delegates to :meth:`~aspose_html.dom.Document.get_selection`. The same
        ``Selection`` instance is returned on every call.

        Per WHATWG HTML §7.5.2.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> from aspose_html.dom._window import Window
        >>> doc = Document()
        >>> w = Window(doc)
        >>> sel = w.get_selection()
        >>> sel is doc.get_selection()
        True
        """
        return self.document.get_selection()

    # ------------------------------------------------------------------
    #  — Window IDL tail ( / )
    # ------------------------------------------------------------------

    @property
    def frames(self) -> "Window":
        """Return ``self`` — headless context has no frame children (WHATWG HTML §7.7.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.frames is w
        True
        """
        return self

    @property
    def length(self) -> int:
        """Number of browsing-context child frames; always ``0`` in headless (WHATWG HTML §7.7.1).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.length
        0
        """
        return 0

    def post_message(self, message: object, target_origin: str = "*",
                     transfer: object = ()) -> None:
        """No-op stub — headless delivery semantics not supported (WHATWG HTML §7.7.5).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.post_message("hello") is None
        True
        """

    def find(self, aString: str = "", aCaseSensitive: bool = False,
             aBackwards: bool = False, aWrapAround: bool = False,
             aWholeWord: bool = False, aSearchInFrames: bool = False,
             aShowDialog: bool = False) -> bool:
        """Always returns ``False`` — headless find-in-page is not supported (WHATWG HTML §9.2.6).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.find("text")
        False
        """
        return False

    def move_to(self, x: int, y: int) -> None:
        """No-op stub — headless has no OS window to reposition (CSSOM View §11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.move_to(100, 200) is None
        True
        """

    def move_by(self, dx: int, dy: int) -> None:
        """No-op stub — headless has no OS window to move (CSSOM View §11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.move_by(10, 10) is None
        True
        """

    def resize_to(self, width: int, height: int) -> None:
        """No-op stub — headless has no OS window to resize (CSSOM View §11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.resize_to(800, 600) is None
        True
        """

    def resize_by(self, dwidth: int, dheight: int) -> None:
        """No-op stub — headless has no OS window to resize (CSSOM View §11).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.resize_by(50, 50) is None
        True
        """

    @property
    def is_secure_context(self) -> bool:
        """Headless context is treated as secure (Secure Contexts §2).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.is_secure_context
        True
        """
        return True

    @property
    def crossorigin_isolated(self) -> bool:
        """Always ``False`` — headless environment has no cross-origin isolation (WHATWG HTML §7.2.2).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.crossorigin_isolated
        False
        """
        return False

    @property
    def origin_agent_cluster(self) -> bool:
        """Always ``False`` — headless environment has no origin-keyed agent clusters (WHATWG HTML §7.2.2).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.origin_agent_cluster
        False
        """
        return False

    @property
    def location_bar(self) -> "BarProp":
        """Location bar visibility stub; always not visible (WHATWG HTML §7.7.3).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.location_bar.visible
        False
        """
        return BarProp()

    @property
    def menu_bar(self) -> "BarProp":
        """Menu bar visibility stub; always not visible (WHATWG HTML §7.7.3).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.menu_bar.visible
        False
        """
        return BarProp()

    @property
    def personal_bar(self) -> "BarProp":
        """Personal bar visibility stub; always not visible (WHATWG HTML §7.7.3).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.personal_bar.visible
        False
        """
        return BarProp()

    @property
    def scroll_bars(self) -> "BarProp":
        """Scrollbar visibility stub; always not visible (WHATWG HTML §7.7.3).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.scroll_bars.visible
        False
        """
        return BarProp()

    @property
    def status_bar(self) -> "BarProp":
        """Status bar visibility stub; always not visible (WHATWG HTML §7.7.3).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.status_bar.visible
        False
        """
        return BarProp()

    @property
    def tool_bar(self) -> "BarProp":
        """Toolbar visibility stub; always not visible (WHATWG HTML §7.7.3).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.tool_bar.visible
        False
        """
        return BarProp()

    # ------------------------------------------------------------------
    #  — Window IDL tail ( / )
    # ------------------------------------------------------------------

    @property
    def navigation(self):
        """Navigation API — headless stub, always ``None``.

        WHATWG Navigation API §5.1: returns the ``Navigation`` object for
        this window. In headless mode no Navigation API is implemented.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().default_view.navigation is None
        True
        """
        return None

    # BarProp camelCase aliases — WHATWG HTML §7.3.4
    @property
    def locationbar(self) -> "BarProp":
        """Alias for :attr:`location_bar` — IDL camelCase name (WHATWG HTML §7.3.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().default_view.locationbar.visible
        False
        """
        return self.location_bar

    @property
    def menubar(self) -> "BarProp":
        """Alias for :attr:`menu_bar` — IDL camelCase name (WHATWG HTML §7.3.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().default_view.menubar.visible
        False
        """
        return self.menu_bar

    @property
    def personalbar(self) -> "BarProp":
        """Alias for :attr:`personal_bar` — IDL camelCase name (WHATWG HTML §7.3.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().default_view.personalbar.visible
        False
        """
        return self.personal_bar

    @property
    def scrollbars(self) -> "BarProp":
        """Alias for :attr:`scroll_bars` — IDL camelCase name (WHATWG HTML §7.3.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().default_view.scrollbars.visible
        False
        """
        return self.scroll_bars

    @property
    def statusbar(self) -> "BarProp":
        """Alias for :attr:`status_bar` — IDL camelCase name (WHATWG HTML §7.3.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().default_view.statusbar.visible
        False
        """
        return self.status_bar

    @property
    def toolbar(self) -> "BarProp":
        """Alias for :attr:`tool_bar` — IDL camelCase name (WHATWG HTML §7.3.4).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().default_view.toolbar.visible
        False
        """
        return self.tool_bar

    def atob(self, data: str) -> str:
        """Decode a base64-encoded ASCII string (WHATWG Infra §1 / HTML §8.2.3).

        Raises ``DOMException("InvalidCharacterError")`` on invalid base64 input.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.atob('aGVsbG8=')
        'hello'
        """
        import base64  # noqa: PLC0415
        cleaned = "".join(data.split())
        try:
            decoded = base64.b64decode(cleaned, validate=True)
        except Exception:
            raise InvalidCharacterError("The string to be decoded is not correctly encoded.")
        try:
            return decoded.decode("latin-1")
        except Exception:
            raise InvalidCharacterError("Decoded bytes contain non-Latin-1 characters.")

    def btoa(self, data: str) -> str:
        """Encode a string to base64 (WHATWG Infra §1 / HTML §8.2.3).

        Raises ``InvalidCharacterError`` if any character has code point > 255 (non-Latin-1).

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.btoa('hello')
        'aGVsbG8='
        """
        import base64  # noqa: PLC0415
        try:
            encoded_bytes = data.encode("latin-1")
        except (UnicodeEncodeError, UnicodeDecodeError):
            raise InvalidCharacterError(
                "The string to be encoded contains characters outside of the Latin1 range."
            )
        return base64.b64encode(encoded_bytes).decode("ascii")

    @property
    def fetch(self) -> None:
        """Always ``None`` — Fetch API (network) is not available in headless mode.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.fetch is None
        True
        """
        return None

    # ------------------------------------------------------------------
    #  — Window IDL tail ( / )
    # ------------------------------------------------------------------

    @property
    def screen_width(self) -> int:
        """Total screen width in CSS pixels (headless stub: 0).

        Per WHATWG HTML §7.6.  In a headless context no physical display
        is available; returns ``0`` for all dimension queries.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.screen_width
        0
        """
        return 0

    @property
    def screen_height(self) -> int:
        """Total screen height in CSS pixels (headless stub: 0).

        Per WHATWG HTML §7.6.  In a headless context no physical display
        is available; returns ``0`` for all dimension queries.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.screen_height
        0
        """
        return 0

    @property
    def trusted_types(self) -> None:
        """Always ``None`` — Trusted Types API is not implemented in headless mode.

        Per W3C Trusted Types §4.1 (``window.trustedTypes``).  Returns ``None``
        so feature-detection code treating it as falsy proceeds to the fallback.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.trusted_types is None
        True
        """
        return None

    @property
    def external(self) -> "_External":
        """Legacy ``window.external`` object stub (WHATWG HTML §11.5).

        Returns an ``_External`` instance whose methods are all no-ops.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> w = Document().default_view
        >>> w.external.add_search_provider('https://example.com') is None
        True
        """
        return _External()

    @property
    def speech_synthesis(self) -> None:
        """Always ``None`` — Web Speech API is not available in headless mode.

        Per W3C Web Speech API §5 (``window.speechSynthesis``).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.speech_synthesis is None
        True
        """
        return None

    @property
    def caches(self) -> None:
        """Always ``None`` — Cache Storage API is not available in headless mode.

        Per Service Workers §6.1 (``window.caches``).

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.caches is None
        True
        """
        return None

    @property
    def index_db(self) -> None:
        """Always ``None`` — IndexedDB is not available in headless mode.

        Per W3C IndexedDB §3 (``window.indexedDB``).  The property name uses
        snake_case per  Python naming conventions.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.index_db is None
        True
        """
        return None

    # ------------------------------------------------------------------
    #  — Window IDL tail ( / )
    # ------------------------------------------------------------------

    @property
    def scheduler(self):
        """Always ``None`` — no Prioritized Task Scheduling API in headless mode.

        WHATWG Scheduling APIs §2.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.scheduler is None
        True
        """
        return None

    def report_error(self, e: object = None) -> None:
        """No-op in headless mode.

        WHATWG HTML §8.2 — reports a script error to the window's error
        handling pipeline. No event loop or error handler exists in headless.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.report_error(Exception("oops"))
        """
        return

    @property
    def pub_key_credential(self):
        """Always ``None`` — no WebAuthn API in headless mode.

        Web Authentication API §2.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.pub_key_credential is None
        True
        """
        return None

    @property
    def cookie_store(self):
        """Always ``None`` — no Cookie Store API in headless mode.

        Cookie Store API §2.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.cookie_store is None
        True
        """
        return None

    @property
    def text_decoder(self):
        """Always ``None`` — TextDecoder is not exposed via the Window IDL in headless mode.

        The Encoding spec exposes TextDecoder as a global constructor; this
        IDL property returns None consistent with other absent constructor stubs.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.text_decoder is None
        True
        """
        return None

    @property
    def text_encoder(self):
        """Always ``None`` — TextEncoder is not exposed via the Window IDL in headless mode.

        Same rationale as ``text_decoder``.

        Examples
        --------
        >>> from aspose_html.dom._document import Document
        >>> Document().default_view.text_encoder is None
        True
        """
        return None
