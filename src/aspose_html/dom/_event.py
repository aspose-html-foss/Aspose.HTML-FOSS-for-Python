"""DOM Event and CustomEvent per WHATWG DOM §2.2."""
import time


class Event:
    """A DOM event object per WHATWG DOM §2.2.

    Parameters
    ----------
    type : str
        The event type string (e.g. ``"click"``).
    bubbles : bool
        Whether the event bubbles up the ancestor chain. Default ``False``.
    cancelable : bool
        Whether the default action can be prevented. Default ``False``.

    Examples
    --------
    >>> e = Event("click", bubbles=True, cancelable=True)
    >>> e.type
    'click'
    >>> e.bubbles
    True
    """

    NONE = 0
    CAPTURING_PHASE = 1
    AT_TARGET = 2
    BUBBLING_PHASE = 3

    __slots__ = (
        "_type",
        "_bubbles",
        "_cancelable",
        "_target",
        "_current_target",
        "_event_phase",
        "_default_prevented",
        "_stop_propagation_flag",
        "_stop_immediate_propagation_flag",
        "_timestamp",
        "_dispatch",  # True while being dispatched (re-dispatch guard per WHATWG DOM §2.9.6)
    )

    def __init__(
        self,
        type: str,
        *,
        bubbles: bool = False,
        cancelable: bool = False,
    ) -> None:
        self._type: str = type
        self._bubbles: bool = bubbles
        self._cancelable: bool = cancelable
        self._target: "EventTarget | None" = None
        self._current_target: "EventTarget | None" = None
        self._event_phase: int = self.NONE
        self._default_prevented: bool = False
        self._stop_propagation_flag: bool = False
        self._stop_immediate_propagation_flag: bool = False
        self._timestamp: float = time.time()
        self._dispatch: bool = False

    @property
    def type(self) -> str:
        """The event type string.

        Examples
        --------
        >>> Event("focus").type
        'focus'
        """
        return self._type

    @property
    def bubbles(self) -> bool:
        """Whether the event bubbles.

        Examples
        --------
        >>> Event("click", bubbles=True).bubbles
        True
        >>> Event("click").bubbles
        False
        """
        return self._bubbles

    @property
    def cancelable(self) -> bool:
        """Whether the default action can be prevented.

        Examples
        --------
        >>> Event("submit", cancelable=True).cancelable
        True
        """
        return self._cancelable

    @property
    def target(self) -> "EventTarget | None":
        """The EventTarget on which the event was dispatched.

        Examples
        --------
        >>> Event("click").target is None
        True
        """
        return self._target

    @property
    def current_target(self) -> "EventTarget | None":
        """The EventTarget whose listener is currently being invoked.

        Examples
        --------
        >>> Event("click").current_target is None
        True
        """
        return self._current_target

    @property
    def event_phase(self) -> int:
        """Phase constant: NONE (0), CAPTURING_PHASE (1), AT_TARGET (2), BUBBLING_PHASE (3).

        Examples
        --------
        >>> Event("click").event_phase == Event.NONE
        True
        """
        return self._event_phase

    @property
    def default_prevented(self) -> bool:
        """Whether preventDefault() was called on a cancelable event.

        Examples
        --------
        >>> Event("click").default_prevented
        False
        """
        return self._default_prevented

    @property
    def timestamp(self) -> float:
        """Unix epoch time (seconds) at Event creation.

        Examples
        --------
        >>> isinstance(Event("click").timestamp, float)
        True
        """
        return self._timestamp

    def prevent_default(self) -> None:
        """Set default_prevented to True if the event is cancelable.

        No-op if not cancelable.

        Examples
        --------
        >>> e = Event("submit", cancelable=True)
        >>> e.prevent_default()
        >>> e.default_prevented
        True
        """
        if self._cancelable:
            self._default_prevented = True

    def stop_propagation(self) -> None:
        """Stop event propagation after all listeners on the current target finish.

        Examples
        --------
        >>> e = Event("click", bubbles=True)
        >>> e.stop_propagation()
        >>> e._stop_propagation_flag
        True
        """
        self._stop_propagation_flag = True

    def stop_immediate_propagation(self) -> None:
        """Stop propagation AND prevent remaining listeners on the current target.

        Examples
        --------
        >>> e = Event("click")
        >>> e.stop_immediate_propagation()
        >>> e._stop_propagation_flag
        True
        >>> e._stop_immediate_propagation_flag
        True
        """
        self._stop_propagation_flag = True
        self._stop_immediate_propagation_flag = True

    def init_event(self, type: str, bubbles: bool, cancelable: bool) -> None:
        """Legacy alias for pre-dispatch event initialization.

        Updates the event type and propagation flags, then resets dispatch
        state to pre-dispatch defaults.

        If the event is currently being dispatched, this method refuses to
        mutate state and returns without changes.

        Examples
        --------
        >>> e = Event("click", bubbles=False, cancelable=False)
        >>> e.init_event("submit", True, True)
        >>> (e.type, e.bubbles, e.cancelable)
        ('submit', True, True)
        >>> e.target is None and e.current_target is None
        True
        """
        if self._dispatch:
            return

        self._type = type
        self._bubbles = bubbles
        self._cancelable = cancelable
        self._target = None
        self._current_target = None
        self._event_phase = self.NONE
        self._default_prevented = False
        self._stop_propagation_flag = False
        self._stop_immediate_propagation_flag = False


class CustomEvent(Event):
    """An Event carrying an arbitrary detail payload.

    Parameters
    ----------
    type : str
        The event type string.
    bubbles : bool
        Default ``False``.
    cancelable : bool
        Default ``False``.
    detail : object
        Arbitrary caller-defined payload. Default ``None``.

    Examples
    --------
    >>> ev = CustomEvent("change", detail={"key": "val"})
    >>> ev.detail
    {'key': 'val'}
    """

    __slots__ = ("_detail",)

    def __init__(
        self,
        type: str,
        *,
        bubbles: bool = False,
        cancelable: bool = False,
        detail: object = None,
    ) -> None:
        super().__init__(type, bubbles=bubbles, cancelable=cancelable)
        self._detail: object = detail

    @property
    def detail(self) -> object:
        """Arbitrary caller-defined payload.

        Examples
        --------
        >>> CustomEvent("update", detail=42).detail
        42
        """
        return self._detail

    def init_custom_event(
        self,
        type: str,
        bubbles: bool,
        cancelable: bool,
        detail: object,
    ) -> None:
        """Legacy alias for pre-dispatch custom-event initialization.

        Updates event core fields and the custom detail payload.

        If the event is currently being dispatched, this method refuses to
        mutate state and returns without changes.

        Examples
        --------
        >>> ev = CustomEvent("change", detail={"v": 1})
        >>> ev.init_custom_event("update", True, True, {"v": 2})
        >>> (ev.type, ev.bubbles, ev.cancelable, ev.detail)
        ('update', True, True, {'v': 2})
        """
        if self._dispatch:
            return

        self.init_event(type, bubbles, cancelable)
        self._detail = detail


class PopStateEvent(Event):
    """History traversal event carrying the active entry state.

    Examples
    --------
    >>> ev = PopStateEvent(state={"page": 2})
    >>> ev.type
    'popstate'
    >>> ev.state
    {'page': 2}
    """

    __slots__ = ("_state",)

    def __init__(self, type: str = "popstate", *, state: object = None) -> None:
        super().__init__(type, bubbles=False, cancelable=False)
        self._state: object = state

    @property
    def state(self) -> object:
        """State snapshot associated with the current history entry."""
        return self._state


class HashChangeEvent(Event):
    """Same-document fragment navigation event.

    Examples
    --------
    >>> ev = HashChangeEvent(old_url="https://example.com/a#one", new_url="https://example.com/a#two")
    >>> ev.type
    'hashchange'
    >>> ev.old_url
    'https://example.com/a#one'
    >>> ev.new_url
    'https://example.com/a#two'
    """

    __slots__ = ("_old_url", "_new_url")

    def __init__(
        self,
        type: str = "hashchange",
        *,
        old_url: str = "",
        new_url: str = "",
    ) -> None:
        super().__init__(type, bubbles=False, cancelable=False)
        self._old_url = old_url
        self._new_url = new_url

    @property
    def old_url(self) -> str:
        """Absolute URL string before the fragment transition."""
        return self._old_url

    @property
    def new_url(self) -> str:
        """Absolute URL string after the fragment transition."""
        return self._new_url


# ---------------------------------------------------------------------------
# WHATWG UI Events — UIEvent and subclasses ( / )
# ---------------------------------------------------------------------------


class UIEvent(Event):
    """Base class for user-interface events (WHATWG UI Events §5.1).

    Parameters
    ----------
    type : str
        The event type string (e.g. ``"scroll"``).
    bubbles : bool
        Whether the event bubbles. Default ``False``.
    cancelable : bool
        Whether the default action can be prevented. Default ``False``.
    detail : int
        Integer detail value (event-type specific). Default ``0``.

    Examples
    --------
    >>> from aspose_html.dom._event import UIEvent
    >>> e = UIEvent("scroll", detail=3)
    >>> e.type
    'scroll'
    >>> e.detail
    3
    >>> e.view is None
    True
    """

    __slots__ = ("_detail",)

    def __init__(
        self,
        type: str,
        *,
        bubbles: bool = False,
        cancelable: bool = False,
        detail: int = 0,
    ) -> None:
        super().__init__(type, bubbles=bubbles, cancelable=cancelable)
        self._detail: int = detail

    @property
    def detail(self) -> int:
        """Integer detail value associated with the event.

        Examples
        --------
        >>> UIEvent("click", detail=2).detail
        2
        """
        return self._detail

    @property
    def view(self) -> None:
        """Always ``None`` in headless mode (Window back-reference out of scope).

        Examples
        --------
        >>> UIEvent("scroll").view is None
        True
        """
        return None


class MouseEvent(UIEvent):
    """Mouse or pointer event (WHATWG UI Events §5.2).

    Parameters
    ----------
    type : str
        The event type string (e.g. ``"click"``).
    bubbles : bool
        Default ``False``.
    cancelable : bool
        Default ``False``.
    detail : int
        Click count or other detail. Default ``0``.
    button : int
        Which button was pressed (0 = primary). Default ``0``.
    buttons : int
        Bitmask of currently pressed buttons. Default ``0``.
    client_x : int
        Horizontal coordinate relative to the viewport. Default ``0``.
    client_y : int
        Vertical coordinate relative to the viewport. Default ``0``.
    screen_x : int
        Horizontal coordinate relative to the screen. Default ``0``.
    screen_y : int
        Vertical coordinate relative to the screen. Default ``0``.
    alt_key : bool
        Whether the Alt key was active. Default ``False``.
    ctrl_key : bool
        Whether the Ctrl key was active. Default ``False``.
    meta_key : bool
        Whether the Meta key was active. Default ``False``.
    shift_key : bool
        Whether the Shift key was active. Default ``False``.
    related_target : object or None
        Secondary target (e.g. element entered/left). Default ``None``.

    Examples
    --------
    >>> from aspose_html.dom._event import MouseEvent
    >>> e = MouseEvent("click", button=0, client_x=10, client_y=20)
    >>> e.button
    0
    >>> e.client_x
    10
    """

    __slots__ = (
        "_button",
        "_buttons",
        "_client_x",
        "_client_y",
        "_screen_x",
        "_screen_y",
        "_alt_key",
        "_ctrl_key",
        "_meta_key",
        "_shift_key",
        "_related_target",
    )

    def __init__(
        self,
        type: str,
        *,
        bubbles: bool = False,
        cancelable: bool = False,
        detail: int = 0,
        button: int = 0,
        buttons: int = 0,
        client_x: int = 0,
        client_y: int = 0,
        screen_x: int = 0,
        screen_y: int = 0,
        alt_key: bool = False,
        ctrl_key: bool = False,
        meta_key: bool = False,
        shift_key: bool = False,
        related_target: object = None,
    ) -> None:
        super().__init__(type, bubbles=bubbles, cancelable=cancelable, detail=detail)
        self._button: int = button
        self._buttons: int = buttons
        self._client_x: int = client_x
        self._client_y: int = client_y
        self._screen_x: int = screen_x
        self._screen_y: int = screen_y
        self._alt_key: bool = alt_key
        self._ctrl_key: bool = ctrl_key
        self._meta_key: bool = meta_key
        self._shift_key: bool = shift_key
        self._related_target: object = related_target

    @property
    def button(self) -> int:
        """Which mouse button was pressed (0 = primary, 1 = middle, 2 = secondary)."""
        return self._button

    @property
    def buttons(self) -> int:
        """Bitmask of all currently pressed mouse buttons."""
        return self._buttons

    @property
    def client_x(self) -> int:
        """Horizontal coordinate relative to the viewport."""
        return self._client_x

    @property
    def client_y(self) -> int:
        """Vertical coordinate relative to the viewport."""
        return self._client_y

    @property
    def screen_x(self) -> int:
        """Horizontal coordinate relative to the screen."""
        return self._screen_x

    @property
    def screen_y(self) -> int:
        """Vertical coordinate relative to the screen."""
        return self._screen_y

    @property
    def offset_x(self) -> int:
        """Horizontal offset relative to the target element's padding edge (always 0)."""
        return 0

    @property
    def offset_y(self) -> int:
        """Vertical offset relative to the target element's padding edge (always 0)."""
        return 0

    @property
    def page_x(self) -> int:
        """Horizontal coordinate relative to the document (always 0 in headless mode)."""
        return 0

    @property
    def page_y(self) -> int:
        """Vertical coordinate relative to the document (always 0 in headless mode)."""
        return 0

    @property
    def alt_key(self) -> bool:
        """Whether the Alt key was active when the event fired."""
        return self._alt_key

    @property
    def ctrl_key(self) -> bool:
        """Whether the Ctrl key was active when the event fired."""
        return self._ctrl_key

    @property
    def meta_key(self) -> bool:
        """Whether the Meta key was active when the event fired."""
        return self._meta_key

    @property
    def shift_key(self) -> bool:
        """Whether the Shift key was active when the event fired."""
        return self._shift_key

    @property
    def related_target(self) -> "object | None":
        """Secondary target (e.g. element left on ``mouseover`` events)."""
        return self._related_target


class KeyboardEvent(UIEvent):
    """Keyboard event (WHATWG UI Events §5.3).

    Parameters
    ----------
    type : str
        The event type string (e.g. ``"keydown"``).
    bubbles : bool
        Default ``False``.
    cancelable : bool
        Default ``False``.
    detail : int
        Default ``0``.
    key : str
        Key value string per the UI Events KeyboardEvent key Values spec.
        Default ``""``.
    code : str
        Physical key code string (e.g. ``"Enter"``). Default ``""``.
    location : int
        Key location constant. Default ``DOM_KEY_LOCATION_STANDARD`` (``0``).
    repeat : bool
        Whether the key is held down (auto-repeat). Default ``False``.
    is_composing : bool
        Whether the event is part of a composition session. Default ``False``.
    alt_key : bool
        Default ``False``.
    ctrl_key : bool
        Default ``False``.
    meta_key : bool
        Default ``False``.
    shift_key : bool
        Default ``False``.

    Examples
    --------
    >>> from aspose_html.dom._event import KeyboardEvent
    >>> e = KeyboardEvent("keydown", key="Enter", code="Enter")
    >>> e.key
    'Enter'
    >>> e.code
    'Enter'
    """

    DOM_KEY_LOCATION_STANDARD: int = 0
    DOM_KEY_LOCATION_LEFT: int = 1
    DOM_KEY_LOCATION_RIGHT: int = 2
    DOM_KEY_LOCATION_NUMPAD: int = 3

    __slots__ = (
        "_key",
        "_code",
        "_location",
        "_repeat",
        "_is_composing",
        "_alt_key",
        "_ctrl_key",
        "_meta_key",
        "_shift_key",
    )

    def __init__(
        self,
        type: str,
        *,
        bubbles: bool = False,
        cancelable: bool = False,
        detail: int = 0,
        key: str = "",
        code: str = "",
        location: int = 0,
        repeat: bool = False,
        is_composing: bool = False,
        alt_key: bool = False,
        ctrl_key: bool = False,
        meta_key: bool = False,
        shift_key: bool = False,
    ) -> None:
        super().__init__(type, bubbles=bubbles, cancelable=cancelable, detail=detail)
        self._key: str = key
        self._code: str = code
        self._location: int = location
        self._repeat: bool = repeat
        self._is_composing: bool = is_composing
        self._alt_key: bool = alt_key
        self._ctrl_key: bool = ctrl_key
        self._meta_key: bool = meta_key
        self._shift_key: bool = shift_key

    @property
    def key(self) -> str:
        """Key value string (e.g. ``"Enter"``, ``"a"``, ``"ArrowLeft"``)."""
        return self._key

    @property
    def code(self) -> str:
        """Physical key code string (e.g. ``"Enter"``, ``"KeyA"``)."""
        return self._code

    @property
    def location(self) -> int:
        """Key location (standard, left, right, or numpad)."""
        return self._location

    @property
    def repeat(self) -> bool:
        """``True`` when the key is held down and the event is auto-repeated."""
        return self._repeat

    @property
    def is_composing(self) -> bool:
        """``True`` when the event is fired within an active IME composition."""
        return self._is_composing

    @property
    def alt_key(self) -> bool:
        """Whether the Alt key was active when the event fired."""
        return self._alt_key

    @property
    def ctrl_key(self) -> bool:
        """Whether the Ctrl key was active when the event fired."""
        return self._ctrl_key

    @property
    def meta_key(self) -> bool:
        """Whether the Meta key was active when the event fired."""
        return self._meta_key

    @property
    def shift_key(self) -> bool:
        """Whether the Shift key was active when the event fired."""
        return self._shift_key


class FocusEvent(UIEvent):
    """Focus transition event (WHATWG UI Events §5.4).

    Parameters
    ----------
    type : str
        The event type string (e.g. ``"focus"``, ``"blur"``).
    bubbles : bool
        Default ``False``.
    cancelable : bool
        Default ``False``.
    detail : int
        Default ``0``.
    related_target : object or None
        The element that is gaining or losing focus opposite to the
        current target. Always ``None`` in headless mode. Default ``None``.

    Examples
    --------
    >>> from aspose_html.dom._event import FocusEvent
    >>> e = FocusEvent("focus")
    >>> e.type
    'focus'
    >>> e.related_target is None
    True
    """

    __slots__ = ("_related_target",)

    def __init__(
        self,
        type: str,
        *,
        bubbles: bool = False,
        cancelable: bool = False,
        detail: int = 0,
        related_target: object = None,
    ) -> None:
        super().__init__(type, bubbles=bubbles, cancelable=cancelable, detail=detail)
        self._related_target: object = related_target

    @property
    def related_target(self) -> "object | None":
        """The element gaining or losing focus opposite to the current target."""
        return self._related_target


class InputEvent(UIEvent):
    """Text-input event (WHATWG Input Events Level 2 / WHATWG UI Events §5.6).

    Parameters
    ----------
    type : str
        The event type string (e.g. ``"input"``, ``"beforeinput"``).
    bubbles : bool
        Default ``False``.
    cancelable : bool
        Default ``False``.
    detail : int
        Default ``0``.
    data : str or None
        The string of characters inserted or deleted, or ``None`` for
        non-character input (e.g. deleting a word). Default ``None``.
    input_type : str
        Granular description of the change (e.g. ``"insertText"``,
        ``"deleteContentBackward"``). Default ``""``.
    is_composing : bool
        ``True`` when the event is part of a composition session. Default ``False``.

    Examples
    --------
    >>> from aspose_html.dom._event import InputEvent
    >>> e = InputEvent("input", data="a", input_type="insertText")
    >>> e.data
    'a'
    >>> e.input_type
    'insertText'
    """

    __slots__ = ("_data", "_input_type", "_is_composing")

    def __init__(
        self,
        type: str,
        *,
        bubbles: bool = False,
        cancelable: bool = False,
        detail: int = 0,
        data: "str | None" = None,
        input_type: str = "",
        is_composing: bool = False,
    ) -> None:
        super().__init__(type, bubbles=bubbles, cancelable=cancelable, detail=detail)
        self._data: "str | None" = data
        self._input_type: str = input_type
        self._is_composing: bool = is_composing

    @property
    def data(self) -> "str | None":
        """Inserted or deleted text; ``None`` for non-character changes."""
        return self._data

    @property
    def input_type(self) -> str:
        """Granular description of the input action (e.g. ``"insertText"``)."""
        return self._input_type

    @property
    def is_composing(self) -> bool:
        """``True`` when the event is fired within an active IME composition."""
        return self._is_composing


# ---------------------------------------------------------------------------
# WHATWG HTML §8.1.3.6 — ErrorEvent (direct subclass of Event, not UIEvent)
# ---------------------------------------------------------------------------


class ErrorEvent(Event):
    """Script error event (WHATWG HTML §8.1.3.6).

    Parameters
    ----------
    type : str
        The event type string (typically ``"error"``).
    bubbles : bool
        Default ``False``.
    cancelable : bool
        Default ``False``.
    message : str
        Human-readable error message. Default ``""``.
    filename : str
        URL of the script file where the error occurred. Default ``""``.
    lineno : int
        Line number where the error occurred. Default ``0``.
    colno : int
        Column number where the error occurred. Default ``0``.
    error : object or None
        The JavaScript error object. Always ``None`` in headless mode.
        Default ``None``.

    Examples
    --------
    >>> from aspose_html.dom._event import ErrorEvent
    >>> e = ErrorEvent("error", message="oops", lineno=42)
    >>> e.message
    'oops'
    >>> e.lineno
    42
    >>> e.error is None
    True
    """

    __slots__ = ("_message", "_filename", "_lineno", "_colno", "_error")

    def __init__(
        self,
        type: str,
        *,
        bubbles: bool = False,
        cancelable: bool = False,
        message: str = "",
        filename: str = "",
        lineno: int = 0,
        colno: int = 0,
        error: object = None,
    ) -> None:
        super().__init__(type, bubbles=bubbles, cancelable=cancelable)
        self._message: str = message
        self._filename: str = filename
        self._lineno: int = lineno
        self._colno: int = colno
        self._error: object = error

    @property
    def message(self) -> str:
        """Human-readable error message."""
        return self._message

    @property
    def filename(self) -> str:
        """URL of the script where the error originated."""
        return self._filename

    @property
    def lineno(self) -> int:
        """Line number where the error occurred."""
        return self._lineno

    @property
    def colno(self) -> int:
        """Column number where the error occurred."""
        return self._colno

    @property
    def error(self) -> "object | None":
        """The error object (always ``None`` in headless mode)."""
        return self._error
