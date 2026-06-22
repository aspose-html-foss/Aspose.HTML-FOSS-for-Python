from aspose_html.dom import Document, HTMLElement, NotSupportedError, CustomElementRegistry


def test_window_custom_elements_cached() -> None:
    doc = Document()
    assert isinstance(doc.default_view.custom_elements, CustomElementRegistry)
    assert doc.default_view.custom_elements is doc.default_view.custom_elements


def test_define_and_create_element_custom_type() -> None:
    doc = Document()

    class MyTag(HTMLElement):
        __slots__ = ()

    doc.default_view.custom_elements.define("my-tag", MyTag)
    el = doc.create_element("my-tag")
    assert isinstance(el, MyTag)


def test_define_validation_and_redefinition() -> None:
    doc = Document()

    class MyTag(HTMLElement):
        __slots__ = ()

    reg = doc.default_view.custom_elements
    reg.define("my-tag", MyTag)
    assert reg.get("my-tag") is MyTag
    assert reg.get_name(MyTag) == "my-tag"
    assert reg.when_defined("my-tag") == "my-tag"
    assert reg.when_defined("other-tag") is None

    try:
        reg.define("my-tag", MyTag)
    except NotSupportedError:
        pass
    else:
        raise AssertionError("Expected NotSupportedError for duplicate define")


def test_upgrade_existing_and_lifecycle_callbacks() -> None:
    doc = Document()
    root = doc.create_element("div")
    doc.append_child(root)
    el = doc.create_element("my-tag")
    before_id = id(el)
    root.append_child(el)

    calls: list[tuple[str, str | None, str | None]] = []

    class MyTag(HTMLElement):
        __slots__ = ()

        def connected_callback(self) -> None:
            calls.append(("connected", None, None))

        def disconnected_callback(self) -> None:
            calls.append(("disconnected", None, None))

        def attribute_changed_callback(self, name: str, old: str | None, new: str | None) -> None:
            calls.append((name, old, new))

    doc.default_view.custom_elements.define("my-tag", MyTag, observed_attributes=("data-x",))
    assert id(el) == before_id
    assert isinstance(el, MyTag)
    assert ("connected", None, None) in calls

    el.set_attribute("data-x", "1")
    el.set_attribute("title", "x")
    el.remove_attribute("data-x")
    assert ("data-x", None, "1") in calls
    assert ("data-x", "1", None) in calls
    assert not any(c[0] == "title" for c in calls)

    root.remove_child(el)
    assert ("disconnected", None, None) in calls


def test_define_rejects_non_empty_slots_for_upgrade_compatibility() -> None:
    doc = Document()

    class BadTag(HTMLElement):
        __slots__ = ("_extra",)

    try:
        doc.default_view.custom_elements.define("bad-tag", BadTag)
    except TypeError:
        pass
    else:
        raise AssertionError("Expected TypeError for slot-incompatible custom element")
