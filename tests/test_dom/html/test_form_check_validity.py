"""Tests for HTMLFormElement.check_validity() and report_validity().

Covers  /  /  Group C acceptance criteria:
  AC-5: check_validity() returns True when all controls valid (or form empty)
  AC-6: check_validity() returns False when at least one listed control with
        will_validate==True has check_validity()==False
  AC-7: report_validity() returns the same boolean as check_validity()
"""
from __future__ import annotations

import pytest

from aspose_html.dom import Document
from aspose_html.html_document import HTMLDocument


# ---------------------------------------------------------------------------
# AC-5 — empty form always valid
# ---------------------------------------------------------------------------

def test_check_validity_empty_form_returns_true():
    doc = Document()
    form = doc.create_element("form")
    assert form.check_validity() is True


# ---------------------------------------------------------------------------
# AC-5 — form with all valid controls
# ---------------------------------------------------------------------------

def test_check_validity_all_valid_returns_true():
    doc = HTMLDocument.parse('<form><input name="x" value="hello"></form>')
    form = doc.query_selector("form")
    assert form.check_validity() is True


# ---------------------------------------------------------------------------
# AC-6 — required input with no value → invalid
# ---------------------------------------------------------------------------

def test_check_validity_required_empty_returns_false():
    doc = HTMLDocument.parse('<form><input name="x" required></form>')
    form = doc.query_selector("form")
    assert form.check_validity() is False


def test_check_validity_required_filled_returns_true():
    doc = HTMLDocument.parse('<form><input name="x" required value="ok"></form>')
    form = doc.query_selector("form")
    assert form.check_validity() is True


# ---------------------------------------------------------------------------
# AC-6 — disabled controls are skipped (will_validate == False)
# ---------------------------------------------------------------------------

def test_check_validity_disabled_required_skipped():
    # disabled controls have will_validate == False — must NOT be counted
    doc = HTMLDocument.parse('<form><input name="x" required disabled></form>')
    form = doc.query_selector("form")
    assert form.check_validity() is True


# ---------------------------------------------------------------------------
# AC-7 — report_validity matches check_validity
# ---------------------------------------------------------------------------

def test_report_validity_same_as_check_validity_valid():
    doc = HTMLDocument.parse('<form><input name="x" value="hello"></form>')
    form = doc.query_selector("form")
    assert form.report_validity() == form.check_validity()
    assert form.report_validity() is True


def test_report_validity_same_as_check_validity_invalid():
    doc = HTMLDocument.parse('<form><input name="x" required></form>')
    form = doc.query_selector("form")
    assert form.report_validity() == form.check_validity()
    assert form.report_validity() is False


# ---------------------------------------------------------------------------
# AC-7 — empty form via report_validity
# ---------------------------------------------------------------------------

def test_report_validity_empty_form_returns_true():
    doc = Document()
    form = doc.create_element("form")
    assert form.report_validity() is True


# ---------------------------------------------------------------------------
# Edge case — multiple controls, one invalid
# ---------------------------------------------------------------------------

def test_check_validity_multiple_controls_one_invalid():
    doc = HTMLDocument.parse(
        '<form>'
        '<input name="a" value="filled">'
        '<input name="b" required>'
        '</form>'
    )
    form = doc.query_selector("form")
    assert form.check_validity() is False


def test_check_validity_multiple_controls_all_valid():
    doc = HTMLDocument.parse(
        '<form>'
        '<input name="a" required value="x">'
        '<input name="b" required value="y">'
        '</form>'
    )
    form = doc.query_selector("form")
    assert form.check_validity() is True
