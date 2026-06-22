"""WHATWG URL Standard surface.

Examples
--------
>>> u = URL("https://example.com/path?a=1#frag")
>>> u.hostname
'example.com'
>>> u.search
'?a=1'
"""
from __future__ import annotations

import re
from urllib.parse import SplitResult
from urllib.parse import urljoin, urlsplit, urlunsplit

from aspose_html.url._search_params import URLSearchParams


class URLParseError(ValueError):
    """Raised when a string cannot be parsed as a URL."""


class URL:
    __slots__ = ("_href", "_search_params")

    @staticmethod
    def parse(input: str, base: str | "URL" | None = None) -> "URL | None":
        """Return a ``URL`` instance, or ``None`` if the input is invalid.

        Unlike the ``URL`` constructor which raises ``URLParseError``,
        this method returns ``None`` when parsing fails, following the
        WHATWG URL Standard §5.1.

        Parameters
        ----------
        input : str
            The URL string to parse.
        base : str, URL, or None
            Optional base URL for resolving relative references.

        Returns
        -------
        URL or None
            A ``URL`` instance on success; ``None`` if parsing would raise
            ``URLParseError``.

        Examples
        --------
        >>> URL.parse("https://example.com").href
        'https://example.com'
        >>> URL.parse("http://%") is None
        True
        >>> URL.parse("page", base="https://example.com/root/").href
        'https://example.com/root/page'
        """
        try:
            return URL(input, base)
        except URLParseError:
            return None

    @staticmethod
    def can_parse(input: str, base: str | "URL" | None = None) -> bool:
        """Return ``True`` when URL construction would succeed.

        The probe follows the same parser path as ``URL(input, base)`` while
        suppressing only ``URLParseError``.

        >>> URL.can_parse("https://example.com")
        True
        >>> URL.can_parse("http://%")
        False
        >>> URL.can_parse("page", base="https://example.com/root/")
        True
        >>> URL.can_parse("page")
        True
        """
        try:
            URL(input, base)
        except URLParseError:
            return False
        return True

    def __init__(self, href: str, base: str | "URL" | None = None) -> None:
        base_str = base.href if hasattr(base, "href") else (base or "")
        self._search_params = None
        self.href = urljoin(str(base_str), str(href))

    def _validate(self, value: str) -> str:
        parts = urlsplit(value)
        scheme = (parts.scheme or "").lower()
        if re.search(r"%(?![0-9A-Fa-f]{2})", value):
            raise URLParseError(f"Invalid URL: {value!r}")
        if scheme not in {"data", "javascript", "mailto", "blob", "file", "about"}:
            if not (parts.scheme or parts.netloc or parts.path):
                raise URLParseError(f"Invalid URL: {value!r}")
        canonical = self._canonicalize_parts(parts._replace(scheme=scheme))
        return urlunsplit(canonical)

    def _canonicalize_parts(self, parts: SplitResult) -> SplitResult:
        scheme = (parts.scheme or "").lower()
        path = parts.path
        if scheme in {"http", "https", "ftp", "ws", "wss"} and parts.netloc:
            path = self._collapse_dot_segments(path)

        query = parts.query
        fragment = parts.fragment
        return parts._replace(path=path, query=query, fragment=fragment)

    @staticmethod
    def _collapse_dot_segments(path: str) -> str:
        if not path:
            return path

        is_absolute = path.startswith("/")
        trailing_slash = path.endswith("/")
        collapsed: list[str] = []
        for segment in path.split("/"):
            if segment in ("", "."):
                continue
            if segment == "..":
                if collapsed:
                    collapsed.pop()
                continue
            collapsed.append(segment)

        normalized = "/".join(collapsed)
        if is_absolute:
            normalized = f"/{normalized}" if normalized else "/"
        if trailing_slash and normalized and not normalized.endswith("/"):
            normalized = f"{normalized}/"
        if not is_absolute and not normalized and trailing_slash:
            normalized = "/"
        return normalized

    @property
    def href(self) -> str:
        """Return the serialized URL string.

        >>> URL("https://example.com").href
        'https://example.com'
        """
        return self._href

    @href.setter
    def href(self, value: str) -> None:
        self._href = self._validate(str(value))
        if self._search_params is not None:
            self._search_params._refresh_from_string(urlsplit(self._href).query)

    @property
    def protocol(self) -> str:
        p = urlsplit(self._href)
        return f"{p.scheme}:" if p.scheme else ""

    @protocol.setter
    def protocol(self, value: str) -> None:
        p = urlsplit(self._href)
        self.href = urlunsplit(p._replace(scheme=str(value).rstrip(":").lower()))

    @property
    def username(self) -> str:
        """Return username from URL userinfo.

        >>> URL("https://u:p@example.com/").username
        'u'
        """
        return urlsplit(self._href).username or ""

    @username.setter
    def username(self, value: str) -> None:
        p = urlsplit(self._href)
        password = p.password or ""
        host = p.hostname or ""
        port = f":{p.port}" if p.port else ""
        username = str(value)
        userinfo = f"{username}:{password}@" if (username or password) else ""
        self.href = urlunsplit(p._replace(netloc=f"{userinfo}{host}{port}"))

    @property
    def password(self) -> str:
        """Return password from URL userinfo.

        >>> URL("https://u:p@example.com/").password
        'p'
        """
        return urlsplit(self._href).password or ""

    @password.setter
    def password(self, value: str) -> None:
        p = urlsplit(self._href)
        username = p.username or ""
        host = p.hostname or ""
        port = f":{p.port}" if p.port else ""
        password = str(value)
        userinfo = f"{username}:{password}@" if (username or password) else ""
        self.href = urlunsplit(p._replace(netloc=f"{userinfo}{host}{port}"))

    @property
    def host(self) -> str:
        return urlsplit(self._href).netloc.split("@", 1)[-1]

    @host.setter
    def host(self, value: str) -> None:
        p = urlsplit(self._href)
        username = p.username or ""
        password = p.password or ""
        userinfo = f"{username}:{password}@" if (username or password) else ""
        self.href = urlunsplit(p._replace(netloc=f"{userinfo}{str(value)}"))

    @property
    def hostname(self) -> str:
        return urlsplit(self._href).hostname or ""

    @hostname.setter
    def hostname(self, value: str) -> None:
        p = urlsplit(self._href)
        username = p.username or ""
        password = p.password or ""
        port = f":{p.port}" if p.port else ""
        userinfo = f"{username}:{password}@" if (username or password) else ""
        self.href = urlunsplit(p._replace(netloc=f"{userinfo}{str(value)}{port}"))

    @property
    def port(self) -> str:
        p = urlsplit(self._href)
        return str(p.port) if p.port else ""

    @port.setter
    def port(self, value: str) -> None:
        p = urlsplit(self._href)
        username = p.username or ""
        password = p.password or ""
        hostname = p.hostname or ""
        userinfo = f"{username}:{password}@" if (username or password) else ""
        port = str(value).lstrip(":")
        port_part = f":{port}" if port else ""
        self.href = urlunsplit(p._replace(netloc=f"{userinfo}{hostname}{port_part}"))

    @property
    def pathname(self) -> str:
        return urlsplit(self._href).path

    @pathname.setter
    def pathname(self, value: str) -> None:
        p = urlsplit(self._href)
        self.href = urlunsplit(p._replace(path=str(value)))

    @property
    def search(self) -> str:
        p = urlsplit(self._href)
        return f"?{p.query}" if p.query else ""

    @search.setter
    def search(self, value: str) -> None:
        p = urlsplit(self._href)
        self.href = urlunsplit(p._replace(query=str(value).lstrip("?")))

    @property
    def hash(self) -> str:
        p = urlsplit(self._href)
        return f"#{p.fragment}" if p.fragment else ""

    @hash.setter
    def hash(self, value: str) -> None:
        p = urlsplit(self._href)
        self.href = urlunsplit(p._replace(fragment=str(value).lstrip("#")))

    @property
    def origin(self) -> str:
        p = urlsplit(self._href)
        if p.scheme in {"http", "https", "ftp", "ws", "wss"} and p.netloc:
            port = f":{p.port}" if p.port else ""
            return f"{p.scheme}://{p.hostname or ''}{port}"
        return "null"

    @property
    def search_params(self) -> URLSearchParams:
        if self._search_params is None:
            params = URLSearchParams(urlsplit(self._href).query)
            params._url_ref = self
            self._search_params = params
        else:
            self._search_params._refresh_from_string(urlsplit(self._href).query)
        return self._search_params

    def _set_search_from_params(self, params: URLSearchParams) -> None:
        p = urlsplit(self._href)
        self.href = urlunsplit(p._replace(query=str(params)))

    def __str__(self) -> str:
        return self._href

    def __repr__(self) -> str:
        return f"URL({self._href!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, URL):
            return NotImplemented
        return self._href == other._href

    def __hash__(self) -> int:
        return hash(self._href)
