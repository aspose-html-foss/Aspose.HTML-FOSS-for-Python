"""test_quirks_mode.py — tests for DOCTYPE handling and quirks mode determination."""
import pytest
from aspose_html.tokenizer import DoctypeToken
from aspose_html.tree._doctype_switch import determine_quirks_mode
from aspose_html.tree import parse_html


def test_html5_doctype_no_quirks():
    """<!DOCTYPE html> results in no-quirks mode."""
    tok = DoctypeToken(
        name="html", public_id=None, system_id=None,
        force_quirks=False, line=1, column=1
    )
    assert determine_quirks_mode(tok) == "CSS1Compat"


def test_force_quirks_flag():
    """force_quirks=True always produces BackCompat mode."""
    tok = DoctypeToken(
        name="html", public_id=None, system_id=None,
        force_quirks=True, line=1, column=1
    )
    assert determine_quirks_mode(tok) == "BackCompat"


def test_missing_doctype_name():
    """Missing DOCTYPE name triggers quirks mode."""
    tok = DoctypeToken(
        name=None, public_id=None, system_id=None,
        force_quirks=False, line=1, column=1
    )
    assert determine_quirks_mode(tok) == "BackCompat"


def test_wrong_doctype_name():
    """DOCTYPE name other than 'html' triggers quirks mode."""
    tok = DoctypeToken(
        name="svg", public_id=None, system_id=None,
        force_quirks=False, line=1, column=1
    )
    assert determine_quirks_mode(tok) == "BackCompat"


def test_known_quirks_public_id():
    """Known quirks public IDs trigger BackCompat mode."""
    # "-//W3C//DTD HTML 4.0 Frameset//" is a known quirks prefix
    tok = DoctypeToken(
        name="html",
        public_id="-//W3C//DTD HTML 4.0 Frameset//EN",
        system_id=None,
        force_quirks=False,
        line=1, column=1,
    )
    assert determine_quirks_mode(tok) == "BackCompat"


def test_known_limited_quirks_public_id():
    """Known limited-quirks public IDs trigger LimitedQuirks mode."""
    tok = DoctypeToken(
        name="html",
        public_id="-//W3C//DTD XHTML 1.0 Frameset//EN",
        system_id=None,
        force_quirks=False,
        line=1, column=1,
    )
    assert determine_quirks_mode(tok) == "LimitedQuirks"


def test_no_doctype_is_quirks():
    """No DOCTYPE at all triggers quirks mode (BackCompat)."""
    doc = parse_html("<html><body></body></html>")
    # Without DOCTYPE, parser switches to BackCompat
    assert doc.compat_mode == "BackCompat"


def test_html5_doctype_via_parse():
    """<!DOCTYPE html> via parse_html sets CSS1Compat."""
    doc = parse_html("<!DOCTYPE html><html><body></body></html>")
    assert doc.compat_mode == "CSS1Compat"


def test_quirks_system_id():
    """Known quirks system IDs trigger BackCompat mode."""
    tok = DoctypeToken(
        name="html",
        public_id=None,
        system_id="http://www.ibm.com/data/dtd/v11/ibmxhtml1-transitional.dtd",
        force_quirks=False,
        line=1, column=1,
    )
    assert determine_quirks_mode(tok) == "BackCompat"


def test_case_insensitive_public_id():
    """Public ID comparison is case-insensitive."""
    tok = DoctypeToken(
        name="html",
        public_id="-//w3c//dtd html 4.0 frameset//en",  # lowercase
        system_id=None,
        force_quirks=False,
        line=1, column=1,
    )
    assert determine_quirks_mode(tok) == "BackCompat"
