"""Window support / stub classes — split from _window.py (ADR-305)."""
from __future__ import annotations

import logging
import time as _time
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable
from urllib.parse import urlsplit, urlunsplit

from aspose_html.dom._event_target import EventTarget
from aspose_html.dom._exceptions import DOMException
from aspose_html.dom._structured_clone import clone_or_raise_data_clone_error
from aspose_html.dom._window_event_loop import WindowEventLoop
from aspose_html.url import URL

if TYPE_CHECKING:
    from aspose_html.dom._window import Window

_DEFAULT_USER_AGENT: str = "AsposeHTML/0.1.0 (Python; FOSS)"


@dataclass(slots=True)
class _UnhandledRejectionReport:
    """Bounded internal payload for Window unhandled rejection surfacing."""

    reason: object
    phase: str = "unhandled-rejection"
    type: str = "unhandledrejection"


def set_default_user_agent(value: str) -> None:
    """Set default user-agent string for new Navigator objects.

    >>> from aspose_html.dom._window import Navigator, set_default_user_agent
    >>> set_default_user_agent("TestUA/1.0")
    >>> Navigator().user_agent
    'TestUA/1.0'
    """
    global _DEFAULT_USER_AGENT
    if not isinstance(value, str):
        raise TypeError("user_agent must be a string")
    _DEFAULT_USER_AGENT = value


class MediaQueryList:
    """MediaQueryList returned by :meth:`Window.match_media`.

    Per CSSOM View Module §4.3. :attr:`matches` delegates to
    :func:`~aspose_html.dom._cascade._media_query_matches` which
    evaluates against the module-level baseline media environment
    (``screen`` + ``prefers-color-scheme: light`` by default).

    :meth:`add_event_listener` and :meth:`remove_event_listener` are
    no-ops — change events are never fired in a headless context.

    Examples
    --------
    >>> from aspose_html.dom._window import MediaQueryList
    >>> MediaQueryList("screen").matches
    True
    >>> MediaQueryList("print").matches
    False
    >>> MediaQueryList("(max-width: 768px)").matches
    False
    >>> MediaQueryList("(max-width: 768px)").media
    '(max-width: 768px)'
    """

    __slots__ = ("_media",)

    def __init__(self, media: str) -> None:
        self._media = media

    @property
    def matches(self) -> bool:
        """Return whether the media query matches the current baseline environment.

        Delegates to :func:`~aspose_html.dom._cascade._media_query_matches`
        which evaluates against :data:`~aspose_html.dom._cascade._MEDIA_BASELINE_ENV`.
        Re-evaluated on every access — not cached.

        Examples
        --------
        >>> from aspose_html.dom._window import MediaQueryList
        >>> MediaQueryList("screen").matches
        True
        >>> MediaQueryList("print").matches
        False
        >>> MediaQueryList("(prefers-color-scheme: light)").matches
        True
        >>> MediaQueryList("(prefers-color-scheme: dark)").matches
        False
        """
        from aspose_html.dom._cascade import _media_query_matches  # noqa: PLC0415
        return _media_query_matches(self._media)

    @property
    def media(self) -> str:
        """The media query string passed to :meth:`Window.match_media`.

        >>> MediaQueryList("print").media
        'print'
        """
        return self._media

    def add_event_listener(
        self,
        type: str,  # noqa: A002
        callback: object,
        options: object = None,
    ) -> None:
        """No-op stub — change events are never fired in this library."""

    def remove_event_listener(
        self,
        type: str,  # noqa: A002
        callback: object,
        options: object = None,
    ) -> None:
        """No-op stub — change events are never fired in this library."""


class Navigator:
    __slots__ = (
        "_user_agent", "_platform", "_language",
        "_languages", "_online", "_cookie_enabled", "_vendor",
    )

    def __init__(self) -> None:
        self._user_agent = _DEFAULT_USER_AGENT
        self._platform = "Python"
        self._language = "en"
        self._languages: tuple[str, ...] = ("en",)
        self._online = True
        self._cookie_enabled = False
        self._vendor = ""

    @property
    def user_agent(self) -> str:
        """Navigator user-agent string.

        >>> Navigator().user_agent.startswith("AsposeHTML")
        True
        """
        return self._user_agent

    @property
    def platform(self) -> str:
        """Platform identifier stub — always ``'Python'``.

        >>> Navigator().platform
        'Python'
        """
        return self._platform

    @property
    def language(self) -> str:
        """Primary language tag stub — always ``'en'``.

        >>> Navigator().language
        'en'
        """
        return self._language

    @property
    def languages(self) -> tuple[str, ...]:
        """Accepted languages sequence stub — always ``('en',)``.

        >>> Navigator().languages
        ('en',)
        """
        return self._languages

    @property
    def online(self) -> bool:
        """Network-online stub — always ``True``.

        >>> Navigator().online
        True
        """
        return self._online

    @property
    def on_line(self) -> bool:
        """Always ``True`` in headless mode.

        WHATWG HTML §8.8 ``navigator.onLine`` IDL attribute.
        Headless environments have no network state; always reports online.
        This is the snake_case IDL alias for :attr:`online`.

        >>> Navigator().on_line
        True
        """
        return True

    @property
    def cookie_enabled(self) -> bool:
        """Cookie-enabled stub — always ``False`` in this headless library.

        >>> Navigator().cookie_enabled
        False
        """
        return self._cookie_enabled

    @property
    def vendor(self) -> str:
        """Browser vendor string stub — always ``''``.

        >>> Navigator().vendor
        ''
        """
        return self._vendor

    @property
    def hardware_concurrency(self) -> int:
        """Logical CPU count stub — always ``1``.

        Per WHATWG HTML §8.7.3. In a headless environment the actual CPU count
        is not exposed; ``1`` is the safe default.

        >>> Navigator().hardware_concurrency
        1
        """
        return 1

    @property
    def max_touch_points(self) -> int:
        """Maximum simultaneous touch points — always ``0`` (no touch device).

        Per WHATWG Pointer Events §4.1. Headless environments have no touch input.

        >>> Navigator().max_touch_points
        0
        """
        return 0

    @property
    def pdf_viewer_enabled(self) -> bool:
        """Whether a built-in PDF viewer is available — always ``False``.

        Per WHATWG HTML §8.7.4. Headless environments have no PDF viewer.

        >>> Navigator().pdf_viewer_enabled
        False
        """
        return False

    @property
    def app_code_name(self) -> str:
        """Legacy browser code name — always ``'Mozilla'`` per spec.

        Per WHATWG HTML §8.7.4 (legacy interface mixin).

        >>> Navigator().app_code_name
        'Mozilla'
        """
        return "Mozilla"

    @property
    def app_name(self) -> str:
        """Legacy application name — always ``'Netscape'`` per spec.

        Per WHATWG HTML §8.7.4 (legacy interface mixin).

        >>> Navigator().app_name
        'Netscape'
        """
        return "Netscape"

    @property
    def app_version(self) -> str:
        """Legacy application version string — always ``''`` in headless mode.

        Per WHATWG HTML §8.7.4 (legacy interface mixin).

        >>> Navigator().app_version
        ''
        """
        return ""

    @property
    def product(self) -> str:
        """Legacy product identifier — always ``'Gecko'`` per spec.

        Per WHATWG HTML §8.7.4 (legacy interface mixin).

        >>> Navigator().product
        'Gecko'
        """
        return "Gecko"

    @property
    def vendor_sub(self) -> str:
        """Legacy vendor sub-string — always ``''`` per spec.

        Per WHATWG HTML §8.7.4 (legacy interface mixin).

        >>> Navigator().vendor_sub
        ''
        """
        return ""

    @property
    def product_sub(self) -> str:
        """Legacy product sub-string — always ``''`` per spec.

        Per WHATWG HTML §8.7.4 (legacy interface mixin).

        >>> Navigator().product_sub
        ''
        """
        return ""

    def java_enabled(self) -> bool:
        """Whether Java is enabled — always ``False``.

        Per WHATWG HTML §8.7.4 (legacy NavigatorPlugins mixin).
        Java applets are not supported in this headless environment.

        Examples
        --------
        >>> Navigator().java_enabled()
        False
        """
        return False

    @property
    def do_not_track(self) -> None:
        """Do-not-track preference — always ``None`` (user preference not set).

        Per WHATWG HTML §8.7.4. Returns ``None`` (not ``'1'`` or ``'0'``)
        as the headless environment does not signal a tracking preference.

        Examples
        --------
        >>> Navigator().do_not_track is None
        True
        """
        return None

    # ------------------------------------------------------------------
    # Track 102 — Navigator IDL tail (BACK-323 / ADR-301)
    # ------------------------------------------------------------------

    @property
    def clipboard(self) -> None:
        """Always ``None`` — no Clipboard API in headless mode (WHATWG Clipboard §3).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().clipboard is None
        True
        """
        return None

    @property
    def media_devices(self) -> None:
        """Always ``None`` — no MediaDevices in headless mode (Media Capture §2).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().media_devices is None
        True
        """
        return None

    @property
    def storage(self) -> None:
        """Always ``None`` — no StorageManager in headless mode (Storage §5).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().storage is None
        True
        """
        return None

    @property
    def geolocation(self) -> None:
        """Always ``None`` — no Geolocation API in headless mode (Geolocation §5).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().geolocation is None
        True
        """
        return None

    @property
    def credentials(self) -> None:
        """Always ``None`` — no CredentialsContainer in headless mode (Credentials §3).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().credentials is None
        True
        """
        return None

    @property
    def xr(self) -> None:
        """Always ``None`` — no XRSystem in headless mode (WebXR §8).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().xr is None
        True
        """
        return None

    def share(self, data: "dict | None" = None) -> None:
        """Raise ``NotSupportedError`` — headless cannot share (Web Share API §2).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> try:
        ...     Navigator().share({'url': 'https://example.com'})
        ... except Exception as e:
        ...     type(e).__name__
        'NotSupportedError'
        """
        from aspose_html.dom import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError("Navigator.share() is not available in headless mode.")

    def can_share(self, data: "dict | None" = None) -> bool:
        """Always ``False`` — headless environment has no sharing capability (Web Share API §2).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().can_share({'url': 'https://example.com'})
        False
        """
        return False

    def vibrate(self, pattern: "int | list") -> bool:
        """Always ``False`` — no vibration hardware in headless mode (Vibration API §2).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().vibrate(200)
        False
        """
        return False

    def send_beacon(self, url: str, data: object = None) -> bool:
        """Always ``False`` — no network delivery in headless mode (Beacon API §3).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().send_beacon('https://example.com/log')
        False
        """
        return False

    @property
    def locks(self) -> None:
        """Always ``None`` — no LockManager in headless mode (Web Locks §4).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().locks is None
        True
        """
        return None

    @property
    def bluetooth(self) -> None:
        """Always ``None`` — no Bluetooth API in headless mode (WebBluetooth §4).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().bluetooth is None
        True
        """
        return None

    @property
    def hid(self) -> None:
        """Always ``None`` — no HID API in headless mode (WebHID §3).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().hid is None
        True
        """
        return None

    @property
    def usb(self) -> None:
        """Always ``None`` — no USB API in headless mode (WebUSB §3).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().usb is None
        True
        """
        return None

    @property
    def serial(self) -> None:
        """Always ``None`` — no Serial API in headless mode (Web Serial §4).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().serial is None
        True
        """
        return None

    @property
    def wake_lock(self) -> None:
        """Always ``None`` — no WakeLock API in headless mode (Wake Lock §4).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().wake_lock is None
        True
        """
        return None

    @property
    def connection(self) -> None:
        """Always ``None`` — no NetworkInformation API in headless mode.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.navigator.connection is None
        True
        """
        return None

    @property
    def device_memory(self) -> float:
        """Device memory in GiB; returns 8.0 as headless sentinel.

        The Navigator.deviceMemory spec (Device Memory §2) allows rounding
        to the nearest 0.25 GiB. 8.0 is the conventional headless default.

        Examples
        --------
        >>> from aspose_html import HTMLDocument
        >>> w = HTMLDocument.parse('<html></html>').default_view
        >>> w.navigator.device_memory
        8.0
        """
        return 8.0

    # ------------------------------------------------------------------
    # Track 110 — Navigator IDL tail (BACK-330 / ADR-309)
    # ------------------------------------------------------------------

    @property
    def media_capabilities(self) -> None:
        """Always ``None`` — MediaCapabilities API not available in headless mode.

        Per W3C Media Capabilities §4 (``navigator.mediaCapabilities``).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().media_capabilities is None
        True
        """
        return None

    @property
    def permissions(self) -> None:
        """Always ``None`` — Permissions API not available in headless mode.

        Per W3C Permissions §5 (``navigator.permissions``).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().permissions is None
        True
        """
        return None

    @property
    def service_worker(self) -> None:
        """Always ``None`` — Service Workers API not available in headless mode.

        Per Service Workers §5.4 (``navigator.serviceWorker``).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().service_worker is None
        True
        """
        return None

    @property
    def user_activation(self) -> None:
        """Always ``None`` — User Activation API not available in headless mode.

        Per WHATWG HTML §6.4 (``navigator.userActivation``).  Headless
        execution never produces user-activation gestures.

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().user_activation is None
        True
        """
        return None

    @property
    def keyboard(self) -> None:
        """Always ``None`` — Keyboard API not available in headless mode.

        Per W3C Keyboard Map §4 (``navigator.keyboard``).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().keyboard is None
        True
        """
        return None

    @property
    def presentation(self) -> None:
        """Always ``None`` — Presentation API not available in headless mode.

        Per W3C Presentation API §5 (``navigator.presentation``).

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().presentation is None
        True
        """
        return None

    # ------------------------------------------------------------------
    # Track 114 — Navigator IDL tail (BACK-335 / ADR-313)
    # ------------------------------------------------------------------

    @property
    def global_privacy_control(self) -> bool:
        """Always ``False`` — GPC signal not asserted in headless mode.

        Global Privacy Control §3.2.

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().global_privacy_control
        False
        """
        return False

    @property
    def webdriver(self) -> bool:
        """Always ``True`` — headless is a WebDriver-equivalent context.

        WHATWG HTML §8.9.  Headless automation environments set this to
        ``True``; returning ``False`` would misrepresent the environment.

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().webdriver
        True
        """
        return True

    def get_gamepads(self) -> list:
        """Return an empty list — no gamepad hardware in headless mode.

        Gamepad API §7.

        Examples
        --------
        >>> from aspose_html.dom._window import Navigator
        >>> Navigator().get_gamepads()
        []
        """
        return []


class Location:
    __slots__ = ("_window",)

    def __init__(self, window: "Window") -> None:
        self._window = window

    @property
    def href(self) -> str:
        """Current document URL string."""
        return self._window._document._url

    @href.setter
    def href(self, value: str) -> None:
        self.replace(str(value))

    def assign(self, url: str) -> None:
        """Push a same-document navigation-style history entry.

        This mutates in-memory history/URL state only. It does not
        fetch, reload, or replace the active document content.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc._url = "https://example.com/"
        >>> loc = doc.default_view.location
        >>> loc.assign("/next")
        >>> loc.pathname
        '/next'
        """
        self._window.history.push_state(self._window.history.state, "", url)

    def replace(self, url: str) -> None:
        """Replace the current history entry URL in-memory.

        This mutates in-memory history/URL state only. It does not
        fetch, reload, or replace the active document content.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc._url = "https://example.com/"
        >>> loc = doc.default_view.location
        >>> loc.replace("/replaced")
        >>> loc.pathname
        '/replaced'
        """
        self._window.history.replace_state(self._window.history.state, "", url)

    def reload(self) -> None:
        """Compatibility stub for browser-style ``location.reload()``.

        This runtime intentionally does not perform network/document
        navigation. ``reload()`` is a deterministic no-op.

        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> doc._url = "https://example.com/"
        >>> before = doc.default_view.location.href
        >>> doc.default_view.location.reload()
        >>> doc.default_view.location.href == before
        True
        """
        return None

    def _mutate_url_component(self, mutator: Callable[[URL], None]) -> None:
        current = self.href
        candidate = URL(current)
        mutator(candidate)
        target = candidate.href
        if target == current:
            return
        self.replace(target)

    @property
    def protocol(self) -> str:
        p = urlsplit(self.href)
        return f"{p.scheme}:" if p.scheme else ""

    @protocol.setter
    def protocol(self, value: str) -> None:
        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Location.protocol cannot be empty")
        if not normalized.endswith(":"):
            normalized = f"{normalized}:"
        self._mutate_url_component(lambda candidate: setattr(candidate, "protocol", normalized))

    @property
    def host(self) -> str:
        return urlsplit(self.href).netloc

    @host.setter
    def host(self, value: str) -> None:
        self._mutate_url_component(lambda candidate: setattr(candidate, "host", str(value)))

    @property
    def hostname(self) -> str:
        return urlsplit(self.href).hostname or ""

    @hostname.setter
    def hostname(self, value: str) -> None:
        self._mutate_url_component(lambda candidate: setattr(candidate, "hostname", str(value)))

    @property
    def port(self) -> str:
        p = urlsplit(self.href)
        return str(p.port) if p.port else ""

    @port.setter
    def port(self, value: str) -> None:
        self._mutate_url_component(lambda candidate: setattr(candidate, "port", str(value)))

    @property
    def pathname(self) -> str:
        return urlsplit(self.href).path

    @pathname.setter
    def pathname(self, value: str) -> None:
        normalized = str(value)
        if normalized and not normalized.startswith("/"):
            normalized = f"/{normalized}"
        self._mutate_url_component(lambda candidate: setattr(candidate, "pathname", normalized))

    @property
    def search(self) -> str:
        p = urlsplit(self.href)
        return f"?{p.query}" if p.query else ""

    @search.setter
    def search(self, value: str) -> None:
        normalized = str(value)
        if normalized and not normalized.startswith("?"):
            normalized = f"?{normalized}"
        self._mutate_url_component(lambda candidate: setattr(candidate, "search", normalized))

    @property
    def hash(self) -> str:
        p = urlsplit(self.href)
        return f"#{p.fragment}" if p.fragment else ""

    @hash.setter
    def hash(self, value: str) -> None:
        """Update fragment via same-document history semantics.

        Non-empty fragments are normalized to ``#...``; unchanged
        effective URLs are a no-op. No real navigation is performed.
        """
        fragment = str(value)
        if fragment and not fragment.startswith("#"):
            fragment = f"#{fragment}"
        split = urlsplit(self.href)
        new_url = urlunsplit((split.scheme, split.netloc, split.path, split.query, fragment.lstrip("#")))
        if new_url == self.href:
            return
        self.assign(new_url)


class Storage:
    """Key-value store implementing the WHATWG HTML §12 Storage interface.

    Used for ``Window.local_storage`` and ``Window.session_storage``.
    In a server-side context all data is in-memory and transient.

    >>> s = Storage()
    >>> s.length
    0
    >>> s.set_item("x", "1")
    >>> s.get_item("x")
    '1'
    >>> s.length
    1
    >>> s.key(0)
    'x'
    >>> s.remove_item("x")
    >>> s.length
    0
    """

    __slots__ = ("_store",)

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    @property
    def length(self) -> int:
        """Number of key-value pairs currently in this store.

        >>> s = Storage()
        >>> s.length
        0
        >>> s.set_item("a", "1")
        >>> s.length
        1
        """
        return len(self._store)

    def key(self, n: int) -> str | None:
        """Return the *n*-th key in insertion order, or ``None`` if out of range.

        Negative indices and indices >= :attr:`length` both return ``None``
        (WHATWG IDL semantics — no ``IndexError``).

        >>> s = Storage()
        >>> s.set_item("first", "1")
        >>> s.set_item("second", "2")
        >>> s.key(0)
        'first'
        >>> s.key(1)
        'second'
        >>> s.key(2) is None
        True
        >>> s.key(-1) is None
        True
        """
        keys = list(self._store.keys())
        if n < 0 or n >= len(keys):
            return None
        return keys[n]

    def get_item(self, key: str) -> str | None:
        """Return the string value for *key*, or ``None`` if the key is absent.

        Never raises ``KeyError``.

        >>> s = Storage()
        >>> s.get_item("missing") is None
        True
        >>> s.set_item("k", "v")
        >>> s.get_item("k")
        'v'
        """
        return self._store.get(key)

    def set_item(self, key: str, value: str) -> None:
        """Store or update a key-value pair.

        *value* is coerced to :class:`str` (WHATWG IDL DOMString coercion).

        >>> s = Storage()
        >>> s.set_item("n", "42")
        >>> s.get_item("n")
        '42'
        >>> s.set_item("n", "99")
        >>> s.get_item("n")
        '99'
        """
        self._store[key] = str(value)

    def remove_item(self, key: str) -> None:
        """Remove the key-value pair identified by *key*.

        No-op if *key* is not present — never raises an exception.

        >>> s = Storage()
        >>> s.set_item("k", "v")
        >>> s.remove_item("k")
        >>> s.get_item("k") is None
        True
        >>> s.remove_item("missing")  # no-op — must not raise
        """
        self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all key-value pairs from this store.

        >>> s = Storage()
        >>> s.set_item("a", "1")
        >>> s.set_item("b", "2")
        >>> s.clear()
        >>> s.length
        0
        """
        self._store.clear()


class VisualViewport:
    """CSSOM View §9 VisualViewport — all values are headless stubs.

    In a server-side / headless context there is no real layout engine,
    so all geometric properties return 0 (or 1.0 for scale).

    >>> from aspose_html.html_document import HTMLDocument
    >>> vv = HTMLDocument.parse('<p>x</p>').default_view.visual_viewport
    >>> vv.width
    0
    >>> vv.scale
    1.0
    """

    __slots__ = ()

    @property
    def width(self) -> int:
        """Viewport width in CSS pixels (stub: 0).

        >>> from aspose_html.dom._window import VisualViewport
        >>> VisualViewport().width
        0
        """
        return 0

    @property
    def height(self) -> int:
        """Viewport height in CSS pixels (stub: 0).

        >>> from aspose_html.dom._window import VisualViewport
        >>> VisualViewport().height
        0
        """
        return 0

    @property
    def scale(self) -> float:
        """Pinch-zoom scale factor (stub: 1.0 — no pinch-zoom in headless).

        >>> from aspose_html.dom._window import VisualViewport
        >>> VisualViewport().scale
        1.0
        """
        return 1.0

    @property
    def offset_top(self) -> float:
        """Top offset of the visual viewport relative to the layout viewport (stub: 0.0).

        >>> from aspose_html.dom._window import VisualViewport
        >>> VisualViewport().offset_top
        0.0
        """
        return 0.0

    @property
    def offset_left(self) -> float:
        """Left offset of the visual viewport relative to the layout viewport (stub: 0.0).

        >>> from aspose_html.dom._window import VisualViewport
        >>> VisualViewport().offset_left
        0.0
        """
        return 0.0

    @property
    def page_top(self) -> float:
        """Top position of the visual viewport in the page (stub: 0.0).

        >>> from aspose_html.dom._window import VisualViewport
        >>> VisualViewport().page_top
        0.0
        """
        return 0.0

    @property
    def page_left(self) -> float:
        """Left position of the visual viewport in the page (stub: 0.0).

        >>> from aspose_html.dom._window import VisualViewport
        >>> VisualViewport().page_left
        0.0
        """
        return 0.0


class Screen:
    """Browser screen geometry — all values are stubs (server-side context).

    In a server-side Python environment there is no physical display.
    All dimension attributes are fixed at zero; ``color_depth`` and
    ``pixel_depth`` default to 24 (a common desktop value) so that code
    that checks these values does not receive 0 unexpectedly.

    Attributes
    ----------
    width : int
        Total screen width in CSS pixels (stub: 0).
    height : int
        Total screen height in CSS pixels (stub: 0).
    avail_width : int
        Available screen width in CSS pixels (stub: 0).
    avail_height : int
        Available screen height in CSS pixels (stub: 0).
    color_depth : int
        Colour depth of the screen in bits (stub: 24).
    pixel_depth : int
        Pixel depth of the screen in bits (stub: 24).

    Examples
    --------
    >>> from aspose_html.dom._document import Document
    >>> w = Document().default_view
    >>> s = w.screen
    >>> s.width
    0
    >>> s.height
    0
    >>> s.avail_width
    0
    >>> s.avail_height
    0
    >>> s.color_depth
    24
    >>> s.pixel_depth
    24
    """

    def __init__(self) -> None:
        self.width: int = 0
        self.height: int = 0
        self.avail_width: int = 0
        self.avail_height: int = 0
        self.color_depth: int = 24
        self.pixel_depth: int = 24


class Console:
    __slots__ = ("_logger",)

    def __init__(self) -> None:
        self._logger = logging.getLogger("aspose_html.window")

    def log(self, *args: object) -> None:
        self._logger.info(" ".join(str(a) for a in args))

    def info(self, *args: object) -> None:
        self.log(*args)

    def warn(self, *args: object) -> None:
        self._logger.warning(" ".join(str(a) for a in args))

    def error(self, *args: object) -> None:
        self._logger.error(" ".join(str(a) for a in args))

    def debug(self, *args: object) -> None:
        self._logger.debug(" ".join(str(a) for a in args))


class IntersectionObserverEntry:
    """Headless IntersectionObserver entry stub.

    Entries are currently never produced in this runtime.
    """

    __slots__ = ()


class IntersectionObserver:
    """Headless IntersectionObserver API-shape stub.

    Methods are deterministic no-ops; callbacks are never auto-invoked.

    >>> from aspose_html.dom import Document
    >>> win = Document().default_view
    >>> observer = win.IntersectionObserver(lambda _entries, _obs: None)
    >>> target = win.document.create_element("div")
    >>> observer.observe(target)
    >>> observer.take_records()
    []
    """

    __slots__ = ("_callback", "_options")

    def __init__(self, callback: object, options: object = None) -> None:
        self._callback = callback
        self._options = options

    def observe(self, target: object) -> None:
        """Register *target* for observation (no-op stub)."""

    def unobserve(self, target: object) -> None:
        """Unregister *target* from observation (no-op stub)."""

    def disconnect(self) -> None:
        """Stop observation for all targets (no-op stub)."""

    def take_records(self) -> list[IntersectionObserverEntry]:
        """Return queued intersection records (always empty).

        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.IntersectionObserver(lambda _entries, _obs: None).take_records()
        []
        """
        return []


class ResizeObserverEntry:
    """Headless ResizeObserver entry stub.

    Entries are currently never produced in this runtime.
    """

    __slots__ = ()


class ResizeObserver:
    """Headless ResizeObserver API-shape stub.

    Methods are deterministic no-ops; callbacks are never auto-invoked.

    >>> from aspose_html.dom import Document
    >>> win = Document().default_view
    >>> observer = win.ResizeObserver(lambda _entries, _obs: None)
    >>> target = win.document.create_element("div")
    >>> observer.observe(target)
    >>> observer.take_records()
    []
    """

    __slots__ = ("_callback", "_options")

    def __init__(self, callback: object, options: object = None) -> None:
        self._callback = callback
        self._options = options

    def observe(self, target: object) -> None:
        """Register *target* for observation (no-op stub)."""

    def unobserve(self, target: object) -> None:
        """Unregister *target* from observation (no-op stub)."""

    def disconnect(self) -> None:
        """Stop observation for all targets (no-op stub)."""

    def take_records(self) -> list[ResizeObserverEntry]:
        """Return queued resize records (always empty).

        >>> from aspose_html.dom import Document
        >>> win = Document().default_view
        >>> win.ResizeObserver(lambda _entries, _obs: None).take_records()
        []
        """
        return []


class MessagePort(EventTarget):
    """Deterministic same-runtime MessagePort queue baseline.

    Messages are queued onto the entangled peer and delivered only from
    scheduled event-loop tasks. This keeps producer calls synchronous-safe
    (no direct callback invocation from :meth:`post_message`).

    >>> from aspose_html.dom import MessageChannel
    >>> channel = MessageChannel()
    >>> port = channel.port1
    >>> port.onmessage = lambda evt: (_ for _ in ()).throw(RuntimeError("never called"))
    >>> port.start()
    >>> port.post_message({"x": 1})
    >>> port._event_loop.drain()
    >>> port.closed
    False
    >>> port.close()
    >>> port.closed
    True
    """

    __slots__ = ("_peer", "_closed", "_started", "_pending", "_event_loop", "onmessage")

    def __init__(self) -> None:
        super().__init__()
        self._peer: MessagePort | None = None
        self._closed = False
        self._started = False
        self._pending: deque[object] = deque()
        self._event_loop = WindowEventLoop()
        self._event_loop.register_task_source("message-port")
        self.onmessage: Callable[[object], object] | None = None

    @property
    def closed(self) -> bool:
        """Whether this port has been closed.

        >>> from aspose_html.dom import MessageChannel
        >>> port = MessageChannel().port1
        >>> port.closed
        False
        >>> port.close()
        >>> port.closed
        True
        """
        return self._closed

    def post_message(self, message: object) -> None:
        """Queue a message for peer delivery via scheduled event-loop task.

        >>> from aspose_html.dom import MessageChannel
        >>> channel = MessageChannel()
        >>> seen = []
        >>> channel.port2.onmessage = lambda evt: seen.append(evt)
        >>> channel.port2.start()
        >>> channel.port1.post_message({"hello": "world"})
        >>> seen
        []
        >>> channel.port1._event_loop.drain()
        >>> seen
        [{'hello': 'world'}]
        """
        from aspose_html.dom._exceptions import InvalidStateError  # noqa: PLC0415

        if self._closed:
            raise InvalidStateError("Cannot post_message() on a closed MessagePort.")
        peer = self._peer
        if peer is None or peer._closed:
            return
        cloned_message = clone_or_raise_data_clone_error(message)
        peer._pending.append(cloned_message)
        self._event_loop.schedule(
            "message-port",
            "dispatch",
            callback=peer._dispatch_queued_messages,
        )

    def start(self) -> None:
        """Start message dispatching (idempotent).

        >>> from aspose_html.dom import MessageChannel
        >>> port = MessageChannel().port1
        >>> port.start()
        >>> port.start()
        >>> port._started
        True
        """
        self._started = True

    def _dispatch_queued_messages(self) -> None:
        if self._closed or not self._started:
            return
        handler = self.onmessage
        if handler is None:
            self._pending.clear()
            return
        while self._pending and self._started and not self._closed:
            handler(self._pending.popleft())

    def close(self) -> None:
        """Close this port. Repeated calls are ignored.

        >>> from aspose_html.dom import MessageChannel
        >>> port = MessageChannel().port1
        >>> port.close()
        >>> port.close()
        >>> port.closed
        True
        """
        self._closed = True
        self._pending.clear()


class MessageChannel:
    """Pair of linked :class:`MessagePort` endpoints.

    >>> from aspose_html.dom import MessageChannel
    >>> channel = MessageChannel()
    >>> isinstance(channel.port1, type(channel.port2))
    True
    >>> channel.port1 is channel.port2
    False
    """

    __slots__ = ("_port1", "_port2")

    def __init__(self) -> None:
        self._port1 = MessagePort()
        self._port2 = MessagePort()
        self._port1._peer = self._port2
        self._port2._peer = self._port1

    @property
    def port1(self) -> MessagePort:
        """First channel endpoint.

        >>> from aspose_html.dom import MessageChannel
        >>> isinstance(MessageChannel().port1, MessagePort)
        True
        """
        return self._port1

    @property
    def port2(self) -> MessagePort:
        """Second channel endpoint.

        >>> from aspose_html.dom import MessageChannel
        >>> isinstance(MessageChannel().port2, MessagePort)
        True
        """
        return self._port2


class BroadcastChannel(EventTarget):
    """Deterministic same-runtime BroadcastChannel fan-out delivery.

    Delivery is bounded to channels created in this Python runtime that
    share the same ``name``. Dispatch is event-loop scheduled (never
    synchronous from :meth:`post_message`) and excludes sender self-delivery.

    >>> from aspose_html.dom import BroadcastChannel
    >>> channel = BroadcastChannel("updates")
    >>> channel.name
    'updates'
    >>> seen = []
    >>> channel.onmessage = lambda evt: seen.append(evt)
    >>> sibling = BroadcastChannel("updates")
    >>> sibling.onmessage = lambda evt: seen.append(evt)
    >>> channel.post_message({"v": 1})
    >>> seen
    []
    >>> channel._event_loop.drain()
    >>> seen
    [{'v': 1}]
    >>> channel.close()
    >>> sibling.close()
    >>> channel.close()
    """

    _registry: dict[str, list["BroadcastChannel"]] = {}

    __slots__ = ("_name", "_closed", "_event_loop", "onmessage")

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = str(name)
        self._closed = False
        self._event_loop = WindowEventLoop()
        self._event_loop.register_task_source("broadcast-channel")
        self.onmessage: Callable[[object], object] | None = None
        self._registry.setdefault(self._name, []).append(self)

    @property
    def name(self) -> str:
        """Channel name provided at construction time.

        >>> from aspose_html.dom import BroadcastChannel
        >>> BroadcastChannel("probe").name
        'probe'
        """
        return self._name

    def post_message(self, message: object) -> None:
        """Queue same-name sibling fan-out delivery via event-loop scheduling.

        >>> from aspose_html.dom import BroadcastChannel
        >>> ch = BroadcastChannel("x")
        >>> seen = []
        >>> ch.onmessage = lambda evt: seen.append(evt)
        >>> sibling = BroadcastChannel("x")
        >>> sibling.onmessage = lambda evt: seen.append(evt)
        >>> ch.post_message("payload")
        >>> seen
        []
        >>> ch._event_loop.drain()
        >>> seen
        ['payload']
        >>> sibling.close()
        """
        from aspose_html.dom._exceptions import InvalidStateError  # noqa: PLC0415

        if self._closed:
            raise InvalidStateError("Cannot post_message() on a closed BroadcastChannel.")

        siblings = tuple(self._registry.get(self._name, ()))
        for target in siblings:
            if target is self or target._closed:
                continue
            cloned_message = clone_or_raise_data_clone_error(message)
            self._event_loop.schedule(
                "broadcast-channel",
                "dispatch",
                callback=lambda target=target, message=cloned_message: target._dispatch_message(message),
            )

    def _dispatch_message(self, message: object) -> None:
        if self._closed:
            return
        handler = self.onmessage
        if handler is None:
            return
        handler(message)

    def close(self) -> None:
        """Close the channel; repeated calls are ignored.

        >>> from aspose_html.dom import BroadcastChannel
        >>> ch = BroadcastChannel("x")
        >>> ch.close()
        >>> ch.close()
        """
        if self._closed:
            return
        self._closed = True
        channels = self._registry.get(self._name)
        if channels is None:
            return
        self._registry[self._name] = [channel for channel in channels if channel is not self and not channel._closed]
        if not self._registry[self._name]:
            self._registry.pop(self._name, None)


class DataCloneError(DOMException):
    """Raised when a value cannot be serialized by the structured clone algorithm.

    Corresponds to DOMException code 25 (DATA_CLONE_ERR) per WebIDL.

    Examples
    --------
    >>> from aspose_html.dom._window import DataCloneError
    >>> e = DataCloneError("cannot clone")
    >>> e.code
    25
    >>> str(e)
    'cannot clone'
    """

    code: int = 25
    __slots__ = ()

    def __init__(self, message: str = "The object cannot be cloned.") -> None:
        super().__init__(message)


class SubtleCrypto:
    """Stub for the SubtleCrypto interface (W3C Web Crypto API §10).

    All operations raise :class:`~aspose_html.dom.NotSupportedError` — no
    cryptographic operations are implemented in this headless runtime.

    Examples
    --------
    >>> from aspose_html.dom._window import SubtleCrypto
    >>> sc = SubtleCrypto()
    >>> try:
    ...     sc.digest("SHA-256", b"data")
    ... except Exception as e:
    ...     type(e).__name__
    'NotSupportedError'
    """

    __slots__ = ()

    def _not_supported(self, *args: object, **kwargs: object) -> None:
        from aspose_html.dom import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError("SubtleCrypto is not available in headless mode.")

    # Common SubtleCrypto method stubs — all raise NotSupportedError
    encrypt = decrypt = sign = verify = digest = \
        generate_key = derive_key = derive_bits = \
        import_key = export_key = wrap_key = unwrap_key = _not_supported


class Crypto:
    """Minimal stub for the Crypto interface (W3C Web Crypto API §10.1).

    ``get_random_values`` fills the supplied array with zeros for
    deterministic headless behavior.  ``random_uuid`` returns a
    fixed-format but deterministic UUID string.  ``subtle`` raises
    :class:`~aspose_html.dom.NotSupportedError` for all operations.

    Examples
    --------
    >>> from aspose_html.dom._window import Crypto
    >>> c = Crypto()
    >>> arr = bytearray(4)
    >>> result = c.get_random_values(arr)
    >>> result is arr
    True
    >>> result == bytearray(4)
    True
    >>> uuid = c.random_uuid()
    >>> len(uuid)
    36
    >>> uuid.count('-')
    4
    """

    __slots__ = ("_subtle",)

    def __init__(self) -> None:
        self._subtle: SubtleCrypto = SubtleCrypto()

    @property
    def subtle(self) -> SubtleCrypto:
        """Return the :class:`SubtleCrypto` interface stub."""
        return self._subtle

    def get_random_values(self, typed_array: bytearray) -> bytearray:
        """Fill *typed_array* with zeros (deterministic headless stub).

        Per W3C Web Crypto API §10.1.2.  Returns the same array.

        Parameters
        ----------
        typed_array:
            A mutable sequence supporting ``len`` and index assignment.

        Returns
        -------
        bytearray
            The same object that was passed in, filled with zeros.
        """
        for i in range(len(typed_array)):
            typed_array[i] = 0
        return typed_array

    def random_uuid(self) -> str:
        """Return a deterministic UUID-format string.

        Per W3C Web Crypto API §10.1.3.  Returns the nil UUID
        ``00000000-0000-4000-8000-000000000000`` in headless mode.

        Returns
        -------
        str
            A 36-character string with four hyphens in UUID layout.
        """
        return "00000000-0000-4000-8000-000000000000"


@dataclass
class PerformanceEntry:
    """A single performance timeline entry.

    Per W3C Performance Timeline Level 2 §4.

    Parameters
    ----------
    name:
        Identifier for the entry (mark name or measure name).
    entry_type:
        One of ``"mark"`` or ``"measure"``.
    start_time:
        Elapsed milliseconds since the :class:`Performance` instance was
        created when this entry was recorded.
    duration:
        Duration in milliseconds.  Always ``0.0`` for ``mark`` entries in
        this stub implementation.

    Examples
    --------
    >>> from aspose_html.dom._window import PerformanceEntry
    >>> e = PerformanceEntry(name="start", entry_type="mark", start_time=0.0, duration=0.0)
    >>> e.name
    'start'
    >>> e.entry_type
    'mark'
    """

    name: str
    entry_type: str   # "mark" | "measure"
    start_time: float
    duration: float


class PerformanceTiming:
    """Legacy Navigation Timing Level 1 interface stub.

    All timing attributes return ``0`` in this headless context.
    Per W3C Navigation Timing Level 1 §7.

    Examples
    --------
    >>> from aspose_html.dom._window import PerformanceTiming
    >>> t = PerformanceTiming()
    >>> t.navigation_start
    0
    >>> t.load_event_end
    0
    """

    __slots__ = ()

    # All Navigation Timing Level 1 attributes return 0.
    # Defined as class-level attributes (not properties) to avoid slot bloat.
    navigation_start = fetch_start = domain_lookup_start = \
        domain_lookup_end = connect_start = connect_end = \
        secure_connection_start = request_start = response_start = \
        response_end = dom_loading = dom_interactive = \
        dom_content_loaded_event_start = dom_content_loaded_event_end = \
        dom_complete = load_event_start = load_event_end = \
        unload_event_start = unload_event_end = redirect_start = \
        redirect_end = 0


class Performance:
    """Minimal stub for the Performance interface.

    ``now()`` returns elapsed milliseconds since the :class:`Performance`
    instance was created, using :func:`time.monotonic` for monotonicity.
    ``mark()`` and ``measure()`` store :class:`PerformanceEntry` objects in an
    internal list; ``get_entries_by_name()`` and ``get_entries_by_type()``
    query it.  ``clear_marks()`` and ``clear_measures()`` prune it.
    ``timing`` returns a :class:`PerformanceTiming` stub with all zeros.

    Per W3C HR Time Level 2 §5, Performance Timeline Level 2 §4, and
    Navigation Timing Level 2 §5.

    Examples
    --------
    >>> from aspose_html.dom._window import Performance
    >>> p = Performance()
    >>> isinstance(p.now(), float)
    True
    >>> p.now() >= 0.0
    True
    >>> p.mark("start")
    >>> entries = p.get_entries_by_type("mark")
    >>> entries[0].name
    'start'
    >>> p.clear_marks()
    >>> p.get_entries_by_type("mark")
    []
    """

    __slots__ = ("_t0", "_entries", "_timing")

    def __init__(self) -> None:
        self._t0: float = _time.monotonic()
        self._entries: list[PerformanceEntry] = []
        self._timing: PerformanceTiming = PerformanceTiming()

    def now(self) -> float:
        """Return elapsed milliseconds since this instance was created.

        Uses :func:`time.monotonic` — values are monotonically non-decreasing.
        Per W3C HR Time Level 2 §5.3.

        Returns
        -------
        float
            Non-negative milliseconds elapsed.

        Examples
        --------
        >>> from aspose_html.dom._window import Performance
        >>> p = Performance()
        >>> p.now() >= 0.0
        True
        """
        return (_time.monotonic() - self._t0) * 1000.0

    @property
    def timing(self) -> PerformanceTiming:
        """Return the :class:`PerformanceTiming` stub (all attributes ``0``).

        Per W3C Navigation Timing Level 1 §7.

        Examples
        --------
        >>> from aspose_html.dom._window import Performance
        >>> p = Performance()
        >>> p.timing.navigation_start
        0
        """
        return self._timing

    def mark(self, name: str) -> None:
        """Record a ``mark`` entry with the given *name*.

        Per W3C User Timing Level 2 §3.1.

        Parameters
        ----------
        name:
            Name for the mark.

        Examples
        --------
        >>> from aspose_html.dom._window import Performance
        >>> p = Performance()
        >>> p.mark("t1")
        >>> p.get_entries_by_type("mark")[0].name
        't1'
        """
        self._entries.append(
            PerformanceEntry(
                name=name,
                entry_type="mark",
                start_time=self.now(),
                duration=0.0,
            )
        )

    def measure(
        self,
        name: str,
        start_mark: str | None = None,
        end_mark: str | None = None,
    ) -> None:
        """Record a ``measure`` entry with the given *name*.

        Per W3C User Timing Level 2 §3.2.  ``start_mark`` and ``end_mark``
        are accepted but ignored in this stub — duration is always ``0.0``.

        Parameters
        ----------
        name:
            Name for the measure.
        start_mark:
            Optional name of a previously recorded mark (ignored in stub).
        end_mark:
            Optional name of a previously recorded mark (ignored in stub).

        Examples
        --------
        >>> from aspose_html.dom._window import Performance
        >>> p = Performance()
        >>> p.measure("m")
        >>> p.get_entries_by_type("measure")[0].entry_type
        'measure'
        """
        self._entries.append(
            PerformanceEntry(
                name=name,
                entry_type="measure",
                start_time=self.now(),
                duration=0.0,
            )
        )

    def get_entries_by_name(self, name: str) -> list[PerformanceEntry]:
        """Return all entries whose ``name`` matches *name*.

        Per W3C Performance Timeline Level 2 §5.2.

        Parameters
        ----------
        name:
            Entry name to filter by.

        Returns
        -------
        list[PerformanceEntry]
            Possibly-empty list of matching entries.

        Examples
        --------
        >>> from aspose_html.dom._window import Performance
        >>> p = Performance()
        >>> p.mark("a")
        >>> p.mark("b")
        >>> [e.name for e in p.get_entries_by_name("a")]
        ['a']
        """
        return [e for e in self._entries if e.name == name]

    def get_entries_by_type(self, type_: str) -> list[PerformanceEntry]:
        """Return all entries whose ``entry_type`` matches *type_*.

        Per W3C Performance Timeline Level 2 §5.3.

        Parameters
        ----------
        type_:
            Entry type to filter by, e.g. ``"mark"`` or ``"measure"``.

        Returns
        -------
        list[PerformanceEntry]
            Possibly-empty list of matching entries.

        Examples
        --------
        >>> from aspose_html.dom._window import Performance
        >>> p = Performance()
        >>> p.mark("x")
        >>> p.measure("y")
        >>> [e.entry_type for e in p.get_entries_by_type("mark")]
        ['mark']
        """
        return [e for e in self._entries if e.entry_type == type_]

    def clear_marks(self, name: str | None = None) -> None:
        """Remove mark entries from the internal store.

        Per W3C User Timing Level 2 §3.3.

        Parameters
        ----------
        name:
            If given, only marks with this name are removed.
            If ``None`` (default), all marks are removed.

        Examples
        --------
        >>> from aspose_html.dom._window import Performance
        >>> p = Performance()
        >>> p.mark("a")
        >>> p.measure("m")
        >>> p.clear_marks()
        >>> p.get_entries_by_type("mark")
        []
        >>> len(p.get_entries_by_type("measure"))
        1
        """
        if name is None:
            self._entries = [e for e in self._entries if e.entry_type != "mark"]
        else:
            self._entries = [
                e for e in self._entries
                if not (e.entry_type == "mark" and e.name == name)
            ]

    def clear_measures(self, name: str | None = None) -> None:
        """Remove measure entries from the internal store.

        Per W3C User Timing Level 2 §3.4.

        Parameters
        ----------
        name:
            If given, only measures with this name are removed.
            If ``None`` (default), all measures are removed.

        Examples
        --------
        >>> from aspose_html.dom._window import Performance
        >>> p = Performance()
        >>> p.mark("a")
        >>> p.measure("m")
        >>> p.clear_measures()
        >>> p.get_entries_by_type("measure")
        []
        >>> len(p.get_entries_by_type("mark"))
        1
        """
        if name is None:
            self._entries = [e for e in self._entries if e.entry_type != "measure"]
        else:
            self._entries = [
                e for e in self._entries
                if not (e.entry_type == "measure" and e.name == name)
            ]


class BarProp:
    """Represents a browser toolbar object (WHATWG HTML §7.7.3).

    All ``visible`` properties return ``False`` in headless mode.

    Examples
    --------
    >>> from aspose_html.dom._window import BarProp
    >>> bp = BarProp()
    >>> bp.visible
    False
    """

    __slots__ = ()

    @property
    def visible(self) -> bool:
        """Always ``False`` — no browser chrome in headless mode (WHATWG HTML §7.7.3).

        Examples
        --------
        >>> from aspose_html.dom._window import BarProp
        >>> BarProp().visible
        False
        """
        return False


class _External:
    """Stub for the legacy ``Window.external`` object (WHATWG HTML §11.5).

    All methods are no-ops — the External interface was removed from the
    spec and implementations treat it as a no-op stub for compatibility.

    Examples
    --------
    >>> from aspose_html.dom._window_stubs import _External
    >>> ext = _External()
    >>> ext.add_search_provider('https://example.com/search') is None
    True
    """

    __slots__ = ()

    def add_search_provider(self, url: str) -> None:
        """No-op stub (WHATWG HTML §11.5 — historical).

        Examples
        --------
        >>> from aspose_html.dom._window_stubs import _External
        >>> _External().add_search_provider('https://example.com/search') is None
        True
        """
