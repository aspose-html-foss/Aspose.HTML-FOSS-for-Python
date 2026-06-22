"""InsertionMode enum — the 23 WHATWG HTML parsing insertion modes.

Defined in §13.2.6 of the WHATWG HTML Living Standard.  Each mode maps to a
handler method on TreeBuilder named ``_process_<mode_value>``.

The string values match the spec terminology to aid reading.
"""
from __future__ import annotations

import enum


class InsertionMode(enum.Enum):
    """The 23 WHATWG insertion modes (§13.2.6).

    Examples
    --------
    >>> InsertionMode.INITIAL.value
    'initial'
    >>> InsertionMode.IN_BODY.value
    'in_body'
    """

    INITIAL = "initial"
    BEFORE_HTML = "before_html"
    BEFORE_HEAD = "before_head"
    IN_HEAD = "in_head"
    IN_HEAD_NOSCRIPT = "in_head_noscript"
    AFTER_HEAD = "after_head"
    IN_BODY = "in_body"
    TEXT = "text"
    IN_TABLE = "in_table"
    IN_TABLE_TEXT = "in_table_text"
    IN_CAPTION = "in_caption"
    IN_COLUMN_GROUP = "in_column_group"
    IN_TABLE_BODY = "in_table_body"
    IN_ROW = "in_row"
    IN_CELL = "in_cell"
    IN_SELECT = "in_select"
    IN_SELECT_IN_TABLE = "in_select_in_table"
    IN_TEMPLATE = "in_template"
    AFTER_BODY = "after_body"
    IN_FRAMESET = "in_frameset"
    AFTER_FRAMESET = "after_frameset"
    AFTER_AFTER_BODY = "after_after_body"
    AFTER_AFTER_FRAMESET = "after_after_frameset"
