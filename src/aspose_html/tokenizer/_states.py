"""TokenizerState IntEnum — all WHATWG HTML §13.2.5 tokeniser states.

Each state corresponds to one private method on the Tokenizer class named
``_state_<lowercase_state_name_with_underscores>``. The dispatch table in
Tokenizer.__init__ maps each value to its method for O(1) dispatch.

See ADR-002, Decision 3.
"""
from __future__ import annotations

from enum import IntEnum


class TokenizerState(IntEnum):
    """All tokeniser states defined in WHATWG HTML Living Standard §13.2.5.

    Each value is the integer identifier used internally. The names match
    the WHATWG specification state names with spaces replaced by underscores
    and all letters uppercased.

    Examples
    --------
    >>> TokenizerState.DATA
    <TokenizerState.DATA: 0>
    >>> TokenizerState.TAG_OPEN
    <TokenizerState.TAG_OPEN: 6>
    >>> int(TokenizerState.DATA)
    0
    """

    # §13.2.5.1
    DATA = 0
    # §13.2.5.2
    RCDATA = 1
    # §13.2.5.3
    RAWTEXT = 2
    # §13.2.5.4
    SCRIPT_DATA = 3
    # §13.2.5.5
    PLAINTEXT = 4
    # §13.2.5.6
    TAG_OPEN = 6
    # §13.2.5.7
    END_TAG_OPEN = 7
    # §13.2.5.8
    TAG_NAME = 8
    # §13.2.5.9
    RCDATA_LESS_THAN_SIGN = 9
    # §13.2.5.10
    RCDATA_END_TAG_OPEN = 10
    # §13.2.5.11
    RCDATA_END_TAG_NAME = 11
    # §13.2.5.12
    RAWTEXT_LESS_THAN_SIGN = 12
    # §13.2.5.13
    RAWTEXT_END_TAG_OPEN = 13
    # §13.2.5.14
    RAWTEXT_END_TAG_NAME = 14
    # §13.2.5.15
    SCRIPT_DATA_LESS_THAN_SIGN = 15
    # §13.2.5.16
    SCRIPT_DATA_END_TAG_OPEN = 16
    # §13.2.5.17
    SCRIPT_DATA_END_TAG_NAME = 17
    # §13.2.5.18
    SCRIPT_DATA_ESCAPE_START = 18
    # §13.2.5.19
    SCRIPT_DATA_ESCAPE_START_DASH = 19
    # §13.2.5.20
    SCRIPT_DATA_ESCAPED = 20
    # §13.2.5.21
    SCRIPT_DATA_ESCAPED_DASH = 21
    # §13.2.5.22
    SCRIPT_DATA_ESCAPED_DASH_DASH = 22
    # §13.2.5.23
    SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN = 23
    # §13.2.5.24
    SCRIPT_DATA_ESCAPED_END_TAG_OPEN = 24
    # §13.2.5.25
    SCRIPT_DATA_ESCAPED_END_TAG_NAME = 25
    # §13.2.5.26
    SCRIPT_DATA_DOUBLE_ESCAPE_START = 26
    # §13.2.5.27
    SCRIPT_DATA_DOUBLE_ESCAPED = 27
    # §13.2.5.28
    SCRIPT_DATA_DOUBLE_ESCAPED_DASH = 28
    # §13.2.5.29
    SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH = 29
    # §13.2.5.30
    SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN = 30
    # §13.2.5.31
    SCRIPT_DATA_DOUBLE_ESCAPE_END = 31
    # §13.2.5.32
    BEFORE_ATTRIBUTE_NAME = 32
    # §13.2.5.33
    ATTRIBUTE_NAME = 33
    # §13.2.5.34
    AFTER_ATTRIBUTE_NAME = 34
    # §13.2.5.35
    BEFORE_ATTRIBUTE_VALUE = 35
    # §13.2.5.36
    ATTRIBUTE_VALUE_DOUBLE_QUOTED = 36
    # §13.2.5.37
    ATTRIBUTE_VALUE_SINGLE_QUOTED = 37
    # §13.2.5.38
    ATTRIBUTE_VALUE_UNQUOTED = 38
    # §13.2.5.39
    AFTER_ATTRIBUTE_VALUE_QUOTED = 39
    # §13.2.5.40
    SELF_CLOSING_START_TAG = 40
    # §13.2.5.41
    BOGUS_COMMENT = 41
    # §13.2.5.42
    MARKUP_DECLARATION_OPEN = 42
    # §13.2.5.43
    COMMENT_START = 43
    # §13.2.5.44
    COMMENT_START_DASH = 44
    # §13.2.5.45
    COMMENT = 45
    # §13.2.5.46
    COMMENT_LESS_THAN_SIGN = 46
    # §13.2.5.47
    COMMENT_LESS_THAN_SIGN_BANG = 47
    # §13.2.5.48
    COMMENT_LESS_THAN_SIGN_BANG_DASH = 48
    # §13.2.5.49
    COMMENT_LESS_THAN_SIGN_BANG_DASH_DASH = 49
    # §13.2.5.50
    COMMENT_END_DASH = 50
    # §13.2.5.51
    COMMENT_END = 51
    # §13.2.5.52
    COMMENT_END_BANG = 52
    # §13.2.5.53
    DOCTYPE = 53
    # §13.2.5.54
    BEFORE_DOCTYPE_NAME = 54
    # §13.2.5.55
    DOCTYPE_NAME = 55
    # §13.2.5.56
    AFTER_DOCTYPE_NAME = 56
    # §13.2.5.57
    AFTER_DOCTYPE_PUBLIC_KEYWORD = 57
    # §13.2.5.58
    BEFORE_DOCTYPE_PUBLIC_IDENTIFIER = 58
    # §13.2.5.59
    DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED = 59
    # §13.2.5.60
    DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED = 60
    # §13.2.5.61
    AFTER_DOCTYPE_PUBLIC_IDENTIFIER = 61
    # §13.2.5.62
    BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS = 62
    # §13.2.5.63
    AFTER_DOCTYPE_SYSTEM_KEYWORD = 63
    # §13.2.5.64
    BEFORE_DOCTYPE_SYSTEM_IDENTIFIER = 64
    # §13.2.5.65
    DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED = 65
    # §13.2.5.66
    DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED = 66
    # §13.2.5.67
    AFTER_DOCTYPE_SYSTEM_IDENTIFIER = 67
    # §13.2.5.68
    BOGUS_DOCTYPE = 68
    # §13.2.5.69
    CDATA_SECTION = 69
    # §13.2.5.70
    CDATA_SECTION_BRACKET = 70
    # §13.2.5.71
    CDATA_SECTION_END = 71
    # §13.2.5.72
    CHARACTER_REFERENCE = 72
    # §13.2.5.73
    NAMED_CHARACTER_REFERENCE = 73
    # §13.2.5.74
    AMBIGUOUS_AMPERSAND = 74
    # §13.2.5.75
    NUMERIC_CHARACTER_REFERENCE = 75
    # §13.2.5.76
    HEXADECIMAL_CHARACTER_REFERENCE_START = 76
    # §13.2.5.77
    DECIMAL_CHARACTER_REFERENCE_START = 77
    # §13.2.5.78
    HEXADECIMAL_CHARACTER_REFERENCE = 78
    # §13.2.5.79
    DECIMAL_CHARACTER_REFERENCE = 79
    # §13.2.5.80
    NUMERIC_CHARACTER_REFERENCE_END = 80
