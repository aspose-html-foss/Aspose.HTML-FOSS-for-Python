"""Property data tables and the _Candidate dataclass for the CSS cascade engine.

Pure data layer — no dependency on shorthand helpers or the engine.
Standard-library imports only.

See .
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal


_SUPPORTED_NAME_RE = re.compile(r"^-?[a-z][a-z0-9-]*$")
_CUSTOM_PROPERTY_NAME_RE = re.compile(r"^--[a-z0-9-]+$")
_IMPORTANT_SUFFIX_RE = re.compile(r"\s*!important\s*$", re.IGNORECASE)
_VAR_FUNCTION_FULL_RE = re.compile(r"^var\((.*)\)$", re.IGNORECASE)
_ENV_FUNCTION_FULL_RE = re.compile(r"^env\((.*)\)$", re.IGNORECASE)
_ANIMATION_TIME_RE = re.compile(r"^(?:\d+(?:\.\d+)?|\.\d+)(?:ms|s)$", re.IGNORECASE)

# Keywords that are NOT color names — used by _looks_like_color_token to reject
# layout/geometry tokens from being mistaken for color values ().
_BACKGROUND_NON_COLOR_KEYWORDS: frozenset[str] = frozenset({
    "none", "auto", "initial", "inherit", "unset", "revert",
    "center", "top", "bottom", "left", "right",
    "cover", "contain",
    "repeat", "no-repeat", "repeat-x", "repeat-y", "space", "round",
    "fixed", "scroll", "local",
    "border-box", "padding-box", "content-box", "text",
})

# W3C CSS Cascading Level 4 Appendix A — inherited properties.
# The frozenset stores lower-cased property names; ``_is_inherited()`` uses
# it for O(1) membership checks.
_INHERITED_PROPERTIES: frozenset[str] = frozenset(
    {
        # Font
        "color",
        "font",
        "font-family",
        "font-feature-settings",
        "font-kerning",
        "font-language-override",
        "font-optical-sizing",
        "font-size",
        "font-size-adjust",
        "font-stretch",
        "font-style",
        "font-synthesis",
        "font-variant",
        "font-variant-alternates",
        "font-variant-caps",
        "font-variant-east-asian",
        "font-variant-ligatures",
        "font-variant-numeric",
        "font-variant-position",
        "font-weight",
        # Text
        "direction",
        "letter-spacing",
        "line-height",
        "overflow-wrap",
        "tab-size",
        "text-align",
        "text-align-last",
        "text-decoration-skip-ink",
        "text-emphasis",
        "text-emphasis-color",
        "text-emphasis-position",
        "text-emphasis-style",
        "text-indent",
        "text-justify",
        "text-orientation",
        "text-rendering",
        "text-shadow",
        "text-transform",
        "text-underline-position",
        "unicode-bidi",
        "white-space",
        "word-break",
        "word-spacing",
        "word-wrap",
        "writing-mode",
        # Lists
        "list-style",
        "list-style-image",
        "list-style-position",
        "list-style-type",
        # Table
        "border-collapse",
        "border-spacing",
        "caption-side",
        "empty-cells",
        # Other inherited
        "cursor",
        "hyphens",
        # CSS Text Level 4 §5.4 — soft-hyphen replacement character
        "hyphenate-character",
        "orphans",
        "pointer-events",
        "quotes",
        # CSS Ruby Annotation Layout Level 1 §5 — ruby annotation placement
        "ruby-position",
        "visibility",
        "widows",
        # --- NEW: ,  — inherited longhands ---
        # CSS Fonts Level 4 §9 — font-synthesis longhands
        "font-synthesis-weight",
        "font-synthesis-style",
        "font-synthesis-small-caps",
        "font-synthesis-position",
        # CSS Text Level 4 §3.3 — hanging punctuation
        "hanging-punctuation",
        # CSS Text Decoration Level 4 §4.4 — text-decoration-skip
        "text-decoration-skip",
        # --- NEW: ,  — inherited CSS tail ---
        # CSS Fonts Level 4 §6.8 — font-variation-settings
        "font-variation-settings",
        # CSS Fonts Level 5 §9 — font-palette
        "font-palette",
        # MathML Core §3.4 — math-style
        "math-style",
    }
)


def _is_inherited(property_name: str) -> bool:
    """Return ``True`` when *property_name* is a CSS inherited property.

    The check is case-insensitive and covers the full CSS Level 4 Appendix A
    inherited-property set.

    Examples
    --------
    >>> _is_inherited("color")
    True
    >>> _is_inherited("Color")
    True
    >>> _is_inherited("background-color")
    False
    >>> _is_inherited("text-align")
    True
    >>> _is_inherited("list-style-type")
    True
    """
    return property_name.strip().lower() in _INHERITED_PROPERTIES


_INITIAL_VALUE_BASELINE: dict[str, str] = {
    # All inherited properties — initial value is "" (no layout engine).
    **{prop: "" for prop in _INHERITED_PROPERTIES},
    # Non-inherited layout properties.
    "margin": "",
    "margin-top": "",
    "margin-right": "",
    "margin-bottom": "",
    "margin-left": "",
    "padding": "",
    "padding-top": "",
    "padding-right": "",
    "padding-bottom": "",
    "padding-left": "",
    "border-top-width": "",
    "border-right-width": "",
    "border-bottom-width": "",
    "border-left-width": "",
    "border-top-style": "",
    "border-right-style": "",
    "border-bottom-style": "",
    "border-left-style": "",
    "border-top-color": "",
    "border-right-color": "",
    "border-bottom-color": "",
    "border-left-color": "",
    "background-color": "",
    "border-color": "",
    # --- NEW: ,  — Physical border sub-shorthands ---
    # border-color is already above; border-width and border-style must also
    # appear here so CSS.supports() returns True and the cascade does not
    # silently drop their declarations.
    "border-width": "",
    "border-style": "",
    # --- NEW: Layout / positioning (, ) ---
    "aspect-ratio": "auto",
    "backface-visibility": "visible",
    "bottom": "auto",
    "box-sizing": "content-box",
    "clear": "none",
    "clip": "auto",
    "contain": "none",
    "display": "inline",
    "float": "none",
    "height": "auto",
    "left": "auto",
    "max-height": "none",
    "max-width": "none",
    "min-height": "auto",
    "min-width": "auto",
    "object-fit": "fill",
    "object-position": "50% 50%",
    "overflow": "",
    "overflow-x": "",
    "overflow-y": "",
    "position": "static",
    "resize": "",
    "right": "auto",
    "table-layout": "auto",
    "top": "auto",
    "vertical-align": "baseline",
    "width": "auto",
    "z-index": "auto",
    # --- NEW: Background (non-color) ---
    "background": "",
    "background-attachment": "scroll",
    "background-clip": "border-box",
    "background-image": "none",
    "background-origin": "padding-box",
    "background-position": "0% 0%",
    "background-repeat": "repeat",
    "background-size": "auto",
    # --- NEW: Border / decoration ---
    "border-bottom-left-radius": "",
    "border-bottom-right-radius": "",
    "border-image": "none",
    "border-image-outset": "",
    "border-image-repeat": "",
    "border-image-slice": "",
    "border-image-source": "none",
    "border-image-width": "",
    "border-radius": "",
    "border-top-left-radius": "",
    "border-top-right-radius": "",
    "box-shadow": "none",
    "outline": "",
    "outline-color": "invert",
    "outline-offset": "",
    "outline-style": "none",
    "outline-width": "medium",
    "text-decoration-color": "",
    "text-decoration-line": "none",
    "text-decoration-style": "solid",
    "text-decoration-thickness": "",
    # --- NEW: Transform / filter ---
    "backdrop-filter": "none",
    "filter": "none",
    "isolation": "auto",
    "mix-blend-mode": "normal",
    "opacity": "1",
    "perspective": "none",
    "perspective-origin": "50% 50%",
    "transform": "none",
    "transform-box": "view-box",
    "transform-origin": "50% 50% 0",
    "transform-style": "flat",
    # --- NEW: Flexbox ---
    "align-content": "normal",
    "align-items": "normal",
    "align-self": "auto",
    "column-gap": "",
    "flex": "0 1 auto",
    "flex-basis": "auto",
    "flex-direction": "row",
    "flex-flow": "",
    "flex-grow": "0",
    "flex-shrink": "1",
    "flex-wrap": "nowrap",
    "gap": "",
    "justify-content": "normal",
    "justify-items": "legacy",
    "justify-self": "auto",
    "order": "0",
    "place-content": "",
    "place-items": "",
    "place-self": "",
    "row-gap": "",
    # --- NEW: Grid ---
    "grid": "",
    "grid-area": "",
    "grid-auto-columns": "auto",
    "grid-auto-flow": "row",
    "grid-auto-rows": "auto",
    "grid-column": "",
    "grid-column-end": "auto",
    "grid-column-start": "auto",
    "grid-row": "",
    "grid-row-end": "auto",
    "grid-row-start": "auto",
    "grid-template": "",
    "grid-template-areas": "none",
    "grid-template-columns": "none",
    "grid-template-rows": "none",
    # --- NEW: Transitions ---
    "transition": "",
    "transition-delay": "0s",
    "transition-duration": "0s",
    "transition-property": "all",
    "transition-timing-function": "ease",
    # --- NEW: Animations ---
    "animation": "",
    "animation-delay": "0s",
    "animation-direction": "normal",
    "animation-duration": "0s",
    "animation-fill-mode": "none",
    "animation-iteration-count": "1",
    "animation-name": "none",
    "animation-play-state": "running",
    "animation-timing-function": "ease",
    # --- NEW: Multi-column ---
    "break-after": "auto",
    "break-before": "auto",
    "break-inside": "auto",
    "column-count": "auto",
    "column-fill": "balance",
    "column-rule": "",
    "column-rule-color": "",
    "column-rule-style": "none",
    "column-rule-width": "",
    "column-span": "none",
    "column-width": "auto",
    "columns": "",
    # --- NEW: Shorthand shims for text-decoration and inset (, ) ---
    # These shorthand names must appear in _KNOWN_PROPERTIES so the cascade
    # engine's property-name filter does not silently discard their declarations.
    # Their longhands (text-decoration-line etc., top/right/bottom/left) are
    # already present elsewhere in this dict.
    "text-decoration": "",
    "inset": "",
    # --- NEW: Misc visual ---
    "appearance": "none",
    "clip-path": "none",
    "content": "normal",
    "counter-increment": "none",
    "counter-reset": "none",
    "counter-set": "none",
    "image-rendering": "auto",
    "overscroll-behavior": "auto",
    "overscroll-behavior-x": "auto",
    "overscroll-behavior-y": "auto",
    "scroll-behavior": "auto",
    "scroll-snap-align": "none",
    "scroll-snap-type": "none",
    "shape-outside": "none",
    "user-select": "auto",
    "will-change": "auto",
    # --- NEW: ,  — CSS Logical Properties Level 1 ---
    # Logical margin longhands (initial value '' — same as physical margins)
    "margin-block-start": "",
    "margin-block-end": "",
    "margin-inline-start": "",
    "margin-inline-end": "",
    # Logical padding longhands (initial value '' — same as physical paddings)
    "padding-block-start": "",
    "padding-block-end": "",
    "padding-inline-start": "",
    "padding-inline-end": "",
    # Logical border longhands (initial value '' — same as physical border longhands)
    "border-block-start-width": "",
    "border-block-end-width": "",
    "border-inline-start-width": "",
    "border-inline-end-width": "",
    "border-block-start-style": "",
    "border-block-end-style": "",
    "border-inline-start-style": "",
    "border-inline-end-style": "",
    "border-block-start-color": "",
    "border-block-end-color": "",
    "border-inline-start-color": "",
    "border-inline-end-color": "",
    # Logical sizing longhands
    "block-size": "auto",
    "inline-size": "auto",
    "min-block-size": "auto",
    "max-block-size": "none",
    "min-inline-size": "auto",
    "max-inline-size": "none",
    # Logical inset longhands (initial value 'auto' — same as physical top/right/bottom/left)
    "inset-block-start": "auto",
    "inset-block-end": "auto",
    "inset-inline-start": "auto",
    "inset-inline-end": "auto",
    # --- NEW: ,  — Property table completeness tail ---
    # CSS Text Level 3 §8.1
    "text-overflow": "clip",
    # CSS Scroll Snap Level 1 §9.1 (scroll-margin physical longhands)
    "scroll-margin-top": "0px",
    "scroll-margin-right": "0px",
    "scroll-margin-bottom": "0px",
    "scroll-margin-left": "0px",
    # CSS Scroll Snap Level 1 §9.2 (scroll-padding physical longhands)
    "scroll-padding-top": "auto",
    "scroll-padding-right": "auto",
    "scroll-padding-bottom": "auto",
    "scroll-padding-left": "auto",
    # CSS Masking Level 1 §2 (mask longhands)
    "mask-image": "none",
    "mask-mode": "match-source",
    "mask-position": "center",
    "mask-size": "auto",
    "mask-repeat": "no-repeat",
    "mask-origin": "border-box",
    "mask-clip": "border-box",
    "mask-composite": "add",
    # CSS Basic User Interface Level 4 (interaction + form theming)
    "touch-action": "auto",
    "accent-color": "auto",
    "caret-color": "auto",
    # CSS Scrollbars Level 1
    "scrollbar-width": "auto",
    "scrollbar-color": "auto",
    # Shorthand sentinel: mask shorthand must be in _KNOWN_PROPERTIES so
    # CSS.supports("mask", ...) returns True (same pattern as border, margin).
    "mask": "",
    # --- NEW: ,  — SVG presentational + misc property completeness ---
    # SVG 1.1 §11.4 — paint properties
    "fill": "black",
    "stroke": "none",
    "stroke-width": "1px",
    "stroke-dasharray": "none",
    "stroke-dashoffset": "0",
    "stroke-linecap": "butt",
    "stroke-linejoin": "miter",
    "stroke-miterlimit": "4",
    "stroke-opacity": "1",
    "fill-opacity": "1",
    "fill-rule": "nonzero",
    # SVG 1.1 §14.3 — clip
    "clip-rule": "nonzero",
    # SVG 1.1 §12.4 — color interpolation
    "color-interpolation": "sRGB",
    "color-interpolation-filters": "linearRGB",
    # SVG 1.1 §11.9 — rendering quality
    "color-rendering": "auto",
    "shape-rendering": "auto",
    # SVG 1.1 §15.7 — filter primitive environment
    "flood-color": "black",
    "flood-opacity": "1",
    "lighting-color": "white",
    # SVG 1.1 §11.6 — markers
    "marker-start": "none",
    "marker-mid": "none",
    "marker-end": "none",
    "marker": "",  # shorthand sentinel
    # SVG 1.1 §13.4 — gradients
    "stop-color": "black",
    "stop-opacity": "1",
    # SVG 1.1 §10.9 / CSS Inline Layout §4.2 — text / baseline
    "text-anchor": "start",
    "dominant-baseline": "auto",
    "alignment-baseline": "auto",
    "baseline-shift": "0",
    # SVG 2.0 — effects
    "vector-effect": "none",
    "paint-order": "normal",
    # CSS Motion Path Level 1 — offset/motion-path
    "offset-path": "none",
    "offset-distance": "0",
    "offset-rotate": "auto",
    "offset-anchor": "auto",
    "offset": "",  # shorthand sentinel
    # CSS Paged Media Level 3 §9 — legacy page-break aliases
    "page-break-before": "auto",
    "page-break-after": "auto",
    "page-break-inside": "auto",
    # CSS Scroll Snap Level 1 §7.2 — scroll-snap-stop (completes scroll-snap family)
    "scroll-snap-stop": "normal",
    # CSS Color Adjustment Level 1 — color scheme + print
    "color-scheme": "normal",
    "forced-color-adjust": "auto",
    "print-color-adjust": "economy",
    # CSS Animations Level 2 — timeline
    "animation-timeline": "auto",
    # CSS Containment Level 2 — content-visibility
    "content-visibility": "visible",
    # CSS Grid Level 1 — legacy gap aliases
    "grid-row-gap": "normal",
    "grid-column-gap": "normal",
    # CSS Writing Modes Level 4 §7 — CJK upright text
    "text-combine-upright": "none",
    # --- NEW: ,  — CSS shorthand registration gap ---
    # These 19 shorthand names are present in _SHORTHAND_EXPANSIONS but were
    # absent from _KNOWN_PROPERTIES, causing CSS.supports() to return False.
    # The fix is purely additive — initial value "" follows the established
    # shorthand convention (no single canonical initial value; resolved to longhands).
    #
    # Physical border-side shorthands (CSS Backgrounds §3: width style color)
    "border": "",
    "border-top": "",
    "border-right": "",
    "border-bottom": "",
    "border-left": "",
    # CSS Logical Properties axis shorthands (CSS Logical Properties Level 1)
    "margin-inline": "",
    "margin-block": "",
    "padding-inline": "",
    "padding-block": "",
    "inset-inline": "",
    "inset-block": "",
    # CSS Logical Properties border shorthands (CSS Logical Properties Level 1)
    "border-block": "",
    "border-inline": "",
    "border-block-start": "",
    "border-block-end": "",
    "border-inline-start": "",
    "border-inline-end": "",
    # CSS Scroll Snap Level 1 §9 — scroll-box shorthands
    "scroll-margin": "",
    "scroll-padding": "",
    # --- NEW: ,  — CSS property tail (GAP-060) ---
    # CSS Transforms Level 2 §3–§5 — individual-transform longhands
    "rotate": "none",
    "scale": "none",
    "translate": "none",
    # CSS Text Level 4 §4.1 — line-break
    "line-break": "auto",
    # CSS Text Level 4 §4.2 — text-wrap family
    "text-wrap": "wrap",
    "text-wrap-mode": "wrap",
    "text-wrap-style": "auto",
    # CSS Compositing Level 1 §11 — background layer blending
    "background-blend-mode": "normal",
    # CSS Fragmentation Level 3 §6.4 — box decoration across breaks
    "box-decoration-break": "slice",
    # CSS Images Level 4 §5.8 — EXIF-based auto-rotation
    "image-orientation": "from-image",
    # CSS Cascade Level 4 §3.3 — all-properties reset shorthand sentinel
    # Not expanded; registered here only so CSS.supports("all", ...) returns True.
    "all": "",
    # CSS Text Decoration Level 4 §4.1 — underline offset
    "text-underline-offset": "auto",
    # CSS Containment Level 3 §3.1 (Container Queries Level 1) — containment axis
    "container-type": "normal",
    # CSS Containment Level 3 §3.1 (Container Queries Level 1) — containment name
    "container-name": "none",
    # CSS Containment Level 3 §3.1 — container shorthand sentinel
    "container": "",
    # --- NEW: ,  — CSS inherited longhand tail (GAP-062) ---
    # CSS Text Level 4 §5.4 — soft-hyphen replacement character (initial "auto")
    "hyphenate-character": "auto",
    # CSS Ruby Annotation Layout Level 1 §5 — ruby annotation placement (initial "over")
    "ruby-position": "over",
    # --- NEW: ,  — CSS property tail (GAP-063) ---
    # CSS Overflow Level 3 §2.2 — overflow-clip-margin (non-inherited)
    "overflow-clip-margin": "0px",
    # CSS Fonts Level 4 §9 — font-synthesis longhands (inherited, initial "auto")
    "font-synthesis-weight":     "auto",
    "font-synthesis-style":      "auto",
    "font-synthesis-small-caps": "auto",
    "font-synthesis-position":   "auto",
    # CSS Transitions Level 2 §3.1 — transition-behavior (non-inherited, initial "normal")
    "transition-behavior": "normal",
    # CSS Text Level 4 §3.3 — hanging-punctuation (inherited, initial "none")
    "hanging-punctuation": "none",
    # CSS Backgrounds Level 3 §3.1 — background-position-x/y (non-inherited, initial "0%")
    "background-position-x": "0%",
    "background-position-y": "0%",
    # CSS Text Decoration Level 4 §4.4 — text-decoration-skip (inherited, initial "objects")
    "text-decoration-skip": "objects",
    # --- NEW: ,  — CSS property tail (GAP-064) ---
    # CSS Fonts Level 4 §6.8 — font-variation-settings (inherited, initial "normal")
    # Note: also added to _INHERITED_PROPERTIES; the entry here sets the explicit initial value.
    "font-variation-settings": "normal",
    # CSS Fonts Level 5 §9 — font-palette (inherited, initial "normal")
    "font-palette": "normal",
    # CSS Transforms Level 2 / CSSOM View legacy — zoom (not inherited, initial "1")
    "zoom": "1",
    # CSS Animations Level 2 §3.7 — animation-composition (not inherited, initial "replace")
    "animation-composition": "replace",
    # CSS Animations Level 2 §4.2 — animation-range longhands (not inherited, initial "normal")
    "animation-range-start": "normal",
    "animation-range-end":   "normal",
    # MathML Core §3.3 — math-depth (not inherited, initial "0")
    "math-depth": "0",
    # MathML Core §3.4 — math-style (inherited, initial "normal")
    # Note: also added to _INHERITED_PROPERTIES.
    "math-style": "normal",
    # CSS Animations Level 2 §4.2 — animation-range shorthand sentinel
    # (same pattern as margin/container/offset; no single canonical initial value)
    "animation-range": "",
    # --- NEW: ,  — CSS property tail (GAP-065) ---
    # CSS Shapes Module Level 1 §7.2 — margin around float shapes (not inherited)
    "shape-margin": "0px",
    # CSS Shapes Module Level 1 §7.3 — alpha threshold for shape-outside images (not inherited)
    "shape-image-threshold": "0",
    # CSS Scrollbars Styling Module Level 1 §3 — scrollbar gutter space (not inherited)
    "scrollbar-gutter": "auto",
    # CSS Containment Module Level 2 §3.3 — contain-intrinsic-size longhands (not inherited)
    "contain-intrinsic-size": "none",
    "contain-intrinsic-width": "none",
    "contain-intrinsic-height": "none",
    "contain-intrinsic-block-size": "none",
    "contain-intrinsic-inline-size": "none",
    # CSS Compatibility §3 — vendor-prefixed alias for user-select (not inherited)
    "-webkit-user-select": "auto",
    # --- NEW: ,  ---
    # CSS Text Level 4 §4 — text-size-adjust (not inherited)
    "text-size-adjust": "auto",
    "-webkit-text-size-adjust": "auto",
    # CSS Overflow Level 4 — line-clamp (not inherited)
    "line-clamp": "none",
    "-webkit-line-clamp": "none",
    # CSS Masking Level 1 §7 — mask-border longhands + shorthand sentinel
    "mask-border": "",
    "mask-border-source": "none",
    "mask-border-slice": "0",
    "mask-border-width": "auto",
    "mask-border-outset": "0",
    "mask-border-repeat": "stretch",
    "mask-border-mode": "alpha",
    # --- NEW: ,  — CSS property tail (GAP-067) ---
    # CSS Overflow Level 3 §6 — overflow-anchor (not inherited)
    "overflow-anchor": "auto",
    # CSS Overscroll — logical axis longhands (physical overscroll-behavior-x/y already present)
    "overscroll-behavior-block": "auto",
    "overscroll-behavior-inline": "auto",
    # CSS Motion Path Level 1 §7.2 — offset-position longhand
    "offset-position": "normal",
    # CSS Color Adjust Level 1 §3 — synonym for print-color-adjust; still in active use
    "color-adjust": "economy",
    # CSS Text Level 4 §4.1 — white-space-collapse (longhand split from white-space shorthand)
    "white-space-collapse": "collapse",
    # Vendor-prefixed appearance (same default as appearance: none)
    "-webkit-appearance": "none",
}

_SHORTHAND_EXPANSIONS: dict[str, tuple[str, ...]] = {
    "margin": ("margin-top", "margin-right", "margin-bottom", "margin-left"),
    "padding": ("padding-top", "padding-right", "padding-bottom", "padding-left"),
    "border": (
        "border-top-width",
        "border-top-style",
        "border-top-color",
        "border-right-width",
        "border-right-style",
        "border-right-color",
        "border-bottom-width",
        "border-bottom-style",
        "border-bottom-color",
        "border-left-width",
        "border-left-style",
        "border-left-color",
    ),
    "border-top": ("border-top-width", "border-top-style", "border-top-color"),
    "border-right": ("border-right-width", "border-right-style", "border-right-color"),
    "border-bottom": ("border-bottom-width", "border-bottom-style", "border-bottom-color"),
    "border-left": ("border-left-width", "border-left-style", "border-left-color"),
    # --- NEW: ,  ---
    "background": (
        "background-image",
        "background-position",
        "background-size",
        "background-repeat",
        "background-attachment",
        "background-clip",
        "background-origin",
        "background-color",
    ),
    "border-radius": (
        "border-top-left-radius",
        "border-top-right-radius",
        "border-bottom-right-radius",
        "border-bottom-left-radius",
    ),
    "flex": ("flex-grow", "flex-shrink", "flex-basis"),
    "flex-flow": ("flex-direction", "flex-wrap"),
    "gap": ("row-gap", "column-gap"),
    "transition": (
        "transition-property",
        "transition-duration",
        "transition-timing-function",
        "transition-delay",
    ),
    "animation": (
        "animation-name",
        "animation-duration",
        "animation-timing-function",
        "animation-delay",
        "animation-iteration-count",
        "animation-direction",
        "animation-fill-mode",
        "animation-play-state",
    ),
    "columns": ("column-count", "column-width"),
    "column-rule": ("column-rule-color", "column-rule-style", "column-rule-width"),
    "place-items": ("align-items", "justify-items"),
    "place-content": ("align-content", "justify-content"),
    "place-self": ("align-self", "justify-self"),
    "overscroll-behavior": ("overscroll-behavior-x", "overscroll-behavior-y"),
    # --- NEW: ,  ---
    "font": (
        "font-style",
        "font-variant",
        "font-weight",
        "font-stretch",
        "font-size",
        "line-height",
        "font-family",
    ),
    "list-style": (
        "list-style-position",
        "list-style-image",
        "list-style-type",
    ),
    "text-decoration": (
        "text-decoration-line",
        "text-decoration-style",
        "text-decoration-color",
        "text-decoration-thickness",
    ),
    "inset": ("top", "right", "bottom", "left"),
    # --- NEW: ,  ---
    "outline": ("outline-width", "outline-style", "outline-color"),
    # --- NEW: ,  ---
    "overflow": ("overflow-x", "overflow-y"),
    "grid-column": ("grid-column-start", "grid-column-end"),
    "grid-row": ("grid-row-start", "grid-row-end"),
    "grid-area": (
        "grid-row-start",
        "grid-column-start",
        "grid-row-end",
        "grid-column-end",
    ),
    "grid-template": (
        "grid-template-rows",
        "grid-template-columns",
        "grid-template-areas",
    ),
    # --- NEW: ,  — CSS Logical Properties Level 1 shorthands ---
    # Two-value axis shorthands (margin/padding/inset): start and end longhands.
    # Dispatched via _TWO_VALUE_AXIS in _expand_shorthand_value.
    "margin-block": ("margin-block-start", "margin-block-end"),
    "margin-inline": ("margin-inline-start", "margin-inline-end"),
    "padding-block": ("padding-block-start", "padding-block-end"),
    "padding-inline": ("padding-inline-start", "padding-inline-end"),
    "inset-block": ("inset-block-start", "inset-block-end"),
    "inset-inline": ("inset-inline-start", "inset-inline-end"),
    # Per-side border shorthands (3 longhands each): dispatched via _expand_border_shorthand.
    "border-block-start": (
        "border-block-start-width",
        "border-block-start-style",
        "border-block-start-color",
    ),
    "border-block-end": (
        "border-block-end-width",
        "border-block-end-style",
        "border-block-end-color",
    ),
    "border-inline-start": (
        "border-inline-start-width",
        "border-inline-start-style",
        "border-inline-start-color",
    ),
    "border-inline-end": (
        "border-inline-end-width",
        "border-inline-end-style",
        "border-inline-end-color",
    ),
    # Axis border shorthands (6 longhands each): dispatched via _expand_border_axis_shorthand.
    "border-block": (
        "border-block-start-width",
        "border-block-start-style",
        "border-block-start-color",
        "border-block-end-width",
        "border-block-end-style",
        "border-block-end-color",
    ),
    "border-inline": (
        "border-inline-start-width",
        "border-inline-start-style",
        "border-inline-start-color",
        "border-inline-end-width",
        "border-inline-end-style",
        "border-inline-end-color",
    ),
    # --- NEW: ,  — Physical border sub-shorthands ---
    # These three shorthands each have exactly four longhands following the
    # standard 1-4 token positional box-model broadcast (top/right/bottom/left).
    # The existing generic broadcaster in _expand_shorthand_value handles them
    # automatically — no new dispatch branch is needed.
    "border-color": (
        "border-top-color",
        "border-right-color",
        "border-bottom-color",
        "border-left-color",
    ),
    "border-style": (
        "border-top-style",
        "border-right-style",
        "border-bottom-style",
        "border-left-style",
    ),
    "border-width": (
        "border-top-width",
        "border-right-width",
        "border-bottom-width",
        "border-left-width",
    ),
    # --- NEW: ,  — Property table completeness tail ---
    # CSS Scroll Snap Level 1 §9.1 — 4-box broadcast (same as margin/padding)
    "scroll-margin": (
        "scroll-margin-top",
        "scroll-margin-right",
        "scroll-margin-bottom",
        "scroll-margin-left",
    ),
    # CSS Scroll Snap Level 1 §9.2 — 4-box broadcast (same as margin/padding)
    "scroll-padding": (
        "scroll-padding-top",
        "scroll-padding-right",
        "scroll-padding-bottom",
        "scroll-padding-left",
    ),
    # CSS Masking Level 1 §2 — 8-longhand broadcast (dispatched via mask arm)
    "mask": (
        "mask-image",
        "mask-mode",
        "mask-position",
        "mask-size",
        "mask-repeat",
        "mask-origin",
        "mask-clip",
        "mask-composite",
    ),
    # --- NEW: ,  — SVG + Motion Path shorthands ---
    # SVG 1.1 §11.6 — marker shorthand → 3-longhand positional broadcast
    "marker": (
        "marker-start",
        "marker-mid",
        "marker-end",
    ),
    # CSS Motion Path Level 1 — offset shorthand → 4-longhand positional broadcast
    "offset": (
        "offset-path",
        "offset-distance",
        "offset-rotate",
        "offset-anchor",
    ),
    # --- NEW: ,  — CSS Container Queries Level 1 §3.1 ---
    "container": ("container-name", "container-type"),
    # --- NEW: ,  — CSS Animations Level 2 §4.2 ---
    # animation-range uses space-separated two-value broadcast (same as container).
    "animation-range": ("animation-range-start", "animation-range-end"),
    # --- NEW: ,  ---
    # CSS Grid Level 1 §10 — grid mega-shorthand
    "grid": (
        "grid-template-rows",
        "grid-template-columns",
        "grid-template-areas",
        "grid-auto-rows",
        "grid-auto-columns",
        "grid-auto-flow",
    ),
    # CSS Backgrounds Level 3 §6.6 — border-image shorthand
    "border-image": (
        "border-image-source",
        "border-image-slice",
        "border-image-width",
        "border-image-outset",
        "border-image-repeat",
    ),
    # CSS Masking Level 1 §7 — mask-border shorthand
    "mask-border": (
        "mask-border-source",
        "mask-border-slice",
        "mask-border-width",
        "mask-border-outset",
        "mask-border-repeat",
        "mask-border-mode",
    ),
}

_BORDER_STYLE_TOKENS: frozenset[str] = frozenset(
    {
        "none",
        "hidden",
        "dotted",
        "dashed",
        "solid",
        "double",
        "groove",
        "ridge",
        "inset",
        "outset",
    }
)
_BORDER_WIDTH_LENGTH_RE = re.compile(r"^(?:\d+(?:\.\d+)?|\.\d+)[a-z%]+$", re.IGNORECASE)

# --- NEW: ,  — two-value axis shorthands for logical properties.
# These six shorthands each have exactly two longhands (start and end) and use
# the CSS two-value box-model rule: one token → both sides; two tokens → start
# then end.  Named here so _expand_shorthand_value can dispatch them before the
# generic 1-4 token broadcast path.
_TWO_VALUE_AXIS: frozenset[str] = frozenset(
    {
        "margin-block",
        "margin-inline",
        "padding-block",
        "padding-inline",
        "inset-block",
        "inset-inline",
    }
)

# Per-side logical border shorthands (3 longhands each) — dispatched through
# _expand_border_shorthand, the same code path as border-top/right/bottom/left.
_LOGICAL_BORDER_SIDE_SHORTHANDS: frozenset[str] = frozenset(
    {
        "border-block-start",
        "border-block-end",
        "border-inline-start",
        "border-inline-end",
    }
)

# Axis logical border shorthands (6 longhands each) — sets width/style/color
# for both start and end sides of the block or inline axis simultaneously.
_LOGICAL_BORDER_AXIS_SHORTHANDS: frozenset[str] = frozenset(
    {
        "border-block",
        "border-inline",
    }
)

# --- NEW: ,  — classification frozensets for shorthand helpers ---

# font shorthand keyword sets (CSS Fonts Level 4 §3.3)
_FONT_STYLE_TOKENS: frozenset[str] = frozenset({"normal", "italic", "oblique"})
_FONT_VARIANT_TOKENS: frozenset[str] = frozenset({"normal", "small-caps"})
_FONT_WEIGHT_TOKENS: frozenset[str] = frozenset(
    {
        "normal",
        "bold",
        "bolder",
        "lighter",
        "100",
        "200",
        "300",
        "400",
        "500",
        "600",
        "700",
        "800",
        "900",
    }
)
_FONT_STRETCH_TOKENS: frozenset[str] = frozenset(
    {
        "normal",
        "ultra-condensed",
        "extra-condensed",
        "condensed",
        "semi-condensed",
        "semi-expanded",
        "expanded",
        "extra-expanded",
        "ultra-expanded",
    }
)
# Size token pattern: numeric value with a CSS length/percentage unit,
# optionally followed by /line-height (e.g. "24px/1.5" or "120%/1.2em").
# Group 1 captures the size portion; group 2 (optional) captures line-height.
_FONT_SIZE_RE = re.compile(r"^([\d.]+[a-z%]+)(?:/([\d.]+(?:[a-z%]+)?))?$", re.IGNORECASE)
# System-font keywords that short-circuit expansion (return {})
_FONT_SYSTEM_KEYWORDS: frozenset[str] = frozenset(
    {"caption", "icon", "menu", "message-box", "small-caption", "status-bar"}
)

# list-style shorthand keyword sets (CSS Lists Level 3 §2)
_LIST_STYLE_POSITION_TOKENS: frozenset[str] = frozenset({"inside", "outside"})
_LIST_STYLE_TYPE_TOKENS: frozenset[str] = frozenset(
    {
        "disc",
        "circle",
        "square",
        "decimal",
        "decimal-leading-zero",
        "lower-roman",
        "upper-roman",
        "lower-greek",
        "lower-latin",
        "upper-latin",
        "armenian",
        "georgian",
        "lower-alpha",
        "upper-alpha",
        "none",
    }
)

# text-decoration shorthand keyword sets (CSS Text Decoration Level 4 §2)
_TEXT_DECORATION_LINE_TOKENS: frozenset[str] = frozenset(
    {"none", "underline", "overline", "line-through", "blink"}
)
_TEXT_DECORATION_STYLE_TOKENS: frozenset[str] = frozenset(
    {"solid", "double", "dotted", "dashed", "wavy"}
)
# Length/percentage pattern for text-decoration-thickness
_TEXT_DECORATION_THICKNESS_RE = re.compile(r"^[\d.]+[a-z%]+$", re.IGNORECASE)
# Common CSS named color keywords (sufficient for text-decoration-color detection)
_CSS_COLOR_KEYWORDS: frozenset[str] = frozenset(
    {
        "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure",
        "beige", "bisque", "black", "blanchedalmond", "blue",
        "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse",
        "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson",
        "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray",
        "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen",
        "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen",
        "darkslateblue", "darkslategray", "darkslategrey", "darkturquoise",
        "darkviolet", "deeppink", "deepskyblue", "dimgray", "dimgrey",
        "dodgerblue", "firebrick", "floralwhite", "forestgreen", "fuchsia",
        "gainsboro", "ghostwhite", "gold", "goldenrod", "gray", "green",
        "greenyellow", "grey", "honeydew", "hotpink", "indianred", "indigo",
        "ivory", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon",
        "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray",
        "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen",
        "lightskyblue", "lightslategray", "lightslategrey", "lightsteelblue",
        "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon",
        "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple",
        "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise",
        "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin",
        "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange",
        "orangered", "orchid", "palegoldenrod", "palegreen", "paleturquoise",
        "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum",
        "powderblue", "purple", "rebeccapurple", "red", "rosybrown", "royalblue",
        "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna",
        "silver", "skyblue", "slateblue", "slategray", "slategrey", "snow",
        "springgreen", "steelblue", "tan", "teal", "thistle", "tomato",
        "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow",
        "yellowgreen", "currentcolor", "transparent", "inherit", "initial",
        "unset", "revert",
    }
)

_LOGICAL_PROPERTY_ALIASES: dict[str, str] = {
    # Formerly aliased logical properties have been promoted to independent
    # cascade registrations in  ().  Logical and physical
    # properties are now independent per FR-11 — no alias mapping.
}

_MEDIA_BASELINE_ENV: dict[str, str] = {
    "type": "screen",
    "prefers-color-scheme": "light",
}

# outline shorthand token sets — placed here (data layer) so _cascade_shorthands
# can import them without pulling in engine-layer symbols.
_OUTLINE_STYLE_TOKENS: frozenset[str] = frozenset(
    {"none", "dotted", "dashed", "solid", "double", "groove", "ridge", "inset", "outset", "hidden"}
)
_OUTLINE_WIDTH_RE = re.compile(r"^(?:\d+(?:\.\d+)?|\.\d+)[a-z%]+$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class _Candidate:
    """A single resolved CSS declaration candidate.

    ``origin`` is ``"ua"`` for user-agent stylesheet rules or ``"author"``
    for both author stylesheet rules *and* inline ``style`` attribute
    declarations.  Inline declarations are not a separate cascade origin per
    CSS Cascading Level 4 §6.4.2; they are ``origin="author"`` with
    ``specificity=(1, 0, 0)``.

    The ``"ua"`` origin is reserved for forward compatibility; this build has
    no UA stylesheet and never constructs ``origin="ua"`` candidates.
    """

    property_name: str
    value: str
    origin: Literal["ua", "author"]
    important: bool
    specificity: tuple[int, int, int]
    style_sheet_index: int
    layer_tier: int
    rule_index: int
    media_rule_child_index: int
    declaration_index: int
    expanded_index: int

    def precedence_key(self) -> tuple[int, int, tuple[int, int, int], int, int, int, int, int, int]:
        """Return a sort key implementing CSS Cascading Level 4 §4 and Level 5 §6 ordering.

        Higher values win.  Tuple layout::

            (importance, origin_tier, specificity, style_sheet_index,
             layer_tier, rule_index, media_rule_child_index,
             declaration_index, expanded_index)

        Origin tiers:

        - Normal declarations:    author=1, ua=0  (author beats ua)
        - !important declarations: ua=2, author=1  (ua !important beats author
          !important — inverted origin order per CSS Level 4 §4)

        ``importance`` is 1 for ``!important``, 0 otherwise, so all important
        declarations outrank all normal ones within the same origin ordering
        before the origin tier is compared.

        ``layer_tier`` encodes CSS Cascade Level 5 §6 layer-order priority:
        unlayered rules receive ``total_layers + 1`` (sentinel, always highest);
        rules inside the *k*-th ``@layer`` block receive
        ``total_layers - 1 - k`` (earlier layers beat later ones).

        Examples
        --------
        Author ``!important`` outranks normal author (same origin, higher
        importance):

        >>> from aspose_html.dom._cascade_data import _Candidate
        >>> imp = _Candidate("color", "red", "author", True,  (0, 1, 0), 0, 1, 1, 0, 0, 0)
        >>> nrm = _Candidate("color", "blue", "author", False, (0, 1, 0), 0, 1, 0, 0, 0, 0)
        >>> imp.precedence_key() > nrm.precedence_key()
        True

        UA ``!important`` outranks author ``!important`` (inverted origin
        order for important declarations):

        >>> ua_imp  = _Candidate("color", "red",  "ua",     True, (0, 0, 0), 0, 1, 0, 0, 0, 0)
        >>> auth_imp = _Candidate("color", "blue", "author", True, (0, 0, 0), 0, 1, 0, 0, 0, 0)
        >>> ua_imp.precedence_key() > auth_imp.precedence_key()
        True

        Author normal beats ua normal (standard origin order):

        >>> auth_nrm = _Candidate("color", "red",  "author", False, (0, 0, 0), 0, 1, 0, 0, 0, 0)
        >>> ua_nrm   = _Candidate("color", "blue", "ua",     False, (0, 0, 0), 0, 1, 0, 0, 0, 0)
        >>> auth_nrm.precedence_key() > ua_nrm.precedence_key()
        True

        Unlayered rule (layer_tier=2) beats layered rule (layer_tier=1) at
        equal specificity and source position:

        >>> unlayered = _Candidate("color", "red",  "author", False, (0, 1, 0), 0, 2, 1, 0, 0, 0)
        >>> layered   = _Candidate("color", "blue", "author", False, (0, 1, 0), 0, 1, 2, 0, 0, 0)
        >>> unlayered.precedence_key() > layered.precedence_key()
        True
        """
        if self.important:
            # Inverted: ua !important (2) beats author !important (1)
            origin_tier: int = {"ua": 2, "author": 1}[self.origin]
        else:
            # Normal: author (1) beats ua (0)
            origin_tier = {"ua": 0, "author": 1}[self.origin]

        return (
            1 if self.important else 0,
            origin_tier,
            self.specificity,
            self.style_sheet_index,
            self.layer_tier,
            self.rule_index,
            self.media_rule_child_index,
            self.declaration_index,
            self.expanded_index,
        )


_KNOWN_PROPERTIES: frozenset[str] = frozenset(_INITIAL_VALUE_BASELINE) | _INHERITED_PROPERTIES
