"""Media element classes.

Contains ``HTMLMediaElement``, ``HTMLVideoElement``, ``HTMLAudioElement``,
``HTMLSourceElement``, ``HTMLTrackElement``, ``HTMLPictureElement``.

See  for the split rationale.
"""
from __future__ import annotations

from aspose_html.dom._html_element import HTMLElement


class _TimeRanges:
    """Minimal TimeRanges stub — always empty in headless mode."""

    length: int = 0


class _EmptyTrackList:
    """Minimal TextTrack/AudioTrack/VideoTrackList stub — always empty."""

    length: int = 0


class HTMLPictureElement(HTMLElement):
    """HTML ``<picture>`` element (structural subclass).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> isinstance(doc.create_element("picture"), HTMLPictureElement)
    True
    """

    __slots__ = ()



class HTMLMediaElement(HTMLElement):
    """Base class for HTML media elements (``<audio>`` / ``<video>``).

    Examples
    --------
    >>> from aspose_html.dom import Document
    >>> media = Document().create_element("audio")
    >>> media.paused
    True
    >>> media.ended
    False
    """

    __slots__ = ("_default_playback_rate", "_playback_rate")

    @property
    def src(self) -> str:
        """The ``src`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.src
        ''
        >>> media.set_attribute("src", "track.mp3")
        >>> media.src
        'track.mp3'
        """
        return self.get_attribute("src") or ""

    @property
    def current_src(self) -> str:
        """Current selected source URL (stub, always ``''``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").current_src
        ''
        """
        return ""

    @property
    def auto_play(self) -> bool:
        """Boolean reflection of the ``autoplay`` attribute.

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.auto_play
        False
        >>> media.set_attribute("autoplay", "")
        >>> media.auto_play
        True
        """
        return self.has_attribute("autoplay")

    @property
    def controls(self) -> bool:
        """Boolean reflection of the ``controls`` attribute.

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.controls
        False
        >>> media.set_attribute("controls", "")
        >>> media.controls
        True
        """
        return self.has_attribute("controls")

    @property
    def loop(self) -> bool:
        """Boolean reflection of the ``loop`` attribute.

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.loop
        False
        >>> media.set_attribute("loop", "")
        >>> media.loop
        True
        """
        return self.has_attribute("loop")

    @property
    def muted(self) -> bool:
        """Boolean reflection of the ``muted`` attribute.

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.muted
        False
        >>> media.set_attribute("muted", "")
        >>> media.muted
        True
        """
        return self.has_attribute("muted")

    @property
    def preload(self) -> str:
        """The ``preload`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.preload
        ''
        >>> media.set_attribute("preload", "metadata")
        >>> media.preload
        'metadata'
        """
        return self.get_attribute("preload") or ""

    @property
    def cross_origin(self) -> str | None:
        """The ``crossorigin`` attribute value, or ``None`` when absent.

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.cross_origin is None
        True
        >>> media.set_attribute("crossorigin", "anonymous")
        >>> media.cross_origin
        'anonymous'
        """
        return self.get_attribute("crossorigin")

    @property
    def paused(self) -> bool:
        """Playback paused state (stub, always ``True``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").paused
        True
        """
        return True

    @property
    def ended(self) -> bool:
        """Playback ended state (stub, always ``False``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").ended
        False
        """
        return False

    @property
    def duration(self) -> float:
        """Media duration in seconds (stub, always NaN).

        >>> import math
        >>> from aspose_html.dom import Document
        >>> math.isnan(Document().create_element("audio").duration)
        True
        """
        return float("nan")

    @property
    def current_time(self) -> float:
        """Current playback position in seconds (stub, always ``0.0``).

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.current_time
        0.0
        >>> media.current_time = 12.5
        >>> media.current_time
        0.0
        """
        return 0.0

    @current_time.setter
    def current_time(self, value: float) -> None:
        """Set playback position (stub no-op).

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.current_time = 3.0
        >>> media.current_time
        0.0
        """

    @property
    def volume(self) -> float:
        """Audio volume level (stub, always ``1.0``).

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.volume
        1.0
        >>> media.volume = 0.2
        >>> media.volume
        1.0
        """
        return 1.0

    @volume.setter
    def volume(self, value: float) -> None:
        """Set volume level (stub no-op).

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.volume = 0.5
        >>> media.volume
        1.0
        """

    @property
    def default_muted(self) -> bool:
        """Default muted state reflected from ``muted`` attribute.

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.default_muted
        False
        >>> media.set_attribute("muted", "")
        >>> media.default_muted
        True
        """
        return self.has_attribute("muted")

    @property
    def ready_state(self) -> int:
        """Readiness state (stub, always ``0`` = HAVE_NOTHING).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").ready_state
        0
        """
        return 0

    @property
    def network_state(self) -> int:
        """Network state (stub, always ``0`` = NETWORK_EMPTY).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").network_state
        0
        """
        return 0

    def play(self) -> None:
        """Start playback (stub no-op).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").play()  # no exception
        """

    def pause(self) -> None:
        """Pause playback (stub no-op).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").pause()  # no exception
        """

    def load(self) -> None:
        """Reload media resource selection (stub no-op).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").load()  # no exception
        """

    @property
    def buffered(self) -> "_TimeRanges":
        """Buffered time ranges (stub, always empty).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").buffered.length
        0
        """
        return _TimeRanges()

    @property
    def played(self) -> "_TimeRanges":
        """Played time ranges (stub, always empty).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").played.length
        0
        """
        return _TimeRanges()

    @property
    def seekable(self) -> "_TimeRanges":
        """Seekable time ranges (stub, always empty).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").seekable.length
        0
        """
        return _TimeRanges()

    def can_play_type(self, type: str) -> str:
        """Return ``''`` — headless mode cannot play any media type.

        WHATWG HTML §4.8.11.7: returns ``""`` (empty string) when the type
        is not supported.

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").can_play_type("video/mp4")
        ''
        """
        return ""

    @property
    def seeking(self) -> bool:
        """Whether the element is currently seeking (stub, always ``False``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").seeking
        False
        """
        return False

    @property
    def default_playback_rate(self) -> float:
        """Default playback rate (headless default ``1.0``).

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.default_playback_rate
        1.0
        >>> media.default_playback_rate = 2.0
        >>> media.default_playback_rate
        2.0
        """
        return getattr(self, "_default_playback_rate", 1.0)

    @default_playback_rate.setter
    def default_playback_rate(self, value: float) -> None:
        object.__setattr__(self, "_default_playback_rate", float(value))

    @property
    def playback_rate(self) -> float:
        """Current playback rate (headless default ``1.0``).

        >>> from aspose_html.dom import Document
        >>> media = Document().create_element("audio")
        >>> media.playback_rate
        1.0
        >>> media.playback_rate = 0.5
        >>> media.playback_rate
        0.5
        """
        return getattr(self, "_playback_rate", 1.0)

    @playback_rate.setter
    def playback_rate(self, value: float) -> None:
        object.__setattr__(self, "_playback_rate", float(value))

    @property
    def media_keys(self) -> None:
        """Associated MediaKeys object (stub, always ``None``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").media_keys is None
        True
        """
        return None

    @property
    def src_object(self) -> None:
        """Associated MediaStream/Blob (stub, always ``None``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").src_object is None
        True
        """
        return None

    @property
    def error(self) -> None:
        """Last media error (stub, always ``None``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").error is None
        True
        """
        return None

    @property
    def text_tracks(self) -> "_EmptyTrackList":
        """Text track list (stub, always empty).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").text_tracks.length
        0
        """
        return _EmptyTrackList()

    @property
    def audio_tracks(self) -> "_EmptyTrackList":
        """Audio track list (stub, always empty).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").audio_tracks.length
        0
        """
        return _EmptyTrackList()

    @property
    def video_tracks(self) -> "_EmptyTrackList":
        """Video track list (stub, always empty).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").video_tracks.length
        0
        """
        return _EmptyTrackList()

    def add_text_track(
        self, kind: str, label: str = "", language: str = ""
    ) -> None:
        """Add a text track (stub no-op, returns ``None``).

        WHATWG HTML §4.8.10.12.5 — headless mode has no text-track pipeline.

        >>> from aspose_html.dom import Document
        >>> Document().create_element("audio").add_text_track("subtitles") is None
        True
        """
        return None


class HTMLVideoElement(HTMLMediaElement):
    """HTML ``<video>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLVideoElement
    >>> isinstance(Document().create_element("video"), HTMLVideoElement)
    True
    """

    __slots__ = ()

    @property
    def width(self) -> int:
        """The ``width`` attribute as integer (default ``0``).

        >>> from aspose_html.dom import Document
        >>> video = Document().create_element("video")
        >>> video.width
        0
        >>> video.width = 640
        >>> video.width
        640
        """
        try:
            return int(self.get_attribute("width") or "0")
        except ValueError:
            return 0

    @width.setter
    def width(self, value: int) -> None:
        self.set_attribute("width", str(value))

    @property
    def height(self) -> int:
        """The ``height`` attribute as integer (default ``0``).

        >>> from aspose_html.dom import Document
        >>> video = Document().create_element("video")
        >>> video.height
        0
        >>> video.height = 360
        >>> video.height
        360
        """
        try:
            return int(self.get_attribute("height") or "0")
        except ValueError:
            return 0

    @height.setter
    def height(self, value: int) -> None:
        self.set_attribute("height", str(value))

    @property
    def video_width(self) -> int:
        """Intrinsic video width (stub, always ``0``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("video").video_width
        0
        """
        return 0

    @property
    def video_height(self) -> int:
        """Intrinsic video height (stub, always ``0``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("video").video_height
        0
        """
        return 0

    @property
    def poster(self) -> str:
        """The ``poster`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> video = Document().create_element("video")
        >>> video.poster
        ''
        >>> video.poster = "thumb.jpg"
        >>> video.poster
        'thumb.jpg'
        """
        return self.get_attribute("poster") or ""

    @poster.setter
    def poster(self, value: str) -> None:
        self.set_attribute("poster", value)

    @property
    def plays_inline(self) -> bool:
        """Whether the ``playsinline`` boolean attribute is present.

        Reflects ``playsinline`` (WHATWG HTML §4.8.9).

        >>> from aspose_html.dom import Document
        >>> video = Document().create_element("video")
        >>> video.plays_inline
        False
        >>> video.plays_inline = True
        >>> video.plays_inline
        True
        >>> video.plays_inline = False
        >>> video.plays_inline
        False
        """
        return self.has_attribute("playsinline")

    @plays_inline.setter
    def plays_inline(self, value: bool) -> None:
        if value:
            self.set_attribute("playsinline", "")
        else:
            self.remove_attribute("playsinline")

    @property
    def disable_picture_in_picture(self) -> bool:
        """Boolean attribute reflection for ``disablepictureinpicture``.

        Returns ``True`` when the ``disablepictureinpicture`` boolean attribute
        is present on the element; ``False`` when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> doc = Document()
        >>> vid = doc.create_element("video")
        >>> vid.disable_picture_in_picture
        False
        >>> vid.set_attribute("disablepictureinpicture", "")
        >>> vid.disable_picture_in_picture
        True
        """
        return self.has_attribute("disablepictureinpicture")

    @disable_picture_in_picture.setter
    def disable_picture_in_picture(self, value: bool) -> None:
        if value:
            self.set_attribute("disablepictureinpicture", "")
        else:
            self.remove_attribute("disablepictureinpicture")

    def request_picture_in_picture(self) -> None:
        """Raise ``NotSupportedError`` — PiP is unavailable in headless mode.

        Picture-in-Picture API §4.3: in a rendering environment this returns
        a ``PictureInPictureWindow`` Promise. Headless mode has no PiP pipeline.

        Raises
        ------
        NotSupportedError
            Always — Picture-in-Picture is not supported in headless mode.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> from aspose_html.dom._exceptions import NotSupportedError
        >>> doc = Document()
        >>> vid = doc.create_element("video")
        >>> vid.request_picture_in_picture()
        Traceback (most recent call last):
            ...
        aspose_html.dom._exceptions.NotSupportedError: ...
        """
        from aspose_html.dom._exceptions import NotSupportedError  # noqa: PLC0415
        raise NotSupportedError(
            "requestPictureInPicture is not supported in headless mode"
            " (Picture-in-Picture API §4.3)"
        )

    @property
    def webkit_decoded_frame_count(self) -> int:
        """Number of decoded video frames (stub, always ``0``).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("video").webkit_decoded_frame_count
        0
        """
        return 0

    @property
    def webkit_dropped_frame_count(self) -> int:
        """Number of dropped video frames (headless stub — always ``0``).

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> Document().create_element("video").webkit_dropped_frame_count
        0
        """
        return 0


class HTMLAudioElement(HTMLMediaElement):
    """HTML ``<audio>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLAudioElement
    >>> el = Document().create_element("audio")
    >>> isinstance(el, HTMLAudioElement)
    True
    >>> el.paused
    True
    """

    __slots__ = ()



class HTMLSourceElement(HTMLElement):
    """HTML ``<source>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLSourceElement
    >>> el = Document().create_element("source")
    >>> isinstance(el, HTMLSourceElement)
    True
    >>> el.src = "clip.mp4"
    >>> el.src
    'clip.mp4'
    """

    __slots__ = ()

    @property
    def src(self) -> str:
        """The ``src`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> source = Document().create_element("source")
        >>> source.src
        ''
        >>> source.src = "video.mp4"
        >>> source.src
        'video.mp4'
        """
        return self.get_attribute("src") or ""

    @src.setter
    def src(self, value: str) -> None:
        self.set_attribute("src", value)

    @property
    def type(self) -> str:
        """The ``type`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> source = Document().create_element("source")
        >>> source.type
        ''
        >>> source.type = "video/mp4"
        >>> source.type
        'video/mp4'
        """
        return self.get_attribute("type") or ""

    @type.setter
    def type(self, value: str) -> None:
        self.set_attribute("type", value)

    @property
    def srcset(self) -> str:
        """The ``srcset`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> source = Document().create_element("source")
        >>> source.srcset
        ''
        >>> source.srcset = "small.png 1x, large.png 2x"
        >>> source.srcset
        'small.png 1x, large.png 2x'
        """
        return self.get_attribute("srcset") or ""

    @srcset.setter
    def srcset(self, value: str) -> None:
        self.set_attribute("srcset", value)

    @property
    def sizes(self) -> str:
        """The ``sizes`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> source = Document().create_element("source")
        >>> source.sizes
        ''
        >>> source.sizes = "(max-width: 600px) 100vw, 50vw"
        >>> source.sizes
        '(max-width: 600px) 100vw, 50vw'
        """
        return self.get_attribute("sizes") or ""

    @sizes.setter
    def sizes(self, value: str) -> None:
        self.set_attribute("sizes", value)

    @property
    def media(self) -> str:
        """The ``media`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> source = Document().create_element("source")
        >>> source.media
        ''
        >>> source.media = "screen and (min-width: 800px)"
        >>> source.media
        'screen and (min-width: 800px)'
        """
        return self.get_attribute("media") or ""

    @media.setter
    def media(self, value: str) -> None:
        self.set_attribute("media", value)

    # -- ,  — IDL tail ----------------------------------------

    @property
    def type_(self) -> str:
        """Reflects the ``type`` content attribute (WHATWG HTML §4.8.8).

        IDL snake_case alias for :attr:`type`, following the ``type_``
        convention. Returns an empty string when absent.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> source = Document().create_element("source")
        >>> source.type_
        ''
        >>> source.set_attribute("type", "video/mp4")
        >>> source.type_
        'video/mp4'
        """
        return self.get_attribute("type") or ""

    @property
    def width(self) -> int:
        """Reflects the ``width`` content attribute as an integer (default 0).

        WHATWG HTML §4.8.8 — for use in ``<picture>`` source descriptors.
        Returns 0 when absent or non-numeric.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> source = Document().create_element("source")
        >>> source.width
        0
        >>> source.set_attribute("width", "800")
        >>> source.width
        800
        >>> source.set_attribute("width", "notanumber")
        >>> source.width
        0
        """
        try:
            return int(self.get_attribute("width") or 0)
        except (ValueError, TypeError):
            return 0

    @property
    def height(self) -> int:
        """Reflects the ``height`` content attribute as an integer (default 0).

        WHATWG HTML §4.8.8.
        Returns 0 when absent or non-numeric.

        Examples
        --------
        >>> from aspose_html.dom import Document
        >>> source = Document().create_element("source")
        >>> source.height
        0
        >>> source.set_attribute("height", "600")
        >>> source.height
        600
        >>> source.set_attribute("height", "notanumber")
        >>> source.height
        0
        """
        try:
            return int(self.get_attribute("height") or 0)
        except (ValueError, TypeError):
            return 0


class HTMLTrackElement(HTMLElement):
    """HTML ``<track>`` element.

    Examples
    --------
    >>> from aspose_html.dom import Document, HTMLTrackElement
    >>> el = Document().create_element("track")
    >>> isinstance(el, HTMLTrackElement)
    True
    >>> el.ready_state
    0
    """

    __slots__ = ()

    @property
    def kind(self) -> str:
        """The ``kind`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> track = Document().create_element("track")
        >>> track.kind
        ''
        >>> track.kind = "subtitles"
        >>> track.kind
        'subtitles'
        """
        return self.get_attribute("kind") or ""

    @kind.setter
    def kind(self, value: str) -> None:
        self.set_attribute("kind", value)

    @property
    def src(self) -> str:
        """The ``src`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> track = Document().create_element("track")
        >>> track.src
        ''
        >>> track.src = "captions.vtt"
        >>> track.src
        'captions.vtt'
        """
        return self.get_attribute("src") or ""

    @src.setter
    def src(self, value: str) -> None:
        self.set_attribute("src", value)

    @property
    def srclang(self) -> str:
        """The ``srclang`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> track = Document().create_element("track")
        >>> track.srclang
        ''
        >>> track.srclang = "en"
        >>> track.srclang
        'en'
        """
        return self.get_attribute("srclang") or ""

    @srclang.setter
    def srclang(self, value: str) -> None:
        self.set_attribute("srclang", value)

    @property
    def label(self) -> str:
        """The ``label`` attribute value, or ``''`` when absent.

        >>> from aspose_html.dom import Document
        >>> track = Document().create_element("track")
        >>> track.label
        ''
        >>> track.label = "English"
        >>> track.label
        'English'
        """
        return self.get_attribute("label") or ""

    @label.setter
    def label(self, value: str) -> None:
        self.set_attribute("label", value)

    @property
    def default(self) -> bool:
        """Boolean reflection of the ``default`` attribute.

        >>> from aspose_html.dom import Document
        >>> track = Document().create_element("track")
        >>> track.default
        False
        >>> track.default = True
        >>> track.default
        True
        """
        return self.has_attribute("default")

    @default.setter
    def default(self, value: bool) -> None:
        if value:
            self.set_attribute("default", "")
        else:
            self.remove_attribute("default")

    @property
    def ready_state(self) -> int:
        """Readiness state (stub, always ``0`` = NONE).

        >>> from aspose_html.dom import Document
        >>> Document().create_element("track").ready_state
        0
        """
        return 0

    @property
    def track(self):
        """Returns ``None`` in headless mode.

        WHATWG HTML §4.8.10 — ``TextTrack`` objects require a media pipeline
        that does not exist in headless operation.

        >>> from aspose_html.dom import Document
        >>> Document().create_element("track").track is None
        True
        """
        return None



