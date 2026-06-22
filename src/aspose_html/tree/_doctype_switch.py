"""Quirks mode determination from a DoctypeToken — §13.2.6.4.

Uses the generated switch table in _quirks_table.py.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_html.tree._quirks_table import (
    QUIRKS_PUBLIC_IDS,
    LIMITED_QUIRKS_PUBLIC_IDS,
    QUIRKS_PUBLIC_ID_PREFIXES,
    LIMITED_QUIRKS_PUBLIC_ID_PREFIXES,
    LIMITED_QUIRKS_PUBLIC_ID_PREFIXES_WITH_SYSTEM_ID,
    QUIRKS_SYSTEM_IDS,
)

if TYPE_CHECKING:
    from aspose_html.tokenizer import DoctypeToken

# Return values matching document.compat_mode values
_NO_QUIRKS = "CSS1Compat"
_QUIRKS = "BackCompat"
_LIMITED_QUIRKS = "LimitedQuirks"


def determine_quirks_mode(doctype: DoctypeToken) -> str:
    """Determine the document's quirks mode from a DOCTYPE token.

    Returns 'BackCompat' (quirks), 'CSS1Compat' (no-quirks), or
    'LimitedQuirks' (limited-quirks) per §13.2.6.4.

    Uses the generated switch table in _quirks_table.py.

    Parameters
    ----------
    doctype : DoctypeToken
        The DOCTYPE token from the tokenizer.

    Returns
    -------
    str
        One of 'BackCompat', 'CSS1Compat', 'LimitedQuirks'.

    Examples
    --------
    >>> from aspose_html.tokenizer import DoctypeToken
    >>> from aspose_html.tree._doctype_switch import determine_quirks_mode
    >>> tok = DoctypeToken(name='html', public_id=None, system_id=None,
    ...                    force_quirks=False, line=1, column=1)
    >>> determine_quirks_mode(tok)
    'CSS1Compat'
    """
    # §13.2.6.4 step 1: force-quirks flag
    if doctype.force_quirks:
        return _QUIRKS

    # §13.2.6.4 step 2: DOCTYPE name is not "html"
    name = doctype.name
    if name is None or name.lower() != "html":
        return _QUIRKS

    pub = doctype.public_id
    sys = doctype.system_id

    # §13.2.6.4 step 3–4: exact public identifier matches (case-insensitive)
    if pub is not None:
        pub_upper = pub.upper()
        if pub_upper in {p.upper() for p in QUIRKS_PUBLIC_IDS}:
            return _QUIRKS

        # §13.2.6.4: prefix matches for quirks
        pub_lower = pub.lower()
        for prefix in QUIRKS_PUBLIC_ID_PREFIXES:
            if pub_lower.startswith(prefix.lower()):
                return _QUIRKS

        # §13.2.6.4: prefixes that are quirks without system ID
        # (same prefixes are limited-quirks when system ID is present)
        if sys is None:
            for prefix in LIMITED_QUIRKS_PUBLIC_ID_PREFIXES_WITH_SYSTEM_ID:
                if pub_lower.startswith(prefix.lower()):
                    return _QUIRKS

    # §13.2.6.4: system identifier checks
    if sys is not None and sys.lower() in {s.lower() for s in QUIRKS_SYSTEM_IDS}:
        return _QUIRKS

    # §13.2.6.4: limited-quirks checks
    if pub is not None:
        pub_upper_lq = pub.upper()
        if pub_upper_lq in {p.upper() for p in LIMITED_QUIRKS_PUBLIC_IDS}:
            return _LIMITED_QUIRKS

        pub_lower_lq = pub.lower()
        for prefix in LIMITED_QUIRKS_PUBLIC_ID_PREFIXES:
            if pub_lower_lq.startswith(prefix.lower()):
                return _LIMITED_QUIRKS

        # Limited quirks that also require system_id to be present
        if sys is not None:
            for prefix in LIMITED_QUIRKS_PUBLIC_ID_PREFIXES_WITH_SYSTEM_ID:
                if pub_lower_lq.startswith(prefix.lower()):
                    return _LIMITED_QUIRKS

    return _NO_QUIRKS
