"""AbortController and AbortSignal stubs — WHATWG HTML §8.1.3.6.

These classes provide the cancellation-signal contract used by Fetch and
other async APIs.  In headless Python there are no real async operations
to cancel, but library code that accepts ``signal`` arguments or tests
``signal.aborted`` will fail at import time or runtime without these classes.

No imports from other ``aspose_html`` subpackages are made at module level
(leaf-module constraint, consistent with ``_event.py`` and ``_range.py``).
"""


class AbortSignal:
    """Represents the signal half of an AbortController pair.

    Consumers test :attr:`aborted` and optionally read :attr:`reason`.
    The signal transitions from ``aborted=False`` to ``aborted=True``
    exactly once (monotonic). Once aborted, :attr:`reason` is fixed.

    Do not construct directly — obtain via ``AbortController().signal``.

    Examples
    --------
    >>> from aspose_html.dom import AbortController
    >>> ctrl = AbortController()
    >>> ctrl.signal.aborted
    False
    >>> ctrl.abort()
    >>> ctrl.signal.aborted
    True
    """

    __slots__ = ("_aborted", "_reason")

    def __init__(self) -> None:
        self._aborted: bool = False
        self._reason: object = None

    @property
    def aborted(self) -> bool:
        """``True`` once :meth:`AbortController.abort` has been called.

        Examples
        --------
        >>> from aspose_html.dom import AbortController
        >>> ctrl = AbortController()
        >>> ctrl.signal.aborted
        False
        >>> ctrl.abort()
        >>> ctrl.signal.aborted
        True
        """
        return self._aborted

    @property
    def reason(self) -> object:
        """The abort reason passed to :meth:`AbortController.abort`, or ``None``.

        Examples
        --------
        >>> from aspose_html.dom import AbortController
        >>> ctrl = AbortController()
        >>> ctrl.signal.reason is None
        True
        >>> ctrl.abort("timeout")
        >>> ctrl.signal.reason
        'timeout'
        """
        return self._reason

    def _do_abort(self, reason: object) -> None:
        """Set the aborted flag and reason (called only by AbortController.abort).

        Idempotent — only the first call takes effect.
        """
        if not self._aborted:
            self._aborted = True
            self._reason = reason

    def __repr__(self) -> str:
        return f"AbortSignal(aborted={self._aborted!r})"


class AbortController:
    """Controls cancellation of operations via an :class:`AbortSignal`.

    Call :meth:`abort` to signal cancellation. The paired :attr:`signal`
    transitions from ``aborted=False`` to ``aborted=True`` exactly once.

    Examples
    --------
    >>> from aspose_html.dom import AbortController
    >>> ctrl = AbortController()
    >>> ctrl.signal.aborted
    False
    >>> ctrl.signal.reason is None
    True
    >>> ctrl.abort("timeout")
    >>> ctrl.signal.aborted
    True
    >>> ctrl.signal.reason
    'timeout'
    >>> ctrl.abort("second")  # second call is a no-op
    >>> ctrl.signal.reason
    'timeout'
    """

    __slots__ = ("_signal",)

    def __init__(self) -> None:
        self._signal: AbortSignal = AbortSignal()

    @property
    def signal(self) -> AbortSignal:
        """The :class:`AbortSignal` paired with this controller.

        Examples
        --------
        >>> from aspose_html.dom import AbortController, AbortSignal
        >>> ctrl = AbortController()
        >>> isinstance(ctrl.signal, AbortSignal)
        True
        >>> ctrl.signal is ctrl.signal
        True
        """
        return self._signal

    def abort(self, reason: object = None) -> None:
        """Signal cancellation with optional *reason*.

        Calling :meth:`abort` more than once is a no-op: the signal's
        ``aborted`` flag and ``reason`` are set only on the first call.

        Parameters
        ----------
        reason:
            Any object describing why the operation was aborted.
            Defaults to ``None``.

        Examples
        --------
        >>> from aspose_html.dom import AbortController
        >>> ctrl = AbortController()
        >>> ctrl.abort()
        >>> ctrl.signal.aborted
        True
        >>> ctrl.signal.reason is None
        True
        """
        self._signal._do_abort(reason)

    def __repr__(self) -> str:
        return f"AbortController(aborted={self._signal.aborted!r})"
