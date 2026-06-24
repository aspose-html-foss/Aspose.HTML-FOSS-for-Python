"""Tests for Element.dataset — DOMStringMap.

Covers acceptance criteria AC-1 through AC-11 ( / ) plus
recommended edge-case tests.
"""
import pytest
from aspose_html.dom import Document, DOMStringMap


@pytest.fixture
def doc():
    return Document()


# ---------------------------------------------------------------------------
# AC-1: el.dataset["foo"] returns value of data-foo attribute
# ---------------------------------------------------------------------------

def test_getitem_simple_key(doc):
    el = doc.create_element("div")
    el.set_attribute("data-foo", "bar")
    assert el.dataset["foo"] == "bar"


# ---------------------------------------------------------------------------
# AC-2: el.dataset["foo"] = "bar" sets attribute data-foo="bar"
# ---------------------------------------------------------------------------

def test_setitem_simple_key(doc):
    el = doc.create_element("div")
    el.dataset["foo"] = "bar"
    assert el.get_attribute("data-foo") == "bar"


# ---------------------------------------------------------------------------
# AC-3: del el.dataset["foo"] removes data-foo; KeyError when absent
# ---------------------------------------------------------------------------

def test_delitem_present_key(doc):
    el = doc.create_element("div")
    el.set_attribute("data-foo", "1")
    del el.dataset["foo"]
    assert not el.has_attribute("data-foo")


def test_delitem_raises_keyerror_when_absent(doc):
    el = doc.create_element("div")
    with pytest.raises(KeyError):
        del el.dataset["missing"]


# ---------------------------------------------------------------------------
# AC-4: "foo" in el.dataset returns True iff data-foo exists
# ---------------------------------------------------------------------------

def test_contains(doc):
    el = doc.create_element("div")
    el.set_attribute("data-foo", "1")
    assert "foo" in el.dataset
    assert "bar" not in el.dataset


# ---------------------------------------------------------------------------
# AC-5: iterating yields camelCase keys for all data-* attrs
# ---------------------------------------------------------------------------

def test_iter_yields_camelcase_keys(doc):
    el = doc.create_element("div")
    el.set_attribute("data-foo", "1")
    el.set_attribute("data-bar-baz", "2")
    keys = list(el.dataset)
    assert keys == ["foo", "barBaz"]


# ---------------------------------------------------------------------------
# AC-6: el.dataset["myName"] reads data-my-name (camelCase to hyphenated)
# ---------------------------------------------------------------------------

def test_getitem_camelcase_key(doc):
    el = doc.create_element("div")
    el.set_attribute("data-my-name", "Alice")
    assert el.dataset["myName"] == "Alice"


# ---------------------------------------------------------------------------
# AC-7: el.dataset["myName"] = "x" writes data-my-name="x"
# ---------------------------------------------------------------------------

def test_setitem_camelcase_key(doc):
    el = doc.create_element("div")
    el.dataset["myName"] = "Bob"
    assert el.get_attribute("data-my-name") == "Bob"


# ---------------------------------------------------------------------------
# AC-8: el.dataset is el.dataset — same object (cached)
# ---------------------------------------------------------------------------

def test_cached_identity(doc):
    el = doc.create_element("div")
    assert el.dataset is el.dataset


# ---------------------------------------------------------------------------
# AC-9: External set_attribute("data-x","v") is immediately visible via dataset["x"]
# ---------------------------------------------------------------------------

def test_live_view_external_mutation(doc):
    el = doc.create_element("div")
    el.set_attribute("data-x", "first")
    assert el.dataset["x"] == "first"
    el.set_attribute("data-x", "second")
    assert el.dataset["x"] == "second"


# ---------------------------------------------------------------------------
# AC-10: DOMStringMap is importable from aspose_html.dom
# ---------------------------------------------------------------------------

def test_domstringmap_importable():
    from aspose_html.dom import DOMStringMap  # noqa: F401 — import is the test
    assert DOMStringMap is not None


# ---------------------------------------------------------------------------
# AC-11: dataset property has __doc__; DOMStringMap has docstrings
# ---------------------------------------------------------------------------

def test_type_hints_and_docstrings(doc):
    el = doc.create_element("div")
    # dataset property docstring
    from aspose_html.dom._element import Element
    assert Element.dataset.__doc__ is not None
    assert len(Element.dataset.__doc__) > 0
    # DOMStringMap class docstring
    assert DOMStringMap.__doc__ is not None
    assert len(DOMStringMap.__doc__) > 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_len_returns_count(doc):
    el = doc.create_element("div")
    assert len(el.dataset) == 0
    el.set_attribute("data-a", "1")
    el.set_attribute("data-b", "2")
    assert len(el.dataset) == 2


def test_get_with_default(doc):
    el = doc.create_element("div")
    el.set_attribute("data-foo", "hello")
    assert el.dataset.get("foo") == "hello"
    assert el.dataset.get("absent") == ""
    assert el.dataset.get("absent", "default") == "default"


def test_get_empty_string_value_not_replaced_by_default(doc):
    """Attribute present with value "" must be returned as "", not default."""
    el = doc.create_element("div")
    el.set_attribute("data-empty", "")
    # get() with is-not-None check: "" attribute is present, return "" not default
    assert el.dataset.get("empty", "fallback") == ""


def test_keys_values_items(doc):
    el = doc.create_element("div")
    el.set_attribute("data-foo", "1")
    el.set_attribute("data-bar-baz", "2")
    assert list(el.dataset.keys()) == ["foo", "barBaz"]
    assert list(el.dataset.values()) == ["1", "2"]
    assert list(el.dataset.items()) == [("foo", "1"), ("barBaz", "2")]


def test_iter_skips_non_data_attrs(doc):
    el = doc.create_element("div")
    el.set_attribute("class", "box")
    el.set_attribute("id", "main")
    el.set_attribute("style", "color:red")
    el.set_attribute("data-x", "1")
    keys = list(el.dataset)
    assert keys == ["x"]


def test_multiple_data_attrs(doc):
    el = doc.create_element("div")
    el.set_attribute("data-a", "1")
    el.set_attribute("data-b", "2")
    el.set_attribute("data-c", "3")
    assert len(el.dataset) == 3
    assert set(el.dataset) == {"a", "b", "c"}


def test_camelcase_roundtrip(doc):
    """Setting via camelCase key must create the correct hyphenated attribute."""
    el = doc.create_element("div")
    el.dataset["fooBarBaz"] = "1"
    assert el.get_attribute("data-foo-bar-baz") == "1"


def test_repr(doc):
    el = doc.create_element("div")
    el.set_attribute("data-foo", "bar")
    r = repr(el.dataset)
    assert r.startswith("DOMStringMap(")
    assert "foo" in r
    assert "bar" in r


def test_no_circular_import():
    """Importing aspose_html.dom must not raise any circular import error."""
    import aspose_html.dom  # noqa: F401 — import is the test


def test_getitem_raises_keyerror_for_absent(doc):
    el = doc.create_element("div")
    with pytest.raises(KeyError):
        _ = el.dataset["nothere"]


def test_contains_non_string_returns_false(doc):
    el = doc.create_element("div")
    el.set_attribute("data-foo", "1")
    # Non-string key must return False, not raise
    assert (42 in el.dataset) is False
    assert (None in el.dataset) is False


def test_dataset_is_domstringmap_instance(doc):
    el = doc.create_element("div")
    assert isinstance(el.dataset, DOMStringMap)
