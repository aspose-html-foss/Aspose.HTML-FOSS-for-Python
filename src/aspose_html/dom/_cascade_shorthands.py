"""Shorthand expansion helpers and CSS value tokenizer utilities.

Depends only on _cascade_data. See ADR-306.
"""
from __future__ import annotations

import re
from typing import Iterator

from aspose_html.dom._cascade_data import (
    _SHORTHAND_EXPANSIONS, _TWO_VALUE_AXIS, _LOGICAL_BORDER_SIDE_SHORTHANDS,
    _LOGICAL_BORDER_AXIS_SHORTHANDS, _BORDER_STYLE_TOKENS,
    _BORDER_WIDTH_LENGTH_RE, _LOGICAL_PROPERTY_ALIASES,
    _INITIAL_VALUE_BASELINE, _ANIMATION_TIME_RE, _VAR_FUNCTION_FULL_RE,
    _ENV_FUNCTION_FULL_RE, _BACKGROUND_NON_COLOR_KEYWORDS,
    _FONT_STYLE_TOKENS, _FONT_VARIANT_TOKENS, _FONT_WEIGHT_TOKENS,
    _FONT_STRETCH_TOKENS, _FONT_SIZE_RE, _FONT_SYSTEM_KEYWORDS,
    _LIST_STYLE_POSITION_TOKENS, _LIST_STYLE_TYPE_TOKENS,
    _TEXT_DECORATION_LINE_TOKENS, _TEXT_DECORATION_STYLE_TOKENS,
    _TEXT_DECORATION_THICKNESS_RE, _CSS_COLOR_KEYWORDS,
    _OUTLINE_STYLE_TOKENS, _OUTLINE_WIDTH_RE,
)


def _tokenize_css_value(s: str) -> list[str]:
    """Split a CSS value string on whitespace at paren-depth 0.

    Treats ``var(--x, y)`` and ``env(name, fallback)`` as single atomic tokens.
    Equivalent to ``str.split()`` for values that contain no function calls.

    Examples
    --------
    >>> _tokenize_css_value("8px 16px")
    ['8px', '16px']
    >>> _tokenize_css_value("var(--space, 8px)")
    ['var(--space, 8px)']
    >>> _tokenize_css_value("var(--w) auto")
    ['var(--w)', 'auto']
    >>> _tokenize_css_value("4px var(--gap, 2px) 4px")
    ['4px', 'var(--gap, 2px)', '4px']
    >>> _tokenize_css_value("single")
    ['single']
    >>> _tokenize_css_value("")
    []
    """
    tokens: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in s:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch in " \t\n\r\f" and depth == 0:
            token = "".join(current).strip()
            if token:
                tokens.append(token)
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        tokens.append(tail)
    return tokens


def _split_top_level(text: str, separator: str) -> list[str]:
    """Split *text* on *separator* only at paren-nesting depth 0.

    Returns a list with one item when the separator is not found at
    depth 0, making it safe to use as a "did we find a top-level
    separator?" check.
    """
    parts: list[str] = []
    depth = 0
    start = 0
    sep_len = len(separator)
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0 and text[i : i + sep_len] == separator:
            parts.append(text[start:i].strip())
            start = i + sep_len
            i += sep_len
            continue
        i += 1
    parts.append(text[start:].strip())
    return parts


def _outer_parens_balanced(text: str) -> bool:
    """Return True when the opening ``(`` at index 0 closes at the last index."""
    depth = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i == len(text) - 1
    return False


def _looks_like_full_value_var_call(value: str) -> bool:
    """Return whether *value* is shaped as a top-level ``var(...)`` call."""
    trimmed = value.strip().lower()
    return trimmed.startswith("var(") and trimmed.endswith(")")


def _looks_like_full_value_env_call(value: str) -> bool:
    """Return whether *value* is shaped as a top-level ``env(...)`` call.

    Used by shorthand broadcast guards to pass ``env(...)`` through unchanged
    to all longhands, parallel to the ``var(...)`` guard.

    Examples
    --------
    >>> _looks_like_full_value_env_call("env(safe-area-inset-top, 12px)")
    True
    >>> _looks_like_full_value_env_call("ENV(safe-area-inset-top)")
    True
    >>> _looks_like_full_value_env_call("var(--x)")
    False
    >>> _looks_like_full_value_env_call("4px")
    False
    """
    trimmed = value.strip().lower()
    return trimmed.startswith("env(") and trimmed.endswith(")")


def _resolve_env_function(value: str) -> str | None:
    """Resolve a full-value ``env(...)`` call to its fallback in headless mode.

    CSS Environment Variables §2: when no env var is defined (headless mode),
    the fallback argument is used.  ``env(name)`` with no fallback resolves to
    ``None`` (caller drops the declaration).

    Returns the fallback string when a comma-separated fallback exists.
    Returns ``None`` when no fallback is present, the fallback is empty, or
    the value is not an ``env(...)`` call (caller skips this path).

    Examples
    --------
    >>> _resolve_env_function("env(safe-area-inset-top, 12px)")
    '12px'
    >>> _resolve_env_function("env(safe-area-inset-top)") is None
    True
    >>> _resolve_env_function("env(--brand, red)")
    'red'
    >>> _resolve_env_function("4px") is None
    True
    >>> _resolve_env_function("env(--x, )") is None
    True
    """
    trimmed = value.strip()
    if not trimmed.lower().startswith("env("):
        return None
    match = _ENV_FUNCTION_FULL_RE.fullmatch(trimmed)
    if match is None:
        return None
    inner = match.group(1).strip()
    _name_part, has_comma, fallback_part = inner.partition(",")
    if not has_comma:
        return None  # no fallback — caller drops declaration
    fallback = fallback_part.strip()
    return fallback if fallback else None


def _looks_like_background_image_token(token: str) -> bool:
    """Return True when *token* is an image-slot token for shorthand splitting."""
    lowered = token.strip().lower()
    return lowered == "none" or lowered.startswith("url(")


def _looks_like_color_token(token: str) -> bool:
    """Return True when *token* looks like a CSS color value.

    Accepts hex colors, functional color notations (``rgb()``, ``rgba()``,
    ``hsl()``, ``hsla()``), and alphabetic tokens that are not known
    layout/geometry keywords.  Never raises.

    >>> _looks_like_color_token("red")
    True
    >>> _looks_like_color_token("#fff")
    True
    >>> _looks_like_color_token("rgba(0,0,0,0.5)")
    True
    >>> _looks_like_color_token("center")
    False
    >>> _looks_like_color_token("url(a.png)")
    False
    """
    lowered = token.strip().lower()
    if lowered.startswith("#"):
        return True
    for prefix in ("rgb(", "rgba(", "hsl(", "hsla(", "color("):
        if lowered.startswith(prefix):
            return True
    if lowered.startswith("url(") or lowered.startswith("linear-gradient(") or lowered.startswith("radial-gradient("):
        return False
    # Plain alphabetic token: color if not a known non-color keyword
    if re.match(r"^[a-z]+(-[a-z]+)*$", lowered):
        return lowered not in _BACKGROUND_NON_COLOR_KEYWORDS
    return False


def _is_css_color_token(token: str) -> bool:
    """Return True when *token* is a CSS color value (named, hex, or functional)."""
    lowered = token.strip().lower()
    if lowered.startswith("#"):
        return True
    if (
        lowered.startswith("rgb(")
        or lowered.startswith("rgba(")
        or lowered.startswith("hsl(")
        or lowered.startswith("hsla(")
    ):
        return True
    return lowered in _CSS_COLOR_KEYWORDS


def _looks_like_number_token(token: str) -> bool:
    """Return True when *token* is a plain CSS number token."""
    try:
        float(token)
    except ValueError:
        return False
    return True


def _is_border_width_token(token: str) -> bool:
    """Return whether *token* matches deterministic border-width baseline."""
    lowered = token.strip().lower()
    if lowered in {"thin", "medium", "thick", "0"}:
        return True
    return bool(_BORDER_WIDTH_LENGTH_RE.fullmatch(lowered))


def _is_border_style_token(token: str) -> bool:
    """Return whether *token* matches deterministic border-style baseline."""
    return token.strip().lower() in _BORDER_STYLE_TOKENS


def _is_border_color_token(token: str) -> bool:
    """Return whether *token* is accepted as deterministic border color slot."""
    stripped = token.strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    if lowered in {"inherit", "initial", "unset"}:
        return False
    return True


def _expand_four_side_values(tokens: list[str]) -> tuple[str, str, str, str]:
    """Expand 1-4 shorthand tokens to four side/corner slots."""
    if len(tokens) == 1:
        return (tokens[0], tokens[0], tokens[0], tokens[0])
    if len(tokens) == 2:
        return (tokens[0], tokens[1], tokens[0], tokens[1])
    if len(tokens) == 3:
        return (tokens[0], tokens[1], tokens[2], tokens[1])
    return (tokens[0], tokens[1], tokens[2], tokens[3])


def _expand_shorthand_value(property_name: str, raw_value: str) -> dict[str, str] | None:
    """Expand supported shorthand families into longhand values.

    Returns ``None`` when *property_name* is not a supported shorthand.
    Returns an empty dict when the shorthand shape is unsupported and should be
    ignored deterministically.
    """
    longhands = _SHORTHAND_EXPANSIONS.get(property_name)
    if longhands is None:
        return None

    if property_name in {
        "border", "border-top", "border-right", "border-bottom", "border-left"
    } | _LOGICAL_BORDER_SIDE_SHORTHANDS:
        return _expand_border_shorthand(property_name, raw_value)

    # --- NEW: Track 92, ADR-291 ---
    if property_name in _LOGICAL_BORDER_AXIS_SHORTHANDS:
        return _expand_border_axis_shorthand(property_name, raw_value)

    if property_name in _TWO_VALUE_AXIS:
        return _expand_two_value_axis_shorthand(property_name, raw_value)

    if property_name == "background":
        return _expand_background_shorthand(raw_value)

    if property_name == "border-radius":
        return _expand_border_radius_shorthand(raw_value)

    if property_name == "animation":
        return _expand_animation_shorthand(raw_value)

    # --- NEW: Track 97, ADR-296 — semantic shorthand helpers ---
    if property_name == "transition":
        return _expand_transition_shorthand(raw_value)

    if property_name == "flex":
        return _expand_flex_shorthand(raw_value)

    # --- NEW: Track 88, ADR-287 — semantic shorthand helpers ---
    if property_name == "font":
        return _expand_font_shorthand(raw_value)

    if property_name == "list-style":
        return _expand_list_style_shorthand(raw_value)

    if property_name == "text-decoration":
        return _expand_text_decoration_shorthand(raw_value)

    if property_name == "outline":
        return _expand_outline_shorthand(raw_value)

    # ``inset`` requires no custom dispatch: the generic 1-4 token box-model
    # mapper below handles it correctly (same positional-broadcast rules as
    # margin/padding).

    # --- NEW: Track 94, ADR-293 — mask 8-longhand positional broadcast ---
    # The mask shorthand has 8 longhands (not a standard 4-box broadcast).
    # Tokens are distributed positionally; surplus tokens beyond 8 are ignored.
    # Multi-layer (comma-separated) declarations are stored as-is in longhands.
    if property_name == "mask":
        longhands = _SHORTHAND_EXPANSIONS["mask"]
        tokens = _tokenize_css_value(raw_value)
        result: dict[str, str] = {lh: "" for lh in longhands}
        for i, token in enumerate(tokens):
            if i < len(longhands):
                result[longhands[i]] = token
        return result

    # --- NEW: Track 89, ADR-288 --- slash-aware grid sub-shorthand helpers ---
    if property_name == "grid-column":
        return _expand_grid_placement_shorthand(raw_value, "grid-column-start", "grid-column-end")

    if property_name == "grid-row":
        return _expand_grid_placement_shorthand(raw_value, "grid-row-start", "grid-row-end")

    if property_name == "grid-area":
        return _expand_grid_area_shorthand(raw_value)

    if property_name == "grid-template":
        return _expand_grid_template_shorthand(raw_value)

    # --- NEW: Track 108, ADR-307 — CSS Container Queries Level 1 §3.1 ---
    if property_name == "container":
        return _expand_container_shorthand(raw_value)

    tokens = _tokenize_css_value(raw_value)
    token_count = len(tokens)
    if token_count == 1:
        # Broadcast single token to all longhands (same-value broadcast).
        # This handles shorthands with more than 4 sub-properties (e.g.
        # ``background`` with 8, ``animation`` with 8).
        return {name: tokens[0] for name in longhands}
    elif token_count == 2:
        mapped_values = (tokens[0], tokens[1], tokens[0], tokens[1])
    elif token_count == 3:
        mapped_values = (tokens[0], tokens[1], tokens[2], tokens[1])
    elif token_count == 4:
        mapped_values = (tokens[0], tokens[1], tokens[2], tokens[3])
    else:
        return {}

    return {name: value for name, value in zip(longhands, mapped_values)}


def _expand_animation_shorthand(raw_value: str) -> dict[str, str]:
    """Expand supported single-entry ``animation`` shorthand values.

    Supported subset (ADR-277): one animation item without comma-separated
    lists. Unsupported/ambiguous forms return ``{}`` deterministically.
    """
    if "," in raw_value:
        return {}

    tokens = _tokenize_css_value(raw_value)
    if not tokens:
        return {}

    resolved: dict[str, str] = {
        "animation-name": _INITIAL_VALUE_BASELINE["animation-name"],
        "animation-duration": _INITIAL_VALUE_BASELINE["animation-duration"],
        "animation-timing-function": _INITIAL_VALUE_BASELINE["animation-timing-function"],
        "animation-delay": _INITIAL_VALUE_BASELINE["animation-delay"],
        "animation-iteration-count": _INITIAL_VALUE_BASELINE["animation-iteration-count"],
        "animation-direction": _INITIAL_VALUE_BASELINE["animation-direction"],
        "animation-fill-mode": _INITIAL_VALUE_BASELINE["animation-fill-mode"],
        "animation-play-state": _INITIAL_VALUE_BASELINE["animation-play-state"],
    }

    time_slots: list[str] = []
    seen_timing = False
    seen_iteration = False
    seen_direction = False
    seen_fill_mode = False
    seen_play_state = False
    name_token: str | None = None

    timing_keywords = {
        "linear",
        "ease",
        "ease-in",
        "ease-out",
        "ease-in-out",
        "step-start",
        "step-end",
    }
    direction_keywords = {"normal", "reverse", "alternate", "alternate-reverse"}
    fill_mode_keywords = {"none", "forwards", "backwards", "both"}
    play_state_keywords = {"running", "paused"}

    for token in tokens:
        lowered = token.lower()

        if _ANIMATION_TIME_RE.fullmatch(lowered):
            if len(time_slots) >= 2:
                return {}
            time_slots.append(token)
            continue

        if lowered in timing_keywords or lowered.startswith("cubic-bezier(") or lowered.startswith("steps("):
            if seen_timing:
                return {}
            seen_timing = True
            resolved["animation-timing-function"] = token
            continue

        if lowered == "infinite" or _looks_like_number_token(lowered):
            if seen_iteration:
                return {}
            seen_iteration = True
            resolved["animation-iteration-count"] = token
            continue

        if lowered in direction_keywords:
            if seen_direction:
                return {}
            seen_direction = True
            resolved["animation-direction"] = token
            continue

        if lowered == "none" and name_token is None:
            # Deterministic ambiguity resolution: prefer the first ``none`` as
            # animation-name; a later ``none`` can still fill fill-mode.
            name_token = token
            continue

        if lowered in fill_mode_keywords:
            if seen_fill_mode:
                return {}
            seen_fill_mode = True
            resolved["animation-fill-mode"] = token
            continue

        if lowered in play_state_keywords:
            if seen_play_state:
                return {}
            seen_play_state = True
            resolved["animation-play-state"] = token
            continue

        if name_token is not None:
            return {}
        name_token = token

    if len(time_slots) == 1:
        resolved["animation-duration"] = time_slots[0]
    elif len(time_slots) == 2:
        resolved["animation-duration"] = time_slots[0]
        resolved["animation-delay"] = time_slots[1]

    resolved["animation-name"] = name_token or _INITIAL_VALUE_BASELINE["animation-name"]
    return resolved


def _expand_transition_shorthand(raw_value: str) -> dict[str, str]:
    """Expand supported single-entry ``transition`` shorthand values.

    Per CSS Transitions §3: ``<property> || <duration> || <easing> || <delay>``.
    The first ``<time>`` token is ``transition-duration``; the second is
    ``transition-delay``.  Omitted slots get their initial values.
    Comma-separated multi-transition forms return ``{}`` (unsupported).

    >>> _expand_transition_shorthand("opacity 0.3s ease")
    {'transition-property': 'opacity', 'transition-duration': '0.3s', 'transition-timing-function': 'ease', 'transition-delay': '0s'}
    >>> _expand_transition_shorthand("all 0.5s")
    {'transition-property': 'all', 'transition-duration': '0.5s', 'transition-timing-function': 'ease', 'transition-delay': '0s'}
    >>> _expand_transition_shorthand("opacity 0.3s ease 0.1s")
    {'transition-property': 'opacity', 'transition-duration': '0.3s', 'transition-timing-function': 'ease', 'transition-delay': '0.1s'}
    >>> _expand_transition_shorthand("opacity 0.3s, transform 0.5s")
    {}
    """
    if "," in raw_value:
        return {}

    tokens = _tokenize_css_value(raw_value)
    if not tokens:
        return {}

    resolved: dict[str, str] = {
        "transition-property": _INITIAL_VALUE_BASELINE["transition-property"],
        "transition-duration": _INITIAL_VALUE_BASELINE["transition-duration"],
        "transition-timing-function": _INITIAL_VALUE_BASELINE["transition-timing-function"],
        "transition-delay": _INITIAL_VALUE_BASELINE["transition-delay"],
    }

    timing_keywords = {
        "linear", "ease", "ease-in", "ease-out", "ease-in-out",
        "step-start", "step-end",
    }

    time_slots: list[str] = []
    seen_timing = False
    property_token: str | None = None

    for token in tokens:
        lowered = token.lower()

        if _ANIMATION_TIME_RE.fullmatch(lowered):
            if len(time_slots) >= 2:
                return {}
            time_slots.append(token)
            continue

        if (
            lowered in timing_keywords
            or lowered.startswith("cubic-bezier(")
            or lowered.startswith("steps(")
        ):
            if seen_timing:
                return {}
            seen_timing = True
            resolved["transition-timing-function"] = token
            continue

        # Everything else is treated as transition-property.
        if property_token is not None:
            return {}
        property_token = token

    if len(time_slots) == 1:
        resolved["transition-duration"] = time_slots[0]
    elif len(time_slots) == 2:
        resolved["transition-duration"] = time_slots[0]
        resolved["transition-delay"] = time_slots[1]

    if property_token is not None:
        resolved["transition-property"] = property_token

    return resolved


def _expand_flex_shorthand(raw_value: str) -> dict[str, str]:
    """Expand supported ``flex`` shorthand values per CSS Flexbox §7.2.

    Canonical forms handled:

    - ``none``  → ``flex-grow:0  flex-shrink:0  flex-basis:auto``
    - ``auto``  → ``flex-grow:1  flex-shrink:1  flex-basis:auto``
    - ``<N>``   → ``flex-grow:N  flex-shrink:1  flex-basis:0%``
    - ``<N> <N>``          → ``flex-grow:N1 flex-shrink:N2 flex-basis:0%``
    - ``<N> <N> <basis>``  → positional (all three from tokens)
    - ``<N> <basis>``      → ``flex-grow:N  flex-shrink:1  flex-basis:<basis>``

    Returns ``{}`` for any other form (4+ tokens, unrecognised keyword).

    >>> _expand_flex_shorthand("none")
    {'flex-grow': '0', 'flex-shrink': '0', 'flex-basis': 'auto'}
    >>> _expand_flex_shorthand("auto")
    {'flex-grow': '1', 'flex-shrink': '1', 'flex-basis': 'auto'}
    >>> _expand_flex_shorthand("1")
    {'flex-grow': '1', 'flex-shrink': '1', 'flex-basis': '0%'}
    >>> _expand_flex_shorthand("2 3")
    {'flex-grow': '2', 'flex-shrink': '3', 'flex-basis': '0%'}
    >>> _expand_flex_shorthand("2 3 50%")
    {'flex-grow': '2', 'flex-shrink': '3', 'flex-basis': '50%'}
    >>> _expand_flex_shorthand("1 30px")
    {'flex-grow': '1', 'flex-shrink': '1', 'flex-basis': '30px'}
    """
    lowered = raw_value.strip().lower()

    if lowered == "none":
        return {"flex-grow": "0", "flex-shrink": "0", "flex-basis": "auto"}
    if lowered == "auto":
        return {"flex-grow": "1", "flex-shrink": "1", "flex-basis": "auto"}

    tokens = _tokenize_css_value(raw_value)
    count = len(tokens)

    if count == 1:
        tok = tokens[0]
        if _looks_like_number_token(tok):
            return {"flex-grow": tok, "flex-shrink": "1", "flex-basis": "0%"}
        return {}

    if count == 2:
        t0, t1 = tokens
        if _looks_like_number_token(t0) and _looks_like_number_token(t1):
            return {"flex-grow": t0, "flex-shrink": t1, "flex-basis": "0%"}
        if _looks_like_number_token(t0) and not _looks_like_number_token(t1):
            return {"flex-grow": t0, "flex-shrink": "1", "flex-basis": t1}
        return {}

    if count == 3:
        t0, t1, t2 = tokens
        if _looks_like_number_token(t0) and _looks_like_number_token(t1):
            return {"flex-grow": t0, "flex-shrink": t1, "flex-basis": t2}
        return {}

    return {}


def _expand_font_shorthand(raw_value: str) -> dict[str, str]:
    """Expand supported ``font`` shorthand values into longhand components.

    Handles the common CSS Fonts Level 4 §3.3 form::

        [<style>] [<variant>] [<weight>] [<stretch>] <size>[/<line-height>] <family>

    Returns ``{}`` for system-font keywords, empty values, or any form where
    the mandatory size token cannot be found. Never raises.

    The four optional pre-size keywords (style / variant / weight / stretch)
    share ``"normal"`` as a valid value. To resolve the ambiguity the first
    unassigned slot in order style → variant → weight → stretch receives it.
    """
    stripped = raw_value.strip()
    if not stripped:
        return {}
    if stripped.lower() in _FONT_SYSTEM_KEYWORDS:
        return {}

    tokens = _tokenize_css_value(stripped)
    if not tokens:
        return {}

    result: dict[str, str] = {}
    # Slots consumed for "normal" ambiguity resolution (index 0=style … 3=stretch)
    normal_slot = 0
    # Sets of slot names in order for "normal" assignment
    _normal_slots = ("font-style", "font-variant", "font-weight", "font-stretch")

    size_value: str | None = None
    line_height_value: str | None = None
    size_index: int = -1

    # Walk tokens left-to-right, classify pre-size keywords until we hit the
    # size token.  The tokenizer keeps "24px/1.5" as one token, so the regex
    # captures both parts via groups.
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        lowered = tok.lower()

        # Detect size (and optional /line-height) token
        m = _FONT_SIZE_RE.fullmatch(lowered)
        if m:
            size_value = m.group(1)  # preserve original case
            # Recover original-case size from tok (tok might differ in case)
            # Use the slice positions from the lower-cased match on the lowered string
            size_value = tok[: len(m.group(1))]
            if m.group(2) is not None:
                line_height_value = tok[len(m.group(1)) + 1:]  # after the "/"
            size_index = i
            break

        # Classify pre-size optional keyword
        if lowered == "normal":
            # Assign to the first unclaimed slot
            if normal_slot < len(_normal_slots):
                result[_normal_slots[normal_slot]] = tok
                normal_slot += 1
        elif lowered in _FONT_STYLE_TOKENS:
            if "font-style" not in result:
                result["font-style"] = tok
                # Advance normal_slot past style if not yet consumed
                if normal_slot == 0:
                    normal_slot = 1
        elif lowered in _FONT_VARIANT_TOKENS:
            if "font-variant" not in result:
                result["font-variant"] = tok
                if normal_slot <= 1:
                    normal_slot = 2
        elif lowered in _FONT_WEIGHT_TOKENS:
            if "font-weight" not in result:
                result["font-weight"] = tok
                if normal_slot <= 2:
                    normal_slot = 3
        elif lowered in _FONT_STRETCH_TOKENS:
            if "font-stretch" not in result:
                result["font-stretch"] = tok
                if normal_slot <= 3:
                    normal_slot = 4
        # Unknown pre-size token — do not bail here; the missing-size guard
        # below will return {} if no size is ever found.
        i += 1

    if size_value is None:
        # No size token found — invalid font shorthand per CSS spec
        return {}

    result["font-size"] = size_value
    if line_height_value:
        result["line-height"] = line_height_value

    # Family starts immediately after the size token (size/lh is one token)
    family_start_index = size_index + 1

    # Everything after size[/line-height] is font-family.
    # _tokenize_css_value splits on whitespace only so "Georgia," stays intact.
    # Joining with a space gives "Georgia, serif" (with the comma from the
    # original token "Georgia,") — correct CSS font-family syntax.
    if family_start_index < len(tokens):
        result["font-family"] = " ".join(tokens[family_start_index:])

    return result


def _expand_list_style_shorthand(raw_value: str) -> dict[str, str]:
    """Expand supported ``list-style`` shorthand values into longhand components.

    Classifies each token in the value into one of three buckets:
    ``list-style-position``, ``list-style-image``, or ``list-style-type``.
    Returns ``{}`` for empty input or any unrecognised token. Never raises.
    """
    stripped = raw_value.strip()
    if not stripped:
        return {}

    tokens = _tokenize_css_value(stripped)
    if not tokens:
        return {}

    result: dict[str, str] = {}
    for tok in tokens:
        lowered = tok.lower()
        if lowered.startswith("url("):
            result["list-style-image"] = tok
        elif lowered in _LIST_STYLE_POSITION_TOKENS:
            result["list-style-position"] = tok
        elif lowered in _LIST_STYLE_TYPE_TOKENS:
            result["list-style-type"] = tok
        else:
            # Unknown token: bail out deterministically
            return {}

    return result


def _expand_text_decoration_shorthand(raw_value: str) -> dict[str, str]:
    """Expand supported ``text-decoration`` shorthand values into longhand components.

    Classifies each token into one of four buckets:
    ``text-decoration-line``, ``text-decoration-style``,
    ``text-decoration-color``, or ``text-decoration-thickness``.
    Multiple line keywords (e.g. ``underline overline``) are joined with a space.
    Returns ``{}`` for empty input or any unrecognised token. Never raises.
    """
    stripped = raw_value.strip()
    if not stripped:
        return {}

    tokens = _tokenize_css_value(stripped)
    if not tokens:
        return {}

    line_parts: list[str] = []
    result: dict[str, str] = {}

    for tok in tokens:
        lowered = tok.lower()

        if lowered in _TEXT_DECORATION_LINE_TOKENS:
            # "none" as the only line keyword is valid; multiple lines are valid too
            line_parts.append(tok)
        elif lowered in _TEXT_DECORATION_STYLE_TOKENS:
            if "text-decoration-style" in result:
                return {}
            result["text-decoration-style"] = tok
        elif _is_css_color_token(tok):
            if "text-decoration-color" in result:
                return {}
            result["text-decoration-color"] = tok
        elif _TEXT_DECORATION_THICKNESS_RE.fullmatch(lowered):
            if "text-decoration-thickness" in result:
                return {}
            result["text-decoration-thickness"] = tok
        else:
            return {}

    if line_parts:
        result["text-decoration-line"] = " ".join(line_parts)

    return result


def _expand_outline_shorthand(raw_value: str) -> dict[str, str]:
    """Expand the ``outline`` shorthand into ``outline-width``, ``outline-style``, ``outline-color``.

    Classifies each space-separated token:

    - A CSS length/dimension token (digits followed by a unit, e.g. ``2px``) → ``outline-width``.
    - A recognised ``outline-style`` keyword → ``outline-style``.
    - Anything else (including named colours, ``#hex``, ``rgb(...)`` values) → ``outline-color``.

    ``outline-offset`` is not part of the ``outline`` shorthand and is left at
    its initial value.

    Returns ``{}`` for empty input or any form where a slot is claimed twice.
    Never raises.

    Examples
    --------
    >>> _expand_outline_shorthand("2px solid red")
    {'outline-width': '2px', 'outline-style': 'solid', 'outline-color': 'red'}
    >>> _expand_outline_shorthand("dashed blue")
    {'outline-style': 'dashed', 'outline-color': 'blue'}
    >>> _expand_outline_shorthand("")
    {}
    """
    stripped = raw_value.strip()
    if not stripped:
        return {}

    tokens = _tokenize_css_value(stripped)
    if not tokens:
        return {}

    result: dict[str, str] = {}
    for tok in tokens:
        lowered = tok.lower()
        if _OUTLINE_WIDTH_RE.fullmatch(lowered):
            if "outline-width" in result:
                return {}
            result["outline-width"] = tok
        elif lowered in _OUTLINE_STYLE_TOKENS:
            if "outline-style" in result:
                return {}
            result["outline-style"] = tok
        else:
            # treat as color (named keyword, hex, functional)
            if "outline-color" in result:
                return {}
            result["outline-color"] = tok

    return result


def _expand_grid_placement_shorthand(raw: str, start_prop: str, end_prop: str) -> dict[str, str]:
    """Expand ``grid-column`` or ``grid-row`` shorthand (CSS Grid §10).

    A single value broadcasts to both start and end longhands.
    The ``start / end`` form splits on the first ``/`` and assigns accordingly.
    Values are passed through as-is — no grid-value validation is performed.
    """
    parts = [t.strip() for t in raw.split("/", 1)]
    if len(parts) == 1:
        return {start_prop: parts[0], end_prop: parts[0]}
    return {start_prop: parts[0], end_prop: parts[1]}


def _expand_grid_area_shorthand(raw: str) -> dict[str, str]:
    """Expand ``grid-area`` shorthand (CSS Grid §13.1).

    Splits on ``/`` into up to 4 parts mapping to
    ``grid-row-start``, ``grid-column-start``, ``grid-row-end``,
    ``grid-column-end``. Omitted parts follow the CSS Grid §13.1
    omission rules: missing end defaults to the corresponding start value;
    missing column-start defaults to the row-start value.

    Examples:

    - Single value: all four longhands receive the same value.
    - Two parts: ``rs / cs``; ``re = rs``, ``ce = cs``.
    - Three parts: ``rs / cs / re``; ``ce = cs``.
    - Four parts: ``rs / cs / re / ce``.
    """
    parts = [t.strip() for t in raw.split("/")]
    rs = parts[0] if len(parts) > 0 else "auto"
    cs = parts[1] if len(parts) > 1 else rs
    re_ = parts[2] if len(parts) > 2 else rs
    ce = parts[3] if len(parts) > 3 else cs
    return {
        "grid-row-start": rs,
        "grid-column-start": cs,
        "grid-row-end": re_,
        "grid-column-end": ce,
    }


def _expand_grid_template_shorthand(raw: str) -> dict[str, str]:
    """Expand ``grid-template`` shorthand slash form (CSS Grid §7).

    Splits on the first ``/``::

        <grid-template-rows> / <grid-template-columns>

    A third slash-separated token (if present) is assigned to
    ``grid-template-areas``; otherwise ``grid-template-areas`` is set to ``""``.

    Only the slash-separated two-/three-part form is handled.  Complex forms
    with quoted strings are outside the scope of this helper (ADR-288).
    """
    parts = [t.strip() for t in raw.split("/", 2)]
    return {
        "grid-template-rows": parts[0],
        "grid-template-columns": parts[1] if len(parts) > 1 else "",
        "grid-template-areas": parts[2] if len(parts) > 2 else "",
    }


def _expand_background_shorthand(raw_value: str) -> dict[str, str]:
    """Expand supported single-layer ``background`` shorthand values.

    Handles the slash form ``<position>/<size>`` (optionally followed by a
    repeat and/or color token) and common single-token/multi-token non-slash
    forms.  Unsupported complex structures (e.g. multi-layer comma lists)
    return ``{}``.

    >>> _expand_background_shorthand("red")
    {'background-color': 'red'}
    >>> _expand_background_shorthand("url(a.png)")
    {'background-image': 'url(a.png)'}
    >>> _expand_background_shorthand("url(a.png) red")
    {'background-image': 'url(a.png)', 'background-color': 'red'}
    >>> _expand_background_shorthand("center/cover no-repeat")
    {'background-position': 'center', 'background-size': 'cover', 'background-repeat': 'no-repeat'}
    """
    if "," in raw_value:
        return {}

    parts = _split_top_level(raw_value, "/")
    if len(parts) > 2:
        return {}

    if len(parts) == 1:
        # Semantic dispatch for non-slash forms (ADR-296).
        tokens = _tokenize_css_value(raw_value)
        if len(tokens) == 1:
            tok = tokens[0]
            lowered = tok.lower()
            if _looks_like_color_token(lowered):
                return {"background-color": tok}
            if _looks_like_background_image_token(lowered):
                return {"background-image": tok}
            # Unrecognised single token — deterministic ignore.
            return {}
        # Multi-token without slash: extract image and/or color.
        return _expand_background_no_slash(raw_value, tokens)

    before_slash, after_slash = parts
    if not before_slash or not after_slash:
        return {}

    position_tokens = _tokenize_css_value(before_slash)
    size_repeat_tokens = _tokenize_css_value(after_slash)
    if not position_tokens or not size_repeat_tokens:
        return {}

    if len(size_repeat_tokens) > 2:
        return {}

    image: str | None = None
    position_tokens_only = position_tokens
    if len(position_tokens) >= 2 and _looks_like_background_image_token(position_tokens[0]):
        image = position_tokens[0]
        position_tokens_only = position_tokens[1:]

    if not position_tokens_only:
        return {}

    position = " ".join(position_tokens_only)
    size = size_repeat_tokens[0]
    repeat = size_repeat_tokens[1] if len(size_repeat_tokens) == 2 else ""

    expanded = {
        "background-position": position,
        "background-size": size,
        "background-repeat": repeat,
    }
    if image is not None:
        expanded["background-image"] = image
    return expanded


def _expand_background_no_slash(raw_value: str, tokens: list[str]) -> dict[str, str]:
    """Extract color and/or image from a multi-token background value without a slash.

    Walks *tokens* and picks out up to one image token and one color token.
    Returns a dict with only the matched longhands — unmatched longhands are
    omitted (treated as initial values by the cascade engine).  Returns ``{}``
    when neither image nor color can be identified.

    >>> _expand_background_no_slash("url(a.png) red", ["url(a.png)", "red"])
    {'background-image': 'url(a.png)', 'background-color': 'red'}
    >>> _expand_background_no_slash("no-repeat center", ["no-repeat", "center"])
    {}
    """
    image: str | None = None
    color: str | None = None
    for tok in tokens:
        lowered = tok.lower()
        if image is None and _looks_like_background_image_token(lowered):
            image = tok
        elif color is None and _looks_like_color_token(lowered):
            color = tok
    result: dict[str, str] = {}
    if image is not None:
        result["background-image"] = image
    if color is not None:
        result["background-color"] = color
    return result


def _expand_border_radius_shorthand(raw_value: str) -> dict[str, str]:
    """Expand supported ``border-radius`` shorthand values.

    Supports 1-4 token horizontal forms and ``horizontal / vertical`` axis
    split. Unsupported complex forms return ``{}``.
    """
    parts = _split_top_level(raw_value, "/")
    if len(parts) > 2:
        return {}

    if len(parts) == 1:
        tokens = _tokenize_css_value(parts[0])
        if not tokens or len(tokens) > 4:
            return {}
        expanded = _expand_four_side_values(tokens)
        return {
            "border-top-left-radius": expanded[0],
            "border-top-right-radius": expanded[1],
            "border-bottom-right-radius": expanded[2],
            "border-bottom-left-radius": expanded[3],
        }

    horizontal_part, vertical_part = parts
    if not horizontal_part or not vertical_part:
        return {}

    horizontal_tokens = _tokenize_css_value(horizontal_part)
    vertical_tokens = _tokenize_css_value(vertical_part)
    if not horizontal_tokens or not vertical_tokens:
        return {}

    if len(horizontal_tokens) > 4 or len(vertical_tokens) > 4:
        return {}

    horizontal = _expand_four_side_values(horizontal_tokens)
    vertical = _expand_four_side_values(vertical_tokens)

    return {
        "border-top-left-radius": f"{horizontal[0]} {vertical[0]}",
        "border-top-right-radius": f"{horizontal[1]} {vertical[1]}",
        "border-bottom-right-radius": f"{horizontal[2]} {vertical[2]}",
        "border-bottom-left-radius": f"{horizontal[3]} {vertical[3]}",
    }


def _expand_container_shorthand(raw_value: str) -> dict[str, str]:
    """Expand ``container`` shorthand into container-name and container-type.

    Syntax: ``<name> / <type>`` or ``<name>`` alone (type defaults to
    ``"normal"``). Slash-splitting uses ``_split_top_level`` to handle any
    future function-call values safely.

    Examples
    --------
    >>> _expand_container_shorthand("sidebar / inline-size")
    {'container-name': 'sidebar', 'container-type': 'inline-size'}
    >>> _expand_container_shorthand("main")
    {'container-name': 'main', 'container-type': 'normal'}
    >>> _expand_container_shorthand("none")
    {'container-name': 'none', 'container-type': 'normal'}
    """
    parts = _split_top_level(raw_value, "/")
    name = parts[0].strip() if parts else ""
    ctype = parts[1].strip() if len(parts) > 1 else ""
    if not name:
        return {}
    return {"container-name": name, "container-type": ctype or "normal"}


def _expand_border_shorthand(property_name: str, raw_value: str) -> dict[str, str]:
    """Expand supported border shorthand values into deterministic longhands."""
    tokens = _tokenize_css_value(raw_value)
    if not tokens or len(tokens) > 3:
        return {}

    if len(tokens) == 1:
        token = tokens[0].strip()
        lowered = token.lower()
        if (
            lowered in {"inherit", "initial", "unset"}
            or _looks_like_full_value_var_call(token)
            or _looks_like_full_value_env_call(token)
        ):
            if property_name == "border":
                return {
                    side_name: token
                    for side_name in _SHORTHAND_EXPANSIONS["border"]
                }
            return {side_name: token for side_name in _SHORTHAND_EXPANSIONS[property_name]}

    width: str | None = None
    style: str | None = None
    color: str | None = None

    for token in tokens:
        is_width = _is_border_width_token(token)
        is_style = _is_border_style_token(token)
        if is_width and is_style:
            return {}
        if is_width:
            if width is not None:
                return {}
            width = token
            continue
        if is_style:
            if style is not None:
                return {}
            style = token
            continue
        if not _is_border_color_token(token):
            return {}
        if color is not None:
            return {}
        color = token

    width = width or "medium"
    style = style or "none"
    color = color or "currentcolor"

    side_values: tuple[str, str, str] = (width, style, color)
    if property_name == "border":
        expanded: dict[str, str] = {}
        for side in ("top", "right", "bottom", "left"):
            expanded[f"border-{side}-width"] = side_values[0]
            expanded[f"border-{side}-style"] = side_values[1]
            expanded[f"border-{side}-color"] = side_values[2]
        return expanded

    return {
        _SHORTHAND_EXPANSIONS[property_name][0]: side_values[0],
        _SHORTHAND_EXPANSIONS[property_name][1]: side_values[1],
        _SHORTHAND_EXPANSIONS[property_name][2]: side_values[2],
    }


def _expand_two_value_axis_shorthand(property_name: str, raw_value: str) -> dict[str, str]:
    """Expand a two-value axis shorthand (margin-block, padding-inline, etc.).

    Applies CSS two-value box-model rules to the two longhands in
    ``_SHORTHAND_EXPANSIONS[property_name]``:

    - One token  → both longhands receive the same value.
    - Two+ tokens → first token → start longhand, second → end longhand.
    - Empty value → both longhands receive the raw string as-is.

    Never raises; malformed values are passed through rather than silently
    discarded so they can be inspected by the cascade consumer.
    """
    longhands = _SHORTHAND_EXPANSIONS[property_name]
    start_prop, end_prop = longhands[0], longhands[1]
    tokens = _tokenize_css_value(raw_value)
    if len(tokens) == 0:
        return {start_prop: raw_value, end_prop: raw_value}
    if len(tokens) == 1:
        return {start_prop: tokens[0], end_prop: tokens[0]}
    # Two or more tokens: first → start, second → end (extra tokens ignored
    # per CSS specification which only defines 1-value and 2-value forms).
    return {start_prop: tokens[0], end_prop: tokens[1]}


def _expand_border_axis_shorthand(property_name: str, raw_value: str) -> dict[str, str]:
    """Expand a border axis shorthand (border-block or border-inline) to six longhands.

    Each axis shorthand sets width, style, and color uniformly for both the
    start and end sides.  The value is classified by the same dimension /
    style-keyword / color logic as ``_expand_border_shorthand``, then broadcast
    to all six longhands.

    Returns ``{}`` for unsupported token shapes (zero tokens, more than three
    tokens, or a token that cannot be classified).  Never raises.
    """
    # Reuse the per-side expansion logic on the start-side triple, then copy
    # the resolved values to the end-side triple.
    longhands = _SHORTHAND_EXPANSIONS[property_name]
    # longhands layout: (start-width, start-style, start-color,
    #                    end-width,   end-style,   end-color)
    start_triple = longhands[:3]
    end_triple = longhands[3:]

    # Build a temporary per-side shorthand entry name — use the start-side name
    # (e.g. "border-block-start") which is already registered in _SHORTHAND_EXPANSIONS.
    if property_name == "border-block":
        side_shorthand = "border-block-start"
    else:  # border-inline
        side_shorthand = "border-inline-start"

    side_result = _expand_border_shorthand(side_shorthand, raw_value)
    if not side_result:
        return {}

    # side_result has {start-width: v, start-style: v, start-color: v}
    # Map to the end triple using the same positional order.
    width_val = side_result.get(start_triple[0], "medium")
    style_val = side_result.get(start_triple[1], "none")
    color_val = side_result.get(start_triple[2], "currentcolor")

    return {
        start_triple[0]: width_val,
        start_triple[1]: style_val,
        start_triple[2]: color_val,
        end_triple[0]: width_val,
        end_triple[1]: style_val,
        end_triple[2]: color_val,
    }


def _iter_expanded_declarations(property_name: str, value: str) -> Iterator[tuple[str, str]]:
    """Yield deterministic declaration stream for shorthand/longhand input."""
    expanded = _expand_shorthand_value(property_name, value)
    if expanded is None:
        yield (property_name, value)
        return
    for name in _SHORTHAND_EXPANSIONS[property_name]:
        expanded_value = expanded.get(name)
        if expanded_value is None:
            continue
        yield (name, expanded_value)


def _iter_logical_alias_declarations(property_name: str, value: str) -> Iterator[tuple[str, str]]:
    """Yield deterministic declaration stream for logical alias baseline."""
    alias_target = _LOGICAL_PROPERTY_ALIASES.get(property_name)
    if alias_target is None:
        yield (property_name, value)
        return
    yield (alias_target, value)
