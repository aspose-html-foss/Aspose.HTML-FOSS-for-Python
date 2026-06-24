"""Cascade style resolution engine for Element.get_computed_style().

Phase-4 scope (): resolve supported declarations from attached
stylesheets and inline style declarations with deterministic precedence by
`!important` > specificity > source order, then fill inherited values for
the full set of CSS inherited properties (``_INHERITED_PROPERTIES``) and
custom properties (``--*``) from nearest ancestor computed style (or
deterministic root fallback), including CSS-wide keyword semantics
(``inherit``, ``initial``, ``unset``, ``revert``) and deterministic baseline
shorthand expansion (``margin``/``padding``).

Phase-6 scope (): Origin ordering per CSS Cascading Level 4 §4.
Inline declarations are **not** a separate cascade origin; they are author
declarations with specificity ``(1, 0, 0)`` per §6.4.2.  ``!important``
inverts origin ordering so that ``ua !important`` beats ``author !important``.

Phase-7 scope (): Full inheritance engine.  ``_INHERITED_PROPERTIES``
is a ~50-property frozenset per CSS Cascading Level 4 Appendix A.  The
``revert`` keyword falls back to ``unset`` semantics (CSS Level 4 §7.5);
revert-to-UA is a deferred follow-up ( HI-2 / AC-10).

M7 UA origin ( / , ): ``_resolve_local_winners`` now
seeds ``origin="ua"`` candidates from the transcribed UA default-``display``
table (:mod:`aspose_html.dom._ua_stylesheet`) before the author/inline loops,
so a ``<div>`` resolves to ``display: block`` (etc.) instead of the §2 initial
``inline``. This feeds the *existing* ``_Candidate.precedence_key()`` UA tier —
it is NOT a second cascade ( §2). Scope is default ``display`` only.

Phase-8 scope (): CSS Cascade Level 5 §6 layer-order priority.
``_iter_applicable_style_rules`` pre-scans each stylesheet to assign a
``layer_tier`` to every rule.  Unlayered rules receive
``layer_tier = total_layer_blocks + 1`` (sentinel, always highest).  Rules
inside the *k*-th ``@layer`` block (0-based) receive
``layer_tier = total_layer_blocks - 1 - k``, so earlier layers beat later
ones while all layers lose to unlayered rules at equal specificity.

Data layer (property tables, _Candidate): see _cascade_data.py ().
Shorthand helpers and tokenizer utilities: see _cascade_shorthands.py ().

Origin tiers (higher = wins, encoded in ``_Candidate.precedence_key()``)::

    Normal:    author(1) > ua(0)
    Important: ua(2)     > author(1)   [inverted per CSS Level 4 §4]

Examples
--------
Author ``!important`` beats non-important inline (inline is just author with
high specificity; author ``!important`` outranks any normal declaration):

>>> from aspose_html.cssom import CSSStyleSheet
>>> from aspose_html.dom import Document
>>> doc = Document()
>>> el = doc.create_element("div")
>>> _ = doc.append_child(el)
>>> sheet = CSSStyleSheet()
>>> sheet.replace_sync("div { color: red !important }")
>>> doc.attach_style_sheet(sheet)
>>> el.style.set_property("color", "blue")
>>> style = el.get_computed_style()
>>> style.get_property_value("color")
'red'

Inherited properties propagate from parent to child automatically:

>>> doc2 = Document()
>>> parent = doc2.create_element("div")
>>> child = doc2.create_element("span")
>>> _ = doc2.append_child(parent)
>>> _ = parent.append_child(child)
>>> sheet2 = CSSStyleSheet()
>>> sheet2.replace_sync("div { color: green; text-align: center }")
>>> doc2.attach_style_sheet(sheet2)
>>> child_style = child.get_computed_style()
>>> child_style.get_property_value("color")
'green'
>>> child_style.get_property_value("text-align")
'center'
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from aspose_html.css import element_matches
from aspose_html.css._matcher import _matches_complex
from aspose_html.css._parser import parse
from aspose_html.css._specificity import specificity
from aspose_html.cssom import CSSLayerBlockRule, CSSMediaRule, CSSStyleRule, CSSSupportsRule

from aspose_html.dom._cascade_data import (
    _SUPPORTED_NAME_RE, _CUSTOM_PROPERTY_NAME_RE, _IMPORTANT_SUFFIX_RE,
    _VAR_FUNCTION_FULL_RE, _ENV_FUNCTION_FULL_RE,
    _INHERITED_PROPERTIES, _INITIAL_VALUE_BASELINE, _KNOWN_PROPERTIES,
    _MEDIA_BASELINE_ENV, _Candidate,
)
from aspose_html.dom._cascade_shorthands import (
    _iter_expanded_declarations, _iter_logical_alias_declarations,
    _split_top_level, _outer_parens_balanced,
    _looks_like_full_value_var_call, _looks_like_full_value_env_call,
    _resolve_env_function,
)
from aspose_html.dom._ua_stylesheet import ua_declarations_for

if TYPE_CHECKING:
    from aspose_html.dom import Element


def _match_single_media_query(query: str) -> bool:
    query = query.strip().lower()
    if not query:
        return False

    if " or " in query:
        return False

    clauses = [part.strip() for part in query.split(" and ")]
    if any(not clause for clause in clauses):
        return False

    for clause in clauses:
        negate = False
        if clause.startswith("not "):
            negate = True
            clause = clause[4:].strip()
            if not clause:
                return False

        if clause == "all":
            matched = True
        elif clause == "screen":
            matched = _MEDIA_BASELINE_ENV["type"] == "screen"
        elif clause == "print":
            matched = _MEDIA_BASELINE_ENV["type"] == "print"
        elif clause.startswith("(") and clause.endswith(")"):
            inner = clause[1:-1].strip()
            if not inner or inner.count(":") != 1:
                return False
            name, value = [part.strip() for part in inner.split(":", 1)]
            if name != "prefers-color-scheme" or value not in {"light", "dark"}:
                return False
            matched = _MEDIA_BASELINE_ENV["prefers-color-scheme"] == value
        else:
            return False

        if negate:
            matched = not matched
        if not matched:
            return False

    return True


def _media_query_matches(media_text: str) -> bool:
    """Return whether *media_text* matches the phase-2 baseline env.

    Unsupported or malformed members are treated as non-matching.
    A comma-separated list matches when any member matches.
    """
    normalized = media_text.strip().lower()
    if not normalized:
        return False

    members = [member.strip() for member in normalized.split(",")]
    if any(not member for member in members):
        return False
    return any(_match_single_media_query(member) for member in members)


def _eval_supports_clause(text: str) -> bool:
    """Recursively evaluate one @supports condition clause.

    Handles: ``(property: value)``, ``not <clause>``,
    ``<clause> and <clause>``, ``<clause> or <clause>``.
    Returns ``False`` for any unrecognised syntax.
    """
    text = text.strip()
    if not text:
        return False

    # --- not <clause> ---
    if text.lower().startswith("not "):
        inner = text[4:].strip()
        if not inner:
            return False
        return not _eval_supports_clause(inner)

    # --- (property: value) ---
    # Only treat as a single wrapped form when the opening ( is balanced by
    # the closing ) at the very end (depth reaches 0 exactly at the last char).
    if text.startswith("(") and text.endswith(")") and _outer_parens_balanced(text):
        inner = text[1:-1].strip()
        # Must be a single colon-separated name:value pair
        colon_pos = inner.find(":")
        if colon_pos < 1:
            return False
        prop_name = inner[:colon_pos].strip().lower()
        # Reject nested selector() inside parens
        if prop_name == "selector":
            return False
        # Check property name is known
        if _SUPPORTED_NAME_RE.fullmatch(prop_name):
            return prop_name in _KNOWN_PROPERTIES
        return False

    # --- <clause> and <clause> (split at top-level " and ") ---
    and_parts = _split_top_level(text, " and ")
    if len(and_parts) > 1:
        return all(_eval_supports_clause(part) for part in and_parts)

    # --- <clause> or <clause> (split at top-level " or ") ---
    or_parts = _split_top_level(text, " or ")
    if len(or_parts) > 1:
        return any(_eval_supports_clause(part) for part in or_parts)

    # Unknown form
    return False


def _supports_condition_matches(condition_text: str) -> bool:
    """Return whether *condition_text* satisfies the @supports baseline.

    Supported forms
    ---------------
    - ``(property: value)``  — True when property name is known to the
      cascade engine (present in ``_INITIAL_VALUE_BASELINE``,
      ``_INHERITED_PROPERTIES``, or matching ``_SUPPORTED_NAME_RE``).
      The *value* token is ignored — only property name is checked.
    - ``not <form>``         — negates the inner form.
    - ``<form> and <form>``  — True when ALL clauses match.
    - ``<form> or <form>``   — True when ANY clause matches.
    - ``selector(...)``      — always False (not evaluated).
    - Empty / malformed      — always False.

    Examples
    --------
    >>> _supports_condition_matches("(color: red)")
    True
    >>> _supports_condition_matches("(color: red) and (font-size: 1em)")
    True
    >>> _supports_condition_matches("not (color: red)")
    False
    >>> _supports_condition_matches("(--custom-flag: 1)")
    False
    >>> _supports_condition_matches("selector(div > p)")
    False
    >>> _supports_condition_matches("")
    False
    """
    text = condition_text.strip()
    if not text:
        return False
    # Reject selector() form
    if text.lower().startswith("selector("):
        return False
    # Delegate to the recursive clause evaluator
    return _eval_supports_clause(text)


def _scan_layer_tiers(sheet: object) -> tuple[int, dict[int, int]]:
    """Pre-scan *sheet* and return ``(total, mapping)`` for layer-tier encoding.

    ``total`` is the number of ``CSSLayerBlockRule`` objects at the top level
    of the sheet's ``css_rules``.

    ``mapping`` maps ``rule_index`` → 0-based ``layer_block_number`` for each
    top-level ``CSSLayerBlockRule``; non-layer rule indices are absent.

    Layer-tier encoding (CSS Cascade Level 5 §6):

    - Unlayered rule at any position: ``layer_tier = total + 1`` (sentinel).
    - Rule inside the *k*-th ``@layer`` block: ``layer_tier = total - 1 - k``.

    This maps "first layer wins" onto "higher tier = higher key" without
    inverting the sort direction.  When ``total == 0`` every rule gets
    ``layer_tier = 1``, which is identical to the pre-layer behaviour.

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> sheet = CSSStyleSheet.from_text(
    ...     "@layer base { p { color: red } } @layer theme { p { color: blue } } p { margin: 0 }"
    ... )
    >>> total, mapping = _scan_layer_tiers(sheet)
    >>> total
    2
    >>> mapping == {0: 0, 1: 1}
    True
    """
    from aspose_html.cssom import CSSLayerBlockRule as _LBR  # noqa: PLC0415

    layer_block_number = 0
    mapping: dict[int, int] = {}
    for rule_index, rule in enumerate(sheet.css_rules):
        if isinstance(rule, _LBR):
            mapping[rule_index] = layer_block_number
            layer_block_number += 1
    return layer_block_number, mapping


def _iter_applicable_style_rules(
    element: "Element",
) -> Iterator[tuple[int, int, int, int, CSSStyleRule]]:
    """Yield applicable style rules with layer-aware source-order coordinates.

    Yields 5-tuples ``(style_sheet_index, layer_tier, rule_index, child_index,
    rule)`` for every ``CSSStyleRule`` that is applicable to *element* through
    any top-level or conditional at-rule.

    ``layer_tier`` encodes CSS Cascade Level 5 §6 layer-order priority so that
    higher tiers win in ``_Candidate.precedence_key()``:

    - Unlayered rules: ``layer_tier = total_layer_blocks_in_sheet + 1``
      (sentinel; always beats any layered tier).
    - Rules inside the *k*-th ``@layer`` block (0-based): ``layer_tier =
      total_layer_blocks - 1 - k`` (earlier layers get larger tiers).

    When a sheet contains no ``@layer`` blocks every rule receives
    ``layer_tier = 1``, which is equivalent to the pre-layer behaviour.
    """
    for style_sheet_index, sheet in enumerate(element.style_sheets):
        total_layers, layer_index_map = _scan_layer_tiers(sheet)
        unlayered_tier = total_layers + 1

        for rule_index, rule in enumerate(sheet.css_rules):
            if isinstance(rule, CSSStyleRule):
                yield (style_sheet_index, unlayered_tier, rule_index, 0, rule)
                continue
            if isinstance(rule, CSSMediaRule):
                if not _media_query_matches(rule.media_text):
                    continue
                for child_index, child_rule in enumerate(rule.css_rules):
                    if isinstance(child_rule, CSSStyleRule):
                        yield (style_sheet_index, unlayered_tier, rule_index, child_index, child_rule)
                continue
            if isinstance(rule, CSSSupportsRule):
                if not _supports_condition_matches(rule.condition_text):
                    continue
                for child_index, child_rule in enumerate(rule.css_rules):
                    if isinstance(child_rule, CSSStyleRule):
                        yield (style_sheet_index, unlayered_tier, rule_index, child_index, child_rule)
                continue
            if isinstance(rule, CSSLayerBlockRule):
                # CSS Cascade Level 5 §6: earlier @layer blocks have higher
                # priority than later ones.  Compute the layer_tier for this
                # block using the pre-scanned mapping.
                layer_block_num = layer_index_map[rule_index]
                layer_tier = total_layers - 1 - layer_block_num
                for child_index, child_rule in enumerate(rule.css_rules):
                    if isinstance(child_rule, CSSStyleRule):
                        yield (style_sheet_index, layer_tier, rule_index, child_index, child_rule)
                continue


class ComputedStyleDeclaration:
    """Read-only resolved style declarations for an element.

    The object is a snapshot: values are resolved at call time and are not
    live-updated if stylesheets later change.

    Examples
    --------
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> el = doc.create_element("div")
    >>> doc.append_child(el)
    <Element 'DIV'>
    >>> sheet = CSSStyleSheet()
    >>> sheet.replace_sync("div { color: red; margin: 0 }")
    >>> doc.attach_style_sheet(sheet)
    >>> style = el.get_computed_style()
    >>> style.length
    6
    >>> style.item(0)
    'color'
    >>> style.get_property_value("color")
    'red'
    >>> style.get_property_value("margin-top")
    '0'
    >>> style.get_property_value("display")  # UA default for <div> (, §15.3.3)
    'block'
    """

    __slots__ = ("_properties",)

    def __init__(self, properties: dict[str, str]) -> None:
        self._properties: dict[str, str] = dict(sorted(properties.items()))

    @property
    def length(self) -> int:
        """Number of resolved properties."""
        return len(self._properties)

    def item(self, index: int) -> str | None:
        """Return property name at *index* or ``None`` when out-of-range."""
        if index < 0 or index >= len(self._properties):
            return None
        return tuple(self._properties.keys())[index]

    def get_property_value(self, name: str) -> str:
        """Return resolved property value or ``''`` when absent."""
        return self._properties.get(name.strip().lower(), "")

    def __len__(self) -> int:
        return len(self._properties)

    def __iter__(self) -> Iterator[str]:
        return iter(self._properties)

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False
        return name.strip().lower() in self._properties

    def __getitem__(self, name: str) -> str:
        normalized = name.strip().lower()
        if normalized not in self._properties:
            raise KeyError(name)
        return self._properties[normalized]


def _parse_specificity_for_matching_selector(element: "Element", selector_text: str) -> tuple[int, int, int]:
    """Return max specificity among selector branches matching *element*.

    Defensive fallback: malformed selectors are skipped by caller; this helper
    returns ``(0, 0, 0)`` if nothing matches.
    """
    parsed = parse(selector_text, forgiving=True)
    matched_specificities = [
        specificity(complex_selector)
        for complex_selector in parsed.selectors
        if _matches_complex(element, complex_selector)
    ]
    return max(matched_specificities, default=(0, 0, 0))


def _normalize_declaration(name: str, value: str) -> tuple[str, str, bool] | None:
    """Normalize a declaration or return ``None`` for unsupported input."""
    normalized_name = name.strip().lower()

    is_custom_property = normalized_name.startswith("--")
    if is_custom_property:
        if not _is_valid_custom_property_name(normalized_name):
            return None
    elif not _SUPPORTED_NAME_RE.fullmatch(normalized_name):
        return None

    normalized_value = value.strip()
    if not normalized_value:
        return None

    important = bool(_IMPORTANT_SUFFIX_RE.search(normalized_value))
    if important:
        normalized_value = _IMPORTANT_SUFFIX_RE.sub("", normalized_value).strip()
        if not normalized_value:
            return None

    return (normalized_name, normalized_value, important)


def _is_valid_custom_property_name(name: str) -> bool:
    """Return whether *name* is accepted as a baseline custom-property name."""
    return bool(_CUSTOM_PROPERTY_NAME_RE.fullmatch(name))


def _parse_var_function(value: str) -> tuple[str, str | None] | None:
    """Parse a baseline full-value ``var(...)`` reference.

    Accepted forms:
    - ``var(--name)``
    - ``var(--name, fallback)``

    Returns ``(name, fallback_or_none)`` when the full value matches one of the
    baseline forms; otherwise returns ``None``.
    """
    match = _VAR_FUNCTION_FULL_RE.fullmatch(value.strip())
    if match is None:
        return None

    inner = match.group(1).strip()
    if not inner:
        return None

    name_part, has_comma, fallback_part = inner.partition(",")
    reference_name = name_part.strip().lower()

    if not has_comma:
        return (reference_name, None)

    return (reference_name, fallback_part.strip())


def _resolve_custom_property_value(
    name: str,
    custom_properties: dict[str, str],
    memo: dict[str, str | None],
    visiting: set[str],
) -> str | None:
    """Resolve custom-property *name* with deterministic cycle handling."""
    if name in memo:
        return memo[name]

    if name in visiting:
        return None

    raw_value = custom_properties.get(name)
    if raw_value is None:
        memo[name] = None
        return None

    parsed = _parse_var_function(raw_value)
    if parsed is None:
        if _looks_like_full_value_var_call(raw_value):
            memo[name] = None
            return None
        memo[name] = raw_value
        return raw_value

    reference_name, fallback = parsed
    if not _is_valid_custom_property_name(reference_name):
        result = fallback if fallback else None
        memo[name] = result
        return result

    visiting.add(name)
    try:
        referenced = _resolve_custom_property_value(reference_name, custom_properties, memo, visiting)
    finally:
        visiting.discard(name)

    if referenced is not None:
        memo[name] = referenced
        return referenced

    result = fallback if fallback else None
    memo[name] = result
    return result


def _resolve_regular_property_value(
    raw_value: str,
    custom_properties: dict[str, str],
    memo: dict[str, str | None],
) -> str | None:
    """Resolve a regular property value with deterministic ``var()``/``env()`` semantics.

    ``env(name, fallback)`` always resolves to its fallback in headless mode
    (no browser environment is available). ``env(name)`` with no fallback
    returns ``None`` so the caller drops the declaration.
    """
    # env() path: resolve before var() since env() needs no custom-property lookup.
    if raw_value.strip().lower().startswith("env("):
        return _resolve_env_function(raw_value)

    parsed = _parse_var_function(raw_value)
    if parsed is None:
        if _looks_like_full_value_var_call(raw_value):
            return None
        return raw_value

    reference_name, fallback = parsed
    if not _is_valid_custom_property_name(reference_name):
        return fallback if fallback else None

    resolved = _resolve_custom_property_value(reference_name, custom_properties, memo, visiting=set())
    if resolved is not None:
        return resolved

    return fallback if fallback else None


def _resolve_css_wide_keyword_value(
    property_name: str,
    raw_value: str,
    parent_style: ComputedStyleDeclaration | None,
) -> str:
    """Resolve CSS-wide keyword semantics per CSS Cascade Level 4 §7.

    Handled keywords: ``inherit``, ``initial``, ``unset``, ``revert``.

    ``revert`` falls back to ``unset`` semantics in this implementation
    (CSS Level 4 §7.5: when there is no value in the UA origin, ``revert``
    acts as ``unset``).

    .. note::

        () added a UA origin for default ``display`` only.
       Bringing ``revert`` fully to spec — rolling back to the UA-origin
       value when one exists (e.g. ``display: revert`` on a ``<div>`` →
       ``block``, not ``inline``) — requires per-property UA-value lookup at
       keyword-resolution time and its own WPT gate, and is a **deliberate
       follow-up slice** ( HI-2 / AC-10, fenced). Until then
       ``revert`` keeps its ``unset`` fallback; this is a known, documented
       gap, not a silent drift.

    Returns the resolved string value.  For non-keyword inputs, returns
    *raw_value* unchanged.

    Examples
    --------
    ``inherit`` returns the parent value when a parent is present:

    >>> from aspose_html.dom import Document
    >>> doc = Document()
    >>> parent = doc.create_element("div")
    >>> child = doc.create_element("span")
    >>> _ = doc.append_child(parent)
    >>> _ = parent.append_child(child)
    >>> from aspose_html.cssom import CSSStyleSheet
    >>> sheet = CSSStyleSheet()
    >>> sheet.replace_sync("div { color: navy }")
    >>> doc.attach_style_sheet(sheet)
    >>> parent_style = parent.get_computed_style()
    >>> _resolve_css_wide_keyword_value("color", "inherit", parent_style)
    'navy'

    ``initial`` always returns the initial value (empty string here):

    >>> _resolve_css_wide_keyword_value("color", "initial", parent_style)
    ''

    ``unset`` on an inherited property acts as ``inherit``:

    >>> _resolve_css_wide_keyword_value("color", "unset", parent_style)
    'navy'

    ``unset`` on a non-inherited property acts as ``initial``:

    >>> _resolve_css_wide_keyword_value("background-color", "unset", parent_style)
    ''

    ``revert`` behaves as ``unset`` (revert-to-UA deferred —  HI-2):

    >>> _resolve_css_wide_keyword_value("color", "revert", parent_style)
    'navy'
    >>> _resolve_css_wide_keyword_value("background-color", "revert", parent_style)
    ''
    """
    normalized = raw_value.strip().lower()
    if normalized not in {"inherit", "initial", "unset", "revert"}:
        return raw_value

    is_inherited = property_name in _INHERITED_PROPERTIES
    baseline_default = _INITIAL_VALUE_BASELINE.get(property_name, "")

    def _resolve_inherit() -> str:
        if parent_style is not None:
            return parent_style.get_property_value(property_name)
        return baseline_default

    def _resolve_initial() -> str:
        return baseline_default

    if normalized == "inherit":
        return _resolve_inherit()
    if normalized == "initial":
        return _resolve_initial()

    # unset: inherited → inherit, non-inherited → initial
    if normalized == "unset":
        if is_inherited:
            return _resolve_inherit()
        return _resolve_initial()

    # revert: falls back to unset (CSS Level 4 §7.5).  added a UA
    # origin for default `display` only; revert-to-UA correctness is a
    # deliberate follow-up slice (HI-2 / AC-10), so revert keeps unset
    # semantics here. This is a documented gap, not a silent drift.
    if is_inherited:
        return _resolve_inherit()
    return _resolve_initial()


def _resolve_local_winners(element: "Element") -> dict[str, _Candidate]:
    """Resolve local winners from the UA origin + stylesheets + inline declarations."""
    winners: dict[str, _Candidate] = {}

    # --- UA origin (lowest priority) —  /  ---------------
    # CSS Cascading Level 4 §4: the UA origin is the lowest normal-origin
    # tier. Seeded FIRST so later author/inline candidates overwrite it via
    # the existing _Candidate.precedence_key() comparison (author=1 beats
    # ua=0 normal; ua=2 beats author=1 important). This is NOT a second
    # cascade (HI-3 /  §2): one winners dict, one precedence_key().
    for ua_name, ua_value, ua_important in ua_declarations_for(element):
        ua_raw_value = f"{ua_value} !important" if ua_important else ua_value
        normalized = _normalize_declaration(ua_name, ua_raw_value)
        if normalized is None:
            continue

        supported_name, supported_value, important = normalized
        for aliased_name, aliased_value in _iter_logical_alias_declarations(
            supported_name, supported_value
        ):
            for expanded_index, (expanded_name, expanded_value) in enumerate(
                _iter_expanded_declarations(aliased_name, aliased_value)
            ):
                candidate = _Candidate(
                    property_name=expanded_name,
                    value=expanded_value,
                    origin="ua",
                    important=important,
                    specificity=(0, 0, 0),
                    # Sort below any author sheet (index >= 0) and below
                    # unlayered author rules; the origin tier in
                    # precedence_key() is the decisive field — these are
                    # belt-and-braces ties, never an origin inversion.
                    style_sheet_index=-1,
                    layer_tier=0,
                    rule_index=0,
                    media_rule_child_index=0,
                    declaration_index=0,
                    expanded_index=expanded_index,
                )

                current = winners.get(expanded_name)
                if current is None or candidate.precedence_key() >= current.precedence_key():
                    winners[expanded_name] = candidate

    style_sheets = element.style_sheets

    for style_sheet_index, layer_tier, rule_index, media_rule_child_index, rule in _iter_applicable_style_rules(element):

            selector_text = rule.selector_text
            if not element_matches(element, selector_text):
                continue

            try:
                selector_specificity = _parse_specificity_for_matching_selector(element, selector_text)
            except SyntaxError:
                # Defensive: parsed CSSOM rules should already be valid.
                continue

            for declaration_index, property_name in enumerate(rule.style):
                property_value = rule.style.get_property_value(property_name)
                normalized = _normalize_declaration(property_name, property_value)
                if normalized is None:
                    continue

                supported_name, supported_value, important = normalized
                for aliased_name, aliased_value in _iter_logical_alias_declarations(
                    supported_name, supported_value
                ):
                    for expanded_index, (expanded_name, expanded_value) in enumerate(
                        _iter_expanded_declarations(aliased_name, aliased_value)
                    ):
                        candidate = _Candidate(
                            property_name=expanded_name,
                            value=expanded_value,
                            origin="author",
                            important=important,
                            specificity=selector_specificity,
                            style_sheet_index=style_sheet_index,
                            layer_tier=layer_tier,
                            rule_index=rule_index,
                            media_rule_child_index=media_rule_child_index,
                            declaration_index=declaration_index,
                            expanded_index=expanded_index,
                        )

                        current = winners.get(expanded_name)
                        if current is None or candidate.precedence_key() >= current.precedence_key():
                            winners[expanded_name] = candidate

    inline_style_sheet_index = len(style_sheets)
    # Inline style has no @layer context — treat as unlayered (tier = 1).
    inline_layer_tier = 1
    inline_specificity = (1, 0, 0)
    for declaration_index, property_name in enumerate(element.style):
        property_value = element.style.get_property_value(property_name)
        # Re-attach !important suffix when present so _normalize_declaration
        # can detect the priority flag (CSSStyleDeclaration.get_property_value
        # returns the clean value without the suffix as per CSSOM §4.1).
        if element.style.get_property_priority(property_name) == "important":
            property_value = f"{property_value} !important"
        normalized = _normalize_declaration(property_name, property_value)
        if normalized is None:
            continue

        supported_name, supported_value, important = normalized
        for aliased_name, aliased_value in _iter_logical_alias_declarations(
            supported_name, supported_value
        ):
            for expanded_index, (expanded_name, expanded_value) in enumerate(
                _iter_expanded_declarations(aliased_name, aliased_value)
            ):
                candidate = _Candidate(
                    property_name=expanded_name,
                    value=expanded_value,
                    origin="author",
                    important=important,
                    specificity=inline_specificity,
                    style_sheet_index=inline_style_sheet_index,
                    layer_tier=inline_layer_tier,
                    rule_index=0,
                    media_rule_child_index=0,
                    declaration_index=declaration_index,
                    expanded_index=expanded_index,
                )

                current = winners.get(expanded_name)
                if current is None or candidate.precedence_key() >= current.precedence_key():
                    winners[expanded_name] = candidate

    return winners


def _resolve_computed_style(
    element: "Element",
    cache: dict[int, ComputedStyleDeclaration],
    visited: set[int],
) -> ComputedStyleDeclaration:
    """Resolve computed style with deterministic inheritance fallback."""
    element_id = id(element)
    cached = cache.get(element_id)
    if cached is not None:
        return cached

    local_winners = _resolve_local_winners(element)
    custom_properties: dict[str, str] = {}
    regular_properties_raw: dict[str, str] = {}
    for name, candidate in local_winners.items():
        if name.startswith("--"):
            custom_properties[name] = candidate.value
            continue
        regular_properties_raw[name] = candidate.value

    parent_style: ComputedStyleDeclaration | None = None
    parent = element.parent_node
    if parent is not None:
        from aspose_html.dom._element import Element as _Element  # noqa: PLC0415

        parent_id = id(parent)
        if isinstance(parent, _Element) and parent_id not in visited:
            visited.add(parent_id)
            parent_style = _resolve_computed_style(parent, cache, visited)
            visited.discard(parent_id)

    for name in _INHERITED_PROPERTIES:
        if name in regular_properties_raw:
            continue

        if parent_style is not None:
            parent_value = parent_style.get_property_value(name)
            if parent_value:
                regular_properties_raw[name] = parent_value

    if parent_style is not None:
        for property_name in parent_style:
            if not property_name.startswith("--") or property_name in custom_properties:
                continue
            custom_properties[property_name] = parent_style.get_property_value(property_name)

    custom_memo: dict[str, str | None] = {}
    resolved_custom_properties: dict[str, str] = {}
    for property_name in sorted(custom_properties):
        resolved_value = _resolve_custom_property_value(
            property_name,
            custom_properties,
            custom_memo,
            visiting=set(),
        )
        if resolved_value is None:
            continue
        resolved_custom_properties[property_name] = resolved_value

    resolved: dict[str, str] = dict(resolved_custom_properties)
    for property_name, raw_value in regular_properties_raw.items():
        keyword_resolved = _resolve_css_wide_keyword_value(property_name, raw_value, parent_style)
        if keyword_resolved != raw_value:
            resolved[property_name] = keyword_resolved
            continue

        substituted = _resolve_regular_property_value(raw_value, custom_properties, custom_memo)
        if substituted is None:
            continue
        resolved[property_name] = substituted

    style = ComputedStyleDeclaration(resolved)
    cache[element_id] = style
    return style


def get_computed_style(element: "Element") -> ComputedStyleDeclaration:
    """Resolve phase-3 cascade declarations for *element*.

    Deterministic unsupported handling (/070/071/072/073/153):
    - `@media` style rules are included only for a constrained baseline query subset,
    - unsupported/invalid media queries are treated as non-matching,
    - `@supports` style rules are included only when `_supports_condition_matches`
      evaluates the condition as True (known property name check),
    - other non-style rules are ignored,
    - declarations with invalid/empty names are ignored,
    - declarations with empty values are ignored,
    - custom properties participate in winner resolution and inheritance,
    - custom property and regular property values support deterministic full-value
      `var(--name)` / `var(--name, fallback)` substitution with cycle-safe
      fallback-or-omit behavior.
    """
    return _resolve_computed_style(element, cache={}, visited={id(element)})
