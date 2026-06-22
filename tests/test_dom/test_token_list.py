"""Tests for DOMTokenList / Element.class_list — BACK-17, ADR-015, SPEC-015."""
import pytest
from aspose_html.dom import Document, DOMTokenList


@pytest.fixture
def doc() -> Document:
    return Document()


# ---------------------------------------------------------------------------
# AC-1: class_list returns a DOMTokenList instance
# ---------------------------------------------------------------------------

def test_class_list_returns_domtokenlist(doc: Document) -> None:
    """AC-1 — class_list returns a DOMTokenList when element has a class attr."""
    el = doc.create_element("div")
    el.set_attribute("class", "foo")
    assert isinstance(el.class_list, DOMTokenList)


# ---------------------------------------------------------------------------
# AC-2: class_list caches identity — same object on repeated calls
# ---------------------------------------------------------------------------

def test_class_list_cached_identity(doc: Document) -> None:
    """AC-2 — el.class_list is el.class_list (same object, cached)."""
    el = doc.create_element("div")
    assert el.class_list is el.class_list


# ---------------------------------------------------------------------------
# AC-3: add is idempotent — no duplicate, attribute unchanged on re-add
# ---------------------------------------------------------------------------

def test_add_idempotent(doc: Document) -> None:
    """AC-3 — add("foo") adds; calling again leaves attribute unchanged."""
    el = doc.create_element("div")
    el.class_list.add("foo")
    assert el.get_attribute("class") == "foo"
    el.class_list.add("foo")
    assert el.get_attribute("class") == "foo"
    assert len(el.class_list) == 1


# ---------------------------------------------------------------------------
# AC-4: remove present and absent tokens
# ---------------------------------------------------------------------------

def test_remove_present_and_absent(doc: Document) -> None:
    """AC-4 — remove("foo") removes it; remove("absent") is no-op."""
    el = doc.create_element("div")
    el.set_attribute("class", "foo bar")
    el.class_list.remove("foo")
    assert el.get_attribute("class") == "bar"
    el.class_list.remove("absent")  # should not raise
    assert el.get_attribute("class") == "bar"


# ---------------------------------------------------------------------------
# AC-5: toggle adds when absent, removes when present
# ---------------------------------------------------------------------------

def test_toggle_adds_and_removes(doc: Document) -> None:
    """AC-5 — toggle absent → True token added; toggle present → False token removed."""
    el = doc.create_element("div")
    result = el.class_list.toggle("active")
    assert result is True
    assert "active" in el.class_list
    result = el.class_list.toggle("active")
    assert result is False
    assert "active" not in el.class_list


# ---------------------------------------------------------------------------
# AC-6: toggle with force parameter
# ---------------------------------------------------------------------------

def test_toggle_with_force(doc: Document) -> None:
    """AC-6 — force=True always adds/returns True; force=False always removes/returns False."""
    el = doc.create_element("div")
    el.set_attribute("class", "existing")

    result = el.class_list.toggle("existing", force=True)
    assert result is True
    assert "existing" in el.class_list

    result = el.class_list.toggle("existing", force=False)
    assert result is False
    assert "existing" not in el.class_list

    result = el.class_list.toggle("absent", force=False)
    assert result is False
    assert "absent" not in el.class_list


# ---------------------------------------------------------------------------
# AC-7: replace success and failure
# ---------------------------------------------------------------------------

def test_replace_success_and_failure(doc: Document) -> None:
    """AC-7 — replace("old","new") → True, attr updated; replace("absent","x") → False."""
    el = doc.create_element("div")
    el.set_attribute("class", "old extra")
    result = el.class_list.replace("old", "new")
    assert result is True
    assert el.get_attribute("class") == "new extra"

    result = el.class_list.replace("absent", "x")
    assert result is False
    assert el.get_attribute("class") == "new extra"  # unchanged


# ---------------------------------------------------------------------------
# AC-8: contains
# ---------------------------------------------------------------------------

def test_contains(doc: Document) -> None:
    """AC-8 — contains("foo") True when present; False when absent."""
    el = doc.create_element("div")
    el.set_attribute("class", "foo bar")
    assert el.class_list.contains("foo") is True
    assert el.class_list.contains("bar") is True
    assert el.class_list.contains("baz") is False


# ---------------------------------------------------------------------------
# AC-9: iteration, len, and indexing
# ---------------------------------------------------------------------------

def test_iter_len_getitem(doc: Document) -> None:
    """AC-9 — iteration yields tokens; len() returns count; [0] returns first token."""
    el = doc.create_element("div")
    el.set_attribute("class", "x y z")
    assert list(el.class_list) == ["x", "y", "z"]
    assert len(el.class_list) == 3
    assert el.class_list[0] == "x"
    assert el.class_list[2] == "z"


# ---------------------------------------------------------------------------
# AC-10: validation — empty and whitespace-containing tokens raise ValueError
# ---------------------------------------------------------------------------

def test_add_invalid_tokens(doc: Document) -> None:
    """AC-10 — add("") raises ValueError; add("a b") raises ValueError."""
    el = doc.create_element("div")
    with pytest.raises(ValueError):
        el.class_list.add("")
    with pytest.raises(ValueError):
        el.class_list.add("a b")
    with pytest.raises(ValueError):
        el.class_list.add("a\tb")
    with pytest.raises(ValueError):
        el.class_list.add("a\nb")


# ---------------------------------------------------------------------------
# AC-11: mutation via class_list is visible through get_attribute
# ---------------------------------------------------------------------------

def test_mutation_visible_via_get_attribute(doc: Document) -> None:
    """AC-11 — after add("bar"), get_attribute("class") reflects the change."""
    el = doc.create_element("div")
    el.set_attribute("class", "foo")
    el.class_list.add("bar")
    assert el.get_attribute("class") == "foo bar"


# ---------------------------------------------------------------------------
# AC-12: removing last token removes the attribute entirely
# ---------------------------------------------------------------------------

def test_remove_all_removes_attribute(doc: Document) -> None:
    """AC-12 — removing last token causes get_attribute("class") to return None."""
    el = doc.create_element("div")
    el.set_attribute("class", "only")
    el.class_list.remove("only")
    assert el.get_attribute("class") is None


# ---------------------------------------------------------------------------
# AC-13: DOMTokenList importable from aspose_html.dom
# ---------------------------------------------------------------------------

def test_domtokenlist_importable() -> None:
    """AC-13 — from aspose_html.dom import DOMTokenList succeeds."""
    from aspose_html.dom import DOMTokenList as DTL  # noqa: PLC0415
    assert DTL is not None


# ---------------------------------------------------------------------------
# AC-14: public API has type hints and docstrings
# ---------------------------------------------------------------------------

def test_public_api_has_type_hints_and_docstrings() -> None:
    """AC-14 — verify __doc__ and __annotations__ are non-empty on key methods."""
    assert DOMTokenList.__doc__ is not None and DOMTokenList.__doc__.strip()
    for method_name in ("add", "remove", "toggle", "replace", "contains", "values"):
        method = getattr(DOMTokenList, method_name)
        assert method.__doc__ is not None and method.__doc__.strip(), (
            f"DOMTokenList.{method_name} missing docstring"
        )
        assert method.__annotations__, (
            f"DOMTokenList.{method_name} missing type annotations"
        )


# ---------------------------------------------------------------------------
# AC-15: no circular import — import aspose_html.dom succeeds
# ---------------------------------------------------------------------------

def test_no_circular_import() -> None:
    """AC-15 — import aspose_html.dom succeeds without circular import error."""
    import aspose_html.dom  # noqa: PLC0415, F401
    assert True


# ---------------------------------------------------------------------------
# Extra edge-case tests (recommended by ADR-015)
# ---------------------------------------------------------------------------

def test_class_list_on_element_without_class_attr(doc: Document) -> None:
    """class_list on element with no class attr: DOMTokenList; len 0; contains False."""
    el = doc.create_element("div")
    cl = el.class_list
    assert isinstance(cl, DOMTokenList)
    assert len(cl) == 0
    assert cl.contains("foo") is False


def test_class_name_consistent_with_class_list(doc: Document) -> None:
    """After class_list.add("x"), class_name reflects the change."""
    el = doc.create_element("div")
    el.class_list.add("x")
    assert el.class_name == "x"


def test_external_set_attribute_visible_through_class_list(doc: Document) -> None:
    """set_attribute("class","a b") without re-fetching class_list; class_list reflects it."""
    el = doc.create_element("div")
    cl = el.class_list  # cache the object
    el.set_attribute("class", "a b")
    assert list(cl) == ["a", "b"]


def test_toggle_no_force_roundtrip(doc: Document) -> None:
    """toggle absent (True), toggle again (False) — attribute restored to no class."""
    el = doc.create_element("div")
    el.class_list.toggle("x")
    assert "x" in el.class_list
    el.class_list.toggle("x")
    assert el.get_attribute("class") is None


def test_values_iterator(doc: Document) -> None:
    """list(el.class_list.values()) on class="a b c" equals ["a","b","c"]."""
    el = doc.create_element("div")
    el.set_attribute("class", "a b c")
    assert list(el.class_list.values()) == ["a", "b", "c"]


def test_in_operator(doc: Document) -> None:
    """'foo' in el.class_list True; 'bar' in el.class_list False."""
    el = doc.create_element("div")
    el.set_attribute("class", "foo")
    assert "foo" in el.class_list
    assert "bar" not in el.class_list


def test_getitem_negative_index(doc: Document) -> None:
    """el.class_list[-1] returns last token."""
    el = doc.create_element("div")
    el.set_attribute("class", "a b c")
    assert el.class_list[-1] == "c"


def test_getitem_out_of_range(doc: Document) -> None:
    """el.class_list[99] raises IndexError."""
    el = doc.create_element("div")
    el.set_attribute("class", "a")
    with pytest.raises(IndexError):
        _ = el.class_list[99]


def test_remove_multiple_tokens(doc: Document) -> None:
    """remove("a","b") removes both in a single call."""
    el = doc.create_element("div")
    el.set_attribute("class", "a b c")
    el.class_list.remove("a", "b")
    assert el.get_attribute("class") == "c"


def test_add_multiple_tokens(doc: Document) -> None:
    """add("a","b") adds both in a single call."""
    el = doc.create_element("div")
    el.class_list.add("a", "b")
    assert el.get_attribute("class") == "a b"


def test_replace_deduplication(doc: Document) -> None:
    """replace("a","b") when "b" already present removes the duplicate "b"."""
    el = doc.create_element("div")
    el.set_attribute("class", "a b extra")
    el.class_list.replace("a", "b")
    # "a" replaced by "b" in position 0; duplicate "b" at position 1 removed
    assert el.get_attribute("class") == "b extra"


def test_empty_element_class_list_len_zero(doc: Document) -> None:
    """New element, class_list len is 0."""
    el = doc.create_element("div")
    assert len(el.class_list) == 0


def test_empty_element_class_list_contains_false(doc: Document) -> None:
    """'foo' not in class_list for new element with no class attr."""
    el = doc.create_element("div")
    assert "foo" not in el.class_list


def test_add_single_token(doc: Document) -> None:
    """add("foo") → "foo" in class_list, len 1."""
    el = doc.create_element("div")
    el.class_list.add("foo")
    assert "foo" in el.class_list
    assert len(el.class_list) == 1


def test_add_multiple_tokens_len(doc: Document) -> None:
    """add("a", "b") → len 2."""
    el = doc.create_element("div")
    el.class_list.add("a", "b")
    assert len(el.class_list) == 2


def test_add_duplicate_ignored(doc: Document) -> None:
    """add("x"), add("x") → len still 1."""
    el = doc.create_element("div")
    el.class_list.add("x")
    el.class_list.add("x")
    assert len(el.class_list) == 1


def test_remove_token(doc: Document) -> None:
    """add("a"), remove("a") → len 0."""
    el = doc.create_element("div")
    el.class_list.add("a")
    el.class_list.remove("a")
    assert len(el.class_list) == 0


def test_remove_missing_no_error(doc: Document) -> None:
    """remove("absent") doesn't raise."""
    el = doc.create_element("div")
    el.class_list.remove("absent")  # should not raise


def test_contains_alias(doc: Document) -> None:
    """contains() returns same as __contains__."""
    el = doc.create_element("div")
    el.set_attribute("class", "foo")
    assert el.class_list.contains("foo") == ("foo" in el.class_list)
    assert el.class_list.contains("bar") == ("bar" in el.class_list)


def test_toggle_add(doc: Document) -> None:
    """toggle("foo") on empty → True, "foo" present."""
    el = doc.create_element("div")
    result = el.class_list.toggle("foo")
    assert result is True
    assert "foo" in el.class_list


def test_toggle_remove(doc: Document) -> None:
    """toggle("foo") when present → False, absent."""
    el = doc.create_element("div")
    el.class_list.add("foo")
    result = el.class_list.toggle("foo")
    assert result is False
    assert "foo" not in el.class_list


def test_toggle_force_true(doc: Document) -> None:
    """toggle("foo", force=True) always adds, returns True."""
    el = doc.create_element("div")
    el.class_list.add("foo")
    result = el.class_list.toggle("foo", force=True)
    assert result is True
    assert "foo" in el.class_list


def test_toggle_force_false(doc: Document) -> None:
    """toggle("foo", force=False) always removes, returns False."""
    el = doc.create_element("div")
    el.class_list.add("foo")
    result = el.class_list.toggle("foo", force=False)
    assert result is False
    assert "foo" not in el.class_list


def test_replace_returns_true(doc: Document) -> None:
    """replace("a","b") when "a" present → True, "b" now present."""
    el = doc.create_element("div")
    el.class_list.add("a")
    result = el.class_list.replace("a", "b")
    assert result is True
    assert "b" in el.class_list
    assert "a" not in el.class_list


def test_replace_returns_false(doc: Document) -> None:
    """replace("x","y") when "x" absent → False."""
    el = doc.create_element("div")
    result = el.class_list.replace("x", "y")
    assert result is False


def test_value_property(doc: Document) -> None:
    """Set value; read back; reflects in class attribute."""
    el = doc.create_element("div")
    el.class_list.value = "alpha beta"
    assert el.class_list.value == "alpha beta"
    assert el.get_attribute("class") == "alpha beta"
    assert list(el.class_list) == ["alpha", "beta"]


# ---------------------------------------------------------------------------
# BACK-27: DOMTokenList.item(index) — ADR-021, SPEC-024
# ---------------------------------------------------------------------------

def test_item_in_bounds(doc: Document) -> None:
    """AC-1 (BACK-27) — item(index) returns correct token for valid indices."""
    el = doc.create_element("div")
    el.set_attribute("class", "alpha beta gamma")
    cl = el.class_list
    assert cl.item(0) == "alpha"
    assert cl.item(1) == "beta"
    assert cl.item(2) == "gamma"


def test_item_out_of_bounds(doc: Document) -> None:
    """AC-2 (BACK-27) — item(index) returns None for all out-of-bounds cases."""
    el = doc.create_element("div")
    el.set_attribute("class", "alpha beta")
    cl = el.class_list
    # Upper bound — index equals length
    assert cl.item(2) is None
    # Far out of bounds
    assert cl.item(99) is None
    # Negative index — Python convention does NOT apply; returns None per WHATWG
    assert cl.item(-1) is None
    # Empty list — element with no class attribute
    el2 = doc.create_element("span")
    assert el2.class_list.item(0) is None


# ---------------------------------------------------------------------------
# BACK-310 / ADR-288: DOMTokenList IDL tail — length, entries, keys,
# for_each, supports
# ---------------------------------------------------------------------------


def test_length(doc: Document) -> None:
    """AC-1 (BACK-310): el.class_list.length returns correct integer count."""
    el = doc.create_element("div")
    assert el.class_list.length == 0
    el.set_attribute("class", "a b c")
    assert el.class_list.length == 3


def test_length_reflects_live_attribute(doc: Document) -> None:
    """length is live — removing a token reduces the count."""
    el = doc.create_element("div")
    el.set_attribute("class", "x y")
    assert el.class_list.length == 2
    el.class_list.remove("x")
    assert el.class_list.length == 1


def test_entries(doc: Document) -> None:
    """AC-2 (BACK-310): list(el.class_list.entries()) == [(0,'a'),(1,'b'),(2,'c')]."""
    el = doc.create_element("div")
    el.set_attribute("class", "a b c")
    assert list(el.class_list.entries()) == [(0, "a"), (1, "b"), (2, "c")]


def test_entries_empty(doc: Document) -> None:
    """entries() on an empty class list yields nothing."""
    el = doc.create_element("div")
    assert list(el.class_list.entries()) == []


def test_keys(doc: Document) -> None:
    """AC-3 (BACK-310): list(el.class_list.keys()) == [0, 1, 2] for three tokens."""
    el = doc.create_element("div")
    el.set_attribute("class", "x y z")
    assert list(el.class_list.keys()) == [0, 1, 2]


def test_keys_empty(doc: Document) -> None:
    """keys() on empty class list yields nothing."""
    el = doc.create_element("div")
    assert list(el.class_list.keys()) == []


def test_for_each(doc: Document) -> None:
    """AC-4 (BACK-310): for_each calls callback with (token, index, tokenlist)."""
    el = doc.create_element("div")
    el.set_attribute("class", "p q r")
    collected: list[tuple[str, int]] = []
    list_ref_seen: list[object] = []

    def cb(tok: str, idx: int, lst: object) -> None:
        collected.append((tok, idx))
        list_ref_seen.append(lst)

    el.class_list.for_each(cb)
    assert collected == [("p", 0), ("q", 1), ("r", 2)]
    # Third argument must be the DOMTokenList itself
    assert all(lst is el.class_list for lst in list_ref_seen)


def test_for_each_empty(doc: Document) -> None:
    """for_each on empty class list: callback never called."""
    el = doc.create_element("div")
    calls: list[object] = []
    el.class_list.for_each(lambda tok, idx, lst: calls.append(tok))
    assert calls == []


def test_supports_raises_type_error(doc: Document) -> None:
    """AC-5 (BACK-310): el.class_list.supports('foo') raises TypeError."""
    el = doc.create_element("div")
    with pytest.raises(TypeError):
        el.class_list.supports("foo")


def test_supports_raises_regardless_of_token(doc: Document) -> None:
    """supports() raises TypeError for any token value, not just unknown ones."""
    el = doc.create_element("div")
    el.set_attribute("class", "active")
    # Even if the token is present, supports() raises TypeError
    with pytest.raises(TypeError):
        el.class_list.supports("active")
